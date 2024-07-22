from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import csv
from datetime import datetime, timedelta

app = FastAPI()

# Serve static files (like buses.js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Real-time data URL
REALTIME_URL = 'https://s3.amazonaws.com/kcm-alerts-realtime-prod/vehiclepositions_pb.json'

@app.get("/")
async def read_index():
    return FileResponse('index.html')

# Function to fetch real-time data
async def fetch_realtime_data(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

# Function to load trips data
def load_trips_data(file_path):
    trips = {}
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['route_id'] == '100162':  # Filter for route 271
                trips[row['trip_id']] = row
    return trips

# Function to load stops data
def load_stops_data(file_path):
    stops = {}
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stops[row['stop_id']] = row
    return stops

@app.get("/api/buses")
async def track_buses():
    # URLs and file paths
    realtime_url = 'https://s3.amazonaws.com/kcm-alerts-realtime-prod/vehiclepositions_pb.json'
    trips_file = 'trips.txt'
    stops_file = 'stops.txt'

    try:
        # Load static data
        trips_data = load_trips_data(trips_file)
        stops_data = load_stops_data(stops_file)

        # Fetch real-time data
        realtime_data = await fetch_realtime_data(realtime_url)

        # Get current time
        current_time = datetime.now()

        # Lists to store active buses
        active_buses = []

        # Process each bus
        for entity in realtime_data['entity']:
            vehicle = entity['vehicle']
            if vehicle['trip']['route_id'] == '100162':  # Filter for route 271
                trip_id = vehicle['trip']['trip_id']
                if trip_id in trips_data:
                    trip = trips_data[trip_id]
                    current_stop = stops_data.get(vehicle['stop_id'], {'stop_name': 'Unknown'})
                    
                    # Check if the bus is currently active
                    is_active = (
                        vehicle['trip']['schedule_relationship'] == 'SCHEDULED' and
                        current_time - datetime.fromtimestamp(vehicle['timestamp']) < timedelta(minutes=10)
                    )
                    
                    bus_info = {
                        'label': vehicle['vehicle']['label'],
                        'direction': 'Westbound' if vehicle['trip']['direction_id'] == 1 else 'Eastbound',
                        'stop': current_stop['stop_name'],
                        'position': {'lat': vehicle['position']['latitude'], 'lon': vehicle['position']['longitude']},
                        'status': vehicle['current_status'],
                        'last_updated': datetime.fromtimestamp(vehicle['timestamp']).isoformat(),
                    }
                    
                    if is_active:
                        active_buses.append(bus_info)

        return active_buses

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


