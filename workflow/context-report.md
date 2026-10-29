# Laporan Konteks — Aplikasi Operasional Laboratorium Ilmu Komputer (ITG)

> Dokumen ini adalah keluaran **上下文收集报告** (laporan pengumpulan konteks) yang menjadi dasar `workflow/prd.md`.
> Tanggal pemindaian: 2026-10-25. Metode: pembacaan langsung file workspace (Python + openpyxl / pdfplumber), bukan asumsi.
>
> **Catatan revisi (2026-10-25):** angka pada laporan ini adalah hasil pemindaian awal. Setelah verifikasi ulang pada revisi PRD v1.1, angka yang berlaku dan menjadi acuan tunggal adalah **Tabel Konsistensi Angka di `prd.md` §2.7** (mis. 185 baris = 174 entri unik; 74 baris = 70 sesi + 4 blok maintenance; 34 file PSD). Jika terjadi perbedaan, §2.7 menang.

## 上下文收集报告

### 1. 扫描范围与方法

| Item | Keterangan |
|------|------------|
| Root yang dipindai | `D:\Koordinator Laboratorium ITG` (rekursif, 4.573 file) |
| Pola dokumen yang dicari | `*PRD*`, `*HLD*`, `*requirement*`, `*design*`, `*arsitektur*`, `*业务*`, `*proses*`, `*rule*`, `README*`, `package.json`, `pyproject.toml`, `*.sql`, `*.json`, `openapi*`, `swagger*` |
| Keyword konten yang dicari | `invent`, `asset`, `aset`, `stok`, `komponen`, `rusak`, `perbaikan`, `maintenance`, `servis`, `sistem`, `aplikasi`, `konten`, `kalender`, `media`, `feed` |
| Exclude | `node_modules`, `.git`, `dist`, `build`, `.venv` (tidak ada di workspace) |
| Hasil pola dokumen | **Tidak ada** PRD/HLD/OpenAPI/README/package.json/skema DB. Satu-satunya `.md` adalah `workflow/status.md` (status internal PRD Studio). |
| Komposisi file | 3.107 `.pdf`, 910 `.jpg`, 142 `.xlsx`, 113 `.jpeg`, 92 `.psd`, 57 `.png`, 52 `.txt`, 40 `.docx`, 28 `.xls`, 14 `.rar`, 10 `.pptx`, 7 `.zip`, 1 `.md` |
| Kesimpulan pemindaian | Proses operasional **masih manual berbasis spreadsheet, PDF, dan folder gambar**. Tidak ditemukan aplikasi, basis data, API, atau kode sumber milik laboratorium. |

Catatan: folder `Dokumen Online\LAMINFOKOM` (ribuan PDF) adalah berkas akreditasi/administrasi eksternal, **bukan** sistem laboratorium; tidak dibaca satu per satu dan tidak dipakai sebagai bukti kapabilitas.

### 2. 已读取的文档 (dokumen yang berhasil dibaca)

| Dokumen | Tipe | Informasi kunci yang didapat |
|---------|------|------------------------------|
| `Dokumen Online\kalender konten media jurusan ilmu komputer.xlsx` | Kalender konten (Excel) | 1 sheet `2021-2022`, 238 baris; **168 baris konten** Des 2021–Nov 2022. Kolom: No, Konten/Kegiatan, Tanggal, Status, Target, Keterangan. Status: `Menunggu Konfirmasi` 143, `Di Jadwalkan` 16, `Di Terima` 9. Keterangan: `Menunggu` 164, `Gagal` 2, `Terupload` 2. Tidak ada kolom akun/prodi → satu kalender untuk semua akun. |
| `Jadwal\jadwal lab ilkom 2021-2.xlsx` | Jadwal lab (Excel) | Sheet `Jadwal`, `Labkom 1`, `Labkom 2`, `STI`, `Jaringan`; grid hari × jam (08.00-10.30, 10.30-13.00, 13.00-15.30, 16.00-18.30), blok tanda tangan Koordinator Lab. |
| `Jadwal\2021 GENAP\Penjadwalan\Gedung C Labkom 1.pdf` | Jadwal per ruang (PDF) | 1 halaman; 7 sesi praktikum/minggu (SENIN–SABTU), format: No, Hari, Waktu, Mata Kuliah, SMT, Kelas, Prodi; catatan aturan ruang + tanda tangan. |
| `Jadwal\2021 GENAP\Penjadwalan\jadwal lab ILKOM 2021-2022 genap.pdf` | Jadwal praktikum jurusan (PDF) | Matriks 4 ruang (C-II-Lab1, C-II-Lab2, D-II-Lab1, D-II-Lab2) × kelas; tiap baris memuat kode MK, dosen/instruktur/asisten, kelas, hari, jam. |
| `Jadwal\2025-2026 GANJIL\5 Jadwal penggunaan ruangan\jadwal penggunaan lab 2025-2026 ganjil.xlsx` | Jadwal 6 ruang (Excel) | 6 sheet: `C101`, `C102`, `C201`, `C202`, `D201`, `D202`. **74 entri sesi/minggu**, termasuk **4 blok "Maintenance dan Pengecekan Fasilitas Laboratorium"** yang ditulis sebagai baris jadwal. Catatan khusus: `D-II-02` hanya untuk praktikum jaringan, robotika, dan IoT. |
| `Jadwal\2025-2026 GANJIL\4 Jadwal Praktikum ILKOM\Jadwal Praktikum Jurusan ILKOM Semester Ganjil T.A 2025 - 2026.pdf` | Jadwal praktikum (PDF) | Daftar per kelas: Prodi, SMT, kode, nama MK, SKS, jenis, kelas, dosen, hari, jam, ruang. Sumber acuan bentrok (dosen/kelas/ruang). |
| `Jadwal\2024 GANJIL\Berita Acara Praktikum\INF Berita Acara Praktikum 2024-2025 Ganjil.xlsx` | Berita acara (Excel) | Sheet `Template` + satu sheet per kelas (DP A–E, STI A–D, …). Template 122 baris: identitas MK/dosen/instruktur/asisten, tabel pertemuan (materi, durasi 1 SKS, jam awal/akhir, pelaksana, paraf). |
| `Jadwal\2023 GENAP\Berita Acara Praktikum\Praktikum Basis Data A.pdf` | Berita acara (PDF) | Form resmi `FAA-ITG-A.13/01`, 3 halaman; laboratorium `C-II-LAB1`; kolom paraf instruktur/asisten, ketua kelas, dosen, monitoring prodi/koordinator lab. **30 PDF berita acara** di folder 2023 Genap. |
| `Jadwal\2025-2026 GANJIL\0 Penjadwalan\0 peta waktu saa.txt` | Catatan (TXT) | Grid jam tidak seragam: `07.10`, `08.00-10.50`, `08.30-11.20`, `11.20-14.10`, `14.40-17.30`, `07.10-10.00`, dst. |
| `Jadwal\2024 GANJIL\Penjadwalan\rapat 10-08-2024.txt` | Catatan rapat (TXT) | Negosiasi bentrok manual per dosen: *"bu fitri : TBO selasa jam 2 bisa pindah ke rabu pagi? [tidak bisa, karena bentrok dengan jadwal teori grafkom bu sri]"*, *"pak elsen : prk. pbo dipindah ke sabtu. [tidak bisa, jadwal lab sabtu enuh]"*. |
| `Jadwal\2023 GANJIL\0 note 2023.txt` | Catatan (TXT) | Daftar permintaan perubahan jadwal per dosen, termasuk *"jadwal beririsan teori dan praktikum"*. |
| `Dokumen Online\Template\*` (92 `.psd`) | Aset desain | Template ucapan skripsi, kegiatan, recruitment aslab, frame IG, logo, virtual background. Tidak ada metadata/index. |
| `Dokumen Online\IG Post\` (829 file, 39 folder) | Arsip konten | Folder per bulan/tahun dengan penamaan tidak konsisten: `Agustus 2026`, `ARSIP 2022\juli 2022`, `ARSIP 2022\nOVEMBER 2022`, `September 2026`, `Juli 20206`, `New folder`. Nama file dominan foto bernomor/nama orang; tidak ada caption/tautan konten. |
| `ITS\Absen ITS 2026.xlsx`, `ITS\Absen ITS 2026.pdf`, `ITS\Absen ITS 2026 Teknik Informatika.pdf`, `ITS\Absen ITS 2026 Sistem Informasi.pdf`, `ITS\DAFTAR PESERTA PELATIHAN ITS 2025.pdf` | Administrasi pelatihan | 239 file di folder ITS; absensi per prodi, daftar peserta, sertifikat per peserta (ratusan PDF), ID card, tanda tangan pimpinan. |

### 3. 未能读取 / 未验证

| Objek | Alasan | Dampak pada PRD |
|-------|--------|-----------------|
| 92 file `.psd`, 14 `.rar`, 7 `.zip`, gambar `.jpg/.png` | Format biner desain/arsip; tidak dibuka | Tidak ada klaim isi; hanya dipakai sebagai bukti keberadaan aset dan pola penamaan. |
| 3.107 PDF (mayoritas `LAMINFOKOM`) | Volume besar, di luar domain lab | Tidak dibaca; tidak dipakai sebagai bukti. |
| Isi rinci tiap berita acara (kehadiran/paraf) | Form kosong/scan; tidak relevan untuk PRD | Tidak diklaim. |
| Data historis kerusakan/perbaikan | **Tidak ada file** | Baseline MTTR tidak tersedia → metrik memakai cara pengukuran, bukan angka historis. |

### 4. 识别的项目约定

- **Tidak ada tech stack** yang bisa diidentifikasi: tidak ada `package.json`, `pyproject.toml`, `go.mod`, `README`, `.sql`, atau folder `src/`.
- **Konvensi dokumen**: hasil kerja berupa Excel (pengolahan) → PDF (pengesahan); setiap dokumen jadwal diakhiri blok *"Garut, <tanggal> / Koordinator Laboratorium Jurusan Ilmu Komputer / ttd"*.
- **Struktur kerja**: folder per tahun akademik (`2021 GENAP` … `2026-2027 GANJIL`) dengan sub-folder berpola `0 Penjadwalan`, `1 Open Recruitment`, `2 Berita Acara`, `3 Instruktur dan Asisten`, `4 Jadwal Praktikum`, `5 Jadwal penggunaan ruangan`, `6/8 Sertifikat`. Pola ini konsisten sejak 2023 dan layak dipertahankan sebagai struktur arsip.
- **Konvensi penamaan**: tidak konsisten — 22 file mengandung `Copy`; versi ditandai `REV 1/2/3`, `student day v2/v3/v4`, `sorting baru`, `Copy - Copy - Copy`.
- **Penamaan ruang tidak konsisten antar tahun**: `Labkom 1`, `Labkom 2`, `STI`, `Jaringan`, `MM` (2021/2022) vs `C-I-01`, `C-I-02`, `C-II-01`, `C-II-02`, `D-II-01`, `D-II-02` (2025/2026) vs `C-II-LAB1` (berita acara 2023).
- **Grid slot tidak konsisten**: `08.00-10.30`, `08.00-10.50`, `10.40-13.30`, `08.50-11.40`, `12.10-14.40` muncul di dokumen berbeda.

### 5. 相关能力识别

| 已有能力 | 能力范围 | 与本需求匹配度 | 能力差距 | 建议方向 | 来源 |
|----------|----------|----------------|----------|----------|------|
| Kalender konten media sosial (Excel) | Perencanaan konten 12 bulan, status, target feed/timeline | Sebagian | Tanpa pemisahan 4 akun, tanpa siklus status baku, tanpa pengingat, tanpa arsip caption/aset tertaut, 164/168 item masih `Menunggu` | Ganti dengan modul konten terstruktur; migrasi 168 baris sebagai data awal | `Dokumen Online\kalender konten media jurusan ilmu komputer.xlsx` |
| Jadwal penggunaan lab per ruang (Excel + PDF) | Grid hari × jam per ruang, 6 ruang, termasuk blok maintenance | Sebagian | Validasi bentrok manual, tanpa versi/resolusi konflik, nama ruang berubah antar tahun, maintenance ditulis sebagai "kelas" | Ganti dengan penjadwalan tervalidasi + master ruang ber-alias | `Jadwal\2025-2026 GANJIL\5 Jadwal penggunaan ruangan\jadwal penggunaan lab 2025-2026 ganjil.xlsx`; `Jadwal\2021 GENAP\Penjadwalan\Gedung C Labkom 1.pdf` |
| Jadwal praktikum jurusan per kelas (PDF) | Daftar sesi praktikum: MK, kelas, dosen, hari, jam, ruang | Sebagian | Diturunkan manual dari beberapa file; rawan tidak sinkron dengan jadwal per ruang | Jadikan keluaran otomatis dari data sesi | `Jadwal\2025-2026 GANJIL\4 Jadwal Praktikum ILKOM\Jadwal Praktikum Jurusan ILKOM Semester Ganjil T.A 2025 - 2026.pdf` |
| Berita acara pelaksanaan praktikum (Excel/PDF) | Bukti pelaksanaan per kelas per pertemuan, tanda tangan berlapis | Tidak cocok untuk MVP | Dokumen resmi bertanda tangan; tidak terhubung ke jadwal/kehadiran; dibuat manual per kelas (30 PDF/semester) | Di luar MVP; integrasi penerbitan dokumen di Fase 3 | `Jadwal\2024 GANJIL\Berita Acara Praktikum\INF Berita Acara Praktikum 2024-2025 Ganjil.xlsx`; `Jadwal\2023 GENAP\Berita Acara Praktikum\Praktikum Basis Data A.pdf` |
| Arsip aset desain & template | 92 template `.psd` + 829 file arsip di 39 folder | Sebagian | Tanpa metadata (akun, jenis, tanggal, caption), penamaan tidak baku, tidak dapat dicari | Modul arsip konten + migrasi bertahap; file tetap disimpan sebagai aset | `Dokumen Online\Template\`; `Dokumen Online\IG Post\` |
| Catatan negosiasi jadwal (TXT) | Permintaan pindah jadwal dosen + alasan bentrok | Sebagian | Tidak terstruktur, tidak terlacak, tidak terhubung ke jadwal | Ganti dengan log perubahan sesi + alasan | `Jadwal\2024 GANJIL\Penjadwalan\rapat 10-08-2024.txt`; `Jadwal\2023 GANJIL\0 note 2023.txt` |
| Administrasi pelatihan ITS (peserta, absensi, sertifikat) | 239 file: daftar peserta, absensi 2 prodi, sertifikat per peserta | Tidak cocok | Di luar 5 modul yang disepakati; beban manual tinggi tetapi bukan prioritas MVP | Catat sebagai kandidat Fase 3 (penerbitan sertifikat) | `ITS\Absen ITS 2026.xlsx`; `ITS\Sertifikat Kepesertaan ITS 2026\` |
| **Inventaris & kondisi komponen** | — | **Tidak ditemukan** | Tidak ada daftar unit, kode aset, kondisi, garansi, atau riwayat perbaikan | Bangun baru; mulai dari stock opname 2 lab prioritas | Hasil pemindaian: keyword `invent|asset|aset|stok|komponen|rusak|perbaikan` pada nama & isi file → 0 file inventaris; hanya catatan naratif di TXT |
| **Log kerusakan & perbaikan terstruktur** | — | **Tidak ditemukan** | Tidak ada tiket, status, biaya, atau MTTR | Bangun baru (modul kerusakan & perbaikan) | Pemindaian sama; tidak ada sheet/kolom kondisi alat di 142 `.xlsx` yang diperiksa sampel |
| **Sistem/aplikasi laboratorium** | — | **Tidak ditemukan** | Tidak ada kode, DB, API, atau aplikasi | Bangun baru (web responsif) | Pemindaian `README*`, `package.json`, `*.sql`, `openapi*` → 0 hasil; komposisi file 100% dokumen/aset |

### 6. 未找到信息的领域 (perlu dilengkapi saat implementasi/HLD)

- Jumlah unit komponen per lab, tahun pengadaan, garansi, dan nilai aset.
- Data historis kerusakan, biaya perbaikan, dan vendor/mitra resmi.
- Apakah laboratorium memiliki alat khusus (IoT, robotika, jaringan) yang perlu validasi ketersediaan per sesi.
- Pemilik kredensial 4 akun media sosial dan kebijakan persetujuan konten (single approver atau ada Kaprodi).
- Format resmi laporan bulanan yang diharapkan pimpinan.
- Ketersediaan hosting/domain/email institusi dan kebijakan backup kampus.
- Apakah jadwal teori (non-lab) juga perlu dikelola atau cukup praktikum/penggunaan lab.

### 7. 业界实践参考

Tidak dilakukan pencarian eksternal. Alasan: kebutuhan sangat spesifik pada satu unit kerja (single-user, 6 lab, 4 akun prodi) dan seluruh keputusan scope sudah ditetapkan pengguna; referensi industri berisiko menambah scope tanpa bukti internal. Bagian ini dapat dilengkapi pada iterasi PRD berikutnya bila diperlukan.

### 8. 证据摘要 (angka yang dipakai di PRD)

| Fakta | Angka | Sumber |
|-------|-------|--------|
| Ruang/lab dikelola (TA 2025/2026 Ganjil) | 6 ruang | `jadwal penggunaan lab 2025-2026 ganjil.xlsx` (sheet C101–D202) |
| Sesi terjadwal per minggu | 74 entri | perhitungan baris ber-hari pada file yang sama |
| Blok maintenance ditulis sebagai baris jadwal | 4 blok | file yang sama (C201, C202, D201, D202) |
| Berita acara praktikum per semester | 30 PDF | `Jadwal\2023 GENAP\Berita Acara Praktikum\` |
| Item kalender konten | 168 item; 143 menunggu konfirmasi; hanya 2 terupload | `kalender konten media jurusan ilmu komputer.xlsx` |
| Arsip konten IG | 829 file, 39 folder, 0 metadata caption | `Dokumen Online\IG Post\` |
| Template desain | 92 `.psd` | `Dokumen Online\Template\` |
| Duplikasi file kerja | 22 file mengandung `Copy`; 6 varian `Ploting Pengajaran ILKOM 2025-2026 Ganjil` | pemindaian nama file `Jadwal\` |
| Folder semester yang diarsipkan | 10 tahun akademik (2021 Genap – 2026/2027 Ganjil) | `Jadwal\` |
| File administrasi ITS | 239 file | `ITS\` |
