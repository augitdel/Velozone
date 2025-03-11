from supabase import create_client, Client
import time
from datetime import datetime, timezone
import threading
import queue
import csv
import os

# Supabase setup
URL = 'https://strada.sportsdatascience.be:8090'
ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzQwOTU2NDAwLAogICJleHAiOiAxODk4NzIyODAwCn0.jmTPjhaI3K_rugPcAe4PrHOWQqytNzNRwxpirHQZ4bA'

supabase: Client = create_client(URL, ANON_KEY)

ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYTlkMzY4NC1kYjkxLTRmYTEtYWY5Ni02OTExZTE1NjBjMDEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoyMDU2NjI5MDM2LCJpYXQiOjE3NDEyNjkwMzYsImVtYWlsIjoiZXhjZWxsZW50aWVAdWdlbnQuYmUiLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl0sInVzZXJyb2xlIjpbImxhcHJlYWRlciJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoicGFzc3dvcmQiLCJ0aW1lc3RhbXAiOjE3NDEyNjkwMzZ9XSwic2Vzc2lvbl9pZCI6ImVkYTkwNGMyLTllYjUtNDM0YS04ZGZlLWQxMjkyMDA3Y2FmMiIsImlzX2Fub255bW91cyI6ZmFsc2V9.gqakyr5TWpknfPJ1fG107B3qm0hIGFg47kwvj3EjcoI'
REFRESH_TOKEN = '0iw1_TL1yWfwZvY_iDs9Sw'

supabase.auth.set_session(ACCESS_TOKEN, REFRESH_TOKEN)

# Fetch data in smaller batches
batch_size = 100  # Adjust the batch size as needed
offset = 0
qMyLaps = queue.Queue()  # Initialize the queue here

while True:
    response = supabase.table("laptimes").select("*").range(offset, offset + batch_size - 1).execute()
    if not response.data:
        break
    for record in response.data:
        print("Gegevens in wachtrij plaatsen:", record)  # Debug message
        qMyLaps.put(record)
    offset += batch_size

# Define necessary variables and objects
stop_event = threading.Event()
laptimes = {}
config = {
    "outputs": {
        "console": True
    }
}
fields = {}
tz_utc = timezone.utc

# Mock objects for cam_coordinator and auto_recorder
class MockCamCoordinator:
    def get_active_camera_preset(self):
        return ""
    
    def get_tracked_rider(self):
        return ""

class MockAutoRecorder:
    def get_current_event(self):
        return "17:00-20:00 Vlaamse wielerschool", None, None, None

cam_coordinator = MockCamCoordinator()
auto_recorder = MockAutoRecorder()

# Function to write data to CSV
def write_to_csv(fields):
    file_path = 'metingen/test.csv'
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write header if file does not exist
            writer.writerow([
                "transponder_id", "loop", "utcTimestamp", "utcTime", "lapTime", 
                "lapSpeed", "maxSpeed", "cameraPreset", "cameraPan", 
                "cameraTilt", "cameraZoom", "eventName", "recSegmentId", "trackedRider"
            ])
        writer.writerow([
            fields.get("transponder_id", ""),
            fields.get("loop", ""),
            fields.get("utcTimestamp", ""),
            fields.get("utcTime", ""),
            fields.get("lapTime", ""),
            fields.get("lapSpeed", ""),
            fields.get("maxSpeed", ""),
            fields.get("cameraPreset", ""),
            fields.get("cameraPan", ""),
            fields.get("cameraTilt", ""),
            fields.get("cameraZoom", ""),
            fields.get("eventName", ""),
            fields.get("recSegmentId", ""),
            fields.get("trackedRider", "")
        ])

# Function to run the main loop
def main_loop():
    while not stop_event.is_set():
        try:
            print("Wachten op gegevens...")
            dataMyLaps = qMyLaps.get(block=True)  # Remove timeout value
            if dataMyLaps:
                print("Gegevens ontvangen:", dataMyLaps)
                # Get 'code' (transponder id)
                code = dataMyLaps["tag"]
                if code != '9992':  # Start block, ignore
                    last_tcp_msg_time = time.time()  # To monitor TCP connection
                laptimes[code] = dataMyLaps
                deviceId = dataMyLaps["location"]
                laptime = laptimes[code][f"{deviceId}.lapTime"]
                passingTimeUtc = dataMyLaps[f"{deviceId}.rtcTime"] / 1000  # is actually UTC, and is sent in ms
                numPassings = dataMyLaps[f"{deviceId}.numLaps"]
                if "console" in config["outputs"] and config["outputs"]["console"]:
                    print("Current " + code + ": " + str(numPassings) + " - " + str(passingTimeUtc) + " - " + deviceId)
                # Fill log entry
                fields["transponder_id"] = code
                fields["loop"] = deviceId
                fields["utcTimestamp"] = passingTimeUtc
                fields["utcTime"] = datetime.fromtimestamp(passingTimeUtc, tz=tz_utc).strftime('%Y-%m-%d %H:%M:%S.%f')
                fields["localTime"] = datetime.fromtimestamp(passingTimeUtc).strftime('%Y-%m-%d %H:%M:%S.%f')
                fields["lapTime"] = laptime
                fields["cameraPreset"] = cam_coordinator.get_active_camera_preset()  # Make sure this is updated in the main thread
                fields["eventName"], _, _, _ = auto_recorder.get_current_event()
                fields["trackedRider"] = cam_coordinator.get_tracked_rider()
                # Write to CSV
                write_to_csv(fields)
        except queue.Empty:
            continue

# Start the main loop in a separate thread
thread = threading.Thread(target=main_loop)
thread.start()

# Run the main loop for a specific duration (e.g., 60 seconds)
time.sleep(60)
stop_event.set()
thread.join()

print("Hoofdloop beëindigd.")
