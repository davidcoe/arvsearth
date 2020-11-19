import logging
import random

from PIL import Image, ImageDraw, ImageFont


class WordSearch:
    def __init__(self, size=10, word="arveth"):
        # TODO: Support a list of words
        # TODO: Have a separate list of allowed characters
        self.word = word
        self.size = size

    def create(self):
        word_search = [[None for _ in range(self.size)] for _ in range(self.size)]

        for y in range(len(word_search)):
            for x in range(len(word_search[y])):
                # TODO: Support word searches where the words to find are already added.
                # if word_search[y][x] is not None:
                #     continue

                candidate = None

                retries = 0
                max_retries = 50
                success = None

                while retries < max_retries and not success:
                    retries += 1
                    candidate = random.choice(self.word)
                    success = self._check(word_search, x, y, candidate)

                if success:
                    word_search[y][x] = candidate
                else:
                    raise ValueError(f"Couldn't find a way to add another letter in {max_retries} tries: {word_search}")

        return word_search

    def _check(self, word_search, x, y, candidate):
        # TODO: If the word_search can arbitrarily have words (not added by top to right to down)
        # I need to check by shifting around the point by all the word sizes that would fit.
        # e.g. with 4 char word . . . x . . . could all be potential matches (including some to the right and some left)

        row = word_search[y]

        # Left & Reversed
        if len(self.word) <= x + 1: # The word could fit to the left
            left = ''.join(row[x + 1 - len(self.word):x])
            if left + candidate == self.word or left + candidate == ''.join(reversed(self.word)):
                logging.debug(f'{left} and {candidate} would have caused a match on the left with {self.word} at {x},{y}')
                return False

        # Top & Reversed
        if y >= len(self.word) - 1: # The word could fit above
            t_indx = y + 1 - len(self.word)
            col = ''.join([row[x] for row in word_search[t_indx:y]])
            if col + candidate == self.word or col + candidate == ''.join(reversed(self.word)):
                logging.debug(f'{col} and {candidate} would have caused a match above with {self.word} at {x},{y}')
                return False

        # Descending Diagonal & Reversed
        if len(self.word) <= x + 1 and len(self.word) <= y + 1: # The word could fit diagonally descending
            upper_y_indx = y + 1 - len(self.word)
            upper_x_indx = x + 1 - len(self.word)
            desc_diag = ''.join([word_search[upper_y_indx+i][upper_x_indx+i] for i in range(len(self.word) - 1)])
            # logging.debug(f'{x},{y} - {desc_diag}')
            if desc_diag + candidate == self.word or desc_diag + candidate == ''.join(reversed(self.word)):
                logging.debug(f'{desc_diag} and {candidate} would have caused a match on a descending diagonal with {self.word} at {x},{y}')
                return False

        # # Ascending Diagonal & Reversed
        if x + len(self.word) <= len(row) and y + 1 - len(self.word) >= 0:
            asc_diag = ''.join([word_search[y-i][x+i] for i in range(1, len(self.word))])
            # logging.debug(f'{x},{y} = {asc_diag}')
            if candidate + asc_diag == self.word or candidate + asc_diag == ''.join(reversed(self.word)):
                logging.debug(f'{candidate} and {asc_diag} would have caused a match on a ascending diagonal with {self.word} at {x},{y}')
                return False
        return True

def build_image(word_search):
    # TODO: This is obviously not going to work on multiple systems. Can I distribute this?
    font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf", 40)
    text = '\n'.join([' '.join(row) for row in word_search])
    w, h = font.getsize_multiline(text)

    image = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font)
    draw.multiline_text((-left / 2, -top / 2), text, font=font, fill=(0, 0, 0))

    return image

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws = WordSearch()

    word_search = ws.create()

    image = build_image(word_search)

    image.save('texting.png')

    print('\n'.join([' '.join(row) for row in word_search]))
