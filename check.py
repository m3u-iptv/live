import requests
import os
import time
from collections import OrderedDict

INPUT = "streams/in.m3u"
OUTPUT = "index.m3u"

VLCOPT = '#EXTVLCOPT:http-user-agent=Dalvik/2.1.0 (Linux; U; Android 10; SM-G975F Build/QP1A.190711.020)'
UA = "Dalvik/2.1.0 (Linux; U; Android 10; SM-G975F Build/QP1A.190711.020)"

def is_dead(url):
    headers = {
        "User-Agent": UA,
        "Range": "bytes=0-1023",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    # 2 baar try karega, ek baar fail hone pe turant dead nahi manega
    for attempt in range(2):
        try:
            # HEAD nahi, sidha GET with Range se check karo
            r = requests.get(url, timeout=15, stream=True, headers=headers, allow_redirects=True)
            # 200, 206, 302, 403 bhi chalu maano - kyunki 403 aksar HEAD block ki wajah se aata hai
            # Sirf 404 ko hi dead maano
            if r.status_code == 404:
                r.close()
                continue
            if r.status_code in [200, 206, 301, 302, 403, 401]:
                r.close()
                return False
            r.close()
            # Agar koi aur code aaya to dobara try karo
        except Exception as e:
            print(f"Try {attempt+1} fail {url[:60]} - {e}")
            time.sleep(2)
            continue
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
    line = lines[i].strip()
    if line.startswith("#EXTINF"):
        # Agli non-empty line me URL dhoondo
        j = i + 1
        url = ""
        while j < len(lines):
            nxt = lines[j].strip()
            if nxt.startswith("#EXTVLCOPT"):
                j += 1
                continue
            if nxt == "" or nxt.startswith("#"):
                j += 1
                continue
            url = nxt
            break
        if url:
            name = get_name(line)
            if name not in channels:
                channels[name] = []
            channels[name].append((line, url))
        i = j + 1
        continue
    i += 1

out = [header]
kept = 0

for name, links in channels.items():
    added = False
    for extinf, url in links:
        if not is_dead(url):
            out.append(extinf)
            out.append(VLCOPT)
            out.append(url)
            kept += 1
            added = True
            break
    if not added:
        print(f"{name} band hai")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Total Channel: {len(channels)}, Index me aaye: {kept}")
