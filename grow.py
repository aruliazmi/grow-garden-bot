import asyncio
import aiohttp
from datetime import datetime, timezone
from telegram import Bot
from telegram.constants import ParseMode
import pytz

BOT_TOKEN = "7263493594:AAH30QT4R-Dpng5DA0GYGAoUQqYp21p6miA"
CHANNEL_ID = "@growgardeninfoo"

RARE_ITEMS = {
    "Master Sprinkler", "Tanning Mirror", "Friendship Pot",
    "Feijoa", "Loquat", "Prickly Pear", "Sugar Apple",
    "Rare Summer Egg", "Paradise Egg", "Mythical Egg", "Bug Egg", "Legendary Egg"
}

API_STOCK = "http://147.93.156.4:2504/api/stock/GetStock"
API_TIMER = "http://147.93.156.4:2504/api/stock/restock-time"

tz = pytz.timezone("Asia/Jakarta")
bot = Bot(BOT_TOKEN)

last_message_id = None
last_rare_alert_id = None
last_rare_alerts = set()

def format_countdown(timestamp):
    now = datetime.now(timezone.utc).timestamp() * 1000
    try:
        remain = max(0, int(float(timestamp) - now) // 1000)
        h, m, s = remain // 3600, (remain % 3600) // 60, remain % 60
        return remain, f"{h:02d}:{m:02d}:{s:02d}"
    except:
        return 0, "00:00:00"

async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            return await res.json()

def extract_emoji_map(last_seen):
    emoji_map = {}
    for section in last_seen.values():
        for item in section:
            emoji_map[item["name"]] = item.get("emoji", "📦")
    return emoji_map

async def build_message(stock, timers, emoji_map):
    lines = ["<b>🧺 Stock Saat Ini</b>"]
    display_map = {
        "gearStock": "🔧 Gears",
        "eggStock": "🥚 Eggs",
        "seedsStock": "🌱 Seeds"
    }

    for key, title in display_map.items():
        if key in stock and stock[key]:
            lines.append(f"\n<b>{title}</b>")
            for item in stock[key]:
                name = item["name"]
                value = item["value"]
                emoji = emoji_map.get(name, "📦")
                lines.append(f"{emoji} {name} x{value}")

    lines.append("\n<b>⏳ Countdown Restock</b>")
    countdown_map = {
        "gears": "gear",
        "eggs": "egg",
        "seeds": "seeds"
    }

    global_timeleft = []

    for label, key in countdown_map.items():
        if key in timers:
            timeleft, text = format_countdown(timers[key].get("timestamp", 0))
            lines.append(f"{label.capitalize()}: {text}")
            global_timeleft.append(timeleft)

    current_time = datetime.now(tz).strftime("%H:%M:%S")
    lines.append(f"\n<i>Update: {current_time} WIB</i>")

    return "\n".join(lines), min(global_timeleft or [0]) 

async def alert_rare_items(stock, emoji_map):
    global last_rare_alerts, last_rare_alert_id

    current_rares = {}
    for section in ["gearStock", "eggStock", "seedsStock"]:
        for item in stock.get(section, []):
            name = item["name"]
            value = item.get("value", 1)
            if name in RARE_ITEMS:
                current_rares[name] = value

    current_set = set(current_rares.keys())

    if current_set != last_rare_alerts:
        if last_rare_alert_id:
            try:
                await bot.delete_message(CHANNEL_ID, last_rare_alert_id)
                print("[RARE] Pesan lama dihapus karena ada perubahan rare.")
            except:
                pass
            last_rare_alert_id = None

        if current_rares:
            try:
                text_parts = []
                for name, qty in current_rares.items():
                    emoji = emoji_map.get(name, "🌟")
                    text_parts.append(f"{emoji} <b>{name}</b>")
                notif_text = "🚨 Rare Item Restock: " + ", ".join(text_parts) + " baru saja muncul!"

                msg = await bot.send_message(
                    CHANNEL_ID,
                    notif_text,
                    parse_mode=ParseMode.HTML
                )
                last_rare_alert_id = msg.message_id
                print("[RARE] Notifikasi dikirim ulang:", notif_text)
            except Exception as e:
                print(f"[RARE ERROR] {e}")

        last_rare_alerts = current_set

async def update_loop():
    global last_message_id
    restock_handled = False

    while True:
        try:
            stock = await fetch_json(API_STOCK)
            timers = await fetch_json(API_TIMER)

            if not stock or not timers:
                print("[WARNING] Data kosong, skip loop.")
                await asyncio.sleep(5)
                continue

            emoji_map = extract_emoji_map(stock.get("lastSeen", {}))
            message, min_left = await build_message(stock, timers, emoji_map)
            is_restock = min_left <= 10

            if is_restock and last_message_id and not restock_handled:
                try:
                    await bot.delete_message(CHANNEL_ID, last_message_id)
                    print("[INFO] Pesan utama dihapus (restock). Menunggu reset...")
                except Exception as e:
                    print(f"[WARNING] Gagal hapus pesan utama: {e}")
                last_message_id = None
                restock_handled = True

            if restock_handled and min_left < 300 and not last_message_id:
                try:
                    msg = await bot.send_message(CHANNEL_ID, message, parse_mode=ParseMode.HTML)
                    last_message_id = msg.message_id
                    restock_handled = False
                    print("[INFO] Pesan utama dikirim ulang setelah reset restock.")
                except Exception as e:
                    print(f"[ERROR] Gagal kirim pesan utama setelah restock: {e}")

            if not last_message_id and not restock_handled:
                try:
                    msg = await bot.send_message(CHANNEL_ID, message, parse_mode=ParseMode.HTML)
                    last_message_id = msg.message_id
                    print("[INFO] Pesan utama pertama dikirim.")
                except Exception as e:
                    print(f"[ERROR] Gagal kirim pesan utama pertama: {e}")

            elif not is_restock and last_message_id:
                try:
                    await bot.edit_message_text(message, CHANNEL_ID, last_message_id, parse_mode=ParseMode.HTML)
                    print("[INFO] Pesan utama di-edit (update countdown).")
                except Exception as e:
                    print(f"[WARNING] Edit pesan gagal: {e}")

            await alert_rare_items(stock, emoji_map)

        except Exception as e:
            print(f"[FATAL LOOP] {e}")

        await asyncio.sleep(5)
        
if __name__ == "__main__":
    try:
        asyncio.run(update_loop())
    except Exception as e:
        print(f"[FATAL MAIN ERROR] {e}")
