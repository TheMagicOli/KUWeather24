class WeatherFileParser:
    def __init__(self, file):
        self.file = open(file, "r")
        self.elements = self.file.read().split("\n")
    def returnWhole(self):
        return self.file.read()
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

