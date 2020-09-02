import asyncio
import threading
import time


async def my_callback(result):
    print("my_callback got:", result)
    return "My return value is ignored"


async def coro(number):
    print("coro")
    await asyncio.sleep(number)
    return number + 1


async def add_success_callback(fut, callback):
    result = await fut
    await callback(result)
    return result

def add():
    print ('add invoked')
    time.sleep(10)
    return 5;

# loop = asyncio.get_event_loop()
# task = asyncio.ensure_future(coro(10))
# task = add_success_callback(task, my_callback)
# print("test1")
# response = loop.run_until_complete(task)
# print("response:", response)
# loop.close()
# print("test2")

threading.Thread(add).start()
print ('returned')