
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

            function spotifyControl(action) {
                fetch(`/spotify/${action}`, { method: 'POST' });
            }

        });

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

    //     $(document).ready(function () {
    //     let stepCount = 0;
    //     $('#addStep').on('click', function (e) {
    //             e.preventDefault()
    //     const stepId = `step-${stepCount++}`;
    //     const stepHTML = `
    //         <div class="card bg-dark text-light mb-3 p-3" id="${stepId}">
    //         <div class="row">
    //             <div class="col-md-3">
    //             <label>Device</label>
    //             <select name="steps[${stepId}][device]" class="form-select" required>
    //                 {% for device in deviceList %}
    //                 <option value="{{ device.ip }}">{{ device.name }}</option>
    //                 {% endfor %}
    //             </select>
    //             </div>
    //             <div class="col-md-3">
    //             <label>Action</label>
    //             <select name="steps[${stepId}][action]" class="form-select" required onchange="toggleParams(this)">
    //                 <option value="toggle">Toggle Power</option>
    //                 <option value="set_brightness">Set Brightness</option>
    //                 <option value="set_color">Set Color</option>
    //             </select>
    //             </div>
    //             <div class="col-md-3 param brightness d-none">
    //             <label>Brightness (%)</label>
    //             <input type="range" min="0" max="100" name="steps[${stepId}][brightness]" class="form-range">
    //             </div>
    //             <div class="col-md-3 param color d-none">
    //             <label>Color</label>
    //             <input type="color" name="steps[${stepId}][color]" class="form-control form-control-color">
    //             </div>
    //         </div>
    //         </div>
    //     `;

    //     document.getElementById('stepsContainer').insertAdjacentHTML('beforeend', stepHTML);
    //     });


    //     function toggleParams(select) {
    //     const card = select.closest('.card');
    //     const brightness = card.querySelector('.brightness');
    //     const color = card.querySelector('.color');

    //     brightness.classList.add('d-none');
    //     color.classList.add('d-none');

    //     if (select.value === 'set_brightness') {
    //         brightness.classList.remove('d-none');
    //     } else if (select.value === 'set_color') {
    //         color.classList.remove('d-none');
    //     }
    //     }
    // });

