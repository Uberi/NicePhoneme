#!/usr/bin/env python3

import json, sys, re
from collections import defaultdict

data = json.load(sys.stdin)

def string_normalize(value):
    return value.encode("UTF-8", errors="replace").decode("UTF-8")

user_characters = defaultdict(int)
user_messages = defaultdict(int)
for entry in data:
    user_characters[entry[1]] += len(entry[2])
    user_messages[entry[1]] += 1

print("Characters typed by user, highest first:")
print("\n".join([k + ":\t" + str(v) for k, v in sorted(dict(user_characters).items(), key=lambda x: -x[1])]) + "\n")
print("Number of messages by user, highest first:")
print("\n".join([k + ":\t" + str(v) for k, v in sorted(dict(user_messages).items(), key=lambda x: -x[1])]) + "\n")

print("Average characters per message by user, highest first:")
user_average_chars = {}
for k, v in user_characters.items(): user_average_chars[k] = v / user_messages[k]
print("\n".join([k + ":\t" + str(v) for k, v in sorted(dict(user_average_chars).items(), key=lambda x: -x[1])]) + "\n")

# get expletive frequencies
words = defaultdict(int)
for entry in data:
    for word in entry[2].split():
        if "shit" in word or "piss" in word or "fuck" in word or "cunt" in word or "cocksucker" in word or "motherfucker" in word or "tits" in word:
            words[entry[1]] += 1
frequencies = sorted([(k, v / user_messages[k]) for k, v in words.items()], key=lambda x: -x[1])
result = "\n".join([k + ":\t" + str(v) for k, v in frequencies])
print("Expletives per message:\n" + result + "\n")

# get pls frequencies
pattern = re.compile(r"^p+[l\|]+s+|psl|lsp|slp|spl$", re.IGNORECASE)
words = defaultdict(int)
for entry in data:
    for word in entry[2].split():
        if pattern.match(word):
            words[entry[1]] += 1
frequencies = sorted(words.items(), key=lambda x: -x[1])
result = "\n".join([k + ":\t" + str(v) for k, v in frequencies])
print("\"pls\" count:\n" + result + "\n")

# get smiley frequencies
pattern = re.compile(":\)|:D|:\(|:/|:O|:\$")
words = defaultdict(int)
for entry in data:
    for word in entry[2].split():
        if pattern.match(word):
            words[entry[1]] += 1
frequencies = sorted(words.items(), key=lambda x: -x[1])
result = "\n".join([k + ":\t" + str(v) for k, v in frequencies])
print("Smilies per user:\n" + result + "\n")

# get sentiments
try:
    from textblob import TextBlob
    users = defaultdict(float)
    for entry in data:
        sentiment = TextBlob(entry[2]).sentiment
        users[entry[1]] += sentiment.polarity * (1 - sentiment.subjectivity)
    sentiments = sorted([(k, v / user_messages[k]) for k, v in users.items()], key=lambda x: -x[1])
    result = "\n".join([k + ":\t" + str(v) for k, v in sentiments])
    print("User positivity:\n" + result + "\n")
except ImportError: pass # ignore this if TextBlob isn't installed

# get word frequencies
words = defaultdict(int)
for entry in data:
    for word in entry[2].split():
        words[word.lower()] += 1
frequencies = sorted(words.items(), key=lambda x: -x[1])
result = "\n".join([k + ":\t" + str(v) for k, v in frequencies])
print("Word frequencies:\n" + string_normalize(result) + "\n")
