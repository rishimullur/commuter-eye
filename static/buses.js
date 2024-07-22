// Initialize the map
var map = L.map('map').setView([47.6162, -122.2665], 11); // Center between Seattle and Bellevue

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Dictionary to keep track of bus markers
var busMarkers = {};

// Custom icon for buses
function createBusIcon(direction) {
    return L.divIcon({
        className: 'bus-icon',
        html: direction === 'Eastbound' ? '→' : '←',
        iconSize: [20, 20]
    });
}

// Function to update bus positions
function updateBusPositions(buses) {
    buses.forEach(bus => {
        var lat = bus.position.lat;
        var lon = bus.position.lon;
        var label = bus.label;

        var popupContent = `
            <strong>${label}</strong><br>
            Direction: ${bus.direction}<br>
            Stop: ${bus.stop}<br>
            Status: ${bus.status}<br>
            Last Updated: ${new Date(bus.last_updated).toLocaleString()}
        `;

        // If the bus marker exists, update its position and popup content
        if (busMarkers[label]) {
            busMarkers[label].setLatLng([lat, lon]);
            busMarkers[label].setIcon(createBusIcon(bus.direction));
            busMarkers[label].getPopup().setContent(popupContent);
        } else {
            // Create a new marker for the bus
            var marker = L.marker([lat, lon], {icon: createBusIcon(bus.direction)}).addTo(map);
            marker.bindPopup(popupContent);
            busMarkers[label] = marker;
        }

        // Check for specific conditions and alert
        if (bus.direction === 'Eastbound' && bus.stop_id === '10912') {
            alert(`Bus ${label} is starting at stop 10912 (Eastbound)`);
        } else if (bus.direction === 'Westbound' && bus.next_stop_id === '67655') {
            alert(`Bus ${label} has next stop 67655 (Westbound)`);
        }
    });

    // Update info panel
    updateInfoPanel(buses);
}

// Function to update the info panel
function updateInfoPanel(buses) {
    var infoHtml = '<h4>Route 271 Buses</h4>';
    buses.forEach(bus => {
        infoHtml += `
            <p>
                <strong>${bus.label}</strong> (${bus.direction})<br>
                Status: ${bus.status}<br>
                Stop: ${bus.stop}<br>
                Last Updated: ${new Date(bus.last_updated).toLocaleString()}
            </p>
        `;
    });
    document.getElementById('bus-info').innerHTML = infoHtml;
}

// Fetch bus data and update the map
function fetchBusData() {
    fetch('/api/buses')
        .then(response => response.json())
        .then(data => {
            updateBusPositions(data);
        })
        .catch(error => console.error('Error fetching bus data:', error));
}

// Fetch bus data every 5 seconds
setInterval(fetchBusData, 1000);
fetchBusData();

