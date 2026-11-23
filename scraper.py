import gzip
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import requests

# Yahan apne channels ke ID aur URL add karein
CHANNELS = {
    "sony.vizha.hd": {
        "name": "SONY Vizha HD",
        "url": "https://www.epgschedule.com/channel/sony-vizha-hd/",
    },
    # Aur channels add karne ke liye neeche copy-paste karein:
    # "adithya.tv": {
    #     "name": "Adithya TV",
    #     "url": "https://epgschedule.com",
    # },
}

IST = timezone(timedelta(hours=5, minutes=30))
TIME_PATTERN = re.compile(r"^(\d{1,2}:\d{2}\s*[AP]M)\s*[–-]\s*(\d{1,2}:\d{2}\s*[AP]M)$", re.I)


def parse_schedule(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    lines = [line.strip() for line in soup.stripped_strings if line.strip()]

    # "Today's Schedule" section se parsing shuru karein
    start_idx = 0
    for i, line in enumerate(lines):
        if "Today's Schedule" in line:
            start_idx = i + 1
            break

    programs = []
    current_date = datetime.now(IST).replace(hour=0, minute=0, second=0, microsecond=0)
    last_start_minutes = -1

    for i in range(start_idx, len(lines)):
        match = TIME_PATTERN.match(lines[i])
        if match and i >= 2:
            title = lines[i - 2]
            desc = lines[i - 1]
            start_str, end_str = match.group(1), match.group(2)

            # Time parse karein
            s_time = datetime.strptime(start_str.upper(), "%I:%M %p")
            e_time = datetime.strptime(end_str.upper(), "%I:%M %p")

            start_minutes = s_time.hour * 60 + s_time.minute
            # Agar time wapas 12:00 AM par aaye toh agla din (Tomorrow) maan lein
            if last_start_minutes != -1 and start_minutes < last_start_minutes:
                current_date += timedelta(days=1)
            last_start_minutes = start_minutes

            start_dt = current_date.replace(hour=s_time.hour, minute=s_time.minute)
            end_dt = current_date.replace(hour=e_time.hour, minute=e_time.minute)
            if end_dt <= start_dt:
                end_dt += timedelta(days=1)

            programs.append({
                "title": title,
                "desc": desc,
                "start": start_dt.strftime("%Y%m%d%H%M%S +0530"),
                "stop": end_dt.strftime("%Y%m%d%H%M%S +0530"),
            })

        # Schedule list khatam hone par ruk jayein
        if "Related Channels" in lines[i]:
            break

    return programs


def build_epg():
    tv = ET.Element("tv", {"generator-info-name": "Custom-EPGSchedule-Scraper"})

    for ch_id, info in CHANNELS.items():
        ch_elem = ET.SubElement(tv, "channel", {"id": ch_id})
        disp = ET.SubElement(ch_elem, "display-name")
        disp.text = info["name"]

        try:
            progs = parse_schedule(info["url"])
            for p in progs:
                prog_elem = ET.SubElement(
                    tv,
                    "programme",
                    {"start": p["start"], "stop": p["stop"], "channel": ch_id},
                )
                t_elem = ET.SubElement(prog_elem, "title", {"lang": "en"})
                t_elem.text = p["title"]
                d_elem = ET.SubElement(prog_elem, "desc", {"lang": "en"})
                d_elem.text = p["desc"]
            print(f"Success: {info['name']} ({len(progs)} shows)")
        except Exception as e:
            print(f"Error scraping {info['name']}: {e}")

    xml_bytes = ET.tostring(tv, encoding="utf-8", xml_declaration=True)
    with gzip.open("epg.xml.gz", "wb") as f:
        f.write(xml_bytes)


if __name__ == "__main__":
    build_epg()
      
