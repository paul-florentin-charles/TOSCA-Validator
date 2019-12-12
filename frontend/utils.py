import os
import json
import random
import zipfile
import tarfile

# Chars used to name temporary created files
CHRS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def dict_to_json(d):
    '''Transforms a Python dictionary into a string representing a json element'''
    return json.dumps(d, separators=(',', ':'))

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


def verify_tar(tarf) :
    '''Verifies that the tar archive can be trusted'''
    for tarinfo in tarf :
        if tarinfo.name.startswith('~') or tarinfo.name.startswith('/') or '..' in tarinfo.name :
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
