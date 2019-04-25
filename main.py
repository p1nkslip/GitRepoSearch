#!/usr/bin/python3

import requests
import base64
import sys
import urllib3
import json
import time
import re
import math
from cmd import Cmd

# disable SSL warnings
urllib3.disable_warnings()

# Time string
TIMESTR = time.strftime("%Y%m%d-%H%M%S")

# Github variables
GIT_SERVER = 'https://api.github.com'
GIT_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# HTTP Headers
headers = {}
headers['Content-Type'] = 'application/json'
headers['Authorization'] = ('token %s' % GIT_TOKEN)

r_whoami = requests.get(GIT_URL + '/user', data="", headers=headers, verify=False, allow_redirects=False)
r_rate = requests.get(GIT_URL + '/rate_limit', data="", headers=headers, verify=False, allow_redirects=False)

class myprompt(Cmd):

    def filter_sensitive_info(self, content_list):
        print("################################################## Summary ######################################################" + '\n')

        reg_awskeyid = re.compile("AKIA([A-Z0-9]){16}")

        for decoded_content in content_list:
            for line in decoded_content.split('\n'):
                # regex
                if reg_awskeyid.search(line):
                    print("AWS Key ID: " + line)
                # strings
                if "-----BEGIN PRIVATE KEY-----" in line:
                    print ("PrivKey: " + line)
                if "-----BEGIN RSA PRIVATE KEY-----" in line:
                    print ("PrivKey: " + line)
                if "password" in line:
                    print ("Password: " + line)

        print("#################################################################################################################" + '\n')

    def repo_content(self, repo_url):
        r_giturl = requests.get(url=repo_url, headers=headers)
        encoded_content = json.loads(r_giturl.text)['content']
        decoded_content = base64.b64decode(encoded_content.encode('ascii')).decode("utf-8",errors='ignore')
        return decoded_content

    def repo_info(self, repo_owner, repo_name):
        print ("repo owner: " + repo_owner)
        print ("repo name: " + repo_name)
        r_master = requests.get(GIT_URL + '/repos/' + repo_owner + '/' + repo_name + '/branches/master', data="", headers=headers, verify=False, allow_redirects=False)
        try:
            commit_info = json.loads(r_master.text)['commit']['commit']
            print("branch url (master): " + r_master.url)
            print(" last commit: " + commit_info['committer']['date'])
            print(" by: " + commit_info['committer']['email'])
        except:
            print("branch info not available")

    ### commands ###

    def do_searchcode(self, srchterm):

        # Find number of entries for searchterm
        r_search = requests.get(GIT_URL + '/search/code?q=' + srchterm, data="", headers=headers, verify=False, allow_redirects=False)
        searchCount = int(json.loads(r_search.text)['total_count'])
        pageCount = int(searchCount)/100
        print ("Search Count: " + str(searchCount))
        print ("Page Count: " + str(math.ceil(pageCount)))

        # Iterate through pages, collect all results
        all_results = []
        for pagex in range(int(math.ceil(pageCount))):
            r_fullsearch = requests.get(GIT_URL + '/search/code?q=' + srchterm + '&page=' + str(pagex) + '&per_page=' + str(100) + '+sort:committer-date-desc', data="", headers=headers, verify=False, allow_redirects=False)
            searchResults = json.loads(r_fullsearch.text)['items']

            # Retrieve details for each entry
            for entry in searchResults:
                content_list = []

                repo_url = entry['git_url']
                repo_owner = entry['repository']['owner']['login']
                repo_name = entry['repository']['name']

                decoded_content = self.repo_content(repo_url)

                print('\n')
                print("=================================================================================================================")
                print("+ html_url: " + entry['html_url'])
                print("+ git_url: " + entry['git_url'])
                self.repo_info(repo_owner,repo_name)
                print("-----------------------------------------------------------------------------------------------------------------")

                # Print full content with highlighted search terms:
                search_terms = srchterm.split()
                for term in search_terms:
                    decoded_content = decoded_content.replace(term, '\033[44;33m{}\033[m'.format(term))

                content_list.append(decoded_content)
                all_results.append(decoded_content)
                print (decoded_content)

        self.filter_sensitive_info(all_results)

        print ('\n' + str(searchCount) + " entries contained the search term: " + "'" + srchterm + "'")
        print ("URL Query: " + r_fullsearch.url  + '\n')

    def do_whoami(self, args):
        userInfo = json.loads(r_whoami.text)
        print("Name: " + userInfo['login'])
        print("Type: " + userInfo['type'])
        print("Created: " + userInfo['created_at'])
        print("Updated: " + userInfo['updated_at'])

    def do_rate(self, args):
        rateInfo = json.loads(r_rate.text)
        print ('\n' + "Core Limit: " + str(rateInfo['resources']['core']['limit']))
        print (" Remaining: " + str(rateInfo['resources']['core']['remaining']))
        print (" Reset: " + str(rateInfo['resources']['core']['reset']) + '\n')
        print ("Search Limit: " + str(rateInfo['resources']['search']['limit']))
        print (" Remaining: " + str(rateInfo['resources']['search']['remaining']))
        print (" Reset: " + str(rateInfo['resources']['search']['reset']) + '\n')

    def do_quit(self, args):
        print("Cyal8r")
        raise SystemExit

if __name__ == '__main__':
    print("")
    prompt = myprompt()
    prompt.prompt = '> '
    prompt.cmdloop()
