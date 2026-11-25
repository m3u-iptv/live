import gzip
import re
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

URL = "https://dishnews.in/goldmines-bollywood-channel-movie-schedule/"
CHANNEL_ID = "GoldminesBollywood.in"
CHANNEL_NAME = "Goldmines Bollywood"

def fetch_schedule():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Webpage ke text se lines nikalna
    lines = [line.strip() for line in soup.get_text().split("\n") if line.strip()]
    
    programs = []
    time_pattern = re.compile(r"^\d{2}:\d{2}(AM|PM)$", re.IGNORECASE)
    
    for i, line in enumerate(lines):
        if time_pattern.match(line):
            # Time se theek upar movie ka naam hota hai ("Hindi | Film" ko chhodkar)
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
    
    # Aaj ki date (IST +0530) ke hisaab se timings set karna
    today = datetime.now().strftime("%Y%m%d")
    parsed_items = []
    
    for p in programs:
        dt = datetime.strptime(f"{today} {p['time_str']}", "%Y%m%d %I:%M%p")
        parsed_items.append((dt, p["title"]))
        
    for i in range(len(parsed_items)):
        start_dt, title = parsed_items[i]
        # Agle program ka start time hi is program ka stop time hoga
        if i + 1 < len(parsed_items):
            stop_dt = parsed_items[i + 1][0]
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
    build_xmltv(data)
    print("epg.xml.gz generated successfully!")
