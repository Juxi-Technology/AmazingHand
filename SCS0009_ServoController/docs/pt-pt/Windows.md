[English](../en/Windows.md) | [Deutsch](../de/Windows.md) | [Español](../es/Windows.md) | [Français](../fr/Windows.md) | [Italiano](../it/Windows.md) | [日本語](../ja/Windows.md) | [한국어](../ko/Windows.md) | [Português (BR)](../pt-br/Windows.md) | Português (PT) | [简体中文](../zh-hans/Windows.md) | [繁體中文](../zh-hant/Windows.md)

# Ferramenta de Depuração do Servo SCS0009 — Guia Windows

Para Windows 10 / 11. Abrange desde a instalação até à depuração completa do servo.

> ⚠️ **Compatibilidade: esta ferramenta suporta atualmente apenas servos Feetech SCS0009 (série SCS, feedback por potenciómetro, resolução de 10 bits 0-1023)**. A tabela de registos e o formato xdat foram concebidos para o Feetech SCS0009; outros fabricantes/modelos não são garantidos.

---

## 1. Requisitos

| Dependência | Versão | Notas |
|-----------|---------|-------|
| Python | >= 3.8 | Recomenda-se 3.10+, descarregue em [python.org](https://www.python.org/downloads/) |
| PySide6 | >= 6.0 | Framework gráfico |
| pyserial | >= 3.5 | Comunicação série |
| SO | Win10 / Win11 | Qualquer edição |

## 2. Instalar o Python

1. Visite <https://www.python.org/downloads/>
2. Descarregue o instalador do Python 3.10+
3. **Assinale "Add Python to PATH"** durante a instalação (caso contrário, o python não será encontrado no terminal)

Verifique:

```bash
python --version
```

## 3. Instalar as dependências

Instale num ambiente virtual para evitar poluir o Python do sistema:

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **Crie o ambiente virtual apenas UMA VEZ**. Executá-lo novamente irá redefinir/substituir o ambiente (apagando as dependências instaladas). Depois disso, basta executar `activate` de cada vez.

> A linha de comandos mostrará `(.venv)` após a ativação.

## 4. Verificar o ambiente

```bash
python setup.py
```

`[OK] 环境检查通过，可以运行项目` significa que o ambiente está pronto.

## 5. Ligar o hardware

1. Ligue o adaptador USB-série (CH340 / CP2102)
2. Ligue o controlador dos servos (placa de controlo do braço robótico)
3. Alimente os servos (CC 5V 5A standard, CC 12V 5A Pro)

Verifique a porta COM no Gestor de Dispositivos (`Win+X` → Gestor de Dispositivos):

```
Ports (COM & LPT)
  └─ USB-SERIAL CH340 (COM3)     ← your servo port
```

> **Anote o número da COM** para a poder selecionar ao iniciar.

## 6. Iniciar a GUI

```bash
python -m src.gui.factory_calibration_tool
```

Ou especifique a porta:

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

Listar as portas disponíveis:

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. Fluxo de trabalho da interface

> Disposição de painel único. Uma barra de deslocamento aparece automaticamente quando a janela é demasiado baixa; estica para se ajustar quando maximizada.

### 7.1 Ligação série

- Selecione a porta e a taxa de transmissão (predefinição 1M) e clique em **Conetar**
- O estado mostra `🟢 Connected`

### 7.2 Procurar servos

- Clique em **Procurar servos** para detetar os servos online (ID 1-254)
- Os resultados aparecem na lista de servos em tempo real (com o modelo)
- Clique numa linha da lista → preenche automaticamente a lista pendente dos servos

### 7.3 Leitura/escrita de parâmetros

- **Ler parâmetros**: lê todos os 44 registos (EEPROM + SRAM); o registo mostra os resultados ao vivo
- **Tabela de parâmetros**: 5 colunas (Endereço/Registo/Valor/Memória/Acesso), com código de cores por EEPROM/SRAM/DEFAULT
- **Seleção vinculada de linha**: clique numa linha → preenche automaticamente "Write Address", "Length" e "Value"
- **Escrever**: modifique o valor e clique em escrever; a ferramenta desbloqueia/escreve/bloqueia a EEPROM automaticamente
- **Janela de resultado da escrita**: a verde "✅ Written successfully" em caso de sucesso, a vermelho "❌ Write failed" (com o motivo) em caso de falha

### 7.4 Controlo de posição

- **Controlo deslizante**: arraste para ajustar a posição alvo (0-1023); a caixa de valor é atualizada ao vivo
- **Caixa de valor**: introduza a posição alvo diretamente; o controlo deslizante acompanha
- Após o movimento, o estado mostra "move complete, please turn off torque"

### 7.5 Taxa de transmissão / Reposição de fábrica

- **Alterar a taxa de transmissão**: selecione 38400-1000000 bps, reversão automática em caso de falha
- **Reposição de fábrica**: restaura as predefinições de fábrica (ID=1, baud=1M); é necessário voltar a procurar

### 7.6 Parâmetros xdat (apenas EEPROM)

1. `💾 Save Current Servo`: guarda os parâmetros EEPROM do servo atual num ficheiro xdat (cópia de segurança)
2. `📂 Open xdat`: carrega um ficheiro de cópia de segurança
3. `📤 Restore to Servo`: grava a cópia de segurança de volta no servo

## 8. Resolução de problemas

| Problema | Solução |
|---------|----------|
| Sem porta série | Verifique o controlador no Gestor de Dispositivos; experimente outra porta USB; instale o controlador CH340 |
| Porta em utilização | Feche os monitores de porta série; reinicie a ferramenta |
| Texto em chinês em branco | O sistema tem a Microsoft YaHei; instale um tipo de letra CJK se estiver corrompido |
| Servo não encontrado | Verifique a alimentação/cablagem; confirme a taxa de 1M |
| Falha na escrita | Verifique a alimentação e a ligação do servo; confirme se o registo é gravável |
| PermissionError ao abrir a porta | Garanta que nenhum outro processo está a utilizar a porta COM |

## 9. Linha de comandos (opcional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port COM3
```
