[English](../en/Windows.md) | Deutsch | [Español](../es/Windows.md) | [Français](../fr/Windows.md) | [Italiano](../it/Windows.md) | [日本語](../ja/Windows.md) | [한국어](../ko/Windows.md) | [Português (BR)](../pt-br/Windows.md) | [Português (PT)](../pt-pt/Windows.md) | [简体中文](../zh-hans/Windows.md) | [繁體中文](../zh-hant/Windows.md)

# SCS0009 Servo Debug Tool — Windows-Anleitung

Für Windows 10 / 11. Deckt alles von der Installation bis zum vollständigen Servo-Debugging ab.

> ⚠️ **Kompatibilität: Dieses Werkzeug unterstützt derzeit nur Feetech SCS0009-Servos (SCS-Serie, Potentiometer-Positionsrückmeldung, 10-Bit-Auflösung 0-1023)**. Die Registertabelle und das xdat-Format sind für den Feetech SCS0009 ausgelegt; andere Marken/Modelle werden nicht garantiert.

---

## 1. Anforderungen

| Abhängigkeit | Version | Hinweise |
|-----------|---------|-------|
| Python | >= 3.8 | 3.10+ empfohlen, Download von [python.org](https://www.python.org/downloads/) |
| PySide6 | >= 6.0 | GUI-Framework |
| pyserial | >= 3.5 | Serielle Kommunikation |
| Betriebssystem | Win10 / Win11 | Jede Edition |

## 2. Python installieren

1. Besuchen Sie <https://www.python.org/downloads/>
2. Laden Sie den Python-3.10+-Installer herunter
3. **Aktivieren Sie während der Installation "Add Python to PATH"** (andernfalls wird python im Terminal nicht gefunden)

Überprüfen:

```bash
python --version
```

## 3. Abhängigkeiten installieren

Installieren Sie in einer virtuellen Umgebung, um das System-Python nicht zu verunreinigen:

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **Erstellen Sie die virtuelle Umgebung nur EINMAL**. Ein erneutes Ausführen setzt die Umgebung zurück bzw. überschreibt sie (installierte Abhängigkeiten werden gelöscht). Danach einfach jedes Mal `activate` ausführen.

> Die Eingabeaufforderung zeigt nach der Aktivierung `(.venv)`.

## 4. Umgebung prüfen

```bash
python setup.py
```

`[OK] 环境检查通过，可以运行项目` bedeutet, dass die Umgebung bereit ist.

## 5. Hardware anschließen

1. Stecken Sie den USB-zu-Seriell-Adapter ein (CH340 / CP2102)
2. Schließen Sie den Servocontroller an (Roboterarm-Steuerplatine)
3. Versorgen Sie die Servos mit Strom (DC 5V 5A Standard, DC 12V 5A Pro)

Prüfen Sie den COM-Port im Geräte-Manager (`Win+X` → Geräte-Manager):

```
Ports (COM & LPT)
  └─ USB-SERIAL CH340 (COM3)     ← your servo port
```

> **Notieren Sie sich die COM-Nummer**, um sie beim Start auszuwählen.

## 6. GUI starten

```bash
python -m src.gui.factory_calibration_tool
```

Oder den Port angeben:

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

Verfügbare Ports auflisten:

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. Bedienablauf der Oberfläche

> Einteiliges Layout. Eine Bildlaufleiste erscheint automatisch, wenn das Fenster zu kurz ist; beim Maximieren dehnt es sich passend aus.

### 7.1 Serielle Verbindung

- Wählen Sie Port und Baudrate (Standard 1M), klicken Sie auf **Verbinden**
- Der Status zeigt `🟢 Connected`

### 7.2 Servos scannen

- Klicken Sie auf **Servos scannen**, um online befindliche Servos zu erkennen (ID 1-254)
- Ergebnisse erscheinen in Echtzeit in der Servoliste (mit Modell)
- Klicken Sie auf eine Zeile in der Liste → das Servo-Dropdown wird automatisch gefüllt

### 7.3 Parameter lesen/schreiben

- **Parameter lesen**: liest alle 44 Register (EEPROM + SRAM), das Log zeigt die Ergebnisse live
- **Parametertabelle**: 5 Spalten (Adresse/Register/Wert/Speicher/Zugriff), farbcodiert nach EEPROM/SRAM/DEFAULT
- **Zeilenauswahl-Verknüpfung**: Klicken Sie auf eine Zeile → füllt „Write Address", „Length", „Value" automatisch
- **Schreiben**: Wert ändern und dann auf Schreiben klicken; das Werkzeug entsperrt/schreibt/sperrt das EEPROM automatisch
- **Popup mit Schreibergebnis**: grün "✅ Written successfully" bei Erfolg, rot "❌ Write failed" (mit Grund) bei Fehler

### 7.4 Positionssteuerung

- **Schieberegler**: ziehen, um die Zielposition anzupassen (0-1023), das Wertfeld wird live aktualisiert
- **Wertfeld**: Zielposition direkt eingeben, der Schieberegler folgt
- Nach der Bewegung zeigt der Status "move complete, please turn off torque" an

### 7.5 Baudrate / Werksreset

- **Baudrate ändern**: 38400-1000000 bps auswählen, automatischer Rollback bei Fehler
- **Werksreset**: Werksstandardwerte wiederherstellen (ID=1, baud=1M), erneutes Scannen erforderlich

### 7.6 xdat-Parameter (nur EEPROM)

1. `💾 Aktuellen Servo speichern`: aktuelle EEPROM-Parameter des Servos in eine xdat-Datei speichern (Backup)
2. `📂 xdat öffnen`: eine Backup-Datei laden
3. `📤 Auf Servo wiederherstellen`: das Backup zurück auf den Servo schreiben

## 8. Fehlerbehebung

| Problem | Lösung |
|---------|----------|
| Kein serieller Port | Treiber im Geräte-Manager prüfen; einen anderen USB-Port versuchen; CH340-Treiber installieren |
| Port belegt | Serielle Monitore schließen; das Werkzeug neu starten |
| Chinesischer Text leer | Das System hat Microsoft YaHei; CJK-Schrift installieren, falls defekt |
| Servo nicht gefunden | Stromversorgung/Verkabelung prüfen; 1M-Baudrate bestätigen |
| Schreiben fehlgeschlagen | Servostromversorgung und Verbindung prüfen; bestätigen, dass das Register beschreibbar ist |
| PermissionError beim Öffnen des Ports | Sicherstellen, dass kein anderer Prozess den COM-Port belegt |

## 9. Kommandozeile (optional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port COM3
```
