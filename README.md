# 🛠️ ShadowBinder - Payload Binding & Delivery Toolkit

**ShadowBinder** is a GUI-based tool made for **Kali Linux** that helps you generate, bind, and host Windows Meterpreter payloads. It's designed for **red team testing**, **ethical hacking**, and **research** purposes.

---

## 🔐 Features

- 💽 Easy-to-use Tkinter GUI
- 🧪 Generates `windows/meterpreter/reverse_tcp` payload
- 📌 Binds payload to:
  - `.jpg`, `.pdf`, `.mp4`, `.mp3`, `.docx` (user-selected)
- 🎨 Optional `.ico` file to change payload icon
- 🌐 Auto-detects LHOST or allows manual input
- ☁️ Automatically hosts payload via Apache server
- 🔔 Sends email alerts when payload is hosted
- 📡 One-click Metasploit listener (handler)

---

## 🧰 Requirements

Install dependencies using:

```bash
sudo apt update
sudo apt install metasploit-framework apache2 python3-tk python3-pil python3-pil.imagetk xterm wine -y
```

> Note: For icon changing to work, place `rcedit.exe` (Windows binary) in the same directory and ensure Wine is installed.

---

## 🚀 How to Use

1. **Clone the repository**:
   ```bash
   git clone https://github.com/darksoham/ShadowBinder.git
   cd shadowbinder
   ```

2. **Run the GUI**:
   ```bash
   python3 PBinderGui.py
   ```

3. **Inside the Tool**:
   - Set `LHOST` and `LPORT`
   - Select file to bind (e.g. image, PDF, etc.)
   - Choose optional `.ico` file
   - Click "Generate & Host Payload"
   - Click "Start Listener" to open Metasploit handler

---

## 📧 Email Alerts (Optional)

Create a file named `email_config.json`:

```json
{
  "sender_email": "your-email@gmail.com",
  "sender_password": "your-password",
  "recipient_email": "receiver@example.com",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587
}
```

---

## ⚠️ Disclaimer

> This tool is made for **educational and authorized penetration testing only**. Misuse of this tool for unauthorized access or malicious purposes is **illegal** and **unethical**.

---

## 👤 Author

Created by **YourName**  
🔗 GitHub: [github.com/yourusername](https://github.com/darksoham)
