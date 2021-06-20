# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.2] - 2021-06-20
### Fixed
- #12 Doing multi-injection multiple times causes the injected image to be corrupted.

## [1.3.1] - 2021-05-19
### Fixed
- Workaround to reduce the probability to treat non-CAI data as CAI metadata.

## [1.3.0] - 2021-03-03
### Added
- Make the `starling` submodule to be importable.
- Add "hello world" example for the `starling` submodule usage.
- Merge `signature` PR to support CMS and CAdES-B signature standards.

### Changed
- Update dependency from `pycrypto` to `pycryptodome`.

### Removed
- Section about "changelog" vs "CHANGELOG".

[Unreleased]: https://github.com/olivierlacan/keep-a-changelog/compare/v1.3.2...HEAD
[1.3.2]: https://github.com/numbersprotocol/starling-cai/compare/v1.3.0...v1.3.2
[1.3.1]: https://github.com/numbersprotocol/starling-cai/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/numbersprotocol/starling-cai/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/numbersprotocol/starling-cai/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/numbersprotocol/starling-cai/compare/v1.1.4...v1.2.0
[1.1.4]: https://github.com/numbersprotocol/starling-cai/compare/v1.1.3...v1.1.4
[1.1.3]: https://github.com/numbersprotocol/starling-cai/releases/tag/v1.1.3
