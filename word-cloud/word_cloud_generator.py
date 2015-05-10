#!/usr/bin/env python3

import os, json, sys, re
from scipy import misc

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator, random_color_func

# process arguments
if not (4 <= len(sys.argv) <= 5):
    print("Usage: {} USER_REGEX OUTPUT_PNG_FILE MASK_IMAGE [COLOR_IMAGE] < NORMALIZED_DATA_JSON".format(sys.argv[0]))
    sys.exit(1)
user_regex = sys.argv[1]
output_png = sys.argv[2]
mask_image = sys.argv[3]
color_image = None if len(sys.argv) < 5 else sys.argv[4]

ignored_words = STOPWORDS

# load message text
messages = json.load(sys.stdin)
pattern = re.compile(user_regex)
text = "\n".join(m[2] for m in messages if pattern.fullmatch(m[1]))

# generate word cloud
mask = misc.imread(mask_image)
coloring_function = ImageColorGenerator(misc.imread(color_image)) if color_image is not None else random_color_func
wc = WordCloud(background_color="white", max_words=10000, mask=mask, stopwords=ignored_words, scale=4, color_func=coloring_function)
wc.generate(text)

# save the word cloud image to stdout
wc.to_file(output_png)
