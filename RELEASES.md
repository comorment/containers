# Releases

Notes related to (making) releases.
This document is not for tracking [changes](CHANGELOG.md).

## Checklist

- Stick to the [semantic versioning scheme](https://semver.org), with the `<MAJOR>.<MINOR>.<PATCH>` numbering [scheme](https://semver.org/#summary) with possible extensions.
- Every merged PR should bump the version info in ``version/version.py`` depending on the nature of the change (minor fix means bumping `<PATCH>` and so forth).
  Reset the lesser version number (e.g., `<PATCH>`) if the higher version level is incremented (e.g, `<MINOR>`).
- [cosgap.readthedocs.io](https://cosgap.rtfd.io) should trigger docs builds automatically with each merged PR.
- Make sure that the [CHANGELOG](CHANGELOG.md) is kept up to date.
- Create a tag for each change in version (excluding `dev`,`rc#` extensions, and similar).
  This can be done by issuing (post merge):
  ```
  git pull
  git tag -a v<MAJOR>.<MINOR>.<PATCH> -m "Release v<MAJOR>.<MINOR>.<PATCH>"
  git push --tags
  ```
- Each new tag warrants a new release. This is presently done via [Draft new release](https://github.com/comorment/containers/releases/new).
  Here, choose the corresponding tag ID and Target, and set the appropriate title as `CoMorMent-Containers-v<MAJOR>.<MINOR>.<PATCH>`.
  Press the "Generate release notes" to list changes since the last appropriate tag (e.g., `v<MAJOR>.<MINOR>` for a bump to `<PATCH>`, and similar).
  Then, press "Publish release".
- New releases should trigger Zenodo.org code deposit automatically at [https://doi.org/10.5281/zenodo.7385620](https://doi.org/10.5281/zenodo.7385620).
- Sync github.com/comorment/containers to TSD p697 project, following steps outlined [here](https://github.com/comorment/containers/issues/174)
