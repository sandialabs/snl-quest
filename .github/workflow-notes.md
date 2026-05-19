# Workflows Details

## github-release.yml

### jobs:

#### prepare-release

```bash
version="$(tr -d '\r\n' < version.txt)"
```

- reads version.txt
- strips newline characters
- stores the result in version

```bash
echo "tag_name=$version" >> "$GITHUB_OUTPUT"
```

exposes the version as the Git tag name for later jobs

```bash
echo "release_name=QuESt $version" >> "$GITHUB_OUTPUT"
```

exposes a human-readable release title like QuESt 2.1.0

```bash
if echo "$version" | grep -Eq '[A-Za-z]'; then

```

checks whether the version contains any letters

```bash
echo "prerelease=true" >> "$GITHUB_OUTPUT"
```

if it contains letters, mark the GitHub release as a prerelease

```bash
echo "prerelease=false" >> "$GITHUB_OUTPUT"
```

otherwise mark it as a normal release
