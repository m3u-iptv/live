import requests, gzip, time, os

URLS = [
  "https://epg.pw/xmltv/epg_IN.xml",
  "http://epg.pw/xmltv/epg_IN.xml",
  "https://epg.pw/xmltv/epg_IN.xml.gz",
]

HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "Accept": "*/*",
  "Accept-Encoding": "gzip, deflate",
  "Referer": "https://epg.pw/",
}

data = None
for url in URLS:
    print("Try:", url)
    for i in range(3):
        try:
            r = requests.get(url, timeout=180, headers=HEADERS)
            print("Status:", r.status_code, "Size:", len(r.content))
            if r.status_code == 200 and len(r.content) > 10000:
                data = r.content
                break
        except Exception as e:
            print("Error:", e)
        time.sleep(10)
    if data:
        break

if not data:
    print("epg.pw DOWN hai, Purani file hi rakhenge - FAIL NAHI HONGE")
    # Fail mat karo, purani file rehne do
    exit(0)

# Agar pehle se .gz aaya hai to direct save karo
if data[:2] == b'\x1f\x8b':
    open("epg.xml.gz","wb").write(data)
    print("Direct .gz save ho gaya")
else:
    with gzip.open("epg.xml.gz", "wb", compresslevel=9) as f:
        f.write(data)
    print("xml -> gz ban gaya, Size:", os.path.getsize("epg.xml.gz"))
