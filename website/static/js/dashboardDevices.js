document.addEventListener('DOMContentLoaded', () => {
  let selectedRoom = null;

  const rooms = document.querySelectorAll('svg g');
  const devices = document.querySelectorAll('.device-card');

  rooms.forEach(room => {
  room.addEventListener('click', () => {
    const roomId = room.id;
    const shape = room.querySelector('.room');

    if (selectedRoom === roomId) {
      selectedRoom = null;
      shape.classList.remove('active');
    } else {
      selectedRoom = roomId;

      rooms.forEach(r => {
        const s = r.querySelector('.room');
        if (s) s.classList.remove('active');
      });

      shape.classList.add('active');
    }

    filterDevices();
  });
});


  function filterDevices() {
    devices.forEach(device => {
      const deviceRoom = device.dataset.room;

      if (!selectedRoom || deviceRoom === selectedRoom) {
        device.style.display = '';
      } else {
        device.style.display = 'none';
      }
    });
  }
});
