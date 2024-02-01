import os


def dir_path(*path):
    return os.path.normpath(os.path.join(*path))


def file_path(*path):
    return os.path.normpath(os.path.join(*path))
