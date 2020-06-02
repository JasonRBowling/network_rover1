# requires python3 and pygame

# autopep8 fixes any indentation issues

# modfied from joystick code at http://programarcadegames.com/

#prerequisites:
#sudo apt-get install python3 python3-pip joystick python3-pygame mplayer


import pygame
import time
from signal import signal, SIGINT
from sys import exit
import socket
import sys
import os

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class TextPrint(object):
    """
    This is a simple class that will help us print to the screen
    It has nothing to do with the joysticks, just outputting the
    information.
    """

    def __init__(self):
        """ Constructor """
        self.reset()
        self.x_pos = 10
        self.y_pos = 10
        self.font = pygame.font.Font(None, 30)

    def print(self, my_screen, text_string):
        """ Draw text onto the screen. """
        text_bitmap = self.font.render(text_string, True, WHITE)
        my_screen.blit(text_bitmap, [self.x_pos, self.y_pos])

    def reset(self):
        """ Reset text to the top of the screen. """
        self.x_pos = 10
        self.y_pos = 10
        self.line_height = 50
        self.tab_width = 250

    def indent(self):
        self.x_pos += self.tab_width

    def unindent(self):
        self.x_pos -= self.tab_width

    def newline(self):
        self.y_pos += self.line_height
        self.x_pos = 10


def computeMotorSpeeds(x, y):

    # allow for a little slop on the stick around zero
    deadZoneSize = .05

    # used to compute what the motors on the robot should do from stick inputs
    x_centered = False
    y_centered = False
    rightMotor = 0
    leftMotor = 0

    # minimum throttle response, prevents motor stall
    minThrottle = .3

    x_centered = False
    if (x < (0.0 + deadZoneSize)):
        if (x > (0.0 - deadZoneSize)):
            x_centered = True

    y_centered = False
    if (y < (0.0 + deadZoneSize)):
        if (y > (0.0 - deadZoneSize)):
            y_centered = True

    # stick centered, full stop
    if (y_centered == True and x_centered == True):
        # print("Stopped")
        leftMotor = 0.0
        rightMotor = 0.0

    # rotate in place by turning motors in different directions at same speed
    if (y_centered == True and x_centered == False):
        if (x < 0.0):
            speed = -1 * x * (1.0 - minThrottle) + minThrottle
            leftMotor = speed * 100.00 * -1.0
            rightMotor = speed * 100.00

        if (x > 0.0):
            speed = x * (1.0 - minThrottle) + minThrottle
            leftMotor = speed * 100.00
            rightMotor = speed * 100.00 * -1.0

        #print("Motor speeds: " + str(leftMotor) + "," + str(rightMotor))

    # straight forward or reverse
    if (y_centered == False and x_centered == True):

        if (y < 0.0):
            speed = -1 * y * (1.0 - minThrottle) + minThrottle

        if (y > 0.0):
            speed = y * (1.0 - minThrottle) + minThrottle
            speed = speed * -1

        leftMotor = speed * 100.00
        rightMotor = speed * 100.00
        #print("Motor speeds: " + str(leftMotor) + "," + str(rightMotor))

    # we have a mix of forward motion and lateral motion
    # start with forward motion but subtract off a fraction of the inside motor's speed based on stick deflection
    # this makes the tracks turn at different speeds and the robot will turn slowly as it moves forward

    if (y_centered == False and x_centered == False):
        rotateInPlace = False

        if (y < 0.0):
            speed = -1 * y * (1.0 - minThrottle) + minThrottle

        if (y > 0.0):
            speed = y * (1.0 - minThrottle) + minThrottle
            speed = speed * -1

        leftMotor = speed * 100.00
        rightMotor = speed * 100.00

        # subtract off some speed from the inside track to induce a turn
        # handle left (negative) this works for right
        if (x < 0.0):
            leftMotor = leftMotor + (leftMotor * x)

        if (x > 0.0):
            rightMotor = rightMotor - (rightMotor * x)

        #print("Motor speeds: " + str(leftMotor) + "," + str(rightMotor))

    leftMotor = int(leftMotor)
    rightMotor = int(rightMotor)
    #print("Motor speeds: " + str(leftMotor) + "," + str(rightMotor))

    return leftMotor, rightMotor


# string to send to rover
commandString = ""

# Set the width and height of the screen [width,height]
window_width = 600
window_height = 100

screen_width = 1366
screen_height = 768

size = [window_width, window_height]

pos_x = screen_width / 2 - window_width / 2
pos_y = screen_height - window_height

os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (pos_x, pos_y)
#os.environ['SDL_VIDEO_CENTERED'] = '0'

pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Rover Status")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()

# Get ready to print
textPrint = TextPrint()

# sensor values
battVoltage = 0.0
signalStrength = ""
linkQuality = ""
getSensor = False
sensorInterval = 10
intervalCount = sensorInterval
recvString = ""

# initialize socket
size = 4096
recv = ""

# default port for socket
port = 6000
host_ip = "192.168.1.214"
#host_ip = "127.0.0.1"

##reconnect loop needs to start here
while not done:

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))

    # connecting to the server
    try:
        s.connect((host_ip, port))
        print("Connection successful.")
    except socket.error as err:
        print("Connection to server failed with error %s" % (err))

    count = 0


    # -------- Main Program Loop -----------
    while not done:

        # EVENT PROCESSING STEP
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Got command to quit.")
                done = True

        screen.fill(BLACK)
        textPrint.reset()

        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()

        #todo: warn on incorrect number of joysticks
        #textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))

        #we only use the first joystick
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        name = joystick.get_name()

        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        buttons = joystick.get_numbuttons()

        x = joystick.get_axis(2)
        y = joystick.get_axis(3)
        button = joystick.get_button(6)
        #print(button)


        #for reference if needed - loops through all buttons and displays status
        #for i in range(buttons):
            #button = joystick.get_button(i)
            #print("Button {:>2} value: {}".format(i, button))

        leftMotor, rightMotor = computeMotorSpeeds(x, y)

        if (intervalCount == sensorInterval):
            getSensor = True

        if (getSensor):
            commandString = "C:" + str(leftMotor) + \
                ":" + str(rightMotor) + ":" + "1:" + str(button) + ":E"
        else:
            commandString = "C:" + str(leftMotor) + \
                ":" + str(rightMotor) + ":" + "0:" + str(button) + ":E"

        #print(commandString)

        try:
            s.sendall(commandString.encode('utf-8'))
        except:
            print("Connection timed out.")
            break

        try:
            recv = s.recv(size)

        except:
            print("Connection timed out.")
            break

        recvString = recv.decode("utf-8")
        #print (recvString)

        if (getSensor):
            if (len(recvString.split(":")) > 2):
               battVoltage = float(recvString.split(":")[1])
               signalStrength = str(recvString.split(":")[2])
               linkQuality = str(recvString.split(":")[3])
               getSensor = False
               intervalCount = 0
            else:
               print("Error: we just got a line without sensor readings when one was requested.")


        textPrint.print(screen, "Batt Voltage (V): {}".format(battVoltage))
        textPrint.indent()
        textPrint.print(screen, "Signal Strength (db): {}".format(signalStrength))
        textPrint.newline()
        textPrint.print(screen, "Link Qual: {}".format(linkQuality))

        buttons = joystick.get_numbuttons()

        # update screen
        pygame.display.flip()

        # Limit to 60 frames per second
        clock.tick(60)
        intervalCount = intervalCount + 1

    #reconnect loop ends here
    if (done == False):
        print("Disconnected from rover, attempting reconnect...")


# Close the window and quit.
s.close()
pygame.quit()
