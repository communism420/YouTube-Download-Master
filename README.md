# 📺 YouTube Download Master
Best program for downloading YouTube videos (with yt-dlp)

## 🇬🇧 ENGLISH INSTRUCTIONS

---

### 📋 Table of Contents

1. [Program Description](#-program-description)
2. [System Requirements](#-system-requirements)
3. [Installing Dependencies](#-installing-dependencies)
   - [Python](#1-python-1)
   - [yt-dlp](#2-yt-dlp-1)
   - [FFmpeg](#3-ffmpeg-1)
   - [pywin32 (optional)](#4-pywin32-optional)
4. [Running the Program](#-running-the-program)
5. [Operating Modes](#-operating-modes)
6. [Quality Settings](#-quality-settings)
7. [Cookies File](#-cookies-file)
8. [Download Options](#-download-options)
9. [Folder Structure](#-folder-structure)
10. [Troubleshooting](#-troubleshooting)

---

### 📖 Program Description

**YouTube Download Master** is a graphical application for downloading videos and audio from YouTube. Main features:

- ✅ Download entire channels
- ✅ Download playlists
- ✅ Download individual videos
- ✅ Extract audio in WAV, MP3, OGG formats
- ✅ Video quality selection (from 144p to 4K)
- ✅ Automatic resume of interrupted downloads
- ✅ Cookies support for accessing private content
- ✅ Bilingual interface (Russian/English)

---

### 💻 System Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | Windows 10/11, Linux, macOS |
| Python | 3.7 or newer |
| RAM | 4 GB minimum |
| Free Space | Depends on content volume |
| Internet | Stable connection |

---

### 📦 Installing Dependencies

#### 1. Python

**Windows:**

1. Go to official website: https://www.python.org/downloads/
2. Download the latest Python version (click "Download Python 3.x.x")
3. Run the installer
4. **⚠️ IMPORTANT:** Check the **"Add Python to PATH"** box at the bottom of the installer window
5. Click "Install Now"
6. Wait for installation to complete

**Verify installation:**
```
Win + R → cmd → Enter
python --version
```
You should see something like: `Python 3.12.0`

---

#### 2. yt-dlp

**Step 1: Download**

1. Go to releases page: https://github.com/yt-dlp/yt-dlp/releases/latest
2. In the **Assets** section, find and download **`yt-dlp.exe`**

**Step 2: Placement**

1. Create folder `C:\yt-dlp`
2. Move the downloaded `yt-dlp.exe` file to this folder
3. Full path should be: `C:\yt-dlp\yt-dlp.exe`

**Step 3: Add to PATH**

1. Press `Win + R`, type `sysdm.cpl` and press Enter
2. Go to **"Advanced"** tab
3. Click **"Environment Variables..."** button
4. In **"User variables"** section, find `Path` variable and double-click it
5. Click **"New"**
6. Enter: `C:\yt-dlp`
7. Click **"OK"** in all open windows

**Verify installation:**
```
Win + R → cmd → Enter
yt-dlp --version
```
You should see version, e.g.: `2024.12.06`

---

#### 3. FFmpeg

**Step 1: Download**

1. Go to: https://www.gyan.dev/ffmpeg/builds/
2. In **"Release builds"** section, download **`ffmpeg-release-essentials.zip`**

**Step 2: Extract**

1. Extract the archive
2. Inside you'll find a folder like `ffmpeg-7.0-essentials_build`
3. Rename it to `ffmpeg`
4. Move the `ffmpeg` folder to `C:\`, so you have `C:\ffmpeg`

**Step 3: Add to PATH**

1. Open Environment Variables (as described above for yt-dlp)
2. Add new line to `Path` variable: `C:\ffmpeg\bin`
3. Click **"OK"** in all windows

**Verify installation:**
```
Win + R → cmd → Enter
ffmpeg -version
```
You should see ffmpeg version information.

---

#### 4. pywin32 (optional)

This library improves file selection dialogs on Windows. The program works without it, but dialogs will be basic.

**Installation:**
```
Win + R → cmd → Enter
pip install pywin32
```

---

### 🚀 Running the Program

**Method 1: Double-click**
- Simply double-click on `YouTube Download Master.py` file

**Method 2: Via Command Line**
```
cd path\to\script\folder
python "YouTube Download Master.py"
```

**Method 3: Create Shortcut**
1. Right-click on file → "Create shortcut"
2. Move shortcut to desktop
3. Launch with double-click

**Method 4: Download and start the exe file**
1. And that's it.

---

### 🎯 Operating Modes

#### 📺 Channel
Downloads **all videos** from specified YouTube channel.

**Supported URL formats:**
- `https://www.youtube.com/@username`
- `https://www.youtube.com/channel/UCxxxxxxxxx`
- `https://www.youtube.com/c/ChannelName`

**Features:**
- Creates `archive.txt` file to track downloaded videos
- On subsequent runs, only new videos are downloaded
- Videos are saved in folder named after channel

---

#### 📋 Playlist
Downloads all videos from specified playlist.

**Supported URL formats:**
- `https://www.youtube.com/playlist?list=PLxxxxxxxxx`
- Link to any video from playlist (playlist will be detected automatically)

**Features:**
- Creates `archive.txt` file
- Videos saved in structure: `Channel / Playlist / video`

---

#### 🎬 Single Video
Downloads one specific video.

**Supported URL formats:**
- `https://www.youtube.com/watch?v=xxxxxxxxxxx`
- `https://youtu.be/xxxxxxxxxxx`

**Features:**
- `archive.txt` file is NOT created
- Video is saved directly in selected folder

---

#### 🎵 Audio Only
Extracts audio track from video.

**Sub-modes:**
| Source | Description |
|--------|-------------|
| 🎬 Single Video | Audio from one video |
| 📋 Playlist | Audio from all playlist videos |
| 📺 Channel | Audio from entire channel (⚠️ for insane people!) |

**Audio formats:**
| Format | Description | Bitrate |
|--------|-------------|---------|
| WAV | Uncompressed, maximum quality | Not applicable |
| MP3 | Universal compressed format | 64-320 kbps |
| OGG | Open compressed format | 64-320 kbps |

---

### 🎚️ Quality Settings

#### Video Quality

| Option | Resolution | Recommendation |
|--------|------------|----------------|
| Maximum | Best available | For archiving |
| 4K (2160p) | 3840×2160 | Large screen, lots of space |
| 1440p (2K) | 2560×1440 | Good balance |
| 1080p (Full HD) | 1920×1080 | **Recommended** |
| 720p (HD) | 1280×720 | Save space |
| 480p (SD) | 854×480 | Slow internet |
| 360p | 640×360 | Minimum quality |
| 240p | 426×240 | Very slow internet |
| 144p | 256×144 | Only audio matters |

#### Audio Bitrate (for MP3/OGG)

| Option | Quality | File Size |
|--------|---------|-----------|
| Max quality | Excellent | Large |
| 320 kbps | Excellent | Large |
| 256 kbps | Very good | Medium |
| 192 kbps | Good | Medium |
| 128 kbps | Acceptable | Small |
| 96 kbps | Low | Very small |
| 64 kbps | Poor | Minimal |

---

### 🍪 Cookies File

Cookies are needed to access:
- Age-restricted videos
- Private videos (if you have access)
- Members-only videos
- Content available only to logged-in users

**How to get cookies file:**

1. Install browser extension **"Get cookies.txt LOCALLY"**:
   - [Chrome](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - [Firefox](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/)

2. Log into your YouTube account in the browser

3. While on YouTube website, click the extension icon

4. Click **"Export"**

5. Save `cookies.txt` file to convenient location

6. Specify path to this file in the program

**⚠️ Important:**
- Don't share your cookies file with others
- Cookies may expire — update them if you have access issues
- Store the file in a secure location

---

### ⚙️ Download Options

#### 🔄 Restart After Each Video

**What it does:** After downloading each video, the yt-dlp process restarts.

**When useful:**
- When downloading large channels (1000+ videos)
- With unstable internet connection
- If yt-dlp "freezes" during long sessions
- Memory errors on low-spec computers

**When NOT needed:**
- When downloading small playlists
- With stable internet
- If you want maximum speed

---

### 📁 Folder Structure

#### "Channel" Mode
```
📂 Download folder/
└── 📂 Channel name/
    ├── 00001. Video title 1 [id].mp4
    ├── 00002. Video title 2 [id].mp4
    ├── 00003. Video title 3 [id].mp4
    └── archive.txt
```

#### "Playlist" Mode
```
📂 Download folder/
└── 📂 Channel name/
    └── 📂 Playlist name/
        ├── 00001. Video title 1 [id].mp4
        ├── 00002. Video title 2 [id].mp4
        └── archive.txt
```

#### "Single Video" Mode
```
📂 Download folder/
└── Video title [id].mp4
```

#### "Audio" Mode
```
📂 Download folder/
└── Video title [id].mp3  (or .wav, .ogg)
```

---

### 🔧 Troubleshooting

#### ❌ "yt-dlp not found"

**Cause:** yt-dlp is not installed or not added to PATH.

**Solution:**
1. Make sure `yt-dlp.exe` file is in `C:\yt-dlp\`
2. Verify that `C:\yt-dlp` is added to PATH variable
3. **Restart your computer** after changing PATH
4. Check in command line: `yt-dlp --version`

---

#### ❌ "ffmpeg not found"

**Cause:** ffmpeg is not installed or not added to PATH.

**Solution:**
1. Make sure `C:\ffmpeg\bin\` folder contains `ffmpeg.exe` file
2. Verify that `C:\ffmpeg\bin` is added to PATH
3. Restart your computer
4. Check: `ffmpeg -version`

---

#### ❌ "Video unavailable" / "Sign in to confirm your age"

**Cause:** Video requires authorization.

**Solution:**
1. Export cookies from browser (see section above)
2. Specify path to cookies file in the program
3. Make sure you're logged into YouTube in your browser

---

#### ❌ "HTTP Error 403: Forbidden"

**Cause:** YouTube is blocking requests.

**Solution:**
1. Update yt-dlp (click "Update yt-dlp" button in program)
2. Use fresh cookies
3. Wait some time and try again
4. Try using VPN

---

#### ❌ "Unable to extract video data"

**Cause:** Outdated yt-dlp version.

**Solution:**
1. Click **"Update yt-dlp"** button in the program
2. Or download new version from GitHub manually

---

#### ❌ Download is very slow

**Possible causes and solutions:**
1. **YouTube throttling** — use cookies
2. **Slow internet** — select lower quality
3. **Server overload** — try later
4. **VPN slowing down** — try without VPN

---

#### ❌ Program freezes when downloading large channel

**Solution:**
1. Enable **"Restart after each video"** option
2. This prevents memory leaks during long sessions

---

#### ❌ "Python not found" on launch

**Solution:**
1. Reinstall Python with **"Add Python to PATH"** checked
2. Or run via command line:
   ```
   C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe YouTube_Download_Master_5_1.py
   ```

---

### 💡 Useful Tips

1. **Regularly update yt-dlp** — YouTube frequently changes its code, and old versions stop working

2. **Use SSD** for download folder — this will speed up file writing

3. **Don't close the program** during download — use the "Stop" button

4. **Check free space** before downloading large channels

5. **Backup** your `archive.txt` file — it contains list of downloaded videos

---

## 📄 License

This program is provided as-is for personal use.

## 🔗 Links

- yt-dlp: https://github.com/yt-dlp/yt-dlp
- FFmpeg: https://ffmpeg.org/
- Python: https://www.python.org/

---

## 🇷🇺 ИНСТРУКЦИЯ НА РУССКОМ

---

### 📋 Содержание

1. [Описание программы](#-описание-программы)
2. [Системные требования](#-системные-требования)
3. [Установка зависимостей](#-установка-зависимостей)
   - [Python](#1-python)
   - [yt-dlp](#2-yt-dlp)
   - [FFmpeg](#3-ffmpeg)
   - [pywin32 (опционально)](#4-pywin32-опционально)
4. [Запуск программы](#-запуск-программы)
5. [Режимы работы](#-режимы-работы)
6. [Настройки качества](#-настройки-качества)
7. [Файл cookies](#-файл-cookies)
8. [Опции скачивания](#-опции-скачивания)
9. [Структура папок](#-структура-папок)
10. [Решение проблем](#-решение-проблем)

---

### 📖 Описание программы

**YouTube Download Master** — это графическая программа для скачивания видео и аудио с YouTube. Основные возможности:

- ✅ Скачивание целых каналов
- ✅ Скачивание плейлистов
- ✅ Скачивание отдельных видео
- ✅ Извлечение аудио в форматах WAV, MP3, OGG
- ✅ Выбор качества видео (от 144p до 4K)
- ✅ Автоматическое продолжение прерванных загрузок
- ✅ Поддержка cookies для доступа к приватному контенту
- ✅ Двуязычный интерфейс (русский/английский)

---

### 💻 Системные требования

| Компонент | Требование |
|-----------|------------|
| Операционная система | Windows 10/11, Linux, macOS |
| Python | 3.7 или новее |
| Оперативная память | 4 ГБ минимум |
| Свободное место | Зависит от объёма скачиваемого контента |
| Интернет | Стабильное соединение |

---

### 📦 Установка зависимостей

#### 1. Python

**Windows:**

1. Перейдите на официальный сайт: https://www.python.org/downloads/
2. Скачайте последнюю версию Python (кнопка "Download Python 3.x.x")
3. Запустите установщик
4. **⚠️ ВАЖНО:** Поставьте галочку **"Add Python to PATH"** в самом низу окна установщика
5. Нажмите "Install Now"
6. Дождитесь завершения установки

**Проверка установки:**
```
Win + R → cmd → Enter
python --version
```
Должно появиться что-то вроде: `Python 3.12.0`

---

#### 2. yt-dlp

**Шаг 1: Скачивание**

1. Перейдите на страницу релизов: https://github.com/yt-dlp/yt-dlp/releases/latest
2. В разделе **Assets** найдите и скачайте файл **`yt-dlp.exe`**

**Шаг 2: Размещение**

1. Создайте папку `C:\yt-dlp`
2. Переместите скачанный файл `yt-dlp.exe` в эту папку
3. Полный путь к файлу должен быть: `C:\yt-dlp\yt-dlp.exe`

**Шаг 3: Добавление в PATH**

1. Нажмите `Win + R`, введите `sysdm.cpl` и нажмите Enter
2. Перейдите на вкладку **"Дополнительно"**
3. Нажмите кнопку **"Переменные среды..."**
4. В разделе **"Переменные среды пользователя"** найдите переменную `Path` и дважды кликните на неё
5. Нажмите **"Создать"**
6. Введите: `C:\yt-dlp`
7. Нажмите **"ОК"** во всех открытых окнах

**Проверка установки:**
```
Win + R → cmd → Enter
yt-dlp --version
```
Должна появиться версия, например: `2024.12.06`

---

#### 3. FFmpeg

**Шаг 1: Скачивание**

1. Перейдите на сайт: https://www.gyan.dev/ffmpeg/builds/
2. В разделе **"Release builds"** скачайте **`ffmpeg-release-essentials.zip`**

**Шаг 2: Распаковка**

1. Распакуйте архив
2. Внутри будет папка вида `ffmpeg-7.0-essentials_build`
3. Переименуйте её в `ffmpeg`
4. Переместите папку `ffmpeg` в `C:\`, чтобы получилось `C:\ffmpeg`

**Шаг 3: Добавление в PATH**

1. Откройте переменные среды (как описано выше для yt-dlp)
2. В переменную `Path` добавьте новую строку: `C:\ffmpeg\bin`
3. Нажмите **"ОК"** во всех окнах

**Проверка установки:**
```
Win + R → cmd → Enter
ffmpeg -version
```
Должна появиться информация о версии ffmpeg.

---

#### 4. pywin32 (опционально)

Эта библиотека улучшает диалоги выбора файлов в Windows. Без неё программа работает, но диалоги будут стандартными.

**Установка:**
```
Win + R → cmd → Enter
pip install pywin32
```

---

### 🚀 Запуск программы

**Способ 1: Двойной клик**
- Просто дважды кликните на файл `YouTube_Download_Master_5_1.py`

**Способ 2: Через командную строку**
```
cd путь\к\папке\со\скриптом
python "YouTube Download Master.py"
```

**Способ 3: Создание ярлыка**
1. Кликните правой кнопкой на файл → "Создать ярлык"
2. Переместите ярлык на рабочий стол
3. Запускайте двойным кликом

**Способ 4: Скачайте и запустите exe-файл**
1. На этом всё.

---

### 🎯 Режимы работы

#### 📺 Канал
Скачивает **все видео** с указанного YouTube-канала.

**Поддерживаемые форматы URL:**
- `https://www.youtube.com/@username`
- `https://www.youtube.com/channel/UCxxxxxxxxx`
- `https://www.youtube.com/c/ChannelName`

**Особенности:**
- Создаётся файл `archive.txt` для отслеживания скачанных видео
- При повторном запуске скачиваются только новые видео
- Видео сохраняются в папку с именем канала

---

#### 📋 Плейлист
Скачивает все видео из указанного плейлиста.

**Поддерживаемые форматы URL:**
- `https://www.youtube.com/playlist?list=PLxxxxxxxxx`
- Ссылка на любое видео из плейлиста (плейлист определится автоматически)

**Особенности:**
- Создаётся файл `archive.txt`
- Видео сохраняются в структуру: `Канал / Плейлист / видео`

---

#### 🎬 Один ролик
Скачивает одно конкретное видео.

**Поддерживаемые форматы URL:**
- `https://www.youtube.com/watch?v=xxxxxxxxxxx`
- `https://youtu.be/xxxxxxxxxxx`

**Особенности:**
- Файл `archive.txt` НЕ создаётся
- Видео сохраняется прямо в выбранную папку

---

#### 🎵 Только аудио
Извлекает аудиодорожку из видео.

**Подрежимы:**
| Источник | Описание |
|----------|----------|
| 🎬 Один ролик | Аудио из одного видео |
| 📋 Плейлист | Аудио из всех видео плейлиста |
| 📺 Канал | Аудио со всего канала (⚠️ для психически больных людей!) |

**Форматы аудио:**
| Формат | Описание | Битрейт |
|--------|----------|---------|
| WAV | Без сжатия, максимальное качество | Не применяется |
| MP3 | Универсальный сжатый формат | 64-320 kbps |
| OGG | Открытый сжатый формат | 64-320 kbps |

---

### 🎚️ Настройки качества

#### Качество видео

| Опция | Разрешение | Рекомендация |
|-------|------------|--------------|
| Максимальное | Лучшее доступное | Для архивирования |
| 4K (2160p) | 3840×2160 | Большой экран, много места |
| 1440p (2K) | 2560×1440 | Хороший баланс |
| 1080p (Full HD) | 1920×1080 | **Рекомендуется** |
| 720p (HD) | 1280×720 | Экономия места |
| 480p (SD) | 854×480 | Слабый интернет |
| 360p | 640×360 | Минимальное качество |
| 240p | 426×240 | Очень слабый интернет |
| 144p | 256×144 | Только аудио важно |

#### Битрейт аудио (для MP3/OGG)

| Опция | Качество | Размер файла |
|-------|----------|--------------|
| Макс. качество | Отличное | Большой |
| 320 kbps | Отличное | Большой |
| 256 kbps | Очень хорошее | Средний |
| 192 kbps | Хорошее | Средний |
| 128 kbps | Приемлемое | Маленький |
| 96 kbps | Низкое | Очень маленький |
| 64 kbps | Плохое | Минимальный |

---

### 🍪 Файл cookies

Cookies нужны для доступа к:
- Видео с возрастными ограничениями
- Приватным видео (если у вас есть доступ)
- Видео для участников канала (Members only)
- Контенту, доступному только авторизованным пользователям

**Как получить файл cookies:**

1. Установите расширение для браузера **"Get cookies.txt LOCALLY"**:
   - [Chrome](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - [Firefox](https://addons.mozilla.org/ru/firefox/addon/get-cookies-txt-locally/)

2. Войдите в свой аккаунт YouTube в браузере

3. Находясь на сайте YouTube, кликните на иконку расширения

4. Нажмите **"Export"** или **"Экспорт"**

5. Сохраните файл `cookies.txt` в удобное место

6. В программе укажите путь к этому файлу

**⚠️ Важно:**
- Не делитесь файлом cookies с другими людьми
- Cookies могут устаревать — обновляйте их при проблемах с доступом
- Храните файл в безопасном месте

---

### ⚙️ Опции скачивания

#### 🔄 Перезапуск после каждого ролика

**Что делает:** После скачивания каждого видео процесс yt-dlp перезапускается.

**Когда полезно:**
- При скачивании больших каналов (1000+ видео)
- При нестабильном интернет-соединении
- Если yt-dlp "зависает" на длинных сессиях
- При ошибках памяти на слабых компьютерах

**Когда НЕ нужно:**
- При скачивании небольших плейлистов
- При стабильном интернете
- Если хотите максимальную скорость

---

### 📁 Структура папок

#### Режим "Канал"
```
📂 Папка загрузки/
└── 📂 Имя канала/
    ├── 00001. Название видео 1 [id].mp4
    ├── 00002. Название видео 2 [id].mp4
    ├── 00003. Название видео 3 [id].mp4
    └── archive.txt
```

#### Режим "Плейлист"
```
📂 Папка загрузки/
└── 📂 Имя канала/
    └── 📂 Название плейлиста/
        ├── 00001. Название видео 1 [id].mp4
        ├── 00002. Название видео 2 [id].mp4
        └── archive.txt
```

#### Режим "Один ролик"
```
📂 Папка загрузки/
└── Название видео [id].mp4
```

#### Режим "Аудио"
```
📂 Папка загрузки/
└── Название видео [id].mp3  (или .wav, .ogg)
```

---

### 🔧 Решение проблем

#### ❌ "yt-dlp не найден"

**Причина:** yt-dlp не установлен или не добавлен в PATH.

**Решение:**
1. Убедитесь, что файл `yt-dlp.exe` находится в `C:\yt-dlp\`
2. Проверьте, что `C:\yt-dlp` добавлен в переменную PATH
3. **Перезапустите компьютер** после изменения PATH
4. Проверьте в командной строке: `yt-dlp --version`

---

#### ❌ "ffmpeg не найден"

**Причина:** ffmpeg не установлен или не добавлен в PATH.

**Решение:**
1. Убедитесь, что папка `C:\ffmpeg\bin\` содержит файл `ffmpeg.exe`
2. Проверьте, что `C:\ffmpeg\bin` добавлен в PATH
3. Перезапустите компьютер
4. Проверьте: `ffmpeg -version`

---

#### ❌ "Видео недоступно" / "Sign in to confirm your age"

**Причина:** Видео требует авторизации.

**Решение:**
1. Экспортируйте cookies из браузера (см. раздел выше)
2. Укажите путь к файлу cookies в программе
3. Убедитесь, что вы авторизованы в YouTube в браузере

---

#### ❌ "HTTP Error 403: Forbidden"

**Причина:** YouTube блокирует запросы.

**Решение:**
1. Обновите yt-dlp (кнопка "Обновить yt-dlp" в программе)
2. Используйте свежие cookies
3. Подождите некоторое время и попробуйте снова
4. Попробуйте использовать VPN

---

#### ❌ "Unable to extract video data"

**Причина:** Устаревшая версия yt-dlp.

**Решение:**
1. Нажмите кнопку **"Обновить yt-dlp"** в программе
2. Или скачайте новую версию с GitHub вручную

---

#### ❌ Скачивание очень медленное

**Возможные причины и решения:**
1. **Ограничение YouTube** — используйте cookies
2. **Медленный интернет** — выберите более низкое качество
3. **Перегрузка сервера** — попробуйте позже
4. **VPN замедляет** — попробуйте без VPN

---

#### ❌ Программа зависает при скачивании большого канала

**Решение:**
1. Включите опцию **"Перезапускать после каждого ролика"**
2. Это предотвратит утечки памяти при длительных сессиях

---

#### ❌ "Python не найден" при запуске

**Решение:**
1. Переустановите Python с галочкой **"Add Python to PATH"**
2. Или запустите через командную строку:
   ```
   C:\Users\ВашеИмя\AppData\Local\Programs\Python\Python312\python.exe YouTube_Download_Master_5_1.py
   ```

---

### 💡 Полезные советы

1. **Регулярно обновляйте yt-dlp** — YouTube часто меняет свой код, и старые версии перестают работать

2. **Используйте SSD** для папки загрузки — это ускорит запись файлов

3. **Не закрывайте программу** во время скачивания — используйте кнопку "Стоп"

4. **Проверяйте свободное место** перед скачиванием больших каналов

5. **Делайте бэкапы** файла `archive.txt` — он содержит список скачанных видео

---

---
