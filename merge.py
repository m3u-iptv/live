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

# ===== AASTHA - aasthatv.tv/tvguide SE ASLI ALAG-ALAG SCHEDULE =====
print("Aastha Original - aasthatv.tv/tvguide...")
try:
    import json
    aastha_map = {
      "AasthaHD": ["Aastha HD", "Aastha"],
      "AasthaBhajan": ["Aastha Bhajan", "Bhajan"],
      "DharamSandesh": ["Dharam Sandesh"],
      "Vedic": ["Vedic"],
      "AasthaPrime": ["Aastha Prime", "Prime"],
      "AasthaGujarati": ["Aastha Gujarati", "Gujarati"],
      "AasthaTamil": ["Aastha Tamil", "Tamil"],
      "AasthaTelugu": ["Aastha Telugu", "Telugu"],
      "AasthaKannada": ["Aastha Kannada", "Kannada"],
      "AasthaUKEurope": ["Aastha UK", "UK Europe"],
      "AasthaUSACanada": ["Aastha USA", "USA Canada"],
    }
    aastha_names = {"AasthaHD":"Aastha HD","AasthaBhajan":"Aastha Bhajan","DharamSandesh":"Dharam Sandesh","Vedic":"Vedic","AasthaPrime":"Aastha Prime","AasthaGujarati":"Aastha Gujarati","AasthaTamil":"Aastha Tamil","AasthaTelugu":"Aastha Telugu","AasthaKannada":"Aastha Kannada","AasthaUKEurope":"Aastha UK Europe","AasthaUSACanada":"Aastha USA Canada"}

    headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36", "Accept":"application/json, text/html"}
    # 1. Pehle HTML uthao - isme JSON chhupa hota hai
    html = ""
    for u in ["https://aasthatv.tv/tvguide", "https://aasthatv.tv/api/tvguide", "https://aasthatv.tv/api/program-guide", "https://api.aasthatv.tv/tvguide"]:
        try:
            rr = requests.get(u, headers=headers, timeout=30)
            print("Try:", u, rr.status_code, len(rr.text))
            if len(rr.text) > 5000:
                html += rr.text + "\n"
        except Exception as e:
            print("Try fail:", u, e)

    # 2. HTML me se Time + Title ke jode nikalo - jaise 07:00 PM YAMUNA AARTI
    # Har channel ke hisse ko alag karo
    def parse_channel_section(section):
        # 07:00 PM, 07:30 PM ke saath title
        pairs = re.findall(r'(\d{1,2}:\d{2}\s*[AP]M)[^A-Za-z0-9]{0,20}([A-Z0-9][A-Za-z0-9 \-\.\(\)\@]{2,60})', section)
        out = []
        for tstr, title in pairs:
            title = title.strip().strip("-").strip()
            if len(title) < 3: continue
            if title.lower() in ["go live","live","home","shorts","search","account"]: continue
            if "Mon" in title or "Tue" in title: continue
            out.append((tstr.strip(), title))
        return out

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for cid, keywords in aastha_map.items():
        if cid not in channels:
            ch_el = ET.Element("channel", {"id": cid})
            dn = ET.SubElement(ch_el, "display-name"); dn.text = aastha_names[cid]
            channels[cid] = ch_el

        # Is channel ka hissa dhoondo HTML me
        sched = []
        for kw in keywords:
            idx = html.find(kw)
            if idx != -1:
                sched = parse_channel_section(html[idx:idx+8000])
                if len(sched) >= 3:
                    break
        print(cid, "schedule:", len(sched), sched[:2])

        # Agar is channel ka alag na mile to uska naam hi daalo, dusre ka copy mat karo
        if len(sched) < 3:
            sched = [("12:00 AM", aastha_names[cid]), ("06:00 AM", aastha_names[cid]), ("12:00 PM", aastha_names[cid]), ("06:00 PM", aastha_names[cid])]

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
                p = ET.Element("programme", {"start": start.strftime("%Y%m%d%H%M%S +0530"), "stop": stop.strftime("%Y%m%d%H%M%S +0530"), "channel": cid})
                t = ET.SubElement(p, "title"); t.text = title
                programmes.append(p)
            except: continue
    print("Aastha OK - Har Channel Alag")
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
