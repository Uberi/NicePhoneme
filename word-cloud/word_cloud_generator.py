#!/usr/bin/env python3

import os, json, sys
from scipy import misc

from wordcloud import WordCloud, STOPWORDS

if not (3 <= len(sys.argv) <= 4):
    print("Usage: {} MASK OUTPUT_FILE [USER_FILTER] < NORMALIZED_DATA".format(sys.argv[0]))
    sys.exit(1)

mask_file = sys.argv[1]
output_file = sys.argv[2]
user = sys.argv[3] if len(sys.argv) >= 4 else None
ignored_words = STOPWORDS

# load message text
messages = json.load(sys.stdin)
text = "\n".join(m[2] for m in messages) if user is None else "\n".join(m[2] for m in messages if m[1] == user)

# generate word cloud
mask = misc.imread(mask_file)
wc = WordCloud(background_color="white", max_words=10000, mask=mask, stopwords=ignored_words, scale=4)
wc.generate(text)

# store the word cloud image in a file
wc.to_file(output_file)
