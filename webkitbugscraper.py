import json
import requests
import os


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
        urls = commit['urls']
        added = False
        if len(urls) > 0:
            last_url = urls[len(urls) - 1]
            if self._is_security_bug(last_url):
                self._add(commit, True)
                added = True

        if not added:
            self._add(commit, False)

        return self.get(commit['id'])

    def _is_security_bug(self, webkit_url: str):
        res = requests.get(webkit_url)
        return "You are not authorized to access bug" in res.text

    def _add(self, commit: dict, classified: bool):
        self._cache[commit['id']] = dict()
        self._cache[commit['id']]['classified'] = classified 

        with open(self._cache_path, 'w') as fp:
            json.dump(self._cache, fp)

