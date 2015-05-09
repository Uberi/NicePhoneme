#!/usr/bin/env python3

import json, sys

messages = json.load(sys.stdin)

# sort by timestamp, format entries on line, and sort keys in each entry
messages = sorted(messages, key=lambda message: message["timestamp"])
result = "[\n" + ",\n".join(json.dumps(entry, sort_keys=True) for entry in messages) + "\n]\n"

sys.stdout.write(result)
