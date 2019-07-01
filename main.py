import kivy
from kivy.app import App
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.label import Label
# from kivy.uix.textinput import TextInput
# from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock

import random
import datetime


# layout and methods
class GriddedScreen(Widget):
    # using this variable so I don't have to modify it everywhere, hopefully it doesn't just become a pointer :P
    initialClockCounter = 600
    clockCounter = initialClockCounter
    statsString = ''
    # app state started/ended
    is_idle = True

    # output file path
    outFile = ''
    
    # convert timer counter to human readable string
    def time2string(self, *args):
        if len(args):
            return f"{args[0] // 60:>02}:{args[0] % 60:>02}"
        return f"{self.clockCounter // 60:>02}:{self.clockCounter % 60:>02}"

    # scheduled countdown every sec while the app is active
    def countDown(self, *args):
        self.clockCounter -= 1
        self.ids.timeText.text = self.time2string()

    # when start is performed
    def startPace(self, *args):
        # schedule clock event
        Clock.schedule_interval(self.countDown, 1)
        # change button text
        self.ids.startEndButton.text = 'END'

        # change stats text
        self.statsString = 'Press FTRd to record your intervals for this session\n'
        self.ids.statsText.text = self.statsString

    # when ftr button is pressed
    def FTRnow(self, *args):
        
        # get time it took
        timeTook = self.initialClockCounter - self.clockCounter
        # get the time stamp
        timeNow = datetime.datetime.now()
        # get the case num
        caseNum = self.ids.optionalCaseNum.text

        # dump the data
        #   open the file for reading
        


        #write time
        self.statsString += f"{self.time2string(timeTook)}\n"
        self.ids.statsText.text = self.statsString
        

        # refresh timer last
        self.clockCounter = self.initialClockCounter
        self.ids.timeText.text = self.time2string()


    # when the END button is clicked
    def endPace(self, *args):
        # one last FTR, refreshes the clock too
        self.FTRnow()
        
        # clear the string
        self.statsString += 'Press START to begin pace with 10 min intervals\n'
        self.ids.statsText.text = self.statsString

        # unschedule clock
        Clock.unschedule(self.countDown)

        # change button text
        self.ids.startEndButton.text = 'START'
        
    # this method is triggered by startEndButton
    def startEndPace(self, *args):
        #change the countdown timer colour for fun :P
        self.ids.timeText.color = [random.randint(0,255), random.randint(0,255), random.randint(0,255), 1]

        if self.is_idle:
            self.is_idle = not self.is_idle
            self.startPace()
        else:
            self.is_idle = not self.is_idle
            self.endPace()

    

# main app entry and run
class countDownTracker(App):
    
    # clockCounter = 600

    def build(self):
        self.title = 'SLA Pacemaker'
        return GriddedScreen()
    
if __name__ == '__main__':
    countDownTracker().run()
