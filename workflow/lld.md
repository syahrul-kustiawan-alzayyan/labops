# LLD: LabOps ITG — Low-Level Design

> **Versi dokumen**: 1.0
> **Referensi**: PRD-LAB-001 v1.2, HLD v1.0 (`workflow/hld.md`)
> **Tanggal**: 2026-10-27
> **Lingkup**: Desain level kode — struktur proyek, service layer, repository, validasi, DTO, komponen UI, state, error handling, testing. Bukan kode implementasi, tetapi kontrak yang cukup untuk mulai coding.

---

## 1. Struktur Proyek

```
labops-itg/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, CORS, middleware
│   │   ├── core/                   # config, db, security, deps, errors
│   │   │   ├── config.py           # pydantic-settings (.env)
│   │   │   ├── database.py         # async engine, session factory
│   │   │   ├── security.py         # JWT, bcrypt, rate limit
│   │   │   ├── deps.py             # dependency injection (get_db, get_current_user)
│   │   │   └── errors.py          # custom exceptions + handlers
│   │   ├── models/                 # SQLAlchemy ORM (1 file per entitas)
│   │   ├── schemas/                # Pydantic DTO (request/response)
│   │   ├── repositories/           # data access (1 per aggregate)
│   │   ├── services/               # business logic (1 per modul)
│   │   ├── routers/                # FastAPI routers (thin controllers)
│   │   ├── jobs/                   # scheduled jobs (reminder, backup)
│   │   ├── importers/              # Excel importers
│   │   ├── exporters/              # PDF/XLSX/CSV
│   │   └── utils/                  # helpers (time, id, file)
│   ├── alembic/                    # migrations
│   ├── tests/                      # pytest
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx                 # router
│   │   ├── api/                    # axios client + endpoints
│   │   ├── components/             # reusable UI (Button, Table, Modal, ...)
│   │   ├── features/               # per modul (inventory, repairs, ...)
│   │   │   └── <modul>/
│   │   │       ├── pages/
│   │   │       ├── components/
│   │   │       ├── hooks/
│   │   │       ├── store.ts        # Zustand slice (jika perlu)
│   │   │       └── types.ts
│   │   ├── hooks/                  # global hooks
│   │   ├── lib/                    # utils (format date, currency)
│   │   └── styles/                 # tailwind config
│   ├── tests/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

### 1.1 Konvensi Penamaan
- Python: `snake_case` (fungsi, variabel, kolom DB), `PascalCase` (kelas).
- TypeScript: `camelCase` (variabel/fungsi), `PascalCase` (komponen/tipe).
- API path: `kebab-case` (`/content-ideas`, `/schedule-versions`).
- DB table: `snake_case` plural (`unit_condition_history`).
- Enum value: sesuai PRD (Bahasa Indonesia, spasi diizinkan, disimpan sebagai string).

---

## 2. Cross-Cutting Concerns

### 2.1 Dependency Injection (FastAPI)
```python
# core/deps.py
def get_db() -> AsyncSession: ...
def get_current_user(token=Depends(oauth2)) -> User: ...
def require_admin(user=Depends(get_current_user)) -> User:
    if user.role != "admin": raise HTTPException(403)
    return user
```
Semua router memakai `Depends(require_admin)`.

### 2.2 Error Handling
Custom exceptions:
- `NotFoundError`, `ConflictError`, `ValidationError`, `ForbiddenError`, `ImportBatchError`.
Handler global mengubah ke `{ code, message, details }` dengan status HTTP yang sesuai (404/409/422/403).

### 2.3 Audit Logging (Service Layer)
Setiap mutasi penting memanggil:
```python
await audit.log(
    actor=user, entity_type="unit", entity_id=unit.id,
    action="update", before=old_dict, after=new_dict, reason=reason
)
```
`AuditService` menulis ke `activity_logs`. Jika `is_break_glass`, set flag.

### 2.4 Timestamp & Timezone
- Semua kolom `timestamptz` disimpan UTC.
- Helper `now_utc()`, `to_wib(dt)`, `from_wib(dt)`.
- Jam operasional & slot disimpan sebagai `time` (WIB) + `date` terpisah; konversi ke UTC hanya saat pengingat dikirim.

### 2.5 File Storage
- Interface `StorageService` dengan implementasi `LocalFileSystem` (dev) dan `S3Storage` (prod).
- Path: `{entity_type}/{entity_id}/{uuid}.{ext}`.
- Validasi: tipe file (whitelist), ukuran maks 10 MB (foto) / 20 MB (aset desain).

### 2.6 Pagination & Filtering
- Query params: `page`, `page_size`, `sort` (field:asc/desc), filter spesifik per endpoint.
- Helper `paginate(query, page, page_size)`.

### 2.7 Import Framework
- `BaseImporter` dengan metode: `parse(file) -> list[dict]`, `validate(rows) -> (valid, errors)`, `commit(valid, batch_id)`.
- Setiap impor: preview (validasi tanpa commit) + commit. `batch_id` untuk rollback.
- Laporan: `{ total, success, failed, duplicate, errors: [{row, field, message}] }`.

---

## 3. Modul: Core (Auth, Master Data, Notif, Log, Backup)

### 3.1 Auth Service
- `login(email, password)`: verifikasi bcrypt, cek lockout, buat access+refresh token, catat `last_login`.
- `refresh(refresh_token)`: validasi, rotate refresh token (revoke lama, buat baru).
- `logout`: revoke refresh token.
- Rate limit: 5 percobaan / 15 menit per IP+email (Redis/in-memory; in-memory cukup untuk single instance).

### 3.2 Master Data Service
- CRUD `labs`, `prodis`, `vendors`, `semesters`, `slot_presets`, `settings`.
- `labs` menyimpan `aliases` (jsonb) untuk nama historis.
- Validasi: nama kanonik unik; alias tidak boleh duplikat antar lab.

### 3.3 Notification Service
- `notify(user, kind, title, body, link)`: simpan ke `notifications` + kirim email (async, retry 3x).
- Template email per `kind` (Jinja2).
- Pengingat (H-3/H-1/H-0) dijadwalkan oleh scheduler job.

### 3.4 Activity Log Service
- `log(actor, entity_type, entity_id, action, before, after, reason, is_break_glass)`.
- Retensi: cleanup job bulanan untuk log > 2 tahun (soft, arsip ke file).

### 3.5 Backup Service
- `run_backup()`: `pg_dump` + snapshot storage -> file timestamped, upload, retensi 30 hari.
- `restore(backup_id)`: validasi, restore DB + storage (admin-only, konfirmasi).
- `test_restore()`: bulanan, tercatat di log.

### 3.6 Scheduler Jobs (APScheduler)
| Job | Frekuensi | Aksi |
|-----|-----------|------|
| `send_reminders` | Setiap jam (09:00 WIB) | Kirim pengingat H-3/H-1/H-0 untuk konten Terjadwal |
| `flag_overdue_content` | Setiap jam | Set flag `Terlambat` pada konten lewat jadwal |
| `backup_daily` | 02:00 WIB | Jalankan backup |
| `test_restore_monthly` | 1x/bulan | Uji restore |
| `cleanup_logs` | 1x/bulan | Arsip log >2 tahun |

---

## 4. Modul: Inventaris

### 4.1 Domain Model
- `Component` (jenis): name, category, unit, is_consumable, min_stock.
- `Unit`: code, component_id, serial_no, brand_model, lab_id, placement, acquired_at, warranty_until, funding_source, ownership, status, verified_at, archived_at.
- `UnitConditionHistory`, `UnitVerification`, `Checklist`, `ConsumableStock`.

### 4.2 Service: InventoryService
Metode utama:
- `create_component`, `update_component`, `archive_component`.
- `create_unit(data)`: validasi kode unik, set status awal `Siap Pakai` (jika unit baru) atau sesuai impor.
- `update_unit_status(unit_id, new_status, reason)`: validasi transisi (BR-26); jika `Dalam Perbaikan` tanpa tiket aktif -> tolak.
- `list_units(filters)`: filter lab, kategori, kondisi, garansi (akan habis), verifikasi (>90 hari).
- `create_checklist(lab_id, date, items)`: satu per lab+tanggal (BR-02); hitung skor; tentukan siap/tidak berdasarkan 4 syarat.
- `verify_unit(unit_id, result, failed_items)`: set `verified_at`, `valid_until` (+90 hari); jika gagal -> buat tiket otomatis.
- `import_units(file, mode)`: preview/commit, validasi duplikat, laporan baris gagal.
- `archive_unit(unit_id, reason)`: soft delete.

### 4.3 Repository: UnitRepository
- `get_by_code(code)`, `get_by_lab(lab_id)`, `search(q, filters)`.
- `count_by_status(lab_id)` untuk dashboard.
- `get_overdue_verification(cutoff_date)`.

### 4.4 Validasi (Pydantic)
- `UnitCreate`: code (regex `^[A-Z0-9-]+$`), component_id (uuid), lab_id (uuid), acquired_at (date), warranty_until (date|null), status (enum).
- `ChecklistCreate`: lab_id, date, items (list of `{ item, required, result, note }`).
- `UnitImportRow`: semua kolom wajib; validasi kondisi di 6 status baku; lab harus ada di master.

### 4.5 Komponen UI (React)
- `UnitListPage`: tabel + filter (lab, kategori, kondisi, garansi) + pencarian kode; tombol Tambah/Impor/Cetak.
- `UnitDetailDrawer`: kondisi, riwayat, tiket terkait, tombol "Buat Tiket".
- `ChecklistPage`: form per lab+tanggal; item wajib/opsional; skor; tombol "Buat Tiket" dari item gagal.
- `ImportPreviewModal`: pratinjau + nomor baris gagal + konfirmasi.

### 4.6 State Management
- React Query untuk server state (units, checklists).
- Zustand slice `inventoryFilters` (filter persist di URL query).

---

## 5. Modul: Kerusakan (Repairs)

### 5.1 Domain Model
- `Ticket`: number (RPR-YYYY-NNN), unit_id (nullable), reporter, severity, impact, priority, status, due_response_at, due_remediation_at, created_at, triaged_at, verified_at.
- `TicketAction`: ticket_id, type, diagnosis, action, sparepart, cost, start_at, end_at, vendor_id.
- `Vendor`.

### 5.2 Service: RepairService
- `create_ticket(data)`: hitung prioritas dari matriks 7.3 (keparahan × dampak); set tenggat respons & remediasi; jika unit ada, cek tiket aktif (BR-07) -> tolak jika ada.
- `triage(ticket_id, result, note)`: valid/duplikat/tidak valid; jika duplikat -> tutup dengan alasan; jika valid -> set status `Ditriase`, catat waktu; unit status -> `Rusak` jika tiket Berat/Kritis (BR-26b).
- `add_action(ticket_id, action)`: catat tindakan; ubah status ke `Dalam Perbaikan` / `Menunggu Suku Cadang/Vendor`.
- `verify(ticket_id, result, note)`: jika lulus -> tiket `Terverifikasi`, unit `Siap Pakai`; jika gagal -> tiket `Tidak Dapat Diperbaiki`, unit `Dinonaktifkan`.
- `close_duplicate/invalid(ticket_id, reason)`: tanpa mengubah unit (BR-26g).
- `list_tickets(filters)`: status, prioritas, keterlambatan.
- `get_sla_report(period)`.

### 5.3 Validasi
- `TicketCreate`: unit_id (uuid|null), severity (enum), impact (boolean), kronologi (str, min 10), dampak praktikum (bool).
- `VerifyRequest`: result (pass/fail), test_notes (str, min 20).

### 5.4 Komponen UI
- `TicketListPage`: tabel + filter status/prioritas/keterlambatan; kartu ringkasan.
- `CreateTicketModal`: form singkat (<=60 detik); unit terisi otomatis dari dashboard/unit.
- `TicketDetailPage`: kronologi, riwayat tindakan, biaya, verifikasi; tombol Verifikasi.
- `VerifyModal`: form uji fungsi.

### 5.5 State
- React Query untuk tickets.
- Optimistic update untuk status (rollback on error).

---

## 6. Modul: Penjadwalan (Scheduling)

### 6.1 Domain Model
- `Lab`, `Semester`, `SlotPreset`, `Lecturer`, `Course`, `Class`, `Session`, `SessionLecturer`, `SessionChange`, `ScheduleVersion`.

### 6.2 Service: SchedulingService
- `create_session(data)`: validasi bentrok (BR-08), maintenance (BR-10), kapasitas (BR-23), perangkat khusus (BR-11), jam operasional (BR-12). Jika jeda <10 menit -> simpan + warning.
- `validate_session(data)`: preview tanpa simpan (untuk UI).
- `update_session`, `cancel_session`: wajib alasan, validasi ulang, catat perubahan.
- `publish_version(semester_id)`: cek 0 konflik; buat `ScheduleVersion` (status published); versi lama -> superseded; generate PDF.
- `import_schedule(file, semester_id)`: parse 74 baris, preview konflik, commit batch.
- `get_calendar(filters)`: per ruang/prodi/dosen/minggu.
- `check_conflicts_on_master_change(master_id)`: peringatan jika perubahan master memicu konflik.

### 6.3 Repository
- `SessionRepository.find_conflicts(lab_id, day, start, end, week_start, week_end, exclude_id)`.
- `SessionRepository.find_by_lecturer`, `find_by_class`.
- `ScheduleVersionRepository.get_latest_published(semester_id)`.

### 6.4 Validasi (Pydantic)
- `SessionCreate`: type (enum), course_id, class_id, lecturer_ids (list uuid), student_count (int>0), lab_id, day_of_week (0-5 Sen-Sab), start_time (time), end_time (time, > start), week_start (int>=1), week_end (int>=week_start), override_reason (str|null).
- `@model_validator`: end_time > start_time; week range valid; jika di luar jam operasional -> override_reason wajib.

### 6.5 Komponen UI
- `ScheduleCalendarPage`: kalender mingguan (Sen-Sab), pemilih ruang/prodi, tombol Tambah Sesi/Terbitkan; sel menampilkan MK/kelas/jam; blok maintenance khusus; bilah bawah (konflik, ruang-hari kosong, maintenance). Pada 360px -> daftar per hari.
- `SessionFormModal`: form sesi; validasi langsung; konflik & jeda <10 menit ditampilkan sebelum simpan.
- `ImportScheduleModal`: upload, preview, koreksi baris, commit.
- `PublishConfirmModal`: cek 0 konflik; tampilkan versi.

### 6.6 State
- React Query untuk sessions/calendar.
- Zustand `scheduleFilters` (ruang, prodi, minggu).
- Optimistic update dengan rollback.

---

## 7. Modul: Media Sosial (Social)

### 7.1 Domain Model
- `SocialAccount`, `ContentIdea`, `Content`, `ContentChecklist`, `ContentAsset`, `Reminder`.

### 7.2 Service: SocialService
- `create_idea`, `create_content_from_idea`.
- `update_content`: caption, aset, jadwal.
- `submit_checklist(content_id, items)`: hitung kelengkapan.
- `approve(content_id)`: hanya jika checklist 100%; catat waktu + identitas (BR-15a); status -> `Disetujui`.
- `schedule(content_id, date, time)`: status -> `Terjadwal`; jadwalkan pengingat H-3/H-1/H-0.
- `mark_posted(content_id, actual_time)`: status -> `Terposting`; kunci aset; arsip.
- `reopen(content_id)`: buat revisi baru (BR-27) berstatus `Draf`, revision_no++, parent_content_id; versi Terposting tetap final.
- `reschedule`, `cancel`.
- `get_calendar(month, account)`, `get_due_list()`.
- `migrate_legacy_content(file)`: batch import 174 item (PRD 6.7.2).

### 7.3 Validasi
- `ContentCreate`: title, account_id, idea_id (nullable), caption (min 10), scheduled_date (nullable), scheduled_time (nullable).
- `ScheduleRequest`: date (>= today), time.
- `ApproveRequest`: checklist 100% (server-side check, bukan hanya UI).

### 7.4 Komponen UI
- `SocialCalendarPage`: kalender bulanan 4 warna akun, filter akun/status/jenis; daftar jatuh tempo di bawah.
- `ContentDetailDrawer`: caption, aset, checklist, riwayat status; tombol Setujui/Jadwalkan/Sudah Diposting.
- `ContentChecklist`: progres; tombol Setujui aktif hanya 100%.
- `ReminderList`: daftar pengingat.

### 7.5 State
- React Query untuk contents/calendar.
- Zustand `socialFilters`.

---

## 8. Modul: Pelaporan (Reports)

### 8.1 Service: ReportService
- `get_dashboard()`: kesiapan per lab, tiket terbuka, sesi hari ini, konten jatuh tempo, tugas lewat tenggat.
- `generate_inventory_report(period)`, `generate_repair_report`, `generate_usage_report`, `generate_social_report`.
- `generate_monthly_report(period)`: agregasi semua modul -> PDF + arsip (status final, tidak dapat diubah; koreksi = revisi bertanggal).
- `export(data, format)`: XLSX/CSV/PDF.

### 8.2 Komponen UI
- `DashboardPage`: kartu kesiapan, tiket, sesi, konten, daftar tugas.
- `ReportPage`: pilih jenis & periode, pratinjau, ekspor.
- `MonthlyReportModal`: pilih bulan, generate, arsip.

---

## 9. Testing Strategy

### 9.1 Backend (pytest)
- Unit tests: service layer (validasi bentrok, prioritas tiket, kesiapan lab, migrasi konten).
- Integration tests: API endpoints dengan DB test (testcontainers postgres).
- Property-based: validasi jam/minggu (hypothesis).
- Target coverage: >=80% untuk service & validation.

### 9.2 Frontend (Vitest + RTL)
- Component tests: form validasi, kalender, checklist.
- E2E (Playwright): alur kunci (lapor kerusakan <=60 detik, jadwal bentrok ditolak, konten approval).

### 9.3 Acceptance Testing
- Semua AC di PRD 10.1-10.7 diuji manual + otomatis sebelum rilis.
- UAT oleh koordinator pada parallel run (2 minggu).

---

## 10. Template Data Awal (M0)

Template disediakan di folder `workflow/templates/` (CSV, dapat dibuka di Excel). Diisi koordinator sebelum Go-Live.

| File | Isi | Kolom wajib |
|------|-----|-------------|
| `labs.csv` | 6 lab + alias historis | canonical_name, aliases, capacity, facilities, capabilities, status |
| `prodi.csv` | Prodi TI, SI, Pascasarjana | code, name |
| `components.csv` | Jenis komponen lab | name, category, unit, is_consumable, min_stock |
| `units_stock_opname.csv` | Hasil stock opname (per unit) | code, component, brand_model, serial_no, lab, placement, acquired_at, warranty_until, funding_source, ownership, condition |
| `semesters.csv` | Semester aktif | name, start_date, end_date, operating_hours, slot_presets |
| `lecturers.csv` | Dosen/instruktur | code, canonical_name, aliases, nidn (opsional), role |
| `courses.csv` | Mata kuliah | code, name, prodi, sks |
| `classes.csv` | Kelas | code, course_code, prodi, semester, academic_year |
| `vendors.csv` | Mitra/vendor perbaikan | name, service_type, contact |
| `social_accounts.csv` | 4 akun resmi | name, type, platform, prodi, tone, audience, ideal_posting_time |
| `content_ideas_backlog.csv` | 15 item tanpa tanggal (backlog) | title, category, target_account, notes |
| `schedule_import.csv` | 74 baris jadwal 2025/2026 | lab_alias, day, start_time, end_time, week_start, week_end, course_code, class_code, lecturer, student_count, type |
| `settings.csv` | Konfigurasi awal | key, value |

### 10.1 Format & Aturan Pengisian
- Encoding: UTF-8 (dengan BOM agar Excel membaca dengan benar).
- Pemisah: koma (`,`); field dengan koma dibungkus tanda kutip.
- Tanggal: `dd/mm/yyyy` (sesuai UI), dikonversi ke ISO saat impor.
- Jam: `HH.MM` (24 jam, WIB).
- Kode unit: huruf kapital, format `LAB-KOMPONEN-NN` (contoh `C201-PC-07`).
- Lab: gunakan nama kanonik (`C-I-01`, dst.); alias lama boleh di kolom `lab_alias` pada impor jadwal.
- Kondisi unit: salah satu dari 6 status baku (Siap Pakai, Perlu Perhatian, Rusak, Dalam Perbaikan, Dinonaktifkan, Hilang).
- Baris kosong dan baris judul (header bulan) pada file lama **tidak** dimasukkan; impor memvalidasi seluruh baris sebelum commit.

### 10.2 Sumber Template
Template CSV dibuat di `workflow/templates/` (lihat file). Koordinator mengisi, lalu impor via aplikasi (preview + validasi + commit). File lama tetap disimpan sebagai arsip.

---

## 11. Catatan
LLD ini adalah **versi 1.0** dan akan diperbarui saat implementasi berjalan (discovery teknis, perubahan skema). Detail API (request/response lengkap) akan dilengkapi di OpenAPI (auto-generate FastAPI) dan di-review saat implementasi. Testing strategy (9) wajib dijalankan sebelum rilis.