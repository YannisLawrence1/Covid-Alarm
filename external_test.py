"""checks that all external files used in the clock programme are working as intended and includes
some suggestions for if some modules are not working"""
import json
from api_information import gather_news, news_anaysis, gather_weather, weather_analysis
from api_information import covid_statistics, covid_data_analysis
from time_conversion import hours_to_minutes, minutes_to_seconds, hhmm_to_seconds

def n_api_test():
    """Checks the news api gives a valid reponse"""
    result = gather_news()
    assert gather_news() != [{'title': 'News cannot currently be gathered - KeyError',
                             'content': 'This may be a API key issue please check config.json',
                              'type': 'news'}], "gather news test: FAILED, this may be an issue with the api key check the config file"

    assert gather_news() != [{'title': 'News cannot currently be gathered',
                        'content': 'sorry an unknow error occured',
                        'type': 'news'}], "gather news test: FAILED"
    

def n_anaysis_test():
    """Checks that the information from the covid api is correctly formatted into notifications"""
    with open('json_tests/gb-news.json', 'r') as file_open:
        articles = json.load(file_open)
    assert news_anaysis(articles) == [{'title': 'Primark shoppers can buy clothes online in lockdown using this hack â€“ but be prepared to pay more - The Sun',
                                      'content': '', 'type': 'news'},
                                      {'title': "Tesla's $40M loan that kept the lights on, and what it teaches all of us - Teslarati",
                                      'content': 'Oftentimes, many of us forget to look around and realize how fortunate we are to have what we have. In times where tensions are relatively high based on the current election, a pandemic, and a string of bad luck that we have all seemed to adopt throughout 202â€¦', 'type': 'news'},
                                      {'title': "Martin Lewis urges Sainsbury's to think again on Nectar deal | York Press - York Press",
                                      'content': "SAINSBURY'S is reviewing a major promotion after Martin Lewis urged it to make changes to avoid customers having to visit stores unnecessarily.", 'type': 'news'},
                                      {'title': 'London Covid: Why Heathrow Airport will stay open during lockdown 2 - My London',
                                      'content': 'A small number of essential retailers and food and beverage outlets remain open at the airport', 'type': 'news'},
                                      {'title': "Shoppers stockpile Aldi's fur throw after it returns to stores for first time in a year - Mirror Online",
                                      'content': 'A small number of essential retailers and food and beverage outlets remain open at the airport', 'type': 'news'}], "news_anaysis test: FAILED"


def w_api_test():
    """Checks that valid information is being gathered from the weather API"""
    assert gather_weather() != {'title': 'weather cannot be gathered - KeyError',
                                'content': 'This may be a API key issue please check config.json',
                                'type': 'weather'}, "gather weather test: FAILED, this may be an issue with the api key check the config file"

    assert gather_weather() != [{'title': 'weather cannot be gathered',
                          'content': 'sorry an unknow error occured',
                          'type': 'weather'}], "gather weather test: FAILED"

def w_anaysis_test():
    """Checks that information from the weather api is being correctly formatted as notifications"""
    with open('json_tests/weather-exeter.json', 'r') as file_open:
        weather = json.load(file_open)

    assert weather_analysis(weather, 'Exeter') == {'title': ('Current weather in Exeter'),
                       'content': ('The current weather is "light rain" with tempretures ' +
                       'of 13.17°C that feels like 11.81°C'),
                       'type': 'weather'}, "weather_analysis test: FAILED"


def c_api_test():
    """Checks the covid API gives a valid response"""
    assert covid_statistics() != [{'title': 'The UK covid 19 statistics cannot be gathered',
                         'content': 'Check that no areas of the config.json file are missing',
                         'type': 'covid'}], "gather covid statistics test: FAILED"

    assert covid_statistics() != [{'title': 'The UK covid 19 statistics cannot be gathered',
                         'content': 'Please make sure you have used pip install uk-covid19',
                         'type': 'covid'}], "gather covid statistics test: FAILED"


def c_anaysis_test():
    """Checks the covid data can be correctly formated as a notification"""
    with open('json_tests/covid-devon.json', 'r') as file_open:
        covid_level = json.load(file_open)

    assert covid_data_analysis(covid_level, 'Exeter') == {
                     'title': 'Current covid statistic for Exeter',
                     'content': "The number of new Covid-19 cases as of 2020-11-30, are: 69 with" +
                     " at total of: 597 new cases in the last 7 days and a total of: 13 new " +
                     "deaths in the last 7 days",
                     'type': 'covid'}, "covid_data_analysis test: FAILED"


def hours_test():
    """Assess if hours are being correctly translated into minutes"""
    assert hours_to_minutes(6) == 360, "hours_to_minutes test: FAILED"

def minutes_test():
    """Assess of minutes are correctly translated into seconds"""
    assert minutes_to_seconds(16) == 960, "minutes_to_seconds test: FAILED"

def time_test():
    """Assess that all the conversions are correctly converted into one total number"""
    assert hhmm_to_seconds("12:35") == 45300, "hhmm_to_seconds test: FAILED"

def assert_external_files():
    """"""
    n_api_test()
    n_anaysis_test()
    w_api_test()
    w_anaysis_test()
    c_api_test()
    c_anaysis_test()
    hours_test()
    minutes_test()
    time_test()


if __name__ == '__main__':
    assert_external_files()
