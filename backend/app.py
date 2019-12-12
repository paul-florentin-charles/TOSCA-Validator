from flask import Flask, render_template, request

from validator import *
from utils import *
from answer_format import *

import config as cfg

app = Flask(__name__)

#############
# INTERFACE #
#############
'''
Interface functions (if the file is used as a library)
'''

def validate_path(file_path) :
    return dict_to_json(validation_from_path(file_path))

def validate_str(s) :
    return dict_to_json(validation_from_yaml_str(s))

def validate_folder(dir_path) :
    return dict_to_json(validation_from_folder(dir_path))

def validate_archive(archive_path) :
    return dict_to_json(validation_from_archive(archive_path))


#############
# ENDPOINTS #
#############


@app.route(cfg.API_ROUTE + cfg.TEXT_ENDPOINT, methods=['POST'])
def validation_text():
    if (request.data):
        content = request.data.decode('UTF-8')

        try :
            cd = json.loads(content)
            data = bytes(cd["data"], "UTF-8").decode("unicode_escape")
            res = validate_str(data)
            return res
        except Exception as e:
            print(e)
            return error_generic_file()
    else:
        return error_empty_or_bad_request()


@app.route(cfg.API_ROUTE + cfg.FILE_ENDPOINT, methods=['POST'])
def validation_file():
    if (request.files):
        fileStorage = request.files['file']
        file_name = rfname_generator(cfg.TMP_DIR, suffix=fileStorage.filename)
        fileStorage.save(file_name)

        try:
            res = validate_path(file_name)
        except Exception as e:
            print(e)
            os.remove(file_name)
            return error_generic_file()
        os.remove(file_name)
        return res

    else:
        return error_empty_or_bad_request()

@app.route(cfg.API_ROUTE + cfg.ARCHIVE_ENDPOINT, methods=['POST'])
def validation_archive():
    if (request.files):
        fileStorage = request.files['file']

        archive_name = rfname_generator(cfg.TMP_DIR, suffix=fileStorage.filename)
        fileStorage.save(archive_name)

        try:
            res = validate_archive(archive_name)
        except Exception as e:
            print(e)
            os.remove(archive_name)
            return error_generic_archive()
        os.remove(archive_name)
        return res
    else:
        return error_empty_or_bad_request()


if __name__ == "__main__" :
    app.run(debug=cfg.DEBUG, port=cfg.PORT)
