# -HTML-SVG-to-GIF-MP4-WEBM-SVG
🎞 HTML to GIF/MP4/WebM/SVG Converter (GUI, Playwright, FFmpeg)

🎞 HTML to GIF/MP4/WebM/SVG Converter (GUI, Playwright, FFmpeg)

Ein benutzerfreundliches Python-Tool zur Umwandlung von HTML/SVG-Animationen in GIF, MP4, WebM oder statische SVG-Dateien – ideal für Entwickler, Designer oder Content-Creators.

Unterstützt interaktive Vorschau, SVG-zu-HTML-Konvertierung und fein abgestimmte Exportoptionen.

============================================================
📦 Features

- HTML-Dateien (SVG + CSS Animation) in GIF, MP4, WebM oder SVG exportieren
- Vorschau-Funktion mit automatischer Erkennung der Animationsdauer
- Integrierter SVG-Editor + CSS-Eingabe → HTML-Datei generieren
- Benutzeroberfläche via Tkinter
- Fortschrittsanzeige, Qualitätseinstellungen, Geschwindigkeit, Größe, u.v.m.
- Unterstützung für gängige Browser: Chrome, Firefox, Edge, Brave, Opera
- Transparenz-Erhalt bei WebM (Alpha Channel)
- Lizenzinformationen + Links zu SVG-Tools

============================================================
⚙️ Installation

1. Voraussetzungen:

- Python 3.8+
- ffmpeg.exe im selben Verzeichnis wie das Script
- Google Chrome, Edge, Brave oder Firefox installiert
- Playwright und Abhängigkeiten installiert:

  pip install playwright
  playwright install

2. Clone dieses Repository:

  git clone https://github.com/deinname/html-to-gif-exporter.git
  cd html-to-gif-exporter

============================================================
🚀 Starten

  python dein_scriptname.py

1. Wähle deinen Browser (Chrome, Edge etc.)
2. Lade eine HTML-Datei mit SVG-Animation
3. Justiere Einstellungen (Größe, Qualität, Format, etc.)
4. Exportiere als .gif, .mp4, .webm oder .svg

============================================================
✏️ Extra Tool: SVG & CSS zu HTML

- SVG + CSS manuell eingeben
- SVG-Dateien laden
- HTML-Datei mit animiertem SVG erzeugen

Nützliche Links:
- https://svgartista.net
- https://maxwellito.github.io/vivus-instant/

============================================================
📁 Ausgabebeispiele

Format | Beschreibung               | Hinweise
-------|----------------------------|---------
.gif   | animiertes GIF             | Ideal für kurze Clips
.mp4   | hochqualitatives Video     | Ideal für Social Media
.webm  | modernes Format mit Alpha  | Unterstützt Transparenz
.svg   | statische Grafik           | Keine Animation enthalten

============================================================
📌 Hinweise zur Dauerermittlung

- Dauer automatisch aus HTML gelesen
- Alternativ manuelle Eingabe möglich
- Geschwindigkeit skalierbar (0.2x–2.0x)

============================================================
🧪 Technologie-Stack

- Python (Tkinter GUI)
- Playwright (Headless-Browser-Automation)
- FFmpeg (Rendering & Video-Encoding)
- Reguläre Ausdrücke (CSS/SVG Parsing)
- Dateiverwaltung: pathlib, shutil, subprocess

============================================================
📝 Lizenz (MIT)

© 2025 jumbo125

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software...

(Details siehe GUI: Lizenzinformationen)

============================================================
🙏 Danksagung

- Vivus-Instant – https://github.com/maxwellito/vivus-instant
- SVG Artista – https://svgartista.net

============================================================
📬 Feedback & Beiträge

Pull Requests, Bugreports oder Feature-Wünsche sind willkommen!


🎞 HTML to GIF/MP4/WebM/SVG Converter (GUI, Playwright, FFmpeg)

A user-friendly Python tool to convert HTML/SVG animations into GIF, MP4, WebM, or static SVG files – perfect for developers, designers, or content creators.

Supports live preview, SVG-to-HTML generation, and fine-grained export options.

============================================================
📦 Features

- Export HTML files (SVG + CSS animation) to GIF, MP4, WebM, or SVG
- Preview functionality with automatic animation duration detection
- Built-in SVG editor + CSS input → generate HTML file
- User interface via Tkinter
- Progress bar, quality settings, playback speed, resolution, etc.
- Supports popular browsers: Chrome, Firefox, Edge, Brave, Opera
- Preserves transparency in WebM (Alpha Channel)
- License viewer and links to SVG helper tools

============================================================
⚙️ Installation

1. Requirements:

- Python 3.8+
- ffmpeg.exe in the same folder as the script
- Chrome, Edge, Brave or Firefox installed
- Install Playwright and dependencies:

  pip install playwright
  playwright install

2. Clone this repository:

  git clone https://github.com/yourname/html-to-gif-exporter.git
  cd html-to-gif-exporter

============================================================
🚀 Getting Started

  python your_script_name.py

1. Choose your browser (Chrome, Edge, etc.)
2. Load an HTML file with SVG animation
3. Adjust settings (size, quality, format, etc.)
4. Export to .gif, .mp4, .webm or .svg

============================================================
✏️ Extra Tool: SVG & CSS to HTML

- Enter SVG + CSS manually
- Load SVG files
- Generate HTML files with animated SVG

Useful Links:
- https://svgartista.net
- https://maxwellito.github.io/vivus-instant/

============================================================
📁 Output Formats

Format | Description                 | Notes
--------|-----------------------------|-------------------------------
.gif    | animated GIF                | Great for short loops
.mp4    | high-quality video          | Ideal for social media
.webm   | modern video format (alpha) | Supports transparency
.svg    | static SVG graphic          | No animation included

============================================================
📌 Animation Duration

- Automatically read from HTML (via input#animationLength)
- Manual override possible via GUI
- Adjustable playback speed (0.2x–2.0x)

============================================================
🧪 Technology Stack

- Python (Tkinter GUI)
- Playwright (browser automation)
- FFmpeg (rendering & encoding)
- Regex (CSS/SVG parsing)
- File management: pathlib, shutil, subprocess

============================================================
📝 License (MIT)

© 2025 jumbo125

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software...

(Full text available in the GUI: License Info)

============================================================
🙏 Acknowledgments

- Vivus-Instant – https://github.com/maxwellito/vivus-instant
- SVG Artista – https://svgartista.net

============================================================
📬 Feedback & Contributions

Pull requests, bug reports, or feature suggestions are always welcome!
