import time
from bluedot.btcomm import BluetoothServer
import os
import bluetooth
import subprocess
from wifi import Cell,scheme

def ssid_discovered():
    cells = Cell.all('wlan0')
    wifi_info = 'Found ssid: \n'
    for current in range(len(Cells)):
        wifi_info+=Cells[current].ssid+"\n"
    print(wifi_info)

def out(cmd):
    try:
        res = subprocess.check_output(cmd, shell=True)
        return res
    except:
        return False

def data_received(data):
    print(data)
    s.send(data+"kalyan")
def modifyPaired(paired_devices):
    res = []
    i,p=0,0
    print(paired_devices)
    while i<len(paired_devices):
        if paired_devices[i]=='Device':      
            res.append({'mAddr':paired_devices[i+1],'name':""})
            i+=2
            p+=1
        else:
            res[p-1]['name']+=paired_devices[i]
            i+=1
    return res
        
        
    
    
os.system('bluetoothctl power on && bluetoothctl discoverable on && bluetoothctl agent NoInputNoOutput')
time.sleep(2)
connected = False
while not connected:
    paired_devices = (out("bluetoothctl paired-devices").decode().split())
    print(1,end="")
    paired_devices = modifyPaired(paired_devices)
    print(paired_devices)
    for p in paired_devices:
        macAddr,name = p['mAddr'],p['name']
        print(macAddr,name)
        res = out('bluetoothctl connect '+macAddr)
        if(res):
            print("connected to",name)
            connected = True
            break
    time.sleep(2)    
s = BluetoothServer(data_received)
while True:
    print(s.client_address)
    time.sleep(10)
    pass

