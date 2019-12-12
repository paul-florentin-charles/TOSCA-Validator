import os
import re
import random
import json
import zipfile
import tarfile

# Chars used to generate random strings, file names, and directories
CHRS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# Chars which are valid to use to make indentation
IND_CHRS = [" ", "\t"]

# Chars considered as empty (no meaning but separation/indentation)
EMPTY_CHRS = IND_CHRS + ["\n"]

def rstr_generator(size=10, chars = CHRS):
    '''Generates a random string of size 'size' containing chars from 'chars\''''
    return ''.join(random.choice(chars) for _ in range(size))

def rdir_generator(parent_dir) :
    if not os.path.exists(parent_dir) :
        os.makedirs(parent_dir)

    d = parent_dir + '/' + rstr_generator()
    while os.path.exists(d) :
        d = parent_dir + '/' + rstr_generator()

    os.makedirs(d)
    return d

def rfname_generator(parent_dir, prefix='', suffix='') :
    if not os.path.exists(parent_dir) :
        os.makedirs(parent_dir)

    fname = parent_dir + '/' + prefix + rstr_generator() + suffix
    while os.path.exists(fname) :
        fname = parent_dir + '/' + prefix + rstr_generator() + suffix

    return fname


def is_empty(s) :
    '''Checks if the string s contains only chars from EMPTY_CHARS'''
    for c in s :
        if c not in EMPTY_CHRS :
            return False
    return True

def dict_to_json(d):
    '''Transforms a Python dictionary into a string representing a json element'''
    return json.dumps(d, separators=(',', ':'))


def node_list(node, req) :
    '''Puts node and req into an appropriate node list (when TOSCA validation fails in sommelier)'''
    return [("topology_template", False),\
             ("node_templates", False),\
             (node, False),\
             ("requirements", False),\
             (req, True)]

def find_node_line(nodes, path):
    '''Inputs :
- nodes : a list of (string, bool) pairs.
          The string is the name of the node.
          The boolean is True if the node is in a list
- path : the path of the file in which to search the node line

Output :
The line of the last node

Example usage :

input : [("A", False), ("b", True), ("flt", False)] on the following file
1  A:
2    -a: "A"
3    -b:
4      str: "value"
5      flt: 1.3
6    -c: 4

Will return 5'''
    l = 0
    lines = []
    res = None
    with open(path, "r") as f :
        lines = f.readlines()

    for nod in nodes :
        node, in_list = nod
        ind = ""
        len_ind = 0
        if l == len(lines) :
            return None
        line = lines[l]

        while (is_empty(line)) :
            l += 1
            if l == len(lines) :
                return None
            line = lines[l]

        if l != 0 :
            for c in line :
                if c in IND_CHRS :
                    ind += c
                    len_ind += 1
                else :
                    break
        dash_re = ""
        if in_list :
            dash_re = "- *"
        rexp = re.compile("\A" + dash_re + node + " *:.*\n\Z")
        while True :
            if l == len(lines) :
                return None
            line = lines[l]
            l += 1
            if line.startswith(ind) :
                if re.search(rexp, line[len_ind:]) != None :
                    res = l
                    break
            elif is_empty(line) :
                continue
            else :
                return None

    return res

def yaml_and_dirs(dirpath) :
    contents = os.listdir(dirpath)
    f = []
    d = []
    for c in contents :
        if dirpath != '.' :
            path = dirpath + '/' + c
        else :
            path = c
        if os.path.isfile(path) :
            if c.lower().endswith('.yaml') :
                f.append(path)
        else :
            d.append(path)
    return f,d


def find_yaml_files(dirpath) :
    cwd = os.getcwd()
    os.chdir(dirpath)
    files, folders = yaml_and_dirs('.')
    while len(folders) != 0 :
        di = folders[0]
        folders = folders[1:]
        f,d = yaml_and_dirs(di)
        files += [ i for i in f]
        folders += [ i for i in d]
    os.chdir(cwd)
    return files


def verify_tar(tarf) :
    '''Verifies that the tar archive can be trusted'''
    for tarinfo in tarf :
        if tarinfo.name.startswith('~') or tarinfo.name.startswith('/') or ('..' in tarinfo.name) :
            return False
    return True

class HarmfulTarException(Exception) :
    pass

def uncompress_archive(dir_path, archive_path) :
    '''Uncompresses the archive located at archive_path into the directory dir_path
    Returns True if the archive type is supported and was successfully uncompressed. Returns False if the archive type is not supported'''
    if archive_path.endswith('.zip') :
        zipf = zipfile.ZipFile(archive_path, 'r')
        zipf.extractall(dir_path)
        zipf.close()

    elif archive_path.endswith('.tar.gz') :
        with tarfile.open(archive_path, 'r:gz') as tarf :
            if not verify_tar(tarf) :
                raise HarmfulTarException
            tarf.extractall(dir_path)

    elif archive_path.endswith('.tar.bz2') :
        with tarfile.open(archive_path, 'r:bz2') as tarf :
            if not verify_tar(tarf) :
                raise HarmfulTarException
            tarf.extractall(dir_path)

    elif archive_path.endswith('.tar') :
        with tarfile.open(archive_path, 'r') as tarf :
            if not verify_tar(tarf) :
                raise HarmfulTarException
            tarf.extractall(dir_path)
    else :
        return False
    return True


KEYWORD_CHRS = "[A-Z]|[a-z]|\\.|_"
NOT_KEYWORD_CHAR_AFTER = "(?!" + KEYWORD_CHRS + ")"
NOT_KEYWORD_CHAR_BEFORE = "(?<!" + KEYWORD_CHRS + ")"
def try_find_lines(keywords, path) :
    if keywords == [] :
        return []
        
    with open(path, 'r') as f :
        lines = f.readlines()

    res = []

    rexps = []
    for k in keywords :
        rex = NOT_KEYWORD_CHAR_BEFORE + k + NOT_KEYWORD_CHAR_AFTER
        rexps.append(re.compile(rex))

    res = []
    for l in range(len(lines)) :
        flag = True
        for rexp in rexps :
            if re.search(rexp, lines[l]) == None :
                flag = False
                break
        if flag :
            res.append(l+1)

    return res
