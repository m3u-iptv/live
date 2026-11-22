import requests, json, gzip, xml.etree.ElementTree as ET
from datetime import datetime, timedelta

headers={"User-Agent":"Mozilla/5.0"}
BASE="https://api-apac.revlet.net/service/api/v1"

def get(url):
    try:
        r=requests.get(url, headers=headers, timeout=30)
        print(f"{url} -> {r.status_code}")
        return r.json()
    except Exception as e:
        print("FAIL", url, e)
        return {}

# 1. SAB KO JODO
channels = get(f"{BASE}/tvguide/channels")
guide = get(f"{BASE}/page/content?path=tvguide&count=30")
apps = get("https://aasthatv.tv/_next/data/k0F4bjJDDvoohwXU0n7k9/apps.html.json?dynamic=apps.html")
index = get("https://aasthatv.tv/_next/data/k0F4bjJDDvoohwXU0n7k9/index.json")
tvguide_next = get("https://aasthatv.tv/_next/data/k0F4bjJDDvoohwXU0n7k9/tvguide.json")

print("Channels:", str(channels)[:500])
print("Guide:", str(guide)[:500])

# 2. EPG.XML BANAO
tv = ET.Element("tv", {"generator-info-name":"aastha-tvguide"})
# Channels
def walk_channels(o):
    if isinstance(o, dict):
        name = o.get("name") or o.get("title") or o.get("channel_name")
        cid = o.get("id") or o.get("slug") or o.get("channel_id")
        logo = o.get("logo") or o.get("image") or o.get("icon")
        if name and cid:
            ch = ET.SubElement(tv, "channel", {"id":str(cid)})
            ET.SubElement(ch, "display-name").text = str(name)
            if logo:
                ET.SubElement(ch, "icon", {"src":str(logo)})
        for v in o.values(): walk_channels(v)
    elif isinstance(o, list):
        for v in o: walk_channels(v)

walk_channels(channels)
walk_channels(tvguide_next)
walk_channels(guide)

# Programmes
def walk_prog(o):
    if isinstance(o, dict):
        title = o.get("title") or o.get("name") or o.get("program_name")
        start = o.get("start_time") or o.get("start") or o.get("time")
        end = o.get("end_time") or o.get("end")
        cid = o.get("channel_id") or o.get("channel") or "aastha"
        desc = o.get("description") or o.get("desc") or ""
        if title and start:
            try:
                # Time ko format karo, nahi to abhi ka time
                s = str(start).replace("T","").replace("-","").replace(":","").replace(" ","")[:14]
                e = str(end).replace("T","").replace("-","").replace(":","").replace(" ","")[:14] if end else s
                p = ET.SubElement(tv, "programme", {"start":s+" +0530", "stop":e+" +0530", "channel":str(cid)})
                ET.SubElement(p, "title", {"lang":"hi"}).text = str(title)
                if desc: ET.SubElement(p, "desc", {"lang":"hi"}).text = str(desc)
            except: pass
        for v in o.values(): walk_prog(v)
    elif isinstance(o, list):
        for v in o: walk_prog(v)

walk_prog(guide)
walk_prog(tvguide_next)
walk_prog(index)
walk_prog(apps)

# Agar kuch nahi mila to ek dummy programme daal do taaki file khali na rahe
if len(list(tv))==0:
    ch = ET.SubElement(tv, "channel", {"id":"aastha"})
    ET.SubElement(ch, "display-name").text = "Aastha TV"

ET.indent(tv)
tree = ET.ElementTree(tv)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

# 3. GZ BANAO
with open("epg.xml","rb") as f_in, gzip.open("epg.xml.gz","wb") as f_out:
    f_out.writelines(f_in)

print("DONE epg.xml.gz ban gaya!")
