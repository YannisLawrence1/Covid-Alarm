 # Covid Smart Alarm System
___
(c) Yannis Lawrence, 2020

### Intro
Thank you for using the covid smart alarm system, this programme is can be used by following the set up guide below and by then opening the file
labled as main.py. Alarms can be set using the labled boxes in the middle of the system and will be diplayed on the lefthand side, notifications 
will be diplayed on the right side and will automatically refresh every 6 hours as well as whenever an alarm goes off to stop outdate information
from being shown. Alarms will always read out their title and the current covid-19 statsiticas and can be selected if they should read out the
current news or weather as well.

### How to set up
The software is easy to use however requires a little bit of start up work before running it please read the information below before opening
the software:
To run the programme it is recommended to use python 3.8 or later and, you must first provide API keys for both the [news api used](https://newsapi.org/)  and 
the [weather api used](https://openweathermap.org). When you have both the keys required for the software you need to open the app folder and 
edit the file named config.json put the keys into the fields labled "news key" for the key from newsapi.org and "weather key" for the key from 
openweathermap.org. Finally, make sure that you have installed the UK covid-19 api using "pip install uk-covid19" in either command prompt 
(windows) or the terminal (mac os / linux).
Once all of the requirments have been met in the folder "app" open the file main.py to start the programme and then open the address listed in 
either google chrome or microsoft edge as the programmes HTML template cannot be formatted correctly in firefox or safari. Further ajustments 
such as the location of where you would like the news, weather and covid-19 statistics, the topic of the displayed news articals and the location 
to keep log files can also be ajusted within the config.json file under their respective names.
In case of error the default values for the config file are (not including API keys):

    {
	"logging info":[{
		"log location": "log files/covid_alarm_log.log"
	}],

	"API information":[{
		"news key": "YOUR NEWS API KEY HERE https://newsapi.org/",
		"news country": "gb",
		"news topic": "covid",
		"weather key": "YOUR WEATHER API KEY HERE https://openweathermap.org",
		"weather location": "Exeter",
		"covid area": "Devon"
	}]
    }

### Testing
Included with the software are two testing file in the app folder: 
* testing in main.py - used to test that the notification and alarm system are working
* external_test.py - used to test that the APIs and time conversion system of the software are working correctly

Both lots of test will be automatically run when the programme is opened and will show an error message relating to a specific function if one is
found. It will also tell you about potential areas of the .config file that could be causing the error messages that are displayed, if no errors are found
the programme will start as expected.

### License
Copyright (c) [2020] [Yannis Lawrence]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
