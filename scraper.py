import gzip
import gzip
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import requests

CHANNELS = {
    "and.pictures": {
        "name": "And Pictures",
        "url": "https://www.epgschedule.com/channel/andpictures/",
    },
    "and.pictures.hd": {
        "name": "And Pictures HD",
        "url": "https://www.epgschedule.com/channel/andpictures-hd/",
    },
    "and.tv": {
        "name": "And TV",
        "url": "https://www.epgschedule.com/channel/andtv/",
    },
     "and.tv.hd": {
        "name": "And TV HD",
        "url": "https://www.epgschedule.com/channel/andtv-hd/",
    },
     "and.xplor.hd": {
        "name": "And Xplor HD",
        "url": "https://www.epgschedule.com/channel/andxplor-hd/",
    },
     "10.tv": {
        "name": "10 TV",
        "url": "https://www.epgschedule.com/channel/10-tv/",
    },
     "24.ghanta": {
        "name": "24 GHANTA",
        "url": "https://www.epgschedule.com/channel/24-ghanta/",
    },
    "4tv.news": {
        "name": "4TV NEWS ",
        "url": "https://www.epgschedule.com/channel/4tv-news/",
    },
    "7s.music": {
        "name": "7S Music",
        "url": "https://www.epgschedule.com/channel/7s-music/",
    },
    "9x.jalwa": {
        "name": "9X Jalwa",
        "url": "https://www.epgschedule.com/channel/9x-jalwa/",
    },
    "9x.tashan": {
        "name": "9X Tashan",
        "url": "https://www.epgschedule.com/channel/9x-tashan/",
    },
    "9xm": {
        "name": "9XM",
        "url": "https://www.epgschedule.com/channel/9xm/",
    },
    "aadinath.tv": {
        "name": "Aadinath TV",
        "url": "https://www.epgschedule.com/channel/aadinath-tv/",
    },
    "aaj.ki.khabar": {
        "name": "Aaj Ki Khabar",
        "url": "https://www.epgschedule.com/channel/aaj-ki-khabar/",
    },
    "aaj.tak": {
        "name": "Aaj Tak",
        "url": "https://www.epgschedule.com/channel/aaj-tak/",
    },
    "aaj.tak.hd": {
        "name": "Aaj Tak HD",
        "url": "https://www.epgschedule.com/channel/aaj-tak-hd/",
    },
    "aakash.aath": {
        "name": "Aakash Aath",
        "url": "https://www.epgschedule.com/channel/aakash-aath/",
    },
    "aaseervatham.tv": {
        "name": "Aaseervatham TV",
        "url": "https://www.epgschedule.com/channel/aaseervatham-tv/",
    },
    "aastha": {
        "name": "Aastha",
        "url": "https://www.epgschedule.com/channel/aastha/",
    },
    "abc.australia": {
        "name": "ABC Australia",
        "url": "https://www.epgschedule.com/channel/abc-australia/",
    },
    "abn.andhra.jyothy": {
        "name": "ABN Andhra Jyothy",
        "url": "https://www.epgschedule.com/channel/abn-andhra-jyothy/",
    },
    "abp.ananda": {
        "name": "ABP Annada",
        "url": "https://www.epgschedule.com/channel/abp-ananda/",
    },
    "abp.asmita": {
        "name": "ABP Asmita",
        "url": "https://www.epgschedule.com/channel/abp-asmita/",
    },
    "abp.ganga": {
        "name": "ABP Ganga",
        "url": "https://tvgenie.in/abp-ganga-schedule",
    },
    "abp.majha": {
        "name": "ABP Majha",
        "url": "https://www.epgschedule.com/channel/abp-majha/",
    },
    "abp.news": {
        "name": "ABP News",
        "url": "https://www.epgschedule.com/channel/abp-news/",
    },
    "action.cinema": {
        "name": "Action Cinema",
        "url": "https://www.epgschedule.com/channel/action-cinema/",
    },
    "ad.free.anime": {
        "name": "AD Free Anime",
        "url": "https://www.epgschedule.com/channel/ad-free-anime/",
    },
    "adithya.tv": {
        "name": "Adithya TV",
        "url": "https://www.epgschedule.com/channel/adithya-tv/",
    },
    "al.jazeera": {
        "name": "AL Jazeera",
        "url": "https://www.epgschedule.com/channel/al-jazeera/",
    },
    "alankar": {
        "name": "Alankar",
        "url": "https://www.epgschedule.com/channel/alankar/",
    },
    "alif.laila": {
        "name": "Alif Laila",
        "url": "https://www.epgschedule.com/channel/alif-laila/",
    },
    "all.times.movies": {
        "name": "ALL Times MOVIES",
        "url": "https://www.epgschedule.com/channel/all-times-movies/",
    },
    "amrita.tv": {
        "name": "Amrita TV",
        "url": "https://www.epgschedule.com/channel/amrita-tv/",
    },
    "anaadi.tv": {
        "name": "Anaadi TV",
        "url": "https://www.epgschedule.com/channel/anaadi-tv/",
    },
    "anb.news": {
        "name": "ANB News",
        "url": "https://www.epgschedule.com/channel/anb-news/",
    },
    "sony.aath": {
        "name": "SONY AATH",
        "url": "https://www.epgschedule.com/channel/sony-aath/",
    },
    "SonyBBCEarth.in@HD": {
        "name": "SONY BBC EARTH HD",
        "url": "https://www.epgschedule.com/channel/sony-bbc-earth-hd/",
    },
    "SonyBBCEarth.in@SD": {
        "name": "SONY BBC EARTH",
        "url": "https://www.epgschedule.com/channel/sony-bbc-earth/",
    },
    "SET.in@HD": {
        "name": "SET HD",
        "url": "https://www.epgschedule.com/channel/set-hd/",
    },
    "SET.in@SD": {
        "name": "SET",
        "url": "https://www.epgschedule.com/channel/set/",
    },
    "sony.marathi": {
        "name": "SONY MARATHI",
        "url": "https://www.epgschedule.com/channel/sony-marathi/",
    },
    "sony.max.1": {
        "name": "SONY MAX 1",
        "url": "https://www.epgschedule.com/channel/sony-max-1/",
    },
    "sony.max.2": {
        "name": "SONY MAX 2",
        "url": "https://www.epgschedule.com/channel/sony-max-2/",
    },
    "sony.max.hd": {
        "name": "SONY MAX HD",
        "url": "https://www.epgschedule.com/channel/sony-max-hd/",
    },
    "sony.max": {
        "name": "SONY MAX",
        "url": "https://www.epgschedule.com/channel/sony-max/",
    },
    "sony.pal": {
        "name": "Sony Pal",
        "url": "https://www.epgschedule.com/channel/sony-pal/",
    },
    "sony.pix.hd": {
        "name": "SONY PIX HD",
        "url": "https://www.epgschedule.com/channel/sony-pix-hd/",
    },
    "sony.pix": {
        "name": "SONY PIX",
        "url": "https://www.epgschedule.com/channel/sony-pix/",
    },
    "sony.sab": {
        "name": "SONY SAB",
        "url": "https://www.epgschedule.com/channel/sony-sab/",
    },
    "sony.sab.hd": {
        "name": "SONY SAB HD",
        "url": "https://www.epgschedule.com/channel/sony-sab-hd/",
    },
    "sony.sports.1.hd": {
        "name": "SONY SPORTS 1 HD",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-1-hd/",
    },
    "sony.sports.1": {
        "name": "SONY SPORTS 1",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-1/",
    },
    "sony.sports.2.hd": {
        "name": "SONY SPORTS 2 HD",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-2-hd/",
    },
    "sony.sports.2": {
        "name": "SONY SPORTS 2",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-2/",
    },
    "sony.sports.3.hindi.hd": {
        "name": "SONY SPORTS 3 HINDI HD",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-3-hindi-hd/",
    },
    "sony.sports.3.hindi": {
        "name": "SONY SPORTS 3 HINDI",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-3-hindi/",
    },
    "sony.sports.4.kannada": {
        "name": "SONY SPORTS 4 KANNADA",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-4-kannada/",
    },
    "sony.sports.4.tamil": {
        "name": "SONY SPORTS 4 TAMIL",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-4-tamil/",
    },
    "sony.sports.4.telugu": {
        "name": "SONY SPORTS 4 TELUGU",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-4-telugu/",
    },
    "sony.sports.5.hd": {
        "name": "SONY SPORTS 5 HD",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-5-hd/",
    },
    "sony.sports.5": {
        "name": "SONY SPORTS 5",
        "url": "https://www.epgschedule.com/channel/sony-sports-ten-5/",
    },
    "sony.wah": {
        "name": "SONY WAH",
        "url": "https://www.epgschedule.com/channel/sony-wah/",
    },
    "sony.yay": {
        "name": "SONY YAY!",
        "url": "https://www.epgschedule.com/channel/sony-yay/",
    },
    "sony.vizha.hd": {
        "name": "SONY Vizha HD",
        "url": "https://www.epgschedule.com/channel/sony-vizha-hd/",
    },
    "sony.vizha": {
        "name": "SONY Vizha",
        "url": "https://www.epgschedule.com/channel/sony-vizha/",
    },
     "star.bharat.hd": {
        "name": "STAR BHARAT HD",
        "url": "https://www.epgschedule.com/channel/star-bharat-hd/",
    },
     "star.bharat": {
        "name": "STAR BHARAT",
        "url": "https://www.epgschedule.com/channel/star-bharat/",
    },
    "star.gold.hd": {
        "name": "STAR GOLD HD",
        "url": "https://www.epgschedule.com/channel/star-gold-hd/",
    },
     "star.gold": {
        "name": "STAR GOLD",
        "url": "https://www.epgschedule.com/channel/star-gold/",
    },
    "star.gold.2.hd": {
        "name": "STAR GOLD 2 HD",
        "url": "https://www.epgschedule.com/channel/star-gold-2-hd/",
    },
     "star.gold.2": {
        "name": "STAR GOLD 2",
        "url": "https://www.epgschedule.com/channel/star-gold-2/",
    },
     "star.gold.romance": {
        "name": "STAR GOLD ROMANCE",
        "url": "https://www.epgschedule.com/channel/star-gold-romance/",
    },
    "star.gold.select.hd": {
        "name": "STAR GOLD SELECT HD",
        "url": "https://www.epgschedule.com/channel/star-gold-select-hd/",
    },
    "star.gold.select": {
        "name": "STAR GOLD SELECT",
        "url": "https://www.epgschedule.com/channel/star-gold-select/",
    },
    "star.gold.thrills": {
        "name": "STAR GOLD THRILLS",
        "url": "https://www.epgschedule.com/channel/star-gold-thrills/",
    },
    "zee.cinema.hd": {
        "name": "ZEE CINEMA HD",
        "url": "https://www.epgschedule.com/channel/zee-cinema-hd/",
    },
    "zee.cinema": {
        "name": "ZEE CINEMA",
        "url": "https://www.epgschedule.com/channel/zee-cinema/",
    },
}

IST = timezone(timedelta(hours=5, minutes=30))
TIME_PATTERN = re.compile(r"^(\d{1,2}:\d{2}\s*[AP]M)\s*[–-]\s*(\d{1,2}:\d{2}\s*[AP]M)$", re.I)


def parse_schedule(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=25)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    lines = [line.strip() for line in soup.stripped_strings if line.strip()]

    # "Today's Schedule" ke baad se shuru karein
    start_idx = 0
    for i, line in enumerate(lines):
        if "Today's Schedule" in line:
            start_idx = i + 1
            break

    # "Add Channel to Favorites on Telegram" jaise buttons skip karein
    while start_idx < len(lines) and (
        "Share on WhatsApp" in lines[start_idx]
        or "Add Channel to Favorites" in lines[start_idx]
    ):
        start_idx += 1

    programs = []
    today_date = datetime.now(IST).replace(hour=0, minute=0, second=0, microsecond=0)
    current_date = today_date
    last_start_minutes = -1
    block_start = start_idx

    for i in range(start_idx, len(lines)):
        if "Related Channels" in lines[i]:
            break

        match = TIME_PATTERN.match(lines[i])
        if match:
            chunk = lines[block_start:i]
            block_start = i + 1
            if not chunk:
                continue

            raw_title = chunk[0]
            # Agar "Started Yesterday" alag span/line mein ho toh merge karein
            if len(chunk) > 1 and chunk[1] == "Started Yesterday":
                raw_title = f"{raw_title} Started Yesterday"
                desc = " ".join(chunk[2:]) if len(chunk) > 2 else raw_title
            else:
                desc = " ".join(chunk[1:]) if len(chunk) > 1 else raw_title

            start_str, end_str = match.group(1), match.group(2)
            s_time = datetime.strptime(start_str.upper(), "%I:%M %p")
            e_time = datetime.strptime(end_str.upper(), "%I:%M %p")
            start_minutes = s_time.hour * 60 + s_time.minute

            if "Started Yesterday" in raw_title:
                title = raw_title.replace("Started Yesterday", "").strip()
                start_dt = (today_date - timedelta(days=1)).replace(
                    hour=s_time.hour, minute=s_time.minute
                )
                end_dt = today_date.replace(hour=e_time.hour, minute=e_time.minute)
                last_start_minutes = -1
            else:
                title = raw_title
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
    
