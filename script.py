import json
import subprocess
import unittest
import requests
import os
import sys

'''
Problem: find probabilities of characters given some coding language

Chose to focus on python given timeframe
Want to build functionality to adjust probability calcs
- uppercase vs. lowercase
- symbols, whitespace, newline characters
- would like to use search function of github api to crawl through repos

Run using: 
python script.py stong1108/wikiracer
'''

def probabilities(d_master):
    total = sum(d_master.values())
    probs = {k: 1.*d_master[k]/total for k in d_master}
    return probs

def count_chars_for_file(filename):
    # return counter of characters
    with open(filename, 'rb') as f:
        text = f.read()
    d_slave = {}
    for char in text:
        d_slave[char] = d_slave.get(char, 0) + 1
    return d_slave

def look_at_repo(repo_api_url):
    # execute count_chars_for_file for python files in repo_api_url
    output = json.loads(requests.get(repo_api_url).content)
    clone_url = output['clone_url']
    subprocess.call(['git', 'clone', clone_url, 'temp'])

    # get in folder, find .py files to execute count_chars_for_file function
    files_to_explore = []
    for root, dirs, files in os.walk('temp'):
        for f in files:
            if f[-3:] == '.py':
                files_to_explore.append(root+"/"+f)
    file_dicts = map(count_chars_for_file, files_to_explore)

    d_master = {}
    for d in file_dicts:
        d_master = merge_master(d_master, d)

    return d_master

def merge_master(d_master, d_slave):
    for key in d_slave:
        d_master[key] = d_master.get(key, 0) + d_slave[key]
    return d_master


class Tests(unittest.TestCase):
    def test_merge_master(self):
        d_master = {'a': 3, 'b': 2}
        d_slave = {'b': 2, 'c': 1}
        self.assertDictEqual(merge_master(d_master, d_slave), {'a': 3, 'b': 4, 'c': 1})

    def test_count_chars(self):
        filename = 'test.py'
        self.assertDictEqual(count_chars_for_file(filename), {'\'': 2, 'h': 1, 'i': 1, '\n': 1})

if __name__ == '__main__':
    user_repo = sys.argv[1]
    api_repo_url = 'https://api.github.com/repos/'+user_repo
    d_master = look_at_repo(api_repo_url)
    print json.dumps(probabilities(d_master), indent=4)
