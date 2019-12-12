from utils import *
from yaml.error import YAMLError


#################
#    ANSWERS    #
#################
'''
Functions formating the answers returned by the API
'''


def answer_valid() :
    return {'valid':True}

def answer_with_error_code(code) :
    return {'valid':False, 'errors':[{'code':code}]}

def answer_sommelier(validation, path) :
    '''Given a validation from Sommelier and the path of the validated file, returns a ditionary containing the result of the validation'''
    res = {'valid':True, 'errors':[]}

    for nodeName in validation:
        reqs = validation.get(nodeName).keys()
        for req in reqs:
            infoList = validation.get(nodeName).get(req)
            for info in infoList:
                res['valid'] = False
                res['errors'].append(err_dict(nodeName, req, info, path))

    if res['valid'] :
        return answer_valid()
    return res

def answer_archive(vals) :
    '''Answer for an archive validation request. Assumes that vals contains a list of tuples (file_name, result) where result is the object returned by answer_sommelier on the file.'''
    valid = True
    results = []

    for i in vals :
        name, result = i
        results.append({'name':name, 'result':result})
        if not result['valid'] :
            valid = False
    if valid :
        return answer_valid()
    return {'valid':False, 'errors':[], 'files':results}



################
#    ERRORS    #
################
'''
Functions formating the errors.
'''


# Error classes
ERR_INTERNAL = 0.0
ERR_YAML = 1.0
ERR_TOSCAPARSER = 2.0
ERR_SOMMELIER = 3.0

ERR_REQUEST = ERR_INTERNAL + 0.1
ERR_FILE = ERR_INTERNAL + 0.2
ERR_ARCHIVE = ERR_INTERNAL + 0.3

def err_dict(node, req, info, path) :
    '''Returns a formated dictionary with the error (sommelier errors)'''
    err = info[0]
    details = info[1:]
    lines = [find_node_line(node_list(node,req), path)]
    err = ERR_SOMMELIER + info[0]/10.0
    return {'code':err, 'lines':lines, 'node':node, 'req':req, 'details':details}


NO_LINE_ERRORS = ["MissingRequiredFieldError", "InvalidSchemaError", "ValidationError", "URLException", "InvalidGroupTargetException"]
def parse_validation_err(e, path) :
    '''Given a ValidationError (from tosca-parser), gets its sub-errors'''

    str_e = str(e)
    lines = str_e.splitlines()
    errors = []
    for l in lines :
        if (not l.startswith("\t\t")) and l.startswith("\t") :
            l = l[1:]
            error_type = ""
            details = ""

            flag=True
            for c in l :
                if flag :
                    if c == ':' :
                        flag = False
                    else :
                        error_type += c
                else :
                    details += c

            details = details[1:]
            error = {'code': ERR_TOSCAPARSER, 'lines':[], 'type':error_type, 'details':details}
            spl = details.replace('".', '"').split(' ')
            find_lines = True
            keywords = [w[1:-1] for w in spl if (w.startswith('"') and w.endswith('"'))]

            if error_type == "TypeMismatchError":
                keywords = [spl[0]]
            elif error_type == "InvalidTemplateVersion":
                keywords = keywords[:1]


            if find_lines and error_type in NO_LINE_ERRORS :
                find_lines = False

            if find_lines :
                error['lines'] += try_find_lines(keywords, path)

            errors.append(error)
    return errors

def error_yaml(e) :
    res = {'valid':False, 'errors':[{'code':ERR_YAML, 'lines':[]}]}

    if type(e) != AttributeError :
        for l in str(e).replace(',', '').splitlines() :
            words = l.split(' ')
            for i in range(len(words)) :
                if words[i] == "line" :
                    res['errors'][0]['lines'].append(int(words[i+1]))

    return res

def error_validation(e, path) :
    return {'valid':False, 'errors':parse_validation_err(e, path)}

def error_generic(e) :
    print(e)
    return answer_with_error_code(ERR_INTERNAL)

def error_generic_file() :
    return answer_with_error_code(ERR_FILE)

def error_empty_or_bad_request() :
    return answer_with_error_code(ERR_REQUEST)

def error_generic_archive() :
    return answer_with_error_code(ERR_ARCHIVE)

def error_no_file_in_archive() :
    return answer_with_error_code(ERR_ARCHIVE+0.01)

def error_harmful_tar() :
    return answer_with_error_code(ERR_ARCHIVE+0.02)

def error_unsupported_archive_type() :
    return answer_with_error_code(ERR_ARCHIVE+0.03)
