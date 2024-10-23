#####################
# KU WEATHER APP 24 #
#  BY LUCAS FRIAS   #
#####################

#IMPORTS
# ALL TOGA
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

#All Java/Android versons
from pathlib import Path
from android.content import Intent
from android.net import Uri
from java.io import File
from android.content import Intent
from java import jarray, jbyte
from datetime import datetime, timedelta
from meteostat import Daily, Point
from flask import Flask, request, jsonify
from multiprocessing import Process
#GLOBAL VARIABLES

#default data is the data that is loaded into WeatherFileParser by default
defaultData = """date: 2024-04-24 2024-04-25 2024-04-26 2024-04-27 2024-04-28 2024-04-29
weather_code: 3.0 61.0 3.0 55.0 3.0 63.0
temperature_max: 54.9464 52.6064 61.9664 52.2464 52.6064 48.4664
temperature_min: 44.2364 47.1164 48.6464 47.9264 42.796402 40.0064 30
precipitation_sum: 0.0 0.22440945 0.0 0.1456693 0.0 0.2952756
wind_speed_max: 9.309791 10.116089 8.249648 10.711936 13.588738 7.4495792
precipitation_probability_max: 45.0 100.0 100.0 100.0 97.0 100.0"""



class WeatherFileParser:
    '''A module that interperts KU '24s weather data and encoding'''
    def __init__(self, data):
        self.data = data
        self.elements = self.data.split("\n")
    def returnWhole(self):
        '''Returns all data'''
        return self.data
    def returnParts(self):
        '''Returns data, segmented by line breaks'''
        return self.elements
    def returnIndexOfDate(self, date):
        '''Returns the current index of the date'''
        i = 0
        for value in self.get('date'):
            if value in date: #I know this is hacky, but it
                #saves a lot of time bc no two dates will
                #have one another in them
                #and removes all need to format the string
                #from the selection
                return i
            i += 1 #if the date doesn't match, iterate
        raise  IndexError  #returns an IndexError if we can't find it
    def get(self, key):
        '''Returns all values associated by a key'''
        for weatherbit in self.returnParts(): #iterate through all segments
            if key in weatherbit: #if the key string is in the data string
                weatherbitValues = weatherbit.replace(key + ": ", "") #remove key from string
                finalValues = []
                for stringValues in weatherbitValues.split(" "): #adds all values matching the key
                    finalValues.append(stringValues)
        return finalValues #returns them
    def getForDay(self, day, key):
        '''Returns data associated with day'''
        index = 0
        #This code gets the index of the date. Since the
        #file format is spaced out so that all data is vertical
        #based like a column. So if we find the index of the date,
        #we can return the value for that specific day bc they have
        #the same index
        for days in self.get("date"): #Gets the index of the date.
            if days == day: #if we match the date that we're trying to find
                break # we found the index
            index += 1 #otherwise iterate
        #If we iterated through the entire list
        #and couldn't find the date return an IndexError
        if index == len(self.get("date")):
            raise IndexError("Unknown Date: " + day)
        #otherwise, return the value associated with
        #that key on that specific day. Implicitly,
        #we don't accept an IndexError here
        return self.get(key)[index]
    def evalWeatherCode(self, code, humanable=True):
        '''Returns human readable weather codes based off of the documentation'''
        #Today will...
        weathercodes = [
            {"code": 0, "plain": "clear", "human": "be clear"},
            {"code": 1, "plain": "mostclear", "human": "be mostly clear"},
            {"code": 2, "plain": "kindacloudy", "human": "be somewhat cloudy"},
            {"code": 3, "plain": "cloudy", "human": "be overcast"},
            {"code": 45, "plain": "fog", "human": "be foggy"},
            {"code": 48, "plain": "rimefog", "human": "be rime foggy"},
            {"code": 51, "plain": "drizzlesmall", "human": "have a light drizzle"},
            {"code": 53, "plain": "drizzlemed", "human": "have a drizzle"},
            {"code": 55, "plain": "drizzlebig", "human": "have a dense drizzle"},
            {"code": 56, "plain": "colddrizzlesmall", "human": "have a cold light drizzle"},
            {"code": 57, "plain": "colddrizzlebig", "human": "have a cold dense drizzle"},
            {"code": 61, "plain": "rainsmall", "human": "be slightly rainy"},
            {"code": 63, "plain": "rainmed", "human": "be rainy"},
            {"code": 65, "plain": "rainbig", "human": "be very rainy"},
            {"code": 66, "plain": "coldrainsmall", "human": "have a cold light rain"},
            {"code": 67, "plain": "coldrainbig", "human": "have a cold dense rain"},
            {"code": 69, "plain": "endofplanetearth", "human": "rain moderate asteroids"},
            {"code": 71, "plain": "snowsmall", "human": "be somewhat snowy"},
            {"code": 73, "plain": "snowmed", "human": "be snowy"},
            {"code": 75, "plain": "snowbig", "human": "be very snowy"},
            {"code": 77, "plain": "snowgrains", "human": "rain snow grains"},
            {"code": 80, "plain": "showersmall", "human": "rain scattered showers"},
            {"code": 81, "plain": "showersmed", "human": "rain moderate showers"},
            {"code": 82, "plain": "showersbig", "human": "rain violent showers"},
            {"code": 85, "plain": "snowshowerssmall", "human": "snow light snow showers"},
            {"code": 86, "plain": "snowshowersbig", "human": "snow dense snow showers"},
            {"code": 95, "plain": "thunderstormsmall", "human": "have thunderstorms"},
            {"code": 96, "plain": "thunderstormhailslight", "human": "hail slighty with thunderstorms"},
            {"code": 99, "plain": "thunderstormhailheavy", "human": "hail heavily with thunderstorms"}

        ]
        #iterate through all values and return the matching weather code

        for value in weathercodes:
            print(value["code"])
            #for whatever reason, the data is a float even though
            # there's no decimal places, so we just convert it
            # to an int here
            if value["code"] == int(float(code)): #str because file
                return "  Today will " + value["human"] + "(" + code + ")"
        return "UNKOWN WEATHER CODE ERROR"

    def updateData(self, datanew):
        '''Updates the data to datanew'''
        self.data = datanew
        self.elements = datanew.split("\n")


class AndroidLinker:
    '''Links GUI Toga elements between the toga.App and WeatherFileParse'''
    def __init__(self, togaInstance, weatherfileInstance):
        self.daySelectCounter = 0 #Multiplied by max length of selector box for scrolling
        #Pass both main app and the weather file parser
        self.togaInstance = togaInstance
        self.currentTab = 0
        self.weatherfileInstance = weatherfileInstance
    def startREST(self):
        FlaskServer(self.weatherfileInstance).startMultiProcess()
    def mysteryCompare(self, seltype, begin, end, forvalue, begin2, end2, forvalue2):
        forvalue = forvalue.replace(" ", "_") #fixes the forvalue to be the same as file format
        forvalue2 = forvalue2.replace(" ", "_") #fixes the forvalue to be the same as file format

        #Get the index of the start and end date
        firstIndex = self.weatherfileInstance.returnIndexOfDate(begin)
        lastIndex  = self.weatherfileInstance.returnIndexOfDate(end)
        firstIndex2 = self.weatherfileInstance.returnIndexOfDate(begin2)
        lastIndex2  = self.weatherfileInstance.returnIndexOfDate(end2)
        print(firstIndex)
        print(lastIndex)
        print(firstIndex2)
        print(lastIndex2)
        print(self.weatherfileInstance.get("date"))
        dayRange = self.weatherfileInstance.get("date")[firstIndex:lastIndex]
        dayRange2 = self.weatherfileInstance.get("date")[firstIndex2:lastIndex2]

        #Based on the given key, we filter based on the day
        #bc it's a 1:1 ratio between the dates
         #For example, if 2024-04-31 is the second index
        #it's temp_max is also in the second index
        allDayValues = self.weatherfileInstance.get(forvalue)[firstIndex:lastIndex]
        allDayValues2 = self.weatherfileInstance.get(forvalue2)[firstIndex2:lastIndex2]
        #we keep spaces for readability
        finalValue1 = 0
        finalValue2 = 0
        resultString = "noneerror"
        if seltype == "Get the minimum":
            finalValue1 = min(allDayValues)
            finalValue2 = min(allDayValues2)
            resultString = "The minimum"
        if seltype == "Get the maximum":
            finalValue1 = max(allDayValues)
            finalValue2 = max(allDayValues2)
            resultString = "The maximum"
        if seltype == "Get the average":
            allDayValues = list(map(float, allDayValues))
            allDayValues2 = list(map(float, allDayValues))
            finalValue1 = int(sum(allDayValues) / len(allDayValues))
            finalValue2 = int(sum(allDayValues2) / len(allDayValues2))
            resultString = "The average"
        print(finalValue1)
        print(finalValue2)
        compString = "equal to"
        if finalValue1 > finalValue2:
            compString = "greater than"
        if finalValue1 < finalValue2:
            compString = "less than"
        self.togaInstance.displayString(resultString + " of " + forvalue +  " is " + str(min(allDayValues)) + " which is " + compString +  " the " + forvalue2 + " of " + str(min(allDayValues2)))
    def switchTab(self, newtab: int):
        '''Changes the currently dispayed tab on the mainBox element'''
        self.currentTab = newtab
        #Clear current window
        self.togaInstance.windowBox.clear()
        # The 'browse window' tab, 0
        if self.currentTab == 0:
            self.togaInstance.windowBox.add(self.togaInstance.dateSelectBox)
            self.togaInstance.windowBox.add(self.togaInstance.scrollBox)
            self.togaInstance.windowBox.add(self.togaInstance.contentBox)
            self.togaInstance.windowBox.add(self.togaInstance.imageBox)

        elif self.currentTab == 1:
            self.togaInstance.windowBox.add(self.togaInstance.compareBox)
        elif self.currentTab == 2:
            self.togaInstance.windowBox.add(self.togaInstance.moreBox)
        elif self.currentTab == 3:
            self.togaInstance.windowBox.add(self.togaInstance.onlineBox)
        elif self.currentTab == 4:
            self.togaInstance.windowBox.add(self.togaInstance.graphBox)
        elif self.currentTab == 5:
            self.togaInstance.windowBox.add(self.togaInstance.webBrowserViewer)
        elif self.currentTab == 6:
            self.togaInstance.windowBox.add(self.togaInstance.mysteryBox)
        else:
            self.togaInstance.windowBox.add(toga.Button(text="Unknown Tab: " + str(self.currentTab) + "selected"))
    def visualise(self):
        #Visualises data passed to function
        #First, clears all values in current graph by
        #manually fetching its contents
        self.togaInstance.graphCanvas.context.clear()
        #this is a long line, but basically pass to draw from values
        #which draws each value that is turned into an int/float by eval
        #and do it based on the key value snatched from wdp
        #and then selected between the range of these values below
        # (which returns int slices for the list of values):
        firstDay = self.weatherfileInstance.returnIndexOfDate(self.togaInstance.beginDay3.value)
        lastDay = self.weatherfileInstance.returnIndexOfDate(self.togaInstance.endDay3.value)
        #with the string from forValue 3 (woah)
        #except if this is equal to the percipitation sum
        #bc then we need to set the values multiplied by a factor of 100
        unformattedValues = [eval(i) for i in self.togaInstance.wdp.get(self.togaInstance.forValue3.value.replace(" ", "_"))[firstDay:lastDay]]
        if "sum" in self.togaInstance.forValue3.value.replace(" ", "_"):
            formattedValues = []
            print("TRUE GRRR")
            for unvalues in unformattedValues:
                formattedValues.append(unvalues * 100)
            print(formattedValues)
        else:
            #this means there is no difference in formatted values
            formattedValues = unformattedValues
        self.togaInstance.graphC.drawFromValues(formattedValues)

    def meteoEval(self):
        #Get the values of latitude and longitude
        #Convert to float for most accurate readings
        lat = float(self.togaInstance.latcoords.value)
        long = float(self.togaInstance.longcoords.value)
        #Get value of comparisson key
        daystring = str(self.togaInstance.onlineDateSelect.value)
        keyvaluestring = str(self.togaInstance.forValue2.value)
        #Generate point given
        pointgiven = MeteoAPI(lat, long)
        #try:
            #Attempt to access and return the data
            #answer = pointgiven.returnForDay(daystring, keyvaluestring)
            #self.togaInstance.displayString("The (" + keyvaluestring + ") is " + str(answer))
            #except Exception as e:
            #Sanatise and display error, fail overtly
            #self.togaInstance.displayString("(" + keyvaluestring + ") Something went wrong: " + str(e))
    def meteoCompare(self):
        #Get the values of latitude and longitude
        #Convert to float for most accurate readings
        lat = float(self.togaInstance.latcoords.value)
        long = float(self.togaInstance.longcoords.value)
        #Get value of comparisson key
        daystring = str(self.togaInstance.onlineDateSelect.value)
        keyvaluestring = str(self.togaInstance.forValue2.value)
        begincompare = str(self.togaInstance.beginDay2.value)
        endcompare = str(self.togaInstance.endDay2.value)

        #Generate point given
        pointgiven = MeteoAPI(lat, long)
        #try:
            #Attempt to access and return the data
        answer = pointgiven.returnForDay(daystring, keyvaluestring)
            #This is the files' answer
        answer2 = self.fetchAndReturnMeteoStat(seltype=self.togaInstance.typeOfData2.value, begin=self.togaInstance.beginDay2.value, end=self.togaInstance.endDay2.value, forvalue = self.togaInstance.forValue2.value)
        programOutput = pointgiven.compareFor(answer, answer2, keyvaluestring)
        self.togaInstance.displayString(programOutput)
            #except Exception as e:
            #Sanatise and display error, fail overtly
            #self.togaInstance.displayString("Something went wrong while getting " + keyvaluestring + ": " + str(e))

    def updateToFile(self):
        '''Updates toga.App to display the current weather file'''
        for i in range(4):
            try:
                #Append string to button in range(4)
                self.togaInstance.allButtons[i].text = self.weatherfileInstance.get("date")[i]
            except IndexError: #Catch IndexError if file is less than four dates
                self.togaInstance.allButtons[i].text = ""
        #Weird code, but we wanna update the text display
        #to display the first date that displays, so we get it's string value
        # and get the day. However, if returning index 0 fails, then
        # we can fail and say it's not a weather file
        try:
            self.updateCurrentDayDisplay(self.weatherfileInstance.get("date")[0])
        except IndexError:
            self.togaInstance.displayString()
    def updateBoxscrollUp(self):
        """Handles updating date button selection  when Next is clicked"""
        self.daySelectCounter += 1 #iterate daySelectCounter
        j = self.daySelectCounter * 4 #multiplies by 4, max view length
        for i in range(4): #Iterates through all buttons, len(4)
            try:
                #Tries to set text based off of the amount scrolled
                self.togaInstance.allButtons[i].text = self.weatherfileInstance.get("date")[i+j] #Adds an offset based on amount scrolled
            except IndexError: #If we reach the End Of File (EOF)
                if i == 0: #If there's no data here at all, the user has scrolled past any data
                    self.daySelectCounter -= 1 #So we don't have infinite null scrolling
                    break #exit mainloop
                self.togaInstance.allButtons[i].text = "" #Sets the box to be empty
    def updateBoxscrollDown(self):
        """Handles updating date button selection  when Back  is clicked"""
        #Make sure to not return negative integers slices
        if not self.daySelectCounter-1 < 0:
            self.daySelectCounter -= 1
        #For documentation read updateBoxscrollUp above
        j = self.daySelectCounter * 4
        for i in range(4):
            try:
                self.togaInstance.allButtons[i].text = self.weatherfileInstance.get("date")[i+j] ##ofset based on amount scrolled
            except IndexError:
                self.togaInstance.allButtons[i].text = ""

    def fetchAndReturnMeteoStat(self, seltype, begin, end, forvalue):
           forvalue = forvalue.replace(" ", "_") #fixes the forvalue to be the same as file format
           #Get the index of the start and end date
           firstIndex = self.weatherfileInstance.returnIndexOfDate(begin)
           lastIndex  = self.weatherfileInstance.returnIndexOfDate(end)
           dayRange = self.weatherfileInstance.get("date")[firstIndex:lastIndex]
           print(dayRange)
           #Based on the given key, we filter based on the day
           #bc it's a 1:1 ratio between the dates
            #For example, if 2024-04-31 is the second index
           #it's temp_max is also in the second index
           allDayValues = self.weatherfileInstance.get(forvalue)[firstIndex:lastIndex]
           if len(allDayValues) == 0:
               # this means that all the day values
               # are equal to 0 and thus that there is only a single day chosen
               dayChosen = self.weatherfileInstance.get('date')[firstIndex] #Get the first beginnign day
               allDayValues = self.weatherfileInstance.getForDay(dayChosen,forvalue)
               print(str(allDayValues))
               return str(allDayValues) #by definition, is the min, max, or avg of area
               #we keep spaces for readability
           if seltype == "Get the minimum":
                    return  str(min(allDayValues))
           if seltype == "Get the maximum":
                return  str(max(allDayValues))
           if seltype == "Get the average":
                allDayValues = list(map(float, allDayValues))
                return  str(int(sum(allDayValues) / len(allDayValues)))


    def fetchData(self, seltype, begin, end, forvalue):
        forvalue = forvalue.replace(" ", "_") #fixes the forvalue to be the same as file format
        #Get the index of the start and end date
        firstIndex = self.weatherfileInstance.returnIndexOfDate(begin)
        lastIndex  = self.weatherfileInstance.returnIndexOfDate(end)
        print(self.weatherfileInstance.get("date"))
        dayRange = self.weatherfileInstance.get("date")[firstIndex:lastIndex]
        print(dayRange)
        #Based on the given key, we filter based on the day
        #bc it's a 1:1 ratio between the dates
         #For example, if 2024-04-31 is the second index
        #it's temp_max is also in the second index
        allDayValues = self.weatherfileInstance.get(forvalue)[firstIndex:lastIndex]
        #we keep spaces for readability
        if seltype == "Get the minimum":
            self.togaInstance.displayString("The minimum is " + str(min(allDayValues)))
        if seltype == "Get the maximum":
            self.togaInstance.displayString("The maximum is " + str(max(allDayValues)))
        if seltype == "Get the average":
            allDayValues = list(map(float, allDayValues))
            self.togaInstance.displayString("The average is " + str(int(sum(allDayValues) / len(allDayValues))))
    def updateCurrentDayDisplay(self, day):
        #Updates the string in todayWillBe to be generated from
        # the WeatherEval function of the current date
        self.togaInstance.imageBox.clear()
        weatherCode = float(self.weatherfileInstance.getForDay(day, "weather_code"))
        #Add images of weathercode
        if weatherCode < 3:
            self.togaInstance.imageBox.add(self.togaInstance.clearImage)
        elif weatherCode < 55:
                self.togaInstance.imageBox.add(self.togaInstance.cloudyImage)
        elif weatherCode < 69:
                    self.togaInstance.imageBox.add(self.togaInstance.rainyImage)
        elif weatherCode < 77:
                    self.togaInstance.imageBox.add(self.togaInstance.snowyImage)
        else:
                            self.togaInstance.imageBox.add(self.togaInstance.snowyImage)
        #self.togaInstance.imageBox.add(self.togaInstance.)
        self.togaInstance.todayWillBe.text = self.weatherfileInstance.evalWeatherCode(self.weatherfileInstance.getForDay(day, "weather_code"))

        self.togaInstance.averagesText.text = "\n Max Temp:  " + self.weatherfileInstance.getForDay(day, "temperature_max") + " Min Temp:" +  self.weatherfileInstance.getForDay(day, "temperature_min") + "\n Percipitation Summary: " + self.weatherfileInstance.getForDay(day, "precipitation_sum") + "\n Wind Speed (Max): " + self.weatherfileInstance.getForDay(day, "wind_speed_max") + "\n Percipitation Probability (Max): " + self.weatherfileInstance.getForDay(day, "precipitation_probability_max") + "\n"
        #Accordng to the docs, you need to be able to specifiy both the dates
        #and the index of the day (list style, so 0)
        datesWithIndexes = []
        i = 0
        for value in self.weatherfileInstance.get("date"):
            datesWithIndexes.append(value + " : Day " + str(i))
            i += 1
        #Same thing but for meteostat without indexes
        datesWithoutIndexes = []
        for value in self.weatherfileInstance.get("date"):
            datesWithoutIndexes.append(str(value))
            i += 1

        self.togaInstance.beginDay.items = datesWithIndexes
        self.togaInstance.endDay.items = datesWithIndexes
        self.togaInstance.beginDay2.items = datesWithoutIndexes
        self.togaInstance.endDay2.items = datesWithoutIndexes
        self.togaInstance.beginDay3.items = datesWithoutIndexes
        self.togaInstance.beginDay4.items = datesWithoutIndexes
        self.togaInstance.beginDay5.items = datesWithoutIndexes


        self.togaInstance.endDay3.items = datesWithoutIndexes
        self.togaInstance.endDay4.items = datesWithoutIndexes
        self.togaInstance.endDay5.items = datesWithoutIndexes



class FlaskServer:
    def __init__(self, data):
        self.app = Flask(__name__)
        self.data = data
        self.setup_routes()

    def setup_routes(self):
        items = self.data

        @self.app.route('/')
        def return_home():
            print("/ REACHED \n\n\n\nWE GETTING PINGED")
            #formatted version of whatever date values exist

            formattedPUTOptions = ""
            for datevalues in self.data.get("date"):
                formattedPUTOptions = formattedPUTOptions + "<option>" + datevalues + "</option>"
            return """
            <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
            KU Weather App 24<br>
            Welcome! If you're seeing this page, the web server is running<br>
            <div class="w3-bar w3-black">
              <button class="w3-bar-item w3-button" onclick="openCity('London')">GET</button>
              <button class="w3-bar-item w3-button" onclick="openCity('Paris')">POST</button>
              <button class="w3-bar-item w3-button" onclick="openCity('Tokyo')">PUT</button>
              <button class="w3-bar-item w3-button" onclick="openCity('Delete')">DEL</button>
            </div>
            <div id="Delete" class="w3-container city">
            <form id="delForm">
            <select id="dateDel">
            """ +  formattedPUTOptions + """
            </form>
            <br>
            <form id="deleteForm">
                <input type="text" name="item_id" placeholder="Enter item ID to delete">
                <button type="submit">Delete Item</button>
            </form>
            <input type='submit' value='DELETE'>
            </div>
            <div id="London" class="w3-container city">
            <form action='items' method='GET'>
            <input type="submit" value="GET"> </input>
            </form>
            </div>
            <div id="Paris" class="w3-container city"><form action='items'  method="POST">
            <b>date <input type='text' name='date' id='date'></b><br>
            <b>weather_code <input type='text' name='weather_code' id='weather_code'></b><br>
            <b>temperature_max <input type='text' name='temperature_max' id='temperature_max'></b><br>
            <b>temperature_min <input type='text' name='temperature_min' id='temperature_min'></b><br>
            <b>precipitation_sum <input type='text' name='precipitation_sum' id='precipitation_sum'></b><br>
            <b>wind_speed_max <input type='text' name='wind_speed_max' id='wind_speed_max'></b><br>
            <b>precipitation_probability_max <input type='text' name='precipitation_probability_max' id='precipitation_probability_max'></b><br>
            <input type="submit" value="POST"></form></div>
            <div id="Tokyo" class="w3-container city">
            <form id="putForm">
                    <select id='datePUT'>
                    """ + formattedPUTOptions + """
                    </select>
                    <br>
                    <select id='keyPUT'>
                    <option>date</option>
                    <option>weather_code</option>
                    <option>temperature_max</option>
                    <option>temperature_min</option>
                    <option>precipitation_sum</option>
                    <option>wind_speed_max</option>
                    <option>precipitation_probability_max</option>
                    </select>
                    <br>
                    <input type="text" id="changePUT">
                    <br>
                    <input type="submit" value="PUT">
                </form>

                <script>
                    document.getElementById('deleteForm').addEventListener('submit', function (e) {
                        e.preventDefault();
                        const formData = new FormData(this);
                        const item_id = formData.get('item_id');

                        fetch(window.location.origin + '/items/' + item_id, {
                            method: 'DELETE'
                        });
                    });
                </script>
                <script>
                    document.getElementById('putForm').addEventListener('submit', async function (e) {
                        e.preventDefault();
                        const formData = new FormData(this);
                        const data = {};
                        formData.forEach((value, key) => (data[key] = value));

                        const response = await fetch('/items/1?date=' + document.getElementById('datePUT').value + '&key=' + document.getElementById('keyPUT').value+ '&change=' + document.getElementById('changePUT').value, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data),
                        });

                        const result = await response.json();
                        console.log(result);
                    });
                </script>
                <script>
                function openCity(cityName) {
                  var i;
                  var x = document.getElementsByClassName("city");
                  for (i = 0; i < x.length; i++) {
                    x[i].style.display = "none";
                  }
                  document.getElementById(cityName).style.display = "block";
                }
                </script>
                <script>
                openCity('London');
                </script>
            """

        @self.app.route('/items', methods=['GET'])
        def getItems():
            return jsonify(items.returnParts())

        @self.app.route('/items', methods=['POST'])
        def addItem():
            #data comes out in predictable way
            #so we should be assigning these right
            dataTypes = ["date", "weather_code", "temperature_max", "temperature_min", "precipitation_sum", "wind_speed_max", "precipitation_probability_max"]
            newParts = []
            i = 0
            for value in self.data.returnParts():
                #compounds the new value with the previous plus
                #space plus the request form data
                newParts.append(value + " " + request.form[dataTypes[i]])
                i += 1
            updatedString = "\n".join(newParts)
            #gross and icky but too late to rename namespace
            #just understand this is weatherfileparser as (self.data)
            self.data.data = updatedString
            self.data.elements = newParts
            return jsonify("Sucess!"), 201

        @self.app.route('/items/<int:item_id>', methods=['PUT'])
        def update_item(item_id):
            #item id is completely unused but the example
            #i ported has it and removing it will break it
            #and being so fr I got a couple hours to commit
            #this so -o-

            date = request.args.get('date')
            key = request.args.get('key')
            change = request.args.get('change')
            #kinda gross but we gonna make a seperate put function
            #built into here with self.data.data
            #corresponding to the index of the weatherdefault
            # we can go into the row through the key given
            dataTypes = ["date", "weather_code", "temperature_max", "temperature_min", "precipitation_sum", "wind_speed_max", "precipitation_probability_max"]
            currentWorkingData = self.data.elements
            #manually search for column of data
            row = 0
            for possibleDataTypePairs in dataTypes:
                #if the dataTypes is not in the current value
                print(key)
                print(possibleDataTypePairs)
                if not key in possibleDataTypePairs:
                    row += 1
                    break
            print(row)
            #manually search for the row by getting the index of the date
            column = self.data.returnIndexOfDate(date)
            #correct value
            rowOfData = self.data.elements[row]
            print(rowOfData)
            #split first at the : that seperate the key with values
            #then the spaces between the values
            columnOfRowOfDataWithKey = rowOfData.split(': ')
            finalRowFormatted = columnOfRowOfDataWithKey[1].split(" ")
            #this is where the magic happens! this is where we
            #set the key value back!
            finalRowFormatted[column] = change
            #lets repackage this and dump it back into self.data.data/elements
            newUnformattedChangedRow = " ".join(finalRowFormatted)
            #merge key with value
            newFormattedChangeRow = columnOfRowOfDataWithKey[0] + ": " + newUnformattedChangedRow
            #change the old row to the new formatted change
            currentWorkingData[row] = newFormattedChangeRow
            #Reassign and clean up
            self.data.elements = currentWorkingData
            self.data.data = "\n".join(self.data.elements)
            print(self.data.data)

            return "grr"

        @self.app.route('/items/<int:item_id>', methods=['DELETE'])
        def delete_item(item_id):
            return jsonify({'message': 'Item deleted'}), 200

    def start(self):
        self.app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)
    def startMultiProcess(self):
        print("RUNNING\n\n\n\n\n\n\n\n\n\n\n\n\n\nRUNNING\n\n\n\n\n\n\n\n")
        startServer = self.start
        server_process = Process(target=startServer)
        server_process.start()


class MeteoAPI:
    def __init__(self, lat, long) -> None:
        #This lambda is used to return a datetime object from the
        #date format that they use in the weaterfile
        self.dateformat = lambda datestring: datetime.strptime(datestring, '%Y-%m-%d')
        #this table is used to convert the string used
        #by the weatherfile into the format used by meteostat
        self.apiConversionTable = [["temperature max", "tmax"], ["temperature min", "tmin"], ["precipitation probability max", "prcp"], ["wind speed max", "wspd"]]
        #Sets the position of the lat and long
        self.lat = lat
        self.long = long
    def returnAPIConv(self, weatherParserValue):
        """Simple iterate function between the apiConversionTable"""
        for value in self.apiConversionTable:
            #Returns the value table
            if value[0] == weatherParserValue:
                return value[1]

    def returnForDay(self, day, value):
        """Returns the value for the day selected"""
        #Get the beginning and end day
        #Since they're the same, it's just one
        start = self.dateformat(day)
        end = self.dateformat(day) +  + timedelta(days=1)
        #Get the location from the lat and long
        location = Point(self.lat, self.long)
        print("start!")
        data = Daily(location, start, end)
        dataUn = data
        data = data.fetch()
        print("fetching!")
        try:
            if "temperature" in value:
                    print(self.returnAPIConv(value))
                    #Checks to see if it's a temperature
                    return self.toF(data.loc[start,  self.returnAPIConv(value)])
            if "precipitation" in value and "sum" in value:
                print("true")
                return dataUn.aggregate('prcp', 'sum')
            #If there's no temperature type, then
            #no conversion to F is needed
            return data.loc[start,  self.returnAPIConv(value)]
        except KeyError:
            raise Exception("Data Point wasn't found")

    def toF(self, celcius):
        return (celcius * 1.8) + 32
    def returnForDays(self, start, end, value):
        #Get the beginning and end day
        start = self.dateformat(start)
        end = self.dateformat(end)

        #Get the location from the lat and long
        location = Point(self.lat, self.long)
        data = Daily(location, start, end)
        dataUn = data
        data = data.fetch()
        if "temperature" in value:
            #Checks to see if it's a temperature
            return self.toF(data.loc[start,  self.returnAPIConv(value)])
        if "precipitation" in value and "sum" in value:
                print("true")
                return dataUn.aggregate('prcp', 'sum')
        return data.loc[start,  self.returnAPIConv(value)]
    def compareFor(self, value1, value2, valuestring):
        """Returns a comparision string. Value 1 is the location  data, Value2 is the WeatherParser data"""
        return "The " +  valuestring.replace("_", "") +  " was " + str(value1) + " at " + str(self.lat) + ", " + str(self.long) + ". Meanwhile, it was " + str(value2) + " in the file."
class graphContextManager():
    def __init__(self, graphContext):
        self.graphContext = graphContext
    def drawFromValues(self, values):
        #Iterate through each value
        #graph goes negative from either side and starts at
        #its highest left point at 0,0
        #y is initilly the original value
        #so we don't have some random value
        #floating around
        print(values)
        y = abs(values[0] -100)
        #x is floating around in the graph
        x = 0
        #iterate between the two
        i = 0
        #for each value in values
        for pointValue in values:
            #what is this? we need to inverse how the graph
            #works bc 0 is the highest value, so we subract it by
            #100 to get the other value and then return its absolute value
            realValue = str(pointValue) #for text later
            #just a little zero abs value error
            # i don't get don't mind me
            pointValue = abs(pointValue -100)
            print("NEWLINE: ")
            print("XI = " + str(x) + " YI = " + str(y))
            print("XF = " + str((i+1)*100) + " YF = " + str(pointValue))
            newy = pointValue
            #it's i + 1 so that i=0 does not have  value of 0*100
            #but still keeps list notation
            self.drawLine(x, y, (i+1)*50, newy)
            #reassign values
            x = (i+1)*50
            y = newy
            #iterate for loop
            i += 1
            with self.graphContext.Fill(color="black") as fill:
                circle = fill.arc(x=x, y=newy, radius=5)
            self.graphContext.stroke(color="black")

    def drawLine(self, xi, yi, xf, yf):
        yi = yi
        yf = yf
        self.graphContext.begin_path()
        self.graphContext.stroke(color="blue")
        self.graphContext.move_to(xi, yi)
        self.graphContext.line_to(xf, yf)
        self.graphContext.stroke(color="blue")

class HelloWorld(toga.App):
    '''The main toga.App function'''
    def fwdClick(self, button):
        """Progresses date bar forward"""
        self.andlink.updateBoxscrollUp()
    def bwdClick(self, button):
        """Progresses date bar backwards"""
        self.andlink.updateBoxscrollDown()
    def showInfoBtn(self, button):
        """Updates info after button is pressed for certain day"""
        day = str(button.text)
        self.andlink.updateCurrentDayDisplay(day)
    def getDataBtn(self, button):
        """Returns data specificed"""
        self.andlink.fetchData(seltype=self.typeOfData.value, begin=self.beginDay.value, end=self.endDay.value, forvalue = self.forValue.value)
    def compareBtn(self, button):
        """Compares value with weather data"""
        self.andlink.switchTab(1)
    def browseBtn(self, button):
        """Browse button that displays file tipes"""
        self.andlink.switchTab(0)
    def moreBtn(self, button):
        """Displays more tabs to explore"""
        self.andlink.switchTab(2)
    def onlineBtn(self, button):
        """Displays more tabs to explore"""
        self.andlink.switchTab(3)
    def graphTrigger(self, button):
            """Displays more tabs to explore"""
            self.andlink.switchTab(4)
    def mysteryTab(self, button):
        """Displays more tabs to explore"""
        self.andlink.switchTab(6)
    def runserver(self, button):
        """Displays more tabs to explore"""
        self.andlink.switchTab(5)
        self.displayString("Server started!")
    def ee():
        pass
    def meteoBackend(self, button):
        self.andlink.meteoEval()
    def meteoCompare(self, button):
        self.andlink.meteoCompare()
    def visualisevalue(self, button):
        self.andlink.visualise()
    def mysteryFunctionTie(self, button):
        self.andlink.mysteryCompare(seltype=self.typeOfData3.value, begin=self.beginDay4.value, end=self.endDay4.value, forvalue = self.forValue4.value, begin2=self.beginDay5.value, end2=self.endDay5.value, forvalue2 = self.forValue5.value)
    async def fileOpen(self, button):
            """Handles file opening of WeatherFileData"""
            #This is some Java Android system level calls.
            #I got this online from a toga discussion board,
            #and I'm not gonna BS to understand what's going
            #on bts but it works and that's good enough for me

            #This appears to call the dialog window and file type
            fileChose = Intent(Intent.ACTION_GET_CONTENT)
            fileChose.addCategory(Intent.CATEGORY_OPENABLE)
            fileChose.setType("*/*")

            # This is why the function is async, we wait for the sys file opener to load
            results  = await self._impl.intent_result(Intent.createChooser(fileChose, "Choose a file"))
            #I have no idea wtf this really does
            #Probably reads the file data from Java's sys call
            data = results['resultData'].getData()
            context = self._impl.native
            stream = context.getContentResolver().openInputStream(data)

            def readStream(stream):
                """This reads Java data stream stuff I think"""
                block = jarray(jbyte)(1024 * 1024)
                blocks = []
                while True:
                    bytes_read = stream.read(block)
                    if bytes_read == -1:
                        return b"".join(blocks)
                    else:
                        blocks.append(bytes(block)[:bytes_read])
            #This finally returns the raw undecoded byes of the file
            content = readStream(stream)
            #Updates the data by calling the apps WeatherFileParser
            #then updates to Android Linker
            #TODO, see if replace actually affects data
            self.wdp.updateData(content.decode('utf-8').replace("b'", "").replace('\'', ''))
            #updates selection to file
            self.andlink.updateToFile()
    async def runAsyncServer(self):
        await self.webBrowserViewer.load_url("http://127.0.0.1:5000")
    def startup(self):
        """toga.App's main initalising of graphic elements"""
        #Initialise all libraries and attributes them to self
        #This is basically our __init__
        self.wdp = WeatherFileParser(defaultData)
        self.andlink = AndroidLinker(self, self.wdp)
        self.frontColorTheme = "red"
        self.backColorTheme = "blue"
        #start the web server
        #self.andlink.startREST()
        #Create all GUI boxes
        #This is the main box that all elements are stored in
        self.mainBox = toga.Box(style=Pack(direction=COLUMN))
        #This is the box where all the windows of the box are
        #stored in. Changed with andlink.changeTab()
        #Is a child to the mainBox
        self.windowBox = toga.Box(style=Pack(direction=COLUMN))
        #This is the what changeTab() is linked to and is
        # a child to the mainBox
        self.hotbarBox  = toga.Box(style=Pack(direction=ROW))
        #This is where the dates are appended and selected
        #Is a child to to windowBox
        self.dateSelectBox = toga.Box(style=Pack(direction=ROW))
        #This is the box to scroll through these dates and is
        # a child to windowBox
        self.scrollBox  = toga.Box(style=Pack(direction=ROW))
        #This is a box that content is stored in and is a child
        #to windowBox
        self.contentBox = toga.Box(style=Pack(direction=COLUMN))
        #This is the box where the compare gui is stored and
        # this is a child to windowBox
        self.compareBox = toga.Box(style=Pack(direction=COLUMN, background_color=self.frontColorTheme))
        # This box allows for the online comparisson function
        # this is a child to windowbox
        self.onlineBox = toga.Box(style=Pack(direction=COLUMN, background_color=self.frontColorTheme))
        # This box displays all of the other features
        # extra to the application, parent to window
        self.moreBox = toga.Box(style=Pack(direction=COLUMN))
        #Make all graphical option buttons
        self.imageBox  = toga.Box(style=Pack(direction=ROW))

        #hotbarBox
        self.graphBox = toga.Box(style=Pack(direction=COLUMN, background_color=self.frontColorTheme))
        self.mysteryBox = toga.Box(style=Pack(direction=COLUMN, background_color=self.frontColorTheme))
        self.openfile = toga.Button(
            text="Open",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.fileOpen
        )
        self.browse = toga.Button(
            text="Browse",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.browseBtn
        )
        self.compare = toga.Button(
            text="Compare",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.compareBtn
        )
        self.more = toga.Button(
            text="More",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.moreBtn
        )
        self.online = toga.Button(
            text="Meteostat",
            style=Pack(padding=(0, 5), width=450, background_color=self.frontColorTheme),
            on_press=self.onlineBtn
        )
        self.graphbtn = toga.Button(
            text="visual graph",
            style=Pack(padding=(0, 5), width=450, background_color=self.frontColorTheme),
            on_press=self.graphTrigger
        )
        self.serverRun = toga.Button(
            text="run server",
            style=Pack(padding=(0, 5), width=450, background_color=self.frontColorTheme),
            on_press=self.runserver
        )
        #Optionsbox
        #the text is updated and the user should never see 'err'
        self.optionOne = toga.Button(
            text="err",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.showInfoBtn
        )
        self.optionTwo = toga.Button(
            text="err",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.showInfoBtn
        )
        self.optionThree = toga.Button(
            text="err",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.showInfoBtn
        )
        self.optionFour = toga.Button(
            text="err",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.showInfoBtn
        )
        #self.scrollBox  selection
        self.scrollFwd = toga.Button(
            text="Next",
            on_press=self.fwdClick,
            style=Pack(background_color=self.frontColorTheme),
        )
        self.scrollBwd = toga.Button(
            text="Back",
            on_press=self.bwdClick,
            style=Pack(background_color=self.frontColorTheme)
        )
        self.scrollSpace = toga.Button(
            text="space",
            style=Pack(padding=(0, 5), width=240, visibility="hidden")
        )
        #Creates a list with allButtons that's refrerenced by the AndroidLinker
        self.allButtons = [self.optionOne, self.optionTwo, self.optionThree, self.optionFour]
        #The selected day object text
        self.todayWillBe = toga.Label(text="Select a date...", style=Pack(font_family="verdana", font_size=13, alignment=CENTER))
        self.averagesText = toga.Label(" ", style=Pack(font_family="verdana"))
        self.typeOfData  = toga.Selection(style=Pack(color=self.frontColorTheme), items=["Get the minimum", "Get the maximum", "Get the average"])
        self.typeOfData2 = toga.Selection(style=Pack(color=self.frontColorTheme), items=["Get the minimum", "Get the maximum", "Get the average"])
        self.typeOfData3  = toga.Selection(style=Pack(color=self.frontColorTheme), items=["Get the minimum", "Get the maximum", "Get the average"])

        self.andCompareWithText =  toga.Label(text="   and compare it with", style=Pack(font_family="verdana", font_size=15, alignment=CENTER))
        self.betweenText = toga.Label(text="    between", style=Pack(font_family="verdana", font_size=15, alignment=CENTER))
        self.betweenText2 = toga.Label(text="    between", style=Pack(font_family="verdana", font_size=15, alignment=CENTER))
        self.betweenText3 = toga.Label(text="    between", style=Pack(font_family="verdana", font_size=15, alignment=CENTER))

        self.beginDay = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.beginDay2 = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.beginDay3 = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.beginDay4 = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.beginDay5 = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))

        self.andText = toga.Label(text="    and", style=Pack(font_family="verdana", font_size=15, alignment=CENTER))
        self.andText2 = toga.Label(text="    and", style=Pack(font_family="verdana", font_size=15, alignment=CENTER))

        self.endDay = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.endDay2 = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.endDay3 = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.endDay4 = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.endDay5 = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))

        self.oftheText = toga.Label(text="    of the", style=Pack(font_family="verdana", font_size=15, alignment=CENTER))
        self.forValue = toga.Selection(style=Pack(color=self.frontColorTheme), items=["temperature max", "temperature min", "precipitation sum", "wind speed max", "weather code", "precipitation probability max"])
        self.forValue2 = toga.Selection(style=Pack(color=self.frontColorTheme), items=["temperature max", "temperature min", "precipitation sum", "wind speed max", "weather code", "precipitation probability max"])
        self.forValue3 = toga.Selection(style=Pack(color=self.frontColorTheme), items=["temperature max", "temperature min", "precipitation sum", "wind speed max", "weather code", "precipitation probability max"])
        self.forValue4 = toga.Selection(style=Pack(color=self.frontColorTheme), items=["temperature max", "temperature min", "precipitation sum", "wind speed max", "weather code", "precipitation probability max"])
        self.forValue5 = toga.Selection(style=Pack(color=self.frontColorTheme), items=["temperature max", "temperature min", "precipitation sum", "wind speed max", "weather code", "precipitation probability max"])

        self.getData =  toga.Button(
            text="Get Data",
            style=Pack(background_color=self.backColorTheme),
            on_press=self.getDataBtn #Get and display data from sel
        )
        self.meteostatDataSelect  = toga.Selection(style=Pack(color=self.frontColorTheme), items=["Get the maximum temp", "Get the minimum temp", "Get the preciptation"])
        self.latcoordsText = toga.Label(text="Latitude: ")
        self.latcoords = toga.TextInput(value="34.052235", style=Pack(background_color=self.backColorTheme))
        self.longcoordsText = toga.Label(text="Longitutde: ")
        self.longcoords = toga.TextInput(value="-119.243683", style=Pack(background_color=self.backColorTheme))
        self.onlineDateSelect = toga.DateInput(style=Pack(background_color=self.frontColorTheme))
        self.meteostatGetBtn= toga.Button(
            text="Get Data",
            style=Pack(padding=(0, 5), width=100, background_color=self.backColorTheme),
            on_press=self.meteoBackend
        )
        self.meteostatGetBtn= toga.Button(
            text="Get Data",
            style=Pack(padding=(0, 5), width=100, background_color=self.backColorTheme),
            on_press=self.meteoBackend
        )
        self.compareAgainst = toga.Button(
            text="Compare Against DAte range",
            style=Pack(padding=(0, 5), width=300, background_color=self.backColorTheme),
            on_press=self.meteoCompare
        )
        self.graphGetValue = toga.Button(
            text="Visualise value",
            style=Pack(padding=(0, 5), width=300, background_color=self.backColorTheme),
            on_press=self.visualisevalue
        )
        self.graphCanvas = toga.Canvas(style=Pack(width=1000, height=150)
        )
        self.graphGetData = toga.Button(
            text="Display",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.meteoCompare
        )
        self.mysteryCheck = toga.Button(
            text="Check",
            style=Pack(padding=(0, 5), width=100, background_color=self.backColorTheme),
            on_press=self.mysteryFunctionTie
        )
        self.mysteryFeature1 = toga.Button(
            text="mystery",
            style=Pack(padding=(0, 5), width=450, background_color=self.frontColorTheme),
            on_press=self.mysteryTab
        )
        self.graphC = graphContextManager(self.graphCanvas.context)
        self.graphC.drawFromValues([0, 100, 50, 35, 100, 0])
        self.webBrowserViewer = toga.WebView()
        e = self.runAsyncServer()

        self.clearImage = toga.ImageView(toga.Image('clear.png'), style=Pack(width=400, height=400, alignment=CENTER))
        self.cloudyImage = toga.ImageView(toga.Image('cloudy.png'), style=Pack(width=400, height=400, alignment=CENTER))
        self.rainyImage = toga.ImageView(toga.Image('rainy.png'), style=Pack(width=400, height=400, alignment=CENTER))
        self.snowyImage = toga.ImageView(toga.Image('csnowy.png'), style=Pack(width=400, height=400, alignment=CENTER))
        self.scaryImage = toga.ImageView(toga.Image('deathlyrain.png'), style=Pack(width=400, height=400, alignment=CENTER))

        #Append all elements
        self.hotbarBox.add(self.openfile)
        self.hotbarBox.add(self.browse)
        self.hotbarBox.add(self.compare)
        self.hotbarBox.add(self.more)
        self.dateSelectBox.add(self.optionOne)
        self.dateSelectBox.add(self.optionTwo)
        self.dateSelectBox.add(self.optionThree)
        self.dateSelectBox.add(self.optionFour)
        self.scrollBox.add(self.scrollBwd)
        self.scrollBox.add(self.scrollSpace)
        self.scrollBox.add(self.scrollFwd)
        self.contentBox.add(self.todayWillBe)
        self.contentBox.add(self.averagesText)
        self.compareBox.add(self.typeOfData)
        self.compareBox.add(self.oftheText)
        self.compareBox.add(self.forValue)
        self.compareBox.add(self.betweenText)
        self.compareBox.add(self.beginDay)
        self.compareBox.add(self.andText)
        self.compareBox.add(self.endDay)
        self.compareBox.add(self.getData)
        self.moreBox.add(self.online)
        self.moreBox.add(self.graphbtn)
        self.moreBox.add(self.serverRun)
        self.moreBox.add(self.mysteryFeature1)
        self.onlineBox.add(self.latcoordsText)
        self.onlineBox.add(self.latcoords)
        self.onlineBox.add(self.longcoordsText)
        self.onlineBox.add(self.longcoords)
        self.onlineBox.add(self.onlineDateSelect)
        #self.onlineBox.add(self.meteostatGetBtn)
        self.onlineBox.add(self.typeOfData2)
        self.onlineBox.add(self.forValue2)
        self.onlineBox.add(self.beginDay2)
        self.onlineBox.add(self.endDay2)
        self.onlineBox.add(self.compareAgainst)
        self.graphBox.add(self.graphCanvas)
        self.graphBox.add(self.forValue3)
        self.graphBox.add(self.beginDay3)
        self.graphBox.add(self.endDay3)
        self.graphBox.add(self.graphGetValue)

        self.mysteryBox.add(self.typeOfData3)
        self.mysteryBox.add(self.forValue4)
        self.mysteryBox.add(self.betweenText2)
        self.mysteryBox.add(self.beginDay4)
        self.mysteryBox.add(self.endDay4)
        self.mysteryBox.add(self.andCompareWithText)
        self.mysteryBox.add(self.forValue5)
        self.mysteryBox.add(self.betweenText3)
        self.mysteryBox.add(self.beginDay5)
        self.mysteryBox.add(self.endDay5)
        self.mysteryBox.add(self.mysteryCheck)



        #Append all boxes to the windowBox in order
        #by setting the tab
        self.andlink.switchTab(1)
        #Add to the mainBox both the hotbar and the window (0 by default)
        self.mainBox.add(self.hotbarBox)
        self.mainBox.add(self.windowBox)

        #Retro-actively, here's a theme setting function for most of the buttons
        for widgets in self.hotbarBox.children:
            widgets.style.background_color = self.frontColorTheme
        for widgets in self.dateSelectBox.children:
            widgets.style.background_color = self.frontColorTheme
        #Then all of the content
        for widgets in self.contentBox.children:
            widgets.style.background_color = self.frontColorTheme
            if type(widgets) == type(toga.Selection()): #Special case for selection
                pass
        #Updates all GUI elements after being made to display current
        #weather data that's selected
        self.andlink.updateToFile()
        newasync = FlaskServer(self.wdp).startMultiProcess()
        #Toga's initialising and displaying the mainBox
        self.main_window = toga.MainWindow(title="KU Weather App")
        self.main_window.full_screen = False
        self.main_window.content = self.mainBox
        self.mainBox.style.background_color = self.backColorTheme
        self.main_window.show()
    def displayString(self, string):
        self.main_window.info_dialog(
            "Task complete!!",
            string,
        )
    def askString(self, string):
        pass

def main():
    """Main execution, returns app"""
    return HelloWorld()
