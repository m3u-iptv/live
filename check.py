import requests
import os
from collections import OrderedDict

INPUT = "streams/in.m3u"
OUTPUT = "index.m3u"

def is_dead(url):
    try:
        r = requests.head(url, timeout=8, allow_redirects=True)
        if r.status_code == 404:
            return True
        if r.status_code < 400:
            return False
    except:
        pass
    try:
        r = requests.get(url, timeout=8, stream=True, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 404:
            return True
        return False
    except:
        return False

def get_name(extinf_line):
    if "," in extinf_line:
        name = extinf_line.split(",", 1)[1].strip().lower()
        name = " ".join(name.split())
        return name
    return extinf_line.strip().lower()

if not os.path.exists(INPUT):
    print("in.m3u nahi mili")
    exit()

with open(INPUT, encoding="utf-8", errors="ignore") as f:
    lines = f.read().splitlines()

# 1. Pehle sab channel ko naam se group karo
# 9XM -> [link1, link2, link3...]
channels = OrderedDict()
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF"):
        if i+1 < len(lines):
            url = lines[i+1].strip()
            name = get_name(line)
            if name not in channels:
                channels[name] = []
            channels[name].append((line, url))
            i += 2
            continue
    i += 1

out = ["#EXTM3U"]
kept = 0

# 2. Har channel ke liye ek ON wali dhoondo
for name, links in channels.items():
    print(f"Checking {name} - {len(links)} links hai")
    added = False
    for extinf, url in links:
        if not is_dead(url):
            out.append(extinf)
            out.append(url)
            kept += 1
            added = True
            print(f"  -> ON mili, add ki: {url[:60]}")
            break  # ek mil gayi, baaki check karne ki zaroorat nahi
        else:
            print(f"  -> Band hai, skip: {url[:60]}")
    
    if not added:
        print(f"  -> {name} ki saari link band hai, index me nahi dala")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Total Channel: {len(channels)}, Index me aaye: {kept}")
