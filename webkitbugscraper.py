import json
import re
import requests
import os

from typing import List

# crappy url regex, but works for now
# _URL_PATTERN = re.compile('https?:\/\/[^ ]*')
_URL_PATTERN = re.compile('https?:\/\/(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?!\. )[^ \n]*')


class WebKitBugScraper(object):
    def __init__(self, cache_path):
        self._cache_path = cache_path

        if os.path.exists(self._cache_path):
            with open(self._cache_path, 'r') as fp:
                self._cache = json.load(fp)
        else:
            self._cache = dict()

    def get(self, commit_id: str):
        try:
            return self._cache[commit_id]
        except:
            return None

    def scrape(self, commit): 
        urls = self._find_urls(commit['msg'])
        added = False
        if len(urls) > 0:
            first_url = urls[0]
            if self._is_security_bug(first_url):
                self._add(commit, True)
                added = True

        if not added:
            self._add(commit, False)

        return self.get(commit['id'])

    def _is_security_bug(self, webkit_url: str):
        print(webkit_url)
        res = requests.get(webkit_url)
        return "You are not authorized to access bug" in res.text

    def _add(self, commit: dict, classified: bool):
        self._cache[commit['id']] = dict()
        self._cache[commit['id']]['id'] = commit['id'] 
        self._cache[commit['id']]['parent_id'] = commit['parent_id'] 
        self._cache[commit['id']]['title'] = commit['title'] 
        self._cache[commit['id']]['classified'] = classified 

        with open(self._cache_path, 'w') as fp:
            json.dump(self._cache, fp)

    def _find_urls(self, line: str) -> List[str]:
        urls = []

        match = _URL_PATTERN.search(line)
        while match:
            if 'bugs.webkit.org' in match.group(0):
                urls.append(match.group(0))
            match = _URL_PATTERN.search(line, match.end(0))

        return urls

