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

# low priority:
    # ToDo: add progress bar
    # toDo: add pause behaviour


# layout and methods
class GriddedScreen(Widget):
    # using this variable so I don't have to modify it everywhere, hopefully it doesn't just become a pointer :P
    initialClockCounter = 480
    breaktime = 1800 #~30 min
    clockCounter = initialClockCounter
    statsString = ''
    # app state started/ended
    is_idle = True
    is_fileCreated = False

    # output file path
    outFileFolder = 'C:\\temp\\slapace'
    outFileName = '_slapace'
    outFileExt = '.csv'
    targetFile = ''

    # cases FTRd so far, average case FTR time, avalable time in this session
    ftrdCounter = 0
    bankedUpTime = 0
    totalTimeSpentOnFtr = 0
    averageFTRtime = 0
    
    # convert timer counter to human readable string
    def time2string(self, *args):
        
        time2disp = int(args[0])
        str2return = ''
        if time2disp < 0: # add negative sign
            str2return += '-'
        time2disp = abs(time2disp)
        if len(args):
            return str2return + f"{time2disp // 60:>02}:{time2disp % 60:>02}"
        else:
            return '00:00'
        
        

    # scheduled countdown every sec while the app is active
    def countDown(self, *args):
        self.clockCounter -= 1
        self.ids.timeText.text = self.time2string(self.clockCounter)

    def refreshCountDown(self, *args):
        self.clockCounter = self.initialClockCounter
        self.ids.timeText.text = self.time2string(self.clockCounter)


    def updateStatsText(self, str2write, clearOutput = False, *args):
        if clearOutput:
            self.statsString = ''
        self.statsString += str2write
        # update element
        self.ids.statsText.text = self.statsString


    def dumpData(self, targetFile, str2write, *args):
        # folder path is checked on start
        #check if file can be opened
        try:
            f = open(targetFile, "a")
        except IOError as ioe:
            self.updateStatsText(f"There was an error opening {targetFile}, {ioe}\n")
            return False
        # open the file and appent the data
        else:
            with open(targetFile, "a") as f:
                f.write(str2write)
                if not self.is_fileCreated:
                    self.is_fileCreated = True
                return True


    # when start is performed
    def startPace(self, *args):
        # schedule clock event
        Clock.schedule_interval(self.countDown, 1)
        # change button text
        self.ids.startEndButton.text = 'END'
        self.ids.ftrButton.text = "FTR"

        # update stats text
        self.updateStatsText('Press FTR to record your intervals for this session\n\n', clearOutput=True)


        # check if folder path exists
        if not os.path.exists(self.outFileFolder):
            try:
                os.makedirs(self.outFileFolder)
                self.updateStatsText(f"Path didn't exist, created {self.outFileFolder}\n")
            except OSError as ose:
                self.updateStatsText(f"There was an error creating {self.outFileFolder}, {ose}\n")
        else:
            self.updateStatsText(f"Path exists, writing to {self.outFileFolder}\n")
        
        # change program state to active!
        self.is_idle = False


    # when ftr button is pressed
    def FTRnow(self, *args):
        """
        The convenient behaviour:
        - require case
        - can SLA without being in active state -> record time as 00:00

        """
        #change the countdown timer colour for fun :P
        self.ids.timeText.color = [random.randint(0,255), random.randint(0,255), random.randint(0,255), 1]

        # commented this out because want to be able to FTR without being in active state to be able to keep track of 
        # tickets that got SLAd by me overall
        # # if idle = do nothing 
        # if self.is_idle:
        #     return
        
        # get the case num, require it
        caseNum = ''
        try:
            caseNum = f"{(int(self.ids.optionalCaseNum.text)):>08}"
            self.ids.optionalCaseNum.text = '########'
        except ValueError:
            caseNum = '0'
        # if failed to collect a valid number, just return
        if caseNum == '0':
            return
        
        # stats shouldn't increase in idle state
        if not self.is_idle:
            # increase ftrdCounter
            self.ftrdCounter += 1
            # addup total time spent
            self.bankedUpTime += self.clockCounter
            self.totalTimeSpentOnFtr += self.initialClockCounter - self.clockCounter
            # get average time took
            self.averageFTRtime = self.totalTimeSpentOnFtr/self.ftrdCounter
            # update middle stats in the APP
            self.ids.middleStatsText.text = f'Set Pace: {self.time2string(self.initialClockCounter)}  |  Average Pace: {self.time2string(int(self.averageFTRtime))}  |  Banked Time: {self.time2string(self.bankedUpTime)}'


        # get time it took, should not be negative because clockCounter should always be < initialClockCounter
        timeTook = self.time2string(self.initialClockCounter - self.clockCounter)
        
        # get the time stamp
        timeNow = datetime.datetime.now()

        # write time to app
        self.updateStatsText(f"{timeNow.strftime('%H:%M:%S')} >> {timeTook}")
        
        # refresh timer last
        self.refreshCountDown()
        
        # string for csv format dump
        str2write = f"{timeNow.strftime('%Y %b %d %H:%M:%S')}, {timeTook}, {caseNum}\n"

        # dump the data
        # get target file name
        targetFile = os.path.join(self.outFileFolder, timeNow.strftime("%Y%b%d")+ self.outFileName + self.outFileExt)
        self.targetFile = targetFile

        if self.dumpData(targetFile,str2write):
            self.updateStatsText(f" >> {caseNum} >> written to {os.path.split(targetFile)[1]}\n")
   
        if self.totalTimeSpentOnFtr > self.breaktime: #pomodoro
            self.updateStatsText(f"FTRd for {self.time2string(self.totalTimeSpentOnFtr)}. Consider stretching or taking a break.\n")

    # when the END button is clicked
    def endPace(self, *args):
        # unschedule clock
        Clock.unschedule(self.countDown)
        
        # no FTR, refresh timer
        self.refreshCountDown()
        # 'disable' FTR button
        self.ids.ftrButton.text = "FTR idle"

        # write end string
        self.updateStatsText('\nThis session:' + f'\nFTRd: {self.ftrdCounter}\nAverage Pace: {self.time2string(int(self.averageFTRtime))}\nBanked Time: {self.time2string(self.bankedUpTime)}\n')

        

        # change button text
        self.ids.startEndButton.text = 'START'

        # output FTRd today
        if self.is_fileCreated:
            with open(self.targetFile, "r") as f:
                numFtrd = 0
                for _ in f.readlines():
                    numFtrd +=1
                self.updateStatsText(f'FTRd today: {numFtrd}\n')
        # new stuff
        self.updateStatsText('\nPress START to begin pace with 10 min intervals\n')        
            

        # change program state to idle
        self.is_idle = True
        # refresh other stats
        self.ftrdCounter = 0
        self.bankedUpTime = 0
        self.totalTimeSpentOnFtr = 0
        self.averageFTRtime = 0
        
    # this method is triggered by startEndButton, so one button can call 2 methods depending on program state
    def startEndPace(self, *args):
        
        if self.is_idle:
            self.startPace()
        else:
            self.endPace()
    
    def changeInitClock(self, *args):
        if self.is_idle:
            # round to nearest 10 sec
            self.initialClockCounter = (int(self.ids.slidr.value)//10) *10
            self.refreshCountDown()
            self.ids.middleStatsText.text = f'Set Pace: {self.time2string(self.initialClockCounter)}  |  Average Pace: {self.time2string(int(self.averageFTRtime))}  |  Banked Time: {self.time2string(self.bankedUpTime)}'


    

# main app entry and run
class countDownTracker(App):
    
    # clockCounter = 600

    def build(self):
        self.title = 'SLA Pacemaker'
        return GriddedScreen()
    
if __name__ == '__main__':
    countDownTracker().run()
