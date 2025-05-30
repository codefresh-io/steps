# Changelog
## [1.5.0] - 2025-01-29
### Changed
- Add APP_NAMESPACE option (supported from app-proxy v1.2600.1)

## [1.4.5] - 2024-04-04
### Fixed
- fixing CVEs
- upgrade requirements.txt
- install Python modules locally

## [1.4.4] - 2024-03-07
### Fixed
- Do not sync an application in auto-sync mode
- Check for application existence before anything is done

## [1.4.3] - 2024-02-22
### Fixed
- Intercepting application not found for better error message

### Changed
- Move the creation of the link to the application earlier
- Exit with error when app is in OUT_OF_SYNC state

## [1.4.2] - 2024-01-17
### Changed
- New graphql call to speed up query

## [1.4.1] - 2023-10-31
### Changed
- Add CA_BUNDLE option

## [1.4.0] - 2023-10-30
### Changed
- Add INSECURE option

## [1.3.1] - 2023-09-18
### Fixed
- CVE-2023-37920 - upgrade Python module certifi to 2023.7.22
- CVE-2019-8457 - upgrade base image to python:3.11.5-slim-bookworm

## [1.3.0] - 2023-05-19
### Changed
- Adding IMAGE_NAME parameter
- Adding example
