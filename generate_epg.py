import gzip
import re
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

URL = "https://dishnews.in/goldmines-bollywood-channel-movie-schedule/"
CHANNEL_ID = "GoldminesBollywood.in"
CHANNEL_NAME = "Goldmines Bollywood"

def fetch_schedule():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(URL, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    lines = [line.strip() for line in soup.get_text().split("\n") if line.strip()]
    
    programs = []
    time_pattern = re.compile(r"^\d{2}:\d{2}(AM|PM)$", re.IGNORECASE)
    
    for i, line in enumerate(lines):
        if time_pattern.match(line):
            title = "Unknown Movie"
            for back in range(1, 4):
                if i - back >= 0 and "Hindi | Film" not in lines[i - back] and "hindi movies" not in lines[i - back].lower():
                    title = lines[i - back]
                    break
            programs.append({"title": title, "time_str": line})
            
    return programs

def build_xmltv(programs):
    tv = ET.Element("tv", {"generator-info-name": "Custom EPG Generator"})
    
    # Channel Info
    channel = ET.SubElement(tv, "channel", {"id": CHANNEL_ID})
    display_name = ET.SubElement(channel, "display-name", {"lang": "hi"})
    display_name.text = CHANNEL_NAME
    
    # Sahi Indian Standard Time (IST +05:30) set karna
    ist = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(ist).strftime("%Y%m%d")
    
    parsed_items = []
    for p in programs:
        dt = datetime.strptime(f"{today} {p['time_str']}", "%Y%m%d %I:%M%p")
        parsed_items.append((dt, p["title"]))
        
    for i in range(len(parsed_items)):
        start_dt, title = parsed_items[i]
        
        # Agle program ka start time uthana
        if i + 1 < len(parsed_items):
            stop_dt = parsed_items[i + 1][0]
            # Agar agla program agle din (midnight ke baad) ka ho
            if stop_dt <= start_dt:
                stop_dt += timedelta(days=1)
        else:
            stop_dt = start_dt + timedelta(hours=2, minutes=30)
            
        prog = ET.SubElement(tv, "programme", {
            "start": start_dt.strftime("%Y%m%d%H%M%S +0530"),
            "stop": stop_dt.strftime("%Y%m%d%H%M%S +0530"),
            "channel": CHANNEL_ID
        })
        title_el = ET.SubElement(prog, "title", {"lang": "hi"})
        title_el.text = title
        desc_el = ET.SubElement(prog, "desc", {"lang": "hi"})
        desc_el.text = "Hindi Bollywood Movie on Goldmines Bollywood"

    # XML ko GZIP (.xml.gz) mein save karna
    xml_bytes = ET.tostring(tv, encoding="utf-8", xml_declaration=True)
    with gzip.open("epg.xml.gz", "wb") as f:
        f.write(xml_bytes)

if __name__ == "__main__":
    data = fetch_schedule()
    if not data:
        print("Warning: Koi schedule nahi mila!")
    else:
        build_xmltv(data)
        print(f"Success: {len(data)} programs ke saath epg.xml.gz update ho gaya!")
