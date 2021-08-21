from random import choice
from copy import copy, deepcopy
import json
from collections import defaultdict

wordlist1 = open('cw.txt').read()
alphabet = [i for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
wordlist2 = [i.split(' ') for i in wordlist1.split('\n')]
wordlist3 = []
for i in wordlist2:
    try:
        if i[-2][-2:] == '%:':
            wordlist3.append([j for j in i if (not j == '') and not (len(j) >= 2 and j[-2:] == '%:')])
    except:
        pass
wordlist4 = [[int(i[0]), i[1]] for i in wordlist3]
wordlist5 = [i[1] for i in wordlist3]
wordlist6 = {i[1]: int(i[0]) for i in wordlist3}
words_by_length = [[] for i in range(22)]
c = [0, '']
for i in wordlist5:
    words_by_length[len(i)].append(i)

with open('xwilist.json') as f:
    xwi_wordlist1 = json.load(f)

xwi_words_by_length = [{i: [word for word in xwi_wordlist1[i] if len(word) == j] for i in xwi_wordlist1} for j in range(22)]
# xwi_words_by_length = [{'60': i} for i in words_by_length]
# xwi_words_by_length = [[word for i in xwi_wordlist1 for word in xwi_wordlist1[i] if (len(word) == j and (j < 6 or i == '60'))] for j in range(22)]
# xwi_words_by_length = words_by_length
# print(xwi_words_by_length[7][-30:])
# print(xwi_words_by_length)
'''print(wordlist5[:30])
for i in range(4, 10):
    print(words_by_length[i][:20])
    print(xwi_words_by_length[i]['60'][:20])
exit(0)'''

class CM(object):
    # Next line unnecessary
    # wordlist = wordlist5

    # words_by_length = words_by_length
    words_by_length = xwi_words_by_length

    def __init__(self, height, width, boxes):
        self.height = height
        self.width = width
        self.boxes = boxes
        self.grid = [['' for _ in range(width)] for _ in range(height)]
        # self.box_array=[[copy(alphabet) for i in range(wordlist1)] for j in range(height)]
        self.box_array = [[Box(self, i, j) for i in range(width)] for j in range(height)]
        self.clue_num_list = [[[0 for _ in range(width)] for _ in range(height)] for _ in range(2)]
        self.num_words_to_fill = []
        self.full_word_list = []
        self.words_info = []
        self.wr1 = [[[0 for _ in range(width)] for _ in range(height)] for _ in range(2)]
        for box in boxes:
            self.grid[box[1]][box[0]] = '#'
            self.box_array[box[1]][box[0]].make_black()
            self.clue_num_list[0][box[1]][box[0]] = '#'
            self.clue_num_list[1][box[1]][box[0]] = '#'
        clue_num = 0
        for i in range(2):
            for row_num in range(height):
                for col_num in range(width):
                    if self.clue_num_list[i][row_num][col_num] != '#' and (row_num * i + col_num * (1 - i) == 0 or self.clue_num_list[i][row_num - i][col_num - 1 + i] == '#'):
                        coord1, coord2 = row_num * i + col_num * (1 - i), row_num * i + col_num * (1 - i)
                        while coord1 < [width, height][i] and self.get_box_by_order(self.clue_num_list[i], [row_num, col_num][i], coord1, i) != '#':
                            coord1 += 1
                        self.full_word_list.append(WordList(self.words_by_length[coord1 - coord2]))
                        for l in range(coord2, coord1):
                            self.set_box_by_order(self.wr1[i], l - coord2, [row_num, col_num][i], l, i)
                            self.set_box_by_order(self.clue_num_list[i], clue_num, [row_num, col_num][i], l, i)
                        self.words_info.append([col_num, row_num, coord1 - coord2])
                        clue_num += 1
            self.num_words_to_fill.append(clue_num)
        for i in self.box_array:
            for row_num in i:
                row_num.create_box()

    @staticmethod
    def get_box_by_order(wordlist, coord1, coord2, coord_order):
        if coord_order == 0:
            return wordlist[coord1][coord2]
        elif coord_order == 1:
            return wordlist[coord2][coord1]

    @staticmethod
    def set_box_by_order(l, letter, coord1, coord2, coord_order):
        if coord_order == 0:
            l[coord1][coord2] = letter
        elif coord_order == 1:
            l[coord2][coord1] = letter

    def insert_across_word(self, word, col_num, row_num):
        if col_num + len(word) > self.width:
            raise SystemExit('Word Doesn\'tries Fit in the Grid')
        for col in range(col_num, col_num + len(word)):
            if self.box_array[row_num][col].cc(word[col - col_num]) and not (self.grid[row_num][col] == '' or self.grid[row_num][col] == word[col - col_num]):
                raise SystemExit('Word Doesn\'tries Fit with other Words')
            self.grid[row_num][col] = word[col - col_num]
            self.box_array[row_num][col].possible_chars = [word[col - col_num]]
            self.full_word_list[self.clue_num_list[0][row_num][col]].unfilled = False
            self.reduce1(col, row_num, 1)

    def insert_down_word(self, word, row_num, col_num):
        if col_num + len(word) > self.height:
            raise ValueError('Word Doesn\'tries Fit in the Grid')
        for i in range(col_num, col_num + len(word)):
            if self.box_array[i][row_num].cc(word[i - col_num]) and not (self.grid[i][row_num] == '' or self.grid[i][row_num] == word[i - col_num]):
                raise ValueError('Word Doesn\'tries Fit with other Words')
            self.grid[i][row_num] = word[i - col_num]
            self.box_array[i][row_num].possible_chars = [word[i - col_num]]
            self.full_word_list[self.clue_num_list[1][i][row_num]].unfilled = False
            self.reduce1(row_num, i, 0)

    def insert_across_or_down(self, word, row_num, col_num, i):
        if i == 0:
            self.insert_across_word(word, row_num, col_num)
        elif i == 1:
            self.insert_down_word(word, row_num, col_num)

    def insert_by_number(self, word, slot_num):
        if slot_num < self.num_words_to_fill[0]:
            direction = 0
        elif slot_num < self.num_words_to_fill[1]:
            direction = 1
        else:
            raise ValueError('Number Too High')
        is_inserted = False
        for row in range(self.height):
            for col in range(self.width):
                if self.clue_num_list[direction][row][col] == slot_num:
                    self.insert_across_or_down(word, col, row, direction)
                    is_inserted = True
                    break
            if is_inserted:
                break

    def __str__(self):
        s = ''
        for i in self.grid:
            for j in i:
                if j == '':
                    s += '-'
                else:
                    s += j
            s += '\n'
        return s

    # This isn't used for some reason
    def insert_word2(self, w, x, y, p):
        if p == 0:
            self.insert_across_word(w, x, y)
        elif p == 1:
            self.insert_down_word(w, x, y)

    def frw(self, n, tries):
        for i in range(tries):
            try:
                self.insert_by_number(self.full_word_list[n].choice(), n)
            except:
                pass

    def reduce1(self, col_num, row_num, direction):
        grid_char = self.grid[row_num][col_num]
        clue_num = self.clue_num_list[direction][row_num][col_num]

        # [col, row, length]
        word_info = self.words_info[clue_num]
        full_word_list = self.full_word_list[clue_num]
        deleted = 0
        for j in range(len(full_word_list)):
            if full_word_list[j - deleted][[col_num, row_num][direction] - word_info[direction]] != grid_char:
                del full_word_list[j - deleted]
                deleted += 1
        for i in range(word_info[2]):
            row, col = word_info[1] + direction * i, word_info[0] + (1 - direction) * i
            deleted = 0
            if self.grid[row][col] == '':
                box = self.box_array[row][col]
                for j in range(len(box.possible_chars)):
                    next_char = box.possible_chars[j - deleted]
                    if next_char == 0:
                        del box.possible_chars[j - deleted]
                        deleted += 1
                        continue
                    if len(self.full_word_list[clue_num].word_by_letter[i][next_char]) == 0:
                        possible_words = box.wordlists[1 - direction]
                        possible_words.delete_by_char(self.wr1[1 - direction][row][col], next_char)
                        del box.possible_chars[j - deleted]
                        deleted += 1

    def fill_puzzle(self, max_attempts=7):
        print(self)
        # [clue_num, num of possible words for that clue]
        n = [0, 10 ** 6]
        for idx, words in enumerate(self.full_word_list):
            # print('Nums:', idx, ':', len(words))
            if len(words) < n[1] and words.unfilled:
                n = [idx, len(words)]
        if n == [0, 10 ** 5]:
            return self
        for i in range(max_attempts):
            try:
                print('a')
                # THIS IS IT RIGHT HERE!!!
                cw1 = deepcopy(self)
                print('boxes')
                cw1.frw(n[0], 1)
                cw1.fill_puzzle(max_attempts)
                return cw1
            except IndexError:
                pass
        raise IndexError('')

    '''def __deepcopy__(self):
        cw1 = CM(self.height, self.width, self.boxes)
        cw1.grid = deepcopy(self.grid)
        cw1.full_word_list = [i.deepcopy() for i in self.full_word_list]
        cw1.box_array = [[j.deepcopy(self) for j in i] for i in self.box_array]
        # print(self.box_array)
        # print(1)
        # print(self.full_word_list)
        return cw1'''


class WordList(object):
    alphabet = alphabet

    def __init__(self, wordlist):
        flatlist = [word for j in wordlist for word in wordlist[j]]
        # self.wordnums = [i for i in range(len(wordlist))]  # 1
        self.wordnums = [i for i in range(len(flatlist))]  #
        # self.wordlist = deepcopy(wordlist)  # 1
        self.wordlist = flatlist  #
        # self.wordlist0 = deepcopy(wordlist)  #
        self.word_values = {word: v for v in wordlist for word in wordlist[v]}  #
        self.num_to_word = {i: self.wordlist[i] for i in range(len(self.wordlist))}
        self.word_to_num = {self.wordlist[i]: i for i in range(len(self.wordlist))}
        self.word_by_letter = []
        self.cell_list = [{} for _ in range(len(self.wordlist[0]))]
        self.unfilled = True
        for letter_idx in range(len(self.wordlist[0])):
            by_ith_letter = {i: {} for i in self.alphabet}
            for wordlist_idx in range(len(self.wordlist)):
                by_ith_letter[self.wordlist[wordlist_idx][letter_idx]][self.word_to_num[self.wordlist[wordlist_idx]]] = self.wordlist[wordlist_idx]
            self.word_by_letter.append(by_ith_letter)

    def get_word(self, n):
        return self.wordlist[self.wordnums[n]]

    def __getitem__(self, item):
        return self.get_word(item)

    def choice(self):
        by_value = defaultdict(list)
        for word_num in self.wordnums:
            by_value[self.word_values[self.wordlist[word_num]]].append(self.wordlist[word_num])
        if len(by_value.keys()) > 0:
            print('Next Word Value:', max(by_value.keys()))
        word = choice(by_value[max(by_value.keys())])
        print(word)
        return word
        # return self.wordlist[choice(self.wordnums)]

    def __delitem__(self, key):
        self.del2(self.wordnums[key], key)

    def del2(self, word_num, k0=-1):
        word = self.wordlist[word_num]
        for idx, letter in enumerate(word):
            del self.word_by_letter[idx][letter][word_num]
        if k0 < 0:
            del self.wordnums[self.wordnums.index(word_num)]
        else:
            del self.wordnums[k0]

    def __len__(self):
        return len(self.wordnums)

    def __str__(self):
        return str([self[i] for i in range(len(self.wordnums))])

    def wbpl(self, x, y):
        a = [[self.wordlist[i], i] for i in self.word_by_letter[x][y]]
        for i in a:
            if i[0] == -1:
                del self.word_by_letter[x][y][i[1]]
        return [i[0] for i in a if not i[0] == -1]

    def delete_by_char(self, pos_in_word, deleted_char):
        direction = [i for i in self.word_by_letter[pos_in_word][deleted_char]]
        for pos in direction:
            self.del2(pos)
        for pos in range(len(self.word_by_letter)):
            for letter in self.word_by_letter[pos]:
                if len(self.word_by_letter[pos][letter]) == 0 and letter in self.cell_list[pos][0].possible_chars and (pos != pos_in_word or letter != deleted_char):
                    box, direction = (self.cell_list[pos][m] for m in range(2))
                    box.possible_chars[box.possible_chars.index(letter)] = 0
                    box.wordlists[1 - direction].delete_by_char(box.crossword.wr1[1 - direction][box.row][box.col], letter)

    def deepcopy(self):
        # print(5)
        # print(vars(self).keys())
        wl2 = WordList(self.wordlist)
        for i in ['wordnums', 'num_to_word', 'word_by_letter', 'cell_list']:
            wl2.wordnums = deepcopy(wl2[i])
        return wl2
        # print(5)


class Box(object):
    def __init__(self, cw, x, y):
        self.crossword = cw
        self.col, self.row = x, y
        self.possible_chars = copy(alphabet)
        self.is_black = False
        self.wordlists = []

    def create_box(self):
        if self.crossword.clue_num_list[0][self.row][self.col] == '#':
            return 0
        self.wordlists = [self.crossword.full_word_list[self.crossword.clue_num_list[i][self.row][self.col]] for i in range(2)]
        for i in range(2):
            self.wordlists[i].cell_list[self.crossword.wr1[i][self.row][self.col]] = [self, i]

    def cc(self, c):
        if c in self.possible_chars:
            return True
        return False

    def make_black(self):
        self.is_black = True

    def deepcopy(self, cw):
        # print(6)
        # print(vars(self).keys())
        b2 = Box(cw, self.col, self.row)
        b2.is_black = self.is_black
        b2.create_box()
        # print(6)
        return b2


'''cw1=CM(8,7,[[0,3],[6,3],[3,4]])
#cw1.frw(0,1)
cw1.insert_word('STEEPLE',0,0)
print(cw1)
print(cw1.full_word_list[10].word_by_letter[6]['Y'])
print(cw1.full_word_list[6].word_by_letter[1]['Y'])
cw1.ibn('TUESD',3)
print(cw1)
print(cw1.full_word_list[10].word_by_letter[6]['Y'])
print(cw1.full_word_list[6].word_by_letter[2])'''
# cw1=CM(5,5,[[0,0],[0,4],[4,0],[4,4]])
'''cw1.ibn('CUP',0)
cw1.ibn('TYPOS',1)
print(cw1)
print(cw1.full_word_list[2].word_by_letter[1]['N'])'''
cws = [[5, 0], [5, 1], [5, 2], [10, 0], [10, 1], [10, 2], [0, 4], [1, 4], [2, 4], [3, 4], [8, 3], [7, 4], [7, 5],
       [6, 6], [5, 6], [5, 7], [4, 8], [3, 9],
       [0, 10], [1, 10], [13, 4], [14, 4], [11, 5], [10, 6], [9, 7], [9, 8], [8, 8], [7, 9], [7, 10], [6, 11], [4, 12],
       [4, 13], [4, 14], [10, 12], [10, 13], [10, 14], [11, 10], [12, 10], [13, 10], [14, 10]]

# cw1=CM(6,5,[[0,0],[4,0],[0,5],[4,5]])
cw1 = CM(15, 15, cws)
print(cw1)
# print(vars(cw1).keys())
# cw2=cw1.deepcopy()
# print(cw2.box_array[1][1]==cw1.box_array[1][1])
# print(cw2.full_word_list[1]==cw1.full_word_list[1])
# print(cw2.box_array)
# print(cw2.full_word_list)
cw1.fill_puzzle(7)
