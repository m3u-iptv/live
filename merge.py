import gzip, requests, copy, xml.etree.ElementTree as ET
import time

URLS = [
  "https://epgshare01.online/epgshare01/epg_ripper_HK1.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_IN2.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_SG1.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
  "https://i.mjh.nz/SamsungTVPlus/all.xml.gz",
  "https://i.mjh.nz/Plex/all.xml.gz",
  "https://avkb.short.gy/epg.xml.gz",
  "https://avkb.short.gy/jioepg.xml.gz",
  "https://avkb.short.gy/tsepg.xml.gz",
  "https://www.open-epg.com/files/india.xml",
  "https://www.open-epg.com/files/unitedkingdom.xml",
  "https://www.open-epg.com/files/hongkong4.xml",
  "https://www.open-epg.com/files/unitedstates10.xml",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

channels = {}
programmes = []
seen_prog = set()  # Duplicate programme rokne ke liye

for url in URLS:
    print("Download:", url)
    data = None
    for attempt in range(3):  # 3 baar try karega, ek baar fail hua to chhodega nahi
        try:
            r = requests.get(url, timeout=120, headers=HEADERS)
            print("Status:", r.status_code, "Size:", len(r.content))
            if r.status_code == 200 and len(r.content) > 1000:
                data = r.content
                break
            else:
                print("Chhota ya galat data, dobara try...")
                time.sleep(5)
        except Exception as e:
            print("FAIL try", attempt+1, e)
            time.sleep(5)
    
    if not data:
        print("SKIP:", url, "- Iska data nahi mila, baaki wala chalu rakhenge")
        continue

    try:
        if data[:2] == b'\x1f\x8b':
            data = gzip.decompress(data)
        root = ET.fromstring(data)
        for ch in root.findall("channel"):
            cid = ch.get("id")
            # Agar pehle wala channel khali hai aur naya wala achha hai to naya rakh lo
            if cid not in channels:
                channels[cid] = copy.deepcopy(ch)
            else:
                # Agar purane me display-name nahi hai aur naye me hai to replace karo
                old_names = channels[cid].findall("display-name")
                new_names = ch.findall("display-name")
                if not old_names and new_names:
                    channels[cid] = copy.deepcopy(ch)

        for p in root.findall("programme"):
            # Same channel + same time wala dobara mat daalo
            key = (p.get("channel"), p.get("start"), p.get("stop"))
            if key not in seen_prog:
                seen_prog.add(key)
                programmes.append(copy.deepcopy(p))
        print("OK - Total Channels:", len(channels), "Programmes:", len(programmes))
    except Exception as e:
        print("PARSE FAIL:", url, e)

tv = ET.Element("tv", {"generator-info-name":"Mega Merged EPG"})
for ch in channels.values():
    tv.append(ch)
for p in programmes:
    tv.append(p)

tree = ET.ElementTree(tv)
with gzip.open("epg.xml.gz","wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print("HO GAYA SIR -", len(channels), "Channels,", len(programmes), "Programmes")
