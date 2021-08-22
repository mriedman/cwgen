import json

with open('xwilist.json') as f:
    wordlist = json.load(f)

while False:
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

flatlist = [i for j in wordlist for i in wordlist[j]]
c1, c2 = 'R', 'O'
for i in flatlist:
    if c1 in i and len(i) >= 4:
        for j, k in enumerate(i[:-3]):
            if k == c1:
                if i[:j] + c2 + ('' if j == len(i) - 1 else i[j+1:]) in flatlist:
                    print(i, i[:j] + c2 + ('' if j == len(i) - 1 else i[j+1:]))
