import os
from time import sleep
from win10toast import ToastNotifier
import socket
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from threading import Thread
import subprocess
from PIL import ImageGrab

stop_countdown = False

def start_threading(): #start the main thread
    start_thread = Thread(target=main_countdown)
    start_thread.start()

def time_converter(hours, minutes, seconds): #converts hours and minutes to seconds and sums the total
    total = 0
    total += seconds + minutes*60 + hours*3600
    return total

def time_estimation(hours, minutes, seconds):  #estimates how much time there is until the shutdown
    current_hours, current_minutes, current_seconds = str(datetime.now()).split(" ")[1].split(".")[0].split(":") #getting the current time
    estimated_seconds = int(current_seconds) + seconds #estimated seconds
    estimated_minutes = int(current_minutes) + minutes #estimated minutes
    estimated_hours = int(current_hours) + hours #estimated hours
    if current_hours == '12' and hours == 12 and estimated_minutes > 50 and estimated_seconds > 50:
        estimated_hours -= 1
    # making it accurate
    if estimated_seconds >= 60:
        estimated_seconds -= 60
        estimated_minutes += 1
    if estimated_minutes >= 60:
        estimated_minutes -= 60
        estimated_hours += 1
    if estimated_hours >= 24:
        estimated_hours -= 24
    print([estimated_hours, estimated_minutes, estimated_seconds])

    # making it look a bit nicer
    if estimated_seconds < 10:
        estimated_seconds = f"0{estimated_seconds}"
    if estimated_minutes < 10:
        estimated_minutes = f"0{estimated_minutes}"
    if estimated_hours < 10:
        estimated_hours = f"0{estimated_hours}"

    # returning string with proper time format
    return f"{estimated_hours}:{estimated_minutes}:{estimated_seconds}"

def countdown(time): #the actual countdown until the shut down
    global stop_countdown
    for i in range(0, time): #this is indeede a for loop
        if i+1 == time:
            shut_down()  # after the loop is over the shut down function gets called
        if stop_countdown:
            stop_countdown = False
            start_button.config(bg="RED", state=NORMAL)
            current_time.config(text="")
            estimated_time.config(text="")
            break
        time_current = str(datetime.now()).split(" ")[1].split(".")[0] #getting the current time
        current_time.config(text= f"current time: {time_current} ({i+1} out of {str(time)} seconds elapsed)")
        if i % 2 == 0:
            print(f"current {time_current} ----------------------------- {i+1} seconds elapsed")
        else:
            print(f"current {time_current} ---------------------------------------------- {i+1} seconds elapsed")
        current_time.update()
        sleep(1) #one second passes

def specified_countdown(hours, minutes, seconds):
    global stop_countdown
    i = 1
    while True:
        if stop_countdown:
            stop_countdown = False
            start_button.config(bg="RED", state=NORMAL)
            current_time.config(text="")
            estimated_time.config(text="")
            break
        current_time_string = str(datetime.now()).split(" ")[1].split(".")[0]
        if f"{hours}:{minutes}:{seconds}" == current_time_string or f"{hours}:{minutes}:{str(int(seconds)+1)}" == current_time_string:
            shut_down()
            break
        current_time.config(text=f"current time: {current_time_string} ({i} seconds elapsed)")
        if i % 2 == 0:
            print(f"current {current_time_string} ----------------------------- {i} seconds elapsed")
        else:
            print(f"current {current_time_string} ---------------------------------------------- {i} seconds elapsed")
        current_time.update()
        i+=1
        sleep(1) #one second  passes

def make_screenshot():
    current_time_list = "-".join(str(datetime.now()).split(".")[0].split(":")).split(" ")
    current_time = current_time_list[1] + "-" + current_time_list[0]
    screenshot = ImageGrab.grab(all_screens=True)
    screenshot.save(f"{os.getcwd()}\\Restart Screenshots\\{current_time}.png")
    print(f"Screenshot saved as {current_time}.png")
    sleep(1)

def shut_down():
    kill_chrome = chrome_clicked.get() #checking if chrome should be killed
    ss = ss_clicked.get()
    if ss == "yes":
        print("Making screenshot.")
        if "Restart Screenshots" not in os.listdir():
            os.mkdir("Restart Screenshots")
        make_screenshot()


    if kill_chrome == "yes":
        print("killing chrome")
        os.system("taskkill /im chrome.exe /f")
    kill_apps = apps_clicked.get()
    if kill_apps == "yes": #checking if more apps should be killed
        apps_to_be_killed = apps.get()
        if apps_to_be_killed == "":
            ...
        else:
            app_list = apps_to_be_killed.split(", ")
            for app in app_list:
                print(f"killing {app}")
                os.system(f"taskkill /im {app} /f")
                print(f"{app} killed successfully")
    print("Restarting...")
    os.system("shutdown /r /t 0") #restarting
    print("Restarted.")



def hours_calculation(hours, minutes): #hour calculator. Kinda annoying to deal with tbh. This kinda works but has some interesting bugs that I am too lazy to actually fix
    all_hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    current_hours, current_minutes, current_seconds = str(datetime.now()).split(" ")[1].split(".")[0].split(":")
    current_hours, current_minutes = int(current_hours), int(current_minutes)

    current_hour_idx = all_hours.index(current_hours) #getting the index of the current hour
    counter = -1 #counter technically starts from 0
    for i in all_hours[current_hour_idx::]:
        counter += 1
        if all_hours[i] == current_hours and current_minutes > minutes:
            continue
        if i == hours:
            return counter
        if i == 23:
            for a in all_hours[:current_hour_idx+1]:
                counter += 1
                if a == hours:
                    return counter
    return 0

def main_countdown(): #well I guess main_function would be a better name for it.
    start_button.config(bg="GREEN", state=DISABLED)
    count_hours, count_minutes, count_seconds = hours_clicked.get(), minutes_clicked.get(), seconds_clicked.get() #getting the countdown time
    time = 0 #declaring the time variable
    if count_hours == "0" and count_minutes == "0" and count_seconds == "0": #if the user didn't touch these then they probably touched the specified time.
        specified_hours, specified_minutes, specified_seconds = specified_hours_clicked.get(), specified_minutes_clicked.get(), specified_seconds_clicked.get() #gettig specified time
        estimated_hours = specified_hours
        estimated_minutes = specified_minutes
        estimated_seconds = specified_seconds
        if int(specified_hours) < 10:
            estimated_hours = f"0{specified_hours}"
        if int(specified_minutes) < 10:
            estimated_minutes = f"0{specified_minutes}"
        if int(specified_seconds) < 10:
            estimated_seconds = f"0{specified_seconds}"
        est_time = f"{estimated_hours}:{estimated_minutes}:{estimated_seconds}"
        estimated_time.config(text=f"estimated time: {est_time}")

        # getting and displaying the apps that should be killed
        kill_apps = apps_clicked.get()
        if kill_apps == "yes":
            apps_to_be_killed = apps.get()
            if apps_to_be_killed == "":
                ...
            else:
                app_list = apps_to_be_killed.split(", ")
                all_apps = '\n'.join(app_list)
                shut_downable_apps.config(text=f"{all_apps}")

        specified_countdown(estimated_hours, estimated_minutes, estimated_seconds)

        # hour_difference = hours_calculation(int(specified_hours), int(specified_minutes))
        # current_hours, current_minutes, current_seconds = str(datetime.now()).split(" ")[1].split(".")[0].split(":")
        # if int(specified_seconds) < int(current_seconds): #seconds
        #     seconds_difference = 60 - int(current_seconds)
        # else:
        #     seconds_difference = abs(int(specified_seconds) - int(current_seconds))
        # if int(specified_minutes) < int(current_minutes): #minutes
        #     minutes_difference = 60 - int(current_minutes)
        # else:
        #     minutes_difference = abs(int(specified_minutes)-int(current_minutes))
        # if int(specified_minutes) < int(current_minutes) and int(specified_hours) == int(current_hours): #TODO - fix this line.
        #     print(hour_difference)
        #     hour_difference -= 1
        # if not hour_difference == 0:
        #     hour_difference -= 1
        # print([hour_difference, minutes_difference, seconds_difference])
        # time = time_converter(int(hour_difference), int(minutes_difference), int(seconds_difference))
        # est_time = time_estimation(int(hour_difference), int(minutes_difference), int(seconds_difference))
        # estimated_time.config(text=f"estimated time: {est_time}")


    elif int(count_hours) > 0 or int(count_minutes) > 0 or int(count_seconds) > 0: #if the user did touch them then countdown it is
        time = time_converter(int(count_hours), int(count_minutes), int(count_seconds))
        est_time = time_estimation(int(count_hours), int(count_minutes), int(count_seconds))
        estimated_time.config(text=f"estimated time: {est_time}")

        #getting and displaying the apps that should be killed
        kill_apps = apps_clicked.get()
        if kill_apps == "yes":
            apps_to_be_killed = apps.get()
            if apps_to_be_killed == "":
                ...
            else:
                app_list = apps_to_be_killed.split(", ")
                all_apps = '\n'.join(app_list)
                shut_downable_apps.config(text=f"{all_apps}")

        countdown(time) #starting the countdown

def stop_countdown():
    global stop_countdown
    stop_countdown = True


root = Tk() #creating tkinter object
root.frame() #creating the frame so it could be fullscreened
root.geometry('1150x450')#decided this is an optimal resolution
root.config(bg='#0F0F0F') #setting the background color to the youtube dark mode one
root.title("PC automatic restart by jtw") #window title
root.config(bg="#0f0f0f")
Label(root, text="PC automatic restart",bg='#0F0F0F',fg='#fafafa' , font='italic 15 bold').pack(pady=10) #first title label



Label(root, text="Specific time", bg='#0F0F0F',fg='#fafafa' , font='italic 11 bold').place(x=100, y=170)
specified_hours_options = [str(i) for i in range(24)]
specified_hours_clicked = StringVar()
specified_hours_clicked.set("0")
specified_hours_drop = OptionMenu(root, specified_hours_clicked, *specified_hours_options)
specified_hours_drop.config(bg="#0f0f0f", fg="#fafafa", font="italic 10 bold", highlightbackground="#0f0f0f", highlightcolor="#0f0f0f")
specified_hours_drop.pack(side=LEFT, fill=BOTH, expand=True)
specified_hours_drop.place(x=75, y=190)


specified_minutes_options = [str(i) for i in range(60) if i%5 == 0] #all 60 minutes in an hour is far too much and makes the menu too long
specified_minutes_clicked = StringVar()
specified_minutes_clicked.set("0")
specified_minutes_drop = OptionMenu(root, specified_minutes_clicked, *specified_minutes_options)
specified_minutes_drop.config(bg="#0f0f0f", fg="#fafafa", font="italic 10 bold", highlightbackground="#0f0f0f", highlightcolor="#0f0f0f")
specified_minutes_drop.place(x=130, y=190)

specified_seconds_options = [str(i) for i in range(60) if i%5 == 0]
specified_seconds_clicked = StringVar()
specified_seconds_clicked.set("0")
specified_seconds_drop = OptionMenu(root, specified_seconds_clicked, *specified_seconds_options)
specified_seconds_drop.config(bg="#0f0f0f", fg="#fafafa", font="italic 10 bold", highlightbackground="#0f0f0f", highlightcolor="#0f0f0f")
specified_seconds_drop.place(x=185, y=190)



Label(root, text="Countdown", bg='#0F0F0F',fg='#fafafa' , font='italic 11 bold').place(x=100, y=70)
hours_options = [str(i) for i in range(24)]
hours_clicked = StringVar()
hours_clicked.set("0")
hours_drop = OptionMenu(root, hours_clicked, *hours_options)
hours_drop.config(bg="#0f0f0f", fg="#fafafa", font="italic 10 bold", highlightbackground="#0f0f0f", highlightcolor="#0f0f0f")
hours_drop.place(x=75, y=90)


minutes_options = [str(i) for i in range(60) if i%5 == 0]
minutes_clicked = StringVar()
minutes_clicked.set("0")
minutes_drop = OptionMenu(root, minutes_clicked, *minutes_options)
minutes_drop.config(bg="#0f0f0f", fg="#fafafa", font="italic 10 bold", highlightbackground="#0f0f0f", highlightcolor="#0f0f0f")
minutes_drop.place(x=130, y=90)

seconds_options = [str(i) for i in range(60) if i%5 == 0]
seconds_clicked = StringVar()
seconds_clicked.set("0")
seconds_drop = OptionMenu(root, seconds_clicked, *seconds_options)
seconds_drop.config(bg="#0f0f0f", fg="#fafafa", font="italic 10 bold", highlightbackground="#0f0f0f", highlightcolor="#0f0f0f")
seconds_drop.place(x=185, y=90)

# Main button
start_button = Button(root, text="Start", bg="RED", fg="#0f0f0f", font="italic 15 bold", highlightbackground="#0f0f0f", highlightcolor="#fafafa",width=7, wraplength=135 ,command=start_threading)
start_button.place(x=475, y=225)
stop_button = Button(root, text="Stop", bg="RED", fg="#0f0f0f", font="italic 15 bold", highlightbackground="#0f0f0f", highlightcolor="#fafafa", width=7, wraplength=135 ,command=stop_countdown)
stop_button.place(x=600, y=225)

estimated_time = Label(root, text="", bg="#0f0f0f", fg = "#fafafa", font="italic 10 bold")
estimated_time.place(x= 350, y=90)
current_time = Label(root, text="", bg="#0f0f0f", fg = "#fafafa", font="italic 10 bold")
current_time.place(x=350, y=110)


Label(root, text="Do you want to shut down chrome?",bg='#0F0F0F',fg='#fafafa' , font='italic 10 bold').place(x=750,y=75)
chrome_options = ["yes", "no"]
chrome_clicked = StringVar()
chrome_clicked.set("yes")
chrome_drop = OptionMenu(root, chrome_clicked, *chrome_options)
chrome_drop.config(bg="#0f0f0f", fg="#fafafa", font="italic 10 bold", highlightbackground="#0f0f0f", highlightcolor="#0f0f0f")
chrome_drop.place(x=990, y=72)

Label(root, text="Do you want to shut down other apps?",bg='#0F0F0F',fg='#fafafa' , font='italic 10 bold').place(x=750,y=175)
apps_options = ["yes", "no"]
apps_clicked = StringVar()
apps_clicked.set("no")
apps_drop = OptionMenu(root, apps_clicked, *apps_options)
apps_drop.config(bg="#0f0f0f", fg="#fafafa", font="italic 10 bold", highlightbackground="#0f0f0f", highlightcolor="#0f0f0f")
apps_drop.place(x=1000, y=172)
apps = Entry(root, width=60)
apps.place(x=750, y = 210)
shut_downable_apps = Label(root, text="",bg='#0F0F0F',fg='#fafafa' , font='italic 10 bold')
shut_downable_apps.place(x=750,y=230)

Label(root, text="Do you want to make a screenshot of the last state \nthe screens were in before the restart?",bg='#0F0F0F',fg='#fafafa' , font='italic 10 bold').place(x=75,y=250)
ss_options = ["yes", "no"]
ss_clicked = StringVar()
ss_clicked.set("yes")
ss_drop = OptionMenu(root, ss_clicked, *ss_options)
ss_drop.config(bg="#0f0f0f", fg="#fafafa", font="italic 10 bold", highlightbackground="#0f0f0f", highlightcolor="#0f0f0f")
ss_drop.place(x=205, y=285)

Button(root, text = "QUIT", font="italic 14 bold", width=8, height=1, bg='RED', fg='#fafafa', command=root.destroy).place(relx= .9, rely=.9, anchor=CENTER)
root.mainloop()
