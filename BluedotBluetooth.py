import time
from bluedot.btcomm import BluetoothServer,BluetoothClient
import os
import bluetooth
import subprocess
import json
from wifi import Cell,scheme
wpa_supplicant_conf = "/etc/wpa_supplicant/wpa_supplicant.conf"
sudo_mode = "sudo "


def wifi_connect(ssid, psk):
    # write wifi config to file
    f = open('wifi.conf', 'w')
    f.write('country=GB\n')
    f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
    f.write('update_config=1\n')
    f.write('\n')
    f.write('network={\n')
    f.write('    ssid="' + ssid + '"\n')
    f.write('    psk="' + psk + '"\n')
    f.write('}\n')
    f.close()

    cmd = 'mv wifi.conf ' + wpa_supplicant_conf
    cmd_result = ""
    cmd_result = os.system(cmd)
    print(cmd + " - " + str(cmd_result))
    # restart wifi adapter
    cmd = sudo_mode + 'ifdown wlan0'
    cmd_result = os.system(cmd)
    print(cmd + " - " + str(cmd_result))
    time.sleep(2)
    cmd = sudo_mode + 'ifup wlan0'
    cmd_result = os.system(cmd)
    print(cmd + " - " + str(cmd_result))
    time.sleep(10)
    cmd = 'iwconfig wlan0'
    cmd_result = os.system(cmd)
    print(cmd + " - " + str(cmd_result))
    cmd = 'ifconfig wlan0'
    cmd_result = os.system(cmd)
    print(cmd + " - " + str(cmd_result))

    p = subprocess.Popen(['ifconfig', 'wlan0'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    out, err = p.communicate()

    ip_address = "<Not Set>"

    for l in out.split('\n'):
        if l.strip().startswith("inet addr:"):
            ip_address = l.strip().split(' ')[1].split(':')[1]
    print(ip_address)
    return ip_address

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
    res = json.loads(data)
    if "ssid" in res and "pass" in res:
        print(res["ssid"],res["pass"])
        #wifi_connect(res["ssid"],res["pass"])
        
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
cname,caddr = '',''
while not connected:
    paired_devices = (out("bluetoothctl paired-devices").decode().split())
    paired_devices = modifyPaired(paired_devices)
    print(paired_devices)
    for p in paired_devices:
        macAddr,name = p['mAddr'],p['name']
        print(macAddr,name)
        res = out('bluetoothctl connect '+macAddr)
        if(res):
            print("connected to",name)
            cname,caddr = name,macAddr
            connected = True
            break
    time.sleep(2)    
s = BluetoothServer(data_received)
while True:
    print(s.client_address)
    time.sleep(4)
    pass

