import requests
import os

INPUT = "streams/in.m3u"
OUTPUT = "index.m3u"

def check_url(url):
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code < 400:
            return True
        r = requests.get(url, timeout=5, stream=True)
        return r.status_code < 400
    except:
        return False

if not os.path.exists(INPUT):
    print("in.m3u nahi mili")
    exit()

with open(INPUT, encoding="utf-8", errors="ignore") as f:
    lines = f.read().splitlines()

out = ["#EXTM3U"]
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF"):
        if i+1 < len(lines):
            url = lines[i+1].strip()
            print("Check:", url[:60])
            if check_url(url):
                out.append(line)
                out.append(url)
            i += 2
            continue
    i += 1

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Ho gaya! {len(out)} lines")
