import key
from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint


class MongoEntity:

    def __init__(self):
        try:
            client = MongoClient(key.MONGO_URL)
            # connected to DB
            self.connect = client['tgclients']
            #serverStatusResult = db.command("serverStatus")
            # pprint(serverStatusResult)
        except Exception as ex:
            pprint(ex)
