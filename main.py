# -*- coding: utf-8 -*-
import logging
import random
import time
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- BOT TOKEN ---
TOKEN = "8945348020:AAHA3sWDRNIGdUhVo6gZ39wdUCBF2uHdcFw"

users_data = {}

# --- SÜRELER (COOLDOWNS) ---
HUNT_COOLDOWN = 15            # 15 Saniye
BATTLE_COOLDOWN = 15          # 15 Saniye
DAILY_COOLDOWN = 24 * 60 * 60 # 24 Saat
PRAY_COOLDOWN = 5 * 60        # 5 Dakika
STEAL_COOLDOWN = 10 * 60      # 10 Dakika

# --- HAYVAN VERİTABANI & NADİRLİKLER & SATIŞ FİYATLARI ---
ANIMALS = {
    "C": ["🐶 Kopek", "🐱 Kedi", "🐰 Tavsan", "🦊 Tilki", "🐭 Fare", "🐸 Kurbaga", "🐷 Domuz", "🐹 Hamster"],
    "U": ["🐻 Ayi", "🐼 Panda", "🦁 Aslan", "🐯 Kaplan", "🐺 Kurt", "🦅 Kartal", "🐵 Maymun", "🐨 Koala"],
    "R": ["🦄 Tekboynuz", "🐉 Ejderha", "🐙 Kraken", "🦅🔥 Anka Kusu", "🦖 T-Rex", "🐬 Yunus"],
    "E": ["🐫 Zumrut Deve", "🦍 Elmas Goril", "🐘 Safir Fil", "🦈 Yakut Kopekbaligi"],
    "M": ["👑 Kozmik Ejderha", "🌟 Galaksi Balinasi", "🔥 Yildirim Anka"],
    "L": ["✨ Tanrisal Kutsal Emanet", "🌌 Bosluk Leviathani"]
}

ANIMAL_PRICES = {
    "C": 15,
    "U": 35,
    "R": 100,
    "E": 300,
    "M": 1000,
    "L": 5000
}

ANIMAL_TO_RARITY = {}
for rarity, items in ANIMALS.items():
    for item in items:
        ANIMAL_TO_RARITY[item] = rarity

def clean_text(text: str) -> str:
    """Turkce karakterleri Ingilizce karakterlere cevirir"""
    if not text:
        return ""
    return text.translate(str.maketrans({
        'ş': 's', 'Ş': 's', 'ğ': 'g', 'Ğ': 'g', 
        'ü': 'u', 'Ü': 'u', 'ö': 'o', 'Ö': 'o', 
        'ç': 'c', 'Ç': 'c', 'ı': 'i', 'İ': 'i'
    })).lower().strip()

def get_user_data(user_id, first_name="Kullanici"):
    if user_id not in users_data:
        users_data[user_id] = {
            "name": first_name,
            "cowoncy": 1000,
            "zoo": {},
            "inventory": {
                "yaygin kutu": 2, 
                "siradisi kutu": 1,
                "nadir kutu": 1,
                "kurabiye": 2, 
                "sans tasi": 1
            },
            "last_hunt": 0,
            "last_battle": 0,
            "last_daily": 0,
            "last_pray": 0,
            "last_steal": 0,
            "luck_boost": 1.0,
            "luck_until": 0,
            "stats": {"wins": 0, "losses": 0}
        }
    else:
        users_data[user_id]["name"] = first_name
    return users_data[user_id]

def check_luck(data):
    if time.time() > data.get("luck_until", 0):
        data["luck_boost"] = 1.0
    return data["luck_boost"]

# --- KOMUTLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user_data(user.id, user.first_name)
    caption = (
        f"🌸✨ <b>| OwO Bota Hos Geldin {user.first_name}!</b> ✨🌸\n\n"
        "🎮 <b>Komut Listesi:</b>\n"
        "• <code>/hunt</code>, <code>/h</code> ➔ 🌿 Hayvan Avla\n"
        "• <code>/sell all</code> veya <code>/sell &lt;C/U/R/E/M/L&gt;</code> ➔ 💵 Hayvan Sat\n"
        "• <code>/zoo</code> ➔ 📜 Hayvanat Bahcesi\n"
        "• <code>/cash</code> ➔ 💳 Cuzdan / Profil\n"
        "• <code>/daily</code> ➔ 🎁 Gunluk Odul (Para + Kutu)\n"
        "• <code>/pray</code> ➔ 🙏 Dua Et (Sansini Arttir)\n"
        "• <code>/inventory</code> ➔ 📦 Envanter\n"
        "• <code>/use &lt;kurabiye/sans tasi&gt;</code> ➔ ✨ Esya Kullan\n"
        "• <code>/lootbox &lt;kutu_adi&gt;</code> ➔ 🎁 Kutu Ac\n"
        "• <code>/cf &lt;miktar&gt; &lt;yazi/tura&gt;</code> ➔ 🪙 Yazi-Tura\n"
        "• <code>/slots &lt;miktar&gt;</code> ➔ 🎰 Slot Makinesi\n"
        "• <code>/bj &lt;miktar&gt;</code> ➔ 🃏 Blackjack\n"
        "• <code>/battle</code> ➔ ⚔️ Yaratik Savasi\n"
        "• <code>/pay &lt;kullanici_id&gt; &lt;miktar&gt;</code> ➔ 💸 Para Gonder\n"
        "• <code>/steal &lt;kullanici_id&gt;</code> ➔ 🥷 Hirsizlik Yap"
    )
    await update.message.reply_html(caption)

async def pray(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    now = time.time()
    
    if now - data["last_pray"] < PRAY_COOLDOWN:
        remaining = int(PRAY_COOLDOWN - (now - data["last_pray"]))
        await update.message.reply_html(f"⏳ <b>| {user.first_name}</b>, tekrar dua etmek icin <b>{remaining // 60} dakika</b> beklemelisin!")
        return

    data["last_pray"] = now
    data["luck_boost"] = 1.3
    data["luck_until"] = now + 300
    await update.message.reply_html(f"🙏✨ <b>{user.first_name}</b> dua etti! <b>5 dakika</b> boyunca sansin <b>x1.3</b> oldu!")

async def use_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)

    if not context.args:
        await update.message.reply_html("⚠️ <b>Kullanim:</b> <code>/use kurabiye</code> veya <code>/use sans tasi</code>")
        return

    item_query = clean_text(" ".join(context.args))
    
    if "kurabiye" in item_query:
        key, boost, duration, name = "kurabiye", 1.5, 1800, "🍪 Kurabiye (x1.5 Sans - 30dk)"
    elif "sans" in item_query:
        key, boost, duration, name = "sans tasi", 2.0, 3600, "💎 Sans Tasi (x2.0 Sans - 1 Saat)"
    else:
        await update.message.reply_html("❌ Gecersiz esya! Sadece <code>kurabiye</code> veya <code>sans tasi</code> kullanabilirsin.")
        return

    if data["inventory"].get(key, 0) <= 0:
        await update.message.reply_html(f"❌ Envanterinde hiç <b>{name}</b> yok!")
        return

    data["inventory"][key] -= 1
    data["luck_boost"] = boost
    data["luck_until"] = time.time() + duration

    await update.message.reply_html(f"✨ <b>{user.first_name}</b> bir <b>{name}</b> kullandi! Aktif sans carpanin: <b>x{boost}</b>")

async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    now = time.time()

    time_passed = now - data["last_hunt"]
    if time_passed < HUNT_COOLDOWN:
        remaining = int(HUNT_COOLDOWN - time_passed)
        await update.message.reply_html(f"⏳ <b>| {user.first_name}</b>, calilar henuz yenilenmedi! Kalan: <b>{remaining} saniye</b>")
        return

    data["last_hunt"] = now
    luck = check_luck(data)
    chance = random.randint(1, 1000)

    if chance <= int(500 / luck): code, name = "C", "Yaygin"
    elif chance <= int(800 / luck): code, name = "U", "Nadir Degil"
    elif chance <= int(940 / luck): code, name = "R", "Nadir"
    elif chance <= int(985 / luck): code, name = "E", "Epik"
    elif chance <= int(998 / luck): code, name = "M", "Mitolojik"
    else: code, name = "L", "Efsanevi"

    animal = random.choice(ANIMALS[code])
    coins = random.randint(30, 90) if code in ["C", "U"] else random.randint(150, 800)

    data["zoo"][animal] = data["zoo"].get(animal, 0) + 1
    data["cowoncy"] += coins

    text = f"🌿✨ <b>{user.first_name}</b> bir <b>{animal}</b> yakaladi! [{name}]\n💰 <b>+{coins}</b> Cowoncy kazandin!"
    
    if random.randint(1, 5) == 1:
        data["inventory"]["kurabiye"] = data["inventory"].get("kurabiye", 0) + 1
        text += "\n🍪✨ <b>Ayrica avlanirken 1 adet Kurabiye buldun!</b>"

    await update.message.reply_html(text)

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    zoo = data["zoo"]

    if not zoo or sum(zoo.values()) == 0:
        await update.message.reply_html(f"🏚️ <b>| {user.first_name}</b>, satacak hiç hayvanin yok!")
        return

    if not context.args:
        await update.message.reply_html("⚠️ <b>Kullanim:</b> <code>/sell all</code> veya <code>/sell C / R</code> vb.")
        return

    target = clean_text(context.args[0]).upper()
    total, count = 0, 0

    if target == "ALL":
        for animal, c in list(zoo.items()):
            if c > 0:
                rarity = ANIMAL_TO_RARITY.get(animal, "C")
                total += c * ANIMAL_PRICES.get(rarity, 15)
                count += c
                zoo[animal] = 0
    elif target in ANIMAL_PRICES:
        for animal, c in list(zoo.items()):
            if c > 0 and ANIMAL_TO_RARITY.get(animal) == target:
                total += c * ANIMAL_PRICES[target]
                count += c
                zoo[animal] = 0
    else:
        await update.message.reply_html("❌ Gecersiz kriter! <code>all</code> veya nadirlik harfi (C, U, R, E, M, L) yazmalisin.")
        return

    if count == 0:
        await update.message.reply_html("❌ Bu grupta satilacak hayvan bulunamadi!")
        return

    data["cowoncy"] += total
    await update.message.reply_html(f"💵✨ <b>{count}</b> hayvan satildi, toplam <b>+{total}</b> Cowoncy kazandin!")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    now = time.time()

    if now - data["last_daily"] < DAILY_COOLDOWN:
        remaining = int(DAILY_COOLDOWN - (now - data["last_daily"]))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        await update.message.reply_html(f"⏱️ <b>| {user.first_name}</b>, gunluk odulunu zaten aldin! <b>{hours}s {minutes}dk</b> sonra tekrar gel.")
        return

    data["last_daily"] = now
    reward_coins = 2000
    reward_boxes = random.choice(["yaygin kutu", "siradisi kutu", "nadir kutu"])
    
    data["cowoncy"] += reward_coins
    data["inventory"][reward_boxes] = data["inventory"].get(reward_boxes, 0) + 1

    await update.message.reply_html(
        f"🎁✨ <b>| {user.first_name}, gunluk odulun alindi!</b>\n"
        f"💰 <b>+{reward_coins}</b> Cowoncy\n"
        f"📦 <b>+1 {reward_boxes.title()}</b> envanterine eklendi!"
    )

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    inv = get_user_data(user.id, user.first_name)["inventory"]

    if not inv or all(v == 0 for v in inv.values()):
        await update.message.reply_html(f"📦 <b>| {user.first_name}</b>, envanterin bombos!")
        return

    msg = f"📦✨ <b>{user.first_name}'in Envanteri:</b>\n<code>--------------------</code>\n"
    for k, v in inv.items():
        if v > 0:
            msg += f"• <code>{k}</code> ➔ <b>x{v}</b>\n"
    msg += "<code>--------------------</code>\n💡 Acma: <code>/lootbox &lt;kutu_adi&gt;</code>"
    await update.message.reply_html(msg)

async def lootbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)

    if not context.args:
        await update.message.reply_html("⚠️ <b>Kullanim:</b> <code>/lootbox yaygin kutu</code>")
        return

    box = clean_text(" ".join(context.args))
    if not box.endswith("kutu"):
        box += " kutu"

    if data["inventory"].get(box, 0) <= 0:
        await update.message.reply_html(f"❌ Envanterinde hiç <b>{box}</b> yok!")
        return

    data["inventory"][box] -= 1
    coins = random.randint(400, 1200)
    data["cowoncy"] += coins

    await update.message.reply_html(f"🎉✨ <b>{user.first_name}</b> bir <b>{box}</b> acti ve <b>+{coins}</b> Cowoncy kazandi!")

async def zoo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    z = {k: v for k, v in get_user_data(user.id, user.first_name)["zoo"].items() if v > 0}

    if not z:
        await update.message.reply_html(f"🏚️ <b>| {user.first_name}</b>, hayvanat bahcen bombos!")
        return

    msg = f"📜✨ <b>{user.first_name}'in Hayvanat Bahcesi:</b>\n<code>--------------------</code>\n"
    for k, v in z.items():
        msg += f"• {k} ➔ <b>x{v}</b>\n"
    msg += f"<code>--------------------</code>\n🐾 <b>Toplam Hayvan:</b> {sum(z.values())}"
    await update.message.reply_html(msg)

async def cash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    await update.message.reply_html(
        f"💳✨ <b>{user.first_name} Profili</b>\n\n"
        f"💰 <b>Para:</b> {data['cowoncy']} c!\n"
        f"✨ <b>Sans Carpanı:</b> x{data.get('luck_boost', 1.0)}\n"
        f"⚔️ <b>Savaslar:</b> {data['stats']['wins']}W / {data['stats']['losses']}L"
    )

async def coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)

    if len(context.args) < 2:
        await update.message.reply_html("⚠️ <b>Kullanim:</b> <code>/cf &lt;miktar&gt; &lt;yazi/tura&gt;</code>")
        return

    try:
        amount = data["cowoncy"] if context.args[0].lower() == "all" else int(context.args[0])
        choice = clean_text(context.args[1])
    except ValueError:
        await update.message.reply_html("⚠️ Gecersiz miktar!")
        return

    if amount <= 0 or data["cowoncy"] < amount:
        await update.message.reply_html("⚠️ Yetersiz bakiye!")
        return

    data["cowoncy"] -= amount
    msg = await update.message.reply_html(f"🪙🌀 <b>{user.first_name}</b> para firlatti <b>({amount}c)</b>...\n<i>Para havada donuyor... 🪙💫</i>")
    
    await asyncio.sleep(1.0)
    outcome = random.choice(["yazi", "tura"])
    user_pick = "yazi" if "y" in choice else "tura"

    if user_pick == outcome:
        data["cowoncy"] += amount * 2
        await msg.edit_text(f"🪙✨ <b>Sonuc: {outcome.upper()}!</b>\n🎉 Kazandin! <b>+{amount}</b> Cowoncy!", parse_mode="HTML")
    else:
        await msg.edit_text(f"🪙💥 <b>Sonuc: {outcome.upper()}!</b>\n💸 Kaybettin! <b>-{amount}</b> Cowoncy.", parse_mode="HTML")

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)

    if not context.args:
        await update.message.reply_html("⚠️ <b>Kullanim:</b> <code>/slots &lt;miktar&gt;</code>")
        return

    try:
        amount = int(context.args[0])
    except ValueError:
        await update.message.reply_html("⚠️ Gecersiz miktar!")
        return

    if amount <= 0 or data["cowoncy"] < amount:
        await update.message.reply_html("⚠️ Yetersiz bakiye!")
        return

    data["cowoncy"] -= amount
    msg = await update.message.reply_html(f"🎰🌀 <b>{user.first_name}</b> slot kolunu cekti...\n<i>Carklar donuyor... 🎰❓❓</i>")
    
    await asyncio.sleep(1.2)
    symbols = ["💎", "🎰", "🔔", "🍋", "7️⃣"]
    s1, s2, s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)

    res = f"🎰 <b>[ {s1} | {s2} | {s3} ]</b>\n\n"
    if s1 == s2 == s3:
        win = amount * 5
        data["cowoncy"] += win
        res += f"🔥 <b>JACKPOT!</b> <b>+{win}</b> Cowoncy kazandin!"
    elif s1 == s2 or s2 == s3 or s1 == s3:
        win = amount * 2
        data["cowoncy"] += win
        res += f"✨ <b>Cifte Eslesme!</b> <b>+{win}</b> Cowoncy kazandin!"
    else:
        res += f"❌ Kaybettin! <b>-{amount}</b> Cowoncy."

    await msg.edit_text(res, parse_mode="HTML")

async def blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)

    if not context.args:
        await update.message.reply_html("⚠️ <b>Kullanim:</b> <code>/bj &lt;miktar&gt;</code>")
        return

    try:
        amount = int(context.args[0])
    except ValueError:
        await update.message.reply_html("⚠️ Gecersiz miktar!")
        return

    if amount <= 0 or data["cowoncy"] < amount:
        await update.message.reply_html("⚠️ Yetersiz bakiye!")
        return

    data["cowoncy"] -= amount
    msg = await update.message.reply_html(f"🃏✨ <b>{user.first_name}</b> masaya oturdu...\n🎴 <i>Kurpiyer kartlari dagitiyor...</i>")
    
    await asyncio.sleep(1.2)
    user_score = random.randint(16, 22)
    bot_score = random.randint(16, 22)

    if user_score > 21:
        res = f"💥 <b>21'i gectin ({user_score})!</b> Kaybettin <b>-{amount}c</b>."
    elif bot_score > 21 or user_score > bot_score:
        data["cowoncy"] += amount * 2
        res = f"🎉 <b>Kazandın!</b> Sen: {user_score} | Kurpiyer: {bot_score}\n💰 <b>+{amount}c</b> kazandin!"
    elif user_score < bot_score:
        res = f"💥 <b>Kurpiyer kazandi!</b> Sen: {user_score} | Kurpiyer: {bot_score}\n💸 <b>-{amount}c</b> kaybettin."
    else:
        data["cowoncy"] += amount
        res = f"🤝 <b>Berabere!</b> Bahsin iade edildi."

    await msg.edit_text(f"🃏 <b>BLACKJACK</b>\n\n{res}", parse_mode="HTML")

async def battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    now = time.time()

    if now - data["last_battle"] < BATTLE_COOLDOWN:
        await update.message.reply_html(f"⏳ Dinlenmelisin! Kalan: {int(BATTLE_COOLDOWN - (now - data['last_battle']))}s")
        return

    data["last_battle"] = now
    if random.choice([True, False]):
        reward = random.randint(80, 200)
        data["cowoncy"] += reward
        data["stats"]["wins"] += 1
        await update.message.reply_html(f"⚔️🔥 Yaratigi yendin! +{reward} Cowoncy kazandin!")
    else:
        penalty = random.randint(40, 100)
        data["cowoncy"] = max(0, data["cowoncy"] - penalty)
        data["stats"]["losses"] += 1
        await update.message.reply_html(f"⚔️💥 Yaratiga yenildin! -{penalty} Cowoncy kaybettin.")

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)

    if len(context.args) < 2:
        await update.message.reply_html("⚠️ <b>Kullanim:</b> <code>/pay &lt;kullanici_id&gt; &lt;miktar&gt;</code>")
        return

    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_html("⚠️ Gecersiz ID veya miktar!")
        return

    if amount <= 0 or data["cowoncy"] < amount:
        await update.message.reply_html("⚠️ Yetersiz bakiye!")
        return

    if target_id not in users_data:
        await update.message.reply_html("❌ Gonderilecek kullanici sistemde bulunamadi (daha once botu kullanmis olmali).")
        return

    data["cowoncy"] -= amount
    users_data[target_id]["cowoncy"] += amount
    await update.message.reply_html(f"💸 Başarıyla <code>{target_id}</code> ID'li kullaniciya <b>{amount}</b> Cowoncy gonderildi!")

async def steal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user.id, user.first_name)
    now = time.time()

    if now - data["last_steal"] < STEAL_COOLDOWN:
        await update.message.reply_html("⏳ Çok fazla hirsizlik yaptin, polisten saklanmalisin!")
        return

    if len(context.args) < 1:
        await update.message.reply_html("⚠️ <b>Kullanim:</b> <code>/steal &lt;kullanici_id&gt;</code>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_html("⚠️ Gecersiz ID!")
        return

    if target_id not in users_data or target_id == user.id:
        await update.message.reply_html("❌ Gecersiz hedef!")
        return

    data["last_steal"] = now
    target_data = users_data[target_id]

    if target_data["cowoncy"] < 100:
        await update.message.reply_html("❌ Hedefin cok az parasi var, değmez!")
        return

    if random.choice([True, False]):
        stolen = random.randint(50, min(300, target_data["cowoncy"] // 2))
        target_data["cowoncy"] -= stolen
        data["cowoncy"] += stolen
        await update.message.reply_html(f"🥷 Basariyla soygun yaptin! <b>+{stolen}</b> Cowoncy caldin!")
    else:
        penalty = 150
        data["cowoncy"] = max(0, data["cowoncy"] - penalty)
        await update.message.reply_html(f"🚨 Polise yakalandin! Para cezasi olarak <b>-{penalty}</b> Cowoncy kaybettin.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

 
