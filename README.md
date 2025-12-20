# 🤖 Otomasi Absen SISAK

Tool otomasi untuk mencatat kehadiran (presensi) dan capaian pembelajaran di sistem SISAK secara otomatis. Buat hidup lebih mudah dengan mengotomasi pengisian absensi tanpa perlu buka web!

## ✨ Fitur Utama

- 🔐 **Login Otomatis** - Autentikasi ke sistem SISAK menggunakan NIM dan password
- 📅 **Fleksibel Tanggal** - Support single day, date range, atau default hari ini
- ✅ **Absen Otomatis** - Pencatatan status kehadiran (HADIR) untuk semua mata kuliah
- 🎯 **Capaian Otomatis** - Pengisian status capaian pembelajaran (SESUAI)
- 🔄 **Retry Otomatis** - Jika session habis atau koneksi error, script akan login ulang
- ⏱️ **Rate Limiting** - Delay antar request untuk keamanan
- 🛡️ **Error Handling** - Penanganan error yang user-friendly

## 📋 Requirements

- Python 3.7+
- Akun SISAK (NIM & password)
- Koneksi internet

## 🚀 Instalasi

### 1. Clone atau Download Project

```bash
git clone <repository-url>
cd otomasi_absen_sisak
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
```

### 3. Aktivasi Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 💻 Cara Pakai

### Jalankan Script

```bash
python script.py
```

### Masukkan Credentials

```
NIM   : 123456789
PASS  : ••••••••
KELAS : TI2K
```

### Pilih Tanggal

Script akan menampilkan format input:

```
--------------------------------------------------
 [?] INPUT FORMAT EXAMPLES:
     1. Today       : (Press Enter)
     2. Single Date : 2025-12-20
     3. Date Range  : 2025-12-20:2025-12-25
--------------------------------------------------

 Target Date > 
```

| Format | Contoh | Hasil |
|--------|--------|-------|
| **Kosong (Enter)** | `` | Absen hari ini |
| **Single Date** | `2025-12-20` | Absen tanggal 20 Desember 2025 |
| **Date Range** | `2025-12-20:2025-12-25` | Absen tanggal 20-25 Desember 2025 (6 hari) |

### Hasil Output

```
[*] Processing: 2025-12-20
    > Mata Kuliah 1
      [+] Marking Presence: HADIR
      [+] Marking Achievement: SESUAI
    > Mata Kuliah 2
      [+] Marking Presence: HADIR
      [+] Marking Achievement: SESUAI
[+] Done. Processed 2 subjects.
```

## 🔧 Konfigurasi (Opsional)

Edit `CONFIG` di `script.py` jika ingin customize:

```python
CONFIG = {
    "NIM": "",              # Kosongkan untuk input manual saat jalankan
    "PASS": "",             # Kosongkan untuk input manual saat jalankan
    "KELAS": "",            # Kosongkan untuk input manual saat jalankan
    "URL_BASE": "https://sisak1.polsri.ac.id/mahasiswa",
    "TIMEOUT": 30,          # Timeout request (detik)
    "RETRIES": 3            # Jumlah retry jika koneksi error
}
```

### Pre-fill Credentials (Opsional)

Jika malas input setiap kali, bisa langsung set credentials:

```python
CONFIG = {
    "NIM": "123456789",
    "PASS": "your_password",
    "KELAS": "TI2K",
    ...
}
```

⚠️ **Tips:** Jangan commit credentials ke git! Gunakan `.gitignore` atau hanya set saat jalankan.

## 📊 Arti Log Output

| Simbol | Arti |
|--------|------|
| `[*]` | Proses sedang berjalan |
| `[+]` | Sukses/berhasil |
| `[-]` | Tidak ada data |
| `[.]` | Sudah ada/skip |
| `[!]` | Warning/error |
| `[X]` | Gagal/skipped |

## 🐛 Troubleshooting

### ❌ Login Failed
```
[!] Login failed. Check credentials.
```
**Solusi:**
- Pastikan NIM dan password benar
- Periksa koneksi internet
- Pastikan akun tidak terkunci di sistem

### ❌ Session Invalid
```
[!] Session invalid. Attempting re-login...
```
**Solusi:**
- Normal, script akan otomatis login ulang
- Jika terus gagal, coba jalankan lagi

### ❌ No Schedule Found
```
[-] No schedule found for 2025-12-20.
```
**Solusi:**
- Hari libur atau tidak ada jadwal
- Periksa format tanggal (YYYY-MM-DD)

### ❌ Connection Timeout
```
[!] Connection error (1/3). Retrying...
```
**Solusi:**
- Periksa koneksi internet
- Script akan retry otomatis hingga 3x
- Tunggu beberapa saat lalu coba lagi

## 📦 Dependencies

Lihat `requirements.txt` untuk full list. Package yang sebenarnya dipakai:

- **requests** - HTTP client untuk request ke SISAK
- **urllib3** - HTTP library (included via requests)
- **certifi** - SSL certificate validation

Package lainnya adalah dependencies dari requests (auto-installed).

## 📝 Notes

- Tool ini dibuat untuk **automation purposes** dan **personal use**
- Gunakan dengan bijak dan sesuai aturan kampus
- Password di-input via `getpass` sehingga tidak terlihat di console/history
- Script akan otomatis handle session expiry dengan re-login

## 📄 License

Personal tool, bebas dimodifikasi sesuai kebutuhan.

---

**TL;DR:** Run script → input NIM/pass/kelas → pilih tanggal → selesai!

*Made for lazy students who don't want to open web browser* 😎
