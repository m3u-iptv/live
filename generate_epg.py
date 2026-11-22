import gzip
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# आपके सभी 11 चैनलों की लिस्ट (Website ID -> आपका tvg-id)
CHANNELS = {
    "aastha-hd": "AasthaHD",
    "aastha-bhajan": "AasthaBhajan",
    "dharam-sandesh": "DharamSandesh",
    "vedic": "Vedic",
    "aastha-prime": "AasthaPrime",
    "aastha-gujarati": "AasthaGujarati",
    "aastha-tamil": "AasthaTamil",
    "aastha-telugu": "AasthaTelugu",
    "aastha-kannada": "AasthaKannada",
    "aastha-uk-europe": "AasthaUKEurope",
    "aastha-usa-canada": "AasthaUSACanada"
}

def build_epg():
    tv = ET.Element("tv", {"generator-info-name": "AasthaAutoEPG"})

    # 1. सभी चैनलों के टैग जोड़ें
    for site_id, tvg_id in CHANNELS.items():
        channel_el = ET.SubElement(tv, "channel", id=tvg_id)
        display_name = ET.SubElement(channel_el, "display-name")
        display_name.text = tvg_id

    # 2. वेबसाइट की API से शेड्यूल डेटा लाएं
    # (यहाँ Chrome Network टैब से निकाला गया असली API URL डालें)
    API_URL = "https://aasthatv.tv/tvguide"  # <-- इसे असली URL से बदलें
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(API_URL, headers=headers, timeout=15)
        data = response.json()

        # API के JSON डेटा के अनुसार नीचे की फील्ड्स (channel, start, stop, title) एडजस्ट करें
        for item in data.get("schedules", []):
            site_channel = item.get("channel_slug")
            if site_channel in CHANNELS:
                tvg_id = CHANNELS[site_channel]
                
                # XMLTV टाइम फॉर्मेट: YYYYMMDDHHMMSS +0530
                start_time = item.get("start_time") 
                stop_time = item.get("end_time")
                
                prog_el = ET.SubElement(
                    tv, "programme",
                    start=f"{start_time} +0530",
                    stop=f"{stop_time} +0530",
                    channel=tvg_id
                )
                title_el = ET.SubElement(prog_el, "title", lang="hi")
                title_el.text = item.get("program_name", "Aastha Program")
                
                desc_el = ET.SubElement(prog_el, "desc", lang="hi")
                desc_el.text = item.get("description", "")

    except Exception as e:
        print(f"Error fetching data: {e}")

    # 3. epg.xml.gz फाइल जनरेट करें
    xml_bytes = ET.tostring(tv, encoding="utf-8", xml_declaration=True)
    with gzip.open("epg.xml.gz", "wb") as f:
        f.write(xml_bytes)

if __name__ == "__main__":
    build_epg()
