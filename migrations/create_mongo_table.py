from pymongo import MongoClient
from pymongo.synchronous import collection


def run():
    client = MongoClient("mongodb://localhost:27017/") 
    db = client["library"]  

    collection_names = db.list_collection_names()
    exists = 'patron' in collection_names
    patrons = db["patrons"] 
    if not exists:
        patrons.insert_one({'id' : 1, 'name' : 'John Doe', 'books' : []})

if __name__ == "__main__":
    run()
