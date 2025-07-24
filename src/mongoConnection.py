from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# === CONNECT VÀO MONGODB ===
def connect_mongo(uri=None, db_name="HtechVolam", collection_name="money_monitor"):
    """
    Kết nối MongoDB Atlas và trả về collection.
    :param uri: MongoDB connection string URI
    :param db_name: Tên database
    :param collection_name: Tên collection
    :return: collection object
    """
    if uri is None:
        # URI mặc định - bạn nên thay bằng URI thật
        uri = "mongodb+srv://htechvolam:Htech317@htechvolam.oefc26z.mongodb.net/?retryWrites=true&w=majority&appName=HtechVolam"
        
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    return client, collection