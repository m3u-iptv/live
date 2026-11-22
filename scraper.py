import gzip
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

IST = timezone(timedelta(hours=5, minutes=30))

def ms_to_xmltv_time(ms):
    dt = datetime.fromtimestamp(int(ms) / 1000.0, tz=IST)
    return dt.strftime("%Y%m%d%H%M%S +0530")

def create_xmltv():
    captured_responses = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # असली Revlet API से आने वाले डेटा को पकड़ें
        def handle_response(response):
            url = response.url
            if "api-apac.revlet.net" in url and response.status == 200:
                try:
                    data = response.json()
                    if data.get("status"):
                        if "tvguide/channels" in url:
                            captured_responses["channels"] = data.get("response", {})
                        elif "static/tvguide" in url:
                            captured_responses["tvguide"] = data.get("response", {})
                        elif "page/content" in url and "tvguide" in url:
                            captured_responses["page_content"] = data.get("response", {})
                except Exception:
                    pass

        page.on("response", handle_response)
        page.goto("https://aasthatv.tv", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(7000)
        browser.close()

    tv = ET.Element("tv", {"generator-info-name": "Aastha-EPG-Original"})
    channel_map = {}

    # 1. सभी 11 चैनलों की लिस्ट बनाएं
    raw_channels = captured_responses.get("channels", {})
    ch_list = raw_channels.get("data", []) if isinstance(raw_channels, dict) else raw_channels
    for ch in ch_list:
        ch_id = str(ch.get("id", ""))
        ch_name = ch.get("name") or ch.get("title") or f"Aastha {ch_id}"
        if ch_id:
            channel_map[ch_id] = ch_name
            ch_el = ET.SubElement(tv, "channel", {"id": f"aastha_{ch_id}"})
            ET.SubElement(ch_el, "display-name").text = ch_name

    # 2. सभी चैनलों के प्रोग्राम और सटीक समय जोड़ें
    raw_progs = captured_responses.get("tvguide") or captured_responses.get("page_content") or {}
    prog_list = raw_progs.get("data", []) if isinstance(raw_progs, dict) else raw_progs

    prog_count = 0
    for item in prog_list:
        ch_id = str(item.get("channelId") or item.get("channel_id") or "")
        progs = item.get("programs") or item.get("programmes") or item.get("sectionData", {}).get("data", []) or [item]
        
        for p_item in progs:
            start_ms = p_item.get("startTime") or p_item.get("start_time")
            end_ms = p_item.get("endTime") or p_item.get("end_time")
            title_txt = p_item.get("title") or p_item.get("name") or p_item.get("programName")
            desc_txt = p_item.get("description") or p_item.get("synopsis") or ""
            p_ch_id = str(p_item.get("channelId") or p_item.get("channel_id") or ch_id)

            if start_ms and end_ms and title_txt and p_ch_id:
                if p_ch_id not in channel_map:
                    channel_map[p_ch_id] = f"Aastha {p_ch_id}"
                    ch_el = ET.SubElement(tv, "channel", {"id": f"aastha_{p_ch_id}"})
                    ET.SubElement(ch_el, "display-name").text = channel_map[p_ch_id]

                prog_el = ET.SubElement(tv, "programme", {
                    "start": ms_to_xmltv_time(start_ms),
                    "stop": ms_to_xmltv_time(end_ms),
                    "channel": f"aastha_{p_ch_id}"
                })
                ET.SubElement(prog_el, "title", {"lang": "hi"}).text = str(title_txt)
                if desc_txt:
                    ET.SubElement(prog_el, "desc", {"lang": "hi"}).text = str(desc_txt)
                prog_count += 1

    # यदि API की कोई Key अलग हो, तो डीबग फ़ाइल सेव करें
    if prog_count == 0 and captured_responses:
        with open("debug_sample.json", "w", encoding="utf-8") as df:
            json.dump(captured_responses, df, ensure_ascii=False, indent=2)

    xml_data = ET.tostring(tv, encoding="utf-8", xml_declaration=True)
    with gzip.open("epg.xml.gz", "wb") as f:
        f.write(xml_data)
    print(f"Success! Channels: {len(channel_map)}, Programs: {prog_count}")

if __name__ == "__main__":
    create_xmltv()
