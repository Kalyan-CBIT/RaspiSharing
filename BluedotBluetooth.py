import time
from bluedot.btcomm import BluetoothServer
import os
import bluetooth
import subprocess

def out(cmd):
    try:
        res = subprocess.check_output(cmd, shell=True)
        return res
    except:
        return False

def data_received(data):
    print(data)
    s.send(data)
os.system('bluetoothctl discoverable on && bluetoothctl agent NoInputNoOutput')
time.sleep(2)
connected = False
while not connected:
    paired_devices = (out("bluetoothctl paired-devices").decode().split())
    print(1,end="")
    for i in range(0,len(paired_devices),3):
        macAddr,name = paired_devices[i+1],paired_devices[i+2]
        print(macAddr,name)
        res = out('bluetoothctl connect '+macAddr)
        if(res):
            print("connected to",name)
            connected = True
            break
    time.sleep(2)
    
#s = BluetoothServer(data_received)

