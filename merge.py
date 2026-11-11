import gzip, requests, copy, xml.etree.ElementTree as ET
import re, glob
from datetime import datetime, timedelta, timezone

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
        # Agar GZ hai to kholo, nahi to aise hi use karo
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

# ===== NO PROGRAMS WALA RULE YAHI SE SHURU - SIR =====
IST = timezone(timedelta(hours=5, minutes=30))
now = datetime.now(IST).replace(minute=0, second=0, microsecond=0)

# Aapke Playlist se saare channel nikalenge
playlist_channels = set(channels.keys())
for m3u in glob.glob("**/*.m3u", recursive=True):
    try:
        with open(m3u, errors="ignore") as f:
            for line in f:
                m = re.search(r'tvg-id="([^"]+)"', line)
                if m and m.group(1):
                    playlist_channels.add(m.group(1))
    except:
        pass

# Har channel ke liye check karenge - kaha pehle se program hai
for cid in sorted(playlist_channels):
    if cid not in channels:
        ch = ET.Element("channel", {"id": cid})
        dn = ET.SubElement(ch, "display-name")
        dn.text = cid
        channels[cid] = ch

    # Is channel ke busy time
    busy = set()
    for p in programmes:
        if p.get("channel") == cid:
            # start ka YYYYMMDDHH le lo
            busy.add(p.get("start", "")[:10])

    # 72 Ghante = 3 Din, Har 1 Ghante Me No Programs
    for h in range(72):
        start = now + timedelta(hours=h)
        s = start.strftime("%Y%m%d%H%M%S +0530")
        # Agar is ghante me Original Program hai, to skip - Original hi rahega!
        if s[:10] in busy:
            continue
        stop = start + timedelta(hours=1)
        e = stop.strftime("%Y%m%d%H%M%S +0530")
        prog = ET.Element("programme", {"start": s, "stop": e, "channel": cid})
        title = ET.SubElement(prog, "title", {"lang": "en"})
        title.text = "No Programs"
        programmes.append(prog)

print("NO PROGRAMS ADD HO GAYA - Total Programmes:", len(programmes))
# ===== NO PROGRAMS KHATAM =====

tv = ET.Element("tv", {"generator-info-name":"Mega Merged EPG"})
for ch in channels.values():
    tv.append(ch)
for p in programmes:
    tv.append(p)

tree = ET.ElementTree(tv)
with gzip.open("epg.xml.gz","wb") as f:
    tree.write(f, encoding="utf-8", xml_declaration=True)

print("HO GAYA SIR -", len(channels), "Channels,", len(programmes), "Programmes")
