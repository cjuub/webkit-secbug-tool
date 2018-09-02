import requests

from webkit_commit_generator import WebKitCommitGenerator

COMMIT_STR = 'commit</td><td class="sha1">'
PARENT_COMMIT_STR = 'parent: <a href="/?p=WebKit.git;a=commit;h='
TITLE_STR = '<a class="title" href="/?p=WebKit.git;a=commitdiff;h='
MSG_STR = '<div class="page_body">'

ID_LEN = 40


class WebKitCommitScraper(WebKitCommitGenerator):
    def __init__(self, git_url: str, scraped_bugs: dict, max_date: str):
        super().__init__(max_date)
        self._git_url = git_url
        self._scraped_bugs = scraped_bugs

    def __iter__(self):
        # Find first commit ID
        res = requests.get(self._git_url + 'HEAD')
        commit_id_index = res.text.find(COMMIT_STR) + len(COMMIT_STR)
        next_commit_id = res.text[commit_id_index:commit_id_index + ID_LEN]

        while next_commit_id:
            commit_data = dict()

            res = requests.get(self._git_url + next_commit_id)

            commit_id_index = res.text.find(COMMIT_STR) + len(COMMIT_STR)
            commit_data['id'] = res.text[commit_id_index:commit_id_index + ID_LEN]

            next_commit_id_index = res.text.find(PARENT_COMMIT_STR)
            if next_commit_id_index != -1:
                next_commit_id_index += len(PARENT_COMMIT_STR)
                next_commit_id = res.text[next_commit_id_index:next_commit_id_index + ID_LEN]
            else:
                next_commit_id = None
            commit_data['parent_id'] = next_commit_id

            title_start_index = res.text.find(TITLE_STR) + len(TITLE_STR) + ID_LEN + 2
            tag_in_title_index = res.text.find('<span', title_start_index)
            title_stop_index = res.text.find('</a>', title_start_index)

            if tag_in_title_index != -1 and tag_in_title_index < title_stop_index:
                title_stop_index = tag_in_title_index - 1

            commit_data['title'] = res.text[title_start_index:title_stop_index]

            msg_start_index = res.text.find(MSG_STR) + len(MSG_STR) + 1
            msg_stop_index = res.text.find('</div>', msg_start_index)
            commit_data['msg'] = res.text[msg_start_index:msg_stop_index]
            commit_data['msg'] = commit_data['msg'].replace('&nbsp', ' ')
            commit_data['msg'] = commit_data['msg'].replace('<br/>', '')

            yield commit_data

            cached_commit_info = self._scraped_bugs.get(next_commit_id)
            while cached_commit_info:
                yield cached_commit_info

                next_commit_id = cached_commit_info['parent_id']
                cached_commit_info = self._scraped_bugs.get(next_commit_id)

