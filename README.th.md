# fuse

[![skills.sh](https://skills.sh/b/ChinawatDc/fuse)](https://skills.sh/ChinawatDc/fuse)

**Circuit breaker สำหรับ AI coding agents. ตัดวงจรก่อนโทเค็นหมดหลอด.**

เวลาที่ผู้ช่วยเขียนโค้ดเจอเทสพังหรือ error จากคอมไพเลอร์ บ่อยครั้งที่ AI จะเข้าสู่วังวนลองผิดลองถูกแบบสุ่มสี่สุ่มห้า (trial-and-error thrash)—ไล่แก้ไฟล์มั่ว ซ้อนแพตช์ที่พังทับถมกัน และเผาโทเค็นนับแสนโดยไม่ได้งาน

`fuse` ทำหน้าที่เป็น Circuit Breaker ที่มีระบบ **Error-Tiered Thresholds** และ **Context Trimmer** เมื่อจำนวนครั้งที่พยายามแก้ถึงขีดจำกัด วงจรจะตัดทันที (Trip): Agent จะหยุดเขียนโค้ด บันทึกสาเหตุที่ล้มเหลวลงใน Negative Knowledge Ledger และส่งต่อให้โปรแกรมเมอร์ตัดสินใจผ่านตัวเลือกเชิงกลยุทธ์

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
                                 หยุดแก้ & Rollback     ส่งรายงาน 2 ทางเลือกยุทธศาสตร์
                                                        ให้มนุษย์เป็นผู้เคาะทิศทาง
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

### 5. วินัยการ Rollback โค้ด
ไม่ซ้อนโค้ดทดลองที่พังทับบนของเดิม ถ้าการทดลองไม่ได้ผล ต้อง `git checkout` / `git restore` คืนค่ากลับสู่ baseline ที่สะอาดเสมอ

### 6. การรายงานเมื่อวงจรตัด (Escalation Protocol)
เมื่อตัดวงจร Agent จะสรุป bottleneck ที่แท้จริง และยื่น **Option A** และ **Option B** ให้มนุษย์ตัดสินใจเสมอ

---

## ลิขสิทธิ์ (License)

MIT License. ออกแบบและดูแลโดย Chinawat Daochai.
