import telebot
from pylibdmtx.pylibdmtx import encode
from PIL import Image
from telebot import types
import io
import logging

# Установите уровень логирования
logging.basicConfig(level=logging.INFO)

# Ваш API токен, полученный от BotFather
API_TOKEN = '7128680547:AAECg5Dpd8RPt9aA5qq2tnuBM1J1JAbBTRA'  # Замените на ваш токен

bot = telebot.TeleBot(API_TOKEN)


# Функция для создания кастомной клавиатуры
def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_start = types.KeyboardButton('/start')  # Кнопка перезапуска бота
    markup.add(btn_start)
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Отправьте мне значение, и я сгенерирую DataMatrix код для вас!",
        reply_markup=create_main_menu()
    )


@bot.message_handler(content_types=['text'])
def generate_datamatrix(message):
    # Если сообщение совпадает с командами или "Перезапуск бота", не обрабатываем его как текст для DataMatrix
    if message.text in ['/start', '/help']:
        return

    logging.info(f"Получено сообщение для генерации DataMatrix: {message.text}")

    try:
        data = message.text
        # Кодируем данные в UTF-8 перед передачей в encode
        encoded_data = data.encode('utf-8')
        code = encode(encoded_data)
        img = Image.frombytes('RGB', (code.width, code.height), code.pixels)

        # Увеличиваем размер для лучшей разборчивости
        scale = 2
        img = img.resize((code.width * scale, code.height * scale), Image.NEAREST)

        # Создание нового изображения с черным фоном
        new_img = Image.new('RGB', img.size, 'black')
        new_img.paste(img)

        # Инвертирование цветов (чтобы сам DataMatrix был белым, а фон черным)
        pixels = new_img.load()
        for i in range(new_img.size[0]):
            for j in range(new_img.size[1]):
                if pixels[i, j] == (0, 0, 0):
                    pixels[i, j] = (255, 255, 255)
                else:
                    pixels[i, j] = (0, 0, 0)

        bio = io.BytesIO()
        new_img.save(bio, format='PNG')
        bio.seek(0)

        bot.send_photo(message.chat.id, photo=bio)
    except Exception as e:
        logging.error(f"Ошибка при генерации DataMatrix: {e}")
        bot.reply_to(message, "Произошла ошибка при генерации DataMatrix кода. Пожалуйста, попробуйте снова.")


# Запуск бота
bot.polling(none_stop=True)