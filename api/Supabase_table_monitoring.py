import json
import asyncio
import time
from threading import Thread
from supabase import acreate_client, AsyncClient, create_client, Client

# Load configuration once
CONFIG_PATH = "./api/static/config/config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

ACCESS_TOKEN = config["outputs"]["supabase"]["auth"]["access_token"]
REFRESH_TOKEN = config["outputs"]["supabase"]["auth"]["refresh_token"]


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
    """Callback function to process table updates."""
    print(f"Received update: {payload}")
    if 'data' in payload and 'record' in payload['data']:
        record = payload['data']['record']
        print(f"Updated record: {record}")


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


if __name__ == "__main__":
    monitor_thread = start_monitor_thread()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")