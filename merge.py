import gzip, requests, copy, xml.etree.ElementTree as ET

URLS = [
  "https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_IN2.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
  "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
]

channels = {}
programmes = []

for url in URLS:
    print("Download:", url)
    try:
        r = requests.get(url, timeout=60)
        print("Status:", r.status_code)
        data = gzip.decompress(r.content)
        root = ET.fromstring(data)
        for ch in root.findall("channel"):
            cid = ch.get("id")
            if cid not in channels:
                channels[cid] = copy.deepcopy(ch)
        for p in root.findall("programme"):
            programmes.append(copy.deepcopy(p))
        print("OK - Total Channels:", len(channels))
    except Exception as e:
        print("FAIL:", url, e)

tv = ET.Element("tv", {"generator-info-name":"Merged EPG"})
for ch in channels.values():
    tv.append(ch)
for p in programmes:
    tv.append(p)

tree = ET.ElementTree(tv)
with gzip.open("epg.xml.gz","wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print("HO GAYA -", len(channels), "Channels,", len(programmes), "Programmes")
