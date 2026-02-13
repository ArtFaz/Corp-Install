# 02 — Configuração

Referência completa do arquivo `config.py` — como personalizar softwares, pastas de rede, instaladores e atalhos.

---

## Visão Geral

Toda a personalização da ferramenta é feita em **um único arquivo**: `config.py`. Você não precisa alterar nenhum outro arquivo para adaptar a ferramenta ao seu ambiente.

O arquivo utiliza `dataclasses` do Python para definir os parâmetros com tipos fortes e valores padrão. A instância global `CONFIG` é importada por todos os módulos.

```
config.py  ──→  modules/identity.py   (domínio padrão)
           ──→  modules/install.py    (pacotes, pastas, Office, atalhos)
           ──→  modules/diagnostics.py (caminhos UNC para verificação)
```

---

## Estrutura Completa do `config.py`

```python
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class InstallerConfig:
    path: str          # Caminho do executável do instalador
    args: str = ""     # Argumentos de linha de comando (opcional)

@dataclass
class AppConfig:
    # ── Domínio ──────────────────────────────────────
    default_domain: str = "ultradisplays.local"

    # ── Caminho raiz dos instaladores na rede ────────
    unc_installers: str = r"\\192.168.0.11\t.i\@Instaladores..."

    # ── Pastas a copiar da rede ──────────────────────
    unc_folders_to_copy: List[Tuple[str, str]] = field(default_factory=lambda: [
        (r"\\192.168.0.8\nextone\client", r"C:\NextUltraDisplays"),
        (r"\\192.168.0.8\nextone\MEGAPAPER\Client_Mega", r"C:\NextUltraArt"),
    ])

    # ── Pacotes Chocolatey ───────────────────────────
    choco_packages: List[Tuple[str, str]] = field(default_factory=lambda: [
        ("googlechrome", ""),
        ("winrar", ""),
        ("anydesk", "--params \"'/INSTALL'\""),
        ("microsoft-teams-new-install", ""),
    ])

    # ── Instaladores do Office ───────────────────────
    office_installer: InstallerConfig = field(default_factory=lambda: InstallerConfig(
        path=r"\\servidor\...\setup.exe"
    ))
    office16_365_installer: InstallerConfig = field(default_factory=lambda: InstallerConfig(
        path=r"\\servidor\...\OfficeSetup.exe"
    ))

    # ── Atalho Web (Chrome App) ──────────────────────
    webapp_url: str = "http://192.168.0.15"
    webapp_name: str = "NextBP Sistema"
    webapp_shortcut_location: str = "Desktop"
    chrome_path: str = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Instância global usada por toda a aplicação
CONFIG = AppConfig()
```

---

## Como Alterar Cada Configuração

### 1. Domínio Padrão

O domínio sugerido automaticamente ao técnico durante a Etapa 1.

```python
default_domain: str = "ultradisplays.local"
```

**Para alterar:** Substitua pelo domínio da sua empresa:

```python
default_domain: str = "minhaempresa.local"
```

> 💡 O técnico sempre pode digitar outro domínio durante a execução. Este valor é apenas uma sugestão padrão.

---

### 2. Pastas de Rede (UNC)

Lista de pastas que serão copiadas dos servidores de rede para o computador local.

```python
unc_folders_to_copy: List[Tuple[str, str]] = field(default_factory=lambda: [
    # (ORIGEM na rede,                              DESTINO no PC)
    (r"\\192.168.0.8\nextone\client",                r"C:\NextUltraDisplays"),
    (r"\\192.168.0.8\nextone\MEGAPAPER\Client_Mega", r"C:\NextUltraArt"),
])
```

#### Como adicionar uma nova pasta

Adicione uma nova tupla `(origem, destino)` dentro da lista:

```python
unc_folders_to_copy: List[Tuple[str, str]] = field(default_factory=lambda: [
    (r"\\192.168.0.8\nextone\client",                r"C:\NextUltraDisplays"),
    (r"\\192.168.0.8\nextone\MEGAPAPER\Client_Mega", r"C:\NextUltraArt"),
    (r"\\192.168.0.11\share\templates",              r"C:\Templates"),        # ← NOVO
])
```

#### Como remover uma pasta

Delete a linha correspondente:

```python
unc_folders_to_copy: List[Tuple[str, str]] = field(default_factory=lambda: [
    (r"\\192.168.0.8\nextone\client", r"C:\NextUltraDisplays"),
    # Linha removida — não copia mais NextUltraArt
])
```

> ⚠️ **ATENÇÃO:** A cópia **substitui** completamente a pasta de destino. Se `C:\NextUltraDisplays` já existir, todo o conteúdo anterior será apagado e substituído pelo da rede.

---

### 3. Pacotes Chocolatey (Softwares)

Lista de softwares instalados automaticamente via Chocolatey.

```python
choco_packages: List[Tuple[str, str]] = field(default_factory=lambda: [
    # (id_do_pacote,                 argumentos_extras)
    ("googlechrome",                 ""),
    ("winrar",                       ""),
    ("anydesk",                      "--params \"'/INSTALL'\""),
    ("microsoft-teams-new-install",  ""),
])
```

Cada entrada é uma tupla com **dois valores**:

| Posição | O que é | Exemplo |
|---------|---------|---------|
| 1ª | ID do pacote no Chocolatey | `"googlechrome"` |
| 2ª | Argumentos extras (opcional) | `""` ou `"--params \"'/INSTALL'\""` |

#### Como descobrir o ID de um pacote

1. Acesse [community.chocolatey.org/packages](https://community.chocolatey.org/packages)
2. Pesquise o software desejado
3. Na página do pacote, copie o nome que aparece no comando `choco install <nome>`

**Exemplos populares:**

| Software | ID do Pacote |
|----------|-------------|
| Google Chrome | `googlechrome` |
| Mozilla Firefox | `firefox` |
| 7-Zip | `7zip` |
| WinRAR | `winrar` |
| VLC Player | `vlc` |
| Notepad++ | `notepadplusplus` |
| AnyDesk | `anydesk` |
| Teams (novo) | `microsoft-teams-new-install` |
| Visual Studio Code | `vscode` |
| Adobe Reader | `adobereader` |
| PuTTY | `putty` |

#### Como adicionar um novo software

Adicione uma nova tupla ao final da lista:

```python
choco_packages: List[Tuple[str, str]] = field(default_factory=lambda: [
    ("googlechrome", ""),
    ("winrar", ""),
    ("anydesk", "--params \"'/INSTALL'\""),
    ("microsoft-teams-new-install", ""),
    ("7zip", ""),              # ← NOVO
    ("vlc", ""),               # ← NOVO
    ("notepadplusplus", ""),   # ← NOVO
])
```

#### Como remover um software

Delete a linha correspondente:

```python
choco_packages: List[Tuple[str, str]] = field(default_factory=lambda: [
    ("googlechrome", ""),
    ("winrar", ""),
    ("anydesk", "--params \"'/INSTALL'\""),
    # Teams removido — já vem pré-instalado no Win11
])
```

#### Argumentos especiais

Alguns pacotes aceitam argumentos para personalizar a instalação:

```python
# AnyDesk: modo instalado (não portátil)
("anydesk", "--params \"'/INSTALL'\""),

# Firefox: idioma em português
("firefox", "--params \"l=pt-BR\""),
```

> 💡 Consulte a página do pacote no Chocolatey para ver os argumentos disponíveis.

---

### 4. Instaladores do Office

Dois instaladores de Office são suportados, acessíveis via caminho de rede:

```python
# Office 2013
office_installer: InstallerConfig = field(default_factory=lambda: InstallerConfig(
    path=r"\\192.168.0.11\t.i\...\setup.exe"
))

# Office 365
office16_365_installer: InstallerConfig = field(default_factory=lambda: InstallerConfig(
    path=r"\\192.168.0.11\t.i\...\OfficeSetup.exe"
))
```

#### Como alterar o caminho do Office

Substitua o `path` pelo novo caminho:

```python
office_installer: InstallerConfig = field(default_factory=lambda: InstallerConfig(
    path=r"\\novo-servidor\instaladores\Office2013\setup.exe"
))
```

#### Como adicionar argumentos ao instalador

```python
office16_365_installer: InstallerConfig = field(default_factory=lambda: InstallerConfig(
    path=r"\\servidor\Office365\OfficeSetup.exe",
    args="/configure install.xml"
))
```

> ⚠️ Certifique-se de que o caminho está acessível pela rede **antes** de executar a instalação. Use a opção **Diagnóstico** para verificar.

---

### 5. Atalho Web (Chrome App)

Cria um atalho no Desktop que abre uma URL em modo aplicativo do Chrome (sem barra de endereço):

```python
webapp_url: str = "http://192.168.0.15"       # URL do sistema web
webapp_name: str = "NextBP Sistema"            # Nome do atalho
webapp_shortcut_location: str = "Desktop"      # Onde criar: "Desktop" ou "StartMenu"
chrome_path: str = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
```

#### Como alterar o sistema web

```python
webapp_url: str = "http://192.168.0.20:8080/erp"
webapp_name: str = "ERP Corporativo"
```

#### Opções de localização do atalho

| Valor | Resultado |
|-------|-----------|
| `"Desktop"` | Cria no Desktop público (`C:\Users\Public\Desktop`) |
| `"StartMenu"` | Cria no Menu Iniciar |

---

## Regras Importantes

### Sempre use `r"..."` em caminhos Windows

O prefixo `r` antes da string faz com que barras invertidas sejam tratadas literalmente:

```python
# ✅ Correto
path=r"\\192.168.0.8\pasta\subpasta"

# ❌ Errado — \p e \s seriam interpretados como caracteres especiais
path="\\192.168.0.8\pasta\subpasta"
```

### Mantenha a estrutura de tuplas

Cada entrada nas listas deve seguir o formato exato:

```python
# ✅ Correto — tupla com 2 elementos
("googlechrome", ""),

# ❌ Errado — faltou a vírgula após o último item
("googlechrome", "")
("winrar", "")

# ❌ Errado — tupla com apenas 1 elemento
("googlechrome"),
```

### Teste antes de distribuir

Após qualquer alteração:

1. Execute o Diagnóstico (opção 4) para verificar caminhos de rede
2. Se estiver usando o `.exe`, **recompile** com `build.bat`
3. O executável não reflete mudanças no código-fonte automaticamente

---

## Referência Rápida

| Quero... | Alterar... | Onde no `config.py` |
|----------|-----------|---------------------|
| Mudar o domínio | `default_domain` | Linha 1 da `AppConfig` |
| Adicionar um software | `choco_packages` | Adicionar tupla à lista |
| Remover um software | `choco_packages` | Remover tupla da lista |
| Adicionar pasta de rede | `unc_folders_to_copy` | Adicionar tupla à lista |
| Mudar caminho do Office | `office_installer.path` | Alterar o `path` |
| Mudar URL do atalho | `webapp_url` | Alterar a string |
| Mudar nome do atalho | `webapp_name` | Alterar a string |
