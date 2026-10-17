# dircolors
if command -v dircolors >/dev/null 2>&1 &&
        [[ -r ~/.shell/plugins/dircolors-solarized/dircolors.256dark ]] &&
        [[ "$(tput colors 2>/dev/null)" -ge 256 ]]; then
    eval "$(dircolors -b ~/.shell/plugins/dircolors-solarized/dircolors.256dark)"
fi
