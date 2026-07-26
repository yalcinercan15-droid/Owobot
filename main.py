# -*- coding: utf-8 -*-
import logging
import random
import time
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Telegram Bot Token
TOKEN = "8945348020:AAFlHHVmzhIt25jfF4Ed_qrUJLZf8495L-w"

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
    translation_table = str.maketrans({
        'ş': 's', 'Ş': 's', 'ğ': 'g', 'Ğ': 'g',
        'ü': 'u', 'Ü': 'u', 'ö': 'o', 'Ö': 'o',
        'ç': 'c', 'Ç': 'c', 'ı': 'i', 'I': 'i', 'İ': 'i'
    })
    return text.translate(translation_table).lower().strip()

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        get_user_data(user.id, user.first_name)
        caption = (
            f"🌸✨ <b>| OwO Bota Hos Geldin {user.first_name}!</b> ✨🌸\n\n"
            "🎮 <b>Komut Listesi:</b>\n"
            "• <code>/wh</code>, <code>/hunt</code>, <code>/h</code> ➔ 🌿 Hayvan Avla\n"
            "• <code>/sell all</code> / <code>/sell &lt;C/U/R/E/M/L&gt;</code> ➔ 💵 Hayvan Sat\n"
            "• <code>/pray</code>, <code>/dua</code> ➔ 🙏 Dua Et (Sans Artirir)\n"
            "• <code>/use &lt;kurabiye/sans tasi&gt;</code> ➔ 🍪 Esya Kullan\n"
            "• <code>/zoo</code>, <code>/z</code> ➔ 📜 Hayvanat Bahcesi\n"
            "• <code>/cash</code>, <code>/c</code> ➔ 💳 Cuzdan / Profil\n"
            "• <code>/daily</code>, <code>/d</code> ➔ 🎁 Gunluk Odul\n"
            "• <code>/inventory</code>, <code>/inv</code> ➔ 📦 Envanter\n"
            "• <code>/lootbox &lt;kutu_adi&gt;</code>, <code>/lb</code> ➔ 🎁 Kutu Acma\n"
            "• <code>/cf &lt;miktar/all&gt; &lt;yazi/tura&gt;</code> ➔ 🪙 Yazi-Tura\n"
            "• <code>/s &lt;miktar&gt;</code> ➔ 🎰 Slot Makinesi\n"
            "• <code>/bj &lt;miktar&gt;</code> ➔ 🃏 Blackjack\n"
            "• <code>/battle</code>, <code>/b</code> ➔ ⚔️ Savas\n"
            "• <code>/top</code>, <code>/leaderboard</code> ➔ 🏆 Zenginler Listesi\n"
            "• <code>/pay &lt;kullanici&gt; &lt;miktar&gt;</code> ➔ 💸 Para Gonder\n"
            "• <code>/steal &lt;kullanici&gt;</code> ➔ 🥷 Soygun Yap"
        )
        await update.message.reply_html(caption)
    except Exception as e:
        logging.error(f"Start hatasi: {e}")

async def pray(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)
        now = time.time()

        if now - data["last_pray"] < PRAY_COOLDOWN:
            remaining = int(PRAY_COOLDOWN - (now - data["last_pray"]))
            await update.message.reply_html(f"⏳ <b>| {user.first_name}</b>, tekrar dua etmek icin <b>{remaining}s</b> beklemelisin!")
            return

        data["last_pray"] = now
        data["luck_boost"] = 1.3
        data["luck_until"] = now + 300

        await update.message.reply_html(
            f"🙏✨ <b>| {user.first_name}</b> tanrilara dua etti!\n"
            f"✨ <b>5 dakika boyunca sansin x1.3 katina cikarildi!</b>"
        )
    except Exception as e:
        logging.error(f"Pray hatasi: {e}")

async def use_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)
        now = time.time()

        if not context.args:
            await update.message.reply_html("⚠️ <b>| Kullanim:</b> <code>/use &lt;kurabiye / sans tasi&gt;</code>")
            return

        item_query = clean_text(" ".join(context.args))

        if "kurabiye" in item_query or "cookie" in item_query:
            key = "kurabiye"
            boost = 1.5
            duration = 1800
            msg_name = "🍪 Kurabiye"
        elif "sans" in item_query or "tasi" in item_query or "tas" in item_query:
            key = "sans tasi"
            boost = 2.0
            duration = 3600
            msg_name = "💎 Sans Tasi"
        else:
            await update.message.reply_html("❌ <b>| Gecersiz esya!</b> Kullanilabilir esyalar: <code>kurabiye</code>, <code>sans tasi</code>")
            return

        if data["inventory"].get(key, 0) <= 0:
            await update.message.reply_html(f"❌ <b>| Envanterinde hic <code>{msg_name}</code> kalmamis!</b>")
            return

        data["inventory"][key] -= 1
        data["luck_boost"] = boost
        data["luck_until"] = now + duration

        await update.message.reply_html(
            f"✨ <b>| {user.first_name}</b> bir <b>{msg_name}</b> tuketti!\n"
            f"🔥 Sans carpani <b>x{boost}</b> olarak guncellendi! ({int(duration/60)} dakika gecerli)"
        )
    except Exception as e:
        logging.error(f"Use item hatasi: {e}")

async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)
        now = time.time()

        time_passed = now - data["last_hunt"]
        
        if time_passed < HUNT_COOLDOWN:
            remaining = int(HUNT_COOLDOWN - time_passed)
            await update.message.reply_html(
                f"⏳ <b>| {user.first_name}</b>, calilar henuz yenilenmedi!\n"
                f"⏱️ Kalan sure: <b>{remaining} saniye</b>"
            )
            return

        data["last_hunt"] = now
        luck_multiplier = check_luck(data)
        chance = random.randint(1, 1000)

        if chance <= int(500 / luck_multiplier): rarity_code, rarity_name = "C", "⚪ Yaygin (Common)"
        elif chance <= int(800 / luck_multiplier): rarity_code, rarity_name = "U", "🟢 Nadir Degil (Uncommon)"
        elif chance <= int(940 / luck_multiplier): rarity_code, rarity_name = "R", "🔵 Nadir (Rare)"
        elif chance <= int(985 / luck_multiplier): rarity_code, rarity_name = "E", "🟣 Epik (Epic)"
        elif chance <= int(998 / luck_multiplier): rarity_code, rarity_name = "M", "🔴 Mitolojik (Mythic)"
        else: rarity_code, rarity_name = "L", "🟡 Efsanevi (Legendary)"

        caught = random.choice(ANIMALS[rarity_code])
        earned_coins = random.randint(30, 90) if rarity_code in ["C", "U"] else random.randint(150, 800)

        data["zoo"][caught] = data["zoo"].get(caught, 0) + 1
        data["cowoncy"] += earned_coins

        reply_text = f"🌿✨ <b>| {user.first_name}</b> calilarin arasindan bir <b>{caught}</b> yakaladi! <== [<b>{rarity_name}</b>]\n💰 <b>+{earned_coins}</b> Cowoncy kazandin!"

        if luck_multiplier > 1.0:
            reply_text += f"\n✨ <i>Sans Artirici (x{luck_multiplier}) etkisi aktif!</i>"

        if random.randint(1, 5) == 1:
            dropped_key = random.choice(["yaygin kutu", "siradisi kutu", "nadir kutu", "kurabiye"])
            data["inventory"][dropped_key] = data["inventory"].get(dropped_key, 0) + 1
            reply_text += f"\n🎁✨ <b>Ayrica bir <code>{dropped_key}</code> dusurdun!</b>"

        await update.message.reply_html(reply_text)
    except Exception as e:
        logging.error(f"Hunt hatasi: {e}")

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)
        zoo_data = data["zoo"]

        if not zoo_data or sum(zoo_data.values()) == 0:
            await update.message.reply_html(f"🏚️ <b>| {user.first_name}</b>, satacak hic hayvanin yok!")
            return

        if not context.args:
            await update.message.reply_html(
                "⚠️ <b>| Kullanim Sekilleri:</b>\n"
                "• <code>/sell all</code> ➔ Tum hayvanlari sat\n"
                "• <code>/sell C</code> ➔ Sadece Yaygin (C) hayvanlari sat\n"
                "• <code>/sell R</code> ➔ Sadece Nadir (R) hayvanlari sat"
            )
            return

        target = clean_text(" ".join(context.args)).upper()
        total_earned = 0
        sold_count = 0

        if target == "ALL":
            for animal, count in list(zoo_data.items()):
                if count > 0:
                    rarity = ANIMAL_TO_RARITY.get(animal, "C")
                    total_earned += count * ANIMAL_PRICES.get(rarity, 15)
                    sold_count += count
                    zoo_data[animal] = 0

        elif target in ANIMAL_PRICES:
            for animal, count in list(zoo_data.items()):
                if count > 0 and ANIMAL_TO_RARITY.get(animal) == target:
                    total_earned += count * ANIMAL_PRICES[target]
                    sold_count += count
                    zoo_data[animal] = 0

        if sold_count == 0:
            await update.message.reply_html(f"❌ <b>| {user.first_name}</b>, satilacak hayvan bulunamadi!")
            return

        data["cowoncy"] += total_earned
        await update.message.reply_html(
            f"💵✨ <b>| {user.first_name}</b>, <b>{sold_count}</b> adet hayvan satti!\n"
            f"💰 Kazanc: <b>+{total_earned}</b> Cowoncy!"
        )
    except Exception as e:
        logging.error(f"Sell hatasi: {e}")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
        data["cowoncy"] += 1500
        data["inventory"]["nadir kutu"] = data["inventory"].get("nadir kutu", 0) + 1
        data["inventory"]["kurabiye"] = data["inventory"].get("kurabiye", 0) + 1

        await update.message.reply_html(
            f"🎁✨ <b>| {user.first_name}</b>, gunluk odulun teslim edildi!\n💰 <b>+1500</b> Cowoncy\n📦 <b>+1</b> nadir kutu & 🍪 <b>+1</b> kurabiye eklendi!"
        )
    except Exception as e:
        logging.error(f"Daily hatasi: {e}")

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)
        inv = data["inventory"]

        if not inv or all(val == 0 for val in inv.values()):
            await update.message.reply_html(f"📦 <b>| {user.first_name}</b>, envanterin bombos!")
            return

        inv_text = f"📦✨ <b>| {user.first_name}'in Envanteri</b>\n<code>--------------------</code>\n"
        for item, count in inv.items():
            if count > 0:
                inv_text += f"• <code>{item}</code> ➔ <b>x{count}</b>\n"
        inv_text += f"<code>--------------------</code>\n💡 Kutular icin: <code>/lb &lt;kutu_adi&gt;</code>\n💡 Esyalar icin: <code>/use &lt;esya_adi&gt;</code>"
        await update.message.reply_html(inv_text)
    except Exception as e:
        logging.error(f"Inventory hatasi: {e}")

async def lootbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)

        if not context.args:
            await update.message.reply_html("⚠️ <b>| Kullanim:</b> <code>/lootbox &lt;yaygin/siradisi/nadir&gt;</code>")
            return

        query = clean_text(" ".join(context.args))

        if "sans" in query or "tasi" in query or "kurabiye" in query:
            await update.message.reply_html(f"⚠️ <b>| {user.first_name}</b>, bu bir kutu degil esyadir! Kullanmak icin: <code>/use {query}</code> yazmalisin.")
            return

        box_query = query if query.endswith("kutu") else f"{query} kutu"

        target_key = None
        for inv_key in data["inventory"].keys():
            if clean_text(inv_key) == box_query:
                target_key = inv_key
                break

        if not target_key or data["inventory"].get(target_key, 0) <= 0:
            await update.message.reply_html(f"❌ <b>| Envanterinde hic <code>{box_query}</code> yok!</b>")
            return

        data["inventory"][target_key] -= 1
        coins_won = random.randint(300, 900) if "yaygin" in box_query else random.randint(1000, 3000)
        data["cowoncy"] += coins_won
        
        extra_animal = random.choice(ANIMALS["R" if "nadir" in box_query else "C"])
        data["zoo"][extra_animal] = data["zoo"].get(extra_animal, 0) + 1

        await update.message.reply_html(
            f"🎉✨ <b>| {user.first_name} bir <code>{target_key}</code> acdi!</b>\n"
            f"💰 <b>+{coins_won}</b> Cowoncy!\n🐾 Bonus Hayvan: <b>{extra_animal}</b>"
        )
    except Exception as e:
        logging.error(f"Lootbox hatasi: {e}")

async def zoo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)
        active_animals = {k: v for k, v in data["zoo"].items() if v > 0}

        if not active_animals:
            await update.message.reply_html(f"🏚️ <b>| {user.first_name}</b>, hayvanat bahcen bombos!")
            return

        zoo_text = f"📜✨ <b>| {user.first_name}'in Hayvanat Bahcesi</b>\n<code>--------------------</code>\n"
        total_animals = sum(active_animals.values())
        for animal, count in active_animals.items():
            zoo_text += f"• {animal} ➔ <b>x{count}</b>\n"
        zoo_text += f"<code>--------------------</code>\n🐾 <b>Toplam Hayvan:</b> <b>{total_animals}</b>\n💡 Satmak icin: <code>/sell all</code>"
        await update.message.reply_html(zoo_text)
    except Exception as e:
        logging.error(f"Zoo hatasi: {e}")

async def cash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)
        current_luck = check_luck(data)
        msg = (
            f"💳✨ <b>| {user.first_name} Profili</b>\n\n"
            f"💰 <b>Cowoncy Bakiyesi:</b> {data['cowoncy']} <code>c!</code>\n"
            f"✨ <b>Aktif Sans Carpani:</b> x{current_luck}\n"
            f"⚔️ <b>Savas Gecmisi:</b> {data['stats']['wins']}W / {data['stats']['losses']}L"
        )
        await update.message.reply_html(msg)
    except Exception as e:
        logging.error(f"Cash hatasi: {e}")

async def coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)

        if len(context.args) < 2:
            await update.message.reply_html("⚠️ <b>| Kullanim:</b> <code>/cf &lt;miktar/all&gt; &lt;yazi/tura&gt;</code>")
            return

        amount_arg = clean_text(context.args[0])
        if amount_arg in ["all", "max"]:
            amount = data["cowoncy"]
        else:
            try:
                amount = int(amount_arg)
            except ValueError:
                await update.message.reply_html("⚠️ <b>| Gecersiz miktar! Sayi veya 'all' yazmalisin.</b>")
                return

        if amount <= 0:
            await update.message.reply_html("⚠️ <b>| Oynayacak paran yok!</b>")
            return

        if data["cowoncy"] < amount:
            await update.message.reply_html("⚠️ <b>| Yeterli bakiyen yok!</b>")
            return

        choice = clean_text(context.args[1])
        user_pick = "yazi" if choice in ["y", "yazi"] else "tura"
        msg = await update.message.reply_html(f"🪙🌀 <b>| {user.first_name}</b> parayi firlatti! <b>({amount} Cowoncy)</b>\n<i>Para havada donuyor... 🪙💫</i>")

        await asyncio.sleep(1.2)

        luck = check_luck(data)
        win_chance = 50 * luck
        roll = random.randint(1, 100)

        if roll <= win_chance:
            outcome = user_pick
        else:
            outcome = "tura" if user_pick == "yazi" else "yazi"

        if user_pick == outcome:
            data["cowoncy"] += amount
            final_caption = f"🪙✨ <b>| Para dustu ve {outcome.upper()} geldi!</b>\n🎉 Tebrikler! <b>+{amount}</b> Cowoncy kazandin!"
        else:
            data["cowoncy"] -= amount
            final_caption = f"🪙💥 <b>| Para dustu ve {outcome.upper()} geldi!</b>\n💸 Maalesef <b>-{amount}</b> Cowoncy kaybettin!"

        await msg.edit_text(final_caption, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Coinflip hatasi: {e}")

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        data = get_user_data(user.id, user.first_name)

        if len(context.args) < 1:
            await update.message.reply_html("⚠️ <b>| Kullanim:</b> <code>/s &lt;miktar&gt;</code>")
            return

        try:
            amount = int(context.args[0])
        except ValueError:
            await update.message.reply_html("⚠️ <b>| Gecersiz miktar! Sayi yazmalisin.</b>")
            return

        if amount <= 0 or data["cowoncy"] < amount:
            await update.message.reply_html("⚠️ <b>| Yeterli bakiyen yok!</b>")
            return

        data["cowoncy"] -= amount
        msg = await update.message.reply_html(f"🎰🌀 <b>| {user.first_name}</b> slot kolunu cekti... <b>({amount} Cowoncy)</b>\n<i>Carklar donuyor... 🎰❓❓</i>")

        await asyncio.sleep(1.2)
        symbols = ["💎", "🎰", "🔔", "🍋", "7️⃣"]
        
        luck = check_luck(data)
        if luck > 1.0 and random.random() < 0.4:
            s1 = s2 = s3 = random.choice(symbols)
        else:
            s1, s2, s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)

        final_msg = f"🎰 <b>[ {s1} | {s2} | {s3} ]</b>\n\n"
        if s1 == s2 == s3:
            win = amount * 5
            data["cowoncy"] += win
            final_msg += f"🔥✨ <b>BUYUK IKRAMIYE (JACKPOT)!</b> <b>+{win}</b> Cowoncy!"
        elif s1 == s2 or s2 == s3 or s1 == s3:
            win = amount * 2
            data["cowoncy"] += win
            final_msg += f"✨ <b>Cifte Eslesme!</b> <b>+{win}</b> Cowoncy!"
        else:
            final_msg += f"❌ Kaybettin! <b>-{amount}</b> Cowoncy."

        await msg.edit_text(final_msg, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Slots hatasi: {e}")

async def black
