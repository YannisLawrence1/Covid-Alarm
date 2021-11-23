"""Creates a smart alarm system that can gather news, weather and covid-19 levels as well as
allowing for ALARMS to be created
This project required  PIP install uk-covid19 to gather information on Covid levels within the UK
The priority for ALARMS / NOTIFICATIONS is (1 most important, 3 least important):
    1. Daily refresh (next_day())
    2. ALARMS
    3. Notification refresh (gather_notifications())"""
from datetime import date, datetime
import sched
import time
import logging
import json
from flask import Flask, request, render_template, redirect, url_for
import pyttsx3

from api_information import update_notifications, gather_news, gather_weather, covid_statistics
from time_conversion import hhmm_to_seconds
from external_test import assert_external_files

s = sched.scheduler(time.time, time.sleep)
ALARMS = [] #the list that contains all alarms
NOTIFICATIONS = [] #the list of all current notifications

app = Flask(__name__)

@app.route('/')
def send_to_correct():
    """Redirect the user to the /index url instead of a blank one"""
    return redirect(url_for('home'))


@app.route('/index')
def home():
    """Generates the home screen for the clock interface"""
    #uses the globla values for ALARMS and notification rather than creating local values
    global ALARMS
    global NOTIFICATIONS

    s.run(blocking=False) # checks if any alarm has triggerd since the last time the page updated

    alarm_time = request.args.get("alarm")
    if alarm_time:

        #sets all the information for the alarm when the submit button is pressed
        title = request.args.get("two")
        alarm_date = alarm_time[0:10]
        time_of_alarm = alarm_time[11:]
        is_news = request.args.get("news")
        is_weather = request.args.get("weather")

        #converts to a boolean statement
        include_news = bool(is_news=='news')
        include_weather = bool(is_weather=='weather')
        set_alarm(title, alarm_date, time_of_alarm, include_news, include_weather)

    #checks if the delete button for a notification or alarm is pressed
    delete_notification = request.args.get("notif")
    if delete_notification:
        pop_notification(delete_notification)

    delete_alarm = request.args.get("alarm_item")
    if delete_alarm:
        pop_alarm(delete_alarm)

    #returns the information that needs to be injected into the into the HTML template
    return render_template('smart_alarm.html', title = 'Covid Smart Alarm System',
    image = 'Coronavirus.jpg', notifications=NOTIFICATIONS, alarms=ALARMS)


def next_day():
    """calculates all notifications that should run today and sets a delay for them
    This method is used to avoid having to calculate how long each month is which can
    become complex"""

    #Uses the global value for ALARMS rather than creating a local value
    global ALARMS

    #First checks if any set ALARMS are due to take place today
    for item in ALARMS:
        alarm_date = item['date']

        if alarm_date == str(date.today()):
            #if an alarm is due to take place today calculates the delay using delay - current time
            time_of_alarm = item['time']

            delay = hhmm_to_seconds(time_of_alarm)

            #Formats the time into the correct form and then calculates the time passed midnight
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_time_day = hhmm_to_seconds(current_time)

            if current_time > delay:
                #if the time for an alarm has passed the alarm runs instantly
                alarm_triggerd(item)
                logging.warning("alarm triggerd instantly as time had already passed %s", item)
            else:
                #sets the alarm with the calculated delay
                item["set alarm"] = s.enter((delay - current_time_day),2,alarm_triggerd,(item ,))
                logging.info("alarm due for today %s", item)



    #sets a new refresh alarm for midnight the next day that will check for any ALARMS that day
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_time_day = hhmm_to_seconds(current_time)

    s.enter((86400-current_time_day), 1, next_day,()) # sets the schedule for the next day


def gather_notifications():
    """Updates all NOTIFICATIONS and then sets a request to update them all again in 6 hours"""
    global NOTIFICATIONS #uses the global value for notification rather than creating a local value
    NOTIFICATIONS = update_notifications()
    #sets a timer for 6 hours time to replace the notification to prevent outdated news/weather
    s.enter(21600, 3, gather_notifications,())
    logging.info("Notifications where update: %s", NOTIFICATIONS)



def set_alarm(title: str, alarm_date: str, time_of_alarm: str, include_news: bool,
include_weather: bool):
    """takes the information when a new alarm is request
    and converts it into an alarm that can be displayed in ALARMS and set on the correct day"""
    global ALARMS

    invalid_data = False
    #prevents a second alarm with the same name from being created
    for item in ALARMS:
        if item["title"] == title:
            ALARMS.append({'title': "ERROR: name already exists",
                            'content': 'The system cannot create to ' +
                            'active timers with the same name'})
            logging.info("Couldn't creat a new alarm as an alarm with that name already exists")
            invalid_data = True


    #Section used to see if a day has passed date is in the format [YYYY-MM-DD]
    #checks in the order, year, month, day
    today = str(date.today())
    if invalid_data is not True:
        invalid_data = has_date_passed(alarm_date, today, title)

    #if both the date and name check where passed moves into setting the alarm
    if invalid_data is not True:
        #flips the date for display purposes to the format [dd-mm-yyyy]
        flip_date  = alarm_date.split('-')
        flip_date = flip_date[2] + "-" + flip_date[1] + "-" + flip_date[0]

        #Sets up the discription ready to be displayed in the list of ALARMS
        if include_news is True and include_weather is True:
            description = " the news, weather and current covid infection levels will be included"
        elif include_news is True:
            description = " the news and current covid infection levels will be included"
        elif include_weather is True:
            description = " the weather and current covid infection levels will be include"
        else:
            description = " current covid infection levels will be included"

        #if an alarm is today checks if the timeslot has already passed
        if alarm_date == str(today):
            delay = hhmm_to_seconds(time_of_alarm)

            now = datetime.now()
            current_time = now.strftime("%H:%M")

            current_time_day = hhmm_to_seconds(current_time)

            if current_time_day > delay:
                logging.info("User attempted to create a new alarm but failed as time had passed")
                ALARMS.append({'title': title,
                             'content': 'That time has already passed, therfore no alarm was set.'})

            else:
                #stores all the information for an alarm and adds it to ALARMS

                alarm = {'title': title,
                    'content': (flip_date +" at the time of: "+ time_of_alarm +
                    description),
                    'date': alarm_date,
                    'time': time_of_alarm,
                    'include news': include_news,
                    'include weather': include_weather }

                #sets the delay for the alarm from the current time
                alarm["set alarm"] = s.enter((delay - current_time_day),2,alarm_triggerd,(alarm ,))

                logging.info("set alarm: %s", alarm)
                ALARMS.append(alarm)

        else:
            #if the alarm isn't today the alarm is just added to the global ALARMS
            alarm = {'title': title,
                    'content': (flip_date +" at the time of: "+ time_of_alarm + description),
                    'date': alarm_date,
                    'time': str(time_of_alarm),
                    'include news': include_news,
                    'include weather': include_weather}

            logging.info("set alarm: %s", alarm)
            ALARMS.append(alarm)

def has_date_passed(alarm_date:str, today:str, title:str,) -> bool:
    """Checks if the date for a set alarm has already passed"""
    global ALARMS
    split_date = alarm_date.split('-')
    split_today = today.split('-')

    date_has_passed = False

    if int(split_date[0]) > int(split_today[0]):
        date_has_passed = False
    elif  int(split_date[0])== int(split_today[0]):

        if int(split_date[1]) > int(split_today[1]):
            date_has_passed = False
        elif  int(split_date[1])== int(split_today[1]):

            if int(split_date[2]) >= int(split_today[2]):
                date_has_passed = False
            else:
                logging.info("User attempted to create a new alarm but failed as date had passed")
                ALARMS.append({'title': title,
                               'content': 'Error cannot create an alarm for a day that has ' +
                               'already passed.'})
                date_has_passed = True
        else:
            logging.info("User attempted to create a new alarm but failed as date had passed")
            ALARMS.append({'title': title,
                           'content': 'Error cannot create an alarm for a day that has ' +
                           'already passed.'})
            date_has_passed = True
    else:
        logging.info("User attempted to create a new alarm but failed as date had passed")
        ALARMS.append({'title': title,
                       'content': 'Error cannot create an alarm for a day that has ' +
                       'already passed.'})
        date_has_passed = True

    return date_has_passed

def alarm_triggerd(alarm_active: dict):
    """Defines what to do when an alarm is triggered
    Finds out what the user requests to be read and then uses pyttsx3 to read that information
    When an alarm is triggerd a notification refresh is also performed"""
    global NOTIFICATIONS
    global ALARMS

    logging.info("alarm activated %s", alarm_active)
    engine = pyttsx3.init()
    #The engine always reads the title of the alarm and the current covid-19 levels
    engine.say(alarm_active["title"])
    covid_levels_read = covid_statistics()
    engine.say(covid_levels_read["content"])


    if alarm_active["include news"] is True:
        #gathers and reads the up to date headlines one by one
        news_to_read = gather_news()
        engine.say("The current headlines surronding the covid pandemic are")
        for item in news_to_read:
            engine.say("Headline: " + item["title"])
        NOTIFICATIONS.append(news_to_read)
    else:
        #only gathers news to update NOTIFICATIONS
        news_to_read = gather_news()

    if alarm_active["include weather"] is True:
        #gathers and reads the current weather
        weather_to_read = gather_weather()
        engine.say(weather_to_read["content"])
    else:
         #only gathers weather to update NOTIFICATIONS
        weather_to_read = gather_weather()

    for alar in ALARMS:
        if alar["title"] == alarm_active["title"]:
            #if the alarm is set for that day it is cancelled
            ALARMS.remove(alar) #removes the alarm that has been completed from ALARMS
            break

    engine.runAndWait() #reads out the prepared information
    #updates NOTIFICATIONS
    NOTIFICATIONS = news_to_read
    NOTIFICATIONS.append(weather_to_read)
    NOTIFICATIONS.append(covid_levels_read)
    logging.info("Notifications where update: %s", NOTIFICATIONS)


def pop_notification(notif_title):
    """Finds and removes a notification when the user chooses to remove it with the x"""
    global NOTIFICATIONS
    for notif in NOTIFICATIONS:
        if notif["title"] == notif_title:
            logging.info("removed the notification %s", notif)
            NOTIFICATIONS.remove(notif)
            break

def pop_alarm(alar_title):
    """Finds and removes an alarm when the user chooses to remove it with the x"""
    global ALARMS
    for alar in ALARMS:
        if alar["title"] == alar_title:
            #if the alarm is set for that day it is cancelled
            logging.info("removed the alarm %s", alar)
            if alar.get("set alarm") is not None:
                s.cancel(alar["set alarm"])
            ALARMS.remove(alar)
            break


def test_notification_removed():
    """Tests that removing notifications in the main project works correctly"""
    global NOTIFICATIONS
    NOTIFICATIONS = [{'title': "test news story", 'content': "description of news story",
                          'type': 'news'},
                          {'title': "test news story2",
                          'content': "description of another news story", 'type': 'news'},
                          {'title': "the current weather",
                          'content': "current weather elements", 'type': 'weather'},
                          {'title': "current covid infection rates",
                          'content': "the current infection rates for covid 19", 'type': 'covid'}]

    pop_notification("the current weather")

    assert NOTIFICATIONS == [{'title': "test news story",
                             'content': "description of news story", 'type': 'news'},
                             {'title': "test news story2",
                             'content': "description of another news story", 'type': 'news'},
                             {'title': "current covid infection rates",
                             'content': "the current infection rates for covid 19",
                             'type': 'covid'}], "pop_notification test: FAILED"
    NOTIFICATIONS = []

def test_alarm_removed():
    """Tests that removing alarms in the main project works correctly"""
    global ALARMS
    ALARMS = [{'title': "Test 1",
                    'content': "Content of an alarm",
                    'date': "2025-11-30",
                    'time': "12:01",
                    'include news': True,
                    'include weather': True },

                    {'title': "Test 2",
                    'content': "Content of an alarm",
                    'date': "2027-10-12",
                    'time': "14:53",
                    'include news': True,
                    'include weather': False }]

    pop_alarm("Test 2")
    assert ALARMS == [{'title': "Test 1",
                    'content': "Content of an alarm",
                    'date': "2025-11-30",
                    'time': "12:01",
                    'include news': True,
                    'include weather': True }], "pop_alarm test: FAILED"
    ALARMS = []


def test_set_alarm():
    """Tests that when an alarm is set it is correctly formatted as a notification
    and then pushed to the global alarms
    The alarm is set for 9999-12-31 so that the test date will not have passed for
    a very long time"""
    global ALARMS
    set_alarm("alarm system test", "9999-12-31", "23:59", True, False)

    assert ALARMS == [{'title': 'alarm system test',
                            'content': '31-12-9999 at the time of: 23:59 the news ' +
                            'and current covid infection levels will be included',
                            'date': '9999-12-31',
                            'time': '23:59',
                            'include news': True,
                            'include weather': False}], "set_alarm test: FAILED"

    ALARMS = []

def test_duplicate_alarm():
    """Tests that the system is successfully blocking alarms with duplicate
    names from being created"""
    global ALARMS
    ALARMS = [{'title': "Test 1",
                    'content': "Content of an alarm",
                    'date': "2025-11-30",
                    'time': "12:01",
                    'include news': True,
                    'include weather': True }]

    set_alarm("Test 1", "2025-11-30", "12:01", True, True)

    assert ALARMS ==[{'title': "Test 1",
                    'content': "Content of an alarm",
                    'date': "2025-11-30",
                    'time': "12:01",
                    'include news': True,
                    'include weather': True },
                    {'title': "ERROR: name already exists",
                    'content': 'The system cannot create to ' +
                    'active timers with the same name'}], "dupe alarm test: FAILED"
    ALARMS = []

def all_local_tests():
    """Combination of all local test"""
    test_notification_removed()
    test_alarm_removed()
    test_set_alarm()
    test_duplicate_alarm()


#When the programm is run collects all the required information and starts the app
if __name__ == '__main__':
    with open('config.json', 'r') as file_open:
        config_info = json.load(file_open)
        logging_info = config_info["logging info"][0]

    FORM = '%(asctime)-15s %(levelname)s %(message)s'
    logging.basicConfig(filename=logging_info["log location"], format=FORM, level=logging.info)

    #runs the tests on the main programme
    all_local_tests()

    #runs the tests on the other code in: api_information and time_conversion
    assert_external_files()

    next_day()
    gather_notifications()
    print("* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)")
    app.run()
