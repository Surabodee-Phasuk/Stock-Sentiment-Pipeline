# INFRA-04: GitHub Actions: lint + unit test ทุก PR

**Status:** todo  
**Owner:** M2  
**Phase:** PoC (T1/2569)  
**Refs:** —  
**Branch:** `chore/infra-04-ci-pipeline`  
**PR:** —

## งาน

- [ ] workflow รัน `ruff check`, `ruff format --check`, `pytest`
- [ ] ตั้ง branch protection ของ `main` ให้ต้องผ่าน CI + 1 review

## Acceptance criteria

- PR ที่ lint ไม่ผ่านถูก block

## File scope

`.github/workflows/`, `pyproject.toml`

## Evidence

_(ผลทดสอบ / query / ภาพ — เติมก่อนขอ review)_

## Comments
