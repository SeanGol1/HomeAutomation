
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
    //const body = document.body;

    const savedMode = localStorage.getItem('darkMode');
    const isDarkMode = savedMode === null ? true : savedMode === 'true'

    // Set dark mode as default            
    toggle.checked = isDarkMode;
    document.body.classList.toggle('dark-mode', toggle.checked);
    //body.classList.add('dark-mode');

    toggle.addEventListener('change', function () {
        const isDark = this.checked;
        localStorage.setItem('darkMode', isDark);
        document.body.classList.toggle('dark-mode', isDark);

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










});