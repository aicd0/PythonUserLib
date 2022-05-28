import argparse
import fm

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
            fm.init(repo_path)
        elif op == 'commit':
            fm.commit(repo_path)
        else:
            raise fm.FmException("Unknown command '" + op + "'.")
    except fm.FmException as e:
        print(str(e))

if __name__ == '__main__':
    main()