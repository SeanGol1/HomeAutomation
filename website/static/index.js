
 $(document).ready(function(){
  
    $('.lampswitch').on('click', function(e) {
        e.preventDefault()
        const ip = $(this).data('ip');
        fetch(`/lampswitch/${ip}`,{
            method: "POST",            
        })
        .then(response => {
            console.log(response);
            return response.json();
        })
        .then(data => {
            console.log("Response from /lampswitch:", data);
            console.log(`#lampswitch-${ip}`)
            //id = `lampswitch-${ip}`
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

    $('.lampbright').on('click', function(e) {
        e.preventDefault()
        const ip = $(this).data('ip');
        fetch(`lampbright/${ip}`,{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });

    $('.brightnessSlider').on('change', function(e) {
        e.preventDefault()
        const ip = $(this).data('ip');
        const brightness = $(this).val();
        data = {
            ip: ip ,
            brightness:brightness
        };
        fetch('/setlampbright',{            
            method: "POST",
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then((_res) => {
        });
        return false;
    });

    $('.lightcolour').on('change', function(e) {
        e.preventDefault()
        const ip = $(this).data('ip');
        const colour = $(this).val();
        data = {
            ip: ip ,
            colour:colour
        };
        fetch('/setcolour',{            
            method: "POST",
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then((_res) => {
        });
        return false;
    });

    $('.deleteDevice').on('click', function(e) {
    e.preventDefault();
    const ip = $(this).data('ip');
    if (!confirm(`Are you sure you want to delete device with IP: ${ip}?`)) return;

    fetch('/deleteDevice', {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: ip })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            $(`#obj${CSS.escape(ip)}`).remove();
        } else {
            alert("Failed to delete device.");
        }
    });
});
    
    /*$('#moodlight').on('click', function(e) {
        e.preventDefault()
        fetch('moodlight',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    
    $('#lightsoff').on('click', function(e) {
        e.preventDefault()
        fetch('lightsoff',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });

    $('#next_episode').on('click', function(e) {
        e.preventDefault()
        fetch('next_episode',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#spotify').on('click', function(e) {
        e.preventDefault()
        fetch('spotify',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#playpause').on('click', function(e) {
        e.preventDefault()
        fetch('playpause',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    
    $('#poweroff').on('click', function(e) {
        e.preventDefault()
        fetch('poweroff',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
     
    $('#formula1').on('click', function(e) {
        e.preventDefault()
        fetch('formula1',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });

   $('#recent_show').on('click', function(e) {
        e.preventDefault()
        fetch('recent_show',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });

    $('#wakeup').on('click', function(e) {
        e.preventDefault()
        fetch('wakeup',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
          
     */
  });