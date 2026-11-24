#!/bin/zsh
# Kept for existing instructions. The Basilisk source is committed with this
# project and is no longer downloaded: build it with the main script.
exec zsh "$(dirname -- "$0")/reset_install_requirements.sh" "$@"
