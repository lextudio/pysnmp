# Release 6.0 Roadmap

## Background

Ilya started this project and worked on the 1.0-4.0 releases.

> Ilya left his ideas on the future of the project in the `TODO.txt` file.

The Splunk team took over part of the project and started the 5.0 release.
LeXtudio Inc. continued the 5.0 release when it started to [take over the
entire PySNMP ecosystem](https://github.com/etingof/pysnmp/issues/429).

Now the Python landscape has changed a lot due to frequent Python releases
and breaking changes in each of them. The PySNMP project needs to adapt to
the new reality and provide a better user experience.

Thus, the 6.0 release is planned to address the most critical issues.

## Goals

- Modern Python support (new releases and new features)
- Better documentation
- Better test coverage
- Frequent housekeeping (remove old code, update dependencies, etc.)

## Tasks

- [x] Limit Python support to 3.8+. This is to reduce the maintenance burden.
- [x] Removed asyncore support. This is to reduce the maintenance burden.
- [x] Converted all asyncore code to asyncio. This is to support modern Python.
- [x] Updated sample code and documentation to use asyncio. This is to support modern Python.
- [ ] Improve test cases and coverage. This is to improve code quality.

## Breaking Changes

- Removed asyncore related API from `pysnmp.hlapi` module. This is expected to break existing code that uses `pysnmp.hlapi` module with asyncore. Users can stay on 5.0 release but are encouraged to migrate to asyncio and our 6.0 release.
- Switched to `asyncio` in many type implementation in `pysnmp.hlapi` module. This is expected to break existing code that uses `pysnmp.hlapi` module if it assumes the relevant API is implemented upon asyncore. Users are encouraged to test their code thoroughly and make necessary changes.
- Stopped supporting Python 3.7 and below. Users are encouraged to upgrade their Python to 3.8+ (ideally 3.11+).
