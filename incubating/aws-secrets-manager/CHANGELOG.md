# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [1.0.1] - 2021-10-01
### Changed
- Added support for reading from IAM role
- Remove unset environment variables from Dockerfile

## [1.0.0] - 2021-07-23
### Changed
- Add proper support for optional AWS IAM role ARN.

### Fixed
- Handle failure when `AWS_IAM_ROLE_ARN` input parameter is omitted entirely.

## [0.0.3] - 2020-07-01
### Added
- Cache fetched secrets.

## [0.0.2] - 2020-05-08
### Changed
- Export environment variables directly from within the custom step. The additional freestyle step to export the variables is no longer necessary.

## [0.0.1] - 2020-01-06
### Added
- Core functionality to fetch secrets from AWS Secrets Manager.
