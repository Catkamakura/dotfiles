path_prepend "$HOME/.local/bin"
path_prepend "$HOME/.dotfiles/bin"

# Respect machine-local editor choices; prefer Neovim when it is available.
if [[ -z ${EDITOR:-} ]]; then
    if command -v nvim >/dev/null 2>&1; then
        export EDITOR=nvim
    else
        export EDITOR=vi
    fi
fi
export VISUAL="${VISUAL:-$EDITOR}"
