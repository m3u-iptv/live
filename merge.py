import gzip, requests, copy, xml.etree.ElementTree as ET
import time

URLS = [
  "https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_IN2.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

channels = {}
programmes = []
seen = set()

for url in URLS:
    print("Download:", url)
    data = None
    for i in range(3):
        try:
            r = requests.get(url, timeout=120, headers=HEADERS)
            print("Status:", r.status_code, "Size:", len(r.content))
            if r.status_code == 200 and len(r.content) > 1000:
                data = r.content
                break
            time.sleep(5)
        except Exception as e:
            print("Retry", i+1, e)
            time.sleep(5)
    
    if not data:
        print("SKIP:", url)
        continue

    try:
        if data[:2] == b'\x1f\x8b':
            data = gzip.decompress(data)
        root = ET.fromstring(data)
        for ch in root.findall("channel"):
            cid = ch.get("id")
            if cid not in channels:
                channels[cid] = copy.deepcopy(ch)
        for p in root.findall("programme"):
            key = (p.get("channel"), p.get("start"), p.get("stop"))
            if key not in seen:
                seen.add(key)
                programmes.append(copy.deepcopy(p))
        print("OK - Channels:", len(channels), "Programmes:", len(programmes))
    except Exception as e:
        print("FAIL:", url, e)

tv = ET.Element("tv", {"generator-info-name": "IN EPG"})
for ch in channels.values():
    tv.append(ch)
for p in programmes:
    tv.append(p)

tree = ET.ElementTree(tv)
with gzip.open("epg.xml.gz", "wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print("HO GAYA SIR -", len(channels), "Channels,", len(programmes), "Programmes")
