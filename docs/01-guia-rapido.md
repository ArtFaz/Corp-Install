# 01 — Guia Rápido

Guia para o primeiro uso da ferramenta. Se você nunca utilizou o Provisionador antes, comece aqui.

---

## O que é o Provisionador?

É uma ferramenta de linha de comando que **automatiza a configuração de máquinas Windows** após uma formatação. Em vez de instalar cada software manualmente, configurar rede e renomear a máquina, o Provisionador faz tudo com poucos cliques.

### O que ele faz automaticamente

| Tarefa | Detalhes |
|--------|----------|
| Renomear a máquina | Define o hostname correto (ex: `PC-RH-001`) |
| Ingressar no domínio AD | Adiciona a máquina ao Active Directory da empresa |
| Instalar softwares | Chrome, WinRAR, Teams, AnyDesk via Chocolatey |
| Copiar pastas da rede | Copia diretórios de servidores de rede para o disco local |
| Instalar Office | Office 2013 ou 365, conforme escolha |
| Criar atalho NextBP | Atalho do sistema web no Desktop |
| Abrir AnyDesk | Para anotar o ID de acesso remoto |

---

## Requisitos

| Requisito | Por que é necessário |
|-----------|---------------------|
| **Windows 10 ou 11** | Compatível apenas com estes sistemas |
| **Executar como Administrador** | Todas as operações requerem privilégios elevados |
| **Acesso à rede corporativa** | Para copiar pastas dos servidores e acessar instaladores |
| **Acesso à internet** | Para o Chocolatey baixar e instalar os softwares |

> ⚠️ Se a ferramenta não for executada como Administrador, ela exibirá um erro e não prosseguirá.

---

## Como executar

### Com o executável (.exe)

1. Copie o arquivo `Provisionador.exe` para a máquina recém-formatada
2. **Clique com o botão direito** no arquivo → **Executar como administrador**
3. O menu principal será exibido automaticamente

### Com Python (ambiente de desenvolvimento)

```powershell
pip install rich
python main.py
```

---

## Fluxo de Trabalho Padrão

A configuração de uma máquina acontece em **duas etapas**, com uma reinicialização entre elas:

```
  Máquina recém-formatada
         │
         ▼
  ┌── ETAPA 1 ──────────────────────────────┐
  │  1. Abra o Provisionador como Admin     │
  │  2. Selecione [1] Nome e Domínio        │
  │  3. Informe: nome, domínio, usuário     │
  │  4. Confirme e aguarde                  │
  │  5. Reinicie quando solicitado          │
  └──────────────┬──────────────────────────┘
                 │
         🔄 REINICIALIZAÇÃO
                 │
         ▼ Faça login com o usuário do domínio
                 │
  ┌── ETAPA 2 ──────────────────────────────┐
  │  1. Abra o Provisionador novamente      │
  │  2. Selecione [2] Instalação Completa   │
  │  3. Aguarde (tudo é automático)         │
  │  4. Escolha a versão do Office          │
  │  5. Anote o ID do AnyDesk ao final      │
  └──────────────┬──────────────────────────┘
                 │
         ✅ MÁQUINA PRONTA PARA USO
```

### Passo a passo da Etapa 1

1. Após a instalação limpa do Windows, finalize o OOBE (configuração inicial)
2. Execute o Provisionador como Administrador
3. No menu, pressione **1** e depois **Enter**
4. Digite o novo nome da máquina (ex: `PC-VENDAS-005`)
5. O domínio padrão (`ultradisplays.local`) será sugerido — pressione Enter para aceitar ou digite outro
6. Informe o usuário administrador do domínio (ex: `ULTRADISPLAYS\admin.ti`)
7. Confira o resumo exibido e confirme com **S**
8. Uma janela do Windows solicitará a senha do administrador — insira-a
9. Quando solicitado, confirme a reinicialização

### Passo a passo da Etapa 2

1. Após a reinicialização, **faça login com um usuário do domínio**
2. Execute o Provisionador como Administrador novamente
3. No menu, pressione **2** e depois **Enter**
4. A ferramenta irá automaticamente:
   - Instalar o Chocolatey (se necessário)
   - Instalar Chrome, WinRAR, AnyDesk e Teams
   - Copiar as pastas da rede para o computador
5. Quando perguntado, escolha a versão do Office (1 = 2013, 2 = 365, 0 = pular)
6. O AnyDesk será aberto automaticamente — **anote o ID que aparece na tela**
7. Um resumo final mostrará o status de cada tarefa

> 💡 Se alguma tarefa falhar, use a opção **[3] Instalações Avulsas** para executar individualmente as que falharam.

---

## Menu Principal — Resumo

| Tecla | Nome | Quando usar |
|:-----:|------|-------------|
| **1** | Nome e Domínio | Logo após a primeira formatação, uma única vez |
| **2** | Instalação Completa | Após reiniciar e logar no domínio |
| **3** | Instalações Avulsas | Para executar tarefas específicas se algo falhou |
| **4** | Diagnóstico | Para verificar se a rede e os recursos estão acessíveis |
| **5** | Abrir Logs | Para consultar histórico de operações |
| **0** | Sair | Encerra a ferramenta |

---

## Próximos passos

- Para personalizar os softwares, pastas e configurações → [02 — Configuração](02-configuracao.md)
- Para entender cada opção do menu em detalhe → [03 — Uso Detalhado](03-uso-detalhado.md)
- Para boas práticas e resolução de problemas → [04 — Boas Práticas](04-boas-praticas.md)
