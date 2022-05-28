import os
from user.utils.platform import is_linux

def to_path(path: str) -> str:
    path = path.replace('\\', '/')
    items = path.split('/')
    items = [i.strip() for i in items]
    if any([len(i) == 0 for i in items[1 if is_linux() else 0 : -1]]):
        raise ValueError('Invalid path')
    path = '/'.join(items)
    path = os.path.abspath(path)
    path = path.replace('\\', '/')
    return path

def to_file_path(path: str) -> str:
    path = to_path(path)
    if len(path) == 0:
        raise ValueError()
    if path[-1] == '/':
        raise ValueError()
    return path

def to_file_name(path: str) -> str:
    path = to_file_path(path)
    i = path.rfind('/')
    if i == -1:
        return path
    return path[i + 1:]

def to_display_name(path: str) -> str:
    filename = to_file_name(path)
    i = filename.rfind('.')
    if i == -1:
        return filename
    return filename[:i]

def to_parent_path(path: str) -> str:
    path = to_path(path)
    if len(path) == 0:
        return path
    if path[-1] == '/':
        path = path[:-1]
    i = path.rfind('/')
    if i == -1:
        return ''
    return path[:i + 1]

def to_folder_path(path: str) -> str:
    path = to_path(path)
    if len(path) != 0 and path[-1] != '/':
        path += '/'
    return path
    
def dict_to_str(x: dict) -> str:
    return ', '.join([str(k) + '=' + str(v) for k, v in x.items()])