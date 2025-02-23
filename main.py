# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import os
import math
import sys
import time

os.environ["DISPLAY"] = ":0.0"

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
from dpeaDPi.DPiComputer import *
from dpeaDPi.DPiStepper import *

# ////////////////////////////////////////////////////////////////
# //                     HARDWARE SETUP                         //
# ////////////////////////////////////////////////////////////////
"""Stepper goes into MOTOR 0
   Limit Sensor for Stepper Motor goes into HOME 0
   Talon Motor Controller for Magnet goes into SERVO 1
   Talon Motor Controller for Air Piston goes into SERVO 0
   Tall Tower Limit Sensor goes in IN 2
   Short Tower Limit Sensor goes in IN 1
   """
dpiStepper = DPiStepper()
dpiStepper.setBoardNumber(0)
dpiComputer = DPiComputer()
dpiComputer.initialize()
# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP = False
UP = False
DOWN = True
ON = True
OFF = False
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

lowerTowerPosition = 60
upperTowerPosition = 76


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):

    def build(self):
        self.title = "Robotic Arm"
        return sm


Builder.load_file('main.kv')
Window.clearcolor = (.1, .1, .1, 1)  # (WHITE)

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

class MainScreen(Screen):
    armPosition = 0
    lastClick = time.time()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def debounce(self):
        processInput = False
        currentTime = time.time()
        if ((currentTime - self.lastClick) > DEBOUNCE):
            processInput = True
        self.lastClick = currentTime
        return processInput

    def toggleArm(self):
        print("Process arm movement here")
        armSpeed = 1500
        self.lowerArm()
        sleep(2)
        self.raiseArm()


    def lowerArm(self):
        servoNumber = 0
        dpiComputer.writeServo(servoNumber, 0)

    def raiseArm(self):
        servoNumber = 0
        dpiComputer.writeServo(servoNumber, 90)

    def toggleMagnet(self):
        if (self.ids.magnetControl.text == "Magnet off"):
            self.magnetOn()
        else:
            self.magnetOff()


    def magnetOn(self):
        servoNumber = 1
        dpiComputer.writeServo(servoNumber, 180)
        self.ids.magnetControl.text = "Magnet on"
        print("Magnet turned on")

    def magnetOff(self):
        servoNumber = 1
        dpiComputer.writeServo(servoNumber, 90)
        self.ids.magnetControl.text = "Magnet off"
        print("Magnet turned off")

    def auto(self):
        print("Running arm!!")
        dpiStepper.enableMotors(True)
        if(self.isBallOnTallTower() == 0):
            print("Ball on tall tower")
            self.ids.moveArm.value = 100
            dpiStepper.moveToAbsolutePositionInSteps(0, 0, True)
            self.lowerArm()
            sleep(1)
            self.magnetOn()
            sleep(1)
            self.raiseArm()
            sleep(1)
            self.ids.moveArm.value = 630
            dpiStepper.moveToAbsolutePositionInSteps(0, 530, True)
            self.lowerArm()
            sleep(1)
            self.magnetOff()
            sleep(1)
            self.raiseArm()
        elif(self.isBallOnShortTower() == 0):
            print("Ball on short tower")
            self.ids.moveArm.value = 630
            dpiStepper.moveToAbsolutePositionInSteps(0, 530, True)
            self.lowerArm()
            sleep(1)
            self.magnetOn()
            sleep(1)
            self.raiseArm()
            sleep(1)
            self.ids.moveArm.value = 100
            dpiStepper.moveToAbsolutePositionInSteps(0, 0, True)
            self.lowerArm()
            sleep(1)
            self.magnetOff()
            sleep(1)
            self.raiseArm()
        else:
            print("Ball not on a tower")


    def setArmPosition(self, position):
        print("Move arm here")
        pos = position
        dpiStepper.enableMotors(True)
        dpiStepper.setSpeedInStepsPerSecond(0, 500)
        dpiStepper.moveToAbsolutePositionInSteps(0, pos, True)

    def homeArm(self):
        dpiStepper.setCurrentPositionInSteps(0,0)

    def isBallOnTallTower(self):
        value = dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_2)
        if(value == 0):
            print("Ball is on tall tower")
        else:
            print("Ball is not on tall tower")
        return(value)


    def isBallOnShortTower(self):
        value = dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1)
        if (value == 0):
            print("Ball is on short tower")
        else:
            print("Ball is not on short tower")
        return (value)

    def initialize(self):
        print("Home arm and turn off magnet")

    def resetColors(self):
        self.ids.armControl.color = YELLOW
        self.ids.magnetControl.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////
if __name__ == "__main__":
    # Window.fullscreen = True
    # Window.maximize()
    MyApp().run()