path_remove() {
    [[ $# -eq 1 ]] || return 2
    local remaining=$PATH entry result='' separator=''
    while :; do
        entry=${remaining%%:*}
        if [[ $entry != "$1" ]]; then
            result="${result}${separator}${entry}"
            separator=:
        fi
        [[ $remaining == *:* ]] || break
        remaining=${remaining#*:}
    done
    export PATH="$result"
}

path_append() {
    [[ $# -eq 1 && -n $1 ]] || return 2
    path_remove "$1" || return
    export PATH="${PATH:+"$PATH:"}$1"
}

path_prepend() {
    [[ $# -eq 1 && -n $1 ]] || return 2
    path_remove "$1" || return
    export PATH="$1${PATH:+":$PATH"}"
}

here() {
    local loc
    if [ "$#" -eq 1 ]; then
        loc=$(realpath "$1") || return
    else
        loc=$(realpath ".") || return
    fi
    ln -sfn "${loc}" "$HOME/.shell.here" || return
    printf 'here -> %s\n' "$loc"
}

there="$HOME/.shell.here"

there() {
    local destination
    destination=$(readlink "${there}") || return
    cd -- "$destination" || return
}
