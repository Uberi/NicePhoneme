#!/usr/bin/env bash

echo "GENERATING..."
python3 plot_usage.py < data/normalized_data.json
echo "DONE"
