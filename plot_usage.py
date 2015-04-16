#!/usr/bin/env python3

import json, sys, collections
from datetime import datetime

import matplotlib.pyplot as plt

data = json.load(sys.stdin)

BUCKET_COUNT = 10000
SMOOTH_WINDOW_EXTENT = 400

start_time, end_time = data[0][0], data[-1][0]
buckets = [0] * BUCKET_COUNT
bucket_size = ((end_time + 1) - start_time) / BUCKET_COUNT # add 1 to end time to make sure the last message doesn't go out of bounds

start_offset = int(start_time // bucket_size)
previous_user = None
for entry in data:
    # skip duplicate messages
    if entry[1] == previous_user: continue
    previous_user = entry[1]
    
    buckets[int((entry[0] - start_time) // bucket_size)] += 1

times = [datetime.fromtimestamp((start_time + i * bucket_size) / 1000) for i in range(BUCKET_COUNT)]

fig, axes = plt.subplots()
axes.plot(times, buckets)

# apply smoothing
window_size = SMOOTH_WINDOW_EXTENT * 2 + 1
previous_buckets = collections.deque(buckets[:SMOOTH_WINDOW_EXTENT + 1], maxlen=window_size)
rolling_sum = sum(buckets[:SMOOTH_WINDOW_EXTENT + 1])
smoothed = []
for i in range(len(buckets)):
    index = i + SMOOTH_WINDOW_EXTENT
    if len(previous_buckets) == previous_buckets.maxlen: rolling_sum -= previous_buckets[0] # item on the end is getting removed, remove it from the average
    if index < len(buckets):
        rolling_sum += buckets[index]
        previous_buckets.append(buckets[index])
    
    smoothed.append(rolling_sum / window_size)
axes.plot(times, smoothed, linewidth=2)

axes.set_xlim(times[0], times[-1])
fig.autofmt_xdate()
axes.set_ylabel("Unique user message frequency")
axes.set_title("Facebook chat activity over time")

#plt.savefig("usage.png", format="png", dpi=800)

plt.show()
