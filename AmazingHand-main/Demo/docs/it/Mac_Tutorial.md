[English](../en/Mac_Tutorial.md) | [Deutsch](../de/Mac_Tutorial.md) | [Español](../es/Mac_Tutorial.md) | [Français](../fr/Mac_Tutorial.md) | Italiano | [日本語](../ja/Mac_Tutorial.md) | [한국어](../ko/Mac_Tutorial.md) | [Português (BR)](../pt-br/Mac_Tutorial.md) | [Português (PT)](../pt-pt/Mac_Tutorial.md) | [简体中文](../zh-hans/Mac_Tutorial.md) | [繁體中文](../zh-hant/Mac_Tutorial.md)

# AmazingHand, mano robotica · Hand-tracking · Tutorial macOS

Questo tutorial illustra la Demo ufficiale dell'AmazingHand (mano robotica Pollen Robotics) con script di deploy in un clic.
Eseguire gli script nell'ordine numerato. **Tutti gli script si trovano in `Demo/Mac_Deploy_Scripts/` — eseguire `./script` da un terminale.**

---

## Indice

1. [Preparazione hardware](#1-preparazione-hardware)
2. [Concedere i permessi agli script (importante)](#2-concedere-i-permessi-agli-script-importante)
3. [Configurazione dell'ambiente (script 1)](#3-configurazione-dellambiente-script-1)
4. [Cablaggio](#4-cablaggio)
5. [Configurazione della porta seriale (script 2)](#5-configurazione-della-porta-seriale-script-2)
6. [Deploy del codice (script 3)](#6-deploy-del-codice-script-3)
7. [Eseguire la Demo (script 4)](#7-eseguire-la-demo-script-4)
8. [Pulizia del progetto (script 0)](#8-pulizia-del-progetto-script-0)
9. [Risoluzione dei problemi e note](#9-risoluzione-dei-problemi-e-note)
10. [Struttura del codice](#10-struttura-del-codice)

---

## 1. Preparazione hardware

| Voce | Requisito |
|---|---|
| Mano robotica | Destra / Sinistra / Entrambe |
| Scheda di controllo dei servo | Esterna, USB verso il PC |
| Alimentazione | **Almeno 5V 4A** (l'USB da solo non è sufficiente, usare un alimentatore esterno) |
| Fotocamera | Integrata o webcam USB |

> I file del modello (URDF ecc.) possono essere visualizzati/scaricati su [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e).
> Supporta i Mac Apple Silicon (M1/M2/M3/M4) e Intel.

---

## 2. Concedere i permessi agli script (importante)

**Quando gli script vengono copiati da Windows o da uno zip verso macOS, il permesso di esecuzione (`+x`) va perso** — eseguendoli direttamente si ottiene
`Permission denied`. **Eseguire questo comando una volta prima del primo utilizzo:**

```bash
cd "AmazingHand-main/Demo/Mac_Deploy_Scripts"
chmod +x *.sh
```

Poi ciascuno script può essere eseguito con `./script`.

> Suggerimento: per spostare la cartella `AmazingHand-main` su macOS conservando i permessi, creare un archivio con **tar**:
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`, oppure eseguire semplicemente `chmod +x *.sh` una volta dopo l'estrazione.

---

## 3. Configurazione dell'ambiente (script 1)

Dalla cartella degli script, eseguire (dopo il `chmod +x` del passaggio 2):

```bash
cd "AmazingHand-main/Demo/Mac_Deploy_Scripts"
./1-Install_Env.sh
```

Automaticamente:

1. **Verifica gli Xcode Command Line Tools** (necessari per compilare Rust). Se mancano, eseguire `xcode-select --install`
2. **Installa Rust** (rustup + toolchain stable)
3. **Configura il mirror tuna di cargo** (`~/.cargo/config.toml`) per accelerare il download dei crate
4. **Installa uv** (gestore di pacchetti Python)
5. **Installa dora-cli 0.5.0** (`cargo install`, la prima compilazione richiede ~10–20 min, portare pazienza). Le versioni vecchie di dora vengono rilevate automaticamente e sostituite forzatamente.
6. **Installa il pacchetto pip dora-rs** (opzionale)

> **Importante**: **chiudere e riaprire il terminale** dopo lo script affinché le variabili d'ambiente abbiano effetto.
> Se una versione risulta vuota, aggiungere a `~/.zshrc`:
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### Installazione manuale (se lo script non è utilizzabile)

- **Xcode Command Line Tools**: `xcode-select --install`
- **Rust**: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### Mirror tuna di cargo (~/.cargo/config.toml)

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

## 4. Cablaggio

- Collegare la scheda di controllo dei servo al PC tramite USB, **alimentarla con un alimentatore esterno da 5V 4A**
- I nomi dei dispositivi seriali USB di macOS sono **`/dev/tty.usbmodem*`** oppure **`/dev/cu.usbmodem*`** (NON `/dev/ttyACM*` di Linux)
- Trovare la porta:
  ```bash
  ls /dev/tty.usbmodem* /dev/cu.usbmodem*
  ```

---

## 5. Configurazione della porta seriale (script 2)

**Eseguire `./2-Setup_Serial.sh`**:

1. "Collegare la scheda di controllo" → premere Invio per eseguire la scansione
2. Vengono elencate le porte seriali rilevate (`/dev/tty.usbmodem*` / `/dev/cu.usbmodem*` / `*.usbserial*`)
3. Porta singola: premere Invio per confermare; più porte: digitare l'indice
4. Scrive `--serialport` nei 3 file yml del dataflow e la porta predefinita in `AHControl/src/main.rs`
5. Le porte seriali USB di macOS sono di solito leggibili dall'utente. Se l'accesso viene negato, eseguire manualmente:
   ```bash
   sudo chmod 666 /dev/cu.usbmodem*
   ```
   Oppure consentire il terminale in **Impostazioni di Sistema → Privacy e sicurezza → Monitoraggio input**.

> Se si è all'interno di una VM, collegare il dispositivo USB alla VM.

---

## 6. Deploy del codice (script 3)

**Eseguire `./3-Deploy_Demo.sh`** — automaticamente:

1. Avvia il demone dora (`dora up`)
2. Crea un venv Python 3.12 (`uv venv --python 3.12`)
3. Attiva il venv
4. Compila il nodo Rust AHControl (`cargo build --release`, la prima volta ~10 min)
5. Sincronizza le dipendenze di AHSimulation e HandTracking (`uv sync`)
6. Installa forzatamente mediapipe==0.10.14 (problema noto, fallback)

> Eseguire il deploy una sola volta. Rieseguendolo viene chiesto se ricostruire il venv.

---

## 7. Eseguire la Demo (script 4)

**Eseguire `./4-Run_Demo.sh`** — menu interattivo:

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

> **Al primo avvio, macOS chiede il permesso per la fotocamera**: Impostazioni di Sistema → Privacy e sicurezza → Fotocamera → consentire il terminale.

---

## 8. Pulizia del progetto (script 0)

**Eseguire `./0-Cleanup_Project.sh`**, digitare `Y` per confermare:

1. Arresta il demone dora
2. Elimina i 3 ambienti virtuali (`.venv`)
3. Elimina l'output di compilazione Rust (`Demo/target`)
4. Elimina `__pycache__`, i backup `.bak`, i log e `Demo/out` (log di dora)
5. **Ripristina la porta predefinita** (`--serialport /dev/ttyACM0`), rimuovendo i residui di porta di questa macchina

> Dopo la pulizia è possibile copiare l'intera cartella `AmazingHand-main` su un'altra macchina — pulita e portabile.
> Sulla nuova macchina eseguire semplicemente 1 → 2 → 3 → 4 nell'ordine.

---

## 9. Risoluzione dei problemi e note

### 9.1 `Permission denied` (lo script non ha il permesso di esecuzione)

- Sintomo: `bash: ./1-Install_Env.sh: Permission denied`
- Causa: lo script ha perso il bit di esecuzione quando è stato copiato da Windows / da uno zip
- Soluzione:
  ```bash
  chmod +x *.sh
  ```

### 9.2 cargo bloccato su `Updating 'tuna' index`

- Causa: mirror configurato in **modalità git-repo** (`.../git/crates.io-index.git`), la prima esecuzione scarica un indice da 1 GB+
- Soluzione: impostare `~/.cargo/config.toml` sullo **sparse index** (vedere 3.2), oppure rieseguire `1-Install_Env.sh`

### 9.3 sottomodulo solutions di mediapipe mancante / installazione non funzionante

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Eseguire all'interno del venv attivato (nella cartella `Demo`)
- `3-Deploy_Demo.sh` lo fa già come fallback

### 9.4 versione di dora non corrispondente (messaggio v0.8.0 vs v0.7.0)

- Sintomo: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Causa: la versione di dora-cli è diversa da quella di dora-node-api. **Devono essere entrambe 0.5.0**
  - Verifica: `dora --version` deve stampare `dora-cli 0.5.0` e `dora-message: 0.8.0`
  - `1-Install_Env.sh` rileva automaticamente le versioni vecchie e installa forzatamente la 0.5.0

**Se sul sistema è rimasta una versione vecchia di dora (ad es. 0.4.1), rimuoverla prima:**

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

> Se `dora --version` mostra ancora una versione vecchia, un'altra copia obsoleta è nascosta da qualche parte nel PATH — usare `which dora` per trovarla e rimuoverla.

### 9.5 Permesso negato sulla porta seriale

```bash
sudo chmod 666 /dev/cu.usbmodem*
```

- Oppure consentire il terminale in **Impostazioni di Sistema → Privacy e sicurezza → Monitoraggio input**
- Se un dispositivo `tty.*` non è leggibile, usare al suo posto il dispositivo `cu.*` corrispondente (il dispositivo cu è la porta di lettura/scrittura preferita per il controllo diretto)

### 9.6 Permesso della fotocamera

- **Al primo avvio: fare clic su "Consenti"** nella finestra che compare, oppure consentire il terminale in **Impostazioni di Sistema → Privacy e sicurezza → Fotocamera**
- Assicurarsi che nessun'altra app (FaceTime, app di videoconferenza) stia usando la fotocamera

### 9.7 Il numero di porta cambia ogni volta

- Dopo aver ricollegato l'USB il nome del dispositivo può cambiare — rieseguire `2-Setup_Serial.sh`

### 9.8 OpenCV mancante

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(nella cartella `HandTracking`, venv attivato)

### 9.9 Apple Silicon: prima compilazione lenta / avviso di Gatekeeper

- La prima `cargo build` su Apple Silicon compila molte dipendenze di dora — è normale che sia lenta, portare pazienza
- Se compare un avviso "sviluppatore non verificato": Impostazioni di Sistema → Privacy e sicurezza → Apri comunque

---

## 10. Struttura del codice

### Cartella Demo

| Percorso | Descrizione |
|---|---|
| `AHControl` | Nodo Rust che controlla i servo. Entry: `src/main.rs` |
| `AHSimulation` | Nodo Python: simulazione MuJoCo + cinematica inversa (mink) |
| `HandTracking` | Nodo Python: hand tracking con MediaPipe |
| `dataflow_*.yml` | Definizioni dei dataflow di dora (grafo dei nodi) |
| `Mac_Deploy_Scripts` | Questo pacchetto di script |

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

- La riga `args:` dei 3 file `dataflow_tracking_real_*.yml`: `--serialport /dev/cu.usbmodem...`
- `AHControl/src/main.rs` `default_value` (default della serialport)
- `AHControl/config/*.toml`: modello dei servo, ID, offset (di solito non serve modificarli)
