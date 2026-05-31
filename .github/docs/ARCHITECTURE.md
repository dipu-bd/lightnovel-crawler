# Setting Up CI on Forks

This guide explains how GitHub Actions workflows work on forks of lightnovel-crawler.

## Full Validation on All Repositories

All workflows are designed to provide full validation on forks, following the principle: **Anyone can validate, only authorized repos can publish**.

### What Runs on Forks

| Capability         | Main Repo               | Forks                |
| ------------------ | ----------------------- | -------------------- |
| Lint/validation    | Yes                     | Yes                  |
| Build executables  | Yes                     | Yes                  |
| Download artifacts | Yes                     | Yes                  |
| GitHub Releases    | Yes                     | No                   |
| Docker push        | Yes (lncrawl namespace) | Yes (fork namespace) |
| PyPI publish       | Yes                     | No                   |

## Workflows Overview

### Lint & Test (No Setup Required)

These workflows run automatically on pushes and pull requests:

| Workflow             | File          | Description                                   |
| -------------------- | ------------- | --------------------------------------------- |
| Lint & Test (Python) | `lint.yml` | Runs ruff, builds wheel, tests installation |

### Other Workflows

- **`build-server.yml`** – Builds and pushes the server Docker image (main repo only).
- **`docker-base.yml`** – Builds the Calibre base image for multi-arch.
- **`index-gen.yml`** – Generates source search index (main repo).

### Build and Publish (`release.yml`)

Triggered by version tags (`v*`). On forks, this workflow:

1. **Validates** the build across multiple Python versions
2. **Builds executables** for Windows, macOS, and Linux
3. **Uploads artifacts** - downloadable from the Actions tab
4. **Builds and pushes Docker image** to your fork's GHCR namespace

The following steps only run on the main repository:

- GitHub Release creation
- PyPI package publishing
- Short link updates (SHLINK)

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

```bash
docker pull ghcr.io/<your-username>/lightnovel-crawler:latest
docker run --rm ghcr.io/<your-username>/lightnovel-crawler lncrawl --version
```

## Optional: Publishing to PyPI from Your Fork

If you want to publish releases from your fork to PyPI:

1. Go to your fork's **Settings** > **Secrets and variables** > **Actions**
2. Add the following secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token

Note: You'll need to modify the workflow condition or publish under a different package name on PyPI.

## Server Deployment

The deploy workflow is designed for the main project's infrastructure. For your own deployment:

1. Modify `scripts/server-compose.yml` with your configuration
2. Add your deployment secrets:
   - `SSH_SECRET`: Private SSH key for deployment server
   - `SSH_HOST`: Hostname of your deployment server
   - `DEPLOY_SERVER`: SSH connection string (e.g., `user@host`)

## Testing Releases on Your Fork

To test the full release pipeline:

```bash
# Create a test tag
git tag v0.0.0-test
git push origin v0.0.0-test

# Verify in GitHub Actions:
# - All jobs run and pass
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

ARM64 builds use QEMU emulation and may take longer. If builds timeout:

1. The base image must be built for ARM64 first, if you are coming from older builds this may not be the case

## Questions?

If you encounter issues setting up CI on your fork, please open a discussion in the main repository.
