#!/usr/bin/env python3
import os
import subprocess
import time
import sys

FLASK_PORT = 8080
INTERFACE_IP = "192.168.77.1"
SUBNET = "192.168.77.0/24"
DNS_RANGE = "192.168.77.10,192.168.77.50,12h"
PORTAL_PATH = os.path.join(os.getcwd(), "portal.html")

def run(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_wifi_adapters():
    out = subprocess.check_output("iw dev | grep Interface | awk '{print $2}'", shell=True).decode().splitlines()
    return [i.strip() for i in out if i.strip()]

def configure_ap(interface, ssid):
    print("[+] Setting up interface and configuration...")
    run(f"ip link set {interface} down")
    run(f"ip addr flush dev {interface}")
    run(f"ip link set {interface} up")
    run(f"ip addr add {INTERFACE_IP}/24 dev {interface}")

    with open("hostapd.conf", "w") as f:
        f.write(f"""
interface={interface}
driver=nl80211
ssid={ssid}
hw_mode=g
channel=6
auth_algs=1
ignore_broadcast_ssid=0
""")

    with open("dnsmasq.conf", "w") as f:
        f.write(f"""
interface={interface}
dhcp-range={DNS_RANGE}
address=/#/{INTERFACE_IP}
port=53
log-queries
log-dhcp
""")

    run("iptables -t nat -F")
    run(f"iptables -t nat -A PREROUTING -i {interface} -p tcp --dport 80 -j REDIRECT --to-port {FLASK_PORT}")
    run(f"iptables -t nat -A PREROUTING -i {interface} -p udp --dport 53 -j REDIRECT --to-port 53")

def start_services():
    print("[+] Launching hostapd and dnsmasq...")
    hostapd = subprocess.Popen("hostapd hostapd.conf", shell=True)
    time.sleep(2)
    dnsmasq = subprocess.Popen("dnsmasq -C dnsmasq.conf", shell=True)
    return hostapd, dnsmasq

def start_flask():
    print("[+] Starting Flask captive portal...")
    return subprocess.Popen("python3 web_portal.py", shell=True)

def cleanup(interface):
    print("\n[!] Cleaning up...")
    run("pkill hostapd")
    run("pkill dnsmasq")
    run("pkill -f web_portal.py")
    run("iptables -t nat -F")
    run(f"ip addr flush dev {interface}")
    run(f"ip link set {interface} down")
    run(f"ip link set {interface} up")
    print("[*] Done.")

def main():
    if os.geteuid() != 0:
        print("[!] Please run as root.")
        sys.exit(1)

    adapters = get_wifi_adapters()
    if not adapters:
        print("[!] No wireless adapters found.")
        sys.exit(1)

    print("📡 Dead Drop Messenger – Rogue AP + Captive Portal\n")
    for i, iface in enumerate(adapters):
        print(f"  [{i}] {iface}")
    choice = input("\nSelect interface by number: ").strip()

    if not choice.isdigit() or int(choice) >= len(adapters):
        print("[!] Invalid choice.")
        sys.exit(1)

    interface = adapters[int(choice)]
    ssid = input("Enter SSID message (max 32 chars): ").strip()
    if len(ssid) > 32:
        print("[!] SSID too long.")
        sys.exit(1)

    configure_ap(interface, ssid)
    hostapd, dnsmasq = start_services()
    flask = start_flask()

    try:
        print("[*] Rogue AP running. Press CTRL+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup(interface)

if __name__ == "__main__":
    main()
