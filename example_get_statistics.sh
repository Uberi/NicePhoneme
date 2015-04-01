#!/usr/bin/env bash

echo "GENERATING..."
python3 statistics.py < data/normalized_data.json > data/statistics-summary.txt
echo "DONE: results saved to \"data/statistics-summary.txt\""
