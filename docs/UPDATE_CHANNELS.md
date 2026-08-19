# Update Channels

## Nightly

A Nightly is a release that has finished building but has not successfully completed the post-release verification workflow.

States represented by the release body:

- `verification:pending`
- `verification:failed`

Nightlies are GitHub prereleases.

## Verified

A release becomes Verified only after the release-triggered test workflow passes. GitHub then marks it as a normal non-prerelease and the body contains `verification:passed`.

## Desktop updater

The desktop client reads GitHub Releases using `rl_client.update.github.GitHubReleaseClient`.

- `verified` selects the newest non-prerelease.
- `nightly` selects the newest prerelease.

For public repositories the update check does not require a user API token.
