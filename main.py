# -*- coding: utf-8 -*-
import logging
import random
import time
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8945348020:AAHA3sWDRNIGdUhVo6gZ39wdUCBF2uHdcFw"
users_data = {}

HUNT_COOLDOWN = 15
BATTLE_COOLDOWN = 15
DAILY_COOLDOWN = 24 * 60 * 60
PRAY_COOLDOWN = 5 * 60
STEAL_COOLDOWN = 10 * 60

ANIMALS = {
    "C": ["🐶 Kopek", "🐱 Kedi", "🐰 Tavsan", "🦊 Tilki", "🐭 Fare", "🐸 Kurbaga", "🐷 Domuz", "🐹 Hamster"],
    "U": ["🐻 Ayi", "🐼 Panda", "🦁 Aslan", "🐯 Kaplan", "🐺 Kurt", "🦅 Kartal", "🐵 Maymun", "🐨 Koala"],
    "R": ["🦄 Tekboynuz", "🐉 Ejderha", "🐙 Kraken", "🦅🔥 Anka Kusu", "🦖 T-Rex", "🐬 Yunus"],
    "E": ["🐫 Zumrut Deve", "🦍 Elmas Goril", "🐘 Safir Fil", "🦈 Yakut Kopekbaligi"],
    "M": ["👑 Kozmik Ejderha", "🌟 Galaksi Balinasi", "🔥 Yildirim Anka"],
    "L": ["✨ Tanrisal Kutsal Emanet", "🌌 Bosluk Leviathani"]
}

ANIMAL_PRICES = {"C": 15, "U": 35, "R": 100, "E": 300, "M": 1000, "L": 5000}
ANIMAL_TO_RARITY = {}
for rarity, items in ANIMALS.items():
    for item in items:
        ANIMAL_TO_RARITY[item] = rarity

def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.translate(str.maketrans({'ş': 's', 'Ş': 's', 'ğ': 'g', 'Ğ': 'g', 'ü': 'u', 'Ü': 'u', 'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c', 'ı': 'i', 'I': 'i', 'İ': 'i'})).lower().strip()

def get_user_data(user_id, first_name="Kullanici"):
    if user_id not in users_data:
        users_data[user_id] = {
            "name": first_name, "cowoncy": 1000, "zoo": {},
            "inventory": {"yaygin kutu": 2, "siradisi kutu": 1, "nadir kutu": 1, "kurabiye": 2, "sans tasi": 1},
            "last_hunt": 0, "last_battle": 0, "last_daily": 0, "last_pray": 0, "last_steal": 0,
            "luck_boost": 1.0, "luck_until": 0, "stats": {"wins": 0, "losses": 0}
        }
    else:
        users_data[user_id]["name"] = first_name
    return users_data[user_id]

def check_luck(data):
    if time.time() > data.get("luck_until", 0):
        data["luck_boost"] = 1.0
    return data["luck_boost"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user_data(user.id, user.first_name)
    await update.message.reply_html(
        f"🌸✨ <b>| OwO Bota Hos Geldin {user.first_name}!</b> ✨🌸\n\n"
        "🎮 <b>Komutlar:</b> /hunt, /sell, /pray, /use, /zoo, /cash, /daily, /inventory, /lootbox, /cf, /slots, /bj, /battle, /top, /pay, /steal"
    )

async def pray(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    now = time.time()
    if now - data["last_pray"] < PRAY_COOLDOWN:
        await update.message.reply_html(f"⏳ Beklemelisin: {int(PRAY_COOLDOWN - (now - data['last_pray']))}s")
        return
    data["last_pray"] = now
    data["luck_boost"] = 1.3
    data["luck_until"] = now + 300
    await update.message.reply_html(f"🙏✨ {user.first_name} dua etti! 5 dakika boyunca sansin x1.3!")

async def use_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    if not context.args:
        await update.message.reply_html("⚠️ Kullanim: /use <kurabiye / sans tasi>")
        return
    q = clean_text(" ".join(context.args))
    key, boost, duration, name = ("kurabiye", 1.5, 1800, "🍪 Kurabiye") if "kurabiye" in q else ("sans tasi", 2.0, 3600, "💎 Sans Tasi") if "sans" in q else (None, 0, 0, "")
    if not key or data["inventory"].get(key, 0) <= 0:
        await update.message.reply_html("❌ Envanterinde bu esyadan yok!")
        return
    data["inventory"][key] -= 1
    data["luck_boost"] = boost
    data["luck_until"] = time.time() + duration
    await update.message.reply_html(f"✨ {name} kullanildi! Sansin x{boost} oldu.")

async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    now = time.time()
    if now - data["last_hunt"] < HUNT_COOLDOWN:
        await update.message.reply_html(f"⏳ Bekle: {int(HUNT_COOLDOWN - (now - data['last_hunt']))}s")
        return
    data["last_hunt"] = now
    luck = check_luck(data)
    chance = random.randint(1, 1000)
    code, name = ("C", "Yaygin") if chance <= int(500/luck) else ("U", "Nadir Degil") if chance <= int(800/luck) else ("R", "Nadir") if chance <= int(940/luck) else ("E", "Epik") if chance <= int(985/luck) else ("M", "Mitolojik") if chance <= int(998/luck) else ("L", "Efsanevi")
    animal = random.choice(ANIMALS[code])
    coins = random.randint(30, 90) if code in ["C", "U"] else random.randint(150, 800)
    data["zoo"][animal] = data["zoo"].get(animal, 0) + 1
    data["cowoncy"] += coins
    await update.message.reply_html(f"🌿 {user.first_name} bir <b>{animal}</b> yakaladi! [{name}] (+{coins} Cowoncy)")

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    if not data["zoo"] or sum(data["zoo"].values()) == 0:
        await update.message.reply_html("🏚️ Satacak hayvanin yok!")
        return
    if not context.args:
        await update.message.reply_html("⚠️ Kullanim: /sell all veya /sell C/R vb.")
        return
    target = clean_text(context.args[0]).upper()
    total, count = 0, 0
    for animal, c in list(data["zoo"].items()):
        if c > 0 and (target == "ALL" or ANIMAL_TO_RARITY.get(animal) == target):
            total += c * ANIMAL_PRICES.get(ANIMAL_TO_RARITY.get(animal, "C"), 15)
            count += c
            data["zoo"][animal] = 0
    if count == 0:
        await update.message.reply_html("❌ Satilacak hayvan bulunamadi!")
        return
    data["cowoncy"] += total
    await update.message.reply_html(f"💵 {count} hayvan satildi, +{total} Cowoncy kazandin!")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    if time.time() - data["last_daily"] < DAILY_COOLDOWN:
        await update.message.reply_html("⏱️ Gunluk odulunu zaten aldin!")
        return
    data["last_daily"] = time.time()
    data["cowoncy"] += 1500
    data["inventory"]["nadir kutu"] = data["inventory"].get("nadir kutu", 0) + 1
    await update.message.reply_html("🎁 Gunluk odul: +1500 Cowoncy ve +1 Nadir Kutu!")

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    inv = get_user_data(user.id, user.first_name)["inventory"]
    msg = "📦 <b>Envanterin:</b>\n" + "".join([f"• {k}: x{v}\n" for k, v in inv.items() if v > 0])
    await update.message.reply_html(msg)

async def lootbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    if not context.args:
        await update.message.reply_html("⚠️ Kullanim: /lootbox <yaygin/nadir>")
        return
    q = clean_text(" ".join(context.args))
    key = q if q.endswith("kutu") else f"{q} kutu"
    if data["inventory"].get(key, 0) <= 0:
        await update.message.reply_html("❌ Bu kutudan yok!")
        return
    data["inventory"][key] -= 1
    coins = random.randint(300, 900)
    data["cowoncy"] += coins
    await update.message.reply_html(f"🎉 Kutu acildi: +{coins} Cowoncy kazandin!")

async def zoo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    z = {k: v for k, v in get_user_data(user.id, user.first_name)["zoo"].items() if v > 0}
    if not z:
        await update.message.reply_html("🏚️ Hayvanat bahcen bombos!")
        return
    msg = "📜 <b>Hayvanat Bahcen:</b>\n" + "".join([f"• {k}: x{v}\n" for k, v in z.items()])
    await update.message.reply_html(msg)

async def cash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    await update.message.reply_html(f"💳 <b>{user.first_name} Profili</b>\n💰 Para: {data['cowoncy']} c!")

async def coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    if len(context.args) < 2:
        await update.message.reply_html("⚠️ Kullanim: /cf <miktar> <yazi/tura>")
        return
    amount = data["cowoncy"] if context.args[0].lower() == "all" else int(context.args[0])
    if amount <= 0 or data["cowoncy"] < amount:
        await update.message.reply_html("⚠️ Yetersiz bakiye!")
        return
    data["cowoncy"] -= amount
    win = random.choice([True, False])
    if win:
        data["cowoncy"] += amount * 2
        await update.message.reply_html(f"🪙 Kazandin! +{amount} Cowoncy!")
    else:
        await update.message.reply_html(f"🪙 Kaybettin! -{amount} Cowoncy.")

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    if not context.args:
        await update.message.reply_html("⚠️ Kullanim: /s <miktar>")
        return
    amount = int(context.args[0])
    if amount <= 0 or data["cowoncy"] < amount:
        await update.message.reply_html("⚠️ Yetersiz bakiye!")
        return
    data["cowoncy"] -= amount
    symbols = ["💎", "🎰", "🔔", "🍋", "7️⃣"]
    s1, s2, s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
    if s1 == s2 == s3:
        data["cowoncy"] += amount * 5
        await update.message.reply_html(f"🎰 [ {s1} | {s2} | {s3} ]\n🔥 JACKPOT! +{amount*5} Cowoncy!")
    elif s1 == s2 or s2 == s3:
        data["cowoncy"] += amount * 2
        await update.message.reply_html(f"🎰 [ {s1} | {s2} | {s3} ]\n✨ Cifte Eslesme! +{amount*2} Cowoncy!")
    else:
        await update.message.reply_html(f"🎰 [ {s1} | {s2} | {s3} ]\n❌ Kaybettin!")

async def blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    if not context.args:
        await update.message.reply_html("⚠️ Kullanim: /bj <miktar>")
        return
    amount = int(context.args[0])
    if amount <= 0 or data["cowoncy"] < amount:
        await update.message.reply_html("⚠️ Yetersiz bakiye!")
        return
    data["cowoncy"] -= amount
    if random.choice([True, False]):
        data["cowoncy"] += amount * 2
        await update.message.reply_html(f"🃏 Blackjack Kazandin! +{amount} Cowoncy!")
    else:
        await update.message.reply_html(f"🃏 Kurpiyer kazandi! -{amount} Cowoncy.")

async def battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    if time.time() - data["last_battle"] < BATTLE_COOLDOWN:
        await update.message.reply_html("⏳ Dinlenmelisin!")
        return
    data["last_battle"] = time.time()
    if random.choice([True, False]):
        reward = 100
        data["cowoncy"] += reward
        await update.message.reply_html(f"⚔️ Savasi kazandin! +{reward} Cowoncy!")
    else:
        data["cowoncy"] = max(0, data["cowoncy"] - 50)
        await update.message.reply_html("⚔️ Savasi kaybettin! -50 Cowoncy.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users_data:
        await update.message.reply_html("🏆 Kimse yok!")
        return
    top = sorted(users_data.items(), key=lambda x: x[1]["cowoncy"], reverse=True)[:5]
    msg = "🏆 <b>En Zenginler:</b>\n" + "".join([f"• {u['name']}: {u['cowoncy']} c\n" for _, u in top])
    await update.message.reply_html(msg)

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("💸 Para gonderme aktif.")

async def steal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("🥷 Soygun sistemi aktif.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    
    for cmd, func in [("start", start), ("hunt", hunt), ("sell", sell), ("use", use_item), ("pray", pray), ("zoo", zoo), ("cash", cash), ("daily", daily), ("inventory", inventory), ("lootbox", lootbox), ("cf", coinflip), ("slots", slots), ("bj", blackjack), ("battle", battle), ("top", leaderboard), ("pay", pay), ("steal", steal)]:
        app.add_handler(CommandHandler(cmd, func))

    print("OwO Bot Calisiyor!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
      
