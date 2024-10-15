import logging
import random
from io import BytesIO
import urllib.request

from PIL import Image, ImageDraw, ImageFont


class WordSearch:
    def __init__(self, size=32, words=["CAT", "DOG", "GOD"]):
        # TODO: Have a separate list of allowed characters
        self.words = words
        self.size = size

    def create(self):
        allowed_characters = list(set([char for word in self.words for char in word]))

        word_search = [["" for _ in range(self.size)] for _ in range(self.size)]

        for word in self.words:
            self._add_word(word_search, word)

        for y in range(len(word_search)):
            for x in range(len(word_search[y])):

                if word_search[y][x]:
                    continue

                candidate = None

                retries = 0
                max_retries = 50
                success = None

                while retries < max_retries and not success:
                    retries += 1
                    candidate = random.choice(allowed_characters)
                    success = self._check(word_search, x, y, candidate)

                if success:
                    word_search[y][x] = candidate
                else:
                    raise ValueError(f"Couldn't find a way to add another letter in {max_retries} tries: {word_search}")

        return word_search

    def _add_word(self, word_search, word):
        '''
        Add a word to the word search.

        The current approach is very nieve and doesn't try to do any calculations. This would need to become more
        complicated to handle dense puzzles.
        :param word_search:
        :param word:
        :return:
        '''

        steps = [(1, 0),  # left->right
                 (0, 1),  # up->down
                 (1, 1),  # Descending diagonal
                 (1, -1),  # Ascending diagonal
                 (-1, 0),  # right->left
                 (0, -1),  # down->up
                 (-1, 1),  # Reverse ascending diagonal
                 (-1, -1),  # Reverse descending diagonal
                 ]

        directions = random.choices(
            steps,
            weights=(100, 100, 75, 25, 10, 10, 5, 5),  # Some directions are less fun than others. Very scientific here.
            k=50)

        h = len(word_search)
        w = len(word_search[0])

        word_added = False
        for x_direction, y_direction in directions:
            # I could be smarter here about if the select coords will work and early return
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)

            positions = []
            for i, letter in enumerate(word):
                letter_x = x + (x_direction * i)
                letter_y = y + (y_direction * i)

                if(letter_x < 0 or w - 1 < letter_x) or (letter_y < 0 or h - 1 < letter_y) or not self._check(word_search, letter_x, letter_y, letter):
                    # logging.debug(f'{letter_x} > {w} || {letter_y} > {h}')
                    positions = []
                    break
                positions.append((letter_x, letter_y, letter))

            if positions:
                for x, y, char in positions:
                    word_search[y][x] = char
                    word_added = True
                break
        if not word_added:
            puzzle_repr = '\n'.join([' '.join(row) for row in word_search])
            raise ValueError(f"Couldn't add '{word}' to the puzzle.\n{puzzle_repr}")

    def _check(self, word_search, x, y, candidate):
        # TODO: If the word_search can arbitrarily have words (not added by top to right to down)
        # I need to check by shifting around the point by all the word sizes that would fit.
        # e.g. with 4 char word . . . x . . . could all be potential matches (including some to the right and some left)

        row = word_search[y]

        if row[x]:
            # If we're trying to add the same letter where it already exists, we're good
            if row[x] is candidate:
                return True
            else:
                return False

        for word in self.words:
            # Left & Reversed
            if len(word) <= x + 1: # The word could fit to the left
                left = ''.join(row[x + 1 - len(word):x])
                if left + candidate == word or left + candidate == ''.join(reversed(word)):
                    logging.debug(f'{left} and {candidate} would have caused a match on the left with {word} at {x},{y}')
                    return False

            # Top & Reversed
            if y >= len(word) - 1: # The word could fit above
                t_indx = y + 1 - len(word)
                col = ''.join([row[x] for row in word_search[t_indx:y]])
                if col + candidate == word or col + candidate == ''.join(reversed(word)):
                    logging.debug(f'{col} and {candidate} would have caused a match above with {word} at {x},{y}')
                    return False

            # Descending Diagonal & Reversed
            if len(word) <= x + 1 and len(word) <= y + 1: # The word could fit diagonally descending
                upper_y_indx = y + 1 - len(word)
                upper_x_indx = x + 1 - len(word)
                desc_diag = ''.join([word_search[upper_y_indx+i][upper_x_indx+i] for i in range(len(word) - 1)])
                # logging.debug(f'{x},{y} - {desc_diag}')
                if desc_diag + candidate == word or desc_diag + candidate == ''.join(reversed(word)):
                    logging.debug(f'{desc_diag} and {candidate} would have caused a match on a descending diagonal with {word} at {x},{y}')
                    return False

            # # Ascending Diagonal & Reversed
            if x + len(word) <= len(row) and y + 1 - len(word) >= 0:
                asc_diag = ''.join([word_search[y-i][x+i] for i in range(1, len(word))])
                # logging.debug(f'{x},{y} = {asc_diag}')
                if candidate + asc_diag == word or candidate + asc_diag == ''.join(reversed(word)):
                    logging.debug(f'{candidate} and {asc_diag} would have caused a match on a ascending diagonal with {word} at {x},{y}')
                    return False
        return True

def build_image(word_search):
    font_url = 'https://github.com/google/fonts/blob/main/ofl/courierprime/CourierPrime-Regular.ttf?raw=true'
    font = ImageFont.truetype(BytesIO(urllib.request.urlopen(font_url).read()), 40)

    text = '\n'.join([' '.join(row) for row in word_search])
    left, top, right, bottom = ImageDraw.Draw(Image.new("RGB", (0, 0), (255, 255, 255))).multiline_textbbox((0, 0), text, font)

    img = Image.new("RGB", (right, bottom), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.multiline_text((-left / 2, -top / 2), text, font=font, fill=(0, 0, 0))
    # TODO Add solution
    ## It would be really helpful to have a solution to the puzzle that could be printed.

    return img

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    ws = WordSearch()

    word_search = ws.create()

    image = build_image(word_search)

    image.save('texting.png')

    print('\n'.join([' '.join(row) for row in word_search]))
