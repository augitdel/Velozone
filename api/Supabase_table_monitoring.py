import json
import asyncio
import time
import pandas as pd
from threading import Thread
from supabase import acreate_client, AsyncClient, create_client, Client
from datetime import datetime, timezone

# Load configuration once
CONFIG_PATH = "./api/static/config/config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

ACCESS_TOKEN = config["outputs"]["supabase"]["auth"]["access_token"]
REFRESH_TOKEN = config["outputs"]["supabase"]["auth"]["refresh_token"]

columns_incomming_DF = ['transponder_id','loop','utcTimestamp','utcTime','lapTime','lapSpeed','maxSpeed','cameraPreset','cameraPan','cameraTilt','cameraZoom','eventName','recSegmentId','trackedRider']
df_wielerrecords = pd.DataFrame(columns=columns_incomming_DF)

tz_utc = timezone.utc


class SupabaseClientRealtime:
    def __init__(self, config):
        self.config = config
        self.supabase_rt = None

    async def connect_to_supabase(self):
        """Establish an asynchronous connection to Supabase."""
        self.supabase_rt: AsyncClient = await acreate_client(
            self.config["outputs"]["supabase"]["url"],
            self.config["outputs"]["supabase"]["key"]
        )

        await self.supabase_rt.auth.set_session(ACCESS_TOKEN, REFRESH_TOKEN)

    async def enable_simulation(self):
        """Set enable_simulation to True before starting monitoring."""
        print("Setting enable_simulation to True...")
        # Disable and re-enable the 'enable simulation' bit to get new data from the simulation (rerun in between)
        response = await self.supabase_rt.table("development").update({"enable_simulation": True}).eq("id", 1).execute()
        print(f"Enable_simulation set to True: {response.data}")

    async def monitor_table(self, table, callback):
        """Monitor a table for updates and trigger a callback."""
        if not self.supabase_rt:
            await self.connect_to_supabase()

        # Ensure simulation is enabled before monitoring
        await self.enable_simulation()

        await self.supabase_rt.realtime.connect()

        await (self.supabase_rt
            .channel(table)
            .on_postgres_changes(
                "UPDATE", schema="public", table=table, callback=callback)
            .subscribe()
        )

        await self.supabase_rt.realtime.listen()


def handle_table_update(payload):
    """Callback function to process table updates and store them in DataFrame."""
    global df_wielerrecords

    # print(f"Received update: {payload}")
    if 'data' in payload and 'record' in payload['data']:
        record = payload['data']['record']
        # print(f"Updated record: {record}")

        location = record.get("location")  #e.g. "L03"
        if not location:
            print("No location/device found in update.")
            return

        try:
            transponder_id = record.get("tag", "")
            rtcTime = record.get(f"{location}.rtcTime")
            lapTime = record.get(f"{location}.lapTime")
            lapSpeed = record.get(f"{location}.lapSpeed")
            maxSpeed = record.get(f"{location}.maxSpeed")
            cameraPreset = record.get(f"{location}.cameraPreset")
            cameraPan = record.get(f"{location}.cameraPan")
            cameraTilt = record.get(f"{location}.cameraTilt")
            cameraZoom = record.get(f"{location}.cameraZoom")
            trackedRider = record.get(f"{location}.trackedRider")
            if rtcTime is None or lapTime is None:
                return

            utc_ts = rtcTime / 1000
            utc_time_str = datetime.fromtimestamp(utc_ts, tz=tz_utc).strftime('%Y-%m-%d %H:%M:%S.%f')
            
            # ['transponder_id','loop','utcTimestamp','utcTime','lapTime','lapSpeed','maxSpeed','cameraPreset','cameraPan','cameraTilt','cameraZoom','eventName','recSegmentId','trackedRider']
            new_row = {
                "transponder_id": transponder_id if transponder_id else "",
                "loop": location if location else "",
                "utcTimestamp": utc_ts if utc_ts else "",
                "utcTime": utc_time_str if utc_time_str else "",
                "lapTime": lapTime if lapTime else "",
                "lapSpeed": lapSpeed if lapSpeed else "",
                "maxSpeed": maxSpeed if maxSpeed else "",
                "cameraPreset": cameraPreset if cameraPreset else "",
                "cameraPan": cameraPan if cameraPan else "",
                "cameraTilt": cameraTilt if cameraTilt else "",
                "cameraZoom": cameraZoom if cameraZoom else "", 
                "eventName": "Vlaamse wielerschool",
                "recSegmentId": location if location else "",
                "trackedRider": trackedRider if trackedRider else ""
            }

            # Voeg toe aan DataFrame
            new_row_DF = pd.DataFrame([new_row])
            if not df_wielerrecords.empty:
                if not new_row_DF.empty:
                    df_wielerrecords = pd.concat([df_wielerrecords, new_row_DF], ignore_index=True)
            else:
                df_wielerrecords = new_row_DF

        except Exception as e:
            print(f"Fout bij verwerken update: {e}")


def start_monitor_thread():
    """Start monitoring Supabase in a separate thread."""
    try:
        async def monitor_table_async():
            supabase_rt = SupabaseClientRealtime(config)
            table_name = "laptimes"
            await supabase_rt.monitor_table(table_name, handle_table_update)

            # Keep the connection alive
            while True:
                await asyncio.sleep(7200)   # runs now for 7200s = 2h

        # Start the monitoring thread
        monitor_thread = Thread(
            target=lambda: asyncio.run(monitor_table_async()), 
            daemon=True
        )
        monitor_thread.start()
        print("Started monitoring Supabase table updates")

        return monitor_thread

    except Exception as e:
        print(f"Error starting monitor thread: {e}")
        return None


def get_and_clear_dataframe():
    """Geeft de dataframe terug en wist de inhoud."""
    global df_wielerrecords
    df_copy = df_wielerrecords.copy()
    # Has to be adjusted to recent changes
    df_wielerrecords = pd.DataFrame(columns=columns_incomming_DF)
    return df_copy

def run_get_and_clear_every(interval=3):
    """Roept get_and_clear_dataframe elke X seconden aan."""
    def loop():
        while True:
            time.sleep(interval)
            df = get_and_clear_dataframe()
            if not df.empty:
                print("\nNieuwe data uit Supabase:")
                print(df)
            else:
                print("Geen nieuwe data op dit moment.")
    # Start de thread
    Thread(target=loop, daemon=True).start()



if __name__ == "__main__":
    monitor_thread = start_monitor_thread()
    run_get_and_clear_every(interval=3)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")