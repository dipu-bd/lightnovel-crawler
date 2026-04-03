# =============================================================================
# Lightnovel Crawler — developer tasks (uv, git, docker)
# =============================================================================

.PHONY: all \
	version submodule clean ensure-uv setup sync install upgrade \
	major minor patch \
	lint lint-fixstart watch add-source index-gen \
	build-wheel build-exe build \
	docker-base docker-build docker-up docker-down docker-logs \
	remove-tag push-tag push-tag-force \
	add-dep add-dev rm-dep rm-dev

# --- uv executable (PATH, else default install location) ---------------------
ifeq ($(OS),Windows_NT)
  PS := powershell -NoProfile -Command
  VERSION := $(shell $(PS) "(Get-Content lncrawl/VERSION).Trim()")
  UV := $(shell $(PS) "if (Get-Command uv -ErrorAction SilentlyContinue) { (Get-Command uv).Source } else { Join-Path $$env:USERPROFILE '.local\bin\uv.exe' }")
else
  VERSION := $(shell cat lncrawl/VERSION | tr -d '\n')
  UV := $(shell command -v uv 2>/dev/null || echo "$(HOME)/.local/bin/uv")
endif

# Same flags everywhere so `add-dep` / `install` / `sync` match.
UV_SYNC_FLAGS := --all-extras --all-groups

# Package name for: make add-dep <pkg>  (second goal; see %-catchall below)
ifneq ($(filter add-dep add-dev rm-dep rm-dev,$(MAKECMDGOALS)),)
  PKG := $(word 2,$(MAKECMDGOALS))
endif

# =============================================================================
# Default
# =============================================================================

all: install

# =============================================================================
# Git — info, submodules, release tags
# =============================================================================

version:
	@echo Lightnovel Crawler: $(VERSION)

submodule:
	@git submodule sync
	@git submodule update --force --init --recursive --remote

remove-tag:
	git diff --exit-code HEAD
	git push --delete origin "v$(VERSION)"
	git tag -d "v$(VERSION)"

push-tag:
	git diff --exit-code HEAD
	git tag "v$(VERSION)"
	@git push --tags

push-tag-force: remove-tag push-tag

# =============================================================================
# Cleanup
# =============================================================================

clean:
ifeq ($(OS),Windows_NT)
	@powershell -Command "try { Remove-Item -ErrorAction SilentlyContinue -Recurse -Force .venv, logs, build, dist } catch {}; exit 0"
	@powershell -Command "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter '*.egg-info' | Remove-Item -Recurse -Force"
	@powershell -Command "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"
else
	@rm -rf .venv logs build dist
	@find . -depth -name '*.egg-info' -type d -exec rm -rf '{}' \; 2>/dev/null || true
	@find . -depth -name '__pycache__' -type d -exec rm -rf '{}' \; 2>/dev/null || true
endif

# =============================================================================
# uv — bootstrap & version file (X.Y.Z)
# =============================================================================

ensure-uv:
ifeq ($(OS),Windows_NT)
	@$(UV) --version || powershell -NoProfile -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
else
	@$(UV) --version || curl -LsSf https://astral.sh/uv/install.sh | sh
endif

major: ensure-uv
	@$(UV) run python ./scripts/bump.py major

minor: ensure-uv
	@$(UV) run python ./scripts/bump.py minor

patch: ensure-uv
	@$(UV) run python ./scripts/bump.py patch

setup: submodule ensure-uv

sync:
	$(UV) sync $(UV_SYNC_FLAGS)

install: setup sync

upgrade: setup
	$(UV) sync --upgrade $(UV_SYNC_FLAGS)

# =============================================================================
# Python — lint, server, scaffolding
# =============================================================================

lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

lint-fix:
	$(UV) run ruff check --fix .

start:
	$(UV) run python -m lncrawl -ll server

watch:
	$(UV) run python -m lncrawl -ll server --watch

add-source:
	$(UV) run python -m lncrawl -ll sources create

index-gen:
	$(UV) run python scripts/index_gen.py
	
check-sources:
	$(UV) run python scripts/check_sources.py

# =============================================================================
# Build — wheel, PyInstaller
# =============================================================================

build-wheel:
	$(UV) run python -m build -w

build-exe:
	$(UV) run python setup_pyi.py

build: version install build-wheel build-exe

# =============================================================================
# Docker
# =============================================================================

docker-base:
	docker build -t lncrawl-base -f Dockerfile.base .

docker-build: docker-base
	docker build -t lncrawl --build-arg BASE_IMAGE=lncrawl-base .

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# =============================================================================
# Dependencies — usage: make add-dep <package>
# =============================================================================

add-dep: setup
	@test -n "$(PKG)" || (echo >&2 "Usage: make add-dep <package>"; exit 1)
	$(UV) add $(PKG)
	$(UV) sync $(UV_SYNC_FLAGS)

add-dev: setup
	@test -n "$(PKG)" || (echo >&2 "Usage: make add-dev <package>"; exit 1)
	$(UV) add --optional dev $(PKG)
	$(UV) sync $(UV_SYNC_FLAGS)

rm-dep: setup
	@test -n "$(PKG)" || (echo >&2 "Usage: make rm-dep <package>"; exit 1)
	$(UV) remove $(PKG)
	$(UV) sync $(UV_SYNC_FLAGS)

rm-dev: setup
	@test -n "$(PKG)" || (echo >&2 "Usage: make rm-dev <package>"; exit 1)
	$(UV) remove --optional dev $(PKG)
	$(UV) sync $(UV_SYNC_FLAGS)

# Ignore the second word (package name) as a nested target
%:
	@:
