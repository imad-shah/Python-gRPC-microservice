from pymongo import MongoClient


def run():
    client = MongoClient("mongodb://localhost:27017/") 
    db = client["library_db"]  
    patrons = db["patrons"] 

    result = patrons.update_many(
        {"books": {"$exists": False}}, 
        {"$set": {"books": []}}       
    )

if __name__ == "__main__":
    run()