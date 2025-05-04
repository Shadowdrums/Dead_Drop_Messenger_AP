# 📡 Dead Drop Messenger AP

The **Dead Drop Messenger** is a rogue Access Point tool for ethical red team field operations, built to simulate captive portal behavior and covertly collect messages from connecting devices.

Once a user connects to the SSID (which can be a one-time signal like `📡 S3cr3tMsg:CallNow`), they are redirected to a fake login page where they can leave a message. If the server has an internet uplink, the system enables outbound forwarding and optionally limits user access to a YouTube Rickroll.

---

## 🔧 Features

- Broadcasts covert SSID messages (like a digital dead drop)
- Rogue AP with DNS/DHCP via `dnsmasq` and `hostapd`
- Captive portal via Flask web server
- Logs user messages, IP, User-Agent, and optional ARP info
- Detects internet uplink automatically
- Redirects HTTP traffic to YouTube (or blocks all else)
- Logs everything to `messages.txt` and `access.log`

---

## 🖥️ Requirements

Install required Python libraries:

```bash
pip install -r requirements.txt
```
Install required system tools:
```bash
sudo apt install hostapd dnsmasq iptables
```
## 📁 Project Structure
```bash
DeadDropMessenger/
├── dead_drop_messenger.py   # Main AP launcher
├── web_portal.py            # Flask captive portal backend
├── portal.html              # Web form for message input
├── messages.txt             # User-submitted messages
├── access.log               # Connection and system logs
├── requirements.txt
└── README.md
```
## 🚀 How to Use
1. Connect an external WiFi adapter capable of AP mode.

2. Run the messenger with root:
```bash
sudo python3 dead_drop_messenger.py
```
3. Select your WiFi interface and set your SSID dead drop message.

4. Devices that connect will be redirected to a portal.

5. After submitting, if internet is available, they’ll get Rickrolled 😈
## 🔐 Use Cases (Red Team / Field Ops)
. Leave covert instructions or signals via SSID

. Collect anonymous drops in the field

. Trigger captive portals for social engineering scenarios

. Simulate hotel/public Wi-Fi behavior during a physical engagement

# 🛡️ MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**Disclaimer**: The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

# 🛡️ Disclaimer

ShadowDrums and ShadowTEAM members will not be held liable for any misuse of this source code, program, or software. It is the responsibility of the user to ensure that their use of this software complies with all applicable laws and regulations. By using this software, you agree to indemnify and hold harmless Shadowdrums and ShadowTEAM members from any claims, damages, or liabilities arising from your use or misuse of the software.
