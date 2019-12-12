import config as cfg

import topologyvalidator as sommelier

from utils import *
from answer_format import *

from yaml.error import YAMLError
from toscaparser.common.exception import ValidationError

import shutil



def validation_from_path(input_path) :
    '''Given a path from a file to validate, returns the answer of the validation'''
    v = sommelier.TopologyValidator()
    try :
        validation = v.validate(input_path)
    except (YAMLError, AttributeError) as e:
        return error_yaml(e)
    except ValidationError as e:
        return error_validation(e, input_path)
    except Exception as e:
        return error_generic(e)

    return answer_sommelier(validation, input_path)


def validation_from_yaml_str(s) :
    '''Validates the YAML (TOSCA) file contained into the string 's', and returns the response.'''

    path = rfname_generator(cfg.TMP_DIR, suffix='.yaml')

    with open(path, 'w') as f :
        f.write(s)
        
    try :
        res = validation_from_path(path)
    except Exception as e :
        os.remove(path)
        raise e
    os.remove(path)
    return res

def validation_from_folder(dirpath) :
    '''Validates all YAML files found in the folder.'''

    f = find_yaml_files(dirpath)

    if len(f) == 0 :
        return error_no_file_in_archive()

    vals = [(i, validation_from_path(dirpath + '/' + i)) for i in f]

    return answer_archive(vals)


def validation_from_archive(path) :
    '''Takes an archive (.zip, .tar.gz, .tar.bz2, or .tar) and validates all YAML files found'''

    d = rdir_generator(cfg.TMP_DIR)
    
    try :
        res = uncompress_archive(d, path)
        if not res :
           shutil.rmtree(d)
           return error_unsupported_archive_type()

    except HarmfulTarException :
        shutil.rmtree(d)
        return error_harmful_tar()

    except Exception :
        shutil.rmtree(d)
        return error_generic_archive()


    res = validation_from_folder(d)
    shutil.rmtree(d)
    return res
