import os
import user.utils.string_utils as string_utils

def mktree(path):
    path = string_utils.to_folder_path(path)
    if len(path) == 0:
        return
    folders = path.split('/')[0 : -1]
    path = ''
    for f in folders:
        path += f + '/'
        if not os.path.exists(path):
            os.mkdir(path)
            