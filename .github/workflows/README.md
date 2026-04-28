# Release workflows

This repository now uses two GitHub Actions workflows for PyPI releases:

- [build-package.yml](./build-package.yml) validates a version bump automatically.
- [publish-pypi.yml](./publish-pypi.yml) publishes to PyPI when a maintainer starts it manually.
- [github-release.yml](./github-release.yml) creates a GitHub Release from a tag.

## What triggers it

`build-package.yml` starts when `version.txt` changes on `main` or `master`.

`publish-pypi.yml` only starts when someone runs it manually from the GitHub Actions tab.

`github-release.yml` starts when a release tag is pushed, and it can also be run manually.

## Why there are two workflows

- The build workflow gives fast feedback that the package can be built and validated.
- The publish workflow is the manual checkpoint before anything is uploaded to PyPI.

This is the fallback design for repositories where you cannot manage a protected GitHub
Environment. It replaces environment approval with a separate manual publish action.

The GitHub Release workflow stays separate from PyPI publishing so a release page can be
managed independently of package publishing.

## Required GitHub setup

1. Add `PYPI_API_TOKEN` as a repository secret in the repository settings.
2. Use the build workflow to confirm a version bump builds cleanly.
3. Run the publish workflow manually and choose the git ref you want to release.

## How manual publish works

When you run `publish-pypi.yml`, GitHub asks for a `ref` input.

That `ref` can be:

- a branch name such as `main`
- a tag such as `v2.1.0`
- a commit SHA for an exact commit

The workflow checks out that ref, rebuilds the package from that source, validates it,
and then uploads it to PyPI using `PYPI_API_TOKEN`.

## How GitHub release works

`github-release.yml` is focused on GitHub Releases, not PyPI.

When a supported tag is pushed, the workflow:

- extracts the tag name and release version
- checks that `version.txt` matches the tag version
- builds and validates the package
- creates or updates the GitHub Release
- uploads the built `dist/` files as release assets

Pre-release tags such as `2.1.0b1` or `v2.1.0rc1` are marked as GitHub pre-releases
automatically.

## Version source of truth

`setup.py` now reads the package version from the top-level `version.txt` file.

That matters because the workflow is triggered by `version.txt`. If `version.txt` changes but
the package metadata does not, PyPI publish would likely fail due to a duplicate version.
