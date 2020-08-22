# Rate Info Class file


class RateInfo:
    def __init__(self, gold22, gold24, silver):
        self.__gold22 = gold22
        self.__gold24 = gold24
        self.__silver = silver

    def get_gold22(self):
        return self.__gold22

    def get_gold24(self):
        return self.__gold24

    def get_silver(self):
        return self.__silver