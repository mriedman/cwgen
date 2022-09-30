import json
from collections import defaultdict
from time import time
import numpy as np

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

def benchmark():
    flatlist = [i for j in wordlist for i in wordlist[j]]
    sixes = [i for i in flatlist if len(i) == 6]
    six_arr = np.array([[i for i in j] for j in sixes])
    t = time()
    for j in range(len(sixes)):
        if sixes[j][3] != 'A':
            t -= 0e-5
    print(time() - t)
    t = time()
    # a = [''.join([i for i in j]) for j in six_arr[six_arr[:, 3] != ord('A')]][:10]
    a = []
    print(time() - t)
    print(a)
    t = time()
    a = six_arr[:, 3] != 'A'
    print(time() - t)
    print(six_arr[a][:10])


while False:
    print(check_word(input()))


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

xw3 = '''ASAMI#MAUI#UMNO
LINEN#ACTS#NOON
INGOT#REAR#LRON
EEEWIDTH#APIANO
####FAY#YENTL##
STCLAIR#LLC#FAB
AAHED##PEI#TIPI
YREKA#MOM#GOBIG
ODAS#HEP##ONETO
KOP#HUE#APTERYX
##SKULK#ROY####
AGENTK#ATLANTIS
BRAE#OOPSY#OHNO
RATE#UNREP#LEON
ASSS#TESTS#OATY'''

xw4 = '''GULF#SKEWED#TOD
OSEE#APPEAR#ULE
DEPTHCHARGE#NEN
#TRIO###ELATION
WHOSWE#ENEMYSPY
GISH#PARTD#KIRS
TSE#CEDE##PEAY#
###THEEAGLES###
#CIAO##DIVE#GAD
URSI#ARESO#DELA
GOONTOUR#VERTEX
SALTERN###MUIR#
OKA#STYLEPOINTS
MET#LAOTZE#DTEN
EDE#ASNERS#SODA'''

xw5 = '''VISA#ONRAMP#DST
ESTS#LIENEE#EAR
NOAHWEBSTER#APE
#MIRA###ETRURIA
LENEXA#MGMIDGET
BREW#ADAGE#DONS
SSR#PREC##ZEDS#
###SUPERUSER###
#LEER##ONCD#STU
CINC#VINCA#PHEN
OLDCOINS#BYHAND
MYWORLD###EERO#
API#BEERGARDENS
TAT#ILENES#RIEL
EDH#CYPHER#ENDY'''

xw6 = '''ICBM#OHNONO#BUS
THUR#MATRON#IPA
TAMMANYHALL#CVI
#TRON###TOOCOOL
WHATIF#BOSWORTH
WAPO#LEERS#ONEO
IMS#CAVA##ALES#
###TATERTOTS###
#AJOT##CONV#AVS
FLAK#KCUPS#TMAC
LAZYSLOB#ONHAND
UNZONED###RENU#
TIA#ABECEDARIAN
ING#KARPOV#ETTA
EEE#ENSLER#DAUB'''

xw7 = '''IDOL#OWASSO#ADM
SISI#OILCUP#REY
ROCKCONCERT#CTR
#RUED###NEITHER
WALLSTREETCRASH
IMAY#AERIE#AITS
EAR#GLEE##DSCS#
###MUCKAMUCK###
#ENDS##DESI#UNU
ACAP#PAEAN#GPAS
RUSHHOURTRAFFIC
CATDOOR###DORR#
ADA#UPONTHEROOF
NOS#SEROSA#CNBC
ERE#EDATES#ETIC'''

xw_actual = '''NATO#ASPIRE#BAT
ANON#CLOSET#APE
MONSTERMASH#RTE
#MEAD###BEIGNET
WALLSTREETCRASH
ALOE#WILLS#ARTE
NYC#FIFE##ODDS#
###CONTACTUS###
#TBAR##NAIR#BEE
PHAT#GROPE#AIMS
RUSHHOURTRAFFIC
ONMYOWN###IRON#
ADA#FILMSPLICER
MET#FLOTUS#CANI
SRI#ADWARS#ALTO'''

xw8 = '''PEPE#ASMARA#SPH
AMIA#THENOD#ARI
MONSTERMASH#GED
#BEEB###BEOFUSE
WALLSTREETCRASH
ANOS#MARLO#AREI
LDG#GENE##IGOR#
###CONTACTUS###
#CMAS##DYED#OWI
CHIT#IBEST#AFRO
RUSHHOURTRAFFIC
OKAYING###OFIT#
OKC#FILMSPLICER
NET#ISEEIT#REMO
SRS#SERENA#MRED'''

xw9 = '''BASH#SCALA#MUDS
RIPA#HADIT#EMIL
IWANTITALL#ANNI
SANDART##ASGOOD
###VCR#RASTA###
LAPAT#REN#RINSE
CROC#HEADBANGER
DIN#JIMCROW#ANI
TETEATETES#LISE
VSIGN#ETS#ALOES
###GETTO#BUC###
MAOTSE##POLOADS
OCHO#LOVEYDOVEY
TAMS#LOCAL#LIAM
HISS#YORKE#JARS'''

xw10 = '''IMDB#SPOCK#NANO
MYRA#KERRI#IPAD
HEAD#INCARNATED
IAMSAMSAMIAM###
TRAMP#ESP#REECE
###ERBE#OOCYTES
#MALIA#GNC##HEP
#CALLMEISHMAEL#
VCR##BLT#ROLLO#
MOONPIE#DEAL###
IONIA#GIO#THEOC
###MYNAMEISEARL
SPARSENESS#ASEA
OREO#ICANT#RYAN
LORD#LENTO#TADS'''

check_xword(xw10)
# benchmark()
