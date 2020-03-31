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
        return  "Error: json communication problem", 404
    
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
            return "Error: email not found", 404

        elif user_json['password'] != look_for_email['password']:
            # if email was retrieved but password is wrong
            print("Error: wrong password")
            return "Error: wrong password", 404
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
            return "Error: username not found", 404

        elif user_json['password'] != look_for_name['password']:
            # if email was retrieved but password is wrong
            print("Error: wrong password")
            return "Error: wrong password", 404
        else:
            # everything went good
            
            # looking for objectid and making it str to jsonify
            object_id = look_for_name['_id']
            look_for_name['_id'] = str(object_id)
            
            print("success")
            return jsonify(look_for_name)


#-------------------------------------------------#
# registration route
@app.route("/auth/local/register", methods=['POST'])
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
        return  "Error: json communication problem", 404
    
    #------------------------------#
    # sent info validation
    for value0 in reg_value_list:
        # checking no field is empty
        if value0 == "" :
            print("empty field provided")
            return "Error: empty field provided", 404  
        # checking no field is just spaces
        elif len(value0)==value0.count(" "):
            print("one of fields provided is just spaces")
            return "Error: a field provided is just spaces", 404

    if len(user_json['password']) < 5 :
        # checking passowrd is at least 5 notes
        print("password too short")
        return "Error: password too short, at least 5 characters", 404

    elif len(user_json['username']) < 3 :
        # checking name is at least 3 notes
        print("name too short")
        return "Error: name too short, at least 3 characters", 404
    
    elif re.search("[@]", user_json['username']):
        # disallowing @ to distinguish between email and name later
        # need to disallow all special characters later on
        print("cant put @ in name")
        return "Error: cant put @ in name", 404

    elif not re.search("[@]", user_json['email']):
        # making @ mandatory to distinguish between email and name later
        # need to disallow special characters later on
        print("must put @ in email")
        return "Error: must put @ in email", 404
        
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
        print("registration attempt of user: ", db_obj)
        try:
            registerer.insert_one(db_obj)
            return "Success: registration"
        except:
            print("Error: db communication")
            return "Error: db communication", 404
    #------------------------------#


#-------------------------------------------------#
# posts route with method=POST
@app.route("/posts", methods=['POST'])
def register_post():
    #------------------------------#
    # json related
    try:     
        # taking the json file sent
        post_json = request.get_json()
        # making a list of keys and values for validation check
        # reg_key_list = list( user_json.keys() )
        post_value_list = list( post_json.values() )
    
    # json validations
    except:
        print("Error: json communication problem")
        return  "Error: json communication problem", 404
    
    #------------------------------#
    # sent info validation
    for post_value in post_value_list:
        # checking no field is empty
        if post_value == "" :
            print("empty field provided")
            return "Error: empty field provided", 404  
        # checking no field is just spaces
        elif len(post_value)==post_value.count(" "):
            print("one of fields provided is just spaces")
            return "Error: a field provided is just spaces", 404

    #------------------------------#
        # taking the info and putting it in DB
        # first ensuring strings
        name = str(post_json['name'])
        title = str(post_json['title'])
        description = str(post_json['description'])
        
        # then formatting to ensure db compatibility  
        db_obj = { 'name':name, 'title':title, 'description':description}
        
        # connecting to db with relevant collection - posts
        post_registerer = db_connect('post_collection')
        
        # registering new post
        print("registration attempt of post:", db_obj)
        try:
            post_registerer.insert_one(db_obj)
            return "Success: registration"
        except:
            print("Error: db communication")
            return "Error: db communication", 404
    #------------------------------#


#-------------------------------------------------#
# posts route with method=GET
@app.route("/posts", methods=['GET'])
def retrieve_posts():
        
    # a list to append all posts to and then jsonify
    all_posts = []

    try:
        # connecting to db with relevant collection - posts
        post_retriever = db_connect('post_collection')
        
        # querying all of the posts db
        posts_query = post_retriever.find({})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # appending them to the list stated above
    for post in posts_query:
        
        
        # looking for objectid and making it str to jsonify later on
        object_id = post['_id']
        post['_id'] = str(object_id)
        
        print(post)
        all_posts.append(post)
    
    

    try:
        print("trying to return the queries")
        return jsonify(all_posts)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#


#-------------------------------------------------#
# posts route with method=DELETE

@app.route("/posts/<string:id>", methods=['DELETE'])
def remove_post(id):
    from bson.objectid import ObjectId        
    print(id)
    try:
        # connecting to db with relevant collection - posts
        post_delete = db_connect('post_collection')
        
        # deleting the relevant object
        p = post_delete.delete_one({'_id': ObjectId(id)})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # returning answer
    try:
        print(f'deleted post with id {id}')
        return jsonify(id)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#


#-------------------------------------------------#
# tasks route with method=POST
@app.route("/tasks", methods=['POST'])
def register_task():
    #------------------------------#
    # json related
    try:     
        # taking the json file sent
        task_json = request.get_json()
        # making a list of keys and values for validation check
        # reg_key_list = list( user_json.keys() )
        task_value_list = list( task_json.values() )
    
    # json validations
    except:
        print("Error: json communication problem")
        return  "Error: json communication problem", 404
    
    #------------------------------#
    # sent info validation
    for task_value in task_value_list:
        # checking no field is empty
        if task_value == "" :
            print("empty field provided")
            return "Error: empty field provided", 404  
        # checking no field is just spaces
        elif len(task_value) == task_value.count(" "):
            print("one of fields provided is just spaces")
            return "Error: a field provided is just spaces", 404

    #------------------------------#
        # taking the info and putting it in DB
        # first ensuring strings
        task = str(task_json['task'])
        
        # then formatting to ensure db compatibility  
        db_obj = { 'task': task}
        
        # connecting to db with relevant collection - posts
        task_registerer = db_connect('task_collection')
        
        # registering new post
        print("registration attempt of task:", db_obj)
        try:
            task_registerer.insert_one(db_obj)
            return "Success: registration"
        except:
            print("Error: db communication")
            return "Error: db communication", 404
    #------------------------------#


#-------------------------------------------------#
# tasks route with method=GET
@app.route("/tasks", methods=['GET'])
def retrieve_tasks():
        
    # a list to append all posts to and then jsonify
    all_tasks = []

    try:
        # connecting to db with relevant collection - posts
        task_retriever = db_connect('task_collection')
        
        # querying all of the posts db
        tasks_query = task_retriever.find({})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # appending them to the list stated above
    for task in tasks_query:
        print(task)
        
        # looking for objectid and making it str to jsonify later on
        object_id = task['_id']
        task['_id'] = str(object_id)
        
        
        all_tasks.append(task)
    
    

    try:
        print("trying to return the queries")
        return jsonify(all_tasks)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#


#-------------------------------------------------#
# tasks route with method=DELETE

@app.route("/tasks/<string:id>", methods=['DELETE'])
def remove_task(id):
    from bson.objectid import ObjectId        
    try:
        # connecting to db with relevant collection - posts
        task_delete = db_connect('task_collection')
        
        # deleting the relevant object
        task_delete.delete_one({'_id': ObjectId(id)})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # returning answer
    try:
        print(f'deleted post with id {id}')
        return jsonify(id)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#


#-------------------------------------------------#
# calendars route with method=POST
@app.route("/calenders", methods=['POST'])
def register_date():
    #------------------------------#
    # json related
    try:     
        # taking the json file sent
        date_json = request.get_json()
        # making a list of keys and values for validation check
        # reg_key_list = list( user_json.keys() )
        date_value_list = list( date_json.values() )
    
    # json validations
    except:
        print("Error: json communication problem")
        return  "Error: json communication problem", 404
    
    #------------------------------#
    # sent info validation
    for date_value in date_value_list:
        # checking no field is empty
        if date_value == "" :
            print("empty field provided")
            return "Error: empty field provided", 404  
        # checking no field is just spaces
        elif len(date_value) == date_value.count(" "):
            print("one of fields provided is just spaces")
            return "Error: a field provided is just spaces", 404

    #------------------------------#
        # taking the info and putting it in DB
        # first ensuring strings
        title = str(date_json['title'])
        date = str(date_json['date'])

        # then formatting to ensure db compatibility  
        db_obj = { 'title': title, 'date': date }
        
        # connecting to db with relevant collection - posts
        date_registerer = db_connect('calendar_collection')
        
        # registering new post
        print("registration attempt of date:", db_obj)
        try:
            date_registerer.insert_one(db_obj)
            return "Success: registration"
        except:
            print("Error: db communication")
            return "Error: db communication", 404
    #------------------------------#


#-------------------------------------------------#
# calendars route with method=GET
@app.route("/calenders", methods=['GET'])
def retrieve_calendar():
        
    # a list to append all posts to and then jsonify
    all_dates = []

    try:
        # connecting to db with relevant collection - posts
        date_retriever = db_connect('calendar_collection')
        
        # querying all of the posts db
        dates_query = date_retriever.find({})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # appending them to the list stated above
    for date in dates_query:
        print(date)
        
        # looking for objectid and making it str to jsonify later on
        object_id = date['_id']
        date['_id'] = str(object_id)
        
        
        all_dates.append(date)
    
    

    try:
        print("trying to return the queries")
        return jsonify(all_dates)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#


#-------------------------------------------------#
# calendars route with method=DELETE
@app.route("/calenders/<string:id>", methods=['DELETE'])
def remove_date(id):
    from bson.objectid import ObjectId        
    try:
        # connecting to db with relevant collection - posts
        date_delete = db_connect('calendar_collection')
        
        # deleting the relevant object
        date_delete.delete_one({'_id': ObjectId(id)})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # returning answer
    try:
        print(f'deleted post with id {id}')
        return jsonify(id)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#


#-------------------------------------------------#
# users connectivity check route with method=POST
@app.route("/onlines", methods=['POST'])
def register_online():
    #------------------------------#
    # json related
    try:     
        # taking the json file sent
        online_json = request.get_json()
        # making a list of keys and values for validation check
        # reg_key_list = list( user_json.keys() )
        online_value_list = list( online_json.values() )
    
    # json validations
    except:
        print("Error: json communication problem")
        return  "Error: json communication problem", 404
    
    #------------------------------#
    # sent info validation
    for online_value in online_value_list:
        # checking no field is empty
        if online_value == "" :
            print("empty field provided")
            return "Error: empty field provided", 404  
        # checking no field is just spaces
        elif len(online_value) == online_value.count(" "):
            print("one of fields provided is just spaces")
            return "Error: a field provided is just spaces", 404

    #------------------------------#
        # taking the info and putting it in DB
        # first ensuring strings
        name = str(online_json['name'])
        
        # then formatting to ensure db compatibility  
        db_obj = { 'name': name }
        
        # connecting to db with relevant collection - posts
        online_registerer = db_connect('online_collection')
        
        # registering new post
        print("registration attempt of online user:", db_obj)
        try:
            online_registerer.insert_one(db_obj)
            return "Success: registration"
        except:
            print("Error: db communication")
            return "Error: db communication", 404
    #------------------------------#


#-------------------------------------------------#
# users connectivity check route with method=GET
@app.route("/onlines", methods=['GET'])
def retrieve_onlines():
        
    # a list to append all posts to and then jsonify
    all_onlines = []

    try:
        # connecting to db with relevant collection - posts
        online_retriever = db_connect('online_collection')
        
        # querying all of the posts db
        onlines_query = online_retriever.find({})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # appending them to the list stated above
    for online in onlines_query:
        print(online)
        
        # looking for objectid and making it str to jsonify later on
        object_id = online['_id']
        online['_id'] = str(object_id)
        
        
        all_onlines.append(online)
    
    

    try:
        print("trying to return the queries")
        return jsonify(all_onlines)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#


#-------------------------------------------------#
# users connectivity check route with method=DELETE
@app.route("/onlines/<string:user_name>", methods=['DELETE'])
def remove_online(user_name):
    from bson.objectid import ObjectId        
    try:
        # connecting to db with relevant collection - posts
        online_delete = db_connect('online_collection')
        
        # deleting the relevant object
        online_delete.delete_one({'name': user_name})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # returning answer
    try:
        print(f'deleted post with id {id}')
        return jsonify(id)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#

#-------------------------------------------------#
# projects route with method=POST
@app.route("/projects", methods=['POST'])
def register_project():
    #------------------------------#
    # json related
    try:     
        # taking the json file sent
        project_json = request.get_json()
        # making a list of keys and values for validation check
        # reg_key_list = list( user_json.keys() )
        project_value_list = list( project_json.values() )
    
    # json validations
    except:
        print("Error: json communication problem")
        return  "Error: json communication problem", 404
    
    #------------------------------#
    # sent info validation
    for project_value in project_value_list:
        # checking no field is empty
        if project_value == "" :
            print("empty field provided")
            return "Error: empty field provided", 404  
        # checking no field is just spaces
        elif len(project_value) == project_value.count(" "):
            print("one of fields provided is just spaces")
            return "Error: a field provided is just spaces", 404

    #------------------------------#
        # taking the info and putting it in DB
        # first ensuring strings
        name = str(project_json['name'])
        desc = str(project_json['description'])
        comments = str(project_json['comments'])

        # then formatting to ensure db compatibility  
        db_obj = { 'name': name, 'description': desc, 'comments': comments }
        
        # connecting to db with relevant collection - posts
        project_registerer = db_connect('project_collection')
        
        # registering new post
        print("registration attempt of project:", db_obj)
        try:
            project_registerer.insert_one(db_obj)
            return "Success: registration"
        except:
            print("Error: db communication")
            return "Error: db communication", 404
    #------------------------------#


#-------------------------------------------------#
# projects route with method=GET
@app.route("/projects", methods=['GET'])
def retrieve_projects():
        
    # a list to append all posts to and then jsonify
    all_projects = []

    try:
        # connecting to db with relevant collection - posts
        project_retriever = db_connect('project_collection')
        
        # querying all of the posts db
        projects_query = project_retriever.find({})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # appending them to the list stated above
    for project in projects_query:
        # print(project)
        
        # looking for objectid and making it str to jsonify later on
        object_id = project['_id']
        project['_id'] = str(object_id)
        
        
        all_projects.append(project)
    
    

    try:
        print("trying to return the queries")
        return jsonify(all_projects)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#


#-------------------------------------------------#
# projects route with method=DELETE
@app.route("/projects/<string:id>", methods=['DELETE'])
def remove_project(id):
    from bson.objectid import ObjectId        
    try:
        # connecting to db with relevant collection - posts
        project_delete = db_connect('project_collection')
        
        # deleting the relevant object
        project_delete.delete_one({'_id': ObjectId(id)})
    except:
        print("Error: db communication")
        return "Error: db communication", 404

    # returning answer
    try:
        print(f'deleted project with id {id}')
        return jsonify(id)
    except:
        print("Error: problem jsonifing or returning")
        return "Error: problem jsonifing or returning", 404
#------------------------------#

#-------------------------------------------------#
# projects route with method=PUT
@app.route("/projects/<string:id>", methods=['PUT'])
def update_project(id):
    from bson.objectid import ObjectId
    #------------------------------#
    # json related
    try:     
        # taking the json file sent
        project_json = request.get_json()
        return jsonify(project_json)
        # making a list of keys and values for validation check
        # reg_key_list = list( user_json.keys() )
        project_value_list = list( project_json.values() )
        
    # json validations
    except:
        print("Error: json communication problem")
        return  "Error: json communication problem", 404
    
    #------------------------------#
    # sent info validation
    for project_value in project_value_list:
        # checking no field is empty
        if project_value == "" :
            print("empty field provided")
            return "Error: empty field provided", 404  
        # checking no field is just spaces
        elif len(project_value) == project_value.count(" "):
            print("one of fields provided is just spaces")
            return "Error: a field provided is just spaces", 404

    #------------------------------#
        # taking the info and putting it in DB
        # first ensuring strings
        comments = str(project_json['comments'])
        
        query = {'_id': ObjectId(id)}
        # then formatting to ensure db compatibility  
        update = { "$set": { 'comments': comments } }
        
        # connecting to db with relevant collection - posts
        project_registerer = db_connect('project_collection')
        
        # registering new post
        print("update attempt of project with id: ", str(id) )
        try:
            project_registerer.update_one(query, update)
            return "Success: update"
        except:
            print("Error: db communication")
            return "Error: db communication", 404
    #------------------------------#


#-------------------------------------------------#
# RUNNING THE APP # 
if __name__ == "__main__":
    # finding relevent configs before running
    host = get_config("host")
    port = get_config("port")
    debug_state = get_config("app_debug_state")
    app.run(host=host, port=port, debug=debug_state)
