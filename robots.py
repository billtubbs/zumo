import pygame
import serial
import struct

# Connection details

# These are specific to the computer you are running
# this code on

# To identify new devices connected to the Raspberry Pi's
# USB ports type lsusb into the shell

# Example:
# Bus 001 Device 006: ID 16c0:0483 VOTI Teensyduino Serial
# Bus 001 Device 005: ID 16c0:0483 VOTI Teensyduino Serial

# To find the port name of each Teensy use the following with
# and without the Teensies plugged in:
# ls /dev/tty*

address = '/dev/tty.usbmodem1421'

class Zumo(object):

    def __init__(self, address=address, baud=9600):

        self.address = address
        self.baud = baud
        self.serial = None
        self.name = None

    def connect(self):

        # Establish connection
        self.serial = serial.Serial(self.address, self.baud)
        #self.serial.open()

        # Check connection by requesting identification
        result = False
        try:
            response = self.get_id()
        except:
            print "Connection to", self.address, "failed."
            self.serial.close()
            return result

        if response.startswith("Zumo"):
            self.name = response
            print "Connection to", self.address, "(" + \
                  response + ") successful."
            result = True

        return result

    def get_id(self):
        self.serial.write('ID')
        return self.serial.readline().rstrip()

    def forward(self, speed=2):
        self.serial.write('F{:1s}'.format(str(speed)))

    def backward(self, speed=2):
        self.serial.write('B{:1s}'.format(str(speed)))

    def right(self, speed=2):
        self.serial.write('R{:1s}'.format(str(speed)))

    def left(self, speed=2):
        self.serial.write('L{:1s}'.format(str(speed)))

    def set_speeds(self, left_speed, right_speed):
        self.serial.write('SS{:4s}'.format(
            struct.pack(">2h", left_speed, right_speed))
        )

    def stop(self):
        self.serial.write('F0')

    def buzzer(self, n=1):
        self.serial.write('N%d' % n)

    def led_yellow(self, n):
        self.serial.write('Y%d' % n)

    def led_green(self, n):
        self.serial.write('Z%d' % n)

    def get_encoder_value(self, side):
        self.serial.write('E{:1s}'.format(side))
        return struct.unpack(">h", self.serial.read(2))[0]

    def get_proximity_value(self, direction):
        self.serial.write('P{:1s}'.format(direction))
        if direction == 'F':
            return (ord(self.serial.read()), ord(self.serial.read()))
        else:
            return ord(self.serial.read())

    def get_compass_a(self):
        self.serial.write('CA')
        return struct.unpack(">3h", self.serial.read(6))

    def get_compass_m(self):
        self.serial.write('CM')
        return struct.unpack(">3h", self.serial.read(6))

    def get_gyro_readings(self):
        self.serial.write('GY')
        return struct.unpack(">3h", self.serial.read(6))

    def get_battery_voltage(self):
        self.serial.write('BA')
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
    zumo.connect()
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
            zumo.set_speeds(left_speed, right_speed)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key in number_keys[0:5]:
                    speed = number_keys.index(event.key) * 100
                elif event.key == pygame.K_y:
                    led_yellow = led_yellow ^ 1
                    zumo.led_yellow(led_yellow)
                elif event.key == pygame.K_z:
                    led_green = led_green ^ 1
                    zumo.led_green(led_green)
                elif event.key == pygame.K_SPACE:
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