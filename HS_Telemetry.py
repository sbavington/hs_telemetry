#!/usr/bin/python3
import threading
import time
import datetime
from pexpect import pxssh

servers = ['10.0.2.189']
threads = []
user = 'root'
passwd = 'root'
pod_device_codes =[
    {'hex':'0x18','type':'f','name':'Board Temp'},
    {'hex':'0x20','type':'f','name':'12 Volt 0 Volts'},
    {'hex':'0x21','type':'f','name':'12 Volt 0 Amps'},
    {'hex':'0x22','type':'f','name':'12 Volt 1 Volts'},
    {'hex':'0x23','type':'f','name':'12 Volt 1 Amps'},
    {'hex':'0x24','type':'f','name':'3v3_MGMT Voltage'},
    {'hex':'0x25','type':'f','name':'3v3 Volts'},
    {'hex':'0x26','type':'f','name':'3v3 Amps'},
    {'hex':'0x27','type':'f','name':'5 Volt Volts'},
    {'hex':'0x28','type':'f','name':'5 Volt Amps'}
]

lc_device_codes =[
    {'hex': '0x18', 'type': 'f', 'name': 'Board Temp'},
    {'hex': '0x19', 'type': 'f', 'name': 'FPGA Temp'},
    {'hex': '0x20', 'type': 'f', 'name': '12 voltage Volts'},
    {'hex': '0x21', 'type': 'f', 'name': '3v3_mgmt volts'},
    {'hex': '0x22', 'type': 'f', 'name': '3v0 voltage Volts'},
    {'hex': '0x23', 'type': 'f', 'name': '2v5 voltage'},
    {'hex': '0x24', 'type': 'f', 'name': '5v0_IMR voltage Volts'},
    {'hex': '0x25', 'type': 'f', 'name': '5v0_IMR current Amps'},
    {'hex': '0x26', 'type': 'f', 'name': 'VccVccpEramsLhps voltage Volts'},
    {'hex': '0x27', 'type': 'f', 'name': 'VccVccpEramsLhps [0] current AMPS'},
    {'hex': '0x28', 'type': 'f', 'name': 'VccVccpEramsLhps [1] current Amps'},
    {'hex': '0x29', 'type': 'f', 'name': '1v8 voltage in Volts'},
    {'hex': '0x2A', 'type': 'f', 'name': '1v8 current Amps'}
]

def login(lognum, server ,user,pawsswd):
    try:
        session.login(server, user, password=passwd)

    except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            print('{:4d}\t{:15s}\t{}\t\tLogin'.format(lognum, server, datetime.date.today()))
            # print ('Login to {}'.format(host))
    commands = [
        {'command':'I2cOp list', 'wait': 0},
    ]
    for command in commands:
        #print('Command for {}: {}'.format(server,command))
        sessionCommand(lognum,server,session,command.get('command'),command.get('wait'))

def sessionCommand(logNum,server,session,command,wait = 1):
    try:
        if command is None:return
        session.sendline(command)
        session.prompt()
        lines = session.before.decode()
        pod_devices = []
        lc_devices =[]
        for line in lines.splitlines():
            if 'pwrmgmt/pod-if/' in line:
                pod_devices.append(line.strip())
            if 'pwrmgmt/smbkpln/' in line:
                lc_devices.append(line.strip())
        for pod_device in pod_devices:
            for register in pod_device_codes:
                hex_register = register.get('hex')
                return_type = register.get('type')
                device_name = register.get('name')
                #print ('Server: {}, Name: {}, Device: {} Register: {} return type: {}'.format(server, device_name, device, hex_register, return_type))
                send_command = 'I2cOp rdreg{} {} {}'.format(return_type,pod_device,hex_register)
                time.sleep(0.5)
                #print (send_command)
                session.sendline(send_command)
                session.prompt()
                lines = session.before.decode()
                for line in lines.splitlines():
                    if "ERR" not in line and 'I2cOp' not in line:
                        print('{} {} {} {}'.format(server,device_name,send_command,line.strip()))
        for lc_device in lc_devices:
            for register in lc_device_codes:
                hex_register = register.get('hex')
                return_type = register.get('type')
                device_name = register.get('name')
                #print ('Server: {}, Name: {}, Device: {} Register: {} return type: {}'.format(server, device_name, device, hex_register, return_type))
                send_command = 'I2cOp rdreg{} {} {}'.format(return_type,lc_device,hex_register)
                time.sleep(0.5)
                #print (send_command)
                session.sendline(send_command)
                session.prompt()
                lines = session.before.decode()
                for line in lines.splitlines():
                    if "ERR" not in line and 'I2cOp' not in line:
                        print('{} {} {} {}'.format(server,device_name,send_command,line.strip()))
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

if __name__ == '__main__':
    lognum = 0
    for server in servers:
        session = pxssh.pxssh()
        print(server)
        lognum = lognum + 1
        t = threading.Thread(name='CMM_Login', target=login, args=(lognum, server, user, passwd))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()
    time.sleep(10)