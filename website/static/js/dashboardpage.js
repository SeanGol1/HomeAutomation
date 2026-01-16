document.addEventListener("DOMContentLoaded", function () {
    let isEditing = false;

    document.getElementById('editLayoutBtn').addEventListener('click', function () {
        isEditing = !isEditing;

        grid.enableMove(isEditing);
        grid.enableResize(isEditing);
        grid.setStatic(!isEditing);

        this.textContent = isEditing ? 'Lock Layout' : 'Edit Layout';
        this.classList.toggle('btn-warning', !isEditing);
        this.classList.toggle('btn-success', isEditing);
    });

    

function updateClock() {
    const now = new Date();

    const est = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));
    const gmt = new Date(now.toLocaleString("en-US", { timeZone: "Europe/Dublin" }));

    document.getElementById("est-time").textContent = est.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    document.getElementById("gmt-time").textContent = gmt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
setInterval(updateClock, 30000);
updateClock();

function fetchSystemStatus() {
    fetch('/system_status')
        .then(response => response.json())
        .then(data => {
            document.getElementById("cpu-usage").textContent = `${data.cpu}%`;
            document.getElementById("ram-usage").textContent = `${data.ram}%`;
            document.getElementById("down-speed").textContent = data.download ? `${data.download} Mbps` : "N/A";
            document.getElementById("up-speed").textContent = data.upload ? `${data.upload} Mbps` : "N/A";
        });
}

function updateBatteryStatus() {
    if ('getBattery' in navigator) {
        navigator.getBattery().then(battery => {
            const percent = Math.round(battery.level * 100);
            document.getElementById("battery-status").textContent = `Battery: ${percent}%`;
        });
    }
}

// Update on load and every 30 seconds
fetchSystemStatus();
updateBatteryStatus();
setInterval(fetchSystemStatus, 30000);
setInterval(updateBatteryStatus, 60000);

let recognition;
let waitingForWakeWord = true;  // start by listening for wake word
let responseBox = document.getElementById("response");



document.getElementById("micBtn").addEventListener("click", () => {
    if (recognition) {
        recognition.stop(); // stop any old instance
    }

    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = true;

    recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
        console.log("Heard:", transcript);

        if (waitingForWakeWord) {
            // Listen for wake word only
            if (transcript.includes("aurora")) {
                responseBox.innerText = "🟢 Wake word 'Aurora' detected! Listening for your command...";
                const utterance = new SpeechSynthesisUtterance("How can I help you?");
                window.speechSynthesis.speak(utterance);
                waitingForWakeWord = false;

                // Switch to single-command mode
                recognition.stop();
                setTimeout(() => listenForCommand(), 1500);
            }
        } else {
            // In command mode, process the command
            responseBox.innerText = "🗣️ Command received: " + transcript;

            // Send command to backend
            fetch("/voice", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: transcript })
            })
                .then(res => res.json())
                .then(data => {
                    responseBox.innerText += "\n🤖 Assistant: " + data.response;
                    const utterance = new SpeechSynthesisUtterance(data.response);
                    window.speechSynthesis.speak(utterance);
                })
                .catch(() => {
                    responseBox.innerText += "\n❌ Error contacting server.";
                });

            // After command processed, go back to wake word listening
            recognition.stop();
            setTimeout(() => startWakeWordListening(), 1000);
        }
    };

    recognition.onerror = (event) => {
        responseBox.innerText = "❌ Error: " + event.error;
        if (event.error === "no-speech" || event.error === "network") {
            recognition.stop();
            setTimeout(() => recognition.start(), 1000);
        }
    };

    recognition.onend = () => {
        // Auto-restart only when waiting for wake word
        if (waitingForWakeWord) {
            recognition.start();
        }
    };

    // Start by listening for wake word
    startWakeWordListening();

    // Helper functions:

    function startWakeWordListening() {
        waitingForWakeWord = true;
        responseBox.innerText = "👂 Listening for 'Aurora'...";
        recognition.continuous = true;
        recognition.start();
    }

    function listenForCommand() {
        waitingForWakeWord = false;
        responseBox.innerText = "📝 Please say your command now...";
        recognition.continuous = false;  // listen once for command
        recognition.start();
    }
});

function runScene(sceneName) {
    fetch(`/run_scene/${encodeURIComponent(sceneName)}`, {
        method: 'POST'
    })
        .then(res => res.json())
        .then(data => {
            alert(`Scene "${sceneName}" has been run.\nResult: ${data.status}`);
            console.log(data);
        })
        .catch(err => {
            alert(`Failed to run scene "${sceneName}".`);
            console.error(err);
        });
}

let map;
let directionsService;
let directionsRenderer;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 7,
        center: { lat: 40.7128, lng: -74.0060 }
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);

    // Autocomplete for home and work
    const homeInput = document.getElementById("home");
    const workInput = document.getElementById("work");

    new google.maps.places.Autocomplete(homeInput, {
        types: ["geocode"],
        componentRestrictions: { country: "ca" }
    });

    new google.maps.places.Autocomplete(workInput, {
        types: ["geocode"],
        componentRestrictions: { country: "ca" }
    });


    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                map.setCenter(userLocation);
                map.setZoom(12);
            },
            () => console.warn("Geolocation failed or denied.")
        );
    }
}

});

$(document).ready(function () {
    function loadSpotifyTrack() {
        fetch('/spotify/spotify_status')
            .then(res => res.json())
            .then(data => {
                if (data && data.item) {
                    document.getElementById('spotify-track').innerHTML = `
                            <strong>${data.item.name}</strong><br>
                            ${data.item.artists.map(a => a.name).join(', ')}
                        `;

                    const icon = document.getElementById('spotify-icon');
                    if (data.is_playing) {
                        icon.classList.remove('fa-play');
                        icon.classList.add('fa-pause');
                    } else {
                        icon.classList.remove('fa-pause');
                        icon.classList.add('fa-play');
                    }

                    document.getElementById('spotify-art-img').src = data.item.album.images[0].url;
                } else {
                    document.getElementById('spotify-track').innerText = 'Not playing';

                }
            });
    }
    setInterval(loadSpotifyTrack, 10000); // refresh every 10s
    loadSpotifyTrack();

});

function spotifyControl(action) {
    fetch(`/spotify/${action}`, { method: 'POST' });
}

function toggleAllLights() {
    fetch('/lightson', { method: 'POST' });
}

function playPause() {
    fetch('/playpause', { method: 'POST' });
}

function turnOffAll() {
    fetch('/lightsoff', { method: 'POST' });
    fetch('/poweroff', { method: 'POST' });
}

function firestickCommand(endpoint) {
    fetch(`/${endpoint}`, { method: 'POST' });
}