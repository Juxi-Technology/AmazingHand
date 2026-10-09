[English](../en/Mac_Tutorial.md) | Deutsch | [Español](../es/Mac_Tutorial.md) | [Français](../fr/Mac_Tutorial.md) | [Italiano](../it/Mac_Tutorial.md) | [日本語](../ja/Mac_Tutorial.md) | [한국어](../ko/Mac_Tutorial.md) | [Português (BR)](../pt-br/Mac_Tutorial.md) | [Português (PT)](../pt-pt/Mac_Tutorial.md) | [简体中文](../zh-hans/Mac_Tutorial.md) | [繁體中文](../zh-hant/Mac_Tutorial.md)

# AmazingHand Dexterhand Hand-Tracking · macOS-Tutorial

Dieses Tutorial behandelt das offizielle Demo des AmazingHand (Dexterhand von Pollen Robotics) mit Ein-Klick-Deploy-Skripten.
Führen Sie die Skripte in der nummerierten Reihenfolge aus. **Alle Skripte befinden sich in `Demo/Mac_Deploy_Scripts/` — führen Sie `./script` in einem Terminal aus.**

---

## Inhalt

1. [Hardware-Vorbereitung](#1-hardware-vorbereitung)
2. [Skript-Ausführungsrechte vergeben (Wichtig)](#2-skript-ausführungsrechte-vergeben-wichtig)
3. [Umgebung einrichten (Skript 1)](#3-umgebung-einrichten-skript-1)
4. [Verkabelung](#4-verkabelung)
5. [Serielle Schnittstelle einrichten (Skript 2)](#5-serielle-schnittstelle-einrichten-skript-2)
6. [Code bereitstellen (Skript 3)](#6-code-bereitstellen-skript-3)
7. [Demo ausführen (Skript 4)](#7-demo-ausführen-skript-4)
8. [Projekt aufräumen (Skript 0)](#8-projekt-aufräumen-skript-0)
9. [Fehlerbehebung & Hinweise](#9-fehlerbehebung--hinweise)
10. [Code-Struktur](#10-code-struktur)

---

## 1. Hardware-Vorbereitung

| Element | Anforderung |
|---|---|
| Dexterhand | Rechts / Links / Beide |
| Servo-Treiberplatine | Extern, USB zum PC |
| Stromversorgung | **Mindestens 5V 4A** (USB allein reicht nicht, verwenden Sie ein externes Netzteil) |
| Kamera | Integriert oder USB-Webcam |

> Modelldateien (URDF usw.) können bei [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e) angesehen/heruntergeladen werden.
> Unterstützt Apple Silicon (M1/M2/M3/M4) und Intel-Macs.

---

## 2. Skript-Ausführungsrechte vergeben (Wichtig)

**Wenn Skripte von Windows oder aus einem ZIP-Archiv nach macOS kopiert werden, geht das Ausführungsrecht (`+x`) verloren** — beim direkten Ausführen erscheint
`Permission denied`. **Führen Sie dies einmal vor der ersten Verwendung aus:**

```bash
cd "AmazingHand-main/Demo/Mac_Deploy_Scripts"
chmod +x *.sh
```

Danach kann jedes Skript mit `./script` ausgeführt werden.

> Tipp: Um den Ordner `AmazingHand-main` unter Beibehaltung der Rechte nach macOS zu übertragen, packen Sie ihn mit **tar**:
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`, oder führen Sie nach dem Entpacken einfach einmal `chmod +x *.sh` aus.

---

## 3. Umgebung einrichten (Skript 1)

Führen Sie im Skriptordner aus (nach dem `chmod +x` in Schritt 2):

```bash
cd "AmazingHand-main/Demo/Mac_Deploy_Scripts"
./1-Install_Env.sh
```

Es erledigt automatisch:

1. **Prüft die Xcode Command Line Tools** (erforderlich zum Kompilieren von Rust). Falls sie fehlen, führen Sie `xcode-select --install` aus
2. **Installiert Rust** (rustup + stable Toolchain)
3. **Konfiguriert den cargo-tuna-Mirror** (`~/.cargo/config.toml`), um Crate-Downloads zu beschleunigen
4. **Installiert uv** (Python-Paketmanager)
5. **Installiert dora-cli 0.5.0** (`cargo install`, die erste Kompilierung dauert ~10–20 min, haben Sie Geduld). Alte dora-Versionen werden automatisch erkannt und zwangsweise ersetzt.
6. **Installiert das dora-rs-pip-Paket** (optional)

> **Wichtig**: **Schließen Sie das Terminal nach dem Skript und öffnen Sie es erneut**, damit die Umgebungsvariablen wirksam werden.
> Falls eine Version leer angezeigt wird, fügen Sie Folgendes zu `~/.zshrc` hinzu:
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### Manuelle Installation (falls das Skript nicht verwendbar ist)

- **Xcode Command Line Tools**: `xcode-select --install`
- **Rust**: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### cargo-tuna-Mirror (~/.cargo/config.toml)

```
[source.crates-io]
replace-with = "tuna"

[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[registries.tuna]
index = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[http]
check-revoke = false
```

> Verwenden Sie den **sparse index** (oben), NICHT den git-repo-Mirror — der git-Mirror lädt zuerst ~1 GB Index herunter und bleibt oft bei `Updating 'tuna' index` hängen.

---

## 4. Verkabelung

- Verbinden Sie die Servo-Treiberplatine per USB mit dem PC, **versorgen Sie sie mit einer externen 5V-4A-Stromversorgung**
- Die Namen der USB-Seriell-Geräte unter macOS sind **`/dev/tty.usbmodem*`** oder **`/dev/cu.usbmodem*`** (NICHT `/dev/ttyACM*` wie unter Linux)
- Finden Sie den Port:
  ```bash
  ls /dev/tty.usbmodem* /dev/cu.usbmodem*
  ```

---

## 5. Serielle Schnittstelle einrichten (Skript 2)

**Führen Sie `./2-Setup_Serial.sh` aus**:

1. "Connect the driver board" → drücken Sie die Eingabetaste zum Scannen
2. Erkannte serielle Ports werden aufgelistet (`/dev/tty.usbmodem*` / `/dev/cu.usbmodem*` / `*.usbserial*`)
3. Ein einzelner Port: drücken Sie die Eingabetaste zum Bestätigen; mehrere: geben Sie den Index ein
4. Es schreibt `--serialport` in die 3 dataflow-yml-Dateien und den Standardport in `AHControl/src/main.rs`
5. Die USB-Seriell-Ports unter macOS sind für den Benutzer üblicherweise lesbar. Bei verweigertem Zugriff führen Sie manuell aus:
   ```bash
   sudo chmod 666 /dev/cu.usbmodem*
   ```
   Oder erlauben Sie das Terminal unter **Systemeinstellungen → Datenschutz & Sicherheit → Eingabeüberwachung**.

> Wenn Sie sich in einer VM befinden, verbinden Sie das USB-Gerät mit der VM.

---

## 6. Code bereitstellen (Skript 3)

**Führen Sie `./3-Deploy_Demo.sh` aus** — es erledigt automatisch:

1. Startet den dora-Daemon (`dora up`)
2. Erstellt eine Python-3.12-venv (`uv venv --python 3.12`)
3. Aktiviert die venv
4. Baut den AHControl-Rust-Node (`cargo build --release`, beim ersten Mal ~10 min)
5. Synchronisiert die Abhängigkeiten von AHSimulation und HandTracking (`uv sync`)
6. Installiert mediapipe==0.10.14 zwangsweise (bekannte Stolperfalle, Fallback)

> Einmalig bereitstellen. Bei erneuter Ausführung wird gefragt, ob die venv neu gebaut werden soll.

---

## 7. Demo ausführen (Skript 4)

**Führen Sie `./4-Run_Demo.sh` aus** — interaktives Menü:

```
============================================
  Select a run mode:
============================================
   1 - Simulation (webcam hand tracking)
   2 - Real hardware
   q - Quit
============================================
Enter number [1/2/q]:
```

- **1**: Simulation — Webcam-Gesten steuern zwei simulierte Hände
- **2**: Echte Hardware — Untermenü für rechte / linke / beide Hände

```
============================================
  Real hardware - select the hand:
============================================
   1 - Right hand
   2 - Left hand
   3 - Both hands
   b - Back to main menu
============================================
```

Anschließend werden `dora build` + `dora run` ausgeführt. Ein Kamerafenster öffnet sich; machen Sie Handgesten, um die Hand bzw. Hände in Echtzeit zu bewegen. **Ctrl+C zum Beenden**. Nach dem Ende des Dataflows drücken Sie die Eingabetaste, um zum Menü zurückzukehren und einen anderen Modus zu wählen, oder `q` zum Beenden.

> **Beim ersten Start fragt macOS nach der Kameraberechtigung**: Systemeinstellungen → Datenschutz & Sicherheit → Kamera → Terminal erlauben.

---

## 8. Projekt aufräumen (Skript 0)

**Führen Sie `./0-Cleanup_Project.sh` aus**, geben Sie `Y` zur Bestätigung ein:

1. Stoppt den dora-Daemon
2. Löscht die 3 virtuellen Umgebungen (`.venv`)
3. Löscht die Rust-Build-Ausgabe (`Demo/target`)
4. Löscht `__pycache__`, `.bak`-Sicherungen, Logs und `Demo/out` (dora-Logs)
5. **Stellt den Standardport wieder her** (`--serialport /dev/ttyACM0`) und entfernt die Port-Rückstände dieser Maschine

> Nach dem Aufräumen können Sie den gesamten Ordner `AmazingHand-main` auf eine andere Maschine kopieren — sauber und portabel.
> Führen Sie auf der neuen Maschine einfach 1 → 2 → 3 → 4 der Reihe nach aus.

---

## 9. Fehlerbehebung & Hinweise

### 9.1 `Permission denied` (Skript hat kein Ausführungsrecht)

- Symptom: `bash: ./1-Install_Env.sh: Permission denied`
- Ursache: Das Skript hat sein Ausführungsbit verloren, als es von Windows / aus einem ZIP kopiert wurde
- Lösung:
  ```bash
  chmod +x *.sh
  ```

### 9.2 cargo bleibt bei `Updating 'tuna' index` hängen

- Ursache: Mirror als **git-repo-Modus** konfiguriert (`.../git/crates.io-index.git`), der erste Lauf lädt einen Index von 1 GB+ herunter
- Lösung: Setzen Sie `~/.cargo/config.toml` auf den **sparse index** (siehe 3.2) oder führen Sie `1-Install_Env.sh` erneut aus

### 9.3 mediapipe: fehlendes solutions-Submodul / defekte Installation

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Führen Sie dies in der aktivierten venv aus (im Ordner `Demo`)
- `3-Deploy_Demo.sh` erledigt dies bereits als Fallback

### 9.4 dora-Versionskonflikt (Nachricht v0.8.0 vs. v0.7.0)

- Symptom: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Ursache: Die dora-cli-Version weicht von dora-node-api ab. **Beide müssen 0.5.0 sein**
  - Prüfen: `dora --version` sollte `dora-cli 0.5.0` und `dora-message: 0.8.0` ausgeben
  - `1-Install_Env.sh` erkennt alte Versionen automatisch und installiert 0.5.0 zwangsweise

**Wenn ein altes dora (z. B. 0.4.1) im System verbleibt, räumen Sie es zuerst auf:**

```bash
# 1. Find where the old dora is
which dora
ls -la ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora 2>/dev/null

# 2. Delete the found old versions (adjust paths; there may be several)
rm -f ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora

# 3. Force-install 0.5.0 (goes to ~/.cargo/bin)
cargo install dora-cli --version 0.5.0 --force

# 4. Verify (should print dora-cli 0.5.0 / dora-message: 0.8.0)
dora --version
```

> Wenn `dora --version` weiterhin eine alte Version anzeigt, versteckt sich eine weitere alte Kopie irgendwo im PATH — finden und entfernen Sie sie mit `which dora`.

### 9.5 Serielle Schnittstelle: Zugriff verweigert

```bash
sudo chmod 666 /dev/cu.usbmodem*
```

- Oder erlauben Sie das Terminal unter **Systemeinstellungen → Datenschutz & Sicherheit → Eingabeüberwachung**
- Lässt sich ein `tty.*`-Gerät nicht lesen, verwenden Sie stattdessen das passende `cu.*`-Gerät (das cu-Gerät ist der bevorzugte Lese-/Schreibport für die direkte Steuerung)

### 9.6 Kamera-Berechtigung

- **Beim ersten Start: Klicken Sie auf "Allow"** im Popup, oder erlauben Sie das Terminal unter **Systemeinstellungen → Datenschutz & Sicherheit → Kamera**
- Stellen Sie sicher, dass keine andere Anwendung (FaceTime, Konferenz-Apps) die Kamera verwendet

### 9.7 Portnummer ändert sich bei jedem Mal

- Nach dem erneuten Anstecken von USB kann sich der Gerätename ändern — führen Sie `2-Setup_Serial.sh` erneut aus

### 9.8 OpenCV fehlt

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(im Ordner `HandTracking`, venv aktiviert)

### 9.9 Apple Silicon: langsame erste Kompilierung / Gatekeeper-Abfrage

- Das erste `cargo build` auf Apple Silicon kompiliert viele dora-Abhängigkeiten — langsam ist normal, haben Sie Geduld
- Erscheint eine Abfrage "developer cannot be verified": Systemeinstellungen → Datenschutz & Sicherheit → Trotzdem öffnen

---

## 10. Code-Struktur

### Demo-Ordner

| Pfad | Beschreibung |
|---|---|
| `AHControl` | Rust-Node, der die Servos steuert. Einstieg: `src/main.rs` |
| `AHSimulation` | Python-Node: MuJoCo-Simulation + inverse Kinematik (mink) |
| `HandTracking` | Python-Node: MediaPipe-Hand-Tracking |
| `dataflow_*.yml` | dora-Dataflow-Definitionen (Node-Graph) |
| `Mac_Deploy_Scripts` | Dieses Skriptpaket |

### dataflow-Dateien

| Datei | Zweck |
|---|---|
| `dataflow_tracking_simu.yml` | Simulation: Webcam-Gesten → simulierte Hände |
| `dataflow_tracking_real_right.yml` | Echte rechte Hand |
| `dataflow_tracking_real_left.yml` | Echte linke Hand |
| `dataflow_tracking_real_2hands.yml` | Beide echten Hände (gleiche Treiberplatine) |

### Dataflow-Prinzip

```
Webcam → HandTracking (MediaPipe hand detection)
              ↓ hand keypoints
         AHSimulation (MuJoCo simulation + IK)
              ↓ joint target angles
         AHControl (serial → servo driver board → hand)
```

### Positionen der Portkonfiguration

- Die Zeile `args:` der 3 Dateien `dataflow_tracking_real_*.yml`: `--serialport /dev/cu.usbmodem...`
- `AHControl/src/main.rs` `default_value` (Standard der seriellen Schnittstelle)
- `AHControl/config/*.toml`: Servo-Modell, IDs, Offsets (in der Regel keine Änderung nötig)
