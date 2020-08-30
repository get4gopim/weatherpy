# Rate Info Class file
import util

class RateInfo:

    def __init__(self, gold22, gold24, silver, date, last_updated_time):
        self.__gold22 = self.remove_fraction (gold22)
        self.__gold24 = self.remove_fraction (gold24)
        self.__silver = silver
        self.__date = date
        self.__last_updated_time = last_updated_time
        self.error = None

    def remove_fraction(self, rate):
        idx = util.index_of(rate, ".")
        if idx > 0:
            rate = rate[0:idx]
        return rate

    def get_error(self):
        return self.error

    def set_error(self, error):
        self.error = error

    def get_gold22(self):
        return self.__gold22

    def get_gold24(self):
        return self.__gold24

    def get_silver(self):
        return self.__silver

    def get_date(self):
        return self.__date

    def get_last_updated_time(self):
        return self.__last_updated_time