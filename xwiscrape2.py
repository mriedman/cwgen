import os
import json
from collections import defaultdict

words = defaultdict(set)

for f in os.listdir('xwlist'):
    if 'xwi' in f:
        with open(f'xwlist/{f}') as f2:
            new_words = json.load(f2)
            for i in new_words:
                words[i] = words[i].union(set(new_words[i]))

for i in words:
    print(i)
    print(len(words[i]))
    print(list(words[i])[:20])

'''with open('xwilist.json', 'wordlist1') as f:
    json.dump({i: list(words[i]) for i in words}, f)'''
