import tkinter as tk
from tkinter import filedialog, scrolledtext
import os
import re
import sys
from PIL import Image, ImageTk

def resource_path(relative_path):
    """ Hämtar absolut sökväg till resurser, krävs för att bilder ska fungera i en .exe """
    try:
        # PyInstaller skapar en temporär mapp _MEIPASS när exe körs
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Loggerhead:
    def __init__(self, root):
        self.root = root
        self.root.title("Loggerhead v1.3 - The Cleaner")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2b2b2b")

        self.file_path = None
        self.last_size = 0
        self.monitoring = False

        # --- FÖNSTERIKON ---
        try:
            # Laddar loggerhead.png för att använda som ikon i fönstrets hörn och aktivitetsfältet
            icon_path = resource_path("loggerhead.png")
            self.icon_img = ImageTk.PhotoImage(Image.open(icon_path))
            self.root.iconphoto(False, self.icon_img)
        except Exception as e:
            print(f"System: Kunde inte sätta fönsterikon ({e})")

        # --- UI-DESIGN (Top Bar) ---
        self.top_frame = tk.Frame(root, bg="#3c3f41", pady=10)
        self.top_frame.pack(fill=tk.X)

        # --- LOGOTYP ---
        try:
            # Använder resource_path för att hitta bilden i EXE-filen
            logo_path = resource_path("loggerhead.png")
            self.logo_img = Image.open(logo_path)
            self.logo_img = self.logo_img.resize((40, 40), Image.Resampling.LANCZOS)
            self.logo_render = ImageTk.PhotoImage(self.logo_img)
            
            self.lbl_logo = tk.Label(self.top_frame, image=self.logo_render, bg="#3c3f41")
            self.lbl_logo.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"System: Logotyp hittades inte ({e}), fortsätter utan bild.")

        # --- KNAPPAR ---
        self.btn_open = tk.Button(self.top_frame, text="📁 Öppna Fil", command=self.open_file, 
                                  bg="#4e5254", fg="white", relief=tk.FLAT, padx=10)
        self.btn_open.pack(side=tk.LEFT, padx=10)

        self.btn_paste = tk.Button(self.top_frame, text="📋 Klistra in", command=self.paste_from_clipboard, 
                                   bg="#4e5254", fg="white", relief=tk.FLAT, padx=10)
        self.btn_paste.pack(side=tk.LEFT, padx=5)

        self.btn_wash = tk.Button(self.top_frame, text="🧼 Tvätta & Analysera", command=self.wash_log, 
                                   bg="#2874a6", fg="white", relief=tk.FLAT, padx=10)
        self.btn_wash.pack(side=tk.LEFT, padx=5)

        self.btn_clear = tk.Button(self.top_frame, text="🗑️ Rensa", command=self.clear_screen, 
                                   bg="#a93226", fg="white", relief=tk.FLAT, padx=10)
        self.btn_clear.pack(side=tk.RIGHT, padx=10)

        self.lbl_status = tk.Label(self.top_frame, text="Redo", bg="#3c3f41", fg="#a9b7c6")
        self.lbl_status.pack(side=tk.LEFT, padx=20)

        # --- LOGG-YTA ---
        self.log_area = scrolledtext.ScrolledText(root, bg="#1e1e1e", fg="#dcdcdc", 
                                                  font=("Consolas", 11), padx=10, pady=10)
        self.log_area.pack(expand=True, fill=tk.BOTH)

        # --- FÄRG-TAGGAR (Fixade för att undvika TclError) ---
        self.log_area.tag_config("ERROR", foreground="#ff6b68", font=("Consolas", 11, "bold"))
        self.log_area.tag_config("WARNING", foreground="#ffb86c")
        self.log_area.tag_config("INFO", foreground="#62d6ff")
        self.log_area.tag_config("SYSTEM", foreground="#bd93f9", font=("Consolas", 11, "italic"))

    def wash_log(self):
        """Tar bort brus och långa URL:er för att lyfta fram felen."""
        raw_text = self.log_area.get(1.0, tk.END)
        if not raw_text.strip():
            return
            
        self.log_area.delete(1.0, tk.END)
        self.log_area.insert(tk.END, "--- Tvättad Logg (Brus borttaget) ---\n", "SYSTEM")
        
        for line in raw_text.splitlines():
            if not line.strip(): continue
            
            # 1. Ersätt långa URL:er med [URL]
            clean_line = re.sub(r'https?://\S+', '[URL]', line)
            
            # 2. Ta bort onödiga spårnings-ID:n
            clean_line = re.sub(r'BardChatUi\.[a-zA-Z0-9.-]+', 'BardChatUi.[ID]', clean_line)
            
            self.append_log(clean_line + "\n")
        
        self.lbl_status.config(text="Loggen har tvättats!")

    def clear_screen(self):
        self.log_area.delete(1.0, tk.END)
        self.monitoring = False
        self.lbl_status.config(text="Skärm rensad")

    def open_file(self):
        file = filedialog.askopenfilename(filetypes=[("Log files", "*.txt *.log"), ("All files", "*.*")])
        if file:
            self.file_path = file
            self.lbl_status.config(text=f"Bevakar: {os.path.basename(file)}")
            self.log_area.delete(1.0, tk.END)
            self.last_size = os.path.getsize(self.file_path)
            
            # Läs in befintligt innehåll
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
                for line in data.splitlines():
                    self.append_log(line + "\n")
            
            self.monitoring = True
            self.check_for_updates()

    def paste_from_clipboard(self):
        try:
            pasted_text = self.root.clipboard_get()
            self.monitoring = False 
            self.log_area.delete(1.0, tk.END)
            for line in pasted_text.splitlines():
                self.append_log(line + "\n")
            self.lbl_status.config(text="Data inklistrad")
        except:
            self.lbl_status.config(text="Urklipp tomt")

    def append_log(self, line, force_tag=None):
        tag = force_tag
        if not tag:
            upper_line = line.upper()
            if any(w in upper_line for w in ["ERROR", "FAIL", "ERR_", "429", "500", "TRACEBACK"]): tag = "ERROR"
            elif any(w in upper_line for w in ["WARNING", "VIOLATES", "INTERVENTION"]): tag = "WARNING"
            elif any(w in upper_line for w in ["INFO", "XHR", "FETCH"]): tag = "INFO"
        
        self.log_area.insert(tk.END, line, tag)
        self.log_area.see(tk.END)

    def check_for_updates(self):
        if self.monitoring and self.file_path and os.path.exists(self.file_path):
            current_size = os.path.getsize(self.file_path)
            if current_size > self.last_size:
                with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(self.last_size)
                    new_data = f.read()
                    if new_data:
                        for line in new_data.splitlines():
                            self.append_log(line + "\n")
                self.last_size = current_size
        self.root.after(500, self.check_for_updates)

if __name__ == "__main__":
    root = tk.Tk()
    app = Loggerhead(root)
    root.mainloop()