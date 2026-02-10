# 🖥️ Provisionador Corporativo

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Ferramenta CLI para automação pós-formatação de máquinas Windows em ambiente corporativo.**

Interface com visual premium: ASCII art, cores 256, barras de progresso, spinners animados e cards de resumo — tudo nativo no terminal, sem dependências externas.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Requisitos](#-requisitos)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação](#-instalação)
- [Guia de Uso](#-guia-de-uso)
- [Configuração](#-configuração)
- [Compilação (.exe)](#-compilação-exe)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

Automatiza o provisionamento de máquinas Windows após formatação em **duas etapas**:

| Etapa | Quando Executar | O que Faz |
|-------|-----------------|-----------|
| **1** | Antes do reboot | Renomeia máquina e ingressa no domínio AD |
| **2** | Após login no AD | Instala softwares, copia pastas, cria atalhos |

### Recursos Visuais

| Recurso | Descrição |
|---------|-----------|
| ASCII Art Banner | Logo com gradiente cyan→azul |
| Menu Categorizado | Seções com ícones (⚙ Configuração, 📦 Instalação, 🔧 Utilidades) |
| Spinner Braille | Animação `⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏` para operações longas |
| Barra de Progresso | `████████░░░░ 60% [3/5] 12s` inline |
| Cards de Resumo | Caixas Unicode com status por etapa |
| Diagnóstico | Health bar visual `████████████████████ 100%` |
| Transições | Animação suave entre telas |

---

## 💻 Requisitos

| Requisito | Versão | Notas |
|-----------|--------|-------|
| **Windows** | 10/11 | Testado em 10 21H2+ e 11 |
| **Python** | 3.8+ | Apenas para desenvolvimento |
| **PowerShell** | 5.1+ | Já incluso no Windows |
| **Winget** | 1.0+ | Pré-instalado no Windows 10/11 |
| **Privilégios** | Admin | Obrigatório |

> **Zero dependências externas** para execução — usa apenas stdlib do Python.

---

## 📁 Estrutura do Projeto

```
install-formatacao/
├── main.py                 # Entry point, banner, menus
├── config.py               # Configurações do ambiente (editar)
│
├── modules/
│   ├── identity.py         # Etapa 1: Rename + ingresso AD
│   ├── install.py          # Etapa 2: Softwares e configs
│   └── diagnostics.py      # Verificação de pré-requisitos
│
└── utils/
    ├── colors.py            # Paleta ANSI 256, formatadores
    ├── common.py            # Helpers de UI (header, step, box)
    ├── logger.py            # Logging em arquivo + console
    ├── powershell.py        # Wrapper PowerShell
    └── progress.py          # Spinner, ProgressBar, transições
```

---

## Instalação

### Direto com Python

```bash
git clone <url-do-repositorio>
cd install-formatacao

# Executar como administrador
python main.py
```

### Compilar para .exe (recomendado)

```bash
pip install pyinstaller
pyinstaller --onefile --uac-admin --name "Provisionador" main.py

# Resultado: dist/Provisionador.exe
```

---

## 📖 Guia de Uso

### Fase 1: Após Instalação Limpa do Windows

1. Finalize o OOBE do Windows
2. Execute como Administrador
3. Opção **[1]** — Nome e Domínio
4. Informe: nome da máquina, domínio, usuário admin
5. Confirme e insira credenciais na janela do Windows
6. Reinicie quando solicitado

### Fase 2: Após Login com Usuário do Domínio

1. Login com usuário do AD
2. Execute novamente como Admin
3. Opção **[2]** — Instalação Completa
4. Aguarde:
   - ✅ Chrome, WinRAR, Teams, AnyDesk (Winget)
   - ✅ Cópia de pastas da rede
   - ✅ Office (2013 ou 365)
   - ✅ Atalho WebApp
   - ✅ AnyDesk (anotar ID)
5. Pronto! 🎉

### Fluxo

```
Formatação Windows
       │
       ▼
┌─ ETAPA 1: PRÉ-DOMÍNIO ─────────┐
│  Renomear + Ingressar no AD     │
│  Reiniciar                      │
└──────────────┬──────────────────┘
               ▼
        🔄 REBOOT + LOGIN AD
               ▼
┌─ ETAPA 2: PÓS-DOMÍNIO ─────────┐
│  Winget (Chrome, WinRAR, etc.)  │
│  Copiar pastas da rede          │
│  Instalar Office                │
│  Atalho WebApp + AnyDesk        │
└──────────────┬──────────────────┘
               ▼
        ✅ MÁQUINA PRONTA
```

---

## ⚙️ Configuração

Edite `config.py`:

```python
CONFIG = {
    "default_domain": "ultradisplays.local",

    # Pastas UNC: (origem, destino)
    "unc_folders_to_copy": [
        (r"\\192.168.0.8\nextone\client", r"C:\NextUltraDisplays"),
    ],

    # Pacotes Winget
    "winget_packages": [
        "Google.Chrome",
        "RARLab.WinRAR",
        "Microsoft.Teams",
        "AnyDesk.AnyDesk",
    ],

    # Office
    "office_installer": {
        "path": r"\\servidor\caminho\setup.exe",
        "args": ""
    },

    # WebApp
    "webapp_url": "http://192.168.0.15",
    "webapp_name": "NextBP Sistema",
}
```

---

## 📦 Compilação (.exe)

```bash
# Básico
pyinstaller --onefile --uac-admin --name "Provisionador" main.py

# Com ícone
pyinstaller --onefile --uac-admin --name "Provisionador" --icon=icon.ico main.py
```

| Opção | Descrição |
|-------|-----------|
| `--onefile` | .exe portátil único |
| `--uac-admin` | Solicita elevação automática |
| `--icon` | Ícone personalizado (.ico) |

---

## 🔧 Troubleshooting

| Problema | Solução |
|----------|---------|
| "PRECISA ser executada como ADMINISTRADOR" | Botão direito → "Executar como administrador" |
| Winget não encontrado | Instale [App Installer](https://www.microsoft.com/store/productId/9NBLGGH4NNS1) da Microsoft Store |
| Falha ao ingressar no domínio | Verificar DNS, conectividade com DC, credenciais |
| Cópia de pastas falha | Verificar acesso ao UNC, permissões de rede |
| Office não instala | Verificar caminho do instalador e acessibilidade |

---

## 📝 Logs

Salvos em `C:\ProvisioningLogs\` com formato:

```
provisioning_<HOSTNAME>_<TIMESTAMP>.log
```

---

## 🧑‍💻 Contribuição

O código segue estas convenções:

- **Comentários pontuais** — apenas quando o "porquê" não é óbvio pelo código
- **Docstrings curtas** — uma linha quando possível, sem repetir o que a assinatura já diz
- **Sem headers decorativos** — nada de `# ═══════` ou blocos visuais nos fontes
- **Imports limpos** — só o que é usado, agrupados por stdlib → internos
- **Nomes em português** — consistente com o contexto corporativo da ferramenta

---

## 📄 Licença

[MIT](LICENSE)

---

**Desenvolvido para automação de TI corporativa** 🏢