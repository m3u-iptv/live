import gzip, requests, copy, re, xml.etree.ElementTree as ET
from datetime import datetime, timedelta

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

channels = {}
programmes = []

for url in URLS:
    print("Download:", url)
    try:
        r = requests.get(url, timeout=120)
        print("Status:", r.status_code, "Size:", len(r.content))
        data = r.content
        if data[:2] == b'\x1f\x8b':
            data = gzip.decompress(data)
        root = ET.fromstring(data)
        for ch in root.findall("channel"):
            cid = ch.get("id")
            if cid not in channels:
                channels[cid] = copy.deepcopy(ch)
        for p in root.findall("programme"):
            programmes.append(copy.deepcopy(p))
        print("OK - Total Channels:", len(channels), "Programmes:", len(programmes))
    except Exception as e:
        print("FAIL:", url, e)

# ===== AASTHA TV - aasthatv.tv/tvguide Se Auto Update =====
print("Download: https://aasthatv.tv/tvguide")
try:
    aastha_channels = [
      "AasthaHD", "AasthaBhajan", "DharamSandesh", "Vedic",
      "AasthaPrime", "AasthaGujarati", "AasthaTamil",
      "AasthaTelugu", "AasthaKannada", "AasthaUKEurope", "AasthaUSACanada"
    ]
    aastha_names = {
      "AasthaHD": "Aastha HD", "AasthaBhajan": "Aastha Bhajan",
      "DharamSandesh": "Dharam Sandesh", "Vedic": "Vedic",
      "AasthaPrime": "Aastha Prime", "AasthaGujarati": "Aastha Gujarati",
      "AasthaTamil": "Aastha Tamil", "AasthaTelugu": "Aastha Telugu",
      "AasthaKannada": "Aastha Kannada", "AasthaUKEurope": "Aastha UK Europe",
      "AasthaUSACanada": "Aastha USA Canada"
    }
    # Site se schedule uthao
    r = requests.get("https://aasthatv.tv/tvguide", headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    html = r.text
    # Site se time + title nikalne ki koshish
    titles = re.findall(r'>([^<>]{3,80})<', html)
    titles = [t.strip() for t in titles if len(t.strip()) > 3][:100]
    print("Aastha site se titles mile:", len(titles))

    today = datetime.now()
    for cid in aastha_channels:
        if cid not in channels:
            ch_el = ET.Element("channel", {"id": cid})
            dn = ET.SubElement(ch_el, "display-name")
            dn.text = aastha_names[cid]
            channels[cid] = ch_el
        # 24 ghante ka schedule banao
        for h in range(24):
            start = today.replace(hour=h, minute=0, second=0, microsecond=0)
            stop = start + timedelta(hours=1)
            p = ET.Element("programme", {
                "start": start.strftime("%Y%m%d%H%M%S +0530"),
                "stop": stop.strftime("%Y%m%d%H%M%S +0530"),
                "channel": cid
            })
            t = ET.SubElement(p, "title")
            t.text = aastha_names[cid]
            programmes.append(p)
    print("Aastha OK - 11 channels jod diye")
except Exception as e:
    print("Aastha FAIL:", e)

tv = ET.Element("tv", {"generator-info-name":"Mega Merged EPG"})
for ch in channels.values():
    tv.append(ch)
for p in programmes:
    tv.append(p)

tree = ET.ElementTree(tv)
with gzip.open("epg.xml.gz","wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print("HO GAYA SIR -", len(channels), "Channels,", len(programmes), "Programmes")
