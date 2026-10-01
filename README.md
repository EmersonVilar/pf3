# pf3 (pathtree)

Árvore de pastas para o terminal, somente leitura, no estilo neo-tree / VS Code.
Digite `pf3` em qualquer pasta e a árvore dela abre. Feito em Python com [Textual](https://textual.textualize.io/).

## Recursos

- Accordion: pastas abrem e fecham no lugar (`Enter`, setas, `h`/`l`).
- Navegação por `j`/`k` e setas; rolagem horizontal com `Shift+←/→` ou `H`/`L`.
- Arquivos ocultos escondidos por padrão; `.` alterna.
- Atualiza sozinha quando arquivos mudam (só as pastas abertas são observadas).
- Somente navegação e leitura: nunca abre, edita ou apaga arquivos.
- Cores ANSI (herda a paleta do terminal, ex.: Nord no kitty).
- Ícones Nerd Font por extensão e nome de arquivo (mapa do nvim-web-devicons).
- Pasta fechada = ícone vazado, pasta aberta = ícone preenchido, ambos em azul.
- Barras de rolagem finas.

## Teclas

| Tecla | Ação |
|---|---|
| `j` / `↓`, `k` / `↑` | mover cursor |
| `Enter` | abrir/fechar pasta |
| `l` / `→`, `h` / `←` | abrir; fechar ou ir para a pasta pai |
| `Shift+→` / `L`, `Shift+←` / `H` | rolar visão 8 colunas |
| `g` / `Home`, `G` / `End` | topo, fim |
| `.` | mostrar/ocultar arquivos ocultos |
| `r` | recolher tudo (reset) |
| `q` | sair |

## Requisitos

- Python 3.10+ (testado em 3.14)
- `textual` e `watchfiles` (ver `requirements.txt`)
- Terminal com fonte Nerd Font para os ícones (o kitty traz uma embutida)

## Instalação

O `pip` global é bloqueado (Ubuntu), então use um venv dentro do repositório:

```sh
git clone <este repo> ~/tree-tui   # ou copie a pasta
cd ~/tree-tui
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
install -m 755 bin/pf3 ~/.local/bin/pf3   # launcher
```

O launcher `bin/pf3` chama `~/tree-tui/.venv/bin/python ~/tree-tui/pf3/app.py "$@"`.
Se o repo ficar em outro lugar, edite o caminho nele. `~/.local/bin` precisa estar no `PATH`.

## Uso

```sh
pf3            # pasta atual
pf3 ~/projeto  # outra pasta
```

## Desenvolvimento

```sh
.venv/bin/python tests/smoke.py      # teste headless (imprime "ok")
.venv/bin/python tools/gen_icons.py  # regenera pf3/icons_data.py (baixa da internet)
```

Estrutura:

```
pf3/app.py          app inteiro (widget, teclas, watcher, ícones, scrollbar)
pf3/icons_data.py   GERADO por tools/gen_icons.py, não edite à mão
tools/gen_icons.py  gerador do mapa de ícones
tests/smoke.py      teste de fumaça headless
bin/pf3             launcher (copiar para ~/.local/bin)
```

## Roadmap

- Cores por status do git (arquivo modificado, novo, ignorado), como VS Code e neo-tree.
  Ponto de extensão: `PathTree.status_style(path)` em `pf3/app.py`.

## Créditos

Mapa de ícones: [nvim-web-devicons](https://github.com/nvim-tree/nvim-web-devicons) (MIT).
