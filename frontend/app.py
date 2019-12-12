from flask import Flask, render_template, request
import requests
import json, os
from utils import *
from shutil import rmtree
from config import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/validate/text', methods=['POST'])
def validation_text():
    if (request.data):
        data = request.data
        try :
            res = requests.post("http://" + str(ADDRESS) + ":" + str(PORT) + "/api/validate/text", data=data)
            return res.text
        except Exception as e:
            return "Invalid text input"
    elif (request.files):
        return "Not a text"
    else:
        return "Empty request"

@app.route('/api/validate/file', methods=['POST'])
def validation_file():
    if (request.files):
        fileStorage = request.files['file']
        file_name = rstr_generator() + fileStorage.filename
        while os.path.exists(file_name) :
            file_name = rstr_generator() + fileStorage.filename
        try:
            fileStorage.save(file_name)
            file = {'file': open(file_name, 'rb')}
            res = requests.post("http://" + str(ADDRESS) + ":" + str(PORT) + "/api/validate/file", files=file)
            os.remove(file_name)
            return res.text
        except Exception as e:
            return "Invalid file input"
    elif (request.data):
        return "Not a file"
    else:
        return "Empty request"

@app.route('/api/validate/archive', methods=['POST'])
def validation_archive():
    if (request.files):
        fileStorage = request.files['file']
        filename = fileStorage.filename
        name = filename[:filename.index('.')]
        extension = filename[filename.index('.'):]
        dir_path = rdir_generator(TMP_DIR)
        archive_path = rfname_generator(TMP_DIR, name , extension)
        try:
            fileStorage.save(archive_path)
            files = {'file': open(archive_path, 'rb')}
            res = requests.post("http://" + str(ADDRESS) + ":" + str(PORT) + "/api/validate/archive", files=files)
            answer = res.text
            uncompress_archive(dir_path, archive_path)
            names = []
            contents = []
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    path = root + '/' + file
                    with open(path, 'r') as content:
                        path = path[path.index(name):]
                        names.append(path)
                        contents.append(content.read())
            answer = json.loads(answer)
            for f in answer['files']:
                if f['name'] in names:
                    f['content'] = contents[names.index(f['name'])]
            answer = dict_to_json(answer)
            rmtree(dir_path)
            os.remove(archive_path)
            return answer
        except Exception as e:
            return "Invalid archive input" + str(e)
    elif (request.data):
        return "Not an archive"
    else:
        return "Empty request"

if __name__ == "__main__":
    app.run(host=HOST, port=APP_PORT, debug=DEBUG)
