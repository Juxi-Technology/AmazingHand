[English](../en/macOS.md) | Deutsch | [Español](../es/macOS.md) | [Français](../fr/macOS.md) | [Italiano](../it/macOS.md) | [日本語](../ja/macOS.md) | [한국어](../ko/macOS.md) | [Português (BR)](../pt-br/macOS.md) | [Português (PT)](../pt-pt/macOS.md) | [简体中文](../zh-hans/macOS.md) | [繁體中文](../zh-hant/macOS.md)

# SCS0009 Servo Debug Tool — macOS-Anleitung

Für macOS 11 (Big Sur) und später. Kernpunkte: Benennung serieller Geräte (`cu.*` vs. `tty.*`), USB-Treiber.

> ⚠️ **Kompatibilität: Dieses Werkzeug unterstützt derzeit nur Feetech SCS0009-Servos (SCS-Serie, Potentiometer-Positionsrückmeldung, 10-Bit-Auflösung 0-1023)**. Die Registertabelle und das xdat-Format sind für den Feetech SCS0009 ausgelegt; andere Marken/Modelle werden nicht garantiert.

---

## 1. Anforderungen

| Abhängigkeit | Version |
|-----------|---------|
| Python | >= 3.8 (3.10+ empfohlen, über Homebrew) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| Betriebssystem | macOS 11+ (Apple Silicon / Intel) |

## 2. Python installieren

Empfohlen über Homebrew:

```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

Überprüfen:

```bash
python3 --version
```

## 3. Abhängigkeiten installieren

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Erstellen Sie die virtuelle Umgebung nur EINMAL**. Ein erneutes Ausführen setzt die Umgebung zurück bzw. überschreibt sie (installierte Abhängigkeiten werden gelöscht). Danach einfach `source .venv/bin/activate`.

## 4. ⚠️ Benennung serieller Geräte unter macOS [wichtig]

macOS legt USB-Seriell-Geräte unter `/dev` mit **zwei Namenskonventionen** ab:

| Präfix | Bedeutung | Verwendbar |
|--------|---------|--------|
| `/dev/tty.usbserial-*` | Modem-Stil (blockierend) | kann hängen bleiben, nicht empfohlen |
| `/dev/cu.usbserial-*` | Call-/Terminal-Stil (**nicht blockierend**) | ✅ empfohlen |

**Port finden:**

```bash
ls /dev/cu.*
```

Typische Ausgabe:

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # onboard USB serial (Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> Das Werkzeug bevorzugt automatisch `cu.*`-Geräte. Wenn Sie einen Port manuell angeben, verwenden Sie `cu.` statt `tty.`.

## 5. USB-Treiber

Die meisten gängigen Chips (CH340, CP2102, FTDI) haben integrierte macOS-Treiber. Wenn das Gerät nicht erkannt wird:

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**: ältere Chargen benötigen den offiziellen WCH-Treiber
- Im Allgemeinen genügt es, wenn `ls /dev/cu.*` das Gerät anzeigt

## 6. Umgebung prüfen

```bash
python setup.py
```

## 7. GUI starten

```bash
python -m src.gui.factory_calibration_tool
```

Port angeben:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 8. Bedienablauf der Oberfläche

> Einteiliges Layout. Eine Bildlaufleiste erscheint automatisch, wenn das Fenster zu kurz ist; beim Maximieren dehnt es sich passend aus.

### 8.1 Serielle Verbindung
Wählen Sie Port und Baudrate (Standard 1M), klicken Sie auf **Verbinden**.

### 8.2 Servos scannen
Klicken Sie auf **Servos scannen** (ID 1-254); klicken Sie auf eine Listenzeile, um das Dropdown automatisch zu füllen.

### 8.3 Parameter lesen/schreiben
- Alle 44 Register lesen, Punktauswahl-Verknüpfung füllt Adresse/Länge/Wert
- Schreiben mit automatischem Entsperren/Schreiben/Sperren; Erfolgs-/Fehler-Popup wird angezeigt

### 8.4 Positionssteuerung
Schieberegler ziehen (0-1023) oder Wert eingeben; Hinweis auf abgeschlossene Bewegung zum Ausschalten des Drehmoments.

### 8.5 Baudrate / Werksreset
Baudrate ändern (automatischer Rollback bei Fehler), Werksreset.

### 8.6 xdat-Parameter (nur EEPROM)
Aktuellen Servo speichern → Backup öffnen → auf Servo wiederherstellen.

## 9. Fehlerbehebung

| Problem | Lösung |
|---------|----------|
| Port mit `tty.` bleibt hängen | Stattdessen das Präfix `cu.` verwenden |
| Gerät nicht gefunden | `ls /dev/cu.*`; neu einstecken; `system_profiler SPUSBDataType` |
| Chinesische UI leer | Das System-PingFang ist meist in Ordnung; Noto Sans CJK installieren, falls defekt |
| Berechtigungsproblem | macOS benötigt im Allgemeinen keine zusätzliche Berechtigung; Terminalzugriff erlauben, wenn dazu aufgefordert |
| Venv-Aktivierung schlägt fehl | `source .venv/bin/activate` (nicht `.bat`) |
| Apple-Silicon-Build-Fehler | Python 3.10+ ist nativ; altes Python über Rosetta vermeiden |

## 10. Kommandozeile (optional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. Tipps

- **Portname ändert sich**: `cu.*`-Namen können je nach USB-Port variieren; wählen Sie bei jedem Start im Dropdown aus
- **Ruhezustand**: macOS kann in den Ruhezustand wechseln und die serielle Verbindung trennen; halten Sie das System während des Betriebs wach
- **Datenschutzberechtigung**: Wenn nach dem Zugriff auf "access removable disks" gefragt wird, erlauben Sie ihn
