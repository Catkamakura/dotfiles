# Initialize completion
autoload -Uz compinit && compinit -i
zstyle ':completion:*' menu select=4
zmodload zsh/complist
# Use vim style navigation keys in menu completion
bindkey -M menuselect 'h' vi-backward-char
bindkey -M menuselect 'k' vi-up-line-or-history
bindkey -M menuselect 'l' vi-forward-char
bindkey -M menuselect 'j' vi-down-line-or-history

# Initialize editing command line
autoload -U edit-command-line && zle -N edit-command-line

# Enable interactive comments (# on the command line)
setopt interactivecomments

# Nicer history
HISTSIZE=1048576
HISTFILE="$HOME/.zsh_history"
SAVEHIST=$HISTSIZE
setopt appendhistory
setopt incappendhistory
setopt extendedhistory
setopt histignorespace

# Allow escape sequences to arrive in separate SSH packets (hundredths of a
# second). A 10ms timeout can turn paste markers into vi commands.
KEYTIMEOUT=${DOTFILES_KEYTIMEOUT:-40}

# Use vim style line editing in zsh
bindkey -v

# Treat terminal pastes as literal text in either vi mode. Finish in insert
# mode so typing after a paste cannot accidentally execute vi commands.
zle_bracketed_paste=($'\e[?2004h' $'\e[?2004l')
_dotfiles_bracketed_paste() {
    if [[ $KEYMAP == vicmd ]]; then
        zle vi-insert
    fi
    zle .bracketed-paste
}
zle -N _dotfiles_bracketed_paste

# Some terminal/multiplexer combinations send a trailing marker without a
# matching start. Otherwise its Escape enters command mode and ~ flips case.
_dotfiles_paste_end() { :; }
zle -N _dotfiles_paste_end
for _dotfiles_keymap in viins vicmd emacs; do
    bindkey -M "$_dotfiles_keymap" $'\e[200~' _dotfiles_bracketed_paste
    bindkey -M "$_dotfiles_keymap" $'\e[201~' _dotfiles_paste_end
done
unset _dotfiles_keymap

# Movement
bindkey -a 'gg' beginning-of-buffer-or-history
bindkey -a 'G' end-of-buffer-or-history
# Undo
bindkey -a 'u' undo
bindkey -a '^R' redo
# Edit line
bindkey -a '^V' edit-command-line
# Backspace
bindkey '^?' backward-delete-char
bindkey '^H' backward-delete-char

# Use incremental search
bindkey "^R" history-incremental-search-backward

# Disable shell builtins
disable r
