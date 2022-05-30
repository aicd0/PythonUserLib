__package__ = 'user.fm'

import argparse
import user.utils.print as print_utils
from .exception import FmException
from .repo import Repository

def init(repo_path):
    repo = Repository(repo_path)
    repo.init()

def commit(repo_path, **kwargs):
    repo = Repository(repo_path, retreat=True)
    repo.commit(**kwargs)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='path to your repository')
    parser.add_argument('op', type=str, help='operation to perform')
    parser.add_argument('-m', '--md5', action='store_true', help='enable MD5 check')
    args = parser.parse_args()
    return args.dir, args.op, args.md5

def main():
    repo_path, op, md5 = parse_args()
    op = op.lower()

    try:
        if op == 'init':
            init(repo_path)
        elif op == 'commit':
            commit(repo_path, enable_md5=md5)
        else:
            raise FmException("Unknown command '" + op + "'.")
    except FmException as e:
        print_utils.put(str(e))

if __name__ == '__main__':
    main()