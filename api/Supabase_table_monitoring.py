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

df_wielerrecords = pd.DataFrame(columns=[
    "transponder_id", "loop", "utcTimestamp", "utcTime", "lapTime",
    "eventName", "trackedRider"
])

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

    print(f"Received update: {payload}")
    if 'data' in payload and 'record' in payload['data']:
        record = payload['data']['record']
        print(f"Updated record: {record}")

        location = record.get("location")  #e.g. "L03"
        if not location:
            print("No location/device found in update.")
            return

        try:
            rtc_time_ms = record.get(f"{location}.rtcTime")
            lap_time = record.get(f"{location}.lapTime")
            
            if rtc_time_ms is None or lap_time is None:
                return

            utc_ts = rtc_time_ms / 1000
            utc_time_str = datetime.fromtimestamp(utc_ts, tz=tz_utc).strftime('%Y-%m-%d %H:%M:%S.%f')

            new_row = {
                "transponder_id": record.get("tag", ""),
                "loop": location,
                "utcTimestamp": utc_ts,
                "utcTime": utc_time_str,
                "lapTime": lap_time,
                "eventName": "Vlaamse wielerschool",
                "trackedRider": "",
            }

            # Voeg toe aan DataFrame
            df_wielerrecords = pd.concat([df_wielerrecords, pd.DataFrame([new_row])], ignore_index=True)

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
                await asyncio.sleep(60)

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
    df_wielerrecords = pd.DataFrame(columns=[
        "transponder_id", "loop", "utcTimestamp", "utcTime", "lapTime",
        "eventName", "trackedRider"
    ])
    return df_copy


if __name__ == "__main__":
    monitor_thread = start_monitor_thread()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")