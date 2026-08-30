# Alinhamento das Skills com Repositórios Upstream — Spec

## Why

As skills locais de `ai-governance` foram derivadas de repositórios open-source de alta adoção, mas hoje carregam apenas o "esqueleto conceitual" de cada um. Comparando-as com os projetos de referência, identificamos que todas mantêm o conceito central correto, porém perdem profundidade operacional (camada de dados, estado persistente, hooks executáveis, catálogos curados e scripts de geração). Este documento valida o grau de similaridade e define melhorias com prós/contras para elevar cada skill ao nível do upstream sem sacrificar a leveza e a portabilidade atuais.

## Análise de Similaridade (Validação)

| Skill local | Upstream | Similaridade | Lacuna principal |
|---|---|---|---|
| `graphify` | [safishamsi/graphify](https://github.com/safishamsi/graphify) (v8, 962 commits) | **Conceito alto, profundidade baixa** | Engine completo vs. script único |
| `awesome-design-md` | [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (70+ DESIGN.md, 36k★) | **Formato alto, conteúdo baixo** | Template sem biblioteca curada |
| `get-shit-done` | [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) (62k★) | **Fases iguais, operação baixa** | Sem ROADMAP/STATE/comandos |
| `everything-claude-code` | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (140k★) | **Filosofia alta, runtime baixo** | Sem hooks/agentes/memória |
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (690k★) | **Regras altas, dados baixos** | Sem catálogo/reasoning/geração |

---

## What Changes

- **graphify**: documentar schema JSON + formatos; adicionar cache incremental em `.ai-cache/`; adicionar detecção de entry points e saída `mermaid` validada.
- **awesome-design-md**: adicionar exemplos concretos de DESIGN.md; adotar arquitetura de tokens em 3 camadas; modelo de `preview.html`.
- **get-shit-done**: adicionar artefatos `ROADMAP.md`/`STATE.md`; distinguir fase de discussão/blueprint; formato de plano estruturado.
- **everything-claude-code**: adicionar seção de hooks runtime (bloquear/alertar); definir agentes declarativos; guia de memória persistente + segurança.
- **ui-ux-pro-max**: adicionar arquitetura de tokens, anti-patterns e checklist QA em 5 dimensões.

## Impact

- Affected specs: `graphify`, `awesome-design-md`, `get-shit-done`, `everything-claude-code`, `ui-ux-pro-max`.
- Affected code: `skills/<skill>/SKILL.md` de cada um; novos artefatos opcionais (`references/`, `data/`, `scripts/`).

---

## ADDED Requirements

### Requirement: Graphify documenta a saída e armazena cache incremental
A skill SHALL documentar o schema JSON de saída e os formatos suportados, e SHALL persistir grafos intermediários em `.ai-cache/` para evitar re-extração.

#### Scenario: Extrator roda duas vezes no mesmo projeto
- **WHEN** o agente executa `graphify.py` sobre um projeto já mapeado
- **THEN** o grafo é reutilizado do `.ai-cache/` e re-extraído apenas se `--force` ou se houve mudança de assinaturas.

### Requirement: Awesome Design MD fornece exemplos e tokens em camadas
A skill SHALL incluir exemplos reais de DESIGN.md e SHALL estruturar tokens em `primitive → semantic → component`, suportando um `preview.html` para validação visual.

#### Scenario: Gerar DESIGN.md de uma landing page
- **WHEN** o agente gera um DESIGN.md para um novo produto
- **THEN** o arquivo contém tokens em 3 camadas e referencia um exemplo curado do mesmo domínio.

### Requirement: Get Shit Done persiste estado entre sessões
A skill SHALL produzir `ROADMAP.md` e `STATE.md` como fonte de verdade do progresso, e SHALL separar as fases de discussão e blueprint.

#### Scenario: Retomar um trabalho interrompido
- **WHEN** o agente reinicia um fluxo de implementação
- **THEN** ele lê `STATE.md` para restaurar a fase atual e não repete trabalho concluído.

### Requirement: Everything Claude Code descreve hooks de qualidade e agentes declarativos
A skill SHALL especificar hooks `PreToolUse` que bloqueiam/alertam/autocorrigem, e SHALL definir agentes como personas declarativas com contrato de saída.

#### Scenario: Impedir commit com segredo
- **WHEN** uma tool call tenta escrever um valor que casa com padrão de segredo
- **THEN** o hook bloqueia (exit 2) ou alerta antes da execução.

### Requirement: UI UX Pro Max aplica anti-patterns e checklist de QA
A skill SHALL enumerar anti-patterns de "AI-slop" e SHALL impor um checklist de QA em 5 dimensões (visual, interação, claro/escuro, consistência, acessibilidade) antes da entrega.

#### Scenario: Revisar página gerada
- **WHEN** uma UI é gerada
- **THEN** o agente executa o checklist de 5 dimensões e remove emoji, gradientes AI e estados de hover ausentes.