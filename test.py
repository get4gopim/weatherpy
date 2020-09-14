import time
from utility import util

if __name__ == '__main__':
    location = '49ceef3a36a9f805cdbf9fb01da64837d038f2256d4c3457dca28833422e0000'
    location = 'kolathur'
    result = util.is_uuid(location)

    if result:
        print("Successful.")
    else:
        print("Not Matched.")

