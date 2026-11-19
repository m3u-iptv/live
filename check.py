import requests
import os
from collections import OrderedDict

INPUT = "streams/in.m3u"
OUTPUT = "index.m3u"

VLCOPT = '#EXTVLCOPT:http-user-agent=Dalvik/2.1.0 (Linux; U; Android 10; SM-G975F Build/QP1A.190711.020)'

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
        return True

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

header = "#EXTM3U"
if lines and lines[0].startswith("#EXTM3U"):
    header = lines[0].strip()

channels = OrderedDict()
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF"):
        if i+1 < len(lines):
            url = lines[i+1].strip()
            # agar agle line me hi VLCOPT hai to usko skip karo, hum khud lagayenge
            if url.startswith("#EXTVLCOPT"):
                if i+2 < len(lines):
                    url = lines[i+2].strip()
                    i += 1
            name = get_name(line)
            if name not in channels:
                channels[name] = []
            channels[name].append((line, url))
            i += 2
            continue
    i += 1

out = [header]
kept = 0

for name, links in channels.items():
    added = False
    for extinf, url in links:
        if not is_dead(url):
            out.append(extinf)
            out.append(VLCOPT)  # <-- Har channel ke neeche ye line
            out.append(url)
            kept += 1
            added = True
            break
    
    if not added:
        print(f"{name} band hai")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Total Channel: {len(channels)}, Index me aaye: {kept}")
