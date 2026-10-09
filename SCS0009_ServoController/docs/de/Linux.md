[English](../en/Linux.md) | Deutsch | [Español](../es/Linux.md) | [Français](../fr/Linux.md) | [Italiano](../it/Linux.md) | [日本語](../ja/Linux.md) | [한국어](../ko/Linux.md) | [Português (BR)](../pt-br/Linux.md) | [Português (PT)](../pt-pt/Linux.md) | [简体中文](../zh-hans/Linux.md) | [繁體中文](../zh-hant/Linux.md)

# SCS0009 Servo Debug Tool — Linux-Anleitung

Für Ubuntu / Debian / andere gängige Distributionen. Kernpunkte: serielle Berechtigungen (dialout), Erkennung von USB-zu-Seriell-Geräten.

> ⚠️ **Kompatibilität: Dieses Werkzeug unterstützt derzeit nur Feetech SCS0009-Servos (SCS-Serie, Potentiometer-Positionsrückmeldung, 10-Bit-Auflösung 0-1023)**. Die Registertabelle und das xdat-Format sind für den Feetech SCS0009 ausgelegt; andere Marken/Modelle werden nicht garantiert.

---

## 1. Anforderungen

| Abhängigkeit | Version |
|-----------|---------|
| Python | >= 3.8 (3.10+ empfohlen) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| Betriebssystem | Ubuntu 20.04+ / Debian 11+ |

Chinesische Schriften (für die chinesische Oberfläche erforderlich):

```bash
sudo apt install fonts-noto-cjk
```

Emoji-Symbolschriften (für ✅⚠️ usw. in Logs):

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. Python-Abhängigkeiten installieren

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Erstellen Sie die virtuelle Umgebung nur EINMAL**. Ein erneutes Ausführen setzt die Umgebung zurück bzw. überschreibt sie (installierte Abhängigkeiten werden gelöscht). Danach einfach `source .venv/bin/activate`.

> Wenn pip "externally-managed-environment" meldet, verwenden Sie ein venv oder `pip install --break-system-packages -r requirements.txt`.

## 3. ⚠️ Serielle Berechtigung (dialout) [erforderlich]

Standardmäßig **können normale Benutzer nicht** auf `/dev/ttyUSB*` / `/dev/ttyACM*` **zugreifen**. Fügen Sie Ihren Benutzer zur Gruppe `dialout` hinzu:

```bash
sudo usermod -a -G dialout $USER
```

**Melden Sie sich ab und wieder an** (oder starten Sie neu). Überprüfen:

```bash
groups
# output should include dialout
```

> Manche Distributionen verwenden `uucp` (Arch) oder `tty`.

## 4. USB-Seriell-Gerät identifizieren

Nach dem Einstecken:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Typische Ausgabe:

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # native USB serial (Arduino/ESP32 onboard)
```

## 5. Umgebung prüfen

```bash
python setup.py
```

## 6. GUI starten

```bash
python -m src.gui.factory_calibration_tool
```

Port angeben:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> Wenn nur ein Port existiert, verwendet das Werkzeug ihn direkt.

## 7. Bedienablauf der Oberfläche

> Einteiliges Layout. Eine Bildlaufleiste erscheint automatisch, wenn das Fenster zu kurz ist; beim Maximieren dehnt es sich passend aus.

### 7.1 Serielle Verbindung
Wählen Sie Port und Baudrate (Standard 1M), klicken Sie auf **Verbinden**.

### 7.2 Servos scannen
Klicken Sie auf **Servos scannen** (ID 1-254); klicken Sie auf eine Listenzeile, um das Dropdown automatisch zu füllen.

### 7.3 Parameter lesen/schreiben
- Alle 44 Register lesen (EEPROM + SRAM), Punktauswahl-Verknüpfung füllt Adresse/Länge/Wert
- Schreiben mit automatischem Entsperren/Schreiben/Sperren; Erfolgs-/Fehler-Popup wird angezeigt

### 7.4 Positionssteuerung
Schieberegler ziehen (0-1023) oder Wert eingeben; Hinweis auf abgeschlossene Bewegung zum Ausschalten des Drehmoments.

### 7.5 Baudrate / Werksreset
Baudrate ändern (automatischer Rollback bei Fehler), Werksreset.

### 7.6 xdat-Parameter (nur EEPROM)
Aktuellen Servo speichern → Backup öffnen → auf Servo wiederherstellen.

## 8. Fehlerbehebung

| Problem | Lösung |
|---------|----------|
| **Permission denied: /dev/ttyUSB0** | Nicht in der dialout-Gruppe, siehe Abschnitt 3; oder `sudo chmod 666 /dev/ttyUSB0` (temporär) |
| Kein serieller Port | `ls /dev/ttyUSB* /dev/ttyACM*`; `lsusb` zur Bestätigung des Geräts |
| Gerätename ändert sich | Die ttyUSB-Nummerierung hängt von der Einsteckreihenfolge ab; verwenden Sie eine udev-Regel oder wählen Sie bei jedem Start aus |
| Chinesische UI leer | `fonts-noto-cjk` installieren |
| Emoji zeigt Kästchen | `fonts-noto-color-emoji` installieren |
| pip install schlägt fehl | venv verwenden; oder `--break-system-packages` |
| App startet nicht | `python3 --version` prüfen; `pip list` für Abhängigkeiten |

## 9. Kommandozeile (optional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. Erweitert: Fester Gerätename über udev (optional)

Erstellen Sie `/etc/udev/rules.d/99-servo.rules`, um den Gerätenamen über die USB-ID festzulegen:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

Dann `ls -l /dev/ttyServo`. Ermitteln Sie die Hersteller-ID mit `lsusb`.
