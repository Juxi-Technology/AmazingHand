---
title: "Tutorial di utilizzo di Arduino Nano"
description: "Eseguire il «programma dimostrativo 02» di AmazingHand con Arduino Nano (328P) e la scheda driver servo: cablaggio, installazione delle librerie, compilazione, caricamento e risultato."
version: scs0009
---

# Tutorial di utilizzo di Arduino Nano

> Questa pagina è la demo Arduino Nano per la **versione con servo bus SCS0009**. Per il cablaggio TTL e l'impostazione dell'ID vedi [Messa a punto e calibrazione dei servo SCS0009](../06-servo-tuning/scs0009.md), per altri esempi vedi [Esempi Arduino / Python](examples.md).


## Modalità di cablaggio (scheda driver servo + scheda Nano)

**Controlla bene la posizione dei pin della scheda Nano (cioè della scheda di sviluppo 328P)!**

![Posizione dei pin della scheda Nano (1)](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Posizione dei pin della scheda Nano (2)](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Posizione dei pin della scheda Nano (3)](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Posizione dei pin della scheda Nano (4)](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

Di seguito viene descritto il processo di messa a punto con il microcontrollore. Il microcontrollore esegue continuamente in loop il programma dimostrativo; per fermarlo basta scollegare il cavo dati.

## Esecuzione del «programma dimostrativo 02»

1. Installa autonomamente Arduino IDE.

2. In base alla **mano destra o sinistra**, apri il file `.ino` corrispondente.

   ![File ino del programma dimostrativo 02 per mano sinistra/destra](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. Prima di compilare e caricare il programma Arduino sulla scheda Nano, installa nel «Gestore librerie» la **libreria FTServo** e la **libreria SCServo**.

   ![Installazione delle librerie FTServo e SCServo nel Gestore librerie](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Tipo di scheda Nano: seleziona «**Arduino Nano**».

   ![Selezione del tipo di scheda Arduino Nano](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. Compila e carica.

> **Nota:** in questo momento il PC è collegato solo alla scheda Nano, che non è ancora collegata alla scheda driver servo (cioè non è collegata alla mano robotica).

Dopo il caricamento riuscito, collega la scheda Nano alla scheda driver servo tramite tre jumper, collega i servo alla scheda driver servo, come descritto in [Modalità di cablaggio per la messa a punto con la scheda MEGA328P Nano](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc).

La mano robotica eseguirà continuamente in loop il «programma dimostrativo 02»; il risultato è il seguente:

![Risultato dell'esecuzione del programma dimostrativo 02](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
