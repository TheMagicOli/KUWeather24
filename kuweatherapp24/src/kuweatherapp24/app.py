import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import requests

defaultData = """date: 2024-04-24 2024-04-25 2024-04-26 2024-04-27 2024-04-28 2024-04-29
weather_code: 3.0 61.0 3.0 55.0 3.0 63.0
temperature_max: 54.9464 52.6064 61.9664 52.2464 52.6064 48.4664
temperature_min: 44.2364 47.1164 48.6464 47.9264 42.796402 40.0064 30
precipitation_sum: 0.0 0.22440945 0.0 0.1456693 0.0 0.2952756
wind_speed_max: 9.309791 10.116089 8.249648 10.711936 13.588738 7.4495792
precipitation_probability_max: 45.0 100.0 100.0 100.0 97.0 100.0"""

class HelloWorld(toga.App):
    def startup(self):
        
        wdp = WeatherFileParser(defaultData)
        main_box = toga.Box(style=Pack(direction=COLUMN))

        name_label = toga.Label(
            "Weather Visualiser ",
            style=Pack(padding=(0, 5)),
        )

        self.container = toga.OptionContainer(
            content=[],
        )
        self.container.style.height = 80
        main_box.add(self.container)

        AndroidLinker.updateToFile(wdp, self)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


    def say_hello(self, widget):
        self.main_window.info_dialog(
            str(requests.get(self.name_input.value).status_code),
            "Hi there!",
        )


class WeatherFileParser:
    def __init__(self, data):
        self.data = data
        self.elements = self.data.split("\n")
    def returnWhole(self):
        return self.data
    def returnParts(self):
        return self.elements
    def get(self, key):
        for weatherbit in self.returnParts():
            if key in weatherbit:
                weatherbitValues = weatherbit.replace(key + ": ", "")
                finalValues = []
                for stringValues in weatherbitValues.split(" "):
                    finalValues.append(stringValues)
        return finalValues
    def getForDay(self, day, key):
        index = 0
        for days in self.get("date"): #iterate to get index point of day
            if days == day:
                break
            else:
                index += 1

        if index == len(self.get("date")): #Searched proved unsuccessful
            raise IndexError("Unknown Date: " + day)
        
        return self.get(key)[index]
    def evalWeatherCode(code, humanable=True):
        weathercodes = [
            {"code": 0, "plain": "clear", "human": "Clear skies"},
            {"code": 1, "plain": "mainly clear", "human": "Mostly clear"}
        ]

class AndroidLinker:
    def updateToFile(WeatherFileParserInstance, HelloWorldInstance):
        #Update date selector
        for value in WeatherFileParserInstance.get("date"):
            newBox = toga.Box()
            newBox.style.width = "500"
            HelloWorldInstance.container.content.append(value, newBox)

def main():
    return HelloWorld()