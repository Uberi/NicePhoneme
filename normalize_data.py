#!/usr/bin/env python3

from urllib.parse import urlparse, parse_qs
import json, sys

users = {
    "fbid:100001608518631": "Anthony Zhang",
    # ADD MORE USERS HERE AS NECESSARY - map the Facebook user ID to human-readable names
}

def get_attachment(attach):
    url = attach["url"]
    if url.startswith("/ajax/mercury/attachments/photo/view"):
        url = parse_qs(urlparse(url).query)["uri"][0]
    elif url.startswith("/"):
        url = "https://facebook.com" + url
    return [attach["attach_type"] + ":" + url]

def get_body(entry):
    if "body" in entry:
        return entry["body"]
    elif "log_message_body" in entry:
        return entry["log_message_body"]
    else:
        raise Exception("Bad entry:\n" + str(entry))

def get_user(author):
    if author not in users:
        sys.stderr.write("UNKNOWN AUTHOR \"{}\"\n".format(author))
        return author
    return users[author]

def get_entry(entry):
    result = [
        entry["timestamp"], # unix timestamp
        get_user(entry["author"]), # message author
        get_body(entry), # message value
        [get_attachment(attach) for attach in entry["attachments"] if isinstance(attach, dict)] if "attachments" in entry else [],
    ]
    #if "coordinates" in entry: # GPS coordinates
        #result.append(entry["coordinates"])
    return json.dumps(result)

data = json.load(sys.stdin)
data = sorted(data, key=lambda entry: entry["timestamp"])

# output the normalized message data
messages = [get_entry(entry) for entry in data]
sys.stdout.write("[\n" + ",\n".join(messages) + "\n]\n")
