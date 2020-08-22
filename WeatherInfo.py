# Weather Info Class file

class WeatherInfo:
    def __init__(self, temp, low, high, asof, condition, location):
        self.__temp = temp
        self.__low = low
        self.__high = high
        self.__asof = asof
        self.__condition = condition
        self.__location = location

    def get_temp(self):
        return self.__temp

    def get_low(self):
        return self.__low

    def get_high(self):
        return self.__high

    def get_as_of(self):
        return self.__asof

    def get_condition(self):
        return self.__condition

    def get_location(self):
        return self.__location
