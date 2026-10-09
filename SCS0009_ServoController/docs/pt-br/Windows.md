[English](../en/Windows.md) | [Deutsch](../de/Windows.md) | [Español](../es/Windows.md) | [Français](../fr/Windows.md) | [Italiano](../it/Windows.md) | [日本語](../ja/Windows.md) | [한국어](../ko/Windows.md) | Português (BR) | [Português (PT)](../pt-pt/Windows.md) | [简体中文](../zh-hans/Windows.md) | [繁體中文](../zh-hant/Windows.md)

# Ferramenta de depuração do servo SCS0009 — Guia para Windows

Para Windows 10 / 11. Abrange desde a instalação até a depuração completa dos servos.

> ⚠️ **Compatibilidade: atualmente esta ferramenta suporta apenas servos Feetech SCS0009 (série SCS, feedback de posição por potenciômetro, resolução de 10 bits 0-1023)**. A tabela de registradores e o formato xdat são projetados para o Feetech SCS0009; outras marcas/modelos não são garantidos.

---

## 1. Requisitos

| Dependência | Versão | Observações |
|-----------|---------|-------|
| Python | >= 3.8 | Recomenda-se 3.10+, baixe em [python.org](https://www.python.org/downloads/) |
| PySide6 | >= 6.0 | Framework da GUI |
| pyserial | >= 3.5 | Comunicação serial |
| SO | Win10 / Win11 | Qualquer edição |

## 2. Instalar o Python

1. Acesse <https://www.python.org/downloads/>
2. Baixe o instalador do Python 3.10+
3. **Marque "Add Python to PATH"** durante a instalação (caso contrário, o python não será encontrado no terminal)

Verifique:

```bash
python --version
```

## 3. Instalar as dependências

Instale em um ambiente virtual para não poluir o Python do sistema:

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **Crie o ambiente virtual apenas UMA VEZ**. Executá-lo novamente vai redefinir/sobrescrever o ambiente (apagando as dependências instaladas). Depois disso, basta ativá-lo (`activate`) a cada vez.

> O prompt exibirá `(.venv)` após a ativação.

## 4. Verificar o ambiente

```bash
python setup.py
```

`[OK] 环境检查通过，可以运行项目` significa que o ambiente está pronto.

## 5. Conectar o hardware

1. Conecte o adaptador USB-serial (CH340 / CP2102)
2. Conecte o controlador de servos (placa de controle do braço robótico)
3. Alimente os servos (padrão DC 5V 5A, Pro DC 12V 5A)

Verifique a porta COM no Gerenciador de Dispositivos (`Win+X` → Gerenciador de Dispositivos):

```
Ports (COM & LPT)
  └─ USB-SERIAL CH340 (COM3)     ← your servo port
```

> **Anote o número da COM** para selecioná-la ao iniciar.

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

> Layout de painel único. Uma barra de rolagem aparece automaticamente quando a janela fica muito baixa; ela se estende para se ajustar ao maximizar.

### 7.1 Conexão serial

- Selecione a porta e a taxa de transmissão (padrão 1M) e clique em **Conectar**
- O status exibe `🟢 Connected`

### 7.2 Escanear servos

- Clique em **Escanear servos** para detectar os servos online (ID 1-254)
- Os resultados aparecem na lista de servos em tempo real (com o modelo)
- Clique em uma linha da lista → preenche automaticamente o menu suspenso de servos

### 7.3 Leitura/escrita de parâmetros

- **Ler parâmetros**: lê todos os 44 registradores (EEPROM + SRAM); o log mostra os resultados ao vivo
- **Tabela de parâmetros**: 5 colunas (Endereço/Registrador/Valor/Memória/Acesso), com cores por EEPROM/SRAM/DEFAULT
- **Vínculo de seleção de linha**: clique em uma linha → preenche automaticamente "Endereço de escrita", "Tamanho" e "Valor"
- **Escrever**: modifique o valor e clique em escrever; a ferramenta desbloqueia/escreve/bloqueia a EEPROM automaticamente
- **Popup de resultado da escrita**: verde "✅ Written successfully" em caso de sucesso, vermelho "❌ Write failed" (com o motivo) em caso de falha

### 7.4 Controle de posição

- **Controle deslizante**: arraste para ajustar a posição alvo (0-1023); a caixa de valor é atualizada ao vivo
- **Caixa de valor**: digite a posição alvo diretamente; o controle deslizante acompanha
- Após o movimento, o status exibe "move complete, please turn off torque"

### 7.5 Taxa de transmissão / Restauração de fábrica

- **Alterar taxa de transmissão**: selecione de 38400 a 1000000 bps, reversão automática em caso de falha
- **Restauração de fábrica**: restaura os padrões de fábrica (ID=1, baud=1M); é necessário escanear novamente

### 7.6 Parâmetros xdat (somente EEPROM)

1. `💾 Save Current Servo`: salva os parâmetros EEPROM do servo atual em um arquivo xdat (backup)
2. `📂 Open xdat`: carrega um arquivo de backup
3. `📤 Restore to Servo`: grava o backup de volta no servo

## 8. Solução de problemas

| Problema | Solução |
|---------|----------|
| Nenhuma porta serial | Verifique o driver no Gerenciador de Dispositivos; tente outra porta USB; instale o driver CH340 |
| Porta em uso | Feche os monitores seriais; reinicie a ferramenta |
| Texto em chinês em branco | O sistema tem a Microsoft YaHei; instale uma fonte CJK se estiver corrompido |
| Servo não encontrado | Verifique a alimentação/cabeamento; confirme a taxa de 1M |
| Falha na escrita | Verifique a alimentação e a conexão do servo; confirme se o registrador é gravável |
| PermissionError ao abrir a porta | Garanta que nenhum outro processo esteja usando a porta COM |

## 9. Linha de comando (opcional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port COM3
```
