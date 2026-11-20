# INFRA-04: GitHub Actions: lint + unit test ทุก PR

**Status:** in-review  
**Owner:** M1  
**Phase:** PoC (T1/2569)  
**Refs:** —  
**Branch:** `chore/infra-04-ci-pipeline`  
**PR:** —

## งาน

- [x] workflow รัน `ruff check`, `ruff format --check`, `pytest`
- [ ] ตั้ง branch protection ของ `main` ให้ต้องผ่าน CI + 1 review

## Acceptance criteria

- PR ที่ lint ไม่ผ่านถูก block

## File scope

`.github/workflows/`, `pyproject.toml`

## Evidence

ทดสอบในเครื่อง (Python 3.13, ruff 0.16.10) ด้วย config ใหม่ใน `pyproject.toml`

```
$ ruff check .
All checks passed!
$ ruff format --check .
118 files already formatted
$ pytest
73 passed
```

- workflow `.github/workflows/ci.yml` รันบน `pull_request` และ `push` เข้า `main` → job `lint-test`: `ruff check` → `ruff format --check` → `pytest`
- ผลรันจริงบน GitHub Actions: ดูแท็บ Checks ของ PR นี้
- ทดสอบว่า block จริง: หลังตั้ง branch protection ให้ลองเปิด draft PR ที่จงใจใส่ `import os` ที่ไม่ได้ใช้ → `ruff check` ต้องแดง และปุ่ม Merge ต้องกดไม่ได้

**ตั้ง branch protection (เจ้าของ repo ทำใน GitHub):** Settings → Branches → Add rule → `main`
- Require a pull request before merging → Required approvals = 1
- Require status checks to pass → เลือก `lint-test`
- Require branches to be up to date before merging

## Comments

- 2026-11-20 (M1): เพิ่ม `pyproject.toml` (ruff + pytest + dependency groups) และ workflow `CI` job `lint-test` โค้ดเตรียมด้วย Claude Code (เปิดเผยในภาคผนวก ก ของรายงาน) รอเจ้าของ repo ตั้ง branch protection
