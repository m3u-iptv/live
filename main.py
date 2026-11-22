import requests, json, gzip, re, xml.etree.ElementTree as ET
from datetime import datetime

headers={"User-Agent":"Mozilla/5.0","Referer":"https://aasthatv.tv/tvguide"}

# 1. HTML LO
html = requests.get("https://aasthatv.tv/tvguide", headers=headers, timeout=30).text
print("HTML LEN:", len(html))
# HTML ko file me bhi save karo taaki dekh sake
open("debug.html","w",encoding="utf-8").write(html[:50000])

# 2. JSON BHI LO
def get_json(url):
    try:
        r=requests.get(url, headers=headers, timeout=30)
        j=r.json()
        open("debug_"+url.split("/")[-1].split("?")[0]+".json","w").write(json.dumps(j, indent=2)[:20000])
        print(url, "OK", str(j)[:1000])
        return j
    except Exception as e:
        print("FAIL", url, e)
        return {}
channels = get_json("https://api-apac.revlet.net/service/api/v1/tvguide/channels")
guide = get_json("https://api-apac.revlet.net/service/api/v1/page/content?path=tvguide&count=30")

tv = ET.Element("tv", {"generator-info-name":"aastha-tvguide"})
ch = ET.SubElement(tv, "channel", {"id":"aastha"})
ET.SubElement(ch, "display-name").text="Aastha TV"

programs=[]

# 3. TARIQA 1 - HTML ME TIME + NAAM WALA PATTERN
# Jaise 06:00 - Mangal Maye, 06:30 - Bhajan
# HTML se saare text nikaalo
text = re.sub(r'<script.*?</script>','', html, flags=re.S)
text = re.sub(r'<style.*?</style>','', text, flags=re.S)
text = re.sub(r'<[^>]+>',' | ', text)
text = re.sub(r'\s+',' ', text)

# Pattern: 06:00 AM / 6:00 / 06:00:00 ke baad naam
for m in re.finditer(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\s*\|?\s*([A-Za-z\u0900-\u097F][A-Za-z\u0900-\u097F0-9 \-\(\)]{3,60})', text):
    t_raw = m.group(1).strip()
    title = m.group(2).strip().strip('|').strip()
    # kachra hatao
    if len(title)<3 or "Aastha" in title and len(title)<10: continue
    if any(x in title.lower() for x in ["cookie","privacy","copyright","menu","search","login","subscribe"]): continue
    programs.append((t_raw, title))
    print(f"HTML SE MILA: {t_raw} - {title}")

# 4. TARIQA 2 - NEXT_DATA ME JO BHI HO
m2=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
if m2:
    try:
        data=json.loads(m2.group(1))
        def walk(o):
            if isinstance(o, dict):
                title=o.get("title") or o.get("name") or o.get("program_name")
                st=o.get("start_time") or o.get("start") or o.get("time")
                if title and st:
                    print("NEXT_DATA PROGRAM:", title, st)
                    programs.append((str(st), str(title)))
                for v in o.values(): walk(v)
            elif isinstance(o, list):
                for v in o: walk(v)
        walk(data)
    except Exception as e: print(e)

# 5. DEDUPE + EPG BANAO
seen=set()
today=datetime.now().strftime("%Y%m%d")
for t_raw, title in programs:
    if title in seen: continue
    seen.add(title)
    # Time ko saaf karo
    tm=re.search(r'(\d{1,2}):(\d{2})', t_raw)
    if not tm: continue
    h,mn=int(tm.group(1)), int(tm.group(2))
    is_pm = "pm" in t_raw.lower()
    is_am = "am" in t_raw.lower()
    if is_pm and h<12: h+=12
    if is_am and h==12: h=0
    start=f"{today}{h:02d}{mn:02d}00"
    # End = agle program ka start, abhi ke liye +30 min
    p=ET.SubElement(tv, "programme", {"start":start+" +0530", "stop":start+" +0530", "channel":"aastha"})
    ET.SubElement(p, "title", {"lang":"hi"}).text=title

# End time fix karo - agle wale ka start = iska end
progs=[c for c in tv if c.tag=='programme']
progs_sorted=sorted(progs, key=lambda x: x.get("start"))
for i,pr in enumerate(progs_sorted):
    if i+1 < len(progs_sorted):
        pr.set("stop", progs_sorted[i+1].get("start"))

print("TOTAL PROGRAM:", len(progs))

ET.indent(tv)
ET.ElementTree(tv).write("epg.xml", encoding="utf-8", xml_declaration=True)
with open("epg.xml","rb") as f_in, gzip.open("epg.xml.gz","wb") as f_out:
    f_out.writelines(f_in)
print("DONE!")
