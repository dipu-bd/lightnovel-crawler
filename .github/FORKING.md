# Setting Up CI on Forks

This guide explains how GitHub Actions workflows work on forks of lightnovel-crawler.

## Full Validation on All Repositories

All workflows are designed to provide full validation on forks, following the principle: **Anyone can validate, only authorized repos can publish**.

### What Runs on Forks

| Capability         | Main Repo               | Forks                  |
| ------------------ | ----------------------- | ---------------------- |
| Lint/validation    | Yes                     | Yes                    |
| Build executables  | Yes                     | Yes                    |
| Download artifacts | Yes                     | Yes                    |
| GitHub Releases    | Yes                     | Yes (in your own fork) |
| Docker push        | Yes (lncrawl namespace) | Yes (fork namespace)   |
| PyPI publish       | Yes                     | No                     |
| Short links        | Yes                     | No                     |

## Workflows Overview

### Lint & Test (No Setup Required)

These workflows run automatically on pushes and pull requests:

| Workflow             | File       | Description                                                                                                       |
| -------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------- |
| Lint & Test (Python) | `lint.yml` | pyright + ruff on every supported Python version, then builds the wheel, installs it, and checks for schema drift |

The live crawl test is off by default; it runs when the workflow is dispatched manually or a
caller asks for it.

### Build and Publish (`release.yml`)

Triggered by version tags (`v*`). On forks, this workflow:

1. **Validates** the build across every supported Python version
2. **Builds executables** for Windows, macOS, and Linux
3. **Uploads artifacts** - downloadable from the Actions tab
4. **Attaches them to a draft release** in your own fork
5. **Builds and pushes Docker image** to your fork's GHCR namespace

The `publish-package` job is guarded by `if: github.repository == 'lncrawl/lightnovel-crawler'`
and is skipped everywhere else, so a fork never reaches:

- PyPI package publishing
- Short link updates (SHLINK)
- Flipping the draft release to published

### Downloading Build Artifacts

After a successful release workflow run on your fork:

1. Go to **Actions** tab in your fork
2. Click on the completed workflow run
3. Scroll to **Artifacts** section
4. Download:
   - `lncrawl-windows` - Windows executable
   - `lncrawl-mac` - macOS executable
   - `lncrawl-linux` - Linux executable and wheel package

## Docker Image Publishing

Docker images automatically push to your fork's namespace:

- **Main repo**: `ghcr.io/lncrawl/lightnovel-crawler`
- **Your fork**: `ghcr.io/<your-username>/lightnovel-crawler`

This works automatically with the default `GITHUB_TOKEN` - no additional setup required.

### Viewing Your Docker Images

1. Go to your GitHub profile
2. Click on **Packages** tab
3. Find `lightnovel-crawler` image

### Using Your Fork's Image

The image entrypoint is `lncrawl` itself, so pass it a command directly:

```bash
docker pull ghcr.io/<your-username>/lightnovel-crawler:latest
docker run --rm ghcr.io/<your-username>/lightnovel-crawler version
```

## Optional: Publishing to PyPI from Your Fork

The `publish-package` job is skipped on forks by a repository check. To publish from your own
fork you would have to:

1. Change or drop that `if:` condition in `release.yml`
2. Pick a different package name in `pyproject.toml` — `lightnovel-crawler` is taken
3. Configure PyPI Trusted Publishing for your fork, or switch the publish step to an API token
   passed under `with:` rather than `env:`

## Server Deployment

There is no deploy workflow — the main project deploys out of band.
[`scripts/server-compose.yml`](../scripts/server-compose.yml) is the compose file it uses, and
it is a reasonable starting point for hosting your own instance.

## Testing Releases on Your Fork

To test the full release pipeline:

```bash
# Create a test tag
git tag v0.0.0-test
git push origin v0.0.0-test

# Verify in GitHub Actions:
# - Every job passes, except PyPI Publish, which is skipped on forks by design
# - Artifacts are available for download
# - Docker image appears in your Packages

# Clean up
git tag -d v0.0.0-test
git push origin :v0.0.0-test
```

## Common Issues

### Workflow Won't Run

1. Ensure GitHub Actions is enabled in your fork's Settings
2. Check that the workflow file hasn't been modified to break triggers
3. Verify that the paths filter matches your changes (for path-filtered workflows)

### Build Fails on ARM64

Each architecture builds natively on its own runner — `linux/amd64` on `ubuntu-latest` and
`linux/arm64` on `ubuntu-24.04-arm` — and a manifest is merged from the two digests afterwards.
If the arm64 leg fails on its own, check that your fork can schedule ARM runners; the image
also downloads Firefox per architecture at build time, so a Mozilla download failure fails only
that leg.

## Questions?

If you encounter issues setting up CI on your fork, please open a discussion in the main repository.
