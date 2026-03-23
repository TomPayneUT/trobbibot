import serial
import time


ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

def send_command(cmd):
    ser.write(cmd.encode())
    print(f'sent: {cmd}')

if __name__ == '__main__':
    send_command('F')
    time.sleep(2)
    send_command('S')
    time.sleep(.5)
    send_command('B')
    time.sleep(1)
    send_command('S')

