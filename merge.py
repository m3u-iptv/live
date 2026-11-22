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

# ===== AASTHA - AISA KAR DIYA - SITE FAIL HO TO BHI PROGRAM AAYEGA =====
print("Aastha...")
try:
    aastha_names = {"AasthaHD":"Aastha HD","AasthaBhajan":"Aastha Bhajan","DharamSandesh":"Dharam Sandesh","Vedic":"Vedic","AasthaPrime":"Aastha Prime","AasthaGujarati":"Aastha Gujarati","AasthaTamil":"Aastha Tamil","AasthaTelugu":"Aastha Telugu","AasthaKannada":"Aastha Kannada","AasthaUKEurope":"Aastha UK Europe","AasthaUSACanada":"Aastha USA Canada"}
    aastha_alias = {
      "AasthaHD": ["AasthaHD","Aastha","Aastha.in"],
      "AasthaBhajan": ["AasthaBhajan","AasthaBhajan.in"],
      "DharamSandesh": ["DharamSandesh","DharamSandesh.in"],
      "Vedic": ["Vedic","Vedic.in"],
      "AasthaPrime": ["AasthaPrime","AasthaPrime1","AasthaPrime1.in"],
      "AasthaGujarati": ["AasthaGujarati","AasthaGujarati.in"],
      "AasthaTamil": ["AasthaTamil","AasthaTamil.in"],
      "AasthaTelugu": ["AasthaTelugu","AasthaTelugu.in"],
      "AasthaKannada": ["AasthaKannada","AasthaKannada.in"],
      "AasthaUKEurope": ["AasthaUKEurope","AasthaUK"],
      "AasthaUSACanada": ["AasthaUSACanada","AasthaUSA"],
    }
    fallback = {
      "AasthaBhajan": [("12:00 AM","BHAJAN"),("03:00 AM","BHAGWAT KATHA"),("05:00 AM","YAMUNA AARTI - MATHURA"),("06:00 AM","BHAGWAT GEETA"),("07:00 AM","SHRIMAD BHAGWAT KATHA"),("12:00 PM","BHAJAN"),("05:00 PM","AARTI"),("07:00 PM","SATSANG"),("09:00 PM","BHAJAN SANDHYA")],
      "Vedic": [("12:00 AM","VEDIC"),("04:30 AM","YOGRISHI SWAMI RAMDEVJI - YOG"),("06:00 AM","AYURVED EVAM JEEVAN DARSHAN"),("08:00 AM","PATANJALI YOG"),("12:00 PM","VEDIC SATSANG"),("06:00 PM","YOG SHIVIR"),("09:00 PM","VEDIC BHAJAN")],
      "AasthaGujarati": [("12:00 AM","Aastha Gujarati"),("05:00 AM","AARTI"),("06:00 AM","GUJARATI BHAJAN"),("09:00 AM","MORARI BAPU - GUJARATI"),("12:00 PM","SATSANG"),("05:00 PM","KATHA"),("07:00 PM","AARTI - GUJARATI")],
      "AasthaTamil": [("12:00 AM","Aastha Tamil"),("05:00 AM","PANDURANGA BHAJAN"),("06:00 AM","TAMIL SATSANG"),("09:00 AM","TAMIL KATHA"),("12:00 PM","BHAJAN"),("06:00 PM","AARTI"),("09:00 PM","TAMIL BHAJAN")],
      "AasthaTelugu": [("12:00 AM","Aastha Telugu"),("05:00 AM","SRIMAD BHAGWATAM"),("06:00 AM","TELUGU BHAJAN"),("09:00 AM","TELUGU KATHA"),("12:00 PM","SATSANG"),("06:00 PM","AARTI"),("09:00 PM","TELUGU BHAJAN")],
      "AasthaKannada": [("12:00 AM","Aastha Kannada"),("05:00 AM","KANNADA BHAJAN"),("06:00 AM","KANNADA SATSANG"),("09:00 AM","KANNADA KATHA"),("12:00 PM","BHAJAN"),("06:00 PM","AARTI"),("09:00 PM","KANNADA BHAJAN")],
      "AasthaHD": [("12:00 AM","Aastha Special"),("03:00 AM","Bhajan"),("04:30 AM","Yog Rishi Swami Ramdevji"),("05:20 AM","Ayurved Evam Jeevan Darshan"),("07:00 AM","Aastha Special"),("09:00 AM","Bhaishri Rameshbhai Oza"),("10:00 AM","Morari Bapu"),("02:00 PM","Pujya Rajan ji Maharaj"),("05:00 PM","Pujya Devi Hemlata Shastri ji"),("06:40 PM","Morari Bapu"),("09:45 PM","Aastha Special")],
      "DharamSandesh": [("12:00 AM","Dharam Sandesh"),("05:00 AM","AARTI"),("06:00 AM","SATSANG"),("09:00 AM","KATHA"),("12:00 PM","BHAJAN"),("06:00 PM","AARTI"),("09:00 PM","SATSANG")],
      "AasthaPrime": [("12:00 AM","Aastha Prime"),("05:00 AM","YOG"),("06:00 AM","BHAJAN"),("09:00 AM","MORARI BAPU"),("12:00 PM","KATHA"),("06:00 PM","AARTI"),("09:00 PM","BHAJAN")],
      "AasthaUKEurope": [("12:00 AM","Aastha UK Europe"),("05:00 AM","YOG"),("06:00 AM","BHAJAN"),("09:00 AM","MORARI BAPU"),("12:00 PM","KATHA"),("06:00 PM","AARTI"),("09:00 PM","BHAJAN")],
      "AasthaUSACanada": [("12:00 AM","Aastha USA Canada"),("05:00 AM","YOG"),("06:00 AM","BHAJAN"),("09:00 AM","MORARI BAPU"),("12:00 PM","KATHA"),("06:00 PM","AARTI"),("09:00 PM","BHAJAN")],
    }
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    for main_cid, alias_list in aastha_alias.items():
        sched = fallback.get(main_cid, [])
        prog_list = []
        for i, (tstr, title) in enumerate(sched):
            try:
                st = datetime.strptime(tstr, "%I:%M %p")
                start = today.replace(hour=st.hour, minute=st.minute)
                if i+1 < len(sched):
                    et = datetime.strptime(sched[i+1][0], "%I:%M %p")
                    stop = today.replace(hour=et.hour, minute=et.minute)
                    if stop <= start: stop += timedelta(days=1)
                else:
                    stop = start + timedelta(hours=1)
                prog_list.append((start, stop, title))
            except: continue
        for cid in alias_list:
            if cid not in channels:
                ch_el = ET.Element("channel", {"id": cid})
                dn = ET.SubElement(ch_el, "display-name"); dn.text = aastha_names[main_cid]
                channels[cid] = ch_el
            for start, stop, title in prog_list:
                p = ET.Element("programme", {"start": start.strftime("%Y%m%d%H%M%S +0530"), "stop": stop.strftime("%Y%m%d%H%M%S +0530"), "channel": cid})
                t = ET.SubElement(p, "title"); t.text = title
                programmes.append(p)
        print(main_cid, "OK -", len(prog_list))
    print("Aastha OK")
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
