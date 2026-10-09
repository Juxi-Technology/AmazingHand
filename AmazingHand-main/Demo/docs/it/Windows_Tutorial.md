[English](../en/Windows_Tutorial.md) | [Deutsch](../de/Windows_Tutorial.md) | [Español](../es/Windows_Tutorial.md) | [Français](../fr/Windows_Tutorial.md) | Italiano | [日本語](../ja/Windows_Tutorial.md) | [한국어](../ko/Windows_Tutorial.md) | [Português (BR)](../pt-br/Windows_Tutorial.md) | [Português (PT)](../pt-pt/Windows_Tutorial.md) | [简体中文](../zh-hans/Windows_Tutorial.md) | [繁體中文](../zh-hant/Windows_Tutorial.md)

# AmazingHand, mano robotica · Hand-tracking · Tutorial Windows

Questo tutorial illustra la Demo ufficiale dell'AmazingHand (mano robotica Pollen Robotics) con script di deploy in un clic.
Eseguire gli script nell'ordine numerato. **Tutti gli script si trovano in `Demo\Windows_Deploy_Scripts\` — fare doppio clic per eseguirli.**

---

## Indice

1. [Preparazione hardware](#1-preparazione-hardware)
2. [Configurazione dell'ambiente (script 1)](#2-configurazione-dellambiente-script-1)
3. [Cablaggio](#3-cablaggio)
4. [Configurazione della porta seriale (script 2)](#4-configurazione-della-porta-seriale-script-2)
5. [Deploy del codice (script 3)](#5-deploy-del-codice-script-3)
6. [Eseguire la Demo (script 4)](#6-eseguire-la-demo-script-4)
7. [Pulizia del progetto (script 0)](#7-pulizia-del-progetto-script-0)
8. [Risoluzione dei problemi e note](#8-risoluzione-dei-problemi-e-note)
9. [Struttura del codice](#9-struttura-del-codice)

---

## 1. Preparazione hardware

| Voce | Requisito |
|---|---|
| Mano robotica | Destra / Sinistra / Entrambe |
| Scheda di controllo dei servo | Esterna, USB verso il PC |
| Alimentazione | **Almeno 5V 4A** (l'USB da solo non è sufficiente, usare un alimentatore esterno) |
| Fotocamera | Integrata o webcam USB |

> I file del modello (URDF ecc.) possono essere visualizzati/scaricati su [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e).

---

## 2. Configurazione dell'ambiente (script 1)

**Fare doppio clic su `1-Install_Env.bat`** — automaticamente:

1. **Verifica i build tools MSVC** (cl.exe) — necessari per compilare Rust. Se mancano, installare Visual Studio 2022 Build Tools con il carico di lavoro "Sviluppo desktop con C++", poi riaprire il terminale.
2. **Installa Rust** (rustup + toolchain stable-msvc)
3. **Configura il mirror tuna di cargo** (`C:\Users\<you>\.cargo\config.toml`) per accelerare il download dei crate
4. **Installa uv** (gestore di pacchetti Python)
5. **Installa dora-cli 0.5.0** (`cargo install`, la prima compilazione richiede ~10–20 min, portare pazienza)
6. **Installa il pacchetto pip dora-rs** (opzionale; viene installato anche nel venv durante il deploy)

> **Importante**: **chiudere e riaprire il terminale** dopo lo script affinché le variabili d'ambiente abbiano effetto.
> I download possono essere lenti a seconda della rete — attendere, non interrompere.

### Installazione manuale (se lo script non è utilizzabile)

- **Rust**: <https://www.rust-lang.org/tools/install> — usare rustup-init.exe, toolchain MSVC predefinita.
  - PATH: aggiungere `%USERPROFILE%\.cargo\bin`
- **uv**: PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`
  - PATH: aggiungere `%USERPROFILE%\.local\bin`
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### Mirror tuna di cargo (config.toml)

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

> Usare lo **sparse index** (sopra), NON il mirror git-repo — il mirror git scarica prima ~1 GB di indice e spesso si blocca su `Updating 'tuna' index`.

---

## 3. Cablaggio

- Collegare la scheda di controllo dei servo al PC tramite USB, **alimentarla con un alimentatore esterno da 5V 4A**
- Trovare la porta: **Gestione dispositivi → Porte (COM e LPT)**, ad es. `COM11`

---

## 4. Configurazione della porta seriale (script 2)

**Fare doppio clic su `2-Setup_Serial.bat`** (la logica è in `2-Setup_Serial.ps1`):

1. "Collegare la scheda di controllo" → premere Invio per eseguire la scansione
2. Vengono elencate le porte COM rilevate (con i nomi dei dispositivi)
3. Porta singola: premere Invio per confermare; più porte: digitare l'indice
4. Scrive `--serialport` nei 3 file yml del dataflow e la porta predefinita in `AHControl\src\main.rs`
5. I file originali vengono salvati come `.bak`

> Se si ricollega il cavo USB, il numero di COM può cambiare — rieseguire questo script.

---

## 5. Deploy del codice (script 3)

**Fare doppio clic su `3-Deploy_Demo.bat`** — automaticamente:

1. Avvia il demone dora (`dora up`)
2. Crea un venv Python 3.12 (`uv venv --python 3.12`)
3. Attiva il venv
4. Compila il nodo Rust AHControl (`cargo build --release`, la prima volta ~10 min)
5. Sincronizza le dipendenze di AHSimulation e HandTracking (`uv sync`)
6. Installa forzatamente mediapipe==0.10.14 (problema noto, fallback)

> Eseguire il deploy una sola volta. Rieseguendolo viene chiesto se ricostruire il venv.

---

## 6. Eseguire la Demo (script 4)

**Fare doppio clic su `4-Run_Demo.bat`** — menu interattivo:

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

- **1**: Simulazione — i gesti davanti alla webcam pilotano due mani simulate
- **2**: Hardware reale — sottomenu per mano destra / sinistra / entrambe

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

Poi esegue `dora build` + `dora run`. Si apre una finestra della fotocamera; fare gesti con la mano per muovere la o le mani in tempo reale. **Ctrl+C per fermare**. Al termine del dataflow, premere Invio per tornare al menu e scegliere un'altra modalità, oppure `q` per uscire.

> Al primo avvio, Windows può chiedere il permesso per la fotocamera — fare clic su "Consenti".

---

## 7. Pulizia del progetto (script 0)

**Fare doppio clic su `0-Cleanup_Project.bat`**, digitare `Y` per confermare:

1. Arresta il demone dora
2. Elimina i 3 ambienti virtuali (`.venv`)
3. Elimina l'output di compilazione Rust (`Demo\target`)
4. Elimina `__pycache__`, i backup `.bak`, i log e `Demo\out` (log di dora)
5. **Ripristina la porta predefinita** (`--serialport /dev/ttyACM0`), rimuovendo i residui di COM di questa macchina

> Dopo la pulizia è possibile copiare l'intera cartella `AmazingHand-main` su un'altra macchina — pulita e portabile.
> Sulla nuova macchina eseguire semplicemente 1 → 2 → 3 → 4 nell'ordine.

---

## 8. Risoluzione dei problemi e note

### 8.1 cargo bloccato su `Updating 'tuna' index`

- Causa: mirror configurato in **modalità git-repo** (`.../git/crates.io-index.git`), la prima esecuzione scarica un indice da 1 GB+
- Soluzione: impostare `C:\Users\<you>\.cargo\config.toml` sullo **sparse index** (vedere 2.3), oppure rieseguire `1-Install_Env.bat`

### 8.2 sottomodulo solutions di mediapipe mancante / installazione non funzionante

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Eseguire all'interno del venv attivato (nella cartella `Demo`)
- `3-Deploy_Demo.bat` lo fa già come fallback

### 8.3 versione di dora non corrispondente (messaggio v0.8.0 vs v0.7.0)

- Sintomo: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Causa: la versione di dora-cli è diversa da quella di dora-node-api. **Devono essere entrambe 0.5.0**
  - Verifica: `dora --version` deve stampare `dora-cli 0.5.0` e `dora-message: 0.8.0`
  - Soluzione: `cargo install dora-cli --version 0.5.0 --force`
  - `1-Install_Env.bat` ora rileva automaticamente le versioni vecchie e installa forzatamente la 0.5.0

### 8.4 Caricamento del modello MuJoCo / mediapipe non riuscito (percorsi in cinese)

- Sintomo: `ParseXML: Error opening file '...\scene.xml'` oppure `Can't find file: ...\.tflite`
- Causa: i loader C++ di MuJoCo 3.x / mediapipe falliscono su **percorsi assoluti contenenti caratteri non ASCII (cinesi)** (ad es. `D:\Claude工作区\...`)
- Questo progetto include già le correzioni:
  - `AHSimulation\AHSimulation\mj_mink_*.py` cambia la directory di lavoro prima del caricamento
  - `HandTracking\mediapipe_patch.py` usa i percorsi brevi 8.3 + percorsi relativi
- **Non eliminare questi file di correzione**

### 8.5 Permesso della fotocamera

- Primo avvio: scegliere "Consenti"
- Impostazioni → Privacy → Fotocamera → consentire l'accesso alle app desktop

### 8.6 Il numero di porta cambia ogni volta

- Dopo aver ricollegato l'USB il numero di COM può cambiare — rieseguire `2-Setup_Serial.bat`

### 8.7 OpenCV mancante

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(nella cartella `HandTracking`, venv attivato)

---

## 9. Struttura del codice

### Cartella Demo

| Percorso | Descrizione |
|---|---|
| `AHControl` | Nodo Rust che controlla i servo. Entry: `src/main.rs` |
| `AHSimulation` | Nodo Python: simulazione MuJoCo + cinematica inversa (mink) |
| `HandTracking` | Nodo Python: hand tracking con MediaPipe |
| `dataflow_*.yml` | Definizioni dei dataflow di dora (grafo dei nodi) |
| `Windows_Deploy_Scripts` | Questo pacchetto di script |

### file dataflow

| File | Scopo |
|---|---|
| `dataflow_tracking_simu.yml` | Simulazione: gesti della webcam → mani simulate |
| `dataflow_tracking_real_right.yml` | Mano destra reale |
| `dataflow_tracking_real_left.yml` | Mano sinistra reale |
| `dataflow_tracking_real_2hands.yml` | Entrambe le mani reali (stessa scheda di controllo) |

### Principio del dataflow

```
Webcam → HandTracking (MediaPipe hand detection)
              ↓ hand keypoints
         AHSimulation (MuJoCo simulation + IK)
              ↓ joint target angles
         AHControl (serial → servo driver board → hand)
```

### Posizioni di configurazione della porta

- La riga `args:` dei 3 file `dataflow_tracking_real_*.yml`: `--serialport COMxx`
- `AHControl\src\main.rs` `default_value = "COMxx"` (default della serialport)
- `AHControl\config\*.toml`: modello dei servo, ID, offset (di solito non serve modificarli)
