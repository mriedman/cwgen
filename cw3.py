from random import choice
from copy import copy
import json
from collections import defaultdict
import numpy as np
from typing import Final, List, Dict

alphabet = [i for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']

with open('xwilist.json') as f:
    xwi_wordlist1 = json.load(f)

for i in list(xwi_wordlist1.keys()):
    if int(i) < 25:
        del xwi_wordlist1[i]
    # if int(i) == 25:
    #     xwi_wordlist1[i] = [j for j in xwi_wordlist1[i] if len(j) == 3]

xwi_words_by_length = [{i: [word for word in xwi_wordlist1[i] if len(word) == j] for i in xwi_wordlist1} for j in range(22)]


class CM(object):
    words_by_length = xwi_words_by_length

    def __init__(self, height: int, width: int, boxes: List[List[int]]):
        # CONSTANTS- not to be changed outside __init__
        # Grid height
        self.height: Final[int] = height
        # Grid width
        self.width: Final[int] = width
        # Grid boxes as [col, row]
        self.boxes: Final[List[List[int]]] = boxes
        # Contains Box objects for each grid tile
        self.box_array: Final[List[List[Box]]] = [[Box(self, i, j) for i in range(width)] for j in range(height)]
        # Grid containing clue indices for across and down boxes in a grid
        self.clue_num_list: List[List[List[int]]] = [[[0 for _ in range(width)] for _ in range(height)] for _ in range(2)]
        # [num_across, num_clues]
        self.num_words_to_fill: Final[List[int]] = []
        # List of WordLists
        self.full_word_list: Final[List[WordList]] = []
        self.words_info = []
        self.wr1 = [[[0 for _ in range(width)] for _ in range(height)] for _ in range(2)]
        self.words_inserted = 1
        self.clue_nums_filled = []
        self.main_wordlist_dict: Final[Dict[int, MainWordList]] = {}

        # DYNAMIC VARIBALES
        # Grid characters
        self.grid = [['' for _ in range(width)] for _ in range(height)]
        # Word insertion on which a grid character was fixed (-1 means unfilled)
        self.grid_history = np.zeros((height, width), int) - 1

        for box in boxes:
            self.grid[box[1]][box[0]] = '#'
            self.box_array[box[1]][box[0]].make_black()
            self.clue_num_list[0][box[1]][box[0]] = -1
            self.clue_num_list[1][box[1]][box[0]] = -1
        clue_num = 0
        for i in range(2):
            for row_num in range(height):
                for col_num in range(width):
                    if self.clue_num_list[i][row_num][col_num] != -1 and (row_num * i + col_num * (1 - i) == 0 or self.clue_num_list[i][row_num - i][col_num - 1 + i] == -1):
                        coord1, coord2 = row_num * i + col_num * (1 - i), row_num * i + col_num * (1 - i)
                        while coord1 < [width, height][i] and self.get_box_by_order(self.clue_num_list[i], [row_num, col_num][i], coord1, i) != -1:
                            coord1 += 1
                        word_len = coord1 - coord2

                        if word_len not in self.main_wordlist_dict:
                            self.main_wordlist_dict[word_len] = MainWordList(self.words_by_length[word_len])
                        self.full_word_list.append(WordList(self.main_wordlist_dict[word_len]))

                        for l in range(coord2, coord1):
                            self.set_box_by_order(self.wr1[i], l - coord2, [row_num, col_num][i], l, i)
                            self.set_box_by_order(self.clue_num_list[i], clue_num, [row_num, col_num][i], l, i)
                        self.words_info.append([col_num, row_num, word_len])
                        clue_num += 1
            self.num_words_to_fill.append(clue_num)
        for i in self.box_array:
            for row_num in i:
                row_num.create_box()

        for i in self.clue_num_list:
            for j in i:
                for k in j:
                    if k >= 0:
                        print('%2d ' % (k,), end='')
                    else:
                        print('## ', end='')
                print()
            print()

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
            if self.grid_history[row_num][col] == -1:
                self.grid_history[row_num][col] = self.words_inserted
            # self.box_array[row_num][col].possible_chars = [word[col - col_num]]
            box = self.box_array[row_num][col]
            box.char_history[box.char_history < 0] = self.words_inserted
            box.char_history[alphabet.index(word[col - col_num])] = -1
            self.full_word_list[self.clue_num_list[0][row_num][col]].unfilled = False
            self.reduce(col, row_num, 1)

    def insert_down_word(self, word, row_num, col_num):
        if col_num + len(word) > self.height:
            raise ValueError('Word Doesn\'t Fit in the Grid')
        for i in range(col_num, col_num + len(word)):
            if self.box_array[i][row_num].cc(word[i - col_num]) and not (self.grid[i][row_num] == '' or self.grid[i][row_num] == word[i - col_num]):
                raise ValueError('Word Doesn\'t Fit with other Words')
            self.grid[i][row_num] = word[i - col_num]
            if self.grid_history[i][row_num] == -1:
                self.grid_history[i][row_num] = self.words_inserted
            # self.box_array[i][row_num].possible_chars = [word[i - col_num]]
            box = self.box_array[i][row_num]
            box.char_history[box.char_history < 0] = self.words_inserted
            box.char_history[alphabet.index(word[i - col_num])] = -1
            self.full_word_list[self.clue_num_list[1][i][row_num]].unfilled = False
            self.reduce(row_num, i, 0)

    def insert_across_or_down(self, word, row_num, col_num, i):
        if i == 0:
            self.insert_across_word(word, row_num, col_num)
        elif i == 1:
            self.insert_down_word(word, row_num, col_num)
        '''for words in self.full_word_list:
            words.words_inserted = self.words_inserted'''
        for word_len in self.main_wordlist_dict:
            self.main_wordlist_dict[word_len].words_inserted = self.words_inserted + 1

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
                self.words_inserted += 1
                self.clue_nums_filled.append(slot_num)
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

    def frw(self, n, tries):
        for i in range(tries):
            next_word = self.full_word_list[n].choice()
            if next_word is not None:
                self.insert_by_number(next_word, n)
                return next_word, n
            else:
                return None

    def reduce(self, col_num, row_num, direction):
        grid_char = self.grid[row_num][col_num]
        clue_num = self.clue_num_list[direction][row_num][col_num]

        # word_info: [col, row, length]
        word_info = self.words_info[clue_num]
        full_word_list = self.full_word_list[clue_num]
        for j in range(len(full_word_list)):
            if full_word_list[j][[col_num, row_num][direction] - word_info[direction]] != grid_char:
                del full_word_list[j]
        for i in range(word_info[2]):
            row, col = word_info[1] + direction * i, word_info[0] + (1 - direction) * i
            if self.grid[row][col] == '':
                box = self.box_array[row][col]
                for j in range(len(box.char_set)):
                    if not box.cc(box.char_set[j]):
                        continue
                    next_char = box.char_set[j]
                    if all(self.full_word_list[clue_num].word_by_letter[i][next_char] >= 0):
                        possible_words = box.wordlists[1 - direction]
                        still_possible = possible_words.delete_by_char(self.wr1[1 - direction][row][col], next_char)
                        # if still_possible == -1:
                        #     return -1
                        box.char_history[j] = self.words_inserted
            return 0

    def roll_back(self, last_word, last_num):
        print('Rollback Time! Word:', last_word)
        self.words_inserted -= 1
        # Grid fill
        letters_to_revert = np.array(np.nonzero(self.grid_history == self.words_inserted)).T
        for square in letters_to_revert:
            self.grid[square[0]][square[1]] = ''
        self.grid_history[self.grid_history == self.words_inserted] = -1

        # WordLists
        for words in self.full_word_list:
            words.wordnums[words.wordnums == self.words_inserted] = -1
            for pos_list in words.word_by_letter:
                for letter in pos_list:
                    pos_list[letter][pos_list[letter] == self.words_inserted] = -1

        for word_len in self.main_wordlist_dict:
            self.main_wordlist_dict[word_len].words_inserted = self.words_inserted - 1

        self.full_word_list[self.clue_nums_filled.pop()].unfilled = True

        # Boxes
        for row in self.box_array:
            for box in row:
                box.char_history[box.char_history == self.words_inserted] = -1

        # Don't try previous word again
        self.words_inserted -= 1
        for word_len in self.main_wordlist_dict:
            self.main_wordlist_dict[word_len].words_inserted = self.words_inserted - 1

        self.full_word_list[last_num].del2(self.full_word_list[last_num].main_wordlist.word_to_num[last_word])

        self.words_inserted += 1
        for word_len in self.main_wordlist_dict:
            self.main_wordlist_dict[word_len].words_inserted = self.words_inserted - 1

        print('Done with rollback!')

    def fill_puzzle(self):
        last_words, last_nums = [], []
        for _ in range(500):
            print(self)
            # [clue_num, num of possible words for that clue]
            n = [0, 10 ** 9]
            for idx, words in enumerate(self.full_word_list):
                possible_words = words.possible_word_equiv()
                if possible_words < n[1] and words.unfilled:
                    n = [idx, possible_words]
            if n == [0, 10 ** 9]:
                return self
            res = self.frw(n[0], 1)
            if res:
                last_words.append(res[0])
                last_nums.append(res[1])
            else:
                self.roll_back(last_words.pop(), last_nums.pop())
        return self


class MainWordList(object):
    alphabet = alphabet

    def __init__(self, wordlist):
        self.wordlist = [word for j in wordlist for word in wordlist[j]]
        self.word_values = {word: v for v in wordlist for word in wordlist[v]}
        self.num_to_word = {i: self.wordlist[i] for i in range(len(self.wordlist))}
        self.word_to_num = {self.wordlist[i]: i for i in range(len(self.wordlist))}
        self.nums_by_letter = []
        self.nums_by_letter_rev = []
        self.words_inserted = 1

        for letter_idx in range(len(self.wordlist[0])):
            nums_by_ith_letter = {i: [] for i in self.alphabet}
            nums_by_ith_letter_rev = {}
            for wordlist_idx in range(len(self.wordlist)):
                nums_by_ith_letter_rev[wordlist_idx] = len(nums_by_ith_letter[self.wordlist[wordlist_idx][letter_idx]])
                nums_by_ith_letter[self.wordlist[wordlist_idx][letter_idx]].append(wordlist_idx)
            self.nums_by_letter.append({i: np.array(nums_by_ith_letter[i]) for i in nums_by_ith_letter})
            self.nums_by_letter_rev.append(nums_by_ith_letter_rev)


class WordList(object):
    alphabet = alphabet

    def __init__(self, main_wordlist: MainWordList):
        self.main_wordlist = main_wordlist
        self.wordlist = main_wordlist.wordlist
        self.wordnums = np.zeros(len(self.wordlist), int) - 1
        self.word_by_letter = []
        self.cell_list = [{} for _ in range(len(self.wordlist[0]))]
        self.unfilled = True

        for letter_pos in self.main_wordlist.nums_by_letter:
            self.word_by_letter.append({letter: np.zeros(letter_pos[letter].shape, int) - 1 for letter in letter_pos})

    def get_word(self, n):
        return self.wordlist[n]

    def __getitem__(self, item):
        return self.get_word(item)

    def choice(self):
        by_value = defaultdict(list)
        for word_num in np.nonzero(self.wordnums < 0)[0]:
            by_value[self.main_wordlist.word_values[self.wordlist[word_num]]].append(self.wordlist[word_num])
        if len(by_value.keys()) > 0:
            print('Next Word Value:', max(by_value.keys()))
        else:
            print('No words found!')
            return None
        word = choice(by_value[max(by_value.keys())])
        print(word)
        return word

    def __delitem__(self, key):
        self.del2(key)

    def del2(self, word_num):
        word = self.wordlist[word_num]
        for idx, letter in enumerate(word):
            if self.word_by_letter[idx][letter][self.main_wordlist.nums_by_letter_rev[idx][word_num]] == -1:
                self.word_by_letter[idx][letter][self.main_wordlist.nums_by_letter_rev[idx][word_num]] = self.main_wordlist.words_inserted
        if self.wordnums[word_num] == -1:
            self.wordnums[word_num] = self.main_wordlist.words_inserted

    def __len__(self):
        return len(self.wordlist)

    def __str__(self):
        return str([self[i] for i in np.nonzero(self.wordnums < 0)[0]])

    def delete_by_char(self, pos_in_word, deleted_char):
        still_possible = np.nonzero(self.word_by_letter[pos_in_word][deleted_char] < 0)[0]
        word_nums = [i for i in self.main_wordlist.nums_by_letter[pos_in_word][deleted_char][still_possible]]
        for pos in word_nums:
            self.del2(pos)
        for pos in range(len(self.word_by_letter)):
            for letter in self.word_by_letter[pos]:
                if all(self.word_by_letter[pos][letter] > 0) and letter in self.cell_list[pos][0].possible_chars() and (pos != pos_in_word or letter != deleted_char):
                    box, word_nums = (self.cell_list[pos][m] for m in range(2))
                    box.char_history[alphabet.index(letter)] = self.main_wordlist.words_inserted
                    # if not self.cell_list[pos][0].possible_chars():
                    #     return -1
                    box.wordlists[1 - word_nums].delete_by_char(box.crossword.wr1[1 - word_nums][box.row][box.col], letter)
        return 0

    def possible_word_equiv(self):
        word_sum = 0
        val_conv_chart = {'60': 100, '50': 50, '30': 25, '25': 20, '20': 15, '15': 5, '10': 2, '5': 1}
        len_conv_chart = {3: 10, 4: 10, 5: 15, 6: 25, 7: 35, 8: 50, 9: 75, 10: 100, 11: 100, 12: 100, 13: 100, 14: 100,
                          15: 100, 16: 100, 17: 100, 18: 100, 19: 100, 20: 100, 21: 100}
        for idx, word in enumerate(self.wordlist):
            if self.wordnums[idx] == -1:
                word_sum += val_conv_chart[self.main_wordlist.word_values[word]]
        return word_sum / len_conv_chart[len(self.wordlist[0])]


class Box(object):
    def __init__(self, cw, x, y):
        self.crossword = cw
        self.col, self.row = x, y
        self.char_set = np.array(copy(alphabet))
        self.char_history = np.zeros(len(alphabet), int) - 1
        self.is_black = False
        self.wordlists = []

    def create_box(self):
        if self.crossword.clue_num_list[0][self.row][self.col] == -1:
            return 0
        self.wordlists = [self.crossword.full_word_list[self.crossword.clue_num_list[i][self.row][self.col]] for i in range(2)]
        for i in range(2):
            self.wordlists[i].cell_list[self.crossword.wr1[i][self.row][self.col]] = [self, i]

    def possible_chars(self):
        return list(self.char_set[self.char_history < 0])

    def cc(self, c):
        if c in self.possible_chars():
            return True
        return False

    def make_black(self):
        self.is_black = True


cws = [[5, 0], [5, 1], [5, 2], [10, 0], [10, 1], [10, 2], [0, 4], [1, 4], [2, 4], [3, 4], [8, 3], [7, 4], [7, 5],
       [6, 6], [5, 6], [5, 7], [4, 8], [3, 9],
       [0, 10], [1, 10], [13, 4], [14, 4], [11, 5], [10, 6], [9, 7], [9, 8], [8, 8], [7, 9], [7, 10], [6, 11], [4, 12],
       [4, 13], [4, 14], [10, 12], [10, 13], [10, 14], [11, 10], [12, 10], [13, 10], [14, 10]]
saturday_boxes0 = '''
.......x.......
.......x.......
.......x.......
xx.............
x....x....xx...
....x....x.....
...x....x....xx
...............
xx....x....x...
.....x....x....
...xx....x....x
.............xx
.......x.......
.......x.......
.......x.......
'''

boxes0 = '''
.........x.....
.........x.....
.........x.....
.....x.........
xxx....x.......
......x.......x
.........x.....
...xx.....xx...
.....x.........
x.......x......
.......x....xxx
.........x.....
.....x.........
.....x.........
.....x.........
'''

boxes = [[k, i] for i, j in enumerate(boxes0.split('\n')[1:-1]) for k, k1 in enumerate(j) if k1 == 'x']
print(boxes)

cw1 = CM(15, 15, cws)
print(cw1)
print(cw1.fill_puzzle())
