# History

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org/).

## 0.1.4 (2024-04-19)

- Bug fix when getting key from .env file for comparision

## 0.1.3 (2024-04-19)

- Added `ignore_keys` to config for keys (exact key names) to always ignore even if they contain `key_word`.

## 0.1.2 (2024-04-18)

- Bug fix for if a env value contains an "=". We only split on the first "=" so we get key,value from .env.

## 0.1.1 (2024-04-18)

- Write secrets files non-destructively
- Sort keys for secrets files

## 0.1.0 (2024-04-15)

- First release
