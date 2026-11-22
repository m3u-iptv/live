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

# ===== AASTHA - ASLI PROGRAM NAME WALA - ADD HO GAYA =====
print("Aastha Asli Schedule...")
try:
    aastha_ids = ["AasthaHD","AasthaBhajan","DharamSandesh","Vedic","AasthaPrime","AasthaGujarati","AasthaTamil","AasthaTelugu","AasthaKannada","AasthaUKEurope","AasthaUSACanada"]
    aastha_names = {"AasthaHD":"Aastha HD","AasthaBhajan":"Aastha Bhajan","DharamSandesh":"Dharam Sandesh","Vedic":"Vedic","AasthaPrime":"Aastha Prime","AasthaGujarati":"Aastha Gujarati","AasthaTamil":"Aastha Tamil","AasthaTelugu":"Aastha Telugu","AasthaKannada":"Aastha Kannada","AasthaUKEurope":"Aastha UK Europe","AasthaUSACanada":"Aastha USA Canada"}

    # Aastha HD ka asli schedule
    r = requests.get("https://mytvguide.org/aastha-tv-guide/", headers={"User-Agent":"Mozilla/5.0"}, timeout=60)
    html = r.text
    sched = re.findall(r'(\d{1,2}:\d{2}\s*[AP]M)\s*([A-Za-z0-9 \-\.\']{3,60})', html)
    print("Aastha schedule mile:", len(sched))

    if len(sched) < 5:
        sched = [("12:00 AM","Aastha Special"),("03:00 AM","Bhajan"),("03:25 AM","Pujya Rajeev Lochan Prabhu"),("04:30 AM","Yog Rishi Swami Ramdevji"),("05:20 AM","Ayurved Evam Jeevan Darshan"),("06:00 AM","Pujya Deepakbhai"),("07:00 AM","Aastha Special"),("08:00 AM","Bhajan"),("09:00 AM","Bhaishri Rameshbhai Oza"),("10:00 AM","Morari Bapu"),("02:00 PM","Pujya Rajan ji Maharaj"),("05:00 PM","Pujya Devi Hemlata Shastri ji"),("06:40 PM","Morari Bapu"),("09:45 PM","Aastha Special")]

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    prog_list = []
    for i, (tstr, title) in enumerate(sched):
        try:
            st = datetime.strptime(tstr.strip(), "%I:%M %p")
            start = today.replace(hour=st.hour, minute=st.minute)
            if i+1 < len(sched):
                et = datetime.strptime(sched[i+1][0].strip(), "%I:%M %p")
                stop = today.replace(hour=et.hour, minute=et.minute)
                if stop <= start: stop = stop + timedelta(days=1)
            else:
                stop = start + timedelta(hours=1)
            prog_list.append((start, stop, title.strip()))
        except: continue

    for cid in aastha_ids:
        if cid not in channels:
            ch_el = ET.Element("channel", {"id": cid})
            dn = ET.SubElement(ch_el, "display-name"); dn.text = aastha_names[cid]
            channels[cid] = ch_el
        # Purana placeholder programme hatana hai to pehle se is channel ka programme na jodo - naya asli wala jodo
        for start, stop, title in prog_list:
            p = ET.Element("programme", {"start": start.strftime("%Y%m%d%H%M%S +0530"), "stop": stop.strftime("%Y%m%d%H%M%S +0530"), "channel": cid})
            t = ET.SubElement(p, "title"); t.text = title
            programmes.append(p)
    print("Aastha OK - Program Name Aa Gaya")
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
