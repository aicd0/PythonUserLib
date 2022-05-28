__package__ = 'user.fm'

import argparse
import user.utils.print as print_utils
from .exception import FmException
from .repo import Repository

def init(repo_path):
    repo = Repository(repo_path)
    repo.init()

def commit(repo_path):
    repo = Repository(repo_path)
    repo.commit()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str)
    parser.add_argument('op', type=str)
    args = parser.parse_args()
    return args.dir, args.op

def main():
    repo_path, op = parse_args()
    op = op.lower()

    try:
        if op == 'init':
            init(repo_path)
        elif op == 'commit':
            commit(repo_path)
        else:
            raise FmException("Unknown command '" + op + "'.")
    except FmException as e:
        print_utils.put(str(e))

if __name__ == '__main__':
    main()