import redis
from flask import jsonify
from xmlrpc.client import ServerProxy

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
instances = {}
# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

def store_instance(mobile_number, user_data):
    server.store_instance(mobile_number, user_data)

def update_instance(mobile_number, user_data):
    server.update_instance(mobile_number, user_data)

def retrieve_instance(mobile_number):
    # Retrieve JSON data from Redis using the mobile number as the key
    # return redis_client.get(mobile_number)
    return server.retrieve_instance(mobile_number)

def get_all_instances():
    print('Getting Instances from Instance Manager')
    instances = server.get_all_instances()
    print(instances)
    return jsonify(instances)


