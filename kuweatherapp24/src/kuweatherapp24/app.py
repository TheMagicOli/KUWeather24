#####################
# KU WEATHER APP 24 #
#  BY LUCAS FRIAS   #
#####################

#IMPORTS
# ALL TOGA
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

#All Java/Android versons
from pathlib import Path
from android.content import Intent
from android.net import Uri
from java.io import File
from android.content import Intent
from java import jarray, jbyte

#GLOBAL VARIABLES

#default data is the data that is loaded into WeatherFileParser by default
defaultData = """date: 2024-09-23 
weather_code: 3.0 
temperature_max: 54.9464 
temperature_min: 44.2364 
precipitation_sum: 0.0 
wind_speed_max: 9.309791
precipitation_probability_max: 45.0"""

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
        #we don't except an IndexError here
        return self.get(key)[index]
    def evalWeatherCode(code, humanable=True):
        '''Returns human readable weather codes based off of the documentation'''
        #Today will
        weathercodes = [
            {"code": 0, "plain": "clear", "human": "be clear"},
            {"code": 1, "plain": "mostclear", "human": "be mostly clear"},
            {"code": 2, "plain": "kindacloudy", "human": "be somewhat cloudy"},
            {"code": 3, "plain": "cloudy", "human": "be vercast"},
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
    def updateData(self, datanew):
        '''Updates the data to datanew'''
        self.data = datanew
        self.elements = datanew.split("\n")

class NaturalLanguageProcessing:
    def __init__(self):
        pass
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

class HelloWorld(toga.App):
    '''The main toga.App function'''
    def fwdClick(self, button):
        """Progresses date bar forward"""
        self.andlink.updateBoxscrollUp()
    def bwdClick(self, button):
        """Progresses date bar backwards"""
        self.andlink.updateBoxscrollDown()
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
            self.andlink.updateToFile()
    def startup(self):
        """toga.App's main initalising of graphic elements"""
        #Initialise all libraries and attributes them to self
        #This is basically our __init__
        self.wdp = WeatherFileParser(defaultData)
        self.andlink = AndroidLinker(self, self.wdp)
        #Create all GUI boxes
        mainBox = toga.Box(style=Pack(direction=COLUMN))
        hotbarBox  = toga.Box(style=Pack(direction=ROW))
        buttonBox = toga.Box(style=Pack(direction=ROW))
        scrollBox  = toga.Box(style=Pack(direction=ROW))
        
        #Make all graphical option buttons
        #hotbarBox
        self.openfile = toga.Button(
            text="Open",
            style=Pack(padding=(0, 5), width=100),
            on_press=self.fileOpen
        )
        #Optionsbox
        #the text is updated and the user should never see 'err'
        self.optionOne = toga.Button(
            text="err",
            style=Pack(padding=(0, 5), width=100)
        )
        self.optionTwo = toga.Button(
            text="err",
            style=Pack(padding=(0, 5), width=100)
        )
        self.optionThree = toga.Button(
            text="err",
            style=Pack(padding=(0, 5), width=100)
        )
        self.optionFour = toga.Button(
            text="err",
            style=Pack(padding=(0, 5), width=100)
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

        #Append all elements      
        hotbarBox.add(self.openfile)
        buttonBox.add(self.optionOne)
        buttonBox.add(self.optionTwo)
        buttonBox.add(self.optionThree)
        buttonBox.add(self.optionFour)
        scrollBox.add(self.scrollBwd)
        scrollBox.add(self.scrollSpace)
        scrollBox.add(self.scrollFwd)
        #Append all boxes to the mainBox in order
        mainBox.add(hotbarBox)
        mainBox.add(buttonBox)
        mainBox.add(scrollBox)

        #Updates all GUI elements after being made to display current
        #weather data that's selected
        self.andlink.updateToFile()

        #Toga's initialising and displaying the mainBox
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = mainBox
        self.main_window.show()

def main():
    """Main execution, returns app"""
    return HelloWorld()