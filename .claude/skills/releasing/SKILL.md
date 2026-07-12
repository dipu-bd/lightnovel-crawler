---
name: releasing
description: How lncrawl (lightnovel-crawler) releases work — version bump, tag-triggered release pipeline, changelog, per-OS builds, PyPI, Docker, web sync. Use when cutting a release, editing workflows, or debugging CI.
---

# Releasing lightnovel-crawler

There is **no version-bump GitHub workflow** — bumping is local and the release is triggered
by pushing a `v*` tag.

## The chain

```
make major|minor|patch        # scripts/bump.py edits lncrawl/VERSION only
<fill in CHANGELOG.md>        # add a "## [x.y.z]" section matching lncrawl/VERSION
make push-tag                 # tags v$(VERSION) and pushes → fires release.yml
```

`release.yml` (on tag `v*`) then runs, in dependency order:

1. **validate** — reuses `lint.yml` with the live crawl test enabled.
2. **sync-web** — reuses `web.yml` to pull the latest web build.
3. **build-docker** — reuses `build-docker.yml` (multi-arch → ghcr.io, tagged `latest`, the
   SHA, and the VERSION).
4. **create-release** — slices the matching version section out of `CHANGELOG.md` and creates
   a **draft** GitHub release.
5. **build-windows / build-mac / build-linux** — wheel + PyInstaller exe per OS (Windows also
   runs Inno Setup for the installer; Linux also uploads the wheel); artifacts attach to the
   draft release.
6. **publish-package** — publishes the wheel to PyPI, updates short links, and flips the
   release from draft to published.

## Supporting workflows

- **`lint.yml`** — CI on push/PR touching `lncrawl/**`, `sources/**`, or dependency files:
  lint (pyright + ruff), wheel build + install smoke test, `sources list`, and
  `dev migrate verify` (schema-drift gate). A live crawl test is opt-in via input/dispatch.
- **`web.yml`** ("Sync Web") — on `repository_dispatch: web-build-updated` from the
  lncrawl-web repo (or manual/`workflow_call`): checks out lncrawl-web's `artifacts` branch
  into `lncrawl/server/web/` and auto-commits to `dev`. That directory is committed build
  output — **never hand-edit it**.
- **`index-gen.yml`** — on `dev` pushes touching `sources/**` or the index scripts: runs
  `scripts/index_gen.py` and auto-commits the regenerated `sources/_index.json`/`.zip` and
  README source tables.

## Changelog & README

- `CHANGELOG.md` sections are curated by hand; the release step extracts the section whose
  heading matches `lncrawl/VERSION` for the release notes. `scripts/changelog_gen.py` is a
  manual maintainer tool that back-fills missing sections from GitHub Releases.
- `README.md` regions between `<!-- auto generated ... -->` markers (source tables, CLI help)
  are rewritten by `scripts/index_gen.py` — never hand-edit them.

## Packaging notes

- PyInstaller via `setup_pyi.py`: `--onedir` on Windows, `--onefile` elsewhere. It bundles the
  whole `sources/` tree as data **and** force-imports every source module so dynamically
  loaded crawlers survive freezing — a new top-level data dependency may need adding there.
- Inno Setup (`installer/installer.iss`): the **AppId GUID must never change** — it identifies
  the app for upgrades/uninstalls. Install is per-user (`PrivilegesRequired=lowest`). The
  doubled `{{` in the AppId is Inno's escape for a literal brace — don't "fix" it.
