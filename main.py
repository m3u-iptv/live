import requests, json, gzip, re, xml.etree.ElementTree as ET
from datetime import datetime

headers={"User-Agent":"Mozilla/5.0", "Referer":"https://aasthatv.tv/tvguide"}

def get(url):
    try:
        r=requests.get(url, headers=headers, timeout=30)
        print(url, r.status_code, len(r.text))
        return r.text
    except Exception as e:
        print("FAIL", e)
        return ""

# 1. SEEDHA TVGUIDE PAGE PAKDO
html = get("https://aasthatv.tv/tvguide")

# 2. NEXT DATA NIKALO
data = {}
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
if m:
    try:
        data = json.loads(m.group(1))
        print("NEXT_DATA mil gaya!")
    except: pass

# 3. API WALA BHI JODO
def get_json(url):
    try:
        r=requests.get(url, headers=headers, timeout=30)
        return r.json()
    except: return {}
channels = get_json("https://api-apac.revlet.net/service/api/v1/tvguide/channels")
guide = get_json("https://api-apac.revlet.net/service/api/v1/page/content?path=tvguide&count=30")

print("channels type:", type(channels))
print("guide keys:", list(guide.keys())[:10] if isinstance(guide, dict) else "list")

# 4. EPG BANAO
tv = ET.Element("tv", {"generator-info-name":"aastha-tvguide"})

all_data = [data, channels, guide, html]

def walk(o):
    if isinstance(o, dict):
        name = o.get("name") or o.get("title") or o.get("channel_name") or o.get("channelName")
        cid = o.get("id") or o.get("slug") or o.get("channel_id")
        if name and cid and len(str(cid))<50:
            ch = ET.SubElement(tv, "channel", {"id":str(cid)})
            ET.SubElement(ch, "display-name").text = str(name)
            logo = o.get("logo") or o.get("image") or o.get("logoUrl")
            if logo: ET.SubElement(ch, "icon", {"src":str(logo)})
        # programme
        title = o.get("title") or o.get("program_name") or o.get("show_title")
        start = o.get("start_time") or o.get("start") or o.get("startTime")
        if title and start:
            try:
                s = str(start).replace("T","").replace("-","").replace(":","").replace(" ","")[:14]
                end = o.get("end_time") or o.get("end") or o.get("endTime") or start
                e = str(end).replace("T","").replace("-","").replace(":","").replace(" ","")[:14]
                p = ET.SubElement(tv, "programme", {"start":s+" +0530", "stop":e+" +0530", "channel":str(cid or "aastha")})
                ET.SubElement(p, "title", {"lang":"hi"}).text = str(title)
            except: pass
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)

for d in all_data:
    walk(d)

# Agar khali hai to Aastha daal do
if len(list(tv))==0:
    ch = ET.SubElement(tv, "channel", {"id":"aastha"})
    ET.SubElement(ch, "display-name").text = "Aastha TV"
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    p = ET.SubElement(tv, "programme", {"start":now+" +0530", "stop":now+" +0530", "channel":"aastha"})
    ET.SubElement(p, "title", {"lang":"hi"}).text = "Aastha TV Live"

ET.indent(tv)
ET.ElementTree(tv).write("epg.xml", encoding="utf-8", xml_declaration=True)
with open("epg.xml","rb") as f_in, gzip.open("epg.xml.gz","wb") as f_out:
    f_out.writelines(f_in)
print("DONE epg.xml.gz ban gaya!")
