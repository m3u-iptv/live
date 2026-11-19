import os, glob, requests

# Tera input file
INPUT = "live/streams/in.m3u"
OUTPUT = "live/index.m3u"

def is_working(url):
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code < 400:
            return True
        r = requests.get(url, timeout=5, stream=True)
        return r.status_code < 400
    except:
        return False

# in.m3u padho
channels = {} # Naam -> list of (extinf, url)
order = []
with open(INPUT, encoding="utf-8", errors="ignore") as f:
    lines = [l.strip() for l in f if l.strip()]

for i in range(len(lines)):
    if lines[i].startswith("#EXTINF"):
        name = lines[i].split(",",1)[-1].strip()
        if i+1 < len(lines) and not lines[i+1].startswith("#"):
            url = lines[i+1].strip()
            if name not in channels:
                channels[name] = []
                order.append(name)
            channels[name].append((lines[i], url))

# Ab har channel ke liye sirf 1 chalu wala chuno
out = ["#EXTM3U"]
for name in order:
    for extinf, url in channels[name]:
        print(f"Checking {name} -> {url[:50]}")
        if is_working(url):
            print(f"CHALU MILA: {name}")
            out.append(extinf)
            out.append(url)
            break
    else:
        print(f"KOI BHI NAHI CHALA: {name}")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print("HO GAYA - 5 MIN WALA UPDATE!")
