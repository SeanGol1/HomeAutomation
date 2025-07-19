
    let grid;
        document.addEventListener("DOMContentLoaded", function () {
            grid = GridStack.init({
                float: false,
                //cellHeight: '120px',
                margin: 5,
                staticGrid: true
            });

            // Load saved layout if available
            const savedLayout = localStorage.getItem("gridLayout");
            if (savedLayout) {
                try {
                    const layout = JSON.parse(savedLayout);
                    grid.load(layout);
                } catch (e) {
                    console.error("Invalid layout data", e);
                }
            }

            const clock = new FlipClock(document.getElementById('flip-clock'), {
                clockFace: 'TwentyFourHourClock',
                showSeconds: true
            });

            
            const toggle = document.getElementById('darkModeToggle');
            document.body.classList.toggle('dark-mode', toggle.checked);
            // const toggle = document.querySelector('.switch__input');
            const body = document.body;

            // Set dark mode as default
            toggle.checked = true;
            body.classList.add('dark-mode');

            toggle.addEventListener('change', function () {
                const isDark = this.checked;
                document.body.classList.toggle('dark-mode', isDark);

                // // Target cards and navbars
                // document.querySelectorAll('.card').forEach(card => {
                //     card.classList.toggle('bg-dark', isDark);
                //     card.classList.toggle('text-light', isDark);
                //     card.classList.toggle('bg-light', !isDark);
                //     card.classList.toggle('text-dark', !isDark);
                // });

                // document.querySelectorAll('#sidebar').forEach(nav => {
                //     nav.classList.toggle('bg-dark', isDark);
                //     nav.classList.toggle('text-light', isDark);
                //     nav.classList.toggle('bg-light', !isDark);
                //     nav.classList.toggle('text-dark', !isDark);
                // });
            });
        });

        function saveLayout() {
            const layout = grid.save(false);  // 'false' means save full layout with content
            localStorage.setItem("gridLayout", JSON.stringify(layout));
            alert("Layout saved!");
        }

        function resetLayout() {
            localStorage.removeItem("gridLayout");
            location.reload();
        }

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


        function refreshDeviceStatus() {
            fetch('/get_device_status')
                .then(res => res.json())
                .then(devices => {
                    devices.forEach(d => {
                        const button = document.querySelector(`.lampswitch[data-ip="${d.ip}"]`);
                        if (button) {
                            button.classList.toggle('btn-success', d.state);
                            button.classList.toggle('btn-danger', !d.state);
                        }

                        const slider = document.querySelector(`.brightnessSlider[data-ip="${d.ip}"]`);
                        if (slider && d.brightness !== null) {
                            slider.value = d.brightness;
                        }

                        const color = document.querySelector(`.lightcolour[data-ip="${d.ip}"]`);
                        if (color && d.colour) {
                            color.value = d.colour;
                        }
                    });
                });
        }

        setInterval(refreshDeviceStatus, 10000);  // every 10 seconds
        refreshDeviceStatus();  // on load

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

                            document.getElementById('spotify-art-img').src = data.item.album.images[0].url;
                        } else {
                            document.getElementById('spotify-track').innerText = 'Not playing';
                            //document.getElementById('spotify-art-img').innerText = 'Not playing';

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


        $(document).ready(function () {
            $('.lampswitch').on('click', function (e) {
                e.preventDefault()
                const ip = $(this).data('ip');
                fetch(`/lampswitch/${ip}`, {
                    method: "POST",
                })
                    .then(response => {
                        return response.json();
                    })
                    .then(data => {
                        const id = `lampswitch-${ip}`;
                        const safeId = CSS.escape(id);
                        if (data.isOn === true) {
                            $(`#${safeId}`).removeClass('btn-danger').addClass('btn-success');
                        } else {
                            $(`#${safeId}`).removeClass('btn-success').addClass('btn-danger');
                        }
                    });

                return false;
            });
        });

        document.querySelectorAll('.brightnessSlider').forEach(slider => {
            slider.addEventListener('change', () => {
                const ip = slider.dataset.ip;
                const brightness = slider.value;
                fetch('/setlampbright', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip, brightness })
                });
            });
        });

        document.querySelectorAll('.lightcolour').forEach(picker => {
            picker.addEventListener('change', () => {
                const ip = picker.dataset.ip;
                const colour = picker.value;
                fetch('/setcolour', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip, colour })
                });
            });
        });

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


