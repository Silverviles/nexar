# =============================================================================
# Nexar — Backend Launcher (separate terminal per service)
#
# Opens each backend service in its own Command Prompt window (via `start`),
# so you get independent, scrollable logs and can Ctrl+C one service without
# killing the others. Assumes dependencies are already installed
# (run: bash setup-dev.sh).
#
# Usage:
#   make backend                  # Start all 5 backend services, each in its own window
#   make api                      # Start just the api service
#   make ai-code-converter        # Start just this one service
#   make code-analysis-engine
#   make decision-engine
#   make hardware-abstraction-layer
#
# Notes:
#   - Paths passed to `cmd start` MUST use backslashes: cmd's argument parser
#     mis-reads a bare "/r" inside a forward-slash path as a switch (e.g.
#     ".../scripts/run-service.sh" gets silently mangled to "un-service.sh"),
#     even when quoted. $(subst) below converts the MSYS forward-slash CURDIR
#     to a Windows-style path to avoid that.
#   - We invoke Git Bash by its full path rather than bare `bash`: Windows
#     also registers WSL's bash.exe as an App Execution Alias, which can
#     shadow Git Bash when cmd.exe resolves "bash" on PATH.
# =============================================================================

GITBASH := C:\Program Files\Git\bin\bash.exe
ROOT_WIN := $(subst /,\,$(CURDIR))
RUN := $(ROOT_WIN)\scripts\run-service.sh

.PHONY: backend ai-code-converter code-analysis-engine decision-engine hardware-abstraction-layer api

backend: ai-code-converter code-analysis-engine decision-engine hardware-abstraction-layer api

ai-code-converter:
	cmd.exe /c start "ai-code-converter (8001)" "$(GITBASH)" "$(RUN)" ai-code-converter

code-analysis-engine:
	cmd.exe /c start "code-analysis-engine (8002)" "$(GITBASH)" "$(RUN)" code-analysis-engine

decision-engine:
	cmd.exe /c start "decision-engine (8003)" "$(GITBASH)" "$(RUN)" decision-engine

hardware-abstraction-layer:
	cmd.exe /c start "hardware-abstraction-layer (8004)" "$(GITBASH)" "$(RUN)" hardware-abstraction-layer

api:
	cmd.exe /c start "api (3000)" "$(GITBASH)" "$(RUN)" api
