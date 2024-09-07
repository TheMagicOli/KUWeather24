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
from datetime import datetime

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

class WeatherAPI:
    def __init__(self, lat, long) -> None:
        #This lambda is used to return a datetime object from the
        #date format that they use in the weaterfile
        self.dateformat = lambda datestring: datetime.strptime(datestring, '%Y-%m-%d')
        #this table is used to convert the string used
        #by the weatherfile into the format used by meteostat
        self.apiConversionTable = [["temperature_max", "tmax"], ["temperature_min", "tmin"], ["precipitation_probability_max", "prcp"]]
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
        end = self.dateformat(day)
        #Get the location from the lat and long
        location = Point(self.lat, self.long)
        data = Daily(location, start, end)
        data = data.fetch()
        print(data)
        print(self.returnAPIConv(value))
        try:
            return data.loc[start, self.returnAPIConv(value)]
        except KeyError:
            raise  Exception("data wasn't found")
    def returnForDays(self, start, end, value):
        #Get the beginning and end day
        start = self.dateformat(start)
        end = self.dateformat(end)
        #Get the location from the lat and long
        location = Point(self.lat, self.long)
        data = Daily(location, start, end)
        data = data.fetch()

        return data.loc[start,  self.returnAPIConv(value)]
    def compareFor(self, value1, value2, valuestring):
        """Returns a comparision string. Value 1 is the location  data, Value2 is the WeatherParser data"""
        return "The " +  valuestring.replace("_", " ") +  " was " + str(value1) + " at " + str(self.lat) + ", " + str(self.long) + ". Meanwhile, it was " + str(value2) + " in the file."


class AndroidLinker:
    '''Links GUI Toga elements between the toga.App and WeatherFileParse'''
    def __init__(self, HelloWorldInstance, WeatherFileParserInstance):
        self.daySelectCounter = 0 #Multiplied by max length of selector box for scrolling
        #Pass both main app and the weather file parser
        self.HelloWorldInstance = HelloWorldInstance
        self.WeatherFileParserInstance = WeatherFileParserInstance
    def updateToFile(self):
        '''Updates toga.App to display the current weather file'''
        for i in range(4):
            try:
                #Append string to button in range(4)
                self.HelloWorldInstance.allButtons[i].text = self.WeatherFileParserInstance.get("date")[i]
            except IndexError: #Catch IndexError if file is less than four dates
                self.HelloWorldInstance.allButtons[i].text = ""
        #Weird code, but we wanna update the text display
        #to display the first date that displays, so we get it's string value
        # and get the day. However, if returning index 0 fails, then
        # we can fail and say it's not a weather file
        try:
            self.updateCurrentDayDisplay(self.WeatherFileParserInstance.get("date")[0])
        except IndexError:
            self.HelloWorldInstance.displayString()
    def updateBoxscrollUp(self):
        """Handles updating date button selection  when Next is clicked"""
        self.daySelectCounter += 1 #iterate daySelectCounter
        j = self.daySelectCounter * 4 #multiplies by 4, max view length
        for i in range(4): #Iterates through all buttons, len(4)
            try:
                #Tries to set text based off of the amount scrolled
                self.HelloWorldInstance.allButtons[i].text = self.WeatherFileParserInstance.get("date")[i+j] #Adds an offset based on amount scrolled
            except IndexError: #If we reach the End Of File (EOF)
                if i == 0: #If there's no data here at all, the user has scrolled past any data
                    self.daySelectCounter -= 1 #So we don't have infinite null scrolling
                    break #exit mainloop
                self.HelloWorldInstance.allButtons[i].text = "" #Sets the box to be empty
    def updateBoxscrollDown(self):
        """Handles updating date button selection  when Back  is clicked"""
        #Make sure to not return negative integers slices
        if not self.daySelectCounter-1 < 0:
            self.daySelectCounter -= 1
        #For documentation read updateBoxscrollUp above
        j = self.daySelectCounter * 4
        for i in range(4):
            try:
                self.HelloWorldInstance.allButtons[i].text = self.WeatherFileParserInstance.get("date")[i+j] ##ofset based on amount scrolled
            except IndexError:
                self.HelloWorldInstance.allButtons[i].text = ""
    def fetchData(self, seltype, begin, end, forvalue):
        forvalue = forvalue.replace(" ", "_") #fixes the forvalue to be the same as file format
        #Get the index of the start and end date
        firstIndex = self.WeatherFileParserInstance.returnIndexOfDate(begin)
        lastIndex  = self.WeatherFileParserInstance.returnIndexOfDate(end)
        print(self.WeatherFileParserInstance.get("date"))
        dayRange = self.WeatherFileParserInstance.get("date")[firstIndex:lastIndex]
        print(dayRange)
        #Based on the given key, we filter based on the day
        #bc it's a 1:1 ratio between the dates
         #For example, if 2024-04-31 is the second index
        #it's temp_max is also in the second index
        allDayValues = self.WeatherFileParserInstance.get(forvalue)[firstIndex:lastIndex]
        #we keep spaces for readability
        if seltype == "Get the minimum":
            self.HelloWorldInstance.displayString("The minimum is " + str(min(allDayValues)))
        if seltype == "Get the maximum":
            self.HelloWorldInstance.displayString("The maximum is " + str(max(allDayValues)))
        if seltype == "Get the average":
            allDayValues = list(map(float, allDayValues))
            self.HelloWorldInstance.displayString("The average is " + str(int(sum(allDayValues) / len(allDayValues))))
    def updateCurrentDayDisplay(self, day):
        #Updates the string in todayWillBe to be generated from
        # the WeatherEval function of the current date
        self.HelloWorldInstance.todayWillBe.text = self.WeatherFileParserInstance.evalWeatherCode(self.WeatherFileParserInstance.getForDay(day, "weather_code"))

        self.HelloWorldInstance.averagesText.text = "\n Max Temp:  " + self.WeatherFileParserInstance.getForDay(day, "temperature_max") + " Min Temp:" +  self.WeatherFileParserInstance.getForDay(day, "temperature_min") + "\n Percipitation Summary: " + self.WeatherFileParserInstance.getForDay(day, "precipitation_sum") + "\n Wind Speed (Max): " + self.WeatherFileParserInstance.getForDay(day, "wind_speed_max") + "\n Percipitation Probability (Max): " + self.WeatherFileParserInstance.getForDay(day, "precipitation_probability_max") + "\n"
        #Accordng to the docs, you need to be able to specifiy both the dates
        #and the index of the day (list style, so 0)
        datesWithIndexes = []
        i = 0
        for value in self.WeatherFileParserInstance.get("date"):
            datesWithIndexes.append(value + " : Day " + str(i))
            i += 1

        self.HelloWorldInstance.beginDay.items = datesWithIndexes
        self.HelloWorldInstance.endDay.items = datesWithIndexes


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
    def onlineBtn(self, button):
        """Compares value with weather data"""
        #self.andlink.online.
        pass
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
    def startup(self):
        """toga.App's main initalising of graphic elements"""
        #Initialise all libraries and attributes them to self
        #This is basically our __init__
        self.wdp = WeatherFileParser(defaultData)
        self.andlink = AndroidLinker(self, self.wdp)
        self.frontColorTheme = "white"
        self.backColorTheme = "black"
        #Create all GUI boxes
        mainBox = toga.Box(style=Pack(direction=COLUMN))
        hotbarBox  = toga.Box(style=Pack(direction=ROW))
        buttonBox = toga.Box(style=Pack(direction=ROW))
        scrollBox  = toga.Box(style=Pack(direction=ROW))
        contentBox = toga.Box(style=Pack(direction=COLUMN))

        #Make all graphical option buttons
        #hotbarBox
        self.openfile = toga.Button(
            text="Open",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.fileOpen
        )
        self.online = toga.Button(
            text="Compare Online",
            style=Pack(padding=(0, 5), width=200),
            on_press=self.onlineBtn
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
        #Scrollbox  selection
        self.scrollFwd = toga.Button(
            text="Next",
            on_press=self.fwdClick,
        )
        self.scrollBwd = toga.Button(
            text="Back",
            on_press=self.bwdClick,
        )
        self.scrollSpace = toga.Button(
            text="space",
            style=Pack(padding=(0, 5), width=240, visibility="hidden")
        )
        #Creates a list with allButtons that's refrerenced by the AndroidLinker
        self.allButtons = [self.optionOne, self.optionTwo, self.optionThree, self.optionFour]
        #The selected day object text
        self.todayWillBe = toga.Label(text="Select a date...", style=Pack(font_family="monospace", font_size=13, alignment=CENTER))
        self.averagesText = toga.Label(" ", style=Pack(font_family="monospace"))
        self.typeOfData  = toga.Selection(style=Pack(color=self.frontColorTheme), items=["Get the minimum", "Get the maximum", "Get the average"])
        self.betweenText = toga.Label(text="    between", style=Pack(font_family="monospace", font_size=15, alignment=CENTER))
        self.beginDay = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.andText = toga.Label(text="    and", style=Pack(font_family="monospace", font_size=15, alignment=CENTER))
        self.endDay = toga.Selection(style=Pack(color=self.frontColorTheme), items=self.wdp.get("date"))
        self.oftheText = toga.Label(text="    of the", style=Pack(font_family="monospace", font_size=15, alignment=CENTER))
        self.forValue = toga.Selection(style=Pack(color=self.frontColorTheme), items=["temperature max", "temperature min", "precipitation sum", "wind speed max", "weather code", "precipitation probability max"])
        self.getData =  toga.Button(
            text="Get Data",
            on_press=self.getDataBtn #Get and display data from sel
        )
        #Append all elements
        hotbarBox.add(self.openfile)
        buttonBox.add(self.optionOne)
        buttonBox.add(self.optionTwo)
        buttonBox.add(self.optionThree)
        buttonBox.add(self.optionFour)
        scrollBox.add(self.scrollBwd)
        scrollBox.add(self.scrollSpace)
        scrollBox.add(self.scrollFwd)
        contentBox.add(self.todayWillBe)
        contentBox.add(self.averagesText)
        contentBox.add(self.typeOfData)
        contentBox.add(self.oftheText)
        contentBox.add(self.forValue)
        contentBox.add(self.betweenText)
        contentBox.add(self.beginDay)
        contentBox.add(self.andText)
        contentBox.add(self.endDay)
        contentBox.add(self.getData)
        #Append all boxes to the mainBox in order
        mainBox.add(hotbarBox)
        mainBox.add(buttonBox)
        mainBox.add(scrollBox)
        mainBox.add(contentBox)

        #Retro-actively, here's a theme setting function for most of the buttons
        for widgets in hotbarBox.children:
            widgets.style.background_color = self.frontColorTheme
        for widgets in buttonBox.children:
            widgets.style.background_color = self.frontColorTheme
        #Then all of the content
        for widgets in contentBox.children:
            widgets.style.background_color = self.frontColorTheme
            if type(widgets) == type(toga.Selection()): #Special case for selection
                pass
        #Updates all GUI elements after being made to display current
        #weather data that's selected
        self.andlink.updateToFile()

        #Toga's initialising and displaying the mainBox
        self.main_window = toga.MainWindow(title="KU Weather App")
        self.main_window.full_screen = False
        self.main_window.content = mainBox
        mainBox.style.background_color = self.backColorTheme
        self.main_window.show()
    def displayString(self, string):
        self.main_window.info_dialog(
            "Task complete",
            string,
        )
    def askString(self, string):
        pass

def main():
    """Main execution, returns app"""
    return HelloWorld()
