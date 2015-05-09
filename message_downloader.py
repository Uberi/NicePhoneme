#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.parse, urllib.request
import gzip, os, sys, io, json, time, re
from datetime import datetime

# request data
request_info = """
:host:www.facebook.com
:method:POST
:path:/ajax/mercury/thread_info.php
:scheme:https
:version:HTTP/1.1
accept:*/*
accept-encoding:gzip, deflate
accept-language:en-US,en;q=0.8
content-length:316
content-type:application/x-www-form-urlencoded
cookie:STUFF
dnt:1
origin:https://www.facebook.com
referer:https://www.facebook.com/messages/STUFF
user-agent:STUFF
Form Data
view source
view URL encoded
messages[STUFF][STUFF][offset]:21
messages[STUFF][STUFF][limit]:20
:
client:web_messenger
__user:STUFF
__a:STUFF
__dyn:STUFF
__req:STUFF
fb_dtsg:STUFF
ttstamp:STUFF
__rev:STUFF
Name
Path
RANDOM OTHER STUFF HERE
"""

# session options
message_offset = 0
if len(sys.argv) > 1:
    try: message_offset = int(sys.argv[1], 0)
    except ValueError:
        print("Invalid message offset - message offset must be an integer", file=sys.stderr)
        sys.exit(1)

# find the conversation form data prefix
match = re.search(r"^messages\[thread_fbids\]\[([^\]]+)\]", request_info, re.MULTILINE)
if match is None: # not a group message, probably a personal conversation
    match = re.search(r"^messages\[user_ids\]\[([^\]]+)\]", request_info, re.MULTILINE)
    assert match is not None, "Conversation/user ID not found"
MESSAGE_FIELD_PREFIX = match.group(0)

# find the request variables in the request data
match = re.search(r"^cookie:(.*)", request_info, re.MULTILINE)
assert match is not None, "Cookie not found"
REQUEST_COOKIE = match.group(1)
match = re.search(r"^__user:(.*)", request_info, re.MULTILINE)
assert match is not None, "User ID not found"
REQUEST_USER = match.group(1)
match = re.search(r"^__a:(.*)", request_info, re.MULTILINE)
assert match is not None, "Request __a value not found"
REQUEST_A = match.group(1)
match = re.search(r"^__dyn:(.*)", request_info, re.MULTILINE)
assert match is not None, "Request __dyn value not found"
REQUEST_DYN = match.group(1)
match = re.search(r"^__req:(.*)", request_info, re.MULTILINE)
assert match is not None, "Request __req value not found"
REQUEST_REQ = match.group(1)
match = re.search(r"^fb_dtsg:(.*)", request_info, re.MULTILINE)
assert match is not None, "Request fb_dtsg value not found"
REQUEST_FB_DTSG = match.group(1)
match = re.search(r"^ttstamp:(.*)", request_info, re.MULTILINE)
assert match is not None, "Request ttstamp value not found"
REQUEST_TTSTAMP = match.group(1)
match = re.search(r"^__rev:(.*)", request_info, re.MULTILINE)
assert match is not None, "Request __rev value not found"
REQUEST_REV = match.group(1)

def get_messages(message_offset = 0, messages_per_request = 2000):
    headers = {
        "origin": "https://www.facebook.com",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.8",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": REQUEST_COOKIE,
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36",
        "accept": "*/*",
        "dnt": "1",
        "referer": "https://www.facebook.com/messages/",
    }
    try:
        while True:
            print("Getting messages {}-{}".format(message_offset, messages_per_request + message_offset), file=sys.stderr)
            
            form_data = urllib.parse.urlencode({
                MESSAGE_FIELD_PREFIX + "[offset]": str(message_offset), 
                MESSAGE_FIELD_PREFIX + "[limit]": str(messages_per_request), 
                "client": "web_messenger",
                "__user": REQUEST_USER,
                "__a": REQUEST_A,
                "__dyn": REQUEST_DYN,
                "__req": REQUEST_REQ,
                "fb_dtsg": REQUEST_FB_DTSG,
                "ttstamp": REQUEST_TTSTAMP,
                "__rev": REQUEST_REV,
            }).encode("UTF-8")
            request = urllib.request.Request("https://www.facebook.com/ajax/mercury/thread_info.php", form_data, headers)
            response_value = urllib.request.urlopen(request).read() # read the GZIP-compressed response value
            messages_data = gzip.GzipFile(fileobj=io.BytesIO(response_value)).read().decode("UTF-8") # GZIP-decompress the response value
            
            messages_data = messages_data[9:] # remove the weird code header at the beginning
            if "\"payload\":{\"end_of_history\"" in messages_data: # end of history, stop downloading
                break
            try:
                json_data = json.loads(messages_data)
                current_messages = json_data["payload"]["actions"] # messages sorted ascending by timestamp
                latest_message_time = datetime.fromtimestamp(current_messages[-1]["timestamp"] / 1000).strftime("%c")
                print("Oldest encountered message timestamp:", latest_message_time, file=sys.stderr)
                yield list(reversed(current_messages))
            except:
                print("Error retrieving messages. Retrying in 20 seconds. Data:", file=sys.stderr)
                print(messages_data, file=sys.stderr)
                time.sleep(20)
                continue
            message_offset += messages_per_request
            time.sleep(5)
    except KeyboardInterrupt: pass # stop when user interrupts the download

if __name__ == "__main__":
    sys.stdout.write("[\n")
    try:
        first = True
        for chunk in get_messages(message_offset):
            for message in chunk:
                if first: first = False
                else: sys.stdout.write(",\n")
                sys.stdout.write(json.dumps(message, sort_keys=True))
    except KeyboardInterrupt: pass # keyboard interrupt received, close brackets in JSON output
    sys.stdout.write("\n]")
