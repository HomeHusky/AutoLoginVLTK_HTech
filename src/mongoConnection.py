from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
# === CONNECT VÀO MONGODB ===
def connect_mongo(uri=None, db_name="HtechVolam", collection_name="tai_khoan_may"):
    """
    Kết nối MongoDB Atlas và trả về collection.
    :param uri: MongoDB connection string URI
    :param db_name: Tên database
    :param collection_name: Tên collection
    :return: collection object
    """
    if uri is None:
        # URI mặc định - bạn nên thay bằng URI thật
        # uri = "mongodb+srv://htechvolam:Htech317@htechvolam.oefc26z.mongodb.net/?retryWrites=true&w=majority&appName=HtechVolam"
        uri = "mongodb://htechvolam:Htech317@htechvolam-shard-00-00.oefc26z.mongodb.net:27017,htechvolam-shard-00-01.oefc26z.mongodb.net:27017,htechvolam-shard-00-02.oefc26z.mongodb.net:27017/?ssl=true&replicaSet=atlas-8v6xvn-shard-0&authSource=admin&retryWrites=true&w=majority"
        

    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client[db_name]
    collection = db[collection_name]
    return client, collection