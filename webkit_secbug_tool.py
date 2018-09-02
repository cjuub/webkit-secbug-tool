#!/usr/bin/python3

import sys
import argparse
import requests

from gitlogparser import GitLogParser
from webkitbugscraper import WebKitBugScraper 
from webkit_commit_scraper import WebKitCommitScraper


WEBKIT_COMMIT_BASE_URL = 'https://git.webkit.org/?p=WebKit.git;a=commit;h='


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('--gitdir', help='Parse commit info from local webkit git repository.')
    parse.add_argument('--since', help='Only consider commits after this date.')
    args = parse.parse_args()

    max_date = args.since if hasattr(args, 'since') else '2018-01-01T00:00:00-00:00'

    scraped_bugs = WebKitBugScraper('cache.json')

    if args.gitdir:
        commit_generator = GitLogParser(args.gitdir, max_date)
    else:
        commit_generator = WebKitCommitScraper(WEBKIT_COMMIT_BASE_URL, scraped_bugs, max_date)

    cnt = 0
    outfile = open('out.txt', 'w')
    for commit in commit_generator:
        bug_info = scraped_bugs.get(commit['id'])

        if not bug_info:
            bug_info = scraped_bugs.scrape(commit)

        if bug_info['classified']:
            outfile.write(commit['title'] + '\n')
            outfile.write(WEBKIT_COMMIT_BASE_URL + commit['id'] + '\n')
            outfile.write('\n')

        cnt += 1
        sys.stdout.write("\r%d" % cnt)
        sys.stdout.flush()

    close(outfile)

if __name__ == '__main__':
    main()

