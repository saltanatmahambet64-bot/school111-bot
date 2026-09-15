import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8688251662:AAHALoLBiIxTv2UJ0buE4vGctg7AM09K70c"
ADMIN_ID = 8327290268  # Ваши права администратора подключены!

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Словарь для хранения выбранного языка пользователей {user_id: 'ru' или 'kk'}
user_languages = {}

# ==================== СЛОВАРЬ ПЕРЕВОДОВ (РУС / КАЗ) ====================
TEXTS = {
    "ru": {
        "welcome": "Здравствуйте, {name}!\n\nДобро пожаловать в Бюро находок школы №111. 🏫\nВыберите нужное действие с помощью кнопок ниже:",
        "choose_lang": "Выберите язык / Тілді таңдаңыз:",
        "lang_selected": "Выбран русский язык! Выберите действие:",
        "cancel": "❌ Отмена",
        "canceled": "Действие отменено.",
        "btn_found": "📦 Я нашёл вещь",
        "btn_lost": "🔍 Я потерял вещь",
        "btn_list": "📋 Список всех находок",
        "btn_info": "ℹ️ Информация и правила",
        "btn_change_lang": "🌐 Сменить язык",
        "btn_skip_photo": "⏭️ Пропустить фото",
        
        "info": (
            "🏫 *Бюро находок Школы №111*\n\n"
            "📍 *Где забрать вещь:*\n"
            "Все найденные вещи хранятся на *вахте (1 этаж, главный вход)* или в *кабинете информатики*.\n\n"
            "🕒 *Часы работы вахты:*\n"
            "Понедельник — Пятница: с 08:00 до 18:00\n"
            "Суббота: с 08:00 до 14:00\n\n"
            "📌 *Как забрать найденную вещь:*\n"
            "1. Найдите свою вещь в «📋 Списке всех находок».\n"
            "2. Назовите вахтёру номер заявки (например, Находка №5).\n"
            "3. Для подтверждения вас могут попросить подробно описать вещь (например, пароль/чехол от телефона или цвет ключей).\n\n"
            "🤝 Давайте вместе сделаем нашу школу честнее и добрее!"
        ),
        
        "found_step1": "Спасибо за помощь! 👏\n\nШаг 1 из 2: Опишите найденную вещь (что это и где вы её нашли):",
        "found_step2": "Отлично! Шаг 2 из 2: Теперь отправьте *фотографию* найденной вещи:",
        "found_success": "✅ Заявка отправлена на проверку администратору. После одобрения она появится в общем списке!",
        
        "lost_step1": "Шаг 1 из 2: Опишите потерю (что именно и где примерно могли оставить):",
        "lost_step2": "Шаг 2 из 2: Прикрепите фото вещи (если есть) или нажмите «⏭️ Пропустить фото».",
        "lost_success": "🔍 Заявка о потере принята! Если вещь найдут, мы свяжемся с вами.",
        
        "empty_list": "📋 В базе пока нет опубликованных находок.",
        "list_title": "📋 *Опубликованные находки в школе №111:*",
        "admin_delete": "🗑️ Выдано (Удалить)"
    },
    "kk": {
        "welcome": "Сәлеметсіз бе, {name}!\n\n№111 мектептің Бюро находок (Табылған заттар бюросы) қызметіне қош келдіңіз. 🏫\nТөмендегі батырмалар арқылы қажетті әрекетті таңдаңыз:",
        "choose_lang": "Тілді таңдаңыз / Выберите язык:",
        "lang_selected": "Қазақ тілі таңдалды! Әрекетті таңдаңыз:",
        "cancel": "❌ Болдырмау",
        "canceled": "Әрекет тоқтатылды.",
        "btn_found": "📦 Мен зат таптым",
        "btn_lost": "🔍 Мен зат жоғалттым",
        "btn_list": "📋 Барлық табылған заттар тізімі",
        "btn_info": "ℹ️ Ақпарат және ережелер",
        "btn_change_lang": "🌐 Тілді ауыстыру",
        "btn_skip_photo": "⏭️ Фотоны өткізу",
        
        "info": (
            "🏫 *№111 мектептің Бюро находок*\n\n"
            "📍 *Затты қайдан алуға болады:*\n"
            "Барлық табылған заттар *кезекшілік бөлімінде (1 қабат, бас кіреберіс)* немесе *информатика кабинетінде* сақталады.\n\n"
            "🕒 *Кезекшілік жұмыс уақыты:*\n"
            "Дүйсенбі — Жұма: 08:00-ден 18:00-ге дейін\n"
            "Сенбі: 08:00-ден 14:00-ге дейін\n\n"
            "📌 *Табылған затты қалай алуға болады:*\n"
            "1. Өз заттарыңызды «📋 Барлық табылған заттар тізімінен» табыңыз.\n"
            "2. Кезекшіге өтінім нөмірін айтыңыз (мысалы, №5 Находка).\n"
            "3. Растау үшін сізден затты толығырақ сипаттауды сұрауы мүмкін (мысалы, телефонның қабы немесе кілттің түсі).\n\n"
            "🤝 Мектебімізді бірге бұрыннан да мейірімді етейік!"
        ),
        
        "found_step1": "Көмегіңіз үшін рақмет! 👏\n\n1-ші қадам (2-ден): Табылған затты сипаттаңыз (не және оны қайдан таптыңыз):",
        "found_step2": "Керемет! 2-ші қадам (2-ден): Енді табылған заттың *фотосуретін* жіберіңіз:",
        "found_success": "✅ Өтінім әкімшінің тексеруіне жіберілді. Мақұлданғаннан кейін ол жалпы тізімде пайда болады!",
        
        "lost_step1": "1-ші қадам (2-ден): Жоғалған затты сипаттаңыз (не және қай жерде қалдырдыңыз):",
        "lost_step2": "2-ші қадам (2-ден): Заттың фотосын тіркеңіз (бар болса) немесе «⏭️ Фотоны өткізу» батырмасын басыңыз.",
        "lost_success": "🔍 Жоғалту туралы өтінім қабылданды! Егер зат табылса, біз сізбен хабарласамыз.",
        
        "empty_list": "📋 Әзірге базада жарияланған заттар жоқ.",
        "list_title": "📋 *№111 мектепте жарияланған табылған заттар:*",
        "admin_delete": "🗑️ Берілді (Өшіру)"
    }
}

def get_main_keyboard(lang="ru"):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_found"]), KeyboardButton(text=t["btn_lost"])],
            [KeyboardButton(text=t["btn_list"])],
            [KeyboardButton(text=t["btn_info"]), KeyboardButton(text=t["btn_change_lang"])]
        ],
        resize_keyboard=True
    )

def get_cancel_keyboard(lang="ru"):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]["cancel"])]],
        resize_keyboard=True
    )

def get_skip_photo_keyboard(lang="ru"):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_skip_photo"])],
            [KeyboardButton(text=t["cancel"])]
        ],
        resize_keyboard=True
    )

def get_language_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
            InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="set_lang_kk")
        ]
    ])

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            description TEXT,
            photo_id TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()

def add_pending_item(user_name: str, description: str, photo_id: str) -> int:
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO found_items (user_name, description, photo_id, status) VALUES (?, ?, ?, 'pending')",
        (user_name, description, photo_id)
    )
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def approve_item(item_id: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE found_items SET status = 'approved' WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def delete_item(item_id: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM found_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def get_approved_items():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, photo_id FROM found_items WHERE status = 'approved' ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

init_db()

class FoundItemState(StatesGroup):
    waiting_for_description = State()
    waiting_for_photo = State()

class LostItemState(StatesGroup):
    waiting_for_description = State()
    waiting_for_photo = State()

@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выберите язык интерфейса / Интерфейс тілін таңдаңыз:",
        reply_markup=get_language_inline_keyboard()
    )

@dp.callback_query(F.data.startswith("set_lang_"))
async def set_language_callback(callback: types.CallbackQuery):
    lang = callback.data.split("_")[2]
    user_languages[callback.from_user.id] = lang
    
    name = callback.from_user.first_name or ""
    t = TEXTS[lang]
    
    await callback.message.delete()
    await callback.message.answer(
        t["welcome"].format(name=name),
        reply_markup=get_main_keyboard(lang)
    )
    await callback.answer()

@dp.message(F.text.in_(["🌐 Сменить язык", "🌐 Тілді ауыстыру"]))
async def change_language_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выберите язык / Тілді таңдаңыз:",
        reply_markup=get_language_inline_keyboard()
    )

@dp.message(F.text.in_(["❌ Отмена", "❌ Болдырмау"]))
async def cancel_action(message: types.Message, state: FSMContext):
    await state.clear()
    lang = user_languages.get(message.from_user.id, "ru")
    await message.answer(TEXTS[lang]["canceled"], reply_markup=get_main_keyboard(lang))

@dp.message(F.text.in_(["ℹ️ Информация и правила", "ℹ️ Ақпарат және ережелер"]))
async def info_cmd(message: types.Message):
    lang = user_languages.get(message.from_user.id, "ru")
    await message.answer(TEXTS[lang]["info"], reply_markup=get_main_keyboard(lang))

@dp.message(F.text.in_(["📦 Я нашёл вещь", "📦 Мен зат таптым"]))
async def start_found_process(message: types.Message, state: FSMContext):
    lang = user_languages.get(message.from_user.id, "ru")
    await state.set_state(FoundItemState.waiting_for_description)
    await message.answer(
        TEXTS[lang]["found_step1"],
        reply_markup=get_cancel_keyboard(lang)
    )

@dp.message(FoundItemState.waiting_for_description)
async def process_found_description(message: types.Message, state: FSMContext):
    lang = user_languages.get(message.from_user.id, "ru")
    await state.update_data(description=message.text)
    await state.set_state(FoundItemState.waiting_for_photo)
    await message.answer(TEXTS[lang]["found_step2"], reply_markup=get_cancel_keyboard(lang))

@dp.message(FoundItemState.waiting_for_photo, F.photo)
async def process_found_photo(message: types.Message, state: FSMContext):
    lang = user_languages.get(message.from_user.id, "ru")
    user_data = await state.get_data()
    description = user_data.get("description")
    photo_id = message.photo[-1].file_id
    user_name = message.from_user.first_name or "Аноним"

    item_id = add_pending_item(user_name, description, photo_id)
    await state.clear()
    
    await message.answer(TEXTS[lang]["found_success"], reply_markup=get_main_keyboard(lang))

    admin_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"approve_{item_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{item_id}")
        ]
    ])
    
    admin_text = f"🆕 *Новая находка №{item_id}!*\n\n📝 Описание: {description}\n👤 Отправитель: {user_name}"
    
    try:
        await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_markup)
    except Exception as e:
        print(f"Ошибка отправки админу: {e}")

@dp.message(F.text.in_(["🔍 Я потерял вещь", "🔍 Мен зат жоғалттым"]))
async def start_lost_process(message: types.Message, state: FSMContext):
    lang = user_languages.get(message.from_user.id, "ru")
    await state.set_state(LostItemState.waiting_for_description)
    await message.answer(TEXTS[lang]["lost_step1"], reply_markup=get_cancel_keyboard(lang))

@dp.message(LostItemState.waiting_for_description)
async def process_lost_description(message: types.Message, state: FSMContext):
    lang = user_languages.get(message.from_user.id, "ru")
    await state.update_data(description=message.text)
    await state.set_state(LostItemState.waiting_for_photo)
    await message.answer(TEXTS[lang]["lost_step2"], reply_markup=get_skip_photo_keyboard(lang))

@dp.message(LostItemState.waiting_for_photo, F.photo)
async def process_lost_photo(message: types.Message, state: FSMContext):
    lang = user_languages.get(message.from_user.id, "ru")
    user_data = await state.get_data()
    description = user_data.get("description")
    photo_id = message.photo[-1].file_id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    await state.clear()
    await message.answer(TEXTS[lang]["lost_success"], reply_markup=get_main_keyboard(lang))

    lost_text = f"🔎 *ЗАЯВКА О ПОТЕРЕ!*\n\n📝 Описание: {description}\n👤 Потерпевший: {username}"
    try:
        await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=lost_text)
    except Exception as e:
        print(f"Ошибка отправки админу: {e}")

@dp.message(LostItemState.waiting_for_photo, F.text.in_(["⏭️ Пропустить фото", "⏭️ Фотоны өткізу"]))
async def process_lost_no_photo(message: types.Message, state: FSMContext):
    lang = user_languages.get(message.from_user.id, "ru")
    user_data = await state.get_data()
    description = user_data.get("description")
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    await state.clear()
    await message.answer(TEXTS[lang]["lost_success"], reply_markup=get_main_keyboard(lang))

    lost_text = f"🔎 *ЗАЯВКА О ПОТЕРЕ (без фото)!*\n\n📝 Описание: {description}\n👤 Потерпевший: {username}"
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=lost_text)
    except Exception as e:
        print(f"Ошибка отправки админу: {e}")

@dp.message(F.text.in_(["📋 Список всех находок", "📋 Барлық табылған заттар тізімі"]))
async def list_items(message: types.Message):
    lang = user_languages.get(message.from_user.id, "ru")
    items = get_approved_items()
    
    if not items:
        await message.answer(TEXTS[lang]["empty_list"])
        return

    await message.answer(TEXTS[lang]["list_title"])
    for item in items:
        item_id, description, photo_id = item
        caption_text = f"🔹 *Находка №{item_id}*\n📝 {description}"
        
        keyboard = None
        if message.from_user.id == ADMIN_ID:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=TEXTS[lang]["admin_delete"], callback_data=f"delete_{item_id}")]
            ])

        if photo_id:
            await message.answer_photo(photo=photo_id, caption=caption_text, reply_markup=keyboard)
        else:
            await message.answer(caption_text, reply_markup=keyboard)

@dp.callback_query(F.data.startswith("approve_"))
async def approve_callback(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    approve_item(item_id)
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ *ОДОБРЕНО И ОПУБЛИКОВАНО*")
    await callback.answer("Заявка одобрена!")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_callback(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    delete_item(item_id)
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ *ОТКЛОНЕНО И УДАЛЕНО*")
    await callback.answer("Заявка отклонена.")

@dp.callback_query(F.data.startswith("delete_"))
async def delete_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return

    item_id = int(callback.data.split("_")[1])
    delete_item(item_id)
    await callback.message.delete()
    await callback.answer("Вещь успешно отмечена как выданная и удалена из базы!")

async def main():
    print("Бот Бюро Находок Школы №111 полностью настроен, поддерживает казахский и русский языки и запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
