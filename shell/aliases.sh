# Use colors in coreutils utilities output
if command ls --color=auto -d . >/dev/null 2>&1; then
    alias ls='ls --color=auto'
else
    alias ls='ls -G' # BSD/macOS
fi
alias grep='grep --color=auto'

# ls aliases
alias ll='ls -lah'
alias la='ls -A'
alias l='ls'

# Aliases to protect against overwriting
alias cp='cp -i'
alias mv='mv -i'

# git related aliases
alias gag='git exec ag'

# Update dotfiles
dfu() {
    (
        cd ~/.dotfiles && git pull --ff-only && ./install
    )
}

# Use pip without requiring virtualenv
syspip() {
    PIP_REQUIRE_VIRTUALENV="" pip "$@"
}

syspip2() {
    PIP_REQUIRE_VIRTUALENV="" pip2 "$@"
}

syspip3() {
    PIP_REQUIRE_VIRTUALENV="" pip3 "$@"
}

# cd to git root directory
cdgr() {
    local root
    root=$(git rev-parse --show-toplevel) || return
    cd -- "$root" || return
}

# Create a directory and cd into it
mcd() {
    [[ $# -eq 1 ]] || return 2
    mkdir -p -- "$1" && cd -- "$1" || return
}

# Jump to directory containing file
jump() {
    [[ $# -eq 1 ]] || return 2
    cd -- "$(dirname -- "$1")" || return
}

# cd replacement for screen to track cwd (like tmux)
scr_cd()
{
    builtin cd "$@" || return
    screen -X chdir "$PWD"
}

if [[ -n $STY ]]; then
    alias cd=scr_cd
fi

# Go up [n] directories
up()
{
    local cdir=$PWD i
    if [[ "${1}" == "" ]]; then
        cdir="$(dirname "${cdir}")"
    elif [[ $1 == *[!0-9]* ]]; then
        echo "Error: argument must be a number" >&2
        return 2
    elif [[ -z ${1//0/} ]]; then
        echo "Error: argument must be positive" >&2
        return 2
    else
        local count=$((10#$1)) ncdir
        for ((i=0; i<count; i++)); do
            ncdir="$(dirname "${cdir}")"
            if [[ "${cdir}" == "${ncdir}" ]]; then
                break
            else
                cdir="${ncdir}"
            fi
        done
    fi
    cd -- "${cdir}" || return
}

# Execute a command in a specific directory
xin() {
    (
        cd "${1}" && shift && "${@}"
    )
}

# Check if a file contains non-ascii characters
nonascii() {
    LC_ALL=C grep -n '[^[:print:][:space:]]' "${@}"
}

# Fetch pull request

fpr() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "error: fpr must be executed from within a git repository"
        return 1
    fi
    (
        cdgr || return
        if [ "$#" -eq 1 ]; then
            local repo="${PWD##*/}"
            local user="${1%%:*}"
            local branch="${1#*:}"
        elif [ "$#" -eq 2 ]; then
            local repo="${PWD##*/}"
            local user="${1}"
            local branch="${2}"
        elif [ "$#" -eq 3 ]; then
            local repo="${1}"
            local user="${2}"
            local branch="${3}"
        else
            echo "Usage: fpr [repo] username branch"
            return 1
        fi

        git fetch "git@github.com:${user}/${repo}" "${branch}:${user}/${branch}"
    )
}

# Serve current directory

serve() {
    ruby -run -e httpd . -p "${1:-8080}"
}

# Mirror a website
alias mirrorsite='wget -m -k -K -E -e robots=off'

# Mirror stdout to stderr, useful for seeing data going through a pipe
alias peek='tee >(cat 1>&2)'
