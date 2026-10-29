# PRD Studio 状态

## 基本信息
- **需求描述**：Aplikasi pengelolaan operasional laboratorium untuk Koordinator Lab Ilmu Komputer — inventaris & kesiapan komponen, pencatatan kerusakan/perbaikan, pengelolaan media sosial 4 prodi, penjadwalan lab, dan pelaporan.
- **Input**：Deskripsi kebutuhan langsung (tanpa BRD)
- **PRD 类型**：新功能（有 UI），1 PRD terintegrasi
- **Keputusan pengguna**：
  - Pengguna: hanya Koordinator Lab (single-user/admin penuh)
  - Platform: web responsif
  - MVP: 5 modul (inventaris, kerusakan & perbaikan, penjadwalan, media sosial, pelaporan & dashboard)
  - Media sosial: perencanaan konten + pengingat + arsip (posting tetap manual, tanpa auto-publish & analitik API di MVP)
  - Penjadwalan: input manual oleh koordinator, validasi bentrok otomatis
- **Mulai**：2026-10-25
- **当前状态**：LLD v1.0 + template data awal selesai — siap implementasi (S0)

## 迭代记录

| 轮次 | 阶段 | 时间 | 结果 |
|------|------|------|------|
| 1 | Writer | 2026-10-25 | prd.md (694 baris, 65 FR, 22 BR, 15 NFR, 35 AC, 5 Mermaid) + context-report.md |
| 1 | Reviewer | 2026-10-25 | 🔴 P0=5, P1=10, P2=10 — perlu revisi |
| 1 | Fixer | 2026-10-25 | ✅ v1.1 — P0 5/5, P1 10/10, P2 10/10 |
| 2 | Reviewer | 2026-10-27 | 🔴 P0=0, P1=7, P2=8 — perlu revisi ronde 2 |
| 2 | Fixer | 2026-10-27 | ✅ v1.2 — P1 7/7, P2 8/8 (BR-26, BR-27, MS-n, PRI-n, dll.) |
| 3 | Reviewer | 2026-10-27 | 🟢 P0=0, P1=1 (lalu diperbaiki), P2=2 (diperbaiki) — 准出通过 |
| 3 | Polish | 2026-10-27 | AC-SOS-04, 8.1, R7 diselaraskan pasca-准出 |
| 4 | HLD | 2026-10-27 | `workflow/hld.md` v1.0 — arsitektur, model data, API, keamanan, NFR, migrasi, deployment, roadmap implementasi |
| 5 | LLD + Templates | 2026-10-27 | `workflow/lld.md` v1.0 (struktur proyek, service layer, validasi, komponen UI, testing) + `workflow/templates/` (13 CSV template data awal M0) |
