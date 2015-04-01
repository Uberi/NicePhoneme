#!/usr/bin/env bash

NAME="Anthony Zhang"

echo "GENERATING..."
python3 markov_generate.py "$NAME" < data/normalized_data.json > "data/results-$NAME.txt"
echo "DONE: results saved to \"data/results-$NAME.txt\""
