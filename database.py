from pymongo import MongoClient

def connect_to_database():
    connection_string = "mongodb+srv://hoanghaiduong:hoanghaiduong@cluster0.usd3yhg.mongodb.net"
    client = MongoClient(connection_string)
    db = client["license-plate"]
    collection = db["cars"]
    return db, collection
