#!/usr/bin/env bash

echo "GENERATING..."
python3 normalize_data.py < data/downloaded.json > data/normalized_data.json
echo "DONE: results saved to \"data/normalized_data.json\""
