import tinytuya

# Connect to Device
d = tinytuya.BulbDevice(
    dev_id='eb4eb54574e97932beiy1z',
    address='192.168.0.19',      # Or set to 'Auto' to auto-discover IP address
    local_key='pY)=7X#`Q<gYDG3~')

d.set_version(3.3) 
# Get Status
data = d.status() 
print('set_status() result %r' % data)

# Turn On
d.turn_on()

# Turn Off
d.turn_off()