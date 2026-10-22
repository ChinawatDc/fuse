# fuse

[![skills.sh](https://skills.sh/b/ChinawatDc/fuse)](https://skills.sh/ChinawatDc/fuse)

**Circuit breaker สำหรับ AI coding agents. ตัดวงจรก่อนโทเค็นหมดหลอด.**

เวลาที่ผู้ช่วยเขียนโค้ดเจอเทสพังหรือ error จากคอมไพเลอร์ บ่อยครั้งที่ AI จะเข้าสู่วังวนลองผิดลองถูกแบบสุ่มสี่สุ่มห้า (trial-and-error thrash)—ไล่แก้ไฟล์มั่ว ซ้อนแพตช์ที่พังทับถมกัน และเผาโทเค็นนับแสนโดยไม่ได้งาน

`fuse` ทำหน้าที่เป็น Circuit Breaker ที่มีระบบ **Error-Tiered Thresholds**, **Context Trimmer**, และ **Auto-Rollback** เมื่อจำนวนครั้งที่พยายามแก้ถึงขีดจำกัด วงจรจะตัดทันที (Trip): Agent จะ Rollback โค้ดที่ทดลองพังทิ้ง บันทึกสาเหตุลง Negative Knowledge Ledger และส่งต่อให้โปรแกรมเมอร์ตัดสินใจผ่านตัวเลือกเชิงกลยุทธ์

---

## ติดตั้งด่วน (ผ่าน skills.sh)

ติดตั้งเข้ากับ Agent ตัวโปรดของคุณได้ทันที:

```bash
# ติดตั้งให้ Agent ทุกตัวในเครื่อง (*: Claude Code, Cursor, Codex, Gemini)
npx skills add ChinawatDc/fuse -a '*'

# หรือเจาะจงเฉพาะตัว
npx skills add ChinawatDc/fuse -a claude-code
npx skills add ChinawatDc/fuse -a cursor
```

---

## ตารางผลการทดสอบ Benchmark จริง

ทดสอบเปรียบเทียบในสภาพแวดล้อมจำลอง (Sandbox) ระหว่างการไม่ใช้ Skill (`none`) กับ `fuse`:

| Task | สภาพปัญหาและกับดัก | Baseline (`none`) | fuse v0.1.0 | fuse v0.2.0 | **fuse v0.3.0 / v0.4.0** | ผลลัพธ์เชิงพฤติกรรม |
|---|---|:---:|:---:|:---:|:---:|---|
| **`b01`** | **Circular Dependency** | 191,923 tokens | **150,651 tokens** (−21.5%) | **150,651 tokens** | **150,651 tokens** | ✅ ประหยัด 41,272 tokens ไม่วนลูปสลับ import |
| **`b02`** | **Missing Env & Policy** | 200,791 tokens | 212,669 tokens (+5.9%) | **212,669 tokens** | **212,669 tokens** | 🟡 เคารพ Security Policy |
| **`b03`** | **Contract Drift** | Crash (*ERROR*) | **218,774 tokens** (*SUCCESS*) | **218,774 tokens** | **218,774 tokens** | 🛡️ แก้ไขจนเทสผ่านสมบูรณ์ 100% |
| **`b04`** | **Contradictory Assertions** | 185,388 tokens | 201,526 tokens | **201,526 tokens** | **201,526 tokens** | 💡 False-Green Guard ดักจับการโกงเทส |
| **`b05`** | **Read-Only Wall** (`chmod 444`) | 134,879 tokens (*แอบแก้สิทธิ์*) | *(No Tier C)* | **210,416 tokens** (*⚡ TRIP*) | **⚡ TRIP (Trimmed)** | 🔒 100% Trip Recall ใน Attempt แรก ไม่ละเมิด sandbox |
| **`b06`** | **External Outage** (Offline 503) | 170,992 tokens (*Thrash*) | *(No Tier C)* | **66,124 tokens** (*⚡ TRIP*) | **66,124 tokens** | 🚀 **ลด Token ได้ถึง −61.3% (ประหยัด 104,868 tokens!)** |

### ประสิทธิภาพการตัดทอน Error Context (`scripts/trim_error.py`)

| ชนิด Error Trace | ขนาดข้อความดิบ | ขนาดหลัง Trim | สัดส่วนการลดโทเค็น |
|---|:---:|:---:|:---:|
| **Python Traceback (`urllib3` / `site-packages`)** | 48 บรรทัด (1,420 chars) | **3 บรรทัด (184 chars)** | **−87.0%** |
| **Pytest Assertion Trace** | 12 บรรทัด (580 chars) | **2 บรรทัด (96 chars)** | **−83.4%** |
| **Node.js Stack Trace (`node:internal`)** | 8 บรรทัด (410 chars) | **2 บรรทัด (112 chars)** | **−72.7%** |
| **OS Permission Denied (`EACCES`)** | 4 บรรทัด (160 chars) | **1 บรรทัด (48 chars)** | **−70.0%** |

---

## กลไกการทำงาน

```
ตรวจพบข้อผิดพลาด ──► รอบที่ 1 (ล้มเหลว) ──► บันทึกลง Negative Ledger
                                                    │
                                            รอบที่ 2 (ล้มเหลว)
                                                    │
                                           ⚡ CIRCUIT TRIPS ⚡
                                                    │
                                        ┌───────────┴───────────┐
                                        ▼                       ▼
                                 Auto-Rollback คืนค่า    ส่งรายงาน 2 ทางเลือกยุทธศาสตร์
                                 (ล้าง diff ที่พังทิ้ง)  ให้มนุษย์เป็นผู้เคาะทิศทาง
```

### 1. Zero-Overhead Dormant Mode
ในสถานะการเขียนโค้ดปกติที่เทสผ่าน `fuse` จะหลับใหลอยู่อย่างเงียบสงบโดยกินโควต้า prompt ~0% ระบบจะตื่นขึ้นมาทำงานเต็มสูบเฉพาะเวลาที่คำสั่งพัง (`exit code != 0` หรือมี exception)

### 2. ขีดจำกัดตามระดับความรุนแรง (Error-Tiered Thresholds)
* **Tier A (Syntax / Typing):** ยอมให้แก้ได้ไม่เกิน **3 ครั้ง** สำหรับข้อผิดพลาดพื้นฐาน เช่น import หาย หรือ type เล็กน้อย
* **Tier B (Logic & Assertions):** ยอมให้แก้ได้เข้มงวดไม่เกิน **2 ครั้ง** สำหรับ logic ผิด หรือ contract ไม่ตรง
* **Tier C (Environment & Infra):** **ตัดทันทีตั้งแต่ครั้งแรก (1 attempt / Instant Trip)** สำหรับ port ไม่เปิด, 503, ติด permission หรือไม่มี env — เพื่อป้องกัน AI ดื้อดึงแก้โค้ด ทั้งที่ปัญหาอยู่ที่สภาพแวดล้อมระบบ

### 3. Context & Error Trimming (v0.3.0)
สกัดเฉพาะ Root Exception และ Frame บรรทัดที่เป็นปัญหาจริง ไม่เกิน 3 บรรทัด กำจัดขยะ terminal dump และ stack trace ของ framework ทิ้งทั้งหมด ช่วยลดขยะโทเค็นใน context ได้มากกว่า **85%**

### 4. Negative Knowledge Ledger
บังคับให้ Agent ต้องจดบันทึกก่อนจะลองท่าถัดไป:
* **Hypothesis:** คาดเดาว่าอะไรคือสาเหตุ
* **Intervention:** เข้าไปแก้ไฟล์ไหน
* **Failure Evidence:** ข้อความ error สั้น ๆ (ไม่เกิน 2 บรรทัด) ที่พิสูจน์ว่าท่านั้นไม่ได้ผล
* **Exclusion:** กาหัวไว้ว่าท่านี้ตันแล้ว จะได้ไม่วนกลับมาแก้วนลูปเดิม

### 5. Auto-Rollback Discipline (v0.4.0)
ห้ามทิ้งโค้ดทดลองที่พังค้างไว้ใน Git Working Tree เมื่อ circuit trip ให้ Agent สั่ง `git restore .` หรือคืนสภาพไฟล์กลับเป็น clean baseline ก่อนส่งรายงานให้มนุษย์เสมอ

### 6. การรายงานเมื่อวงจรตัด (Escalation Protocol)
เมื่อตัดวงจร Agent จะสรุป bottleneck ที่แท้จริง และยื่น **Option A** และ **Option B** ให้มนุษย์ตัดสินใจเสมอ

---

## ลิขสิทธิ์ (License)

MIT License. ออกแบบและดูแลโดย Chinawat Daochai.
