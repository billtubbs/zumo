import pygame
import serial
import struct

# Connection details

# These are specific to the computer you are running
# this code on

# To identify new devices connected to the computer's
# USB ports type lsusb into the shell

# Example:
# Bus 001 Device 006: ID 16c0:0483 VOTI Teensyduino Serial
# Bus 001 Device 005: ID 16c0:0483 VOTI Teensyduino Serial

# To find the port name of each device use the following with
# and without the device plugged in:
# ls /dev/tty*
# Or use the following to list availble ports
# python -m serial.tools.list_ports

# Troube-shooting checklists:
#
# Problem connecting to Zumo
# - Check port address (see notes above and variable below)
#
# Problem: Zumo not responding
# - Check correct Arduino sketch loaded on Zumo 'RemoteControl.ino'
# - To send keyboard commands, the Pygame app window must be selected
#   (not the console output window or any other window)
#
# Problem: Zumo motors not moving
# - Check battery power switch on Zumo is set to ON
# - Changed speed setting to 100 or more
#
# Problem: loading Arduino sketch onto Zumo
# - Check correct port and board are selected in Arduino app (
#   see Pololu A-star boards library)


address = '/dev/cu.usbmodem14201'

class Zumo(object):

    def __init__(self, address=address, baud=9600, timeout=1):

        self.address = address
        self.baud = baud
        self.timeout = timeout
        self.serial = None
        self.name = None

    def connect(self):

        # Establish connection
        try:
            self.serial = serial.Serial(self.address, self.baud,
                                        timeout=self.timeout)
        except serial.SerialException:
            print(f"Connection to {self.address} failed.")
            return False

        # Check connection by requesting identification code
        try:
            response = self.get_id()
        except serial.SerialException:
            print(f"Communication to {self.address} failed.")
            self.serial.close()
            return False

        if response.startswith(b"Zumo"):
            self.name = response
            print(f"Connection to {self.address} ({response}) "
                  f"successful.")
            return True

        print(f"Unexpected device ID: '{response.decode('utf8'):s}'")
        return False

    def get_id(self):
        self.serial.write('ID'.encode('utf-8'))
        return self.serial.readline().rstrip()

    def forward(self, speed=2):
        self.serial.write(f'F{speed:1d}'.encode('utf-8'))

    def backward(self, speed=2):
        self.serial.write(f'B{speed:1d}'.encode('utf-8'))

    def right(self, speed=2):
        self.serial.write(f'R{speed:1d}'.encode('utf-8'))

    def left(self, speed=2):
        self.serial.write(f'L{speed:1d}'.encode('utf-8'))

    def set_speeds(self, left_speed, right_speed):
        s = struct.pack(">2h", left_speed, right_speed)
        self.serial.write(b'SS' + s)

    def stop(self):
        self.serial.write('F0'.encode('utf-8'))

    def buzzer(self, n=1):
        self.serial.write(f'N{n:d}'.encode('utf-8'))

    def led_yellow(self, n):
        self.serial.write(f'Y{n:d}'.encode('utf-8'))

    def led_green(self, n):
        self.serial.write(f'Z{n:d}'.encode('utf-8'))

    def get_encoder_value(self, side):
        self.serial.write(f'E{side:1s}'.encode('utf-8'))
        return struct.unpack(">h", self.serial.read(2))[0]

    def get_proximity_value(self, direction):
        self.serial.write(f'P{direction:1s}'.encode('utf-8'))
        if direction == 'F':
            return (ord(self.serial.read()), ord(self.serial.read()))
        else:
            return ord(self.serial.read())

    def get_compass_a(self):
        self.serial.write('CA'.encode('utf-8'))
        return struct.unpack(">3h", self.serial.read(6))

    def get_compass_m(self):
        self.serial.write('CM'.encode('utf-8'))
        return struct.unpack(">3h", self.serial.read(6))

    def get_gyro_readings(self):
        self.serial.write('GY'.encode('utf-8'))
        return struct.unpack(">3h", self.serial.read(6))

    def get_battery_voltage(self):
        self.serial.write('BA'.encode('utf-8'))
        return struct.unpack(">h", self.serial.read(2))[0]

    def __repr__(self):
        return "Zumo(address='%s', baud=%d)" % (self.address, self.baud)


def test():
    """Simple demonstration code to show how to control
    the Zumo 32U4 robot using pygame."""

    print("\n ------------- robots.py -------------\n")
    print("Use the following keys to control the robot.")
    print("  Cursors - forward, back, turn left, turn right")
    print("  SPACE   - buzzer")
    print("  Y       - yellow LED")
    print("  G       - green LED")
    print("  0-4     - change speed setting (starts at 2)")
    print("  B       - battery voltage")
    print("  ESCAPE  - quit.")

    zumo = Zumo()
    if not zumo.connect():
        raise ValueError("Connection problem")
    pygame.init()

    speed = 200

    done = False
    clock = pygame.time.Clock()

    number_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3,
                   pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                   pygame.K_8, pygame.K_9]

    left_speed, right_speed = (0, 0)
    led_yellow, led_green = (0, 0)

    while not done:

        # Check keys pressed
        keys = pygame.key.get_pressed()

        previous_speeds = (left_speed, right_speed)
        left_speed, right_speed = (0, 0)

        if keys[pygame.K_UP]:
            left_speed += speed
            right_speed += speed
        elif keys[pygame.K_DOWN]:
            left_speed -= speed
            right_speed -= speed

        if keys[pygame.K_LEFT]:
            left_speed -= speed
            right_speed += speed
        elif keys[pygame.K_RIGHT]:
            left_speed += speed
            right_speed -= speed

        if (left_speed, right_speed) != previous_speeds:
            print("Motors activated")
            zumo.set_speeds(left_speed, right_speed)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key in number_keys[0:5]:
                    speed = number_keys.index(event.key) * 100
                    print(f"Speed changed to {speed:d}")
                elif event.key == pygame.K_y:
                    led_yellow = led_yellow ^ 1
                    print("Yellow LED changed")
                    zumo.led_yellow(led_yellow)
                elif event.key == pygame.K_z:
                    led_green = led_green ^ 1
                    print("Green LED changed")
                    zumo.led_green(led_green)
                elif event.key == pygame.K_SPACE:
                    print("Buzzer")
                    zumo.buzzer()
                elif event.key == pygame.K_e:
                    encoders = (zumo.get_encoder_value('L'),
                                zumo.get_encoder_value('R'))
                    print("Encoders: {}".format(encoders))
                elif event.key == pygame.K_p:
                    proximities = (zumo.get_proximity_value('L'),
                                   zumo.get_proximity_value('F'),
                                   zumo.get_proximity_value('R'))
                    print("Proximities: {}".format(proximities))
                elif event.key == pygame.K_g:
                    angular_velocities = zumo.get_gyro_readings()
                    print("Angular velocities: {}".format(angular_velocities))
                elif event.key == pygame.K_c:
                    compass_m = zumo.get_compass_m()
                    print("Compass: {}".format(compass_m))
                elif event.key == pygame.K_b:
                    battery_voltage = (zumo.get_battery_voltage())
                    print("Batteries: {}".format(battery_voltage))
                elif event.key == pygame.K_ESCAPE:
                    done = True

        clock.tick()


if __name__ == "__main__":
    test()