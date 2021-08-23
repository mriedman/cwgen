import json
from collections import defaultdict

with open('xwilist.json') as f:
    wordlist = json.load(f)

def check_word(s):
    found = False
    for i in wordlist:
        if s in wordlist[i]:
            return i
    if s == 'stop':
        exit(0)
    if not found:
        return -1

def change_letter(c1, c2):
    flatlist = [i for j in wordlist for i in wordlist[j]]
    for i in flatlist:
        if c1 in i and len(i) >= 4:
            for j, k in enumerate(i[:-3]):
                if k == c1:
                    if i[:j] + c2 + ('' if j == len(i) - 1 else i[j+1:]) in flatlist:
                        print(i, i[:j] + c2 + ('' if j == len(i) - 1 else i[j+1:]))

def check_xword(xw):
    xws = xw.split('\n')
    wv = defaultdict(list)
    for row in xws:
        for word in row.split('#'):
            if len(word) > 0:
                wv[check_word(word)].append(word)
    for col in range(len(xws[0])):
        s = ''.join(i[col] for i in xws)
        for word in s.split('#'):
            if len(word) > 0:
                wv[check_word(word)].append(word)

    for i in wv:
        print(f'{i}: {len(wv[i])} words')
        print(wv[i])

while False:
    check_word(input())


xw = '''HETUP#ZOOM#SDSU
AMUSE#ENNA#HRAP
DEPOT#RYAN#AAHS
JUICEBOX#SMUGLY
####REI#IMING##
ARMYMEN#WAR#EON
MAEVE##FIN#VDAY
USTEN#OWN#COOKE
STRS#MAD##INUIT
TAO#AIK#ORANTES
##NANAS#GEO####
WHOSIS#TRESBIEN
RUMI#MORAL#ASTI
ALEC#ABIDE#BLOC
PASS#LLOYD#SANE'''

xw2 = '''MCRIB#BSMT#OOZE
UHURU#EACH#GNAT
FINAL#HYDE#LENA
FATELVIS#BLEDEL
####YIN#FLORA##
BLEARED#LOG#YAZ
YALTA##BUB#ISEE
LYING#ITO#BRASI
ALSO#EDU##ROLOS
WAH#OYE#TRICEPS
##APNEA#BUC####
WOOHOO#NOSEJOBS
ANTI#FRONT#OVID
ITIS#REVEL#GIGA
TOSH#ABASE#SDAK'''

check_xword(xw2)
