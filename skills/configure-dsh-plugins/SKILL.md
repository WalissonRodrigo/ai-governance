# configure-dsh-plugins

**Descrição:** Esta skill configura o DeepSeek Harness (DSH) para ativar todos os plugins atualmente presentes no workspace, garantindo que as funcionalidades de `smart-doc-converter`, `graphify`, `cave-man`, `get-shit-done`, `everything-claude-code`, `ui-ux-pro-max`, `awesome-design-md` e o conjunto `openspec-*` estejam habilitadas.

**Objetivo:** Automatizar a inclusão dos plugins no arquivo de configuração do DSH (`settings.json` ou nas configurações internas) e assegurar que o ambiente esteja pronto para uso.

**Passos da skill:**
1. Detectar todas as pastas de skill dentro `./skills/` que correspondam a plugins conhecidos.
2. Atualizar o objeto de configuração do DSH (`settings.json` ou equivalente) adicionando as entradas de plugin na seção `plugins`.
3. Verificar se o `PreToolUse` hook inclui o comando `rtk hook claude` (já presente). Caso não esteja, inserir.
4. Salvar as alterações e informar ao usuário que a configuração foi concluída.

**Uso:**
- No chat, invoque a skill com o comando `configure-dsh-plugins`.
- A skill aplicará automaticamente as alterações e exibirá um resumo das mudanças.

**Nota:** Esta skill não altera código de aplicação, apenas configura o ambiente DSH.
