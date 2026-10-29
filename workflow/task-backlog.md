# Task Backlog — LabOps ITG (Implementasi Penuh)

> Sumber: PRD-LAB-001 v1.2, HLD v1.0, LLD v1.0
> Status: S0 (skeleton) + backend services/routers + frontend pages dasar selesai. Task di bawah adalah **sisa pekerjaan** untuk mencapai rilis MVP.

## Konvensi
- **Prioritas**: P0 (blokir rilis), P1 (penting), P2 (nice-to-have).
- **Estimasi**: hari kerja (1 orang).
- **Status**: `[ ]` todo, `[~]` in progress, `[x]` done.

---

## S0 — Setup & Infra (selesai)
- [x] Struktur proyek backend + frontend + docker-compose
- [x] Migration awal (30+ tabel)
- [x] Seed master data (admin, 6 lab, 12 komponen)
- [x] CI lokal: tsc build OK, compileall OK

## S1 — Inventaris (P0)
- [ ] Unit detail drawer (riwayat kondisi, tiket terkait, tombol buat tiket)
- [ ] Form ubah status unit (validasi transisi BR-26)
- [ ] Archive unit (soft delete + alasan)
- [ ] Checklist page (per lab + tanggal, item wajib/opsional, skor, kesimpulan biner BR-02)
- [ ] Impor unit dari CSV (preview + validasi duplikat + laporan baris gagal + commit)
- [ ] Verifikasi unit (form uji fungsi, set valid_until +90 hari, buat tiket jika gagal)
- [ ] Consumables (stok, ambang minimum, pemakaian)
- [ ] Pencarian & filter (kode, kategori, lab, kondisi, garansi)
- [ ] Label cetak (Fase 2, opsional)

## S2 — Kerusakan (P0)
- [x] Ticket detail page (kronologi, riwayat tindakan, biaya, verifikasi)
- [x] Triase UI (valid/duplikat/tidak valid + alasan wajib)
- [x] Tambah tindakan (internal/vendor, diagnosa, suku cadang, biaya, durasi)
- [x] Verifikasi UI (form uji fungsi -> Siap Pakai atau Dinonaktifkan)
- [x] Daftar vendor (CRUD)
- [ ] Daftar tugas (tiket lewat tenggat, urut prioritas)
- [ ] Notifikasi email tenggat (H-3, H-1, H-0)

## S3 — Penjadwalan (P0)
- [ ] Kalender grid (Sen-Sab × jam, per ruang/prodi, blok maintenance)
- [ ] Form sesi (validasi langsung, preview konflik, override jeda <10 menit)
- [x] Kalender per dosen & per prodi (via filter ruang/prodi; data tersedia)
- [x] Import jadwal 74 baris (preview, koreksi baris, commit) — backend endpoint + UI modal
- [x] Publish version + PDF (A4 landscape, siap tanda tangan) — publish endpoint + ekspor PDF (reportlab)
- [x] Ubah/batalkan sesi (wajib alasan, validasi ulang, riwayat)
- [ ] Peringatan konflik akibat perubahan master data
- [x] Penggunaan di luar jam operasional (izin + alasan) — validasi ada di backend
- [ ] Kalender akademik & hari libur (blokir otomatis) - settings + per-occurrence (kompleks, Fase 2)

## S4 — Media Sosial (P0)
- [x] Kalender konten (bulanan, 4 warna akun, filter)
- [x] Detail konten (caption, aset, checklist, riwayat status)
- [x] Checklist kelengkapan (progres, gate approval)
- [x] Approve (self-approval, catat waktu + identitas)
- [x] Schedule (tanggal + jam, jadwalkan pengingat)
- [x] Mark posted (waktu aktual, kunci aset, arsip)
- [x] Reopen (BR-27 revisi baru)
- [x] Reschedule / cancel
- [x] Migrasi 174 item dari Excel (batch, deterministik) — UI + endpoint
- [ ] Rekap konten (per akun, tepat waktu vs terlambat, kategori)
- [ ] Pengingat H-3/H-1/H-0 (scheduler + email)
- [x] Flag Terlambat (turunan, tidak mengubah status)

## S5 — Pelaporan (P0)
- [ ] Dashboard lengkap (kesiapan, tiket, sesi, konten, tugas)
- [x] Laporan inventaris & kesiapan
- [x] Laporan kerusakan & perbaikan (MTTR, biaya, rusak berulang)
- [x] Laporan penggunaan lab (jam terpakai, utilisasi, jam kosong, maintenance)
- [x] Laporan konten medsos (per akun, ketepatan, kategori)
- [x] Laporan bulanan 1 klik (PDF, arsip final, revisi bertanggal) — JSON agregasi (PDF menyusul)
- [x] Ekspor XLSX/CSV — CSV via frontend
- [ ] Filter periode/prodi/lab

## S6 — Fondasi & NFR (P0)
- [ ] Auth lengkap (login, refresh, logout, lockout 5x/15 menit, idle 30 menit)
- [ ] Pencarian global
- [ ] Notifikasi in-app + email
- [ ] Log aktivitas (retensi ≥2 tahun)
- [ ] Pengaturan master data (lab, prodi, semester, kategori, mitra)
- [ ] Cadangan harian + uji restore bulanan
- [ ] Aksesibilitas (WCAG 2.1 AA dasar, keyboard, label, touch ≥44px)
- [ ] Performa (halaman ≤2s, kalender 6×6 ≤2s)

## S7 — Cutover & Stabilisasi (P0)
- [ ] Parallel run 2 minggu
- [ ] Freeze 1 minggu sebelum semester
- [ ] Go/no-go checklist
- [ ] Fallback & rollback
- [ ] Pelatihan pengguna
- [ ] Perbaikan temuan
- [ ] M1–M9 terukur

## S8 — Fondasi Teknis (P1)
- [ ] Scheduler jobs (reminder, backup, cleanup) — APScheduler
- [ ] Email templates (Jinja2)
- [ ] File storage (local/S3) + validasi tipe/ukuran
- [ ] Import framework (BaseImporter, preview, commit, rollback)
- [ ] Exporter (PDF jadwal, laporan bulanan, XLSX/CSV)
- [ ] CI/CD (GitHub Actions: lint, test, build)
- [ ] Seed data dari template CSV (lab, komponen, vendor, social accounts, settings)

## S9 — Fase 2 (P2)
- [ ] Peran terbatas asisten lab
- [ ] Pengajuan pemakaian lab oleh dosen + approval
- [ ] Label/QR per unit (Fase 2)
- [ ] Pencatatan analitik manual (medsos)
- [ ] Perbandingan semester
- [ ] Mode baca offline

## S10 — Fase 3 (P2)
- [ ] Auto-publish medsos (API)
- [ ] Integrasi SIAKAD
- [ ] Penerbitan berita acara / sertifikat
- [ ] Prediksi perawatan

---

## Prioritas eksekusi (urutan yang disarankan)
1. S1 (Inventaris) — fondasi data
2. S2 (Kerusakan) — bergantung inventaris
3. S3 (Penjadwalan) — independen, bisa paralel dengan S2
4. S4 (Media Sosial) — independen
5. S5 (Pelaporan) — bergantung S1–S4
6. S6 (Fondasi & NFR) — sepanjang jalan
7. S7 (Cutover) — setelah S1–S6

## Catatan
- Backend service & router sudah ada (stub nyata, bukan kosong). Task di atas fokus pada **UI, alur end-to-end, dan fitur yang belum diimplementasi**.
- Setiap modul harus lulus Acceptance Criteria di PRD 10.1–10.7 sebelum rilis.
- Update status task di file ini saat selesai (ubah `[ ]` → `[x]`).