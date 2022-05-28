import hashlib
import json
import numpy as np
import os
import shutil
import user.utils.fileio as fileio
import user.utils.string_utils as string_utils
from .exception import FmException

FM_FOLDER = '.fm'

class FileInfo:
    def __init__(self, path: str) -> None:
        self.path = path
        self.size = None
        self.md5 = None

class RepositoryData:
    def __init__(self) -> None:
        self.files: list[FileInfo] = []

    def save(self, database_file):
        np.savez(database_file,
            files=np.array(self.files, dtype=object)
        )

    def load(self, database_file):
        database = np.load(database_file, allow_pickle=True)
        self.files = database['files'].tolist()

    def update(self, root_directory):
        def update_files(full_path, rel_path, files: list):
            for item in os.listdir(full_path):
                current_full_path = full_path + item
                current_rel_path = rel_path + item
                if os.path.isdir(current_full_path):
                    if item == FM_FOLDER:
                        continue
                    update_files(current_full_path + '/', current_rel_path + '/', files)
                else:
                    fileinfo = FileInfo(current_rel_path)
                    files.append(fileinfo)

        self.files.clear()
        update_files(root_directory, '', self.files)

class RepositoryDelta:
    def __init__(self) -> None:
        self.added_files = []
        self.removed_files = []

    def save(self, delta_file):
        np.savez(delta_file,
            added_files=np.array(self.added_files, dtype=object),
            removed_files=np.array(self.removed_files, dtype=object),
        )

    def load(self, delta_file):
        delta = np.load(delta_file, allow_pickle=True)
        self.added_files = delta['added_files'].tolist()
        self.removed_files = delta['removed_files'].tolist()

    def log(self, detailed=False) -> str:
        added_count = len(self.added_files)
        removed_count = len(self.removed_files)
        result = ''
        if detailed:
            def file2str(f: FileInfo):
                return f.path + ' | ' + str(f.size) + ' | ' + f.md5
            sections = []
            if removed_count > 0:
                section = ''
                section += '%d files removed:\n' % removed_count
                section += '\n'.join(file2str(f) for f in self.removed_files)
                sections.append(section)
            if added_count > 0:
                section = ''
                section += '%d files added:\n' % added_count
                section += '\n'.join(file2str(f) for f in self.added_files)
                sections.append(section)
            result += '\n'.join(sections)
        else:
            result += '%d files added and %d files removed.' % (added_count, removed_count)
        return result

    def export(self, dst_dir, src_dir):
        dst_dir = string_utils.to_folder_path(dst_dir)
        src_dir = string_utils.to_folder_path(src_dir)
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)
        for f in self.added_files:
            src_path = string_utils.to_file_path(src_dir + f.path)
            dst_path = string_utils.to_file_path(dst_dir + f.path)
            dst_folder = string_utils.to_parent_path(dst_path)
            fileio.mktree(dst_folder)
            os.link(src_path, dst_path)

class Repository:
    def __init__(self, repo_dir) -> None:
        self.repo_dir = string_utils.to_folder_path(repo_dir)
        self.fm_dir = string_utils.to_folder_path(self.repo_dir + FM_FOLDER)
        self.delta_dir = string_utils.to_folder_path(self.fm_dir + 'delta')
        self.repo_file = self.fm_dir + 'repo.txt'
        self.data_file = self.fm_dir + 'data.npz'

        if not os.path.isdir(self.repo_dir):
            raise FmException("'" + self.repo_dir + "' not found.")

        self.version = 0
        self.data = RepositoryData()

    def save(self):
        # Repo file.
        with open(self.repo_file, 'w') as f:
            json.dump({
                'version': self.version,
            }, f)

        # Data file.
        self.data.save(self.data_file)
    
    def load(self):
        # Repo file.
        with open(self.repo_file, 'r') as f:
            obj = json.load(f)
        self.version = obj['version']

        # Data file.
        self.data.load(self.data_file)

    def init(self):
        if os.path.exists(self.fm_dir):
            raise FmException('Repository already exists.')

        os.mkdir(self.fm_dir)
        os.mkdir(self.delta_dir)
        self.save()

    def commit(self):
        if not os.path.exists(self.fm_dir):
            raise FmException("'" + self.repo_dir + "' is not a repository.")

        self.load()
        old_repo_data = self.data

        new_repo_data = RepositoryData()
        new_repo_data.update(self.repo_dir)
        
        old_files = old_repo_data.files
        new_files = new_repo_data.files

        old_kept_files = old_files
        new_kept_files = new_files
        added_files = []
        removed_files = []

        def search(key):
            nonlocal old_kept_files, new_kept_files
            old_map = {key(f): f for f in old_kept_files}
            new_map = {key(f): f for f in new_kept_files}
            old_keys = set(old_map.keys())
            new_keys = set(new_map.keys())
            removed_keys = old_keys.difference(new_keys)
            added_keys = new_keys.difference(old_keys)
            kept_keys = old_keys.intersection(new_keys)
            added_files.extend([new_map[k] for k in added_keys])
            removed_files.extend([old_map[k] for k in removed_keys])
            old_kept_files = [old_map[k] for k in kept_keys]
            new_kept_files = [new_map[k] for k in kept_keys]

        # Search by file path.
        search(lambda f: f.path)

        # Search by file size.
        for f in new_kept_files + added_files:
            f.size = os.path.getsize(self.repo_dir + f.path)
        search(lambda f: str(f.size) + '|' + f.path)

        # Search by MD5.
        for f in new_kept_files + added_files:
            with open(self.repo_dir + f.path, 'rb') as fp:
                f.md5 = hashlib.md5(fp.read()).hexdigest()
        search(lambda f: f.md5 + '|' + f.path)

        # Exit if no changes.
        if len(added_files) + len(removed_files) == 0:
            print('No changes detected.')
            return

        # Save repository.
        self.version += 1
        self.data = new_repo_data
        self.save()

        # Create delta file.
        delta_file = self.delta_dir + '%d.npz' % self.version
        repo_delta = RepositoryDelta()
        repo_delta.added_files = added_files
        repo_delta.removed_files = removed_files
        repo_delta.save(delta_file)

        print(repo_delta.log(detailed=False))
        with open(self.fm_dir + 'changes.txt', 'w') as f:
            f.write(repo_delta.log(detailed=True))
        repo_delta.export(self.fm_dir + 'export', self.repo_dir)