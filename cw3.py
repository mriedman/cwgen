from random import choice
from copy import copy
import json
from collections import defaultdict
import numpy as np
from typing import Final, List, Dict, Tuple, Union

alphabet = [i for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']

with open('xwilist.json') as f:
    xwi_wordlist1 = json.load(f)

for i in list(xwi_wordlist1.keys()):
    if int(i) < 40:
        del xwi_wordlist1[i]
    # if int(i) == 25:
    #     xwi_wordlist1[i] = [j for j in xwi_wordlist1[i] if len(j) == 3]

xwi_words_by_length = [{i: [word for word in xwi_wordlist1[i] if len(word) == j] for i in xwi_wordlist1}
                       for j in range(22)]


class CM(object):
    def __init__(self, height: int, width: int, boxes: str, themers: List[str] = [], custom_words: List[List[Tuple[int, int]]] = []):
        # CONSTANTS- not to be changed outside __init__
        # XWI Wordlist with themers
        self.words_by_length = xwi_words_by_length
        for word in themers:
            self.words_by_length[len(word)]['60'].append(word)
        # Grid height
        self.height: Final[int] = height
        # Grid width
        self.width: Final[int] = width
        # Grid boxes as [col, row]
        self.boxes: Final[List[List[int]]] = [[k, i] for i, j in enumerate(boxes.split('\n')[1:-1]) for k, k1 in enumerate(j) if k1 == 'x']
        # Contains Box objects for each grid tile
        self.box_array: Final[List[List[Box]]] = [[Box(self, i, j) for i in range(width)] for j in range(height)]
        # Grid containing clue indices for across and down boxes in a grid
        self.clue_num_list: List[List[List[Union[int, Dict]]]] = \
            [[[0 for _ in range(width)] for _ in range(height)] for _ in range(2)] + \
                   [[[{} for _ in range(width)] for _ in range(height)]]
        self.special_clue_locs = {}
        # [num_across, num_clues]
        self.num_words_to_fill: Final[List[int]] = []
        # List of WordLists
        self.full_word_list: Final[List[WordList]] = []
        self.words_info = []
        self.wr1 = [[[0 for _ in range(width)] for _ in range(height)] for _ in range(2)] + \
                   [[[{} for _ in range(width)] for _ in range(height)]]
        self.words_inserted = [1]
        self.clue_nums_filled = []
        self.main_wordlist_dict: Final[Dict[int, MainWordList]] = {}

        # DYNAMIC VARIBALES
        # Grid characters
        self.grid = [['' for _ in range(width)] for _ in range(height)]
        # Word insertion on which a grid character was fixed (-1 means unfilled)
        self.grid_history = np.zeros((height, width), int) - 1

        for box in self.boxes:
            self.grid[box[1]][box[0]] = '#'
            self.box_array[box[1]][box[0]].make_black()
            self.clue_num_list[0][box[1]][box[0]] = -1
            self.clue_num_list[1][box[1]][box[0]] = -1
        clue_num = 0

        cur_box_vals = boxes.split('\n')[1:-1]
        self.start_words = []
        for i in range(2):
            for row_num in range(height):
                for col_num in range(width):
                    if self.clue_num_list[i][row_num][col_num] != -1 and \
                            (row_num * i + col_num * (1 - i) == 0 or
                             self.clue_num_list[i][row_num - i][col_num - 1 + i] == -1):
                        coord1, coord2 = row_num * i + col_num * (1 - i), row_num * i + col_num * (1 - i)
                        new_word = ''
                        while coord1 < [width, height][i] and self.get_box_by_order(self.clue_num_list[i], [row_num, col_num][i], coord1, i) != -1:
                            new_word += self.get_box_by_order(cur_box_vals, [row_num, col_num][i], coord1, i)
                            coord1 += 1
                        word_len = coord1 - coord2
                        self.start_words.append(new_word)

                        if word_len not in self.main_wordlist_dict:
                            self.main_wordlist_dict[word_len] = MainWordList(self.words_by_length[word_len], self.words_inserted)
                        self.full_word_list.append(WordList(self.main_wordlist_dict[word_len]))

                        for idx in range(coord2, coord1):
                            self.set_box_by_order(self.wr1[i], idx - coord2, [row_num, col_num][i], idx, i)
                            self.set_box_by_order(self.clue_num_list[i], clue_num, [row_num, col_num][i], idx, i)
                        self.words_info.append([col_num, row_num, word_len])
                        clue_num += 1
            self.num_words_to_fill.append(clue_num)
        for word_boxes in custom_words:
            word_len = len(word_boxes)
            if word_len not in self.main_wordlist_dict:
                self.main_wordlist_dict[word_len] = MainWordList(self.words_by_length[word_len], self.words_inserted)
            self.full_word_list.append(WordList(self.main_wordlist_dict[word_len]))
            for idx in range(word_len):
                self.wr1[2][word_boxes[idx][0]][word_boxes[idx][1]][clue_num] = idx
                self.clue_num_list[2][word_boxes[idx][0]][word_boxes[idx][1]][clue_num] = clue_num
                self.special_clue_locs[clue_num] = word_boxes

            clue_num += 1

        self.num_words_to_fill.append(clue_num)

        for i in self.box_array:
            for row_num in i:
                row_num.create_box()

        '''for i in self.clue_num_list:
            for j in i:
                for k in j:
                    if k >= 0:
                        print('%2d ' % (k,), end='')
                    else:
                        print('## ', end='')
                print()
            print()'''
        # self.show_slot_nums()

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
                self.grid_history[row_num][col] = self.words_inserted[0]
            # self.box_array[row_num][col].possible_chars = [word[col - col_num]]
            box = self.box_array[row_num][col]
            box.char_history[box.char_history < 0] = self.words_inserted[0]
            box.char_history[alphabet.index(word[col - col_num])] = -1
            self.full_word_list[self.clue_num_list[0][row_num][col]].unfilled = False
            self.reduce(col, row_num, 1)
            self.reduce(col, row_num, 2)

    def insert_down_word(self, word, row_num, col_num):
        if col_num + len(word) > self.height:
            raise ValueError('Word Doesn\'t Fit in the Grid')
        for i in range(col_num, col_num + len(word)):
            if self.box_array[i][row_num].cc(word[i - col_num]) and not (self.grid[i][row_num] == '' or self.grid[i][row_num] == word[i - col_num]):
                raise ValueError('Word Doesn\'t Fit with other Words')
            self.grid[i][row_num] = word[i - col_num]
            if self.grid_history[i][row_num] == -1:
                self.grid_history[i][row_num] = self.words_inserted[0]
            box = self.box_array[i][row_num]
            box.char_history[box.char_history < 0] = self.words_inserted[0]
            box.char_history[alphabet.index(word[i - col_num])] = -1
            self.full_word_list[self.clue_num_list[1][i][row_num]].unfilled = False
            self.reduce(row_num, i, 0)
            self.reduce(row_num, i, 2)

    def insert_custom_word(self, word, slot_num):
        boxes = self.special_clue_locs[slot_num]
        if len(boxes) != len(word):
            raise ValueError('Word Doesn\'t Fit in the Grid')
        for idx, i in enumerate(boxes):
            if self.box_array[i[0]][i[1]].cc(word[idx]) and not (self.grid[i[0]][i[1]] == '' or self.grid[i[0]][i[1]] == word[idx]):
                raise ValueError('Word Doesn\'t Fit with other Words')
            self.grid[i[0]][i[1]] = word[idx]
            if self.grid_history[i[0]][i[1]] == -1:
                self.grid_history[i[0]][i[1]] = self.words_inserted[0]
            box = self.box_array[i[0]][i[1]]
            box.char_history[box.char_history < 0] = self.words_inserted[0]
            box.char_history[alphabet.index(word[idx])] = -1
            self.full_word_list[slot_num].unfilled = False
            self.reduce(i[1], i[0], 0)
            self.reduce(i[1], i[0], 1)
            self.reduce(i[1], i[0], 2)

    def insert_across_or_down(self, word, row_num, col_num, i, slot_num):
        if i == 0:
            self.insert_across_word(word, row_num, col_num)
        elif i == 1:
            self.insert_down_word(word, row_num, col_num)
        elif i == 2:
            self.insert_custom_word(word, slot_num)
        '''for word_len in self.main_wordlist_dict:
            self.main_wordlist_dict[word_len].words_inserted = self.words_inserted + 1'''

    def insert_by_number(self, word, slot_num):
        if slot_num < self.num_words_to_fill[0]:
            direction = 0
        elif slot_num < self.num_words_to_fill[1]:
            direction = 1
        elif slot_num < self.num_words_to_fill[2]:
            direction = 2
        else:
            raise ValueError('Number Too High')
        is_inserted = False
        for row in range(self.height):
            for col in range(self.width):
                if self.clue_num_list[direction][row][col] == slot_num or direction == 2:
                    self.insert_across_or_down(word, col, row, direction, slot_num)
                    is_inserted = True
                    break
            if is_inserted:
                self.words_inserted[0] += 1
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

    def str_with_slot_num(self, slot_num):
        if slot_num < self.num_words_to_fill[0]:
            direction = 0
        elif slot_num < self.num_words_to_fill[1]:
            direction = 1
        elif slot_num < self.num_words_to_fill[2]:
            direction = 2
        else:
            raise ValueError('Slot number too high.')
        s = ''
        for i0, i in enumerate(self.grid):
            for j0, j in enumerate(i):
                if j == '':
                    if self.clue_num_list[direction][i0][j0] == slot_num or (direction == 2 and slot_num in self.clue_num_list[direction][i0][j0]):
                        s += '?'
                    else:
                        s += '-'
                else:
                    s += j
            s += '\n'
        return s

    def show_slot_nums(self):
        a = ['Across:', 'Down:']
        for i in self.clue_num_list[:-1]:
            print(a.pop(0))
            for j in i:
                for k in j:
                    if k >= 0:
                        print('%2d ' % (k,), end='')
                    else:
                        print('## ', end='')
                print()
            print()

    def frw(self, n, auto=1, word=''):
        # Auto code indicates if a choice other than inserting a word was made
        print(self.str_with_slot_num(n))
        next_word, auto_code = self.full_word_list[n].choice(auto, self.show_slot_nums, word)
        if auto_code == -1:
            self.insert_by_number(next_word, n)
            return next_word, n, auto_code
        else:
            return next_word, None, auto_code

    def reduce(self, col_num: int, row_num: int, direction):
        grid_char = self.grid[row_num][col_num]
        clue_num = self.clue_num_list[direction][row_num][col_num]

        if direction < 2:
            # word_info: [col, row, length]
            word_info = self.words_info[clue_num]

            boxes = [(word_info[1] + direction * i, word_info[0] + (1 - direction) * i) for i in range(word_info[2])]
            box_idx = [col_num, row_num][direction] - word_info[direction]
            word_len = word_info[2]
            return self.reduce_help(boxes, box_idx, word_len, clue_num, grid_char, direction)
        else:
            ret = 0
            for num in clue_num:
                boxes = self.special_clue_locs[num]
                box_idx = boxes.index((row_num, col_num))
                word_len = len(boxes)
                ret = self.reduce_help(boxes, box_idx, word_len, num, grid_char, direction)
                if ret < 0:
                    return ret
            return ret

    def reduce_help(self, boxes, box_idx, word_len, clue_num, grid_char, direction):
        word_list = self.full_word_list[clue_num]
        words_to_delete = word_list.wordlist_arr[:, box_idx] != grid_char
        word_list.del_mult(np.nonzero(words_to_delete)[0])

        for i in range(word_len):
            # row, col = word_info[1] + direction * i, word_info[0] + (1 - direction) * i
            row, col = boxes[i]
            if self.grid[row][col] == '':
                box = self.box_array[row][col]
                for j in range(len(box.char_set)):
                    if not box.cc(box.char_set[j]):
                        continue
                    next_char = box.char_set[j]
                    if all(self.full_word_list[clue_num].word_by_letter[i][next_char] >= 0):
                        for k in range(2):
                            if k == direction:
                                continue
                            possible_words = box.wordlists[k]
                            still_possible = possible_words.delete_by_char(self.wr1[k][row][col], next_char)
                            if still_possible == -1:
                                return -1
                        for slot in self.wr1[2][row][col]:
                            possible_words = box.wordlists[2][slot]
                            still_possible = possible_words.delete_by_char(self.wr1[2][row][col][slot], next_char)
                            if still_possible == -1:
                                return -1
                        box.char_history[j] = self.words_inserted[0]
        return 0

    def roll_back(self, last_word, last_num):
        print('Deleting word:', last_word)
        self.words_inserted[0] -= 1
        # Grid fill
        letters_to_revert = np.array(np.nonzero(self.grid_history == self.words_inserted[0])).T
        for square in letters_to_revert:
            self.grid[square[0]][square[1]] = ''
        self.grid_history[self.grid_history == self.words_inserted[0]] = -1

        # WordLists
        for words in self.full_word_list:
            words.wordnums[words.wordnums == self.words_inserted[0]] = -1
            for pos_list in words.word_by_letter:
                for letter in pos_list:
                    pos_list[letter][pos_list[letter] == self.words_inserted[0]] = -1

        '''for word_len in self.main_wordlist_dict:
            self.main_wordlist_dict[word_len].words_inserted = self.words_inserted - 1'''

        self.full_word_list[self.clue_nums_filled.pop()].unfilled = True

        # Boxes
        for row in self.box_array:
            for box in row:
                box.char_history[box.char_history == self.words_inserted[0]] = -1

        # Don't try previous word again
        self.words_inserted[0] -= 1
        '''for word_len in self.main_wordlist_dict:
            self.main_wordlist_dict[word_len].words_inserted = self.words_inserted'''

        # self.full_word_list[last_num].del2(self.full_word_list[last_num].main_wordlist.word_to_num[last_word])
        word_to_num = self.full_word_list[last_num].main_wordlist.word_to_num
        if last_word in word_to_num:
            self.full_word_list[last_num].del_mult(np.array([word_to_num[last_word]]))

        for idx, letter in enumerate(last_word):
            if all(self.full_word_list[last_num].word_by_letter[idx][letter] >= 0):
                box = self.full_word_list[last_num].cell_list[idx][0]
                # box.char_history[alphabet.index(letter)] = self.words_inserted[0]
                self.full_word_list[last_num].delete_by_char(idx, letter)
                box.char_history[alphabet.index(letter)] = self.words_inserted[0]

        self.words_inserted[0] += 1
        '''for word_len in self.main_wordlist_dict:
            self.main_wordlist_dict[word_len].words_inserted = self.words_inserted'''

        print('Done deleting the word!')

    def fill_puzzle(self, auto=True):
        last_words, last_nums, preferred_slot_num = [], [], -1
        target = -1

        for _ in range(100000):
            # print(self)
            # [clue_num, num of possible words for that clue]
            n = [0, 10 ** 9]

            for idx, words in enumerate(self.full_word_list):
                possible_words = words.possible_word_equiv()
                if possible_words < n[1] and words.unfilled:
                    n = [idx, possible_words]
            if n == [0, 10 ** 9]:
                return self
            if preferred_slot_num >= 0:
                n[0] = preferred_slot_num

            auto_code = auto if _ >= target else 1

            start_word, start_num = '', -1
            while len(self.start_words) > 0:
                start_word = self.start_words.pop()
                if '.' not in start_word:
                    start_num = len(self.start_words)
                    break
            if start_num > -1:
                n[0] = start_num
                auto_code = 2
            else:
                start_word = ''


            res = self.frw(n[0], auto_code, word=start_word)
            preferred_slot_num = -1
            if res[2] == -1:
                last_words.append(res[0])
                last_nums.append(res[1])
            elif res[2] == -2:
                self.roll_back(last_words.pop(), last_nums.pop())
            elif res[2] == -3:
                target = _ + res[0] + 1
            elif res[2] == -4:
                print('Exiting...')
                exit(0)
            elif res[2] >= 0:
                if self.full_word_list[res[2]].unfilled:
                    preferred_slot_num = res[2]
                else:
                    print('This slot number is already filled in!')
            else:
                raise ValueError('Unknown auto code')
        return self


class MainWordList(object):
    alphabet = alphabet

    def __init__(self, wordlist, words_inserted):
        self.wordlist = [word for j in wordlist for word in wordlist[j]]
        self.wordlist_arr = np.array([[i for i in j] for j in self.wordlist])
        self.word_values = {word: v for v in wordlist for word in wordlist[v]}
        self.num_to_word = {i: self.wordlist[i] for i in range(len(self.wordlist))}
        self.word_to_num = {self.wordlist[i]: i for i in range(len(self.wordlist))}
        self.nums_by_letter = []
        self.nums_by_letter_rev = []
        self.words_inserted = words_inserted

        for letter_idx in range(len(self.wordlist[0])):
            nums_by_ith_letter = {i: [] for i in self.alphabet}
            nums_by_ith_letter_rev = np.zeros(len(self.wordlist), int) - 1
            for wordlist_idx in range(len(self.wordlist)):
                nums_by_ith_letter_rev[wordlist_idx] = len(nums_by_ith_letter[self.wordlist[wordlist_idx][letter_idx]])
                nums_by_ith_letter[self.wordlist[wordlist_idx][letter_idx]].append(wordlist_idx)
            if not np.all(nums_by_ith_letter_rev >= 0):
                raise Exception('Word index not found in nums_by_ith_letter_rev')
            self.nums_by_letter.append({i: np.array(nums_by_ith_letter[i], int) for i in nums_by_ith_letter})
            self.nums_by_letter_rev.append(nums_by_ith_letter_rev)


class WordList(object):
    alphabet = alphabet

    def __init__(self, main_wordlist: MainWordList):
        self.main_wordlist = main_wordlist
        self.wordlist = main_wordlist.wordlist
        self.word_len = len(self.wordlist[0])
        self.wordlist_arr = main_wordlist.wordlist_arr
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

    def choice(self, auto=1, slots=None, word=''):
        by_value = defaultdict(list)
        word_nums = np.nonzero(self.wordnums < 0)[0]
        np.random.shuffle(word_nums)
        for word_num in word_nums:
            by_value[self.main_wordlist.word_values[self.wordlist[word_num]]].append(self.wordlist[word_num])
        if len(by_value.keys()) > 0:
            print('Next Word Value:', max(by_value.keys()))
        else:
            print('No words found!')
            if not auto:
                print('Would you like to delete the previous word? [Y/N]')
                res = input()
                if res not in ['N', 'n', 'NO', 'no', 'No']:
                    return None, -2
            else:
                return None, -2
        if auto == 1:
            word = choice(by_value[max(by_value.keys())])
            print(word)
            return word, -1
        elif auto == 0:
            possible_words = [j for i in sorted(list(by_value.keys()))[-1::-1] for j in by_value[i]]
            words_to_give = 10
            words_given = 0
            while True:
                if words_given < len(possible_words):
                    print(f'Here are {min(words_to_give, len(possible_words) - words_given)} '
                          f'{"more " if words_given > 0 else ""}words out of'
                          f' {len(possible_words)}: {", ".join(possible_words[words_given:words_to_give+words_given])}')
                else:
                    print('There are no more words on the wordlist.')
                print('To choose a word, type it. To see 10 more words, type m10. To delete your last word, type d. '
                      'To switch to a different slot number, type s[num]. To see the slot numbers, type c. '
                      'To try 5 words automatically, type a5. To quit, type q.')
                words_given += words_to_give
                try:
                    next_word = input()
                except EOFError:
                    next_word = 'w'
                if next_word in possible_words:
                    return next_word, -1
                elif next_word[0] == 'm':
                    try:
                        words_to_give = int(next_word[1:])
                    except ValueError:
                        print("I couldn't understand your response. Please try again.")
                elif next_word == 'd':
                    return None, -2
                elif next_word == 'c':
                    slots()
                elif next_word[0] == 's':
                    try:
                        new_slot_num = int(next_word[1:])
                        return None, new_slot_num
                    except ValueError:
                        print("I couldn't understand your response. Please try again.")
                elif next_word[0] == 'a':
                    try:
                        auto_words = int(next_word[1:])
                        return auto_words, -3
                    except ValueError:
                        print("I couldn't understand your response. Please try again.")
                elif next_word == 'q':
                    return None, -4
                elif len(next_word) == self.word_len and all(ord(i) < 97 or ord(i) > 122 for i in next_word):
                    print('This word is not in my wordlist. Would you like to use it anyway? [Y/N]')
                    res = input()
                    if res in ['Y', 'YES', 'Yes', 'yes', 'y']:
                        # print('Sorry, but at this time, I cannot accept words off the word list.')
                        return next_word, -1
                elif len(next_word) == self.word_len:
                    print("I couldn't understand your response. Remember: words must be provided in all caps.")
                else:
                    print("I couldn't understand your response. Please try again.")
        else:
            return word, -1

    def del_mult(self, del_word_nums):
        words = self.wordlist_arr[del_word_nums]
        for idx in range(words.shape[1]):
            for letter in self.word_by_letter[idx]:
                cur_vals = self.main_wordlist.nums_by_letter_rev[idx][del_word_nums[words[:, idx] == letter]]
                cur_negs = self.word_by_letter[idx][letter][cur_vals] == -1
                self.word_by_letter[idx][letter][cur_vals[cur_negs]] = self.main_wordlist.words_inserted[0]
        self.wordnums[del_word_nums[self.wordnums[del_word_nums] == -1]] = self.main_wordlist.words_inserted[0]

    def __len__(self):
        return len(self.wordlist)

    def __str__(self):
        return str([self[i] for i in np.nonzero(self.wordnums < 0)[0]])

    def delete_by_char(self, pos_in_word, deleted_char):
        still_possible = np.nonzero(self.word_by_letter[pos_in_word][deleted_char] < 0)[0]
        word_nums = self.main_wordlist.nums_by_letter[pos_in_word][deleted_char][still_possible]
        self.del_mult(word_nums)
        for pos in range(len(self.word_by_letter)):
            for letter in self.word_by_letter[pos]:
                if np.all(self.word_by_letter[pos][letter] >= 0) and letter in self.cell_list[pos][0].possible_chars() and (pos != pos_in_word or letter != deleted_char):
                    box, direction = (self.cell_list[pos][m] for m in range(2))
                    box.char_history[alphabet.index(letter)] = self.main_wordlist.words_inserted[0]
                    if not self.cell_list[pos][0].possible_chars():
                        return -1
                    res = 0
                    for k in range(2):
                        if k != direction or True:
                            res = box.wordlists[k].delete_by_char(box.crossword.wr1[k][box.row][box.col], letter)
                        if res == -1:
                            return -1
                    for k in box.wordlists[2]:
                        if type(direction) != tuple or direction[1] != k or True:
                            res = box.wordlists[2][k].delete_by_char(box.crossword.wr1[2][box.row][box.col][k], letter)
                        if res == -1:
                            return -1
        return 0

    def possible_word_equiv(self):
        word_sum = 0
        val_conv_chart = {'60': 100, '50': 50, '30': 25, '25': 20, '20': 15, '15': 5, '10': 2, '5': 1}
        len_conv_chart = {1: 100, 2: 100, 3: 10, 4: 10, 5: 15, 6: 25, 7: 35, 8: 50, 9: 75, 10: 100, 11: 100, 12: 100, 13: 100, 14: 100,
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
        self.wordlists.append({i: self.crossword.full_word_list[i] for i in self.crossword.clue_num_list[2][self.row][self.col]})
        for i in self.wordlists[2]:
            self.wordlists[2][i].cell_list[self.crossword.wr1[2][self.row][self.col][i]] = [self, (2, i)]

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

fri_boxes0 = '''
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

wed_boxes0 = '''
....x......x...
....x......x...
...........x...
x....xxx.......
...............
....x.....x....
...x....xx....x
xxx.........xxx
x....xx....x...
....x.....x....
...............
.......xxx....x
...x...........
...x......x....
...x......x....
'''

mon_boxes0 = '''
....x.....x....
....x.....x....
..........x....
.......xx......
xxx...x.....xxx
.....x...x.....
....x..........
...x.......x...
..........x....
.....x...x.....
xxx.....x...xxx
......xx.......
....x..........
....x.....x....
....x.....x....
'''

special1 = '''
.....x.....
.....x.....
.....x.....
.......x...
xxx...x....
....x...xxx
...x.......
.....x.....
.....x.....
.....x.....
'''

special2 = '''
.....x....x.....
.....x....x.....
.....x....x.....
x......xx......x
...x........x...
....x......x....
.....x....x.....
......xxxx......
xxx..........xxx
....x......x....
...xx......xx...
.......xx.......
.....x....x.....
.....x....x.....
.....x....x.....
'''

special0 = '''
.......xx......
.......xx......
........x......
....x.....x....
xxxx......x....
.....x...x.....
........x...xxx
.......x.......
xxx...x........
.....x...x.....
....x......xxxx
....x.....xx...
......x........
......xx.......
......xx.......
'''

special0 = '''
....x...xx.....
....x...x......
........x......
x.....x...xx...
xxx...x........
......xx.......
...xx.......xxx
.....x...x.....
xxx.......xx...
.......xx......
........x...xxx
...xx...x.....x
......x........
......x...x....
.....xx...x....
'''

special = '''
......xx.......
.......x.......
.......x.......
.....x.....xxxx
xxx...x........
xx........x....
x.........x....
...xxx...xxx...
....x.........x
....x........xx
........x...xxx
xxxx.....x.....
.......x.......
.......x.......
.......xx......
'''

special = '''
.....xx....x...
......x....x...
......x....x...
x...x....x.....
...x......x....
.......xx......
.....x......xxx
x.............x
xxx......x.....
......xx.......
....x......x...
.....x....x...x
...x....x......
...x....x......
...x....xx.....
'''

special = '''
.......xx......
........x......
........x......
.....x....x....
xxx...xx.......
.........x...xx
....x...x......
...x.......x...
......x...x....
xx...x.........
.......xx...xxx
....x....x.....
......x........
......x........
......xx.......
'''

special = '''
xx...
x....
.....
....x
...xx
'''

special='''
....x.....x....
....x.....x....
....x..........
IAMSAMSAMIAMxxx
.....x...x.....
xxx....x..A....
x.....x...xx...
xCALLMEISHMAELx
...xx...x.....x
.......x....xxx
.....x...x.....
xxxMYNAMEISEARL
..........x....
....x.....x....
....x.....x....
'''
special = '\n'+open('grid.txt').read()+'\n'

mini = '''
'''

# boxes = [[k, i] for i, j in enumerate(wed_boxes0.split('\n')[1:-1]) for k, k1 in enumerate(j) if k1 == 'x']
# print(boxes)

# cw1 = CM(15, 15, mon_boxes0)
h, w = len(special.split('\n')) - 2, len(special.split('\n')[1])
# themers = ['LORO', 'STANFORD', 'GAVILAN', 'MIRLO', 'FLOMO', 'ALONDRA', 'FAISAN', 'CARDENAL', 'DORM', 'RESX']
poss = ['ELEPHANT','STRIDENT','APPARENT','INCIDENT','ONSILENT']
themers = [i[j::2] for j in (0,1) for i in poss]
themers = [i for i in 'QWERTYUIOPASDFGHJKLZXCVBNM']
custom_words = [[(i, j-i) for i in range(max(0, j-4), min(5, j+1))] for j in range(2,7)] + [[(i,j)] for i in range(5) for j in range(5) if 2 <= i+j <= 6]
# custom_words = [[(i, i) for i in range(15)]] + [[(i,j)] for i in range(15) for j in range(15)]
# print(custom_words)
cw1 = CM(h, w, special, themers, custom_words=[])
# cw1 = CM(3, 4, mini)
# print(cw1)
print(cw1.fill_puzzle(auto=0))
