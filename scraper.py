import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

URL = "https://aasthatv.tv/tvguide"
headers = {"User-Agent": "Mozilla/5.0"}

r = requests.get(URL, headers=headers, timeout=30)
soup = BeautifulSoup(r.text, "html.parser")

tv = ET.Element("tv", {"generator-info-name": "Aastha EPG"})

# Sirf Isi Site Wale 11 Channels
channels = [
  "Aastha HD",
  "Aastha Bhajan",
  "Dharam Sandesh",
  "Vedic",
  "Aastha Prime",
  "Aastha Gujarati",
  "Aastha Tamil",
  "Aastha Telugu",
  "Aastha Kannada",
  "Aastha UK Europe",
  "Aastha USA Canada"
]

for ch in channels:
    ch_id = ch.replace(" ", "").replace("/", "")
    c = ET.SubElement(tv, "channel", {"id": ch_id})
    ET.SubElement(c, "display-name").text = ch

today = datetime.now()
for ch in channels:
    ch_id = ch.replace(" ", "").replace("/", "")
    for h in range(24):
        start = today.replace(hour=h, minute=0, second=0, microsecond=0)
        stop = start + timedelta(hours=1)
        p = ET.SubElement(tv, "programme", {
            "start": start.strftime("%Y%m%d%H%M%S +0530"),
            "stop": stop.strftime("%Y%m%d%H%M%S +0530"),
            "channel": ch_id
        })
        ET.SubElement(p, "title").text = ch

tree = ET.ElementTree(tv)
tree.write("aastha.xml", encoding="utf-8", xml_declaration=True)
print("aastha.xml ban gaya! 11 channels done!")
