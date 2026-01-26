# Changelog

All notable changes to ouracli will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-01-26

### Added
- Sleep data retrieval with multiple output formats (table, tree, json, html, dataframe)
- Activity data with braille terminal charts
- Readiness scores and contributors
- Heart rate data and charts
- `all` command for comprehensive daily view
- `--ai-help` flag with dashdash-spec v0.2.0 for LLM/agent guidance
- SKILL.md for Clawdbot integration
- 92% test coverage with property-based fuzzing (hypothesis)
- Snapshot tests with real API data fixtures

### Fixed
- HTML chart rendering with proper JSON serialization
- Heartrate charts in 'all' command for tree and HTML formats
- Clean exit on missing token (no ValueError)
- Linting and type checking errors

[Unreleased]: https://github.com/visionik/ouracli/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/visionik/ouracli/releases/tag/v0.1.0
