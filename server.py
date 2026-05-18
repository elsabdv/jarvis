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
CORS(app, origins="*")

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, ngrok-skip-browser-warning'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

@app.route('/ping', methods=['GET', 'OPTIONS'])
def ping():
    return jsonify({"status": "ok"})

@app.route('/command', methods=['POST', 'OPTIONS'])
def command():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    data = request.json
    cmd = data.get('command', '')
    result = process_command(cmd)
    return jsonify({"response": result or "Выполнено."})

@app.route('/sysinfo', methods=['GET'])
def sysinfo():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.5),
        "ram": psutil.virtual_memory().percent,
        "os": platform.system() + " " + platform.release()
    })

# --- Папки пользователя ---
NAMED_FOLDERS = {
    "рабочий стол": os.path.expanduser("~/Desktop"),
    "desktop": os.path.expanduser("~/Desktop"),
    "документы": os.path.expanduser("~/Documents"),
    "documents": os.path.expanduser("~/Documents"),
    "загрузки": os.path.expanduser("~/Downloads"),
    "downloads": os.path.expanduser("~/Downloads"),
    "картинки": os.path.expanduser("~/Pictures"),
    "pictures": os.path.expanduser("~/Pictures"),
    "музыка": os.path.expanduser("~/Music"),
    "music": os.path.expanduser("~/Music"),
    "видео": os.path.expanduser("~/Videos"),
    "videos": os.path.expanduser("~/Videos"),
}

SEARCH_DIRS = list(NAMED_FOLDERS.values()) + [os.path.expanduser("~")]

def open_folder(name_lower):
    """Открывает известную папку или ищет по имени"""
    # Точное совпадение с известными папками
    for key, path in NAMED_FOLDERS.items():
        if key in name_lower:
            os.startfile(path)
            return f"Открываю папку {key}."

    # Поиск папки по имени на диске
    search_term = name_lower.strip()
    for base in SEARCH_DIRS:
        try:
            for entry in os.scandir(base):
                if entry.is_dir() and search_term in entry.name.lower():
                    os.startfile(entry.path)
                    return f"Открываю папку: {entry.name}"
        except Exception:
            pass

    # Рекурсивный поиск
    for base in SEARCH_DIRS[:4]:
        for dirpath, dirnames, _ in os.walk(base):
            for d in dirnames:
                if search_term in d.lower():
                    full = os.path.join(dirpath, d)
                    os.startfile(full)
                    return f"Нашёл и открываю: {d}"
            if dirpath != base:
                break  # только один уровень вглубь для скорости

    return f"Папка '{name_lower}' не найдена."

def find_file(filename):
    """Ищет файл по имени в стандартных папках"""
    term = filename.lower().strip()
    for base in SEARCH_DIRS:
        try:
            matches = glob.glob(os.path.join(base, "**", f"*{term}*"), recursive=True)
            if matches:
                path = matches[0]
                os.startfile(path)
                return f"Открываю: {os.path.basename(path)}"
        except Exception:
            pass
    return f"Файл '{filename}' не найден ни в одной из стандартных папок."

def process_command(cmd):
    text = cmd.lower()

    # --- САЙТЫ ---
    sites = {
        "youtube": "https://youtube.com",
        "ютуб": "https://youtube.com",
        "гугл": "https://google.com",
        "google": "https://google.com",
        "вконтакте": "https://vk.com",
        "вк": "https://vk.com",
        "vk": "https://vk.com",
        "telegram": "https://web.telegram.org",
        "телеграм": "https://web.telegram.org",
        "github": "https://github.com",
        "spotify": "https://open.spotify.com",
        "спотифай": "https://open.spotify.com",
        "netflix": "https://netflix.com",
        "нетфликс": "https://netflix.com",
        "instagram": "https://instagram.com",
        "twitch": "https://twitch.tv",
        "roblox": "https://roblox.com",
        "роблокс": "https://roblox.com",
    }
    for site, url in sites.items():
        if site in text and any(w in text for w in ["открой", "зайди", "запусти", "покажи"]):
            webbrowser.open(url)
            return f"Открываю {site.title()} в браузере."

    # --- ПОИСК В ИНТЕРНЕТЕ ---
    if "найди в google" in text or "найди в гугл" in text or "поищи" in text:
        for prefix in ["найди в google ", "найди в гугл ", "поищи "]:
            if prefix in text:
                query = text.split(prefix, 1)[1].strip()
                webbrowser.open(f"https://www.google.com/search?q={query}")
                return f"Ищу '{query}' в Google."

    # --- ПАПКИ ---
    # "открой папку Документы" / "открой папку загрузки" / "открой папку my_folder"
    if "папк" in text and any(w in text for w in ["открой", "запусти", "покажи", "перейди"]):
        # Извлекаем название папки
        folder_name = text
        for prefix in ["открой папку ", "открой папка ", "запусти папку ", "покажи папку ", "перейди в папку ", "перейди в "]:
            if prefix in folder_name:
                folder_name = folder_name.split(prefix, 1)[1].strip()
                break
        return open_folder(folder_name)

    # --- ФАЙЛЫ ---
    # "найди файл отчёт" / "открой файл презентация"
    if "файл" in text and any(w in text for w in ["найди", "открой", "запусти"]):
        file_name = text
        for prefix in ["найди файл ", "открой файл ", "запусти файл "]:
            if prefix in file_name:
                file_name = file_name.split(prefix, 1)[1].strip()
                break
        return find_file(file_name)

    # --- ПРОГРАММЫ ---
    programs = {
        "калькулятор": "calc.exe",
        "блокнот": "notepad.exe",
        "проводник": "explorer.exe",
        "paint": "mspaint.exe",
        "пейнт": "mspaint.exe",
        "cmd": "cmd.exe",
        "командная строка": "cmd.exe",
        "диспетчер задач": "taskmgr.exe",
        "vs code": "code",
        "вс код": "code",
    }
    if any(w in text for w in ["открой", "запусти"]):
        for prog, exe in programs.items():
            if prog in text:
                try:
                    subprocess.Popen(exe, shell=True)
                    return f"Открываю {prog}."
                except Exception:
                    return f"Не могу открыть {prog}."

    # --- БЛОКНОТ / СОЗДАНИЕ ФАЙЛА ---
    if "напиши" in text and any(w in text for w in ["блокнот", "файл", "документ"]):
        parts = text.split("напиши", 1)
        content = parts[1].strip() if len(parts) > 1 else ""
        for w in ["в блокноте", "в блокнот", "в файл", "в документ"]:
            content = content.replace(w, "").strip()
        path = os.path.join(os.path.expanduser("~/Desktop"), "jarvis_note.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        os.startfile(path)
        return "Записал и открыл файл на рабочем столе."

    # --- СОЗДАТЬ ПАПКУ ---
    if "создай папку" in text:
        name = text.split("папку", 1)[-1].strip() or "Новая папка"
        path = os.path.join(os.path.expanduser("~/Desktop"), name)
        os.makedirs(path, exist_ok=True)
        os.startfile(path)
        return f"Создал папку '{name}' на рабочем столе."

    # --- МУЗЫКА / МЕДИА ---
    if "музык" in text or "спотифай" in text or "spotify" in text:
        webbrowser.open("https://open.spotify.com")
        return "Открываю Spotify."
    if "громче" in text or "увеличь громкость" in text:
        for _ in range(5): pyautogui.press("volumeup")
        return "Увеличиваю громкость."
    if "тише" in text or "уменьши громкость" in text:
        for _ in range(5): pyautogui.press("volumedown")
        return "Уменьшаю громкость."
    if "без звука" in text or "выключи звук" in text:
        pyautogui.press("volumemute")
        return "Звук отключён."

    # --- СКРИНШОТ ---
    if "скриншот" in text:
        ts = datetime.datetime.now().strftime("%H%M%S")
        path = os.path.join(os.path.expanduser("~/Desktop"), f"screenshot_{ts}.png")
        pyautogui.screenshot(path)
        return f"Скриншот сохранён: screenshot_{ts}.png"

    # --- СИСТЕМНЫЕ ДАННЫЕ ---
    if "оперативн" in text or "ram" in text or "память" in text:
        mem = psutil.virtual_memory()
        return f"RAM: использовано {mem.percent}%, свободно {round(mem.available/1024**3, 1)} ГБ из {round(mem.total/1024**3, 1)} ГБ."
    if "процессор" in text or "cpu" in text or "нагрузка" in text:
        cpu = psutil.cpu_percent(interval=1)
        return f"Нагрузка на процессор: {cpu}%."
    if "диск" in text:
        disk = psutil.disk_usage("C:\\")
        return f"Диск C: свободно {round(disk.free/1024**3, 1)} ГБ из {round(disk.total/1024**3, 1)} ГБ."

    # --- БРАУЗЕР ---
    if "браузер" in text:
        webbrowser.open("https://google.com")
        return "Открываю браузер."

    return None


if __name__ == '__main__':
    print("=" * 52)
    print("  J.A.R.V.I.S Server — запущен!")
    print("  http://localhost:5000")
    print()
    print("  Команды: папки, файлы, сайты, системные")
    print("  Оставьте это окно открытым.")
    print("=" * 52)
    app.run(host='0.0.0.0', port=5000, debug=False)
