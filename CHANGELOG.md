# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## Unreleased

<small>[Compare with latest](https://github.com/OpenDataGIS/ckanext-fototeca/compare/v1.2.0...HEAD)</small>

### Added

- Add site-footer bg color ([d28283b](https://github.com/OpenDataGIS/ckanext-fototeca/commit/d28283b24aedea574507b2cdeadba565870dc510) by mjanez).

<!-- insertion marker -->
## [v1.2.0](https://github.com/OpenDataGIS/ckanext-fototeca/releases/tag/v1.2.0) - 2024-10-17

<small>[Compare with first commit](https://github.com/OpenDataGIS/ckanext-fototeca/compare/9b8d349dfacb42d8cc387d7d075bb4adfe664e47...v1.2.0)</small>

### Added

- Add styling for module headings in fototeca.css ([c48dcdc](https://github.com/OpenDataGIS/ckanext-fototeca/commit/c48dcdc3e0c351ceb4eb9cb0c2f8ff4d1d71f7ed) by mjanez).
- Add WMS URL normalization and configuration for Fototeca ([a60fe76](https://github.com/OpenDataGIS/ckanext-fototeca/commit/a60fe76570692ae07cccb3fc1163831324a64cb7) by mjanez).
- Add hvd_category new categories ([15cdcf9](https://github.com/OpenDataGIS/ckanext-fototeca/commit/15cdcf936ae967da1d3aa8e47b89709eb6ce0a4c) by mjanez).
- Add normalize_fototeca_fields to postgres harvester ([e850d5b](https://github.com/OpenDataGIS/ckanext-fototeca/commit/e850d5bf8a1369ad1968e1b9c601477d72e35a89) by mjanez).
- Add config_declaration.yml to ckanext-fototeca ([2fa9037](https://github.com/OpenDataGIS/ckanext-fototeca/commit/2fa903759d1660edf79f46f03c9b14585d390993) by mjanez).
- Add FototecaCKANHarvest ([2fdb4dc](https://github.com/OpenDataGIS/ckanext-fototeca/commit/2fdb4dcc4b898ce7fa8b789e034efa71b5e33279) by mjanez).

### Fixed

- Fix flight_color values in FOTOTECA_CODELIST_MAPPING ([7a5b6ed](https://github.com/OpenDataGIS/ckanext-fototeca/commit/7a5b6ed855de4c553ce3ef9af304c5271639f146) by mjanez).
- Fix trans label and css ([8e7c0b2](https://github.com/OpenDataGIS/ckanext-fototeca/commit/8e7c0b25962819ecb5126051b379f44a8fb4ba92) by mjanez).
- Fix base harvester to clean tags ([2788896](https://github.com/OpenDataGIS/ckanext-fototeca/commit/27888969dfb662277def262c700c0f7be4f7b2f4) by mjanez).
- Fix logs ([a8c0fc8](https://github.com/OpenDataGIS/ckanext-fototeca/commit/a8c0fc8c113938818f287945b11e185e25aec9f9) by mjanez).
- Fix SQL Clauses to avoid errors when SRID=0 ([8bc5870](https://github.com/OpenDataGIS/ckanext-fototeca/commit/8bc587079a6280c65fe8c94ae23d76f39f091ba7) by mjanez).
- Fix README and i18n translates ([ce51bb1](https://github.com/OpenDataGIS/ckanext-fototeca/commit/ce51bb199943726e5e128fa2e56b39734e3998f9) by mjanez).

### Removed

- Remove source form ([71b86eb](https://github.com/OpenDataGIS/ckanext-fototeca/commit/71b86eb1bfe7b240095ea68ab9b1f25bff136278) by mjanez).
- Remove unnecesary debug log ([ef03a2d](https://github.com/OpenDataGIS/ckanext-fototeca/commit/ef03a2de75983de4957b606b89879dbb7b55e7d1) by mjanez).
- Remove unnecessary psycopg2 ([c22d95d](https://github.com/OpenDataGIS/ckanext-fototeca/commit/c22d95deb5551d549fdcaa4c10623196c9faef37) by mjanez).

