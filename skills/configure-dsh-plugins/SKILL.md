---
name: configure-dsh-plugins
description: Instala e sincroniza os plugins do DeepSeek Harness (DSH) a partir dos forks/correções do usuário (dsh-vsceditor i18n, dsh-llm-failover fix, dsh-tier-router/tier-preset-discovery, dsh-vscode-theme) e integra as skills do ~/.claude/skills do usuário ao DSH.
metadata:
  version: "1.0.0"
  audience: self-hosted DSH
---

# Configure DSH Plugins (forks + skills .claude)

Configura o perfil web do DeepSeek Harness (`$DSH_HOME/profiles/web`) para usar os forks/correções do usuário em vez dos pacotes upstream problemáticos, e garante que o DSH descubra as skills do usuário em `~/.claude/skills`.

## Contexto (por que isto existe)

Os plugins upstream deram problemas e não tinham tradução. Até a adoção oficial das issues, o perfil deve instalar os forks do usuário (`WalissonRodrigo`):

| Plugin | Spec instalável | Correção no fork |
|---|---|---|
| `dsh-vsceditor` | `github:WalissonRodrigo/dsh-vsceditor#feat/multi-language-i18n` | i18n (zh/en/pt-BR/es) em host, client e bridge; config `language` |
| `dsh-llm-failover` | `github:WalissonRodrigo/dsh-llm-failover#fix/settings-plugin-item-keyed-key` | corrige crash do client: slot `settings.plugin.item` precisa de `options.key` |
| `dsh-tier-router` (entry id `tier-preset-discovery`) | `github:WalissonRodrigo/dsh-tier-router#fix/settings-persistence` | manter a configuração do tier-router registrada no escopo do host; consumi-la a partir do escopo do agente; validação rigorosa  |
| `dsh-vscode-theme` | `github:Sim-xia/dsh-vscode-theme` | upstream |

## 1. Verificar o perfil ativo

```bash
echo "$DSH_HOME"                     # default: ~/.dsh
ls "$DSH_HOME/profiles/web/package.json"
```

O perfil web é o usado pelo GUI (servidor `dsh web`). Não use outro perfil sem instrução explícita.

## 2. Corrigir `package.json` do perfil

Garantir `dependencies` e `dsh.profile.bundles` (ordem importa: base → web-app → plugins):

```json
{
  "name": "dsh-profile-web",
  "private": true,
  "dependencies": {
    "dsh-llm-failover": "github:WalissonRodrigo/dsh-llm-failover#fix/settings-plugin-item-keyed-key",
    "dsh-tier-router": "github:WalissonRodrigo/dsh-tier-router#fix/settings-persistence",
    "dsh-vsceditor": "github:WalissonRodrigo/dsh-vsceditor#feat/multi-language-i18n",
    "dsh-vscode-theme": "github:Sim-xia/dsh-vscode-theme"
  },
  "dsh": {
    "profile": {
      "bundles": [
        "@deepseek-ai/dsh-base",
        "@deepseek-ai/dsh-web-app",
        "dsh-vscode-theme",
        "dsh-vsceditor",
        "dsh-llm-failover",
        "dsh-tier-router"
      ]
    }
  }
}
```

**Atenção ao lockfile:** se `pnpm-lock.yaml` ainda resolver `dsh-vsceditor` de `k-ying` (upstream) ou `dsh-llm-failover` do registry npm, o lock está stale — o fork declarado no `package.json` NÃO está efetivamente instalado. Sempre rodar o passo 3 após editar.

## 3. Instalar de forma eficiente (refresh do lock + node_modules)

Dentro do diretório do perfil:

```bash
cd "$DSH_HOME/profiles/web"
pnpm install --no-frozen-lockfile
```

Alternativa equivalente via CLI integrada do DSH:

```bash
dsh plugin --profile web install
```

Se o pnpm bloquear scripts de build de pacotes git-hosted (mensagem sobre `allowBuilds`), adicionar a chave em `pnpm-workspace.yaml` conforme a dica impressa e rodar de novo.

## 4. Verificar a instalação (fork de fato no disco)

```bash
# vsceditor: precisa conter strings i18n (zh/en/pt-BR/es)
grep -n "cfg.language" node_modules/dsh-vsceditor/lib/host.js | head

# llm-failover: precisa usar key: NS no slot settings.plugin.item (não id/order)
grep -n "key: NS" node_modules/dsh-llm-failover/lib/client.js

# lock resolvido para os forks
grep -A2 "dsh-vsceditor\b" pnpm-lock.yaml | head
grep -A2 "dsh-llm-failover" pnpm-lock.yaml | head

# composição final do perfil
dsh --profile web --dump-config | grep -E "vsceditor|failover|tier|vscode-theme"
```

## 5. Integrar as skills de `~/.claude/skills` ao DSH

O provider `skill-filesystem` do DSH escaneia por padrão (rank): projeto `.dsh/skills` e `.agents/skills`, depois `<dshHome>/skills` (`~/.dsh/skills`) e `<agentsHome>/skills` (`~/.agents/skills`), além de `customSkillDirs`. Para o DSH usar as MESMAS skills do Claude (`~/.claude/skills`):

1. **Mecanismo comprovado — espelho `~/.agents/skills`** (DSH descobre por `agentsHome` default; uma skill nova copiada aqui aparece no catálogo da UI imediatamente):

```bash
rsync -a --delete ~/.claude/skills/ ~/.agents/skills/
```

2. **Opcional — `customSkillDirs` explícito** no `cordis.patch.yml` do perfil (`$DSH_HOME/profiles/web/cordis.patch.yml`), SOMENTE se a entrada `skill-filesystem` estiver habilitada no perfil ativo (confira antes com `dsh --profile web --dump-config | grep -A2 dsh-skill-filesystem`; em alguns perfis ela vem `disabled: true` e o patch não tem efeito):

```yaml
- id: skill-filesystem
  name: '@deepseek-ai/dsh-skill-filesystem'
  config:
    customSkillDirs:
      - /home/<user>/.claude/skills
```

3. Conferir no catálogo da UI (o catálogo expõe `name`/`description` de cada skill; carregamentos re-leem o arquivo a cada chamada).

## 6. Reiniciar o ambiente

Mudanças de plugin (node_modules/bundles) só entram em vigor após reiniciar o servidor DSH web. Não derrubar um servidor em uso sem combinar; documentar que o próximo `dsh web` (ou reload do profile) aplica os forks.

## Nota de governança

- Não alterar código de aplicação: esta skill mexe apenas no perfil DSH do usuário (`~/.dsh`) e nos espelhos de skills.
- Backup antes de editar: `cp package.json package.json.bak`.
- Quando as issues do usuário forem adotadas upstream (release oficial), trocar os specs git pelos pacotes npm publicados e remover esta skill da lista de críticos.