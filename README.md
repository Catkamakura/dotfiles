# Dotfiles [![Build Status](https://github.com/Catkamakura/dotfiles/actions/workflows/ci.yml/badge.svg)](https://github.com/Catkamakura/dotfiles/actions/workflows/ci.yml)

After cloning this repo, run `./install` to link the configuration and initialize
the pinned shell, Vim, and Emacs plugins. It can be run multiple times. Existing
regular files are not overwritten: move conflicting files to a backup first.
The installer does not delete untracked plugin files or upgrade plugin versions.

Install Git, Python 3, Zsh 5.8+, Vim 8+ and/or Neovim 0.11+, and optionally tmux with your
system package manager. The installer configures these programs; it does not
install them or change your login shell. Start Zsh with `exec zsh -l` after
installation. `EDITOR` defaults to the first available editor in this order:
`nvim`, `vim`, `vi`. Existing `EDITOR`/`VISUAL` choices take precedence. Git's
diff and merge tools are selected from installed tools instead of requiring
Neovim; set a preferred tool in `~/.gitconfig_local` if needed.

The shell uses Solarized colors when the terminal supports 256 colors. Keep
machine-specific setup in the local files below.

Dotfiles uses [Dotbot][dotbot] for installation.

Making Local Customizations
---------------------------

You can make local customizations for some programs by editing these files:

* `neovim` : `~/.nvim_local.lua`
* `vim` : `~/.vimrc_local`
* `emacs` : `~/.emacs_local`
* `zsh` / `bash` : `~/.shell_local_before` run first
* `zsh` : `~/.zshrc_local_before` run before `.zshrc`
* `zsh` : `~/.zshrc_local_after` run after `.zshrc`
* `bash` : `~/.bashrc_local_before` / `~/.bashrc_local_after`
* `zsh` / `bash` : `~/.shell_local_after` run before the shell-specific after hook
* `zsh` / `bash` : `~/.shell_private` run last
* `git` : `~/.gitconfig_local`
* `hg` : `~/.hgrc_local`
* `tmux` : `~/.tmux_local.conf`

When moving from Bash to Zsh, translate machine-specific PATH entries, tool
initializers, and aliases into `~/.zshrc_local_after`. Do not source `.bashrc`
from Zsh: `shopt`, Bash completion, and Bash prompt escapes are incompatible.
Only settings that should run in both shells belong in `.shell_local_*`.
For example, to prefer Vim on one machine even when Neovim is installed, add
`export EDITOR=vim VISUAL=vim` to `~/.shell_local_before`.

Pasting over SSH
----------------

Vim-style shell editing is retained. Terminal bracketed pastes insert literal
text, including newlines, and leave Zsh in insert mode. A stray paste-ending
marker is ignored so its `~` cannot change the last character's case.

`KEYTIMEOUT` defaults to 40 (400 ms); the previous 10 ms setting could split
escape sequences arriving over SSH. To tune it, put `DOTFILES_KEYTIMEOUT=60` in
`~/.zshrc_local_before` or `KEYTIMEOUT=60` in `~/.zshrc_local_after`. tmux uses a
100 ms escape timeout, adjustable in `~/.tmux_local.conf`.
See the [Zsh line editor documentation][zle] and [tmux escape-time FAQ][tmux-escape].

Vim and Neovim
--------------

Both editors are configured by `./install`; either can be used independently.
Vim loads `~/.vimrc` and `~/.vim`, including the pinned Vim plugins and familiar
NERDTree, CtrlP, and Fugitive shortcuts. Neovim uses its own Lua configuration
and native features. Each editor has a separate machine-local override file.

`nvim/init.lua` is linked to `${XDG_CONFIG_HOME:-~/.config}/nvim`. It uses native
Neovim features, persistent undo, built-in file browsing, and installed
Treesitter parsers. LSP completion is enabled when a server attaches; configure
servers/plugins in `~/.nvim_local.lua`. Nothing is downloaded when the editor
starts. It does not load the Vim config or its plugins.

Useful Neovim keys (leader is `\`; split navigation, relative numbers, and
wrapped-line movement use the same keys in Vim):

| Key | Action |
| --- | --- |
| `Ctrl-h/j/k/l` | Move between splits |
| `Ctrl-n` | Toggle relative numbers |
| `\n` / `\f` | Toggle sidebar / browse current file's directory |
| `\b` or `;` | List and switch buffers |
| `\u` | Show undo history |
| `\d` | Toggle movement by wrapped display lines |
| `Esc` | Clear search highlighting |

Native LSP mappings such as `K`, `grn`, `gra`, and `grr` remain available when a
language server attaches. `:checkhealth` checks local providers and tooling.

Tests
-----

With Zsh, Bash, Vim, Neovim, tmux, Python 3, and the Python `pexpect` package installed:

```sh
git submodule update --init --recursive -- .dotbot shell/plugins/ vim/pack/vendor/start/ zsh/plugins/
python3 tests/test_dotfiles.py
```

The suite uses temporary home directories and real pseudo-terminals to check
SSH-like delayed paste markers, multiline pastes, shell startup, prompt cleanup,
path helpers, editor selection, Vim and Neovim filetype isolation, tmux
configuration, and repeatable links for both editors.
CI runs these checks on Linux and macOS.

License
-------

Copyright (c) Anish Athalye. Released under the MIT License. See
[LICENSE.md][license] for details.

[dotbot]: https://github.com/anishathalye/dotbot
[license]: LICENSE.md
[zle]: https://zsh.sourceforge.io/Doc/Release/Zsh-Line-Editor.html
[tmux-escape]: https://github.com/tmux/tmux/wiki/FAQ#what-is-the-escape-time-option-is-zero-a-good-value
