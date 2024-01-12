import redis
from flask import jsonify
from xmlrpc.client import ServerProxy
from db.connection_manager import *

# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
instances = {}
# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

def store_instance(mobile_number, user_data):
    save_instance(mobile_number, user_data['name'], user_data['status'])

def remove_instance(mobile_number):
    server.remove_instance(mobile_number)
    delete_instance(mobile_number)

def update_instance(mobile_number, user_data):
    modify_instance(mobile_number, user_data['status'])

def retrieve_instance(mobile_number):
    # Retrieve JSON data from Redis using the mobile number as the key
    # return redis_client.get(mobile_number)
    instance = load_instance(mobile_number)
    return instance

def get_all_instances():
    print('Getting Instances from Instance Manager')
    return load_all_instances()
    


