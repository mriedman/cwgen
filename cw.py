from random import randint,choice
from copy import copy,deepcopy
w=open('cw.txt').read()
ab=[i for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
w01=[i.split(' ') for i in w.split('\n')]
w02=[]
for i in w01:
    try:
        if i[-2][-2:]=='%:':
            w02.append([j for j in i if (not j=='') and not (len(j)>=2 and j[-2:]=='%:')])
    except:
        pass
w1a=[[int(i[0]),i[1]] for i in w02]
w1=[i[1] for i in w02]
w2={i[1]:int(i[0]) for i in w02}
wbl=[[] for i in range(21)]
c=[0,'']
for i in w1:
    wbl[len(i)].append(i)
class CM(object):
    wl=w1
    wbl=wbl
    def __init__(self,h,w,b):
        self.H=h
        self.W=w
        self.b=b
        self.g=[['' for i in range(w)] for j in range(h)]
        #self.box_array=[[copy(alphabet) for i in range(wordlist1)] for j in range(height)]
        self.pc=[[Box(self,i,j) for i in range(w)] for j in range(h)]
        self.pwl=[[[0 for i in range(w)] for j in range(h)] for k in range(2)]
        self.wll=[]
        self.fwl=[]
        self.wr=[]
        self.wr1=[[[0 for i in range(w)] for j in range(h)] for k in range(2)]
        for i in b:
            self.g[i[1]][i[0]]='#'
            self.pc[i[1]][i[0]].bl()
            self.pwl[0][i[1]][i[0]]='#'
            self.pwl[1][i[1]][i[0]]='#'
        c1=0
        for i in range(2):
            for j in range(h):
                for k in range(w):
                    if self.pwl[i][j][k]!='#' and (j*i+k*(1-i)==0 or self.pwl[i][j-i][k-1+i]=='#'):
                        c,c0=j*i+k*(1-i),j*i+k*(1-i)
                        while c<[w,h][i] and self.r(self.pwl[i],[j,k][i],c,i)!='#':
                            c+=1
                        self.fwl.append(WL(self.wbl[c-c0]))
                        for l in range(c0,c):
                            self.ra(self.wr1[i],l-c0,[j,k][i],l,i)
                            self.ra(self.pwl[i],c1,[j,k][i],l,i)
                        self.wr.append([k,j,c-c0])
                        c1+=1
            self.wll.append(c1)
        for i in self.pc:
            for j in i:
                j.ib()
    def r(self,l,x,y,s):
        if s==0:
            return l[x][y]
        elif s==1:
            return l[y][x]
    def ra(self,l,a,x,y,s):
        if s==0:
            l[x][y]=a
        elif s==1:
            l[y][x]=a
    def ia(self,w,x,y):
        if x+len(w)>self.W:
            raise SystemExit('Word Doesn\'tries Fit in the Grid')
        for i in range(x,x+len(w)):
            if self.pc[y][i].cc(w[i-x]) and not (self.g[y][i]=='' or self.g[y][i]==w[i-x]):
                raise SystemExit('Word Doesn\'tries Fit with other Words')
            self.g[y][i]=w[i-x]
            self.pc[y][i].pc=[w[i-x]]
            self.fwl[self.pwl[0][y][i]].uf = False
            self.rd1(i,y,1)
    def id1(self,w,y,x):
        if x+len(w)>self.H:
            raise ValueError('Word Doesn\'tries Fit in the Grid')
        for i in range(x,x+len(w)):
            if self.pc[i][y].cc(w[i-x]) and not (self.g[i][y]=='' or self.g[i][y]==w[i-x]):
                raise ValueError('Word Doesn\'tries Fit with other Words')
            self.g[i][y]=w[i-x]
            self.pc[i][y].pc=[w[i-x]]
            self.fwl[self.pwl[1][i][y]].uf=False
            self.rd1(y,i,0)
    def iad(self,w,y,x,i):
        if i==0:
            self.ia(w,y,x)
        elif i==1:
            self.id1(w,y,x)
    def ibn(self,w,n):
        if n<self.wll[0]:
            i=0
        elif n<self.wll[1]:
            i=1
        else:
            raise ValueError('Number Too High')
        f=False
        for j in range(self.H):
            for k in range(self.W):
                if self.pwl[i][j][k]==n:
                    self.iad(w,k,j,i)
                    f=True
                    break
            if f:
                break
    def __str__(self):
        s=''
        for i in self.g:
            for j in i:
                if j=='':
                    s+='-'
                else:
                    s+=j
            s+='\n'
        return s
    def iw(self,w,x,y,p):
        if p==0:
            self.ia(w,x,y)
        elif p==1:
            self.id1(w,x,y)
    def frw(self,n,t):
        for i in range(t):
            try:
                self.ibn(self.fwl[n].choice(),n)
            except SystemExit:
                pass
    def rd1(self,x,y,p):
        ch=self.g[y][x]
        n=self.pwl[p][y][x]
        nl=self.wr[n]
        fwl0=self.fwl[n]
        j0=0
        for j in range(len(fwl0)):
            if fwl0[j-j0][[x,y][p]-nl[p]]!=ch:
                del fwl0[j-j0]
                j0+=1
        for i in range(nl[2]):
            y2,x2=nl[1]+p*i,nl[0]+(1-p)*i
            j0=0
            if self.g[y2][x2]=='':
                pc0=self.pc[y2][x2]
                for j in range(len(pc0.pc)):
                    c=pc0.pc[j-j0]
                    if c==0:
                        del pc0.pc[j-j0]
                        j0+=1
                        continue
                    if len(self.fwl[n].wbpl0[i][c])==0:
                        pcwl=pc0.ad[1-p]
                        pcwl.dbc(self.wr1[1-p][y2][x2],c)
                        del pc0.pc[j-j0]
                        j0+=1
    def f1(self,k):
        print(self)
        n=[0,10**5]
        for i in range(len(self.fwl)):
            if len(self.fwl[i])<n[1] and self.fwl[i].uf:
                n=[i,len(self.fwl[i])]
        if n==[0,10**5]:
            return self
        for i in range(k):
            try:
                #print('a')
                cw1=deepcopy(self)
                #print('boxes')
                cw1.frw(n[0],1)
                cw1.f1(k)
                return cw1
            except IndexError:
                pass
        raise IndexError('')
    def deepcopy(self):
        cw1=CM(self.H,self.W,self.b)
        cw1.g=deepcopy(self.g)
        cw1.fwl=[i.deepcopy() for i in self.fwl]
        cw1.pc=[[j.deepcopy(self) for j in i] for i in self.pc]
        #print(self.box_array)
        #print(1)
        #print(self.full_word_list)
        return cw1
class WL(object):
    ab=ab
    def __init__(self,l):
        self.l=[i for i in range(len(l))]
        self.l0=deepcopy(l)
        self.ll0={i:self.l0[i] for i in range(len(self.l0))}
        self.ll1={self.l0[i]:i for i in range(len(self.l0))}
        self.wbpl0=[]
        self.pcl=[0 for i in range(len(l[0]))]
        self.uf=True
        for i in range(len(l[0])):
            a={i:{} for i in self.ab}
            for j in range(len(l)):
                a[l[j][i]][self.ll1[l[j]]]=l[j]
            self.wbpl0.append(a)
    def gw(self,n):
        return self.l0[self.l[n]]
    def __getitem__(self, item):
        return self.gw(item)
    def choice(self):
        return self.l0[choice(self.l)]
    def __delitem__(self,key):
        self.del2(self.l[key],key)
    def del2(self,k,k0=-1):
        w=self.l0[k]
        for i in range(len(w)):
            del self.wbpl0[i][w[i]][k]
        if k0<0:
            del self.l[self.l.index(k)]
        else:
            del self.l[k0]
    def __len__(self):
        return len(self.l)
    def __str__(self):
        return str([self[i] for i in range(len(self.l))])
    def wbpl(self,x,y):
        a=[[self.l0[i],i] for i in self.wbpl0[x][y]]
        for i in a:
            if i[0]==-1:
                del self.wbpl0[x][y][i[1]]
        return [i[0] for i in a if not i[0]==-1]
    def dbc(self,x,c):
        l=[i for i in self.wbpl0[x][c]]
        for i in l:
            self.del2(i)
        for i in range(len(self.wbpl0)):
            for j in self.wbpl0[i]:
                if len(self.wbpl0[i][j])==0 and j in self.pcl[i][0].box_array and (i != x or j != c):
                    k,l=(self.pcl[i][m] for m in range(2))
                    k.box_array[k.box_array.index(j)]=0
                    k.ad[1-l].dbc(k.crossword.wr1[1 - l][k.y][k.x], j)
    def deepcopy(self):
        #print(5)
        #print(vars(self).keys())
        wl2=WL(self.l0)
        for i in ['wordnums','num_to_word','word_by_letter','pcl']:
            wl2.l=deepcopy(wl2[i])
        return wl2
        #print(5)
class Box(object):
    def __init__(self,cw,x,y):
        self.cw=cw
        self.x,self.y=x,y
        self.pc=copy(ab)
        self.b=False
        self.ad=0
    def ib(self):
        if self.cw.possible_word_list[0][self.y][self.x]== '#':
            return 0
        self.ad=[self.cw.full_word_list[self.cw.possible_word_list[i][self.y][self.x]] for i in range(2)]
        for i in range(2):
            self.ad[i].pcl[self.cw.wr1[i][self.y][self.x]]=[self,i]
    def cc(self,c):
        if c in self.pc:
            return True
        return False
    def bl(self):
        self.b=True
    def deepcopy(self,cw):
        #print(6)
        #print(vars(self).keys())
        b2=Box(cw,self.x,self.y)
        b2.b=self.b
        b2.ib()
        #print(6)
        return b2
'''cw1=CM(8,7,[[0,3],[6,3],[3,4]])
#cw1.frw(0,1)
cw1.ia('STEEPLE',0,0)
print(cw1)
print(cw1.full_word_list[10].word_by_letter[6]['Y'])
print(cw1.full_word_list[6].word_by_letter[1]['Y'])
cw1.ibn('TUESD',3)
print(cw1)
print(cw1.full_word_list[10].word_by_letter[6]['Y'])
print(cw1.full_word_list[6].word_by_letter[2])'''
#cw1=CM(5,5,[[0,0],[0,4],[4,0],[4,4]])
'''cw1.ibn('CUP',0)
cw1.ibn('TYPOS',1)
print(cw1)
print(cw1.full_word_list[2].word_by_letter[1]['N'])'''
cws=[[5,0],[5,1],[5,2],[10,0],[10,1],[10,2],[0,4],[1,4],[2,4],[3,4],[8,3],[7,4],[7,5],[6,6],[5,6],[5,7],[4,8],[3,9],
     [0,10],[1,10],[13,4],[14,4],[11,5],[10,6],[9,7],[9,8],[8,8],[7,9],[7,10],[6,11],[4,12],[4,13],[4,14],[10,12],[10,13],[10,14],[11,10],[12,10],[13,10],[14,10]]

cw1=CM(6,5,[[0,0],[4,0],[0,5],[4,5]])
print(cw1)
#print(vars(cw1).keys())
#cw2=cw1.deepcopy()
#print(cw2.box_array[1][1]==cw1.box_array[1][1])
#print(cw2.full_word_list[1]==cw1.full_word_list[1])
#print(cw2.box_array)
#print(cw2.full_word_list)
#cw1.fill_puzzle(7)