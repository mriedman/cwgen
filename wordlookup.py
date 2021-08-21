import json

with open('xwilist.json') as f:
    wordlist = json.load(f)

while True:
    s = input()
    found = False
    for i in wordlist:
        if s in wordlist[i]:
            print(i)
            found = True
    if s == '':
        break
    if not found:
        print('None')
