# Working Guidelines (สำหรับคนและ AI agent)

ไฟล์นี้คือกฎการทำงานใน repo นี้ `AGENTS.md` และ `CLAUDE.md` ที่ root ชี้มาที่นี่ ถ้างานขัดกับกฎหรือ ADR ให้บอกตรงๆ ห้ามข้ามเงียบๆ

## ก่อนเริ่มงาน
1. อ่าน [CONTEXT.md](CONTEXT.md) — ใช้คำให้ตรงกัน
2. อ่าน [adr/](adr/) — การตัดสินใจทางเทคนิคที่ล็อกแล้ว
3. หา issue ของงานใน [issues/BOARD.md](issues/BOARD.md) — **ไม่มี issue = ห้ามเริ่มเขียนโค้ด**

## กฎหลัก: 1 issue = 1 branch = 1 PR
- ทุก issue มี field `Branch:` กำหนดชื่อไว้แล้ว **ใช้ชื่อนั้นตรงตัว ห้ามตั้งชื่อเอง**
- งานใหม่ที่ไม่มีใน board: เพิ่มไฟล์ issue (เลขถัดไปใน feature นั้น) + แถวใน BOARD.md ใน PR แยกบน branch `docs/<feature>-<NN>-add-issue` ก่อน แล้วค่อยเริ่ม branch ของงาน
- ห้ามรวมหลาย issue ใน branch เดียว ห้ามแยก issue เดียวเป็นหลาย PR (ถ้างานใหญ่เกิน ให้แตก issue ก่อน)

## Branches
| Branch | ใช้ทำอะไร | กฎ |
|---|---|---|
| `main` | โค้ดที่ผ่าน review แล้ว demo ได้เสมอ | protected: ห้าม push ตรง, merge ผ่าน PR เท่านั้น (squash merge), ต้องผ่าน CI และ review จากสมาชิกอีกคน |
| `<type>/<issue-id>-<slug>` | งานหนึ่ง issue | แตกจาก `main` ล่าสุด, ลบหลัง merge |

ไม่มี `develop` branch (ทีม 2 คน ใช้ trunk-based)

### รูปแบบชื่อ branch
```
<type>/<issue-id>-<slug>
```
- `type`: `feat` (ฟีเจอร์), `fix` (แก้บั๊ก), `docs` (เอกสาร), `chore` (config/infra/CI), `test` (เพิ่ม/วัดผลทดสอบ), `exp` (PoC/ทดลองที่ผลคือรายงาน)
- `issue-id`: ตัวพิมพ์เล็ก เช่น `f1-01`, `infra-02`, `qa-01`
- `slug`: ภาษาอังกฤษตัวพิมพ์เล็กคั่นด้วย `-` ไม่เกิน 5 คำ
- ตัวอย่าง: `feat/f1-01-news-collector`, `chore/infra-02-aws-foundation`, `test/f3-03-finbert-goldset-eval`

### Tags
- `v0.1-poc` — จบเทอม 1/2569
- `v1.0` — จบเทอม 2/2570

## Commit
- Conventional Commits ภาษาอังกฤษ: `<type>(<scope>): <summary>` เช่น `feat(ingestion): add RSS collector for 10 tickers`
- `scope` = ชื่อโฟลเดอร์ระดับบน (`ingestion`, `streaming`, `batch`, `lakehouse`, `sentiment`, `ai`, `webapp`, `infra`, `docs`)
- คำไทยเก็บไว้ใน quote ได้ ห้าม commit secrets (`.env` ถูก gitignore)

## Pull Request
- Title: `[F1-01] Short summary` (ID ตัวพิมพ์ใหญ่ตาม issue)
- Body ใช้ [`.github/pull_request_template.md`](../.github/pull_request_template.md): ลิงก์ issue, สิ่งที่เปลี่ยน, หลักฐาน (ผลทดสอบ/ภาพ/query), checklist
- ก่อนเปิด PR:
  ```bash
  git fetch origin main && git merge origin/main   # sync main
  ruff check . && ruff format --check . && pytest  # เมื่อมีโค้ด Python
  ```
- PR เดียวกันต้องอัปเดตไฟล์ issue: ติ๊ก checklist, เปลี่ยน `Status`, ใส่ `PR:` และ `## Evidence`, และอัปเดตแถวใน BOARD.md
- เปลี่ยน schema → แก้ [05-data-design.md](05-data-design.md) ใน PR เดียวกัน
- เปลี่ยนการตัดสินใจที่ล็อกแล้ว → เพิ่ม ADR ใหม่ใน PR เดียวกัน

## Sync `main` 3 จุด
ตอนสร้าง branch, ก่อนเปิด PR, และก่อน merge

## Issue files
- โครงสร้าง: `docs/issues/<feature-slug>/PRD.md` และ `docs/issues/<feature-slug>/issues/<NN>-<slug>.md` (เลขเริ่ม 01)
- `Status`: `todo` · `in-progress` · `in-review` · `done` · `wontfix`
- `Owner`: `M1` (สุรบดี), `M2` (รพินทร์), `M1+M2`
- `Phase`: `PoC (T1/2569)` หรือ `Full (T2/2570)`
- ความคืบหน้าเขียนใน `## Comments` พร้อมวันที่และผู้เขียน

## อยู่ในขอบเขตโฟลเดอร์ของ issue
แต่ละ issue ระบุ `File scope` ถ้าต้องแก้ไฟล์นอก scope ให้เขียนเหตุผลใน PR

## กฎเฉพาะสำหรับ AI agent (Claude ฯลฯ)
- ทำงานบน branch ตาม field `Branch:` ของ issue เท่านั้น ห้ามสร้าง branch ชื่ออื่น
- ถ้า tool/สภาพแวดล้อมบังคับชื่อ branch อื่น ให้หยุดและถามคนก่อน
- ห้ามเปิด PR ถ้าไม่ได้ถูกขอ และห้าม merge เอง
- ห้ามเรียก AWS / LLM API นอกโมดูลที่กำหนด (`ai/` สำหรับ LLM)
