import os
from pymongo import MongoClient


def run():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    db = client["library"]

    collection_names = db.list_collection_names()
    patrons = db["patrons"]

    if patrons.count_documents({}) == 0:
        print("Inserting initial patron data...")
        patrons.insert_many([
            {'id': 1, 'name': 'John Doe', 'books': []},
            {'id': 2, 'name': 'Jane Doe', 'books': []}
        ])
        print("Initial patron data inserted")
    else:
        print("Patron collection already has data, skipping insert")

if __name__ == "__main__":
    run()
