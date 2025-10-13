import os
from mysql.connector import connect
from pymongo import MongoClient


def connect_sqldb():
    try:
        db = connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'password'),
            database=os.getenv('MYSQL_DATABASE', 'my_database'),
        )
        return db
    except Exception as e:
        print(f"Failed to connect to MySQL: {e}")
        return None


def connect_mongodb():
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        client = MongoClient(mongo_uri)
        db = client['library']
        collection = db['patrons']
        return collection
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None


if __name__ == '__main__':
    if connect_sqldb():
        print('MySQL Connected')

    if connect_mongodb() == None:
        print('MongoDB Connected')
