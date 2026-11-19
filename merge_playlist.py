import os, glob

# Purani index.m3u ko bachake rakho
old_channels = set()
if os.path.exists("index.m3u"):
    with open("index.m3u", encoding="utf-8", errors="ignore") as f:
        old_channels = set(f.read().splitlines())
else:
    # Agar file nahi hai to nayi banao
    with open("index.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

new_lines = []
# streams folder ke andar jitni bhi .m3u hai sab uthao - andar + bahar dono
all_files = glob.glob("streams/**/*.m3u", recursive=True) + glob.glob("*.m3u") + glob.glob("iptv/**/*.m3u", recursive=True) + glob.glob("live/**/*.m3u", recursive=True)

for file in all_files:
    if file.endswith("index.m3u"):
        continue
    with open(file, encoding="utf-8", errors="ignore") as f:
        for line in f.read().splitlines():
            if line.startswith("#EXTM3U"):
                continue
            if line not in old_channels and line not in new_lines and line.strip() != "":
                new_lines.append(line)

if new_lines:
    with open("index.m3u", "a", encoding="utf-8") as f:
        for line in new_lines:
            f.write(line + "\n")
    print(f"HO GAYA SIR - {len(new_lines)} Nayi Lines Add Hui")
else:
    print("Koi Naya Channel Nahi Mila Sir")
