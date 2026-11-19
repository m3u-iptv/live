import os, glob

# Purani index.m3u ko bachake rakho
old_channels = set()
if os.path.exists("index.m3u"):
    with open("index.m3u", encoding="utf-8", errors="ignore") as f:
        old_channels = set(f.read().splitlines())

new_lines = []
# streams folder ke andar jitni bhi .m3u hai sab uthao
for file in glob.glob("streams/**/*.m3u", recursive=True) + glob.glob("*.m3u"):
    if file == "index.m3u":
        continue
    with open(file, encoding="utf-8", errors="ignore") as f:
        for line in f.read().splitlines():
            if line.startswith("#EXTM3U"):
                continue
            if line not in old_channels and line.strip() != "":
                new_lines.append(line)

if new_lines:
    with open("index.m3u", "a", encoding="utf-8") as f:
        for line in new_lines:
            f.write(line + "\n")
    print(f"HO GAYA SIR - {len(new_lines)} Nayi Lines Add Hui")
else:
    print("Koi Naya Channel Nahi Mila Sir")
