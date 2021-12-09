from cryptography.fernet import Fernet
import pymongo
import json
import certifi

from cryptography.fernet import Fernet

def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("data/secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():

    return open("data/secret.key", "rb").read()

def decrypt(encrypted_message):

    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)





def save_data( url_mongo):
    client = pymongo.MongoClient(url_mongo, tlsCAFile=certifi.where())


    dbname = client['agroacacias']

    collection_name = dbname["mora_catilla"]


    with open('data/dataset_mongo.json') as file:
        file_data = json.load(file)
    if isinstance(file_data, list):
        collection_name.insert_many(file_data)
    else:
        collection_name.insert_one(file_data)


    client.close()




key = load_key()
f = Fernet(key)

clave=decrypt(b'gAAAAABhqGIE5ryVtZ7dLQ_bv0YSdbSNNO31uM2LGoXRIS7eUCrSF_jzJ7IJA_I9rNDTDBKRKLalacTdESNzs4dgdRq3mx5zjg==')

url_mongo = "mongodb://agroacacias:agroacacias@cluster0-shard-00-00.ekd3c.mongodb.net:27017,cluster0-shard-00-01.ekd3c.mongodb.net:27017,cluster0-shard-00-02.ekd3c.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-d8tcf2-shard-0&authSource=admin&retryWrites=true&w=majority"
save_data( url_mongo)

