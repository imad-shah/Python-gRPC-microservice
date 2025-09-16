from mysql.connector import connect
from pymongo import MongoClient
def connect_sqldb():
    try:
        db = connect(
                host = 'localhost',
                user = 'root',
                password = 'password',
                database = 'my_database',
                )
        return db
    except:
        return None

def connect_mongodb():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['library']
        collection = db['patrons']
        return collection
    except:
        return None


if __name__ == '__main__':
    if connect_sqldb():
        print('MySQL Connected')

    if connect_mongodb() == None:
        print('MongoDB Connected')
