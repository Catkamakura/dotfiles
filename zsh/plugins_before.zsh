# External plugins (initialized before)

# zsh-completions
if [[ -d ~/.zsh/plugins/zsh-completions/src ]]; then
    typeset -U fpath
    fpath=(~/.zsh/plugins/zsh-completions/src $fpath)
fi
