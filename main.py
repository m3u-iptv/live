import requests, json, gzip, re, xml.etree.ElementTree as ET
from datetime import datetime, timezone

headers={"User-Agent":"Mozilla/5.0", "Referer":"https://aasthatv.tv/tvguide"}

def get_json(url):
    try:
        r=requests.get(url, headers=headers, timeout=30)
        print(url, r.status_code)
        j=r.json()
        print("KEYS:", list(j.keys())[:20] if isinstance(j, dict) else f"LIST len {len(j)}")
        print("SAMPLE:", str(j)[:2000])
        return j
    except Exception as e:
        print("FAIL", url, e)
        return {}

channels = get_json("https://api-apac.revlet.net/service/api/v1/tvguide/channels")
guide = get_json("https://api-apac.revlet.net/service/api/v1/page/content?path=tvguide&count=30")

# TVGUIDE PAGE BHI
html = requests.get("https://aasthatv.tv/tvguide", headers=headers, timeout=30).text
data={}
m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
if m:
    try: data=json.loads(m.group(1))
    except: pass

tv = ET.Element("tv", {"generator-info-name":"aastha-tvguide"})
seen=set()

def clean_time(v):
    # epoch, ISO, sab ko handle karega
    if v is None: return None
    s=str(v).strip()
    if not s: return None
    try:
        # epoch 10 ya 13 digit
        if s.isdigit():
            ts=int(s)
            if len(s)==13: ts=ts//1000
            dt=datetime.fromtimestamp(ts, tz=timezone.utc)
            return dt.strftime("%Y%m%d%H%M%S")
        # ISO 2026-11-22T06:00:00
        s2=s.replace("T"," ").replace("Z","").split(".")[0]
        # 2026-11-22 06:00:00 ya 06:00
        for fmt in ("%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M","%Y/%m/%d %H:%M","%d-%m-%Y %H:%M","%H:%M"):
            try:
                dt=datetime.strptime(s2, fmt)
                if fmt=="%H:%M":
                    dt=datetime.now().replace(hour=dt.hour, minute=dt.minute, second=0)
                return dt.strftime("%Y%m%d%H%M%S")
            except: pass
        # sirf digits nikaal lo 20261122060000
        d=re.sub(r'\D','',s)
        if len(d)>=12: return d[:14].ljust(14,'0')
    except: pass
    return None

def walk(o, parent_channel="aastha"):
    if isinstance(o, dict):
        # channel id nikal lo
        cid = o.get("channel_id") or o.get("channelId") or o.get("channel") or o.get("slug") or o.get("id")
        if isinstance(cid, dict): cid=cid.get("id") or cid.get("slug") or parent_channel
        cur_ch = str(cid) if cid and len(str(cid))<60 else parent_channel

        # CHANNEL
        name = o.get("channel_name") or o.get("channelName") or o.get("name")
        # sirf tab jab isme logo ya channel jaisa lage
        if name and (o.get("logo") or o.get("channel_id") or o.get("slug")) and str(cid) not in seen:
            seen.add(str(cid))
            ch=ET.SubElement(tv, "channel", {"id":str(cid)})
            ET.SubElement(ch, "display-name").text=str(name)
            logo=o.get("logo") or o.get("image") or o.get("logoUrl") or o.get("icon")
            if logo and isinstance(logo,str): ET.SubElement(ch, "icon", {"src":logo})

        # PROGRAM - har key check karo
        title = o.get("title") or o.get("program_name") or o.get("programName") or o.get("show_title") or o.get("showName") or o.get("name")
        # time ke 20 tarah ke naam
        start_raw = None
        end_raw = None
        for k,v in o.items():
            lk=str(k).lower()
            if "start" in lk or lk in ("from","time","schedule_time","from_time","begin"): start_raw=v
            if "end" in lk or lk in ("to","to_time","until"): end_raw=v
        # agar schedule list ke andar hai to bhi
        if title and start_raw:
            s=clean_time(start_raw)
            e=clean_time(end_raw) or s
            if s:
                p=ET.SubElement(tv, "programme", {"start":s+" +0530", "stop":e+" +0530", "channel":cur_ch})
                ET.SubElement(p, "title", {"lang":"hi"}).text=str(title)
                desc=o.get("description") or o.get("desc") or o.get("synopsis") or ""
                if desc: ET.SubElement(p, "desc", {"lang":"hi"}).text=str(desc)
                print(f"PROGRAM MILA: {s} {title} ch={cur_ch}")
        for v in o.values(): walk(v, cur_ch)
    elif isinstance(o, list):
        for v in o: walk(v, parent_channel)

walk(channels)
walk(guide)
walk(data)

print("TOTAL CHANNEL:", len([c for c in tv if c.tag=='channel']))
print("TOTAL PROGRAM:", len([c for c in tv if c.tag=='programme']))

if len([c for c in tv if c.tag=='channel'])==0:
    ch=ET.SubElement(tv, "channel", {"id":"aastha"})
    ET.SubElement(ch, "display-name").text="Aastha TV"

ET.indent(tv)
ET.ElementTree(tv).write("epg.xml", encoding="utf-8", xml_declaration=True)
with open("epg.xml","rb") as f_in, gzip.open("epg.xml.gz","wb") as f_out:
    f_out.writelines(f_in)
print("DONE!")
