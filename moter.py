from gpiozero import Motor
import time

motorR = Motor(forward=23, backward=22)
motorL = Motor(forward=24, backward=25)

def forward():
    motorR.forward(speed=0.7)
    motorL.forward(speed=0.7)
    time.sleep(1)
    stop()

def backward():
    motorR.backward(speed=0.7)
    motorL.backward(speed=0.7)
    time.sleep(1)
    stop()


def left():
    motorR.forward(speed=0.7)
    motorL.backward(speed=0.7)
    time.sleep(1)
    stop()


def right():
    motorR.backward(speed=0.7)
    motorL.forward(speed=0.7)
    time.sleep(1)
    stop()


def stop():
    motorR.stop()
    motorL.stop()

while True:
    command = input("Enter a command (1: forward, 2: backward, 3: left, 4: right, q: quit): ")

    if command == '1':
        forward()
    elif command == '2':
        backward()
    elif command == '3':
        left()
    elif command == '4':
        right()
    elif command.lower() == 'q':
        print("Exiting program...")
        stop()
    else:
        print("Invalid command! Please enter 1, 2, 3, 4, or q.")
