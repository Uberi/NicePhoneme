#!/usr/bin/env python3

import json, sys, re
import random
from collections import defaultdict

def main():
    user = sys.argv[1] if len(sys.argv) > 1 else None
    data = json.load(sys.stdin)

    markov = Markov(2)
    if user is None:
        for message in Markov.tokenize_words([m[2] for m in data]):
            markov.train(message)
    else:
        for message in Markov.tokenize_words([m[2] for m in data if m[1] == user]):
            markov.train(message)

    #entries = open("Snow_Crash.txt", "rb").read().decode("UTF-8").split("\n")
    #matcher = re.compile(Markov.PATTERN, re.IGNORECASE)
    #for message in (matcher.findall(m) for m in entries):
        #markov.train([m.lower() for m in message])

    result = "\n".join(markov.speak() for i in range(5000))
    sys.stdout.write(string_normalize(result))

class Markov:
    PUNCTUATION = r"[`~@#$%_\\'+\-/]" # punctuation that is a part of text
    STANDALONE = r"(?:[!.,;()^&\[\]{}|*=<>?]|[dDpP][:8]|:\S)" # standalone characters or emoticons that wouldn't otherwise be captured
    PATTERN = STANDALONE + r"\S*|https?://\S+|(?:\w|" + PUNCTUATION + r")+" # token pattern
    word_matcher = re.compile(PATTERN, re.IGNORECASE)

    def __init__(self, lookbehind_length = 2):
        self.lookbehind_length = lookbehind_length

        self.chain = defaultdict(lambda: defaultdict(int))
        self.counts = defaultdict(int)

    @staticmethod
    def tokenize_words(data):
        return ([m.lower() for m in Markov.word_matcher.findall(entry)] for entry in data)

    def train(self, message, importance = 1):
        # find word chain counts as a dictionary mapping words to dictionaries mapping words to amount of times they appear after the first word
        current_key = ()
        for i, m in enumerate(message): # loop through every index except the highest one
            self.chain[current_key][m] += importance # update the Markov chain with current word
            self.counts[current_key] += importance
            
            if i < self.lookbehind_length: current_key += (m,) # add current word to key if just starting
            else: current_key = current_key[1:] + (m,) # shift word onto key if inside message

        self.chain[current_key][None] += importance # update the Markov chain with end of message
        self.counts[current_key] += importance

    def speak(self):
        if len(self.counts) == 0: raise ValueError("Markov model is not trained yet")
        
        # generate a message based on probability chains
        choices = self.chain[()] # choices at the start of a string
        phrase_list = []
        current_key = ()
        while True:
            # pick a random word weighted on the number of times it has occurred previously
            random_choice = random.randrange(0, self.counts[current_key])
            for current_choice, occurrences in choices.items():
                random_choice -= occurrences
                if random_choice < 0:
                    new_word = current_choice
                    break
            else: # couldn't find the choice somehow
                raise Exception("Bad choice!") # this should never happen but would otherwise be hard to detect if it did

            # add the word to the message
            if new_word == None: break
            phrase_list.append(new_word)

            if len(current_key) < self.lookbehind_length: current_key += (new_word,) # add current word to key if just starting
            else: current_key = current_key[1:] + (new_word,) # shift word onto key if inside message

            choices = self.chain[current_key]

        # format the sentence into a human-readable string
        close_matcher = re.compile("[!.,;:)\]}?]", re.IGNORECASE)
        phrase = ""
        for i, v in enumerate(phrase_list):
            if i == 0 or close_matcher.match(v): phrase += v
            else: phrase += " " + v
        
        return phrase

def string_normalize(value):
    return value.encode("UTF-8", errors="replace").decode("UTF-8")

if __name__ == "__main__": main()