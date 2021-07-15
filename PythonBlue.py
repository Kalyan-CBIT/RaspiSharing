#!/usr/bin/python3
'''import os,sys,time,pexpect

def findaddress():
  address=''
  p = pexpect.spawn('hcitool scan', encoding='utf-8')
  p.logfile_read = sys.stdout
  mylist = ['E4\:17\:D8\:[0-9A-F].[:][0-9A-F].[:][0-9A-F].', '16\:04\:18\:[0-9A-F].[:][0-9A-F].[:][0-9A-F].',pexpect.EOF]
  p.expect(mylist)
  address=p.after
  if address==pexpect.EOF:
    return ''
  else:
    return address
    
def setbt(address):
  response=''
  p = pexpect.spawn('bluetoothctl', encoding='utf-8')
  p.logfile_read = sys.stdout
  p.expect('#')
  p.sendline("remove "+address)
  p.expect("#")
  p.sendline("scan on")

  mylist = ["Discovery started","Failed to start discovery","Device "+address+" not available","Failed to connect","Connection successful"]
  while response != "Connection successful":
    p.expect(mylist)
    response=p.after
    p.sendline("connect "+address)
    time.sleep(1)
  p.sendline("quit")
  p.close()
  #time.sleep(1)
  return


address='' 
while address=='':
  address=findaddress()
  time.sleep(1)
  
print (address," found")
setbt(address)    
    
'''

import time
import pexpect
import subprocess
import sys
 
class BluetoothctlError(Exception):
    """This exception is raised, when bluetoothctl fails to start."""
    pass
 
 
class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""
 
    def __init__(self):
        out = subprocess.check_output("rfkill unblock bluetooth", shell = True)
        self.child = pexpect.spawn("bluetoothctl", echo = False)
 
    def get_output(self, command, pause = 0):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.child.send(command + "\n")
        time.sleep(pause)
        start_failed = self.child.expect(["bluetooth", pexpect.EOF])
 
        if start_failed:
            raise BluetoothctlError("Bluetoothctl failed after running " + command)
 
        return self.child.before.split(b'\r\n')
 
    def start_scan(self):
        """Start bluetooth scanning process."""
        try:
            out = self.get_output('scan on')
        except BluetoothctlError as e:
            print(e)
            return None
 
    def make_discoverable(self):
        """Make device discoverable."""
        try:
            out = self.get_output("discoverable on")
        except BluetoothctlError as e:
            print(e)
            return None
 
    def parse_device_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        string_valid = True#not any(keyword in info_string for keyword in block_list)
        if string_valid:
            try:
                device_position = info_string.index(b"Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(b" ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        "name": attribute_list[2]
                    }
 
        return device
 
    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        try:
            out = self.get_output("devices")
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            available_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)
 
            return available_devices
 
    def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        try:
            out = self.get_output("paired-devices")
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            paired_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)
 
            return paired_devices
 
    def get_discoverable_devices(self):
        """Filter paired devices out of available."""
        available = self.get_available_devices()
        paired = self.get_paired_devices()
 
        return [d for d in available if d not in paired]
 
    def get_device_info(self, mac_address):
        """Get device info by mac address."""
        try:
            out = self.get_output("info " + mac_address)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            return out
 
    def pair(self, mac_address):
        """Try to pair with a device by mac address."""
        try:
            out = self.get_output("pair " + mac_address, 10)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to pair", "Pairing successful", pexpect.EOF])
            success = True if res == 1 else False
            return success
 
    def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            out = self.get_output("remove " + mac_address, 3)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["not available", "Device has been removed", pexpect.EOF])
            success = True if res == 1 else False
            return success
 
    def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            out = self.get_output("connect " + mac_address, 2)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to connect", "Connection successful", pexpect.EOF])
            success = True if res == 1 else False
            return success
 
    def disconnect(self, mac_address):
        """Try to disconnect to a device by mac address."""
        try:
            out = self.get_output("disconnect " + mac_address, 2)
        except BluetoothctlError as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to disconnect", "Successful disconnected", pexpect.EOF])
            success = True if res == 1 else False
            return success

def newConnection(bl):
    bl.start_scan()
    time.sleep(6)
    disc = bl.get_available_devices()
    available_macs = {}
    available_phones = {}
    for d in disc:
        available_macs[d['mac_address'].decode()] = d['name'].decode()
    for m,n in available_macs.items():
        info = bl.get_device_info(m)
        k=0
        for i in info:
            i = i.decode()
            idx = i.find('Icon')
            if (idx>-1 and i[idx+6:]=='phone'):
                available_phones[m] = n
    for m,n in available_phones.items():
        print("Trying to connect",n)
        if(n!='KX5' and n!='Amirul' and n!='hancy' and bl.connect(m)):
            print("Connected")
            break
    print(available_macs)
 
if __name__ == "__main__":
 
    print("Init bluetooth...")
    bl = Bluetoothctl()
    print("Ready!")
    bl.start_scan()
    time.sleep(5)
    bl.make_discoverable()
    paired = bl.get_paired_devices()
    connected = False
    for p in paired:
        print("Trying to connect",p['name'].decode())
        if bl.connect(p['mac_address'].decode()):
            print('connected')
            connected = True
            break
    if not connected:
        newConnection(bl)
'''    
    time.sleep(7)
    
    #print(bl.get_device_info('04:79:70:87:E6:E1')[0].decode())
            
    paired_devices = bl.get_paired_devices()
    for d in paired_devices:
        print(str(d['mac_address'])[2:-1],str(d['name'][1:]))
    if (len(paired_devices)>0):
        res = bl.connect(str(paired_devices[0]['mac_address'])[1:])
    else:
        #bl.pair('04:79:70:87:E6:E1')
        pass
    print(res)   
    bl.start_scan()
    print("Scanning for 10 seconds...")
    for i in range(0, 6):
        print(i)
        time.sleep(1)
    avail_devices = bl.get_discoverable_devices()  '''
