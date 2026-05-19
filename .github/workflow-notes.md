# Workflow Notes

This file documents the release workflows in `.github/workflows/pypi.yml` and
`.github/workflows/github-release-v2.yml`.

## Shared Release Inputs

Both workflows use `version.txt` as the release version source. The workflows
strip newline characters from `version.txt` and use the resulting value as the
package or release version.

Version values that contain any letters are treated as prereleases. For example,
`1.2.0rc1`, `1.2.0a1`, and `1.2.0b1` are prereleases. Versions like `1.2.0`
are treated as normal releases.

Both workflows use the package name `quest-snl`.

## Publish to PyPI

Workflow file: `.github/workflows/pypi.yml`

Workflow name: `Publish to PyPI`

### When It Runs

This workflow runs automatically when `version.txt` changes on `main` or
`master`.

It can also be started manually with `workflow_dispatch`. The manual run includes
an `include_prerelease` boolean input. Leave this set to `false` for normal
releases. Set it to `true` when the version in `version.txt` is a prerelease and
you want to publish it to PyPI.

### Required Repository Setup

The `release` environment must exist in GitHub if environment protection rules
are used.

The repository or `release` environment must define this secret:

- `PYPI_API_TOKEN`: PyPI API token used by
  `pypa/gh-action-pypi-publish`.

### What It Does

The `check-version` job reads `version.txt`, exposes the package name, and
detects whether the version is a prerelease.

The `publish` job only runs when either:

- the version is not a prerelease, or
- the workflow was started manually with `include_prerelease` set to `true`.

The publish job checks out the repository, installs Python 3.13, removes old
egg-info metadata, copies `version.txt` into `quest/version.txt`, clears
generated contents under `quest/app_envs`, installs build tools, builds a wheel,
checks the built distribution with Twine, and publishes the result to PyPI.

The publish step uses `skip-existing: true`, so rerunning the workflow will not
fail just because the same package version already exists on PyPI.

## GitHub Release

Workflow file: `.github/workflows/github-release-v2.yml`

Workflow name: `GitHub Release`

### When It Runs

This workflow runs automatically when `version.txt` changes on `main` or
`master`.

### Required Repository Files

The workflow expects these files to exist:

- `version.txt`: release version and tag name.
- `.github/release-notes.md`: release body used for the GitHub release.
- `.github/scripts/install.sh`: macOS installer copied into the macOS package.
- `.github/scripts/install.bat`: Windows installer copied into the Windows
  package.

### Permissions

The workflow requires `contents: write` so it can create or update the GitHub
release and upload release assets.

### What It Does

The `prepare-release` job reads `version.txt` and exposes shared release
metadata:

- `tag_name`: exact version from `version.txt`.
- `pkg_name`: `quest-snl`.
- `release_name`: `QuESt <version>`.
- `prerelease`: `true` when the version contains letters, otherwise `false`.

The `build-source` job verifies that source distributions can be built. It
installs Python 3.13 and build tooling, builds ZIP and TAR.GZ source
distributions, extracts the ZIP archive, and confirms the build completed.

The `build-macos` job builds a macOS release ZIP on `macos-latest`. It creates a
source ZIP, extracts it, copies `.github/scripts/install.sh` into the extracted
package, marks the installer executable, repackages the result as:

```text
quest-snl-<version>-macos.zip
```

The `build-windows` job builds a Windows release ZIP on `windows-latest`. It
creates a source ZIP, extracts it, copies `.github/scripts/install.bat` into the
extracted package, and repackages the result as:

```text
quest-snl-<version>-windows.zip
```

The `release` job downloads the macOS and Windows build artifacts, then publishes
a GitHub release with `softprops/action-gh-release@v2`. The release tag is the
version from `version.txt`, the release title is `QuESt <version>`, and the body
comes from `.github/release-notes.md`.

The release assets are:

- `quest-snl-<version>-windows.zip`
- `quest-snl-<version>-macos.zip`

If the version contains letters, the GitHub release is marked as a prerelease.

## Release Checklist 

Before changing `version.txt`, update `.github/release-notes.md` with the notes
for the new release.

For a normal release, set `version.txt` to a version with no letters, such as
`1.2.0`, then push the change to `main` or `master`.

For a prerelease, set `version.txt` to a version that includes letters, such as
`1.2.0rc1`. The GitHub release workflow will mark it as a prerelease. The
PyPI workflow will only publish it if manually run with `include_prerelease`
set to `true`.
