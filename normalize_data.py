#!/usr/bin/env python3

from urllib.parse import urlparse, parse_qs
import json, sys

users = {
    "fbid:100001608518631": "Anthony Zhang",
    # ADD MORE USERS HERE AS NECESSARY - map Facebook user IDs to names (find users by ID at `http://graph.facebook.com/<ID_GOES_HERE>`, like `http://graph.facebook.com/100001608518631`)
}

def get_attachments(attachments):
    result = []
    for attach in attachments:
        if not isinstance(attach, dict): continue
        url = attach["url"]
        if attach["attach_type"] == "photo": # replace photo preview with actual photo
            if "hires_url" in attach: # photo is directly available
                url = attach["hires_url"]
            elif url.startswith("/ajax/mercury/attachments/photo/view"):
                url = parse_qs(urlparse(url).query)["uri"][0]
        elif url.startswith("/"): # fix absolute URLs with the hostname
            url = "https://facebook.com" + url
        result.append(attach["attach_type"] + ":" + url)
    return result

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
        entry["timestamp"], # unix millisecond timestamp
        get_user(entry["author"]), # message author
        get_body(entry), # message value
        get_attachments(entry["attachments"]) if "attachments" in entry else [], # attachments
        entry["coordinates"] if "coordinates" in entry else None, # GPS coordinates
    ]
    return json.dumps(result)

data = json.load(sys.stdin)
data = sorted(data, key=lambda entry: entry["timestamp"])

# output the normalized message data
messages = [get_entry(entry) for entry in data]
sys.stdout.write("[\n" + ",\n".join(messages) + "\n]\n")
