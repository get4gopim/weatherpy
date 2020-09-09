
from utility import util

preciption = "5% chance of rain until 19:30"
if len(preciption) > 0:
    idx = util.index_of(preciption, 'until')
    if idx > 0:
        preciption = preciption[0:idx]
        preciption = preciption.replace(' of', '', 1).strip()

print (preciption + ":")