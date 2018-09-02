import subprocess

from webkit_commit_generator import WebKitCommitGenerator


# TODO broken 
class GitLogParser(WebKitCommitGenerator):
    def __init__(self, git_dir: str, max_date: str):
        super().__init__(max_date)
        self.git_dir = git_dir

    def __iter__(self):
        cmd = ['git', 'log', '--oneline', '--pretty=format:"%H %s"', '--since', self._max_date]
        shortlog = subprocess.check_output(cmd, cwd=self.git_dir).decode('utf-8')

        for line in shortlog.split('\n'):
            commit_data = dict()
            commit_data['id'] = line[1:41]
            commit_data['title'] = None
            commit_data['msg'] = line[42:-1]
            commit_data['parent_id'] = None


            yield commit_data

