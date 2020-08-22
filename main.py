# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import RateInfo
import WeatherInfo
import forecast

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    weather = forecast.get_weather()
    print(weather.get_location(), ' Temp: ', weather.get_temp())

    rate_info = forecast.get_gold_rate()
    print(rate_info.get_gold22(), ' S: ', rate_info.get_silver())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
