import requests, gzip, time

URL = "https://epg.pw/xmltv/epg_IN.xml"
HEADERS = {"User-Agent": "Mozilla/5.0"}

print("Download start...")
data = None
for i in range(3):
    try:
        r = requests.get(URL, timeout=180, headers=HEADERS)
        print("Status:", r.status_code, "Size:", len(r.content))
        if r.status_code == 200 and len(r.content) > 10000:
            data = r.content
            break
    except Exception as e:
        print("Retry", e)
    time.sleep(10)

if not data:
    print("FAIL - epg.pw se download nahi hua")
    exit(1)

# .xml ko .xml.gz banao - 40MB -> 3MB ho jayega
with gzip.open("epg.xml.gz", "wb", compresslevel=9) as f:
