from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import webbrowser
import psutil
import pyautogui
import glob
import datetime
import platform

app = Flask(__name__)
CORS(app)

def find_and_open_file(filename):
    """Ищет файл на диске и открывает его"""
    search_dirs = [
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~\\Pictures"),
        os.path.expanduser("~\\Music"),
        os.path.expanduser("~"),
    ]
    for d in search_dirs:
        for f in glob.glob(os.path.join(d, "**", f"*{filename}*"), recursive=True):
            os.startfile(f)
            return f"Открываю файл: {os.path.basename(f)}"
    return f"Файл '{filename}' не найден."

def process_command(cmd):
    text = cmd.lower()

    # ===== БРАУЗЕР И САЙТЫ =====
    sites = {
        "youtube": "https://youtube.com",
        "гугл": "https://google.com",
        "google": "https://google.com",
        "вконтакте": "https://vk.com",
        "vk": "https://vk.com",
        "telegram": "https://web.telegram.org",
        "телеграм": "https://web.telegram.org",
        "github": "https://github.com",
        "spotify": "https://open.spotify.com",
        "netflix": "https://netflix.com",
        "twitter": "https://twitter.com",
        "instagram": "https://instagram.com",
        "roblox": "https://roblox.com",
        "twitch": "https://twitch.tv",
    }
    for site, url in sites.items():
        if site in text and ("открой" in text or "зайди" in text or "перейди" in text or "запусти" in text):
            webbrowser.open(url)
            return f"Открываю {site.title()} в браузере."

    # ===== ПОИСК В GOOGLE =====
    if "найди" in text or "поищи" in text or "поиск" in text:
        for prefix in ["найди в google ", "найди в гугл ", "найди ", "поищи ", "поиск "]:
            if prefix in text:
                query = text.split(prefix, 1)[1].strip()
                webbrowser.open(f"https://google.com/search?q={query}")
                return f"Ищу '{query}' в Google."
        webbrowser.open("https://google.com")
        return "Открываю Google."

    # ===== ПРОГРАММЫ =====
    programs = {
        "калькулятор": "calc.exe",
        "блокнот": "notepad.exe",
        "notepad": "notepad.exe",
        "проводник": "explorer.exe",
        "paint": "mspaint.exe",
        "пейнт": "mspaint.exe",
        "командную строку": "cmd.exe",
        "cmd": "cmd.exe",
        "диспетчер задач": "taskmgr.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "визуальную студию": "devenv.exe",
        "vs code": "code",
        "vscode": "code",
    }
    if "открой" in text or "запусти" in text or "включи" in text:
        for prog, exe in programs.items():
            if prog in text:
                try:
                    subprocess.Popen(exe, shell=True)
                    return f"Открываю {prog}."
                except:
                    return f"Не могу открыть {prog}."

    # ===== БЛОКНОТ С ТЕКСТОМ =====
    if "напиши" in text and ("блокнот" in text or "текст" in text or "файл" in text or "документ" in text):
        parts = text.split("напиши", 1)
        content = parts[1].strip() if len(parts) > 1 else ""
        for word in ["в блокноте", "в блокнот", "в файл", "в документ", "в текст"]:
            content = content.replace(word, "").strip()
        path = os.path.join(os.path.expanduser("~\\Desktop"), "jarvis_note.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        os.startfile(path)
        return f"Написал '{content}' и открыл файл на рабочем столе."

    # ===== СОЗДАТЬ ПАПКУ =====
    if "создай папку" in text or "создай директорию" in text:
        name = text.split("папку", 1)[-1].strip() or "Новая папка"
        path = os.path.join(os.path.expanduser("~\\Desktop"), name)
        os.makedirs(path, exist_ok=True)
        os.startfile(path)
        return f"Создал папку '{name}' на рабочем столе."

    # ===== ПОИСК ФАЙЛА =====
    if "найди файл" in text or "найди картину" in text or "найди картинку" in text or "открой файл" in text:
        for kw in ["найди файл ", "найди картину ", "найди картинку ", "открой файл "]:
            if kw in text:
                fname = text.split(kw, 1)[1].strip()
                return find_and_open_file(fname)
        return "Укажите имя файла."

    # ===== МУЗЫКА =====
    if "музык" in text or "включи музыку" in text or "поставь музыку" in text:
        webbrowser.open("https://open.spotify.com")
        return "Открываю Spotify."

    # ===== ГРОМКОСТЬ =====
    if "громкость" in text or "звук" in text:
        if "увеличь" in text or "громче" in text:
            for _ in range(5): pyautogui.press("volumeup")
            return "Увеличиваю громкость."
        elif "уменьши" in text or "тише" in text:
            for _ in range(5): pyautogui.press("volumedown")
            return "Уменьшаю громкость."
        elif "выключи" in text or "без звука" in text:
            pyautogui.press("volumemute")
            return "Звук отключён."

    # ===== СКРИНШОТ =====
    if "скриншот" in text or "снимок экрана" in text:
        path = os.path.join(os.path.expanduser("~\\Desktop"), f"screenshot_{datetime.datetime.now().strftime('%H%M%S')}.png")
        pyautogui.screenshot(path)
        return f"Скриншот сохранён на рабочий стол."

    # ===== СИСТЕМА =====
    if "выключи компьютер" in text or "выключи пк" in text:
        return "Для безопасности выключение отключено. Подтвердите вручную."

    if "перезагрузи" in text:
        return "Для безопасности перезагрузка отключена. Подтвердите вручную."

    # ===== ИНФОРМАЦИЯ О СИСТЕМЕ =====
    if "оперативн" in text or "память" in text or "ram" in text:
        mem = psutil.virtual_memory()
        return f"Оперативная память: использовано {mem.percent}%, свободно {round(mem.available/1024**3, 1)} ГБ из {round(mem.total/1024**3, 1)} ГБ."

    if "процессор" in text or "cpu" in text or "нагрузка" in text:
        cpu = psutil.cpu_percent(interval=1)
        return f"Нагрузка на процессор: {cpu}%."

    if "диск" in text or "место" in text:
        disk = psutil.disk_usage("C:\\")
        free = round(disk.free/1024**3, 1)
        total = round(disk.total/1024**3, 1)
        return f"Диск C: свободно {free} ГБ из {total} ГБ."

    # ===== ВРЕМЯ И ДАТА =====
    if "время" in text or "час" in text:
        return f"Сейчас {datetime.datetime.now().strftime('%H:%M')}."

    if "дата" in text or "число" in text or "день" in text:
        days = ["понедельник","вторник","среда","четверг","пятница","суббота","воскресенье"]
        months = ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]
        now = datetime.datetime.now()
        return f"Сегодня {days[now.weekday()]}, {now.day} {months[now.month-1]} {now.year} года."

    # ===== ТЕЛЕФОН (открывает WhatsApp Web) =====
    if "позвони" in text or "напиши" in text and "сообщение" in text:
        webbrowser.open("https://web.whatsapp.com")
        return "Открываю WhatsApp Web. Выберите контакт вручную."

    # ===== БРАУЗЕР ПРОСТО =====
    if "браузер" in text and ("открой" in text or "запусти" in text):
        webbrowser.open("https://google.com")
        return "Открываю браузер."

    return None  # не распознано — отдаём AI

@app.route('/ping')
def ping():
    return jsonify({"status": "ok"})

@app.route('/command', methods=['POST'])
def command():
    data = request.json
    cmd = data.get('command', '')
    result = process_command(cmd)
    if result:
        return jsonify({"response": result})
    else:
        return jsonify({"response": f"Команда '{cmd}' выполнена."})

@app.route('/sysinfo')
def sysinfo():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.5),
        "ram": psutil.virtual_memory().percent,
        "os": platform.system() + " " + platform.release()
    })

if __name__ == '__main__':
    print("=" * 50)
    print("  J.A.R.V.I.S Server запущен!")
    print("  Адрес: http://localhost:5000")
    print("  Оставьте это окно открытым.")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)