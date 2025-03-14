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

# Parameters
batch_size = 1000  
stop_event = threading.Event()
tz_utc = timezone.utc
csv_counter = 1  # Start nummering voor csv-bestanden
utc_time_start = datetime(2025, 3, 13, 0, 0, 0, tzinfo=timezone.utc)
utc_time_end = datetime(2025, 3, 14, 0, 0, 0, tzinfo=timezone.utc)
rtc_time_start = int(utc_time_start.timestamp() * 1000)
rtc_time_end = int(utc_time_end.timestamp() * 1000)

# Functie om data op te halen
def fetch_all_data():
    offset = 0
    all_data = []
    while True:
        response = supabase.table("laptimes").select("*").range(offset, offset + batch_size - 1).execute()
        if not response.data:
            break  
        all_data.extend(response.data)
        offset += batch_size
    return all_data

# We houden de eerder opgeslagen gegevens bij in een set
seen_data = set()

# Functie om een nieuwe CSV-bestandsnaam te genereren
def get_next_csv_filename():
    global csv_counter
    directory = 'Metingen'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, f'test{csv_counter}.csv')
    csv_counter += 1
    return filename

# Functie om alle gefilterde data in één CSV-bestand te schrijven
def write_to_csv(data_list):
    if not data_list:
        print("Geen gegevens om te schrijven.")
        return
    
    file_path = get_next_csv_filename()
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "transponder_id", "loop", "utcTimestamp", "utcTime", "lapTime", 
            "lapSpeed", "maxSpeed", "cameraPreset", "cameraPan", 
            "cameraTilt", "cameraZoom", "eventName", "recSegmentId", "trackedRider"
        ])
        
        new_data_added = 0
        for fields in data_list:
            # Maak een tuple van de relevante velden om duplicaten te identificeren
            record_tuple = (
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
            )
            
            # Controleer of dit record al eerder is opgeslagen
            if record_tuple not in seen_data:
                # Voeg het record toe aan de set van eerder opgeslagen gegevens
                seen_data.add(record_tuple)
                # Schrijf het record naar de CSV
                writer.writerow([value for value in record_tuple])
                new_data_added += 1
        
        if new_data_added > 0:
            print(f"{new_data_added} nieuwe records geschreven naar {file_path}")
        else:
            print("Geen nieuwe gegevens om toe te voegen.")

# Hoofdloop voor periodieke fetch en verwerking
def main_loop():
    while not stop_event.is_set():
        print("Fetching nieuwe data...")
        all_records = fetch_all_data()
        
        # Filteren van data
        device_ids = ["L01", "L02", "L03", "L04", "L05", "L06", "L07"]
        filtered_data = []
        
        for record in all_records:
            for device in device_ids:
                rtc_time = record.get(f"{device}.rtcTime")
                if rtc_time and rtc_time_start <= rtc_time <= rtc_time_end:
                    filtered_data.append({
                        "transponder_id": record["tag"],
                        "loop": record["location"],
                        "utcTimestamp": rtc_time / 1000,
                        "utcTime": datetime.fromtimestamp(rtc_time / 1000, tz=tz_utc).strftime('%Y-%m-%d %H:%M:%S.%f'),
                        "lapTime": record.get(f"{device}.lapTime"),
                        "eventName": "Vlaamse wielerschool",
                        "trackedRider": "",
                    })
                    break  # Stop zodra er een match is
        
        print(f"Gefilterde records: {len(filtered_data)} gevonden!")
        
        # Wegschrijven naar CSV
        write_to_csv(filtered_data)
        
        # Wachten tot de volgende fetch
        time.sleep(30)

# Start de main loop in een thread
thread = threading.Thread(target=main_loop)
thread.start()

# Run de hoofdloop voor 5 minuten
time.sleep(300)
stop_event.set()
thread.join()

print("Hoofdloop beëindigd.")