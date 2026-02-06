# 🖥️ Automatizador de Provisionamento Corporativo

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Ferramenta CLI para automação pós-formatação de máquinas Windows em ambiente corporativo.**

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Requisitos do Sistema](#-requisitos-do-sistema)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação](#-instalação)
- [Guia de Uso Completo](#-guia-de-uso-completo)
- [Configuração](#-configuração)
- [Compilação (.exe)](#-compilação-exe)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

Esta ferramenta automatiza o processo de provisionamento de máquinas Windows após formatação, dividido em **duas etapas principais**:

| Etapa | Quando Executar | O que Faz |
|-------|-----------------|-----------|
| **1** | Antes do reboot | Renomeia máquina e ingressa no domínio AD |
| **2** | Após login no AD | Instala softwares, copia pastas, cria atalhos |

---

## 💻 Requisitos do Sistema

### Obrigatórios

| Requisito | Versão Mínima | Notas |
|-----------|---------------|-------|
| **Windows** | 10/11 | Testado em Windows 10 21H2+ e Windows 11 |
| **Python** | 3.8+ | Recomendado 3.10+ (somente para desenvolvimento) |
| **PowerShell** | 5.1+ | Já incluso no Windows |
| **Winget** | 1.0+ | Geralmente pré-instalado no Windows 10/11 |
| **Privilégios** | Administrador | Obrigatório para todas as operações |

### Para Desenvolvimento

```bash
# Apenas para compilar em .exe
pip install pyinstaller>=6.0.0
```

> **Nota**: O projeto usa **apenas bibliotecas padrão do Python**, sem dependências externas para execução!

---

## 📁 Estrutura do Projeto

```
install-formatacao/
├── main.py                 # Ponto de entrada principal
├── config.py               # Configurações globais (editar conforme ambiente)
├── requirements.txt        # Dependências e comandos de compilação
├── README.md               # Esta documentação
├── LICENSE                 # Licença MIT
│
├── modules/
│   ├── __init__.py
│   ├── identity.py         # Etapa 1: Renomear e ingressar no domínio
│   └── install.py          # Etapa 2: Instalação de softwares
│
└── utils/
    ├── __init__.py
    ├── common.py            # Funções utilitárias (clear, pause, etc.)
    ├── logger.py            # Sistema de logging em arquivo
    └── powershell.py        # Wrapper para execução de comandos PS
```

---

## 🚀 Instalação

### Opção 1: Executar direto com Python

```bash
# Clone ou baixe o projeto
git clone <url-do-repositorio>
cd install-formatacao

# Execute como administrador
python main.py
```

### Opção 2: Compilar para .exe (Recomendado)

```bash
# Instale o PyInstaller
pip install pyinstaller

# Compile
pyinstaller --onefile --uac-admin --name "Provisionador" main.py

# O executável estará em: dist/Provisionador.exe
```

---

## 📖 Guia de Uso Completo

### Passo a Passo do Provisionamento

#### 🔷 Fase 1: Após Instalação Limpa do Windows

1. **Finalize a instalação do Windows** (OOBE, criação de usuário local temporário)

2. **Execute a ferramenta como Administrador**
   - Clique direito → "Executar como administrador"
   - Ou via PowerShell Admin: `python main.py`

3. **Selecione a Opção [1] - Configurar Nome e Domínio**

4. **Forneça as informações solicitadas:**
   ```
   Novo nome da máquina: DESKTOP-VENDAS01
   Domínio [ultradisplays.local]: <Enter para usar padrão>
   Usuário Admin do Domínio: ULTRADISPLAYS\admin
   ```

5. **Confirme a operação** (S/N)

6. **Insira as credenciais** na janela do Windows que aparecer

7. **Reinicie a máquina** quando solicitado

---

#### 🔷 Fase 2: Após Login com Usuário do Domínio

1. **Faça login com um usuário do domínio AD**

2. **Execute a ferramenta novamente como Administrador**

3. **Selecione a Opção [2] - Instalar Softwares e Configs**

4. **Aguarde as instalações automáticas:**
   - ✅ Google Chrome (via Winget)
   - ✅ WinRAR (via Winget)
   - ✅ Microsoft Teams (via Winget)
   - ✅ AnyDesk (via Winget)

5. **Aguarde a cópia das pastas da rede:**
   - `\\192.168.0.8\nextone\client` → `C:\NextUltraDisplays`
   - `\\192.168.0.8\nextone\MEGAPAPER\Client_Mega` → `C:\NextUltraArt`

6. **Selecione a versão do Office:**
   ```
   [1] Office 2013 (Standard SP.01 x64)
   [2] Office 365 (Pacote 2016)
   [0] Pular instalação do Office
   ```

7. **Atalho WebApp é criado automaticamente** na Área de Trabalho Pública

8. **AnyDesk abre automaticamente** - Anote o ID para suporte remoto

9. **Pronto!** A máquina está provisionada 🎉

---

### Fluxograma do Processo

```
┌─────────────────────────────────────────────────────────────┐
│                   FORMATAÇÃO WINDOWS                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              ETAPA 1: PRÉ-DOMÍNIO                           │
│  ─────────────────────────────────────────────────────────  │
│  [1] Renomear máquina                                       │
│  [2] Ingressar no domínio AD                                │
│  [3] Reiniciar                                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 🔄 REBOOT + LOGIN AD                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              ETAPA 2: PÓS-DOMÍNIO                           │
│  ─────────────────────────────────────────────────────────  │
│  [1] Instalar Chrome, WinRAR, Teams, AnyDesk (Winget)       │
│  [2] Copiar pastas da rede (NextUltra)                      │
│  [3] Instalar Office (2013 ou 365)                          │
│  [4] Criar atalho WebApp (Sistema)                          │
│  [5] Abrir AnyDesk (coletar ID)                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               ✅ MÁQUINA PROVISIONADA                       │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuração

Edite o arquivo `config.py` para adaptar às suas necessidades:

### Principais Configurações

```python
CONFIG = {
    # Domínio padrão
    "default_domain": "ultradisplays.local",
    
    # Pastas a copiar (origem, destino)
    "unc_folders_to_copy": [
        (r"\\192.168.0.8\nextone\client", r"C:\NextUltraDisplays"),
        (r"\\192.168.0.8\nextone\MEGAPAPER\Client_Mega", r"C:\NextUltraArt"),
    ],
    
    # Softwares via Winget
    "winget_packages": [
        "Google.Chrome",
        "RARLab.WinRAR",
        "Microsoft.Teams",
        "AnyDesk.AnyDesk",
    ],
    
    # Office 2013
    "office_installer": {
        "path": r"\\servidor\caminho\setup.exe",
        "args": "/configure configuration.xml"
    },
    
    # WebApp
    "webapp_url": "http://192.168.0.15",
    "webapp_name": "NextBP Sistema",
}
```

---

## 📦 Compilação (.exe)

### Comando Básico

```bash
pyinstaller --onefile --uac-admin --name "Provisionador" main.py
```

### Com Ícone Personalizado

```bash
pyinstaller --onefile --uac-admin --name "Provisionador" --icon=icon.ico main.py
```

### Opções Úteis

| Opção | Descrição |
|-------|-----------|
| `--onefile` | Gera um único .exe portátil |
| `--uac-admin` | Solicita elevação automaticamente |
| `--name` | Define o nome do executável |
| `--icon` | Ícone personalizado (.ico) |

O executável será gerado em: `dist/Provisionador.exe`

---

## 🔧 Troubleshooting

### "Esta ferramenta PRECISA ser executada como ADMINISTRADOR"

**Solução**: Clique direito no .exe → "Executar como administrador"

### Winget não encontrado

**Soluções**:
1. Instale o [App Installer da Microsoft Store](https://www.microsoft.com/store/productId/9NBLGGH4NNS1)
2. Atualize o Windows para versão mais recente

### Falha ao ingressar no domínio

**Verificar**:
- Conectividade de rede com o controlador de domínio
- Credenciais de administrador do domínio corretas
- DNS configurado para resolver o domínio

### Cópia de pastas falha

**Verificar**:
- Caminho UNC está acessível: `\\servidor\compartilhamento`
- Permissões de leitura no compartilhamento
- Credenciais de rede (pode precisar mapear antes)

### Office não instala

**Verificar**:
- Caminho do instalador existe e está acessível
- Arquivo de configuração (`configuration.xml`) está na mesma pasta
- Versão do Office compatível com o Windows

---

## 📝 Logs

Os logs são salvos em: `C:\ProvisioningLogs\`

Padrão de nome: `provisioning_<HOSTNAME>_<TIMESTAMP>.log`

Exemplo: `provisioning_DESKTOP-01_20260206_152230.log`

---

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

---

**Desenvolvido para automação de TI corporativa** 🏢