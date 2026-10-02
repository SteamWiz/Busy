# Designed to be sourced. We wrap ZSHRC tricks around this.
VIRTUAL_ENV_DISABLE_PROMPT=1 source .venv/bin/activate

alias play="python -m busy --config sandbox/config.yml"
alias real="python -m busy"