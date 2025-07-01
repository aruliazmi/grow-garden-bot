# 🌾 GrowGarden Stock & Rare Alert Bot

Bot Telegram otomatis yang memantau stok dan item rare dari API GrowGarden.  
Fitur utama: menampilkan stok terkini dengan countdown restock, dan mengirim notifikasi saat item rare muncul.

## 📦 Fitur

- ✅ Update stok secara otomatis tiap 5 detik
- ⏳ Countdown restock untuk `Gears`, `Seeds`, dan `Eggs`
- 🌟 Notifikasi khusus saat item **RARE** muncul
- 🔄 Edit pesan utama jika countdown masih berjalan
- 🗑 Hapus dan kirim ulang pesan saat restock terjadi
- 🔔 Notifikasi rare dikirim ulang jika daftar rare berubah

## 🧠 Daftar Item Rare

```text
Master Sprinkler, Tanning Mirror, Friendship Pot,
Feijoa, Loquat, Prickly Pear, Sugar Apple,
Rare Summer Egg, Paradise Egg, Mythical Egg, Bug Egg, Legendary Egg
```

## 🚀 Instalasi

### 1. Clone repository

```bash
git clone https://github.com/username/grow-garden-bot.git
cd grow-garden-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi

Edit variabel berikut di dalam file Python:

```python
BOT_TOKEN = "TOKEN_BOT_ANDA"
CHANNEL_ID = "@channel_or_chat_id"
```

> ⚠️ Bot Anda harus menjadi admin di channel agar dapat mengirim dan menghapus pesan.

### 4. Jalankan

```bash
python3 bot.py
```

## 🛠 Struktur File

```bash
.
├── grow.py
├── requirements.txt 
└── README.md 
```

## 👨‍💻 Lisensi

Proyek ini bersifat open-source dan bebas digunakan untuk keperluan pribadi atau komunitas.  
Tidak diperbolehkan memperjualbelikan tanpa izin.

---

> Made with ❤️ by [Aruli Azmi]
