from supabase import create_client, Client

URL = 'https://strada.sportsdatascience.be:8090'
ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzQwOTU2NDAwLAogICJleHAiOiAxODk4NzIyODAwCn0.jmTPjhaI3K_rugPcAe4PrHOWQqytNzNRwxpirHQZ4bA'

supabase: Client = create_client(URL, ANON_KEY)
  
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYTlkMzY4NC1kYjkxLTRmYTEtYWY5Ni02OTExZTE1NjBjMDEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoyMDU2NjI5MDM2LCJpYXQiOjE3NDEyNjkwMzYsImVtYWlsIjoiZXhjZWxsZW50aWVAdWdlbnQuYmUiLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl0sInVzZXJyb2xlIjpbImxhcHJlYWRlciJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoicGFzc3dvcmQiLCJ0aW1lc3RhbXAiOjE3NDEyNjkwMzZ9XSwic2Vzc2lvbl9pZCI6ImVkYTkwNGMyLTllYjUtNDM0YS04ZGZlLWQxMjkyMDA3Y2FmMiIsImlzX2Fub255bW91cyI6ZmFsc2V9.gqakyr5TWpknfPJ1fG107B3qm0hIGFg47kwvj3EjcoI'
REFRESH_TOKEN = '0iw1_TL1yWfwZvY_iDs9Sw'

supabase.auth.set_session(ACCESS_TOKEN, REFRESH_TOKEN)

response = supabase.table("laptimes").select("*").execute()

# Check for errors
if response.data:
    print("Laptimes Data:", response.data)
else:
    print("Error:", response)
    
# while not stop_event.is_set():
#         try:
#             dataMyLaps = qMyLaps.get(block=True)       
#             if dataMyLaps:
#                 # Get 'code' (transponder id)
#                 code = dataMyLaps["tag"]
#                 if code != '9992': # Start block, ignore
#                     last_tcp_msg_time = time.time() # To monitor TCP connection
#                 laptimes[code] = dataMyLaps
#                 deviceId = dataMyLaps["location"]
#                 laptime = laptimes[code][deviceId]["lapTime"]
#                 passingTimeUtc = dataMyLaps[deviceId]["rtcTime"]/1000 # is actually UTC, and is sent in ms
#                 numPassings = dataMyLaps[deviceId]["numLaps"]
#                 if "console" in config["outputs"] and config["outputs"]["console"]:
#                     # utcTime = datetime.fromtimestamp(passingTimeUtc).strftime("%Y-%m-%d %H:%M:%S.%f")
#                     # print("Current " + code + ": " + str(numPassings) + " - " + str(passingTimeUtc) + " - " + deviceId)
#                     pass
#                 # Fill log entry
#                 fields["transponder_id"] = code
#                 fields["loop"] = deviceId
#                 fields["utcTimestamp"] = passingTimeUtc
#                 fields["utcTime"] = datetime.fromtimestamp(passingTimeUtc, tz=tz_utc).strftime('%Y-%m-%d %H:%M:%S.%f')
#                 fields["localTime"] = datetime.fromtimestamp(passingTimeUtc).strftime('%Y-%m-%d %H:%M:%S.%f')
#                 fields["lapTime"] = laptime
#                 fields["cameraPreset"] = cam_coordinator.get_active_camera_preset() # Make sure this is updated in the main thread
#                 fields["eventName"], _, _, _ = auto_recorder.get_current_event()       
#                 fields["trackedRider"] = cam_coordinator.get_tracked_rider()