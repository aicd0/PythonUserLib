from .repo import Repository

def init(repo_path):
    repo = Repository(repo_path)
    repo.init()

def commit(repo_path):
    repo = Repository(repo_path)
    repo.commit()