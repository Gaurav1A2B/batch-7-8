import socket
import time
import math
import random

HOST = "127.0.0.1"
PORT = 5000

def checksum(sentence):
    cs = 0
    for c in sentence:
        cs ^= ord(c)
    return f"{cs:02X}"

def gga(lat, lon, alt, sats, hdop):
    lat_d = int(abs(lat))
    lat_m = (abs(lat) - lat_d) * 60
    lat_h = "N" if lat >= 0 else "S"

    lon_d = int(abs(lon))
    lon_m = (abs(lon) - lon_d) * 60
    lon_h = "E" if lon >= 0 else "W"

    s = (
        f"GNGGA,123519,"
        f"{lat_d:02d}{lat_m:07.4f},{lat_h},"
        f"{lon_d:03d}{lon_m:07.4f},{lon_h},"
        f"4,{sats},{hdop:.1f},{alt:.1f},M,0.0,M,,"
    )
    return f"${s}*{checksum(s)}\r\n"

def gsv():
    sats = []
    for prn in range(1, 9):
        el = random.randint(10, 80)
        az = random.randint(0, 359)
        snr = random.randint(25, 48)
        sats.append((prn, el, az, snr))

    lines = []
    for i in range(0, len(sats), 4):
        block = sats[i:i+4]
        parts = ["GPGSV", "2", str(i//4+1), str(len(sats))]
        for s in block:
            parts += [f"{s[0]:02d}", str(s[1]), str(s[2]), str(s[3])]
        base = ",".join(parts)
        lines.append(f"${base}*{checksum(base)}\r\n")
    return lines

print("Starting NMEA TCP server on 127.0.0.1:5000")

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.bind((HOST, PORT))
srv.listen(1)

conn, addr = srv.accept()
print("Client connected:", addr)

lat0, lon0 = 28.6139, 77.2090
t = 0.0

while True:
    # simulate slow movement
    lat = lat0 + 0.00001 * math.sin(t)
    lon = lon0 + 0.00001 * math.cos(t)
    alt = 215 + math.sin(t) * 0.5

    conn.sendall(gga(lat, lon, alt, 12, 0.8).encode())
    for l in gsv():
        conn.sendall(l.encode())

    t += 0.2
    time.sleep(1)
