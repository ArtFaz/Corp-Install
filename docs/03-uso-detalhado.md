# 03 — Uso Detalhado

Explicação completa de cada opção do menu, o que acontece internamente e o que esperar durante a execução.

---

## Menu Principal

Ao abrir a ferramenta, você verá o banner com informações do sistema e o menu:

```
 ⚙  CONFIGURAÇÃO
 [1]  Nome e Domínio          Renomeia + ingresso AD

 📦  INSTALAÇÃO
 [2]  Instalação Completa     Tudo automatizado  ● Choco OK
 [3]  Instalações Avulsas     Escolha individual

 🔧  UTILIDADES
 [4]  Diagnóstico do Sistema  Verificar tudo
 [5]  Abrir Pasta de Logs     Histórico

 [0]  Sair
```

O indicador **● Choco OK** ou **● Choco N/A** mostra se o Chocolatey já está instalado no sistema.

---

## [1] Nome e Domínio (Etapa 1)

### O que faz

1. Solicita o **novo nome** da máquina
2. Solicita o **domínio** (com sugestão padrão do `config.py`)
3. Solicita o **usuário administrador** do domínio
4. Exibe um resumo para confirmação
5. Abre uma janela do Windows para digitar a **senha** do administrador
6. Executa o comando PowerShell `Add-Computer` com as flags `-DomainName` e `-NewName`
7. Oferece reinicialização imediata com contagem regressiva

### O que acontece por dentro

A ferramenta gera e executa um script PowerShell que faz o **rename e ingresso no domínio em uma única operação** usando `Add-Computer -NewName`. Isso garante que o nome correto seja propagado ao AD desde o início.

### Possíveis resultados

| Resultado | O que aconteceu |
|-----------|-----------------|
| ✅ Sucesso + Reiniciar | Nome e domínio configurados, máquina reiniciará |
| ✅ Sucesso + Reiniciar manualmente | Configurações aplicadas, reinicie quando conveniente |
| ❌ Credenciais não fornecidas | A janela de senha foi cancelada |
| ❌ Falha na configuração | DNS, conectividade com DC ou permissões incorretas |

### Momento correto de uso

- **Executar apenas uma vez**, logo após a instalação limpa do Windows
- **Antes de reiniciar** — as mudanças só aplicam após reboot
- Não execute se a máquina já está no domínio (não fará mal, mas é desnecessário)

---

## [2] Instalação Completa (Etapa 2)

### O que faz

Executa as 5 sub-tarefas em sequência:

| Ordem | Sub-tarefa | Detalhes |
|:-----:|-----------|----------|
| 1 | Instalar softwares | Chocolatey: Chrome, WinRAR, AnyDesk, Teams |
| 2 | Copiar pastas da rede | De caminhos UNC para o disco local |
| 3 | Instalar Office | Escolha interativa entre 2013 e 365 |
| 4 | Criar atalho NextBP | Atalho Chrome no Desktop público |
| 5 | Abrir AnyDesk | Para anotar o ID de acesso remoto |

### Comportamento do Chocolatey

Antes de instalar os pacotes, a ferramenta verifica se o Chocolatey está presente. Se **não estiver**, ele é instalado automaticamente pela internet.

O flag `--ignore-checksums` já está habilitado em todas as instalações para evitar o erro "Installer hash does not match".

**Códigos de retorno tratados:**

| Código | Significado | Ação |
|--------|-------------|------|
| `0` | Sucesso | Prossegue normalmente |
| `1641` ou `3010` | Sucesso com reboot pendente | Considerado sucesso |
| Qualquer outro | Erro | Verificar log. Se já instalado, é ignorado |

### Comportamento da cópia de pastas

- A pasta de **destino é apagada completamente** antes da cópia
- Uma barra de progresso mostra o andamento arquivo por arquivo
- O tempo total é exibido ao final

### Resumo final

Após todas as sub-tarefas, um painel mostra o resultado:

```
┌── INSTALAÇÃO CONCLUÍDA ──────────────┐
│  Softwares (Chocolatey)   ✅ Sucesso │
│  Pastas da Rede           ✅ Sucesso │
│  Office                   ⏭ Pulado  │
│  Atalho NextBP            ✅ Sucesso │
│  AnyDesk                  ✅ Sucesso │
│                                      │
│  Tempo total: 245s                   │
└──────────────────────────────────────┘
```

---

## [3] Instalações Avulsas

### O que faz

Exibe um submenu para executar **cada sub-tarefa individualmente**:

```
 [1]  Instalar Softwares     Chocolatey: Chrome, WinRAR, Teams, AnyDesk
 [2]  Copiar Pastas da Rede  NextUltraDisplays, NextUltraArt
 [3]  Instalar Office        Office 2013 ou 365
 [4]  Criar Atalho NextBP    Atalho Chrome --app
 [5]  Abrir AnyDesk          Para coletar o ID

 [0]  Voltar
```

### Quando usar

- Quando alguma tarefa **falhou** durante a instalação completa e você quer reexecutá-la
- Quando precisa instalar **apenas um componente** específico (ex: só copiar pastas da rede)
- Quando quer repetir uma tarefa (ex: instalar Office em uma máquina que já tinha o resto)

> 💡 Cada opção funciona de forma **independente**. Você pode executar qualquer uma sem ter executado as anteriores.

---

## [4] Diagnóstico do Sistema

### O que faz

Executa 3 verificações e exibe uma barra de saúde:

| Verificação | O que testa |
|-------------|-------------|
| **Chocolatey** | Se o `choco.exe` existe e responde ao `--version` |
| **Rede** | Ping para `8.8.8.8` via PowerShell (`Test-Connection`) |
| **Caminhos UNC** | Tenta acessar cada pasta e instalador de Office configurados |

### Resultados do diagnóstico

```
┌── RESUMO DO DIAGNÓSTICO ───────────────────────┐
│  Gerenciador de Pacotes (Chocolatey)    ✓ OK   │
│  Conectividade de Rede                  ✓ OK   │
│  Caminhos de Rede (UNC)                ✗ FALHA │
│                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━  67%               │
└─────────────────────────────────────────────────┘
```

### Quando usar

- **Antes da Etapa 2** — para garantir que tudo está acessível
- Após mudanças na rede ou no `config.py` — para validar
- Para diagnóstico rápido se algo falhar durante a instalação

> 💡 Se o teste de rede falhar para Internet mas você está na rede local, isso **não é crítico**. Porém, o Chocolatey precisa de internet para baixar pacotes.

---

## [5] Abrir Pasta de Logs

### O que faz

Abre o Windows Explorer na pasta `C:\ProvisioningLogs\`.

### Formato dos logs

Cada execução gera um arquivo no formato:

```
provisioning_<HOSTNAME>_<DATA_HORA>.log
```

Exemplo: `provisioning_PC-RH-001_20260213_140530.log`

### Conteúdo do log

Cada linha segue o formato:

```
[2026-02-13 14:05:30] [INFO] Chocolatey: googlechrome
[2026-02-13 14:05:45] [SUCCESS] googlechrome instalado.
[2026-02-13 14:06:10] [WARNING] microsoft-teams-new-install já está instalado. Pulando.
[2026-02-13 14:06:12] [ERROR] Falha ao copiar: \\192.168.0.8\pasta — Caminho inacessível
```

**Níveis de log:**

| Nível | Significado |
|-------|-------------|
| `INFO` | Ação iniciada ou informação geral |
| `SUCCESS` | Operação concluída com sucesso |
| `WARNING` | Algo não crítico aconteceu (ex: software já instalado) |
| `ERROR` | Falha que requer atenção |

---

## [0] Sair

Encerra a ferramenta com uma mensagem de despedida. O log registra o encerramento.

Se precisar interromper a ferramenta durante uma operação, use **Ctrl+C** — ele será capturado e tratado de forma segura.
