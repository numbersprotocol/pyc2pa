# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.0] - 2021-11-29
### Added
- Add support for PS256 signature.

## [2.0.0] - 2021-10-18
### Changed
- Change the implementation to be C2PA draft v0.7.0 compatible.

## [1.4.0] - 2021-09-02
### Changed
- Update materials from CAI to C2PA.

## [1.3.3] - 2021-08-26
### Fixed
- [#17](https://github.com/numbersprotocol/starling-cai/issues/17) Fail to pass signature verification

## [1.3.2] - 2021-06-20
### Fixed
- [#12](https://github.com/numbersprotocol/starling-cai/issues/12) Doing multi-injection multiple times causes the injected image to be corrupted
- [#15](https://github.com/numbersprotocol/starling-cai/issues/15) Can not support using copy of raw photo as thumbnail for some photos

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

[Unreleased]: https://github.com/numbersprotocol/starling-cai/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/numbersprotocol/starling-cai/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/numbersprotocol/starling-cai/compare/v1.4.0...v2.0.0
[1.4.0]: https://github.com/numbersprotocol/starling-cai/compare/v1.3.3...v1.4.0
[1.3.3]: https://github.com/numbersprotocol/starling-cai/compare/v1.3.2...v1.3.3
[1.3.2]: https://github.com/numbersprotocol/starling-cai/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/numbersprotocol/starling-cai/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/numbersprotocol/starling-cai/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/numbersprotocol/starling-cai/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/numbersprotocol/starling-cai/compare/v1.1.4...v1.2.0
[1.1.4]: https://github.com/numbersprotocol/starling-cai/compare/v1.1.3...v1.1.4
[1.1.3]: https://github.com/numbersprotocol/starling-cai/releases/tag/v1.1.3
