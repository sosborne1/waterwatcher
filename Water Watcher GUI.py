#!/usr/bin/python3

from tkinter import  *
import tkinter as tk
import tkinter.font as tkFont
from tkinter import simpledialog 
import datetime
from report_gen_method import report_generator

import os         # used to create folders
from pathlib import Path    #used to ignore warning of duplicate folders

import pathlib     # used for creating multiple directories


class App(tk.Frame):    #container

    def location(self):
        dialog_frame = tk.Frame(self)
        dialog_frame.pack(padx=0, pady=0, anchor="center")
        self.curr_location.set("Location: N/A")
        tk.Label(dialog_frame, textvariable=self.curr_location).pack()

    def changeButton(self):
        button_frame = tk.Frame(self)
        button_frame.pack(padx=0, pady=(0), anchor="center")
        tk.Button(button_frame, text='Change Location', command=self.click_Change).pack()

    def click_Change(self):
        print("Changing location...")
        new_location = tk.simpledialog.askstring("Address", "Enter Address")
        self.curr_location.set("Location: " + new_location)

    def nextReport(self):
        myFont = tkFont.Font(size = 14, weight = 'bold')
        dialog_frame = tk.Frame(self)
        dialog_frame.pack(padx=0, pady=(0), anchor="center")
        self.nextReportLabel = tk.Label(dialog_frame, font = myFont)
        self.nextReportLabel.pack()

    def getReportTime(self):
        now = datetime.datetime.now() 
        next_report_time = now + datetime.timedelta(minutes = (self.time_between_tests / 60000))
        report_date = "Next Report at: " + next_report_time.strftime("%c")
        self.nextReportLabel.configure(text = report_date)

    def recentReadings(self):
        myFont = tkFont.Font(size = 14, weight = 'bold')       
        dialog_frame = tk.Frame(self)
        dialog_frame.pack(padx=0, pady=5, anchor="center")
        tk.Label(dialog_frame, font = myFont, text="Most Recent Readings: ").pack(side="left")
    
    def testButtons(self):
        button_frame = tk.Frame(self)
        button_frame.pack(padx=0, pady=0, anchor='center')
        tk.Button(button_frame, text='Test Now', command=self.click_TestNow).pack(side="left")
        self.repeatButton = tk.Button(button_frame, text='Start Repeated Test', command=self.click_RepeatTest)
        self.repeatButton.pack(side="left")

    def click_TestNow(self):
        print("Testing...")
        self.startTest()

    def repeatTestButton(self):
        button_frame = tk.Frame(self)
        button_frame.pack(padx=0, pady=0, anchor='center')
        self.repeatButton = tk.Button(button_frame, text='Start Repeated Test', command=self.click_RepeatTest)

    def click_RepeatTest(self):
        print("The results are... ")
        self.time_between_tests = simpledialog.askfloat("Input", "Enter what time (in minutes) you want between reports:", 
                                                        minvalue=0.0) * 60000
        repeat = True
        self.startTest()
        self.getReportTime()
        self.after_id = root.after(int(self.time_between_tests), self.startTest, repeat)
        self.repeatButton.configure(text = "Stop Repeat Testing", command=self.cancel)

    def cancel(self):
        root.after_cancel(self.after_id)
        self.repeatButton.configure(text = "Start Repeated Test", command=self.click_RepeatTest)
        self.nextReportLabel.configure(text = "")

    def startTest(self, repeat=False):
        new_orp_num, new_ph_num, orp_sensor_okay, ph_sensor_okay = report_generator(address=self.curr_location.get())

        if((self.orp_num is not None) and orp_sensor_okay):
            orp_change = ((new_orp_num - self.orp_num) / self.orp_num) * 100
        else:
            orp_change = 0
        if((self.ph_num is not None) and ph_sensor_okay):
            ph_change = ((new_ph_num - self.ph_num) / self.ph_num) * 100
        else:
            ph_change = 0

        self.orp_num = new_orp_num
        self.ph_num = new_ph_num

        if(orp_sensor_okay):
            self.curr_orp_string.set("ORP: " + str(self.orp_num) + "\n (" + "{:.2f}".format(orp_change) + "% change)")
            if(self.orp_num >= 600 and self.orp_num <= 900):
                self.ORPflag_string.set("")
            else:
                self.ORPflag_string.set("**OUTSIDE ORP TOLERANCE**")
        else:
            self.curr_orp_string.set("ORP SENSOR DISCONNECTED")
        if(ph_sensor_okay):
            self.curr_ph_string.set("pH: " + str(self.ph_num) + "\n (" + "{:.2f}".format(ph_change) + "% change)")
            if (self.ph_num >= 7.0 and self.ph_num <= 8.0):
                self.pHflag_string.set("")
            else:
                self.pHflag_string.set("**OUTSIDE PH TOLERANCE**")
        else:
            self.curr_ph_string.set("PH SENSOR DISCONNECTED")

        if repeat:
            self.getReportTime()
            self.after_id = root.after(int(self.time_between_tests), self.startTest, repeat)

    def viewResultsButton(self):
        button_frame = tk.Frame(self)
        button_frame.pack(padx=0, pady=10, anchor='center')
        tk.Button(button_frame, text='View Results', command=self.click_ViewResults).pack()

    def click_ViewResults(self):
        print("The results are... ")
        time_path = "Reports"
        #creates folders and checks for duplicates
        p = pathlib.Path(time_path)
        p.mkdir(parents=True, exist_ok=True)
        
        os.system("pcmanfm \"%s\"" % time_path)

    def pHxORP(self):
        myFont = tkFont.Font(size = 14, weight = 'bold')
        dialog_frame = tk.Frame(self)
        dialog_frame.pack(padx=0, pady=(10), anchor="center")
        #pH
        self.curr_ph_string.set("Start test to get\n pH reading")
        tk.Label(dialog_frame, font = myFont, textvariable=self.curr_ph_string).pack(side="left")
        #spacing inbetween
        tk.Label(dialog_frame, text="\t\t").pack(side='left')
        #ORP
        self.curr_orp_string.set("Start test to get\n ORP reading")
        tk.Label(dialog_frame, font = myFont, textvariable=self.curr_orp_string).pack(side="right")

    def flag(self):
        myFont = tkFont.Font(size = 14, weight = 'bold')
        dialog_frame = tk.Frame(self)
        dialog_frame.pack(padx=0, pady=(0), anchor="center")
        #pH
        self.pHflag_string.set("")
        tk.Label(dialog_frame, font = myFont, bg = "red", textvariable=self.pHflag_string).pack(side="left")
        self.ORPflag_string.set("")
        tk.Label(dialog_frame, font = myFont, bg = "red", textvariable=self.ORPflag_string).pack(side="right")

    def tolerances(self):
        dialog_frame = tk.Frame(self)
        dialog_frame.pack(padx=25, pady=(10,0), anchor="center")
        tk.Label(dialog_frame, text="(pH Tolerance Range: 7.0 - 8.0)").pack()
        tk.Label(dialog_frame, text="(OPR Tolerance Range: 600 - 900 mV)").pack()


    #display
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.pack()

        #makes widget screen fit to window
        self.pack(fill=BOTH, expand=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #hides menu bar
        self.master.config(menu= tk.Menu(self.master))

        self.curr_location = StringVar()
        self.time_between_tests = DoubleVar()
        self.curr_orp_string = StringVar()
        self.curr_ph_string = StringVar()
        self.orp_num = None
        self.ph_num = None
        self.pHflag_string = StringVar()
        self.ORPflag_string = StringVar()


        self.after_id = None
        self.repeatButton = None
        self.nextButton = None
        self.time_between_tests = None
        
        #prints
        self.changeButton()
        self.location()
        self.nextReport()
        self.testButtons()
        self.recentReadings()
        self.pHxORP()
        self.viewResultsButton()
        self.flag()
        self.tolerances()

#window settings
root = tk.Tk()    #creates window
root.tk_setPalette(background= '#187bcd')   #sets background color
root.title("The Water Watcher")     #name of the window
root.geometry('800x480')    #size of window
root.attributes('-fullscreen', True)

app = App(master = root)
app.mainloop()

#brings windows to the front of the screen (Mac only)
['/usr/bin/osascript', '-e', 'tell app "Finder" to set frontmost of process "Python" to true']