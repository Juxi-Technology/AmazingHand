[English](../en/Windows_Tutorial.md) | Deutsch | [Español](../es/Windows_Tutorial.md) | [Français](../fr/Windows_Tutorial.md) | [Italiano](../it/Windows_Tutorial.md) | [日本語](../ja/Windows_Tutorial.md) | [한국어](../ko/Windows_Tutorial.md) | [Português (BR)](../pt-br/Windows_Tutorial.md) | [Português (PT)](../pt-pt/Windows_Tutorial.md) | [简体中文](../zh-hans/Windows_Tutorial.md) | [繁體中文](../zh-hant/Windows_Tutorial.md)

# AmazingHand Dexterhand Hand-Tracking · Windows-Tutorial

Dieses Tutorial behandelt das offizielle Demo des AmazingHand (Dexterhand von Pollen Robotics) mit Ein-Klick-Deploy-Skripten.
Führen Sie die Skripte in der nummerierten Reihenfolge aus. **Alle Skripte befinden sich in `Demo\Windows_Deploy_Scripts\` — zum Ausführen doppelklicken.**

---

## Inhalt

1. [Hardware-Vorbereitung](#1-hardware-vorbereitung)
2. [Umgebung einrichten (Skript 1)](#2-umgebung-einrichten-skript-1)
3. [Verkabelung](#3-verkabelung)
4. [Serielle Schnittstelle einrichten (Skript 2)](#4-serielle-schnittstelle-einrichten-skript-2)
5. [Code bereitstellen (Skript 3)](#5-code-bereitstellen-skript-3)
6. [Demo ausführen (Skript 4)](#6-demo-ausführen-skript-4)
7. [Projekt aufräumen (Skript 0)](#7-projekt-aufräumen-skript-0)
8. [Fehlerbehebung & Hinweise](#8-fehlerbehebung--hinweise)
9. [Code-Struktur](#9-code-struktur)

---

## 1. Hardware-Vorbereitung

| Element | Anforderung |
|---|---|
| Dexterhand | Rechts / Links / Beide |
| Servo-Treiberplatine | Extern, USB zum PC |
| Stromversorgung | **Mindestens 5V 4A** (USB allein reicht nicht, verwenden Sie ein externes Netzteil) |
| Kamera | Integriert oder USB-Webcam |

> Modelldateien (URDF usw.) können bei [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e) angesehen/heruntergeladen werden.

---

## 2. Umgebung einrichten (Skript 1)

**Doppelklicken Sie auf `1-Install_Env.bat`** — es erledigt automatisch:

1. **Prüft die MSVC-Build-Tools** (cl.exe) — erforderlich zum Kompilieren von Rust. Falls sie fehlen, installieren Sie
   Visual Studio 2022 Build Tools mit der Workload "Desktop development with C++" und öffnen Sie das Terminal anschließend erneut.
2. **Installiert Rust** (rustup + stable-msvc Toolchain)
3. **Konfiguriert den cargo-tuna-Mirror** (`C:\Users\<you>\.cargo\config.toml`), um Crate-Downloads zu beschleunigen
4. **Installiert uv** (Python-Paketmanager)
5. **Installiert dora-cli 0.5.0** (`cargo install`, die erste Kompilierung dauert ~10–20 min, haben Sie Geduld)
6. **Installiert das dora-rs-pip-Paket** (optional; es wird bei der Bereitstellung auch in die venv installiert)

> **Wichtig**: **Schließen Sie das Terminal nach dem Skript und öffnen Sie es erneut**, damit die Umgebungsvariablen wirksam werden.
> Je nach Netzwerk können Downloads langsam sein — warten Sie, brechen Sie nicht ab.

### Manuelle Installation (falls das Skript nicht verwendbar ist)

- **Rust**: <https://www.rust-lang.org/tools/install> — verwenden Sie rustup-init.exe, standardmäßige MSVC-Toolchain.
  - PATH: fügen Sie `%USERPROFILE%\.cargo\bin` hinzu
- **uv**: PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`
  - PATH: fügen Sie `%USERPROFILE%\.local\bin` hinzu
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### cargo-tuna-Mirror (config.toml)

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

## 3. Verkabelung

- Verbinden Sie die Servo-Treiberplatine per USB mit dem PC, **versorgen Sie sie mit einer externen 5V-4A-Stromversorgung**
- Finden Sie den Port: **Geräte-Manager → Anschlüsse (COM & LPT)**, z. B. `COM11`

---

## 4. Serielle Schnittstelle einrichten (Skript 2)

**Doppelklicken Sie auf `2-Setup_Serial.bat`** (die Logik liegt in `2-Setup_Serial.ps1`):

1. "Connect the driver board" → drücken Sie die Eingabetaste zum Scannen
2. Erkannte COM-Ports werden aufgelistet (mit Gerätenamen)
3. Ein einzelner Port: drücken Sie die Eingabetaste zum Bestätigen; mehrere: geben Sie den Index ein
4. Es schreibt `--serialport` in die 3 dataflow-yml-Dateien und den Standardport in `AHControl\src\main.rs`
5. Die Originaldateien werden als `.bak` gesichert

> Wenn Sie das USB-Kabel erneut anstecken, kann sich die COM-Nummer ändern — führen Sie dieses Skript erneut aus.

---

## 5. Code bereitstellen (Skript 3)

**Doppelklicken Sie auf `3-Deploy_Demo.bat`** — es erledigt automatisch:

1. Startet den dora-Daemon (`dora up`)
2. Erstellt eine Python-3.12-venv (`uv venv --python 3.12`)
3. Aktiviert die venv
4. Baut den AHControl-Rust-Node (`cargo build --release`, beim ersten Mal ~10 min)
5. Synchronisiert die Abhängigkeiten von AHSimulation und HandTracking (`uv sync`)
6. Installiert mediapipe==0.10.14 zwangsweise (bekannte Stolperfalle, Fallback)

> Einmalig bereitstellen. Bei erneuter Ausführung wird gefragt, ob die venv neu gebaut werden soll.

---

## 6. Demo ausführen (Skript 4)

**Doppelklicken Sie auf `4-Run_Demo.bat`** — interaktives Menü:

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

> Beim ersten Start fragt Windows möglicherweise nach der Kameraberechtigung — klicken Sie auf "Allow".

---

## 7. Projekt aufräumen (Skript 0)

**Doppelklicken Sie auf `0-Cleanup_Project.bat`**, geben Sie `Y` zur Bestätigung ein:

1. Stoppt den dora-Daemon
2. Löscht die 3 virtuellen Umgebungen (`.venv`)
3. Löscht die Rust-Build-Ausgabe (`Demo\target`)
4. Löscht `__pycache__`, `.bak`-Sicherungen, Logs und `Demo\out` (dora-Logs)
5. **Stellt den Standardport wieder her** (`--serialport /dev/ttyACM0`) und entfernt die COM-Rückstände dieser Maschine

> Nach dem Aufräumen können Sie den gesamten Ordner `AmazingHand-main` auf eine andere Maschine kopieren — sauber und portabel.
> Führen Sie auf der neuen Maschine einfach 1 → 2 → 3 → 4 der Reihe nach aus.

---

## 8. Fehlerbehebung & Hinweise

### 8.1 cargo bleibt bei `Updating 'tuna' index` hängen

- Ursache: Mirror als **git-repo-Modus** konfiguriert (`.../git/crates.io-index.git`), der erste Lauf lädt einen Index von 1 GB+ herunter
- Lösung: Setzen Sie `C:\Users\<you>\.cargo\config.toml` auf den **sparse index** (siehe 2.3) oder führen Sie `1-Install_Env.bat` erneut aus

### 8.2 mediapipe: fehlendes solutions-Submodul / defekte Installation

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Führen Sie dies in der aktivierten venv aus (im Ordner `Demo`)
- `3-Deploy_Demo.bat` erledigt dies bereits als Fallback

### 8.3 dora-Versionskonflikt (Nachricht v0.8.0 vs. v0.7.0)

- Symptom: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Ursache: Die dora-cli-Version weicht von dora-node-api ab. **Beide müssen 0.5.0 sein**
  - Prüfen: `dora --version` sollte `dora-cli 0.5.0` und `dora-message: 0.8.0` ausgeben
  - Lösung: `cargo install dora-cli --version 0.5.0 --force`
  - `1-Install_Env.bat` erkennt alte Versionen jetzt automatisch und installiert 0.5.0 zwangsweise

### 8.4 Fehler beim Laden von MuJoCo-/mediapipe-Modellen (chinesische Pfade)

- Symptom: `ParseXML: Error opening file '...\scene.xml'` oder `Can't find file: ...\.tflite`
- Ursache: Die C++-Lader von MuJoCo 3.x / mediapipe scheitern an **absoluten Pfaden mit Nicht-ASCII-Zeichen (chinesisch)** (z. B. `D:\Claude工作区\...`)
- Dieses Projekt enthält bereits Korrekturen:
  - `AHSimulation\AHSimulation\mj_mink_*.py` wechselt das Arbeitsverzeichnis vor dem Laden
  - `HandTracking\mediapipe_patch.py` verwendet 8.3-Kurznamen + relative Pfade
- **Löschen Sie diese Korrekturdateien nicht**

### 8.5 Kamera-Berechtigung

- Beim ersten Start: Wählen Sie "Allow"
- Einstellungen → Datenschutz → Kamera → Desktop-Apps erlauben

### 8.6 Portnummer ändert sich bei jedem Mal

- Nach dem erneuten Anstecken von USB kann sich die COM-Nummer ändern — führen Sie `2-Setup_Serial.bat` erneut aus

### 8.7 OpenCV fehlt

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(im Ordner `HandTracking`, venv aktiviert)

---

## 9. Code-Struktur

### Demo-Ordner

| Pfad | Beschreibung |
|---|---|
| `AHControl` | Rust-Node, der die Servos steuert. Einstieg: `src/main.rs` |
| `AHSimulation` | Python-Node: MuJoCo-Simulation + inverse Kinematik (mink) |
| `HandTracking` | Python-Node: MediaPipe-Hand-Tracking |
| `dataflow_*.yml` | dora-Dataflow-Definitionen (Node-Graph) |
| `Windows_Deploy_Scripts` | Dieses Skriptpaket |

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

- Die Zeile `args:` der 3 Dateien `dataflow_tracking_real_*.yml`: `--serialport COMxx`
- `AHControl\src\main.rs` `default_value = "COMxx"` (Standard der seriellen Schnittstelle)
- `AHControl\config\*.toml`: Servo-Modell, IDs, Offsets (in der Regel keine Änderung nötig)
