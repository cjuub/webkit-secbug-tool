#!/usr/bin/python3

import sys
import argparse
import requests

from gitlogparser import GitLogParser
from webkitbugscraper import WebKitBugScraper 


def _get_git_url(commit_id: str):
    return 'https://git.webkit.org/?p=WebKit.git;a=commit;h=' + commit_id


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('--gitdir', help='Parse commit info from local webkit git repository.')
    parse.add_argument('--since', help='Only consider commits after this date.')
    args = parse.parse_args()

    max_date = args.since if hasattr(args, 'since') else '2018-01-01T00:00:00-00:00'

    if args.gitdir:
        git_log_parser = GitLogParser(args.gitdir, max_date)
        commits = git_log_parser.parse()
    else:
        raise Exception('Not yet possible to run without local webkit git repository.')

    scraped_bugs = WebKitBugScraper('cache.json')

    cnt = 0
    outfile = open('out.txt', 'w')
    for commit in commits:
        bug_info = scraped_bugs.get(commit['id'])

        if not bug_info:
            bug_info = scraped_bugs.scrape(commit)

        if bug_info['classified']:
            outfile.write(commit['msg'] + '\n')
            outfile.write(_get_git_url(commit['id']) + '\n')
            outfile.write('\n')

        cnt += 1
        sys.stdout.write("\r%d/%d" % (cnt, len(commits)))
        sys.stdout.flush()

    close(outfile)

if __name__ == '__main__':
    main()

