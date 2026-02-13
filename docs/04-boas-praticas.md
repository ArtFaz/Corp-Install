# 04 — Boas Práticas e Troubleshooting

Recomendações para o uso do dia a dia, manutenção do código e resolução de problemas.

---

## Boas Práticas de Uso

### Antes de provisionar

| Prática | Motivo |
|---------|--------|
| Execute o **Diagnóstico** (opção 4) primeiro | Detecta caminhos inacessíveis antes de iniciar |
| Verifique a conexão de rede | Sem internet = sem Chocolatey |
| Confirme que está como **Administrador** | Todas as operações exigem privilégios elevados |
| Tenha as credenciais do AD em mãos | A Etapa 1 solicita usuário e senha do domínio |

### Durante a execução

| Prática | Motivo |
|---------|--------|
| **Não feche a janela** durante instalações | O processo precisa completar sem interrupção |
| Use **Ctrl+C** para cancelar de forma segura | É tratado internamente sem corromper o estado |
| **Anote o ID do AnyDesk** imediatamente | Aparece apenas na tela durante a execução |
| Se algo falhar, use **Instalações Avulsas** | Evita reexecutar tudo desde o início |

### Após o provisionamento

| Prática | Motivo |
|---------|--------|
| Verifique se todos os atalhos funcionam | Confirme que o Chrome App está correto |
| Faça login no AnyDesk pelo menos uma vez | Para ativar o acesso remoto permanente |
| Registre o ID do AnyDesk no inventário | Facilita o suporte remoto futuro |
| Consulte os logs se algo parecer errado | `C:\ProvisioningLogs\` tem o histórico completo |

---

## Boas Práticas de Configuração

### Ao editar o `config.py`

| Prática | Motivo |
|---------|--------|
| Use `r"..."` em todos os caminhos Windows | Evita erros com barras invertidas (`\n`, `\t`) |
| Teste caminhos UNC no Explorer antes | Garante que existe e é acessível |
| Mantenha uma vírgula após cada item da lista | Python exige vírgulas entre itens de lista |
| Coloque pacotes leves antes dos pesados | Se algo falhar cedo, menos tempo perdido |
| Deixe o Teams por último | No Windows 11 ele já vem pré-instalado |

### Ao adicionar novos softwares

1. **Pesquise o pacote** em [community.chocolatey.org/packages](https://community.chocolatey.org/packages)
2. **Verifique a popularidade** — pacotes populares têm manutenção mais ativa
3. **Teste o pacote manualmente** antes de adicionar ao config:
   ```powershell
   choco install nome-do-pacote -y --no-progress
   ```
4. Se o pacote precisar de argumentos, consulte a documentação na página do pacote

### Ao distribuir o executável

| Prática | Motivo |
|---------|--------|
| **Recompile** após qualquer alteração no `config.py` | O `.exe` congela o código no momento da compilação |
| Use o `build.bat` para compilar | Já inclui todos os hidden imports necessários |
| Teste o `.exe` em uma máquina limpa | Garante que funciona fora do ambiente de desenvolvimento |
| Mantenha versões do `.exe` com a data | Facilita identificar qual versão está sendo usada |

---

## Compilação do Executável

### Usando o `build.bat` (recomendado)

```powershell
# Na pasta do projeto, execute:
.\build.bat
```

O script automaticamente:
1. Instala as dependências do `requirements.txt`
2. Limpa builds anteriores
3. Compila o `.exe` com PyInstaller e todas as flags necessárias
4. Resultado: `dist\Provisionador.exe`

### Manualmente

```powershell
pip install pyinstaller rich
pyinstaller --onefile --uac-admin --name "Provisionador" --collect-all rich main.py
```

| Flag | Função |
|------|--------|
| `--onefile` | Gera um arquivo `.exe` único e portátil |
| `--uac-admin` | Solicita permissão de administrador automaticamente ao abrir |
| `--collect-all rich` | Inclui todos os módulos da biblioteca Rich no executável |

---

## Troubleshooting

### Problemas na Etapa 1 (Nome e Domínio)

| Problema | Causa Provável | Solução |
|----------|----------------|---------|
| Janela de credenciais não aparece | PowerShell bloqueado ou política de execução restritiva | Verifique se o PowerShell está funcional |
| "Falha ao configurar identidade" | DNS não resolve o domínio | Configure o DNS para apontar ao Domain Controller |
| Nome não muda após reboot | Raro — versões antigas do Windows | Execute `Rename-Computer` manualmente via PowerShell |
| "Credenciais não fornecidas" | A janela de senha foi fechada | Execute novamente e insira a senha |

### Problemas na Etapa 2 (Instalação)

| Problema | Causa Provável | Solução |
|----------|----------------|---------|
| "Não foi possível garantir o Chocolatey" | Sem acesso à internet | Conecte à internet e tente novamente |
| Software aparece como falha mas está instalado | Chocolatey retorna código de erro para pacote já existente | Verifique o software — provavelmente já foi instalado com sucesso |
| Cópia de pastas muito lenta | Rede congestionada ou caminho via VPN | Tente em horário de menor tráfego |
| "Caminho inacessível" para pastas UNC | Servidor offline, permissões insuficientes, ou caminho errado | Tente acessar o caminho pelo Explorer do Windows |
| Office não instala | Instalador não encontrado no caminho de rede | Execute o Diagnóstico para confirmar acessibilidade |
| Atalho NextBP não funciona | Chrome não instalado no caminho padrão | Verifique `chrome_path` no `config.py` |
| AnyDesk não encontrado | Instalação do AnyDesk falhou ou caminho diferente | Verifique no Painel de Controle se está instalado |

### Problemas Gerais

| Problema | Causa Provável | Solução |
|----------|----------------|---------|
| "PRECISA ser executada como ADMINISTRADOR" | Não executou com elevação | Botão direito → "Executar como administrador" |
| Tela fecha imediatamente | Erro fatal não tratado | Execute via `cmd` ou PowerShell para ver o erro |
| Caracteres estranhos na tela | Terminal sem suporte a Unicode | Use o Windows Terminal em vez do `cmd` clássico |
| `.exe` detectado como vírus | Falso positivo do antivírus com PyInstaller | Adicione exceção no antivírus para o `Provisionador.exe` |

---

## Estrutura do Projeto (Para Desenvolvedores)

Se precisar entender ou modificar o código-fonte:

```
install-formatacao/
├── main.py              → Ponto de entrada, banner, menus e loop principal
├── config.py            → ÚNICO arquivo de configuração (editar aqui)
│
├── modules/
│   ├── identity.py      → Lógica da Etapa 1 (rename + domínio via PowerShell)
│   ├── install.py       → Lógica da Etapa 2 (Chocolatey, pastas, Office, atalhos)
│   └── diagnostics.py   → Verificações de saúde (rede, UNC, Chocolatey)
│
├── utils/
│   ├── console.py       → Tema de cores, instância do Rich console, helpers de print
│   ├── common.py        → Funções básicas (is_admin, clear_screen, pause)
│   ├── logger.py        → Logger com gravação em arquivo + saída colorida
│   └── powershell.py    → Wrapper para execução de comandos PowerShell
│
├── build.bat            → Script de compilação para .exe
├── requirements.txt     → Dependências Python (rich, pyinstaller)
└── README.md            → Documentação resumida do projeto
```

### Onde cada coisa está

| Quero alterar... | Arquivo |
|------------------|---------|
| Softwares, pastas, domínio | `config.py` (apenas este arquivo) |
| Visual/cores do terminal | `utils/console.py` |
| Comportamento das instalações | `modules/install.py` |
| Lógica de rename/domínio | `modules/identity.py` |
| Testes de diagnóstico | `modules/diagnostics.py` |
| Banner e menus | `main.py` |

---

## FAQ

**P: Posso usar a ferramenta sem internet?**
R: Parcialmente. A Etapa 1 (domínio) funciona na rede local. A Etapa 2 precisa de internet para o Chocolatey baixar os softwares. A cópia de pastas funciona na rede local.

**P: Posso executar as etapas fora de ordem?**
R: A Etapa 2 pode ser executada sem a Etapa 1, mas os softwares serão instalados na máquina com o nome/domínio antigos. O recomendado é sempre Etapa 1 → Reboot → Etapa 2.

**P: O que acontece se eu executar a Etapa 1 duas vezes?**
R: Funcionará normalmente — o PowerShell irá renomear/reingressar. Não causa danos.

**P: Posso adicionar instaladores que não são do Chocolatey?**
R: Sim, usando o mesmo mecanismo do Office. Edite o `config.py` e o `modules/install.py` para adicionar uma nova chamada ao `_run_installer` com o caminho do executável.

**P: A ferramenta funciona em Windows Server?**
R: Não foi testada, mas o mecanismo é o mesmo (PowerShell, Chocolatey). Pode funcionar com ajustes.

**P: Onde ficam os logs?**
R: Em `C:\ProvisioningLogs\`, com um arquivo por execução. O nome inclui o hostname e a data/hora.
