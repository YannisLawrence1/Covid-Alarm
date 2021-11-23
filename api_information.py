"""Uses the diffrent apis needed for the covid smart alarm system to gather information
and to format it in the correct form for notifications"""
import json
import logging
import requests
from uk_covid19 import Cov19API

with open('config.json', 'r') as file_setup:
    logging_config = json.load(file_setup)
    logging_info = logging_config["logging info"][0]

FORM = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(filename=logging_info["log location"], format=FORM, level=logging.DEBUG)


def update_notifications() -> list:
    """Triggers all API clls and then combined into one list of notifications"""
    notifications = gather_news()
    weather = gather_weather()
    covid_num = covid_statistics()
    notifications.append(weather)
    notifications.append(covid_num)
    return notifications


def gather_news() -> list:
    """Gathers the first 5 current news articals using newsapi.org
    API key, topic and country can be changed using config.json file"""
    #opens the config file and gathers the dictionary for API information
    with open('config.json', 'r') as file_open:
        config_info = json.load(file_open)
        news_api_info = config_info["API information"][0]


    current_news = []

    base_url = "https://newsapi.org/v2/top-headlines?"
    api_key = news_api_info["news key"]
    country = news_api_info["news country"]
    topic = news_api_info["news topic"]

    #try to gather the news using the information provided in the config file
    try:
        complete_url = base_url + "country=" + country + "&q=" + topic + "&apiKey=" + api_key
        response = requests.get(complete_url)
        news_storys = response.json()

        #passes to a function to turn the news into notification format
        current_news = news_anaysis(news_storys)
        logging.info("News was successfully updated: %s", current_news)

    except KeyError:
        notification = {'title': "News cannot currently be gathered - KeyError",
                        'content': "This may be a API key issue please check config.json",
                        'type': 'news'}
        logging.error("KeyError occured when gathering the news")
        current_news.append(notification)

    except:
        notification = {'title': "News cannot currently be gathered",
                        'content': "sorry an unknow error occured",
                        'type': 'news'}
        logging.error("An unknown error occured whilst gathering the news")
        current_news.append(notification)

    return current_news

def news_anaysis(news_storys: list) -> list:
    """Converts the gatherd news into notification that can be displayed
    The max number of news storys at any time is 5"""
    current_news = []
    #Loop number is used to prevent the user been sent too many notifications at once
    num_of_loops = 0
    for i in news_storys['articles']:
        if num_of_loops > 4:
            break

        title = (i['title'])

        #sees if the news story has a description field and if it does saves it
        if i.get("description") is not None:
            story = (i["description"])

        #stores the notification and then appends it into current news
        notification = {'title': title, 'content': story, 'type': 'news'}
        current_news.append(notification)

        num_of_loops += 1

    return current_news


def gather_weather()-> dict:
    """Gathers the current weather using openweathermap.org
    API key, city can be changed using config.json file"""
    #opens the config file and gathers the dictionary for API information
    with open('config.json', 'r') as file_open:
        config_info = json.load(file_open)
        news_api_info = config_info["API information"][0]

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    api_key = news_api_info["weather key"]
    city_name = news_api_info["weather location"]

    try: #attempts to gather the current weather using the weather API
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        response = requests.get(complete_url)
        weather_file = response.json()

        current_weather = weather_analysis(weather_file, city_name)
        logging.info("Weather was successfully updated: %s", current_weather)

    except KeyError:
        current_weather = {'title': 'weather cannot be gathered - KeyError',
                          'content': 'This may be a API key issue please check config.json',
                          'type': 'weather'}
        logging.error("KeyError occured when gathering the news")

    except:
        current_weather = {'title': 'weather cannot be gathered',
                          'content': 'sorry an unknow error occured',
                          'type': 'weather'}
        logging.error("An unknown error occured whilst gathering the weather")

    return current_weather

def weather_analysis(weather_file: dict, city_name: str) -> dict:
    """Takes the data from gather weather and  turns it into notification format"""
    #Gathers the required information from the response from the weather API
    weather = weather_file["weather"]
    temps = weather_file["main"]
    current = round(temps["temp"] -273.15, 2) #converts the tempreture from kelvin to celcius
    feels_like = round(temps["feels_like"] -273.15, 2)

    #Formats the information on the weather into a notification that can be displayed
    current_weather = {'title': ('Current weather in ' + city_name),
                       'content': ('The current weather is "' +  weather[0]["description"] +
                       '" with tempretures of ' + str(current) +"°C that feels like "
                       + str(feels_like) + "°C"),
                       'type': 'weather'}

    return current_weather


def covid_statistics() -> dict:
    """Calculates the current covid levels in a given area using Public Health Englands's python api
    The area can be changed using config.json file"""
    #opens the config file and gathers the dictionary for API information
    try:
        with open('config.json', 'r') as file_open:
            config_info = json.load(file_open)
            news_api_info = config_info["API information"][0]

        area = news_api_info["covid area"]

        covid_location = [
        'areaName=' + area
        ]

        #sets the format for the response data for the covid levels
        cases_and_deaths = {
        "date": "date",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "newDeathsByDeathDate": "newDeathsByDeathDate",
        "cumDeathsByDeathDate": "cumDeathsByDeathDate"
        }

        api = Cov19API(filters=covid_location, structure=cases_and_deaths)
        result = api.get_json()
        complete_stats = covid_data_analysis(result, area)
        logging.info('covid statistics successfully gathered: %s', complete_stats)

    except KeyError:
        complete_stats = {'title': 'The UK covid 19 statistics cannot be gathered',
                         'content': 'Check that no areas of the config.json file are missing',
                         'type': 'covid'}
        logging.error("A KeyError occured whilst trying to gather covid statistics")

    except:
        complete_stats = {'title': 'The UK covid 19 statistics cannot be gathered',
                         'content': 'Please make sure you have used pip install uk-covid19',
                         'type': 'covid'}
        logging.error("An error occured with uk-covid19 it may not be installed")

    return complete_stats


def covid_data_analysis(result: list, area: str) -> dict:
    """Takes the data gathered by covid_statistics and turns it into a notification form"""
    total_new = 0
    total_death = 0

    latest = (result["data"][0])
    #loops through the first 7 days worth of data to gather the total number of deaths and cases
    for i in range(0, 6):
        last_week = (result["data"][i])
        total_new += last_week["newCasesByPublishDate"]
        if isinstance(last_week["newDeathsByDeathDate"], int):
            total_death += last_week["newDeathsByDeathDate"]

    #formats the gatherd information into a notification that can be understood by the user
    complete_stats = {'title': ('Current covid statistic for ' + area),
                     'content': ('The number of new Covid-19 cases as of ' + latest["date"]
                     + ', are: ' + str(latest["newCasesByPublishDate"]) +
                     ' with at total of: ' + str(total_new) +
                     ' new cases in the last 7 days and a total of: '+ str(total_death) +
                     ' new deaths in the last 7 days'),
                     'type': 'covid'}

    return complete_stats
