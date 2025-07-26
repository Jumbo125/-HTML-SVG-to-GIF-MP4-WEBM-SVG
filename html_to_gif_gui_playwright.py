import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import os
import time
import subprocess
import re
import shutil
import textwrap
from tkinter import filedialog, messagebox
from playwright.sync_api import sync_playwright


ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
browser_path = ""

# Vordefinierte Browser-Pfade
KNOWN_BROWSERS = {
    "Microsoft Edge (x86)": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "Microsoft Edge (64-bit)": r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "Google Chrome (x86)": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "Google Chrome (64-bit)": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "Brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "Opera": rf"C:\Users\{os.getlogin()}\AppData\Local\Programs\Opera\launcher.exe",
    "Mozilla Firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
}

def ask_for_browser_path_gui():
        selected_path = {"path": None}

        def select_from_list():
            value = dropdown_var.get()
            path = KNOWN_BROWSERS.get(value)
            if path and os.path.exists(path):
                selected_path["path"] = path
                window.destroy()
            else:
                messagebox.showwarning(
                    "Datei nicht gefunden",
                    f"Die Datei wurde nicht gefunden:\n\n{path}\n\nBitte wählen Sie einen anderen Browser oder durchsuchen Sie manuell."
                )

        def browse_file():
            path = filedialog.askopenfilename(title="Browser auswählen", filetypes=[("Browser", "*.exe")])
            if path:
                selected_path["path"] = path
                window.destroy()

        window = tk.Tk()
        window.title("Browser auswählen")
        window.geometry("500x200")
        window.resizable(False, False)

        tk.Label(window, text="Bitte wählen Sie einen Browser oder durchsuchen Sie manuell:", font=("Segoe UI", 10)).pack(pady=10)

        dropdown_var = tk.StringVar(window)
        dropdown_var.set(list(KNOWN_BROWSERS.keys())[0])
        tk.OptionMenu(window, dropdown_var, *KNOWN_BROWSERS.keys()).pack(pady=5)

        tk.Button(window, text="Aus Liste verwenden", command=select_from_list).pack(pady=5)
        tk.Button(window, text="Manuell durchsuchen...", command=browse_file).pack(pady=5)

        window.mainloop()


        if not selected_path["path"]:
            raise RuntimeError("Kein Browser ausgewählt.")

        return selected_path["path"]



class GifExporterApp:
   
    def __init__(self, master, browser_path):
        
        self.browser_path = browser_path
        self.master = master
        master.title("HTML → GIF/MP4/Webm Exporter (Playwright)")

       # Haupt-Container mit drei Spalten
        main_container = tk.Frame(master)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        left_column = tk.Frame(main_container)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        rightmost_column = tk.Frame(main_container)
        rightmost_column.pack(side="right", fill="y", padx=(10, 0))

        right_column = tk.Frame(main_container)
        right_column.pack(side="right", fill="y")

        # --- Abschnitt 1: HTML-Quelle ---
        source_frame = ttk.LabelFrame(left_column, text="1. HTML-Quelle")
        source_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(source_frame, text="HTML-Datei wählen:").pack(anchor="w")
        self.html_button = tk.Button(
            source_frame, text="📁 Datei auswählen", command=self.choose_html)
        self.html_button.pack(fill="x", pady=5)

        tk.Label(source_frame, text="Ausgelesene Animationsdauer:").pack(
            anchor="w")
        self.duration_info = tk.Label(
            source_frame, text="Dauer wird nach HTML Auswahl berechnet.")
        self.duration_info.pack(anchor="w", pady=(5))
        self.duration_info1 = tk.Label(
            source_frame, text="Wenn kein Wert ausgelesen kann, werden 3s als Standardwert übernommen.")
        self.duration_info1.pack(anchor="w")
        self.duration_info2 = tk.Label(
            source_frame, text="Dies kann durch manuelle Zeit unterhalb verändert werden.")
        self.duration_info2.pack(anchor="w")

        # Manuelle Zeitangabe
        tk.Label(source_frame, text="⏱ Zeit erzwingen (Sekunden, z. B. 1.8):").pack(
            anchor="w")
        self.manual_duration_entry = tk.Entry(source_frame)
        self.manual_duration_entry.pack(fill="x", pady=(0, 10))

        # --- Abschnitt 2: Einstellungen ---
        settings_frame = ttk.LabelFrame(left_column, text="2. Einstellungen")
        settings_frame.pack(fill="x", padx=5, pady=5)

        # Größe
        tk.Label(settings_frame, text="Größe (px):").pack(anchor="w")
        size_row = tk.Frame(settings_frame)
        size_row.pack(fill="x")
        tk.Label(size_row, text="Breite:").pack(side="left")
        self.width_entry = tk.Entry(size_row, width=6)
        self.width_entry.insert(0, "800")
        self.width_entry.pack(side="left", padx=5)
        tk.Label(size_row, text="Höhe:").pack(side="left")
        self.height_entry = tk.Entry(size_row, width=6)
        self.height_entry.insert(0, "600")
        self.height_entry.pack(side="left", padx=5)
        self.keep_aspect = tk.BooleanVar(value=False)
        self.aspect_check = tk.Checkbutton(
            settings_frame, text="⛓ Proportionen beibehalten", variable=self.keep_aspect, command=self.toggle_height)
        self.aspect_check.pack(anchor="w", pady=(0, 10))

        # Qualität
        tk.Label(settings_frame, text="Qualität (0–100%):").pack(anchor="w")
        self.quality_slider = tk.Scale(
            settings_frame, from_=1, to=100, orient="horizontal")
        self.quality_slider.set(90)
        self.quality_slider.pack(fill="x", pady=(0, 10))

        # Geschwindigkeit
        tk.Label(settings_frame, text="Abspielgeschwindigkeit (0.2x–2.0x):").pack(
            anchor="w")
        self.speed_slider = tk.Scale(
            settings_frame, from_=0.2, to=2.0, resolution=0.1, orient="horizontal")
        self.speed_slider.set(1.0)
        self.speed_slider.pack(fill="x", pady=(0, 10))

        # Manuelle Dauer
        self.manual_duration_active = tk.BooleanVar(value=False)
        self.manual_duration_checkbox = tk.Checkbutton(
            settings_frame, text="🛠 Manuelle Dauer aktivieren", variable=self.manual_duration_active, command=self.toggle_manual_duration_slider)
        self.manual_duration_checkbox.pack(anchor="w")
        tk.Label(settings_frame, text="Manuelle Dauer (Sekunden):").pack(
            anchor="w")
        self.manual_duration_slider = tk.Scale(
            settings_frame, from_=1, to=20, resolution=0.5, orient="horizontal", state="disabled")
        self.manual_duration_slider.set(5)
        self.manual_duration_slider.pack(fill="x", pady=(0, 10))

        # ---  HTML Erstellung ---

       # --- Abschnitt 4: SVG & CSS zu HTML ---
        self.svg_css_frame = ttk.LabelFrame(
            rightmost_column, text="Extra Tool: SVG und CSS zu HTML")
        self.svg_css_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Moduswahl: Manuell oder Datei
        self.svg_mode = tk.StringVar(value="manual")
        mode_frame = tk.Frame(self.svg_css_frame)
        mode_frame.pack(anchor="w", pady=(4, 6))
        tk.Radiobutton(mode_frame, text="✍️ Manuell eingeben", variable=self.svg_mode, value="manual", command=self.toggle_svg_input).pack(side="left", padx=(0, 10))
        tk.Radiobutton(mode_frame, text="📁 SVG-Datei laden", variable=self.svg_mode, value="file", command=self.toggle_svg_input).pack(side="left")

        # --- Manuelle SVG Eingabe ---
        self.svg_input_frame = tk.Frame(self.svg_css_frame)
        tk.Label(self.svg_input_frame, text="SVG-Eingabe:").pack(anchor="w")
        svg_scroll_frame = tk.Frame(self.svg_input_frame)
        svg_scroll_frame.pack(fill="both", expand=True)
        self.svg_input = tk.Text(svg_scroll_frame, height=10, wrap="none")
        svg_scroll_y = tk.Scrollbar(svg_scroll_frame, orient="vertical", command=self.svg_input.yview)
        self.svg_input.configure(yscrollcommand=svg_scroll_y.set)
        self.svg_input.pack(side="left", fill="both", expand=True)
        svg_scroll_y.pack(side="right", fill="y")
        self.svg_input_frame.pack(fill="both", expand=True)

        # --- Manuelle CSS Eingabe ---
        self.css_input_frame = tk.Frame(self.svg_css_frame)
        tk.Label(self.css_input_frame, text="CSS-Eingabe:").pack(anchor="w", pady=(10, 0))
        css_scroll_frame = tk.Frame(self.css_input_frame)
        css_scroll_frame.pack(fill="both", expand=True)
        self.css_input = tk.Text(css_scroll_frame, height=10, wrap="none")
        css_scroll_y = tk.Scrollbar(css_scroll_frame, orient="vertical", command=self.css_input.yview)
        self.css_input.configure(yscrollcommand=css_scroll_y.set)
        self.css_input.pack(side="left", fill="both", expand=True)
        css_scroll_y.pack(side="right", fill="y")
        self.css_input_frame.pack(fill="both", expand=True)

        # --- SVG-Datei Auswahl (initial versteckt) ---
        self.svg_file_button = tk.Button(self.svg_css_frame, text="SVG wählen...", command=self.load_svg_from_file)
        # wird nur bei Auswahl angezeigt
        self.loaded_svg_from_file = None

        # Trennlinie + externe Links
        ttk.Separator(self.svg_css_frame, orient="horizontal").pack(fill="x", padx=0, pady=(10, 6))
        link1 = tk.Label(self.svg_css_frame, text="🌐 https://svgartista.net/ (für SVG-Code manuell erhalten)", fg="blue", cursor="hand2")
        link1.pack(anchor="w", pady=(0, 2))
        link1.bind("<Button-1>", lambda e: self.open_with_playwright("https://svgartista.net/"))
        link2 = tk.Label(self.svg_css_frame, text="🌐 https://maxwellito.github.io/vivus-instant/ (für SVG-Downlaod)", fg="blue", cursor="hand2")
        link2.pack(anchor="w", pady=(0, 6))
        link2.bind("<Button-1>", lambda e: self.open_with_playwright("https://maxwellito.github.io/vivus-instant/"))

        # Button: HTML erzeugen
        self.generate_html_button = tk.Button(self.svg_css_frame, text="🛠 HTML erzeugen", command=self.generate_html_from_svg_css)
        self.generate_html_button.pack(fill="x", pady=(10, 30))

         # Lizenzbutton unten
        tk.Button(self.svg_css_frame, text="Lizenzinformationen", command=self.show_license_info).pack(side="bottom", pady=10)
    
        # --- Abschnitt 3: Export (rechts) ---
        export_frame = ttk.LabelFrame(right_column, text="3. Export")
        export_frame.pack(fill="y", padx=5, pady=5)

        tk.Label(export_frame, text="Ausgabeformat:").pack(anchor="w")
        self.format_choice = ttk.Combobox(
            export_frame, values=["gif", "mp4", "webm", "svg"])
        self.format_choice.bind("<<ComboboxSelected>>", self.on_format_change)
        self.format_choice.current(0)
        self.format_choice.pack(fill="x", pady=(0, 10))

        tk.Label(export_frame, text="Zielverzeichnis:").pack(anchor="w")
        self.output_dir_button = tk.Button(
            export_frame, text="📁 Ordner wählen", command=self.choose_output_dir)
        self.output_dir_button.pack(fill="x", pady=(0, 10))

        tk.Label(export_frame, text="Dateiname (ohne Endung):").pack(anchor="w")
        self.filename_entry = tk.Entry(export_frame)
        self.filename_entry.insert(0, "export")
        self.filename_entry.pack(fill="x", pady=(0, 10))

        self.run_button = tk.Button(
            export_frame, text="🎬 GIF/MP4 erstellen", command=self.generate_output)
        self.run_button.pack(pady=10, fill="x")

        # Interne Variablen
        self.html_path = ""
        self.output_dir = ""
        
        self.browser = None
        self.playwright = None
        self.context = None

    def toggle_svg_input(self):
        mode = self.svg_mode.get()
        if mode == "manual":
            self.svg_input_frame.pack(fill="both", expand=True)
            self.css_input_frame.pack(fill="both", expand=True)
            self.svg_file_button.pack_forget()
        else:
            self.svg_input_frame.pack_forget()
            self.css_input_frame.pack_forget()
            self.svg_file_button.pack(pady=4)

    def show_license_info(self):
        license_window = tk.Toplevel(self.master)
        license_window.title("Lizenzinformationen")
        license_window.geometry("700x500")  # Breiteres Fenster
        license_window.resizable(True, True)

        frame = tk.Frame(license_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=("Courier New", 10))

        text_widget.pack(fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)

        license_text = textwrap.dedent("""\
            HTML/SVG to GIF/MP4/WEBM/SVG – © 2025 jumbo125
            MIT License

            Permission is hereby granted, free of charge, to any person obtaining a copy
            of this software and associated documentation files (the “Software”), to deal
            in the Software without restriction, including without limitation the rights
            to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
            copies of the Software, and to permit persons to whom the Software is
            furnished to do so, subject to the following conditions:

            The above copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software.

            THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
            IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
            AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
            LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
            OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
            SOFTWARE.

            Third-Party Components:

            • Vivus-Instant – MIT License
            https://github.com/maxwellito/vivus-instant

            • SVG Artista – MIT License
            https://svgartista.net
                """)

        text_widget.insert("1.0", license_text)
        text_widget.config(state="disabled")
    
    def open_with_playwright(self, url):
        try:
            self.cleanup_browser()  # alte schließen
        except Exception as e:
            print(f"❗ Fehler beim Cleanup: {e}")

        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False, args=["--start-maximized"])
            self.context = self.browser.new_context()
            page = self.context.new_page()
            page.goto(url)
        except Exception as e:
            print(f"❌ Fehler beim Öffnen von Playwright: {e}")

    def cleanup_browser(self):
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.context:
                self.context.close()
                self.context = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
        except Exception as e:
            print(f"⚠️ Fehler beim Schließen alter Browser-Instanzen: {e}")

    # erhalte den text in zwei variablen
    def extract_svg_and_css(self, svg_raw_text: str):
        # 1. CSS aus <style> extrahieren
        css_match = re.search(r"<style[^>]*>(.*?)</style>", svg_raw_text, re.DOTALL | re.IGNORECASE)
        css_content = css_match.group(1).strip() if css_match else ""

        # 2. Style-Block aus SVG entfernen
        svg_content = re.sub(r"<style[^>]*>.*?</style>", "", svg_raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        # 3. class="active" ins <svg> einfügen, wenn nicht vorhanden
        svg_content = re.sub(
            r'(<svg\b[^>]*?)\s*>',
            lambda m: m.group(1) + (' class="active"' if 'class=' not in m.group(1) else ''),
            svg_content,
            count=1
        )

        return css_content, svg_content
    
    def load_svg_from_file(self):
        from tkinter import filedialog, messagebox
        file_path = filedialog.askopenfilename(filetypes=[("SVG-Dateien", "*.svg")], title="SVG-Datei auswählen")
        if not file_path:
            return  # User abgebrochen

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.loaded_svg_from_file = f.read()
            messagebox.showinfo("SVG geladen", "SVG-Datei erfolgreich geladen.")
        except Exception as e:
            messagebox.showerror("Fehler", f"SVG-Datei konnte nicht geladen werden:\n{e}")
        
    def generate_html_from_svg_css(self):
        css_content = self.css_input.get("1.0", "end").strip()
        svg_content = self.svg_input.get("1.0", "end").strip()
        
        
         # 🧠 Eingabe prüfen
        if not css_content and not svg_content:
            # Falls beides leer ist, verwende geladene SVG-Datei (falls vorhanden)
            if self.loaded_svg_from_file:
                svg_raw = self.loaded_svg_from_file

                # Extrahiere CSS <style> aus SVG
                css_match = re.search(r"<style[^>]*>(.*?)</style>", svg_raw, re.DOTALL | re.IGNORECASE)
                css_content = css_match.group(1).strip() if css_match else ""

                # Entferne style aus SVG
                svg_content = re.sub(r"<style[^>]*>.*?</style>", "", svg_raw, flags=re.DOTALL | re.IGNORECASE).strip()
            else:
                messagebox.showwarning("Eingabe fehlt", "Bitte geben Sie CSS und SVG ein oder wählen Sie eine SVG-Datei.")
                return

         
            # Nur Füllungen bei animierten Elementen ersetzen – nicht globale Farben!
            # Nur bei Klassen wie svg-elem-* ohne vorhandenes fill einfügen
            svg_content = re.sub(
                r'(<(path|circle|rect|polygon|line|ellipse)[^>]*class="svg-elem-\d+"(?![^>]*fill=))',
                r'\1 fill="transparent"',
                svg_content
            )

            # ✅ class="active" in das <svg>-Tag einfügen, wenn noch nicht vorhanden
            svg_content = re.sub(
                r'(<svg\b[^>]*?)>',
                lambda m: (m.group(1) + ' class="active">') if 'class=' not in m.group(1) else m.group(0),
                svg_content,
                count=1
            )
            
            html_str = f"""<!DOCTYPE html>
            <html lang="de">
            <head>
            <meta charset="UTF-8">
            <title>SVG Animation</title>
            <style>
            html::-webkit-scrollbar {{ display: none; }}
            html {{ -ms-overflow-style: none; scrollbar-width: none; background-color: transparent; }}
            {css_content}
            </style>

            <script>
            let animationDuration = 0;
            let animatableElements = [];

            document.addEventListener("DOMContentLoaded", function () {{
            const svg = document.querySelector("svg");
            if (!svg) return;

            const elements = svg.querySelectorAll("[class^='svg-elem']");
            let maxEndTime = 0;

            animatableElements = Array.from(elements).map(el => {{
                const style = getComputedStyle(el);
                const durationStr = style.transitionDuration.split(",")[0] || "0s";
                const delayStr = style.transitionDelay.split(",")[0] || "0s";

                const duration = parseFloat(durationStr) || 0;
                const delay = parseFloat(delayStr) || 0;
                const totalLength = el.getTotalLength?.() || 0;

                const endTime = delay + duration;
                if (endTime > maxEndTime) maxEndTime = endTime;

                el.style.strokeDasharray = totalLength;
                el.style.strokeDashoffset = totalLength;
                el.style.transition = "none";

                return {{
                el,
                length: totalLength,
                duration,
                delay
                }};
            }});

            animationDuration = maxEndTime;

            const input = document.getElementById("animationLength");
            if (input) input.value = animationDuration;
            }});

            function startAnimation() {{
            const svg = document.querySelector("svg");
            if (svg) {{
                svg.classList.add("active");
            }}
            }}

            function renderFrameAt(t) {{
            animatableElements.forEach(({{
                el, length, duration, delay
            }}) => {{
                let progress;

                if (t < delay) {{
                progress = 0;
                }} else if (t >= delay + duration) {{
                progress = 1;
                }} else {{
                progress = (t - delay) / duration;
                }}

                const offset = length * (1 - progress);
                el.style.strokeDashoffset = `${{offset}}`;
            }});
            }}
            </script>
            </head>
            <body>
            <input type="hidden" id="animationLength">
            <div id="container">
            {svg_content}
            </div>
            </body>
            </html>
            """

            # Datei speichern über "Speichern unter"-Dialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML-Dateien", "*.html"), ("Alle Dateien", "*.*")],
                title="HTML speichern unter"
            )

            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(html_str)
                    messagebox.showinfo(
                        "Erfolg", f"HTML-Datei gespeichert:\n{file_path}")
                except Exception as e:
                    messagebox.showerror(
                        "Fehler", f"Beim Speichern ist ein Fehler aufgetreten:\n{e}")
            else:
                # Benutzer hat abgebrochen
                pass

    def on_format_change(self, event=None):
        selected = self.format_choice.get()
        if selected == "gif":
            messagebox.showinfo(
                "Format ausgewählt", "🎞 Du hast GIF als Ausgabeformat gewählt. Ideal für kurze Animationen. Veränderungen der Geschwindigkeit und Dauer werden hier übernommen.")
        elif selected == "mp4":
            messagebox.showinfo(
                "Format ausgewählt", "🎥 Du hast MP4 gewählt. Gute Wahl für Videoplattformen und hohe Kompatibilität. Veränderungen der Geschwindigkeit und Dauer werden hier übernommen.")
        elif selected == "webm":
            messagebox.showinfo(
                "Format ausgewählt", "🌀 Du hast WebM gewählt. Optimal für moderne Browser und transparente Videos. Veränderungen der Geschwindigkeit und Dauer werden hier übernommen.")
        elif selected == "svg":
            messagebox.showinfo(
                "Format ausgewählt", "✏️ Du hast SVG gewählt. Exportiert nur statische SVG-Grafik aus der HTML-Datei. Veränderungen der Geschwindigkeit und Dauer werden hier  NICHT übernommen!")

    def toggle_manual_duration_slider(self):
        if self.manual_duration_active.get():
            self.manual_duration_slider.configure(state="normal")
        else:
            self.manual_duration_slider.configure(state="disabled")

    def get_animation_duration(self, page):
        # 1. Prüfe Textfeld
        manual_text = self.manual_duration_entry.get().strip()
        if manual_text:
            try:
                value = float(manual_text.replace(",", "."))
                if value > 0:
                    self.duration_info.config(
                        text=f"⏱ Manuell eingegeben: {value:.2f} Sekunden")
                    return value
            except ValueError:
                self.duration_info.config(
                    text="⚠️ Ungültiger Wert – automatische Erkennung")

        # 2. Versuche, Dauer aus <input id="animationLength"> zu lesen
        try:
            duration = page.evaluate("""() => {
                const el = document.querySelector("#animationLength");
                if (!el) return 0;
                const val = parseFloat(el.value);
                return isNaN(val) ? 0 : val;
            }""")
        except Exception as e:
            print("Fehler beim Lesen des Hidden-Inputs:", e)
            duration = 0

        if duration > 0:
            self.duration_info.config(
                text=f"⏱ Gelesen aus #animationLength: {duration:.2f} Sekunden")
            return duration

        # 3. Fallback
        self.duration_info.config(
            text="⚠️ Keine Dauer gefunden – Fallback = 3s")
        return 3

    def choose_html(self):
        self.cleanup_browser()  # ❗️Browser beenden, falls offen
        self.html_path = filedialog.askopenfilename(
            filetypes=[("HTML files", "*.html")])
        if not self.html_path:
            return

        # → Zeige "Bitte warten"-Fenster
        wait_popup = tk.Toplevel(self.master)
        wait_popup.title("Bitte warten...")
        tk.Label(wait_popup, text="🔄 Lade HTML und lese Animationsdauer aus.... Vorschau-Fenster NICHT SCHLIEßEN!").pack(padx=20, pady=20)
        wait_popup.update()

        self.master.update_idletasks()

        try:
            with sync_playwright() as p:
                #browser = p.chromium.launch(headless=False)
                browser = p.chromium.launch(executable_path=browser_path, headless=False)
                context = browser.new_context()
                page = context.new_page()
                page.goto("file://" + os.path.abspath(self.html_path))
                page.wait_for_load_state("networkidle")
                time.sleep(1)

                duration = self.get_animation_duration(page)

                if duration == 0:
                    self.duration_info.config(
                        text="Dauer: Nicht erkannt (Fallback = 3s)")
                else:
                    self.duration_info.config(
                        text=f"Dauer: {duration:.2f} Sekunden")

                browser.close()

        except Exception as e:
            self.duration_info.config(
                text="⚠️ Dauer konnte nicht ausgelesen werden")
            print(f"Fehler beim Auslesen der Animationsdauer: {e}")

        # Schließe das „Bitte warten“-Fenster
        wait_popup.destroy()

    def choose_output_dir(self):
        self.output_dir = filedialog.askdirectory()

    def toggle_height(self):
        if self.keep_aspect.get():
            self.height_entry.configure(state="disabled")
        else:
            self.height_entry.configure(state="normal")

    def generate_output(self):
        self.cleanup_browser()  # ❗️Browser beenden, falls offe
        if not self.html_path or not self.output_dir:
            messagebox.showerror(
                "Fehler", "📁 Bitte HTML-Datei und Zielverzeichnis wählen.")
            return

        # Hinweisfenster anzeigen
        wait_popup = tk.Toplevel(self.master)
        wait_popup.title("Export läuft…")
        wait_popup.geometry("300x120")
        wait_popup.resizable(False, False)
        wait_popup.grab_set()
        wait_popup.protocol("WM_DELETE_WINDOW", lambda: None)

        tk.Label(wait_popup, text="⏳ Bitte warten…", font=(
            "Segoe UI", 12, "bold")).pack(pady=(20, 5))
        tk.Label(wait_popup, text="Vorschaubild-Fenster nicht schließen,\nsonst bricht der Export ab.",
                 justify="center").pack(pady=(0, 10))
        wait_popup.update()

        width = int(self.width_entry.get())
        height = int(self.height_entry.get()
                     ) if not self.keep_aspect.get() else 0
        quality = self.quality_slider.get()
        out_format = self.format_choice.get()
        filename = self.filename_entry.get()
        output_file = os.path.join(self.output_dir, f"{filename}.{out_format}")
        fps = 60
        speed_factor = self.speed_slider.get()
        temp_dir = Path("temp_frames")
        temp_dir.mkdir(exist_ok=True)

       # 📤 Wenn SVG als Ausgabe gewählt → Direkt aus HTML extrahieren
        if out_format == "svg":
            try:
                with open(self.html_path, "r", encoding="utf-8") as f:
                    html = f.read()

                match = re.search(r"<svg[\s\S]*?</svg>", html, re.IGNORECASE)
                if match:
                    svg_code = match.group(0)

                    style_match = re.search(
                        r"<style[\s\S]*?</style>", html, re.IGNORECASE)
                    if style_match:
                        style = style_match.group(0)

                        # Ersetze "svg.active .xyz" mit "svg .xyz"
                        style = re.sub(
                            r"svg\.active\s*\.(svg-elem-\d+)", r"svg .\1", style)

                        # Sammle alle Klassen mit ihren CSS-Blöcken
                        blocks = re.findall(
                            r"\.(svg-elem-\d+)\s*\{([^}]+)\}", style)
                        class_styles = {}
                        for cls, props in blocks:
                            props = props.strip()
                            if cls not in class_styles:
                                class_styles[cls] = []
                            class_styles[cls].append(props)

                        final_css = ""
                        keyframes = ""

                        for cls, prop_blocks in class_styles.items():
                            merged = "\n".join(prop_blocks)

                            # Extrahiere stroke-dasharray & -offset
                            dasharray_match = re.search(
                                r"stroke-dasharray:\s*([^;]+);", merged)
                            dashoffset_match = re.search(
                                r"stroke-dashoffset:\s*([^;]+);", merged)

                            dasharray = dasharray_match.group(
                                1).strip() if dasharray_match else None
                            dashoffset = dashoffset_match.group(
                                1).strip() if dashoffset_match else None

                            # Extrahiere evtl. transition-Werte (z.B. "transition: stroke-dashoffset 1s ease-in 0.24s;")
                            trans_match = re.search(
                                r"transition:\s*stroke-dashoffset\s+([0-9.]+s)\s+([\w\-]+)\s+([0-9.]+s);?", merged
                            )
                            duration, timing, delay = trans_match.groups(
                            ) if trans_match else ("2s", "linear", "0s")

                            # transition entfernen
                            merged = re.sub(
                                r"transition\s*:[^;]+;", "", merged)

                            if dasharray and dashoffset and dashoffset != "0":
                                anim_name = f"anim_{cls}"
                                anim_line = (
                                    f"\n  stroke-dasharray: {dasharray};"
                                    f"\n  stroke-dashoffset: {dasharray};"
                                    f"\n  animation: {anim_name} {duration} {timing} {delay} 1 forwards;"
                                )
                                keyframes += f"""
        @keyframes {anim_name} {{
        0% {{ stroke-dashoffset: {dasharray}; }}
        100% {{ stroke-dashoffset: 0; }}
        }}"""
                                final_css += f".{cls} {{{anim_line}\n}}\n"
                            else:
                                final_css += f".{cls} {{{merged}\n}}\n"

                        # Schließe finalen <style>-Block
                        style = f"<style>\n{final_css.strip()}\n{keyframes.strip()}\n</style>"

                        # Setze <style> direkt hinter das öffnende <svg> ein
                        svg_code = re.sub(
                            r"(<svg[^>]*>)", r"\1\n" + style, svg_code, count=1)

                    with open(output_file, "w", encoding="utf-8") as f_out:
                        f_out.write(svg_code)

                    messagebox.showinfo(
                        "Erfolg", f"✅ SVG exportiert: {output_file}")
                else:
                    messagebox.showerror(
                        "Fehler", "⚠️ Kein <svg> im HTML gefunden.")

            except Exception as e:
                messagebox.showerror(
                    "Fehler", f"❌ SVG-Export fehlgeschlagen:\n{str(e)}")

            wait_popup.destroy()
            return
        try: 
            with sync_playwright() as p:
                #browser = p.chromium.launch(headless=False)
                browser = p.chromium.launch(executable_path=browser_path, headless=False)
                context = browser.new_context()
                page = context.new_page()
                page.goto("file://" + os.path.abspath(self.html_path))
                page.wait_for_load_state("networkidle")
                time.sleep(1)

                duration = self.get_animation_duration(page)
                total_frames = int(duration * fps)

                if self.keep_aspect.get():
                    bounding_box = page.evaluate("""
                        () => {
                            const el = document.querySelector("#container");
                            if (!el) return { width: 0, height: 0 };
                            const rect = el.getBoundingClientRect();
                            return { width: rect.width, height: rect.height };
                        }
                    """)
                    orig_width = bounding_box["width"]
                    orig_height = bounding_box["height"]
                    if orig_width == 0 or orig_height == 0:
                        messagebox.showerror(
                            "Fehler", "⚠️ Element nicht gefunden oder Größe 0.")
                        return
                    aspect_ratio = orig_width / orig_height
                    height = int(width / aspect_ratio)
                    if height % 2 != 0:
                        height += 1

                page.set_viewport_size({"width": width, "height": height})

                for i in range(total_frames):
                    current_time = i / fps
                    frame_path = temp_dir / f"frame_{i:03d}.png"
                    page.evaluate(f"renderFrameAt({current_time})")
                    page.wait_for_timeout(100)
                    page.screenshot(path=str(frame_path), omit_background=True)

                    print(
                        f"Gerendert: Frame {i+1}/{total_frames} bei t={current_time:.3f}s")

                browser.close()
                scale_filter = f"scale={width}:{height}"
                temp_video = "temp_original.webm"
                # Qualität: 0 (schlecht) → 4 Mbit/s
                # Qualität: 100 (perfekt) → 10 Mbit/s
                min_bitrate = 4000  # in kbit/s
                max_bitrate = 10000

                target_bitrate = int(min_bitrate + (quality / 100)
                                    * (max_bitrate - min_bitrate))

                # PNGs → WebM mit Alpha (nur sinnvoll wenn SVG wirklich transparent ist)
                vpx_crf = int((100 - quality) / 1.5)
                subprocess.call([
                    ffmpeg_path, "-y",
                    "-framerate", str(fps),
                    "-i", str(temp_dir / "frame_%03d.png"),
                    "-c:v", "libvpx",
                    "-pix_fmt", "yuva420p",
                    "-auto-alt-ref", "0",
                    # "-crf", str(vpx_crf),
                    "-b:v", f"{target_bitrate}k",
                    "-maxrate", f"{target_bitrate}k",
                    "-bufsize", f"{2 * target_bitrate}k",  # Puffergröße doppelt
                    "-threads", "4",           # optional: für mehr Speed
                    "-deadline", "good",       # oder: "best" für Qualität
                    temp_video
                ])

                speed_multiplier = 1 / speed_factor

                if out_format == "mp4":
                    subprocess.call([
                        ffmpeg_path, "-y", "-i", temp_video,
                        "-filter:v", f"setpts={speed_multiplier}*PTS,fps={fps}",
                        "-c:v", "libx264",
                        "-crf", str(int((100 - quality) / 2.5 + 18)),
                        "-pix_fmt", "yuv420p",  # MP4 kann eh kein Alpha
                        output_file
                    ])

                elif out_format == "gif":
                    gif_filters = f"setpts={speed_multiplier}*PTS,fps={fps},scale={width}:{height}"

                    subprocess.call([
                        ffmpeg_path, "-y", "-i", temp_video,
                        "-filter_complex", f"[0:v]{gif_filters}[v]",
                        "-map", "[v]", "-loop", "0", output_file
                    ])
                elif out_format == "webm":
                    webm_filters = f"setpts={speed_multiplier}*PTS,fps={fps},scale={width}:{height}"

                    subprocess.call([
                        ffmpeg_path, "-y", "-i", temp_video,
                        "-filter_complex", f"[0:v]{webm_filters}[v]",
                        "-map", "[v]",
                        "-c:v", "libvpx",
                        "-pix_fmt", "yuva420p",
                        "-auto-alt-ref", "0",
                        "-b:v", f"{target_bitrate}k",
                        "-maxrate", f"{target_bitrate}k",
                        "-bufsize", f"{2 * target_bitrate}k",
                        "-threads", "4",
                        "-deadline", "good",
                        output_file
                    ])

        except Exception as e:
            print("❌ Fehler während des Exports:", e)
            messagebox.showerror("Fehler", f"❌ Der Export wurde abgebrochen.\nMöglicherweise wurde das Browserfenster geschlossen:\n\n{e}")

        finally:
           # WICHTIG: "Bitte warten"-Fenster schließen – egal ob Erfolg oder Fehler
            wait_popup.destroy()
            
      
        for f in temp_dir.glob("*.png"):
            try:
                f.unlink()
            except Exception as e:
                print(f"Konnte Datei nicht löschen: {f} – {e}")

        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"⚠️ temp_frames konnte nicht gelöscht werden: {e}")

        try:
            os.remove(temp_video)
        except Exception as e:
            print(f"⚠️ Temporäres Video konnte nicht gelöscht werden: {e}")

        wait_popup.destroy()


if __name__ == "__main__":
    try:
        selected_browser_path = ask_for_browser_path_gui()  # ← Muss global sein

        root = tk.Tk()
        app = GifExporterApp(root, browser_path=selected_browser_path)
        root.mainloop()

    except RuntimeError as e:
        messagebox.showerror("Abbruch", str(e))
