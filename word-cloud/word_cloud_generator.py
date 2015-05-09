#!/usr/bin/env python3

import os, json, sys
from scipy import misc

from wordcloud import WordCloud, STOPWORDS

FILE_DIR = os.path.dirname(__file__)
user = "Anthony Zhang"
name = "and"
ignored_words = STOPWORDS

# load message text
messages = json.load(sys.stdin)
text = "\n".join(m[2] for m in messages) if user is None else "\n".join(m[2] for m in messages if m[1] == user)

# generate word cloud
mask = misc.imread(os.path.join(FILE_DIR, "mask-{}.png").format(name))
wc = WordCloud(background_color="white", max_words=10000, mask=mask, stopwords=ignored_words, scale=4)
wc.generate(text)

# store the word cloud image in a file
wc.to_file(os.path.join(FILE_DIR, "word-cloud-{}.png".format(name)))
