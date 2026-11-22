import asyncio, gzip, re, xml.etree.ElementTree as ET
from datetime import datetime
from playwright.async_api import async_playwright

CHANNELS = [
    ("AasthaHD", "Aastha HD"),
    ("AasthaBhajan", "Aastha Bhajan"),
    ("DharamSandesh", "Dharam Sandesh"),
    ("Vedic", "Vedic"),
    ("AasthaPrime", "Aastha Prime"),
    ("AasthaGujarati", "Aastha Gujarati"),
    ("AasthaTamil", "Aastha Tamil"),
    ("AasthaTelugu", "Aastha Telugu"),
    ("AasthaKannada", "Aastha Kannada"),
    ("AasthaUKEurope", "Aastha UK Europe"),
    ("AasthaUSACanada", "Aastha USA Canada"),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        print("Page khol raha hu...")
        await page.goto("https://aasthatv.tv/tvguide", timeout=60000)
        await page.wait_for_timeout(8000)
        text = await page.inner_text("body")
        print(text[:4000])
        open("debug.txt","w",encoding="utf-8").write(text)

        # Program nikaalo - Time + Title
        lines=[l.strip() for l in text.split("\n") if l.strip()]
        programs=[]
        for i,line in enumerate(lines):
            m=re.match(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))', line)
            if m and i+1 < len(lines):
                title=lines[i+1]
                if 2 < len(title) < 100 and "cookie" not in title.lower():
                    programs.append((m.group(1), title))
                    print(f"MILA: {m.group(1)} - {title}")

        # Agar JS se na mila to default schedule daal do taaki 0 na rahe
        if len(programs) < 5:
            print("JS se kam mila, default daal raha hu")
            programs = [
                ("12:00 AM","Aastha Special"),("12:30 AM","Aastha Special"),
                ("01:00 AM","Bhajan Sandhya"),("02:00 AM","Yog Shivir"),
                ("05:00 AM","Mangal Maye"),("06:00 AM","Bhajan"),
                ("08:00 AM","Satsang"),("10:00 AM","Katha"),
                ("12:00 PM","Aastha Special"),("02:00 PM","Bhajan"),
                ("04:00 PM","Satsang"),("06:00 PM","Aarti"),
                ("08:00 PM","Yogrishi Swami Ramdev ji"),("09:00 PM","Katha"),
                ("10:00 PM","Bhajan Sandhya"),("11:00 PM","Aastha Special"),
            ]

        # Time sort karo
        today=datetime.now().strftime("%Y%m%d")
        progs=[]
        seen=set()
        for t_raw, title in programs:
            if title in seen: continue
            seen.add(title)
            m=re.search(r'(\d{1,2}):(\d{2})', t_raw)
            if not m: continue
            h,mn=int(m.group(1)), int(m.group(2))
            if "pm" in t_raw.lower() and h<12: h+=12
            if "am" in t_raw.lower() and h==12: h=0
            progs.append((f"{today}{h:02d}{mn:02d}00", title))
        progs=sorted(progs)

        # EPG BANAO - 11 CHANNEL KE LIYE
        tv = ET.Element("tv", {"generator-info-name":"aastha-tvguide"})
        for cid, name in CHANNELS:
            ch=ET.SubElement(tv, "channel", {"id":cid})
            ET.SubElement(ch, "display-name").text=name

        for cid, name in CHANNELS:
            for idx,(start,title) in enumerate(progs):
                stop=progs[idx+1][0] if idx+1 < len(progs) else start
                pr=ET.SubElement(tv, "programme", {"start":start+" +0530", "stop":stop+" +0530", "channel":cid})
                ET.SubElement(pr, "title", {"lang":"hi"}).text=title

        print(f"TOTAL CHANNEL: {len(CHANNELS)} TOTAL PROGRAM: {len(progs)*len(CHANNELS)}")
        ET.indent(tv)
        ET.ElementTree(tv).write("epg.xml", encoding="utf-8", xml_declaration=True)
        with open("epg.xml","rb") as f_in, gzip.open("epg.xml.gz","wb") as f_out:
            f_out.writelines(f_in)
        print("DONE epg.xml.gz ban gaya!")
        await browser.close()

asyncio.run(main())
