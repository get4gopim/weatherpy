import pymongo
import logging
import os
import datetime
import time

# mongodb+srv://<username>:<password>@cluster0.zwfud.mongodb.net/<dbname>?retryWrites=true&w=majority
# read only user: configuser password: configpwd

# connection_url = 'mongodb+srv://cloud:mongoadmin@cluster0.zwfud.mongodb.net/test?retryWrites=true&w=majority'
connection_url = 'mongodb+srv://configuser:configpwd@cluster0.zwfud.mongodb.net/test?retryWrites=true&w=majority'

client = pymongo.MongoClient(connection_url)

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
LOGGER = logging.getLogger(__name__)

# Database
Database = client.get_database('demo')


def get_attr_config(query_str):
    start = time.time()
    try:
        collection = Database.get_collection('api_config')
        query = collection.find_one(query_str)
        if query is not None:
            attr_name = str(query.pop('attr_name'))
            attr_value = str(query.pop('attr_value'))
            last_updated = str(query.pop('last_updated'))
            LOGGER.info('attr_name [' + attr_name + ' : ' + attr_value + '] last_updated : ' + last_updated)
            LOGGER.info(f'time taken {time.time() - start} secs.')
            return attr_value
    except BaseException as ex:
        LOGGER.error(f'Unable to get config {query_str}  :- {repr(ex)}')
        LOGGER.error(ex)


def update_config(search_query, update_param):
    start = time.time()
    try:
        collection = Database.get_collection('api_config')
        query = collection.update_one(search_query, {'$set': update_param})
        if query.acknowledged:
            LOGGER.info(f"Update Successful : {update_param}")
            return True
        else:
            LOGGER.info("Update Failure")
            return False
        LOGGER.info(f'time taken {time.time() - start} secs.')
    except BaseException as ex:
        LOGGER.error(f'Unable to update config {search_query}  :- {repr(ex)}')
        LOGGER.error(ex)
    LOGGER.info(f'time taken {time.time() - start} secs.')
    return False


if __name__ == '__main__':
    # print(client.list_database_names())

    queryObject = {'attr_name': 'aws_weather_uri'}
    print(get_attr_config(queryObject))

    # print (datetime.datetime.now())
    #
    # updateObject = {'attr_value': 'https://rryf2kws46.execute-api.ap-south-1.amazonaws.com/dev', 'last_updated': datetime.datetime.now()}
    # update_config(queryObject, updateObject)
    #
    # get_attr_config(queryObject)

