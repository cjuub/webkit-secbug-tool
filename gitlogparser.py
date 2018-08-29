import re
import subprocess

# crappy url regex, but works for now
_URL_PATTERN = re.compile('https?:\/\/[^ ]*')
# _URL_PATTERN = re.compile('https?:\/\/(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?!\. )[^ \n]*')


class GitLogParser(object):
    def __init__(self, git_dir: str, max_date: str):
        self.git_dir = git_dir
        self.max_date = max_date

    def parse(self):
        cmd = ['git', 'log', '--oneline', '--pretty=format:"%H %s"']
        shortlog = subprocess.check_output(cmd, cwd=self.git_dir).decode('utf-8')

        res = list()
        for line in shortlog.split('\n'):
            commit_data = dict()
            commit_data['id'] = line[1:41]
            commit_data['msg'] = line[42:-1]
            self._find_urls(commit_data['msg'], commit_data)
            res.append(commit_data)

        return res

    def _find_urls(self, line: str, commit_data: dict):
        commit_data['urls'] = list()

        match = _URL_PATTERN.search(line)
        while match:
            commit_data['urls'].append(match.group(0))
            match = _URL_PATTERN.search(line, match.end(0))

