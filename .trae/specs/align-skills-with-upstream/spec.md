# Alinhamento das Skills com Repositórios Upstream — Spec

## Why

As skills locais de `ai-governance` foram derivadas de repositórios open-source de alta adoção, mas hoje carregam apenas o "esqueleto conceitual" de cada um. Este documento revalida o grau de similaridade contra o estado **atual** de cada upstream (v8 / gsd-core / ECC / v2) e define melhorias com prós/contras para elevar cada skill ao nível do upstream sem sacrificar a leveza e a portabilidade atuais.

## Análise de Similaridade (Validação Atualizada)

| Skill local | Upstream (estado atual) | Similaridade | Lacuna principal |
|---|---|---|---|
| `graphify` | [safishamsi/graphify](https://github.com/safishamsi/graphify) (v8, YC S26, PyPI `graphifyy`) | **Conceito alto, profundidade média** | Engine de knowledge graph vs. extrator de arestas |
| `awesome-design-md` | [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (73 DESIGN.md curados) | **Formato alto, conteúdo baixo** | Template vs. corpus curado com previews |
| `get-shit-done` | [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core) (ex-gsd-build; loop Discuss→Plan→Execute→Verify→Ship) | **Fases iguais, operação média** | Sem subagentes de contexto fresco + CONTEXT.md |
| `everything-claude-code` | [affaan-m/ECC](https://github.com/affaan-m/ECC) (67 agents, 281 skills, AgentShield) | **Filosofia alta, runtime baixo** | Guia vs. harness completo com instalador |
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (v2, CLI `uipro`) | **Regras altas, dados baixos** | Princípios declarativos vs. catálogo + engine BM25 |

---

## Skill 01 — Graphify

**Upstream (v8)** — pacote Python `graphifyy` com CLI `graphify` instalável em 20+ plataformas (Claude Code, Codex, Trae, Cursor…). `/graphify .` gera `graphify-out/` com `graph.html` (interativo), `GRAPH_REPORT.md` (god nodes, conexões surpreendentes, comentários "why", suggested questions) e `graph.json` (grafo completo). Suporta 31 linguagens via tree-sitter (AST local, sem API), docs, PDFs, imagens, vídeo/áudio, YouTube, Office e Google Sheets. Flags: `--update` (incremental), `--cluster-only`, `--no-viz`, `--wiki`; comandos `query`, `path`, `explain`, `add`, `merge-graphs`, `prs`; MCP server; hook de auto-rebuild por commit; `.graphifyignore`; tags de confiança `EXTRACTED|INFERRED|AMBIGUOUS`; workflow de equipe (commitar `graphify-out/`).

**Local** — `scripts/graphify.py` leve: formatos `summary|mermaid|json`, cache em `.ai-cache/graphify/` com `--force`, fallback manual com `glob`/`grep`. Sem docs/PDF/figuras, sem clustering, sem query semântica, sem tags de confiança.

### Prós da versão local
- Zero dependência pesada (tree-sitter, whisper, yt-dlp, APIs); roda em qualquer sandbox.
- Token economy agressiva: grafo condensado consumido no contexto, sem abrir arquivos.
- Cache incremental alinhado à convenção `.ai-cache/` do workspace.
- Não depende de install global nem de conta/API.

### Contras da versão local vs upstream
- Só mapeia arestas de import/export; ignora docs, PDFs, imagens e "why" inline — perde o conhecimento tácito.
- Sem rank de god nodes nem conexões surpreendentes (o maior valor da GRAPH_REPORT).
- Sem `query`/`path`/`explain`: o agente não "pergunta" ao grafo, apenas o lê.
- Sem tags de confiança — não distingue extraído de inferido.

### Como melhorar (custo/ganho)
| Ação | Ganho | Custo |
|---|---|---|
| Adicionar seção "God-nodes & Surprising Connections" no `summary` | Alto | Baixo (lógica simples de grau/inesperado) |
| Extrair comentários `# NOTE/WHY/HACK` como nós | Alto | Baixo |
| Tags de confiança por aresta | Médio | Baixo |
| Suporte a `.md/.txt/.yaml` como nós de doc | Médio | Médio (parsers leves) |
| Substituir o script local pelo pacote `graphifyy` quando disponível | Alto | Nenhum (decisão de ambiente; manter fallback local) |

---

## Skill 02 — Awesome Design MD

**Upstream** — coleção curada de **73 `DESIGN.md`** extraídos de sites reais (Claude, Stripe, Revolut, Airbnb, Shopify, Vercel, Linear, Figma, Nike, Tesla, BMW…), cada um com 9 seções: Visual Theme, Color Palette & Roles, Typography Rules, Component Stylings, Layout Principles, Depth & Elevation, Do's & Don'ts, Responsive Behavior, Agent Prompt Guide. Cada site inclui `DESIGN.md` + `preview.html` + `preview-dark.html`. Segue a spec [Google Stitch DESIGN.md](https://stitch.withgoogle.com/docs/design-md/overview/). Fluxo de uso: copiar um DESIGN.md do domínio certo e mandar o agente construir.

**Local** — template de `DESIGN.md` com tokens em 3 camadas, matriz de componentes (8 estados), a11y, geração de `preview.html` e recomendação de ancoragem a referências (Shopify/Stripe/Adobe).

### Prós da versão local
- Template autocontido, não depende de fetch externo.
- Cobrimos o formato canônico + 3 camadas de tokens (primitivo → semântico → componente).
- Instrução de `preview.html`/`preview-dark.html` alinhada ao padrão upstream.
- Adequado para criações greenfield sem esperar curadoria.

### Contras da versão local vs upstream
- Não há corpus: o template não entrega o maior ganho do upstream (exemplo real do mesmo domínio para "ancorar" a IA).
- Sem seções como "Do's & Don'ts", "Depth & Elevation" e "Agent Prompt Guide" — cruciais para consistência.
- Sem `preview-dark.html` (apenas `preview.html`).

### Como melhorar (custo/ganho)
| Ação | Ganho | Custo |
|---|---|---|
| Adicionar seções obrigatórias "Do's & Don'ts" e "Depth & Elevation" ao template | Alto | Baixo |
| Adicionar seção "Agent Prompt Guide" (paleta-resumo + prompts prontos) | Alto | Baixo |
| Referenciar URLs curados por domínio (ex.: `getdesign.md/linear.app/design-md`) em vez de só nomes | Alto | Nenhum (fetch sob demanda) |
| Gerar `preview-dark.html` junto do `preview.html` | Médio | Baixo |
| Incluir exemplo completo ancorado (copy de DESIGN.md real curado) como referência interna | Alto | Médio (licença MIT ok, citar origem) |

---

## Skill 03 — Get Shit Done

**Upstream** — o projeto **migrou para [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core)** (o repo `gsd-build/get-shit-done` agora é apenas redirect). Loop por milestone em 5 fases: **Discuss → Plan → Execute → Verify → Ship**. É um sistema de **context engineering** anti-*context rot*: todo trabalho pesado (pesquisa, planejamento, execução) roda em **subagentes de contexto fresco** mantendo a sessão principal enxuta; artefatos `STATE.md` e `CONTEXT.md` sobrevivem entre sessões; installer `npx @opengsd/gsd-core`, comandos `/gsd-new-project` e `/gsd-onboard`; docs ofic (tutoriais/how-to/referência/explicação); roda em Claude Code, OpenCode, Antigravity, Kimi, Codex, Copilot, Cursor, Windsurf.

**Local** — 5 fases **Discovery → Blueprint → Execution → Verification → Checkpoint**; discussão integrada ao Discovery; `ROADMAP.md` + `STATE.md`; plano YAML/XML; 4 Golden Rules.

### Prós da versão local
- Mesmo espírito de loop em fases com checkpoint e estado persistente.
- Leve e portátil — sem npx, sem instalador, sem dependência de runtime.
- Já possui discussão antes do blueprint (equivalente ao Discuss) e estado entre sessões (STATE.md).

### Contras da versão local vs upstream
- **Sem execução em contexto fresco**: o distintivo do GSD Core (subagentes para combater context rot) não está documentado.
- Sem `CONTEXT.md` (memória do contexto: decisões, descobertas, arquitetura) — só progresso.
- Sem gitops por fase (não define fluxo PR/arquivamento por milestone).
- Sem guia de instalação multi-runtime nem comandos slash.

### Como melhorar (custo/ganho)
| Ação | Ganho | Custo |
|---|---|---|
| Adicionar princípio "subagent de contexto fresco por fase" (Discovery/Plan/Verify delegáveis via `task`)) | Alto | Baixo |
| Introduzir `CONTEXT.md` (decisões + descobertas + arquitetura) além do `STATE.md` | Alto | Baixo |
| Explicitar ordem Ship/PR por fase (referenciar Checkpoint como PR-ready) | Médio | Baixo |
| Atualizar referências do repo antigo para `open-gsd/gsd-core` | Baixo | Nenhum |

---

## Skill 04 — Everything Claude Code

**Upstream (ECC)** — harness completo: **67 agents**, **281 skills**, **94 comandos**, ciclo `plan → test → implement → review → verify → remember → improve`; **hooks + memória em runtime** (session summaries, continuous learning, instincts, context controls); **AgentShield** (scan de prompts, hooks, MCP config, permissões e segredos); regras seletivas por linguagem; install via plugin marketplace (Claude Code), sync (Codex), `install.sh --profile` para Cursor/OpenCode/Gemini/Zed/Copilot etc.

**Local** — guia de orquestração: matriz de roteamento de ferramentas, 3 arquétipos de subagente, personas YAML, protocolo de handoff, hooks `PreToolUse` (bloquear/alertar/autocorrigir), política de segredos, memória persistente.

### Prós da versão local
- Captura corretamente os princípios de roteamento (`rg`/`glob`/`read`/`edit`) e isolamento de contexto.
- Independe de runtime instalado; é auto-contido e portável.
- Já especifica hooks `PreToolUse` e personas declarativas — os dois diferenciais conceituais do upstream.

### Contras da versão local vs upstream
- Sem catálogo real: 1 rota por intenção vs. 281 skills/67 agents operacionais do ECC.
- Sem runtime de memória contínua (apenas orientação de persistir em `.ai-cache/`).
- Sem verificação de segurança automatizada tipo AgentShield (é política, não scanner).
- Sem orquestração de ciclo completo plan→test→implement→review.

### Como melhorar (custo/ganho)
| Ação | Ganho | Custo |
|---|---|---|
| Adicionar ciclo "plan → test → implement → review → verify → remember → improve" como fluxo padrão | Alto | Baixo |
| Adicionar seção "Memory & Instincts": resumo de sessão e reutilização de vitórias em `.ai-cache/` | Alto | Baixo |
| Adicionar checklist de auto-review em contexto fresco (revisar o próprio diff como Auditor) | Alto | Baixo |
| Referenciar ECC como source opcional (plugin/catálogo) sem copiar o harness | Médio | Nenhum |

---

## Skill 05 — UI UX Pro Max

**Upstream (v2)** — CLI `uipro` + catálogo: **161 regras de reasoning por indústria**, **67 estilos UI**, **161 paletas**, **57 pares de fonte**, 25 tipos de chart, 15 stacks, 99 UX guidelines; **engine de reasoning BM25** (busca multi-domínio: produto × estilo × paleta × padrão × tipografia) e **gerador de design system** completo com PATTERN + STYLE + COLORS + TYPOGRAPHY + EFFECTS + ANTI-PATTERNS + PRE-DELIVERY CHECKLIST.

**Local** — regra 60-30-10, grade 8pt, matriz de 8 estados, WCAG 2.2 AA, diretivas CSS, arquitetura de tokens 3 camadas, anti-patterns AI-slop, checklist QA 5 dimensões.

### Prós da versão local
- Regras centrais corretas e consensuais (8 estados, 8pt, 4.5:1, 150–250ms, `transform`/`opacity`).
- Já possui anti-patterns explícitos e checklist de QA em 5 dimensões.
- Compacto; aplicável sem CLI, catálogo ou engine.

### Contras da versão local vs upstream
- Sem camada de dados: paleta/tipografia/estilo não são catalogados por indústria.
- Sem reasoning por indústria: a decisão fica na inferência genérica, não em regra especializada.
- Sem busca multi-domínio nem ranking (BM25) para sintetizar um design system.
- Checklist existe, mas sem a saída estruturada (PATTERN/STYLE/COLORS/…).

### Como melhorar (custo/ganho)
| Ação | Ganho | Custo |
|---|---|---|
| Adicionar tabela "paletas por indústria" curada (subset essencial de ~10 setores) | Alto | Baixo |
| Adicionar "regras de reasoning por indústria" compactas (padrão + estilo + anti-pattern do setor) | Alto | Médio |
| Estruturar a saída do design system como bloco único (PATTERN→STYLE→COLORS→TYPOGRAPHY→EFFECTS→CHECKLIST) | Alto | Baixo |
| Referenciar CLI `uipro`/catálogo upstream como fonte sob demanda | Médio | Nenhum |

---

## What Changes
- Atualizar a seção de validação com o estado atual de cada upstream (feito nesta revisão).
- Adotar as melhorias marcadas como "Alto ganho / Baixo custo" em cada skill via atualização dos `SKILL.md`.
- Manter leveza: nada de dependências obrigatórias; referências a ferramentas externas são opcionais.

## Impact

- Affected specs: `graphify`, `awesome-design-md`, `get-shit-done`, `everything-claude-code`, `ui-ux-pro-max`.
- Affected code: `skills/<skill>/SKILL.md` de cada um; possíveis novos arquivos auxiliares (`references/`, `data/`, `scripts/`).

---

## ADDED Requirements

### Requirement: Graphify reporta god nodes e conexões surpreendentes
A skill SHALL identificar os nós de maior acoplamento e conexões entre arquivos de módulos distintos, sinalizando-as como "surpreendentes".

#### Scenario: Mapeando um repositório grande
- **WHEN** o agente gera o grafo em `summary`
- **THEN** o resumo destaca god nodes e 2–3 conexões inesperadas entre arquivos.

### Requirement: Awesome Design MD inclui Do's & Don'ts e Agent Prompt Guide
A skill SHALL exigir as seções "Do's & Don'ts" e "Agent Prompt Guide" no template e SHALL permitir ancorar a referências curadas por domínio.

#### Scenario: Gerar DESIGN.md de uma landing
- **WHEN** o agente gera um DESIGN.md
- **THEN** o arquivo contém guardrails explícitos e prompts prontos, além de tokens em 3 camadas.

### Requirement: Get Shit Done executa fases pesadas em contexto fresco e mantém CONTEXT.md
A skill SHALL delegar pesquisa/planejamento/verificação a subagentes de contexto fresco e SHALL manter `CONTEXT.md` (decisões, descobertas, arquitetura) além do `STATE.md`.

#### Scenario: Resumir trabalho interrompido
- **WHEN** uma sessão é retomada
- **THEN** o agente restaura fases de `STATE.md` e contexto de `CONTEXT.md`, sem reler o repositório inteiro.

### Requirement: Everything Claude Code adota ciclo plan→test→implement→review e auto-review
A skill SHALL impor o ciclo completo de entrega e SHALL executar auto-review do próprio diff em contexto fresco (Auditor) antes de concluir.

#### Scenario: Concluir uma alteração multi-arquivo
- **WHEN** o executor termina as edições
- **THEN** um subagente Auditor revisa o diff completo antes do handoff.

### Requirement: UI UX Pro Max cataloga decisões por indústria e estrutura a saída
A skill SHALL fornecer subset curado de paletas e regras de reasoning por indústria e SHALL sintetizar o design system como bloco PATTERN→STYLE→COLORS→TYPOGRAPHY→EFFECTS→CHECKLIST.

#### Scenario: Gerar UI para um SaaS financeiro
- **WHEN** o agente recebe um pedido de UI
- **THEN** a entrega começa pelo bloco de design system com paleta/estilo/tipografia por setor e o checklist de QA.