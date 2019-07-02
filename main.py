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
import os


# layout and methods
class GriddedScreen(Widget):
    # using this variable so I don't have to modify it everywhere, hopefully it doesn't just become a pointer :P
    initialClockCounter = 600
    clockCounter = initialClockCounter
    statsString = ''
    # app state started/ended
    is_idle = True

    # output file path
    outFileFolder = 'C:\\temp\\slapace'
    outFileName = '_slapace'
    outFileExt = '.csv'

    # cases FTRd so far, average case FTR time, avalable time in this session
    
    
    # convert timer counter to human readable string
    def time2string(self, *args):
        if len(args):
            return f"{args[0] // 60:>02}:{args[0] % 60:>02}"
        return f"{self.clockCounter // 60:>02}:{self.clockCounter % 60:>02}"

    # scheduled countdown every sec while the app is active
    def countDown(self, *args):
        self.clockCounter -= 1
        self.ids.timeText.text = self.time2string()

    def refreshCountDown(self, *args):
        self.clockCounter = self.initialClockCounter
        self.ids.timeText.text = self.time2string()

    # when start is performed
    def startPace(self, *args):
        # schedule clock event
        Clock.schedule_interval(self.countDown, 1)
        # change button text
        self.ids.startEndButton.text = 'END'
        self.ids.ftrButton.text = "FTR"
        # change stats text
        self.statsString = 'Press FTR to record your intervals for this session\n'
        self.ids.statsText.text = self.statsString

    # when ftr button is pressed
    def FTRnow(self, *args):
        # if idle = do nothing
        if self.is_idle:
            return


        # get time it took
        timeTook = self.time2string(self.initialClockCounter - self.clockCounter)
        
        # get the time stamp
        timeNow = datetime.datetime.now()
        
        # get the case num
        caseNum = ''
        try:
            caseNum = f"{(int(self.ids.optionalCaseNum.text)):>08}"
            self.ids.optionalCaseNum.text = '########'
        except ValueError:
            caseNum = '00000000'

        str2write = f"{timeNow.strftime('%Y %b %d %H %M %S')}, {timeTook}, {caseNum}\n"


        #write time to app
        self.statsString += f"{timeTook}"
        self.ids.statsText.text = self.statsString
        
        # refresh timer last
        self.refreshCountDown()

        # dump the data
        # get target file name
        targetFile = os.path.join(self.outFileFolder, timeNow.strftime("%Y%b%d")+ self.outFileName + self.outFileExt)
        # check if folder path exists
        if not os.path.exists(self.outFileFolder):
            try:
                os.makedirs(self.outFileFolder)
            except OSError as ose:
                self.statsString += f"There was an error creating {self.outFileFolder}, {ose}\n"
                self.ids.statsText.text = self.statsString
        else:
            self.statsString += f"Path exists, writing to {self.outFileFolder}\n"
            self.ids.statsText.text = self.statsString
        
        #check if file can be opened
        try:
            f = open(targetFile, "a")
        except IOError as ioe:
            self.statsString += f"There was an error opening {targetFile}, {ioe}\n"
            self.ids.statsText.text = self.statsString
        # open the file and appent the data
        else:
            with open(targetFile, "a") as f:
                f.write(str2write)
                self.statsString += f" >> written to {os.path.split(targetFile)[1]}\n"
                self.ids.statsText.text = self.statsString


    # when the END button is clicked
    def endPace(self, *args):
        # unschedule clock
        Clock.unschedule(self.countDown)
        
        # no FTR, refresh clock
        self.ids.ftrButton.text = "###"
        self.refreshCountDown()

        # clear the string
        self.statsString += 'Press START to begin pace with 10 min intervals\n'
        self.ids.statsText.text = self.statsString

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
