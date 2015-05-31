#!/usr/bin/env python3

from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
import json, sys

user_aliases = {
    "fbid:100001608518631": "Anthony Zhang",
    "Mr. RealPerson": "Mr. RealPerson's Nickname",
    # ADD MORE USERS HERE AS NECESSARY (OPTIONAL)
    # map Facebook user IDs to names, or names to other names
    # you can find users by ID at `http://graph.facebook.com/<ID_GOES_HERE>`, like `http://graph.facebook.com/100001608518631`)
}

def get_user(user_identifier):
    if user_identifier in user_aliases: return user_aliases[user_identifier] # explicit user ID alias
    if user_identifier.startswith("fbid:"): # facebook ID, look up using the Facebook Graph API
        try:
            response_text = urlopen("http://graph.facebook.com/{}".format(user_identifier[5:])).read().decode("UTF-8")
            name = json.loads(response_text)["name"]
            if name in user_aliases: name = user_aliases[name] # explicit user name alias
            print("SUCCESSFULLY RETRIEVED NAME FOR USER \"{}\": {}".format(user_identifier, name), file=sys.stderr)
            user_aliases[user_identifier] = name # cache the proper name of the user
            return name
        except Exception as e:
            print("COULD NOT GET NAME FOR USER \"{}\": {}".format(user_identifier, e), file=sys.stderr)
    return user_identifier # other type of Facebook identifier, just return it verbatim

def get_attachments(entry):
    result = []
    if "coordinates" in entry and entry["coordinates"] is not None:
        coordinate = entry["coordinates"]
        if "accuracy" in coordinate: result.append("location:{},{} ~{}m".format(coordinate["latitude"], coordinate["longitude"], coordinate["accuracy"]))
        else: result.append("location:{},{}".format(coordinate["latitude"], coordinate["longitude"]))
    if "attachments" in entry:
        for attach in entry["attachments"]:
            if not isinstance(attach, dict): continue
            if attach["attach_type"] == "error": continue
            url = attach["url"]
            if attach["attach_type"] == "photo": # replace photo preview with actual photo
                if "hires_url" in attach: # photo is directly available
                    url = attach["hires_url"]
                elif url.startswith("/ajax/mercury/attachments/photo/view"):
                    url = parse_qs(urlparse(url).query)["uri"][0]
            elif attach["attach_type"] == "share" and "share" in attach: # replace photo preview with actual photo
                if attach["share"]["uri"] is None: continue # attachment removed or don't have permission to see
                url = attach["share"]["uri"]
            elif isinstance(url, str) and url.startswith("/"): # fix absolute URLs with the hostname
                url = "https://facebook.com" + url
            result.append(attach["attach_type"] + ":" + url)
    return result

def get_body(entry):
    if "body" in entry: return entry["body"]
    if "log_message_body" in entry: return entry["log_message_body"]
    print("BAD ENTRY \"{}\"\n".format(entry), file=sys.stderr)

def get_entry(entry):
    result = [
        entry["timestamp"], # unix millisecond timestamp
        get_user(entry["author"]), # message author
        get_body(entry), # message value
        get_attachments(entry), # attachments
    ]
    return json.dumps(result)

data = json.load(sys.stdin)
data = sorted(data, key=lambda entry: entry["timestamp"])

# output the normalized message data
messages = [get_entry(entry) for entry in data]
sys.stdout.write("[\n" + ",\n".join(messages) + "\n]\n")
