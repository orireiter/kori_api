import flask
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import configparser, os
from os import walk


#------------------------------------------------------------------#
# PARSER related

# creating a parser for a config file for better use later on
# it takes as an argument to parameter youre looking for
# and retrieves the variable in it
def get_config(parameter):
    parser = configparser.RawConfigParser()
    config_path = r".\api.config"
    parser.read(config_path)
    return parser.get('file_api-config', str(parameter))


# ----------------------------------------------------------------#
# file serving related
# defining the root folder to allow looking
# just into it
root1 = get_config("base_path")

#------------------------------------------------------------------#
# FLASK related

#-------------------------------------------------#
# creating app
app = Flask(__name__)
# allowing different origins to communicate with it
cors = CORS(app, resources={r"/*": {"origins": "*"}})

#-------------------------------------------------#
# route to VIEW docs and folders in the shared folder
@app.route("/docs_view/", methods=["GET"])
@app.route('/docs_view/<path:path>', methods=["GET"])
def get_dir(**kwargs): 
    # using **kwargs allows having any argument with any name
    # also allows having no arguments (needed to access most
    # exterior folder)
    # creating a list of the args given (only 1 or 0 in this case)
    # to use them later on as path

    relative_path =  list(kwargs.items())
    
    # trying to make a full path iwth the root and relative
    # if no arg was given it will noly use the root
    try:
        full_path = root1 + relative_path[0][1]
    except:
        full_path = root1

    # creating a dict to put in it the folders and files in this
    # WHOLE path, will get rid of sub files and sub folders later
    pre_container = { "folders": [], "files": []}

    # acquiring the files and folders and putting them in the dict
    for root, dirs, files in walk(full_path, topdown=True):
        pre_container["folders"].append(dirs)

        # taking files with full path and only keeping the relative
        files1 = []
        for name in files:
            full_name = os.path.join(root, name)
            full_name = full_name.replace(root1,"")
            files1.append(full_name)
        
        pre_container["files"].append(files1)
        
    # assigning an error if you tried to reach a none existent
    # directory
    if len(pre_container["folders"]) == 0 and len(pre_container["files"]) == 0:
        return "Error: couldnt find that path", 404
    
    # making the dictionary with only the files/folders specifically in it
    post_container = {"folders": pre_container["folders"][0], 
                      "files": pre_container["files"][0]} 
    return jsonify(post_container)

#-------------------------------------------------#
# route to Download docs and folders in the shared folder
@app.route("/docs_down/<path:path>", methods=["GET"])
def download(path):
    # breaking down the path given to filename
    # and relative path if needed
    try:
        extra_path = path.split("/")
        filename = extra_path[-1]
        extra_path.pop(-1)
        fullpath = root1
    
        for extra in extra_path:
            fullpath = fullpath + extra + "/"    
    except:
        fullpath = root1
        filename = path

    # returning the file if it's found 
    return send_from_directory(fullpath, filename=filename, as_attachment=True)

#-------------------------------------------------#



#-------------------------------------------------#
# RUNNING THE APP # 
if __name__ == "__main__":
    # finding relevent configs before running
    host = get_config("host")
    port = get_config("port")
    debug_state = get_config("app_debug_state")
    app.run(host=host, port=port, debug=debug_state)
