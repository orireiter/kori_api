import flask
from flask import Flask, request, jsonify
from flask_cors import CORS

import pymongo
from pymongo import MongoClient

import configparser
import re

#------------------------------------------------------------------#
# PARSER related

# creating a parser for a config file for better use later on
# it takes as an argument to parameter youre looking for
# and retrieves the variable in it
def get_config(parameter):
    parser = configparser.RawConfigParser()
    config_path = r".\api.config"
    parser.read(config_path)
    return parser.get('api-config', str(parameter))

#------------------------------------------------------------------#
# DB related

#-------------------------------------------------#
# connecting to db
# need to specify which collection you need, to easen later use
def db_connect(which_collection):
    try:
        # creating a client
        db_client = MongoClient()

        # assigning relevant variables from config
        db = get_config("db")
        collection = get_config(which_collection)    
        connection =  db_client[db][collection]
        print("Mongo: ", connection)
        # returning a connection to db so you only need to query/insert afterwards
        return connection
    except:
        print("Error: db related")
        return "Error: db related"
#-------------------------------------------------#

#------------------------------------------------------------------#
# FLASK related

#-------------------------------------------------#
# creating app
app = Flask(__name__)
# allowing different origins to communicate with it
cors = CORS(app, resources={r"/*": {"origins": "*"}})
#-------------------------------------------------#
# authentication route
# 
@app.route("/auth/local", methods=['GET','POST'])
def auth_credentials():
    #------------------------------#
    # json related
    try:     
        # taking the json file sent
        user_json = request.get_json()
        # making a list of keys and values for validation check
        # reg_key_list = list( user_json.keys() )
        # reg_value_list = list( user_json.values() )
        
    # json validations
    except:
        print("Error: json communication problem")
        return  "Error: json communication problem"
    
    #------------------------------#
    # sent info validation

    # checking if identifier is email
    if re.search("[@]", user_json['identifier']):
        # here its email
        print("email submitted")

        # connecting to db to look for email
        connection = db_connect('user_collection')
        look_for_email =  connection.find_one( { "email": str(user_json['identifier']) } )
        if look_for_email == None:
            # if no email was retrieved
            print("Error: email not found")
            return "Error: email not found"

        elif user_json['password'] != look_for_email['password']:
            # if email was retrieved but password is wrong
            print("Error: wrong password")
            return "Error: wrong password"
        else:
            # everything went good
            
            # looking for objectid and making it str to jsonify
            object_id = look_for_email['_id']
            look_for_email['_id'] = str(object_id)
            
            print("success")
            return jsonify(look_for_email)

    else:
        # here its username
        print("username submitted")    
        
        # connecting to db to look for username
        connection = db_connect('user_collection')
        look_for_name =  connection.find_one( { "username": str(user_json['identifier']) } )
        if look_for_name == None:
            # if no name was retrieved
            print("Error: username not found")
            return "Error: username not found"

        elif user_json['password'] != look_for_name['password']:
            # if email was retrieved but password is wrong
            print("Error: wrong password")
            return "Error: wrong password"
        else:
            # everything went good
            
            # looking for objectid and making it str to jsonify
            object_id = look_for_name['_id']
            look_for_name['_id'] = str(object_id)
            
            print("success")
            return jsonify(look_for_name)


#-------------------------------------------------#
# registration route
# ask koren if 'GET' method is needed here
@app.route("/auth/local/register", methods=['GET','POST'])
def register_credentials():
    #------------------------------#
    # json related
    try:     
        # taking the json file sent
        user_json = request.get_json()
        # making a list of keys and values for validation check
        # reg_key_list = list( user_json.keys() )
        reg_value_list = list( user_json.values() )
    
    # json validations
    except:
        print("Error: json communication problem")
        return  "Error: json communication problem"
    
    #------------------------------#
    # sent info validation
    for value0 in reg_value_list:
        # checking no field is empty
        if value0 == "" :
            print("empty field provided")
            return "Error: empty field provided"  
        # checking no field is just spaces
        elif len(value0)==value0.count(" "):
            print("one of fields provided is just spaces")
            return "Error: a field provided is just spaces"

    if len(user_json['password']) < 5 :
        # checking passowrd is at least 5 notes
        print("password too short")
        return "Error: password too short, at least 5 characters"

    elif len(user_json['username']) < 3 :
        # checking name is at least 3 notes
        print("name too short")
        return "Error: name too short, at least 3 characters"
    
    elif re.search("[@]", user_json['username']):
        # disallowing @ to distinguish between email and name later
        # need to disallow all special characters later on
        print("cant put @ in name")
        return "Error: cant put @ in name"

    elif not re.search("[@]", user_json['email']):
        # making @ mandatory to distinguish between email and name later
        # need to disallow special characters later on
        print("must put @ in email")
        return "Error: must put @ in email"
        
    else: 
    #------------------------------#
        # taking the info and putting it in DB
        # first ensuring strings
        username = str(user_json['username'])
        email = str(user_json['email'])
        password = str(user_json['password'])
        
        # then formatting to ensure db compatibility  
        db_obj = { 'username':username, 'email':email, 'password':password}
        
        # connecting to db with relevant collection - users
        registerer = db_connect('user_collection')
        
        # registering new user
        print("registration attempt of ", db_obj)
        try:
            registerer.insert_one(db_obj)
            return "Success: registration"
        except:
            print("Error: db communication")
            return "Error: db communication"
    #------------------------------#


#-------------------------------------------------#
# RUNNING THE APP # 
if __name__ == "__main__":
    # finding relevent configs before running
    host = get_config("host")
    port = get_config("port")
    debug_state = get_config("app_debug_state")
    app.run(host=host, port=port, debug=debug_state)
