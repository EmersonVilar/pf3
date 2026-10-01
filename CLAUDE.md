# CLAUDE.md — pf3

Guia para qualquer IA ou pessoa que trabalhe neste repositório. Leia antes de editar.

## O que é

`pf3` é uma árvore de pastas TUI, **somente leitura e somente navegação**, em Python + Textual. Comando: `pf3 [pasta]`.
Ambiente do dono: Ubuntu 26.04, Hyprland, kitty, paleta Nord (Noctalia), Python 3.14. Idioma de conversa: português do Brasil.

## Regras invioláveis

1. **Somente leitura.** Nunca adicione código que abra, edite, mova, apague ou execute arquivos. Seleção de arquivo/pasta só alterna expansão (os handlers `*_selected` param o evento de propósito).
2. **Cores só ANSI** (`ansi_blue`, `ansi_bright_black`, `ansi_default`...), nunca hex fixo nem cores do tema Textual. Assim o app herda a paleta do kitty. `App(ansi_color=True)` é obrigatório. Evite `transparent` (vira preto); use `ansi_default`.
3. **Leve.** Carregamento preguiçoso (só lê pasta ao abrir). O watcher observa só as pastas abertas, `recursive=False`. Não observe a árvore inteira.
4. **Sem argumento obrigatório.** `pf3` sozinho abre a pasta atual.
5. **Sem pip global.** Sempre use `.venv/` deste repo. Nunca `sudo pip` nem `--break-system-packages`.

## Comandos

```sh
.venv/bin/python tests/smoke.py        # deve imprimir "ok"
.venv/bin/python pf3/app.py [pasta]    # roda o app (precisa de terminal real)
.venv/bin/python tools/gen_icons.py    # regenera pf3/icons_data.py
```

Rode `tests/smoke.py` depois de qualquer mudança em `pf3/app.py`. Para testar UI, use `app.run_test()` do Textual (headless) em vez de abrir terminal.

## Arquitetura (`pf3/app.py`)

- `PathTree(DirectoryTree)`: teclas, filtro de ocultos (`filter_paths`), ícones (`render_label`), `status_style` (gancho do git), `open_dirs`/`node_for` (usados pelo watcher).
- `Pf3(App)`: CSS, bindings globais, `watch_dirs`/`_watch` (worker `watchfiles.awatch`; reinicia só quando o conjunto de pastas abertas muda, por isso `_watched`).
- `ThinScrollBarRender`: substitui `ScrollBar.renderer` para barras finas (polegar `▐` vertical, `▂` horizontal).
- `file_icon(name)`: busca em `FILENAME_ICONS`, depois `EXTENSION_ICONS`, depois `FILE_DEFAULT`. `OVERRIDES` troca glifos que ficaram feios no kitty.
- Pastas: `FOLDER_CLOSED` (vazada, U+F0256) e `FOLDER_OPEN` (preenchida, U+F024B), sempre azul.

## Armadilhas já encontradas

- Handlers `on_tree_node_expanded/collapsed` **precisam ficar no `PathTree`**, não no `App` (no App eles não disparam).
- Tecla `.` no kitty chega como `full_stop`, não `period`; mantenha os dois no binding.
- `ctrl+p` abria a command palette do Textual; está desativada (`ENABLE_COMMAND_PALETTE = False`).
- Cursor e hover do Textual têm cores hex fixas por padrão; o CSS do app as sobrescreve com ANSI. Ao mexer no CSS, confira com `get_component_rich_style`.
- Glifos Nerd Font: confirme que existem na fonte do kitty (`/usr/lib/kitty/fonts/SymbolsNerdFontMono-Regular.ttf`, via `fontTools`) antes de usar um codepoint novo; alguns (ex.: U+F114, U+F07B) renderizaram como caixa.
- `pf3/icons_data.py` é gerado. Para trocar um ícone específico, use `OVERRIDES` em `app.py`, não edite o arquivo gerado.

## Convenções

- Texto da UI em português (rodapé: "Ocultos", "Recolher tudo", "Sair").
- Código no estilo atual: comentários poucos, nomes em inglês, sem dependências novas sem necessidade (hoje só `textual` e `watchfiles`).
- Commits curtos e objetivos, em português ou inglês.
- Atualize `README.md` (teclas, recursos) quando mudar comportamento visível.

## Roadmap

Cores por status do git (modificado, novo, ignorado), como VS Code/neo-tree: implemente em `PathTree.status_style(path)`, que hoje retorna `""`. Use cores ANSI. Obtenha o status com `git status --porcelain` fora da thread da UI e só em repositórios git, mantendo o app leve.
