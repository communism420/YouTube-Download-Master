#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    YOUTUBE DOWNLOAD MASTER                                   ║
║                                                                              ║
║  Скачивание YouTube-контента в выбранном качестве                            ║
║  БЕЗ перекодирования. Использует yt-dlp + ffmpeg.                            ║
║                                                                              ║
║  Режимы:                                                                     ║
║    • Канал - все видео с канала                                              ║
║    • Плейлист - все видео из плейлиста                                       ║
║    • Один ролик - одно конкретное видео                                      ║
║    • Аудио - извлечение аудио (WAV/MP3/OGG) из:                              ║
║        - одного ролика                                                       ║
║        - плейлиста                                                           ║
║        - всего канала                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

REQUIREMENTS / ТРЕБОВАНИЯ:
  - Python 3.7+
  - yt-dlp (pip install yt-dlp)
  - ffmpeg in PATH
  - [optional] pywin32 for better dialogs: pip install pywin32

RUN / ЗАПУСК:
  python youtube_channel_downloader.py
"""

import os
import sys
import re
import json
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════════
#  КОНСТАНТЫ
# ══════════════════════════════════════════════════════════════════════════════

CONFIG_FILE = Path.home() / ".youtube_downloader_config.json"

# Флаги для subprocess (Windows: скрыть консоль)
SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0

# Кроссплатформенные шрифты
FONT_FAMILY = ('Segoe UI', 'Helvetica', 'Arial', 'sans-serif')
FONT_MONO = ('Consolas', 'Monaco', 'Courier New', 'monospace')

# Таймауты
SUBPROCESS_TIMEOUT = 15  # секунд для проверки зависимостей
PROCESS_TERMINATE_TIMEOUT = 3  # секунд на graceful termination
PROCESS_KILL_TIMEOUT = 2  # секунд на принудительное завершение

# Константы для режима restart
MAX_CONSECUTIVE_EMPTY_RUNS = 3  # Количество пустых запусков перед остановкой

# Лимит строк в логе (для экономии памяти)
LOG_MAX_LINES = 5000

# Предкомпилированные regex для парсинга прогресса
PROGRESS_REGEX = re.compile(r'[Dd]ownloading\s+(?:item|video)\s+(\d+)\s+of\s+(\d+)')

# Паттерны реально скачанного контента
DOWNLOAD_COMPLETE_PATTERNS = [
    '[download] 100%',
    'has already been downloaded',
]

# Паттерны пропуска из-за архива (НЕ считается как новое скачивание)
ARCHIVE_SKIP_PATTERNS = [
    'has already been recorded in the archive'
]


def get_available_font(preferred_fonts, size, style=''):
    """Возвращает первый доступный шрифт из списка.
    
    Args:
        preferred_fonts: Кортеж предпочтительных шрифтов
        size: Размер шрифта
        style: Стиль ('bold', 'italic', '')
    
    Returns:
        Кортеж (font_name, size, style) для использования в tkinter
    """
    try:
        available = tkfont.families()
        for font in preferred_fonts:
            if font in available:
                return (font, size, style) if style else (font, size)
    except Exception:
        pass
    # Fallback на первый шрифт из списка (tkinter подставит системный)
    return (preferred_fonts[0], size, style) if style else (preferred_fonts[0], size)


# ══════════════════════════════════════════════════════════════════════════════
#  ЛОКАЛИЗАЦИЯ / LOCALIZATION
# ══════════════════════════════════════════════════════════════════════════════

TRANSLATIONS = {
    "ru": {
        # Заголовки
        "window_title": "🎬 YouTube Downloader",
        "main_title": "📺 YouTube Downloader",
        "subtitle": "Скачивание в выбранном качестве без лишнего перекодирования",
        
        # Контекстное меню
        "ctx_cut": "Вырезать",
        "ctx_copy": "Копировать",
        "ctx_paste": "Вставить",
        "ctx_select_all": "Выделить всё",
        "ctx_clear": "Очистить",
        
        # Режимы скачивания
        "mode_label": "📦 Режим скачивания:",
        "mode_channel": "📺 Канал",
        "mode_playlist": "📋 Плейлист",
        "mode_video": "🎬 Один ролик",
        "mode_audio": "🎵 Только аудио",
        "mode_channel_desc": "Все видео с канала",
        "mode_playlist_desc": "Все видео из плейлиста",
        "mode_video_desc": "Одно конкретное видео",
        "mode_audio_desc": "Аудио в WAV/MP3/OGG",
        
        # Качество видео
        "video_quality_label": "🎬 Качество видео:",
        "quality_max": "Максимальное",
        "quality_4k": "4K (2160p)",
        "quality_1440p": "1440p (2K)",
        "quality_1080p": "1080p (Full HD)",
        "quality_720p": "720p (HD)",
        "quality_480p": "480p (SD)",
        "quality_360p": "360p",
        "quality_240p": "240p",
        "quality_144p": "144p",
        
        # Настройки аудио
        "audio_format_label": "🎵 Формат аудио:",
        "audio_bitrate_label": "📊 Битрейт:",
        "bitrate_max": "Макс. качество",
        "bitrate_320": "320 kbps",
        "bitrate_256": "256 kbps",
        "bitrate_192": "192 kbps",
        "bitrate_128": "128 kbps",
        "bitrate_96": "96 kbps",
        "bitrate_64": "64 kbps",
        
        # Источник аудио
        "audio_source_label": "📥 Источник:",
        "audio_source_video": "🎬 Один ролик",
        "audio_source_playlist": "📋 Плейлист",
        "audio_source_channel": "📺 Канал",
        "audio_source_video_desc": "Аудио из одного видео",
        "audio_source_playlist_desc": "Аудио из всего плейлиста",
        "audio_source_channel_desc": "Аудио со всего канала 🤯",
        "url_label_audio_video": "🔗 URL видео:",
        "url_label_audio_playlist": "🔗 URL плейлиста:",
        "url_label_audio_channel": "🔗 URL канала:",
        "url_hint_audio_video": "Примеры: youtube.com/watch?v=xxxxxx  |  youtu.be/xxxxxx",
        "url_hint_audio_playlist": "Примеры: youtube.com/playlist?list=PLxxxxxx",
        "url_hint_audio_channel": "Примеры: youtube.com/@handle  |  youtube.com/channel/UCxxxxxx",
        "warn_audio_channel": "⚠️ Вы собираетесь скачать АУДИО СО ВСЕГО КАНАЛА!\n\nЭто не имеет никакого смысла.\nВы уверены, что хотите продолжить?",
        "folder_struct_audio_video": "название [id].{format} (без вложенных папок)",
        "folder_struct_audio_playlist": "Папка канала / Папка плейлиста / нумерация. название [id].{format}",
        "folder_struct_audio_channel": "Папка канала / нумерация. название [id].{format}",
        
        # Опции
        "options_label": "⚙️ Опции:",
        "restart_each_video": "🔄 Перезапускать процесс после каждого ролика",
        "restart_each_video_hint": "(помогает при долгих загрузках и ошибках соединения)",
        
        # Поля ввода
        "url_label_channel": "🔗 URL канала:",
        "url_label_playlist": "🔗 URL плейлиста:",
        "url_label_video": "🔗 URL видео:",
        "url_hint_channel": "Примеры: youtube.com/@handle  |  youtube.com/channel/UCxxxxxx",
        "url_hint_playlist": "Примеры: youtube.com/playlist?list=PLxxxxxx  |  ссылка на видео из плейлиста",
        "url_hint_video": "Примеры: youtube.com/watch?v=xxxxxx  |  youtu.be/xxxxxx",
        "outdir_label": "📁 Папка для загрузки:",
        "cookies_label": "🍪 Файл cookies.txt:",
        "cookies_hint": "💡 Используйте расширение «Get cookies.txt LOCALLY» для экспорта cookies из браузера",
        
        # Кнопки
        "browse_folder": "📂 Выбрать через Проводник...",
        "browse_file": "📄 Выбрать через Проводник...",
        "start_btn": "▶️  НАЧАТЬ ЗАГРУЗКУ",
        "stop_btn": "⏹️  ОСТАНОВИТЬ",
        "clear_log_btn": "🗑️  Очистить лог",
        "update_ytdlp_btn": "🔄 Обновить до master",
        
        # Статус зависимостей
        "deps_frame": "⚙️ Статус зависимостей",
        "checking": "⏳ Проверка...",
        "installed": "✅ Установлен",
        "not_found": "❌ НЕ НАЙДЕН",
        "pywin32_ok": "✅ Установлен (полноценные диалоги)",
        "pywin32_no": "⚠️ Не установлен (диалоги через tkinter)",
        
        # Лог
        "log_frame": "📋 Лог выполнения",
        "welcome_line2": "Выбор качества • Без лишнего перекодирования",
        
        # Счётчик прогресса
        "progress_label": "📊 Прогресс:",
        "progress_format": "{downloaded} / {total}",
        "progress_idle": "—",
        "progress_scanning": "сканирование...",
        
        # Сообщения проверки
        "checking_deps": "🔍 Проверка зависимостей...",
        "ytdlp_found": "  ✅ yt-dlp: ",
        "ytdlp_not_found": "  ❌ yt-dlp: НЕ НАЙДЕН в PATH!",
        "ytdlp_install_hint": "     Установите: pip install yt-dlp",
        "ffmpeg_found": "  ✅ ffmpeg: установлен",
        "ffmpeg_not_found": "  ❌ ffmpeg: НЕ НАЙДЕН в PATH!",
        "ffmpeg_install_hint": "     Скачайте с ffmpeg.org и добавьте в PATH",
        "pywin32_found": "  ✅ pywin32: установлен (диалоги через COM API)",
        "pywin32_not_found": "  ⚠️ pywin32: не установлен",
        "pywin32_install_hint": "     Для лучших диалогов: pip install pywin32",
        
        # Обновление yt-dlp
        "updating_ytdlp": "🔄 Обновление yt-dlp до master...",
        "updating_cmd": "   Выполняется: yt-dlp -U --update-to master",
        "update_done": "✅ Обновление завершено!",
        "update_error": "❌ Ошибка обновления: ",
        
        # Диалоги выбора
        "select_folder_title": "Выберите папку для сохранения видео",
        "select_file_title": "Выберите cookies.txt",
        "folder_selected": "📁 Выбрана папка: ",
        "file_selected": "🍪 Выбран файл: ",
        
        # Ошибки валидации
        "error": "Ошибка",
        "error_input": "Ошибка ввода",
        "warning": "Предупреждение",
        "error_no_url": "❌ Введите URL!\n\nПримеры:\n• youtube.com/@channelname\n• youtube.com/watch?v=xxxxxx",
        "error_invalid_url": "❌ Некорректный формат URL!\n\nURL должен содержать адрес сайта.\n\nПримеры:\n• https://youtube.com/@channelname\n• youtube.com/watch?v=xxxxxx",
        "warn_not_youtube": "URL не похож на YouTube-ссылку.\n\nПродолжить всё равно?",
        "error_no_outdir": "❌ Выберите папку для загрузки!\n\nНажмите кнопку «Выбрать через Проводник...»",
        "error_create_folder": "❌ Не удалось создать папку:\n\n{path}\n\nОшибка: {error}",
        "error_no_cookies": "❌ Выберите файл cookies.txt!\n\nИспользуйте расширение браузера для экспорта cookies.",
        "error_cookies_not_found": "❌ Файл cookies не найден:\n\n{path}",
        
        # Загрузка
        "folder_created": "📁 Создана папка: ",
        "url_videos_added": "ℹ️ Автоматически добавлено /videos к URL",
        "starting_download": "▶️  Запуск загрузки...",
        "stopping_download": "⏹️  Остановка загрузки...",
        "stop_hint": "   При следующем запуске загрузка продолжится с того же места",
        "download_success": "✅ ЗАГРУЗКА УСПЕШНО ЗАВЕРШЕНА!",
        "download_exit_code": "⚠️ Процесс завершился с кодом: ",
        "download_exit_hint": "   Это может быть нормально если часть видео уже была скачана",
        "download_error": "❌ Ошибка выполнения: ",
        "restarting_process": "🔄 Перезапуск процесса (скачано {count})...",
        "all_videos_downloaded": "✅ Все видео скачаны!",
        
        # Сводка настроек
        "settings_summary": "📋 СВОДКА НАСТРОЕК",
        "setting_mode": "  📦 Режим:      ",
        "setting_url": "  🔗 URL:        ",
        "setting_folder": "  📁 Папка:      ",
        "setting_cookies": "  🍪 Cookies:    ",
        "setting_archive": "  📜 Архив:      archive.txt",
        "setting_no_archive": "  📜 Архив:      не используется",
        "setting_quality": "  🎬 Качество:   ",
        "setting_format": "  🎬 Формат:     ",
        "setting_audio_format": "  🎵 Аудио:      ",
        "setting_bitrate": "  📊 Битрейт:    ",
        "setting_order": "  📊 Порядок:    старые → новые (playlist_reverse)",
        "setting_order_single": "  📊 Порядок:    не применимо (один файл)",
        "setting_retries": "  🔄 Ретраи:     infinite (пауза 5 сек между попытками)",
        "setting_restart": "  🔁 Рестарт:    после каждого ролика",
        "setting_no_restart": "  🔁 Рестарт:    выключен (один процесс)",
        "audio_no_compression": " (без сжатия)",
        
        # Структура папок
        "folder_structure": "  📂 Структура:  ",
        "folder_struct_channel": "Папка канала / нумерация. название [id].ext",
        "folder_struct_playlist": "Папка канала / Папка плейлиста / нумерация. название [id].ext",
        "folder_struct_video": "название [id].ext (без вложенных папок)",
        
        # Сохранение настроек
        "settings_saved": "💾 Настройки сохранены",
        "settings_loaded": "📂 Настройки загружены",
    },
    
    "en": {
        # Headers
        "window_title": "🎬 YouTube Downloader",
        "main_title": "📺 YouTube Downloader",
        "subtitle": "Download in selected quality without unnecessary re-encoding",
        
        # Context menu
        "ctx_cut": "Cut",
        "ctx_copy": "Copy",
        "ctx_paste": "Paste",
        "ctx_select_all": "Select All",
        "ctx_clear": "Clear",
        
        # Download modes
        "mode_label": "📦 Download mode:",
        "mode_channel": "📺 Channel",
        "mode_playlist": "📋 Playlist",
        "mode_video": "🎬 Single video",
        "mode_audio": "🎵 Audio only",
        "mode_channel_desc": "All videos from channel",
        "mode_playlist_desc": "All videos from playlist",
        "mode_video_desc": "One specific video",
        "mode_audio_desc": "Audio as WAV/MP3/OGG",
        
        # Video quality
        "video_quality_label": "🎬 Video quality:",
        "quality_max": "Maximum",
        "quality_4k": "4K (2160p)",
        "quality_1440p": "1440p (2K)",
        "quality_1080p": "1080p (Full HD)",
        "quality_720p": "720p (HD)",
        "quality_480p": "480p (SD)",
        "quality_360p": "360p",
        "quality_240p": "240p",
        "quality_144p": "144p",
        
        # Audio settings
        "audio_format_label": "🎵 Audio format:",
        "audio_bitrate_label": "📊 Bitrate:",
        "bitrate_max": "Max quality",
        "bitrate_320": "320 kbps",
        "bitrate_256": "256 kbps",
        "bitrate_192": "192 kbps",
        "bitrate_128": "128 kbps",
        "bitrate_96": "96 kbps",
        "bitrate_64": "64 kbps",
        
        # Audio source
        "audio_source_label": "📥 Source:",
        "audio_source_video": "🎬 Single video",
        "audio_source_playlist": "📋 Playlist",
        "audio_source_channel": "📺 Channel",
        "audio_source_video_desc": "Audio from one video",
        "audio_source_playlist_desc": "Audio from entire playlist",
        "audio_source_channel_desc": "Audio from entire channel 🤯",
        "url_label_audio_video": "🔗 Video URL:",
        "url_label_audio_playlist": "🔗 Playlist URL:",
        "url_label_audio_channel": "🔗 Channel URL:",
        "url_hint_audio_video": "Examples: youtube.com/watch?v=xxxxxx  |  youtu.be/xxxxxx",
        "url_hint_audio_playlist": "Examples: youtube.com/playlist?list=PLxxxxxx",
        "url_hint_audio_channel": "Examples: youtube.com/@handle  |  youtube.com/channel/UCxxxxxx",
        "warn_audio_channel": "⚠️ You're about to download AUDIO FROM THE ENTIRE CHANNEL!\n\nThis action has no point.\nAre you sure you want to continue?",
        "folder_struct_audio_video": "title [id].{format} (no subfolders)",
        "folder_struct_audio_playlist": "Channel folder / Playlist folder / number. title [id].{format}",
        "folder_struct_audio_channel": "Channel folder / number. title [id].{format}",
        
        # Options
        "options_label": "⚙️ Options:",
        "restart_each_video": "🔄 Restart process after each video",
        "restart_each_video_hint": "(helps with long downloads and connection errors)",
        
        # Input fields
        "url_label_channel": "🔗 Channel URL:",
        "url_label_playlist": "🔗 Playlist URL:",
        "url_label_video": "🔗 Video URL:",
        "url_hint_channel": "Examples: youtube.com/@handle  |  youtube.com/channel/UCxxxxxx",
        "url_hint_playlist": "Examples: youtube.com/playlist?list=PLxxxxxx  |  video link from playlist",
        "url_hint_video": "Examples: youtube.com/watch?v=xxxxxx  |  youtu.be/xxxxxx",
        "outdir_label": "📁 Download folder:",
        "cookies_label": "🍪 cookies.txt file:",
        "cookies_hint": "💡 Use the «Get cookies.txt LOCALLY» extension to export cookies from your browser",
        
        # Buttons
        "browse_folder": "📂 Browse with Explorer...",
        "browse_file": "📄 Browse with Explorer...",
        "start_btn": "▶️  START DOWNLOAD",
        "stop_btn": "⏹️  STOP",
        "clear_log_btn": "🗑️  Clear log",
        "update_ytdlp_btn": "🔄 Update to master",
        
        # Dependencies status
        "deps_frame": "⚙️ Dependencies status",
        "checking": "⏳ Checking...",
        "installed": "✅ Installed",
        "not_found": "❌ NOT FOUND",
        "pywin32_ok": "✅ Installed (full dialogs)",
        "pywin32_no": "⚠️ Not installed (tkinter dialogs)",
        
        # Log
        "log_frame": "📋 Execution log",
        "welcome_line2": "Quality selection • No unnecessary re-encoding",
        
        # Progress counter
        "progress_label": "📊 Progress:",
        "progress_format": "{downloaded} / {total}",
        "progress_idle": "—",
        "progress_scanning": "scanning...",
        
        # Check messages
        "checking_deps": "🔍 Checking dependencies...",
        "ytdlp_found": "  ✅ yt-dlp: ",
        "ytdlp_not_found": "  ❌ yt-dlp: NOT FOUND in PATH!",
        "ytdlp_install_hint": "     Install: pip install yt-dlp",
        "ffmpeg_found": "  ✅ ffmpeg: installed",
        "ffmpeg_not_found": "  ❌ ffmpeg: NOT FOUND in PATH!",
        "ffmpeg_install_hint": "     Download from ffmpeg.org and add to PATH",
        "pywin32_found": "  ✅ pywin32: installed (COM API dialogs)",
        "pywin32_not_found": "  ⚠️ pywin32: not installed",
        "pywin32_install_hint": "     For better dialogs: pip install pywin32",
        
        # yt-dlp update
        "updating_ytdlp": "🔄 Updating yt-dlp to master...",
        "updating_cmd": "   Running: yt-dlp -U --update-to master",
        "update_done": "✅ Update complete!",
        "update_error": "❌ Update error: ",
        
        # Selection dialogs
        "select_folder_title": "Select folder for saving videos",
        "select_file_title": "Select cookies.txt",
        "folder_selected": "📁 Folder selected: ",
        "file_selected": "🍪 File selected: ",
        
        # Validation errors
        "error": "Error",
        "error_input": "Input error",
        "warning": "Warning",
        "error_no_url": "❌ Enter URL!\n\nExamples:\n• youtube.com/@channelname\n• youtube.com/watch?v=xxxxxx",
        "error_invalid_url": "❌ Invalid URL format!\n\nURL must contain a website address.\n\nExamples:\n• https://youtube.com/@channelname\n• youtube.com/watch?v=xxxxxx",
        "warn_not_youtube": "URL doesn't look like a YouTube link.\n\nContinue anyway?",
        "error_no_outdir": "❌ Select download folder!\n\nClick «Browse with Explorer...» button",
        "error_create_folder": "❌ Failed to create folder:\n\n{path}\n\nError: {error}",
        "error_no_cookies": "❌ Select cookies.txt file!\n\nUse browser extension to export cookies.",
        "error_cookies_not_found": "❌ Cookies file not found:\n\n{path}",
        
        # Download
        "folder_created": "📁 Folder created: ",
        "url_videos_added": "ℹ️ Automatically added /videos to URL",
        "starting_download": "▶️  Starting download...",
        "stopping_download": "⏹️  Stopping download...",
        "stop_hint": "   Next run will continue from where it stopped",
        "download_success": "✅ DOWNLOAD COMPLETED SUCCESSFULLY!",
        "download_exit_code": "⚠️ Process finished with code: ",
        "download_exit_hint": "   This may be normal if some videos were already downloaded",
        "download_error": "❌ Execution error: ",
        "restarting_process": "🔄 Restarting process (downloaded {count})...",
        "all_videos_downloaded": "✅ All videos downloaded!",
        
        # Settings summary
        "settings_summary": "📋 SETTINGS SUMMARY",
        "setting_mode": "  📦 Mode:       ",
        "setting_url": "  🔗 URL:        ",
        "setting_folder": "  📁 Folder:     ",
        "setting_cookies": "  🍪 Cookies:    ",
        "setting_archive": "  📜 Archive:    archive.txt",
        "setting_no_archive": "  📜 Archive:    not used",
        "setting_quality": "  🎬 Quality:    ",
        "setting_format": "  🎬 Format:     ",
        "setting_audio_format": "  🎵 Audio:      ",
        "setting_bitrate": "  📊 Bitrate:    ",
        "setting_order": "  📊 Order:      oldest → newest (playlist_reverse)",
        "setting_order_single": "  📊 Order:      not applicable (single file)",
        "setting_retries": "  🔄 Retries:    infinite (5 sec pause between attempts)",
        "setting_restart": "  🔁 Restart:    after each video",
        "setting_no_restart": "  🔁 Restart:    disabled (single process)",
        "audio_no_compression": " (no compression)",
        
        # Folder structure
        "folder_structure": "  📂 Structure:  ",
        "folder_struct_channel": "Channel folder / number. title [id].ext",
        "folder_struct_playlist": "Channel folder / Playlist folder / number. title [id].ext",
        "folder_struct_video": "title [id].ext (no subfolders)",
        
        # Settings save/load
        "settings_saved": "💾 Settings saved",
        "settings_loaded": "📂 Settings loaded",
    }
}


# ══════════════════════════════════════════════════════════════════════════════
#  КОНСТАНТЫ КАЧЕСТВА И ФОРМАТОВ
# ══════════════════════════════════════════════════════════════════════════════

VIDEO_QUALITIES = [
    ("max", "quality_max", None),
    ("4k", "quality_4k", 2160),
    ("1440p", "quality_1440p", 1440),
    ("1080p", "quality_1080p", 1080),
    ("720p", "quality_720p", 720),
    ("480p", "quality_480p", 480),
    ("360p", "quality_360p", 360),
    ("240p", "quality_240p", 240),
    ("144p", "quality_144p", 144),
]

AUDIO_FORMATS = ["wav", "mp3", "ogg"]

AUDIO_BITRATES = [
    ("max", "bitrate_max", 0),
    ("320", "bitrate_320", 320),
    ("256", "bitrate_256", 256),
    ("192", "bitrate_192", 192),
    ("128", "bitrate_128", 128),
    ("96", "bitrate_96", 96),
    ("64", "bitrate_64", 64),
]


# ══════════════════════════════════════════════════════════════════════════════
#  МЕНЕДЖЕР НАСТРОЕК
# ══════════════════════════════════════════════════════════════════════════════

class SettingsManager:
    """Менеджер сохранения и загрузки настроек."""
    
    DEFAULT_SETTINGS = {
        "mode": "channel",
        "url": "",
        "outdir": "",
        "cookies": "",
        "video_quality": "max",
        "audio_format": "wav",
        "audio_bitrate": "max",
        "audio_source": "audio_video",
        "restart_each_video": False,
    }
    
    def __init__(self, config_path=CONFIG_FILE):
        self.config_path = Path(config_path)
    
    def load(self):
        """Загрузить настройки из файла."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # Объединяем с дефолтами (на случай новых полей)
                    settings = self.DEFAULT_SETTINGS.copy()
                    settings.update(saved)
                    return settings
        except Exception:
            pass
        return self.DEFAULT_SETTINGS.copy()
    
    def save(self, settings):
        """Сохранить настройки в файл."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False


# ══════════════════════════════════════════════════════════════════════════════
#  КОНТЕКСТНОЕ МЕНЮ / CONTEXT MENU
# ══════════════════════════════════════════════════════════════════════════════

class ContextMenuManager:
    """Менеджер контекстных меню для текстовых полей."""
    
    def __init__(self, lang="en"):
        self.t = TRANSLATIONS[lang]
    
    def bind_entry(self, entry_widget):
        """Привязать контекстное меню к полю ввода Entry."""
        menu = tk.Menu(entry_widget, tearoff=0)
        
        menu.add_command(label=self.t["ctx_cut"], accelerator="Ctrl+X",
                        command=lambda: self._cut(entry_widget))
        menu.add_command(label=self.t["ctx_copy"], accelerator="Ctrl+C",
                        command=lambda: self._copy(entry_widget))
        menu.add_command(label=self.t["ctx_paste"], accelerator="Ctrl+V",
                        command=lambda: self._paste(entry_widget))
        menu.add_separator()
        menu.add_command(label=self.t["ctx_select_all"], accelerator="Ctrl+A",
                        command=lambda: self._select_all_entry(entry_widget))
        menu.add_separator()
        menu.add_command(label=self.t["ctx_clear"],
                        command=lambda: self._clear_entry(entry_widget))
        
        entry_widget.bind("<Button-3>", lambda e: self._show_menu(e, menu, entry_widget))
        
        entry_widget.bind("<Control-a>", lambda e: self._select_all_entry(entry_widget) or "break")
        entry_widget.bind("<Control-A>", lambda e: self._select_all_entry(entry_widget) or "break")
    
    def bind_text(self, text_widget, readonly=False):
        """Привязать контекстное меню к текстовому полю Text/ScrolledText."""
        menu = tk.Menu(text_widget, tearoff=0)
        
        if not readonly:
            menu.add_command(label=self.t["ctx_cut"], accelerator="Ctrl+X",
                            command=lambda: self._cut_text(text_widget))
        
        menu.add_command(label=self.t["ctx_copy"], accelerator="Ctrl+C",
                        command=lambda: self._copy_text(text_widget))
        
        if not readonly:
            menu.add_command(label=self.t["ctx_paste"], accelerator="Ctrl+V",
                            command=lambda: self._paste_text(text_widget))
        
        menu.add_separator()
        menu.add_command(label=self.t["ctx_select_all"], accelerator="Ctrl+A",
                        command=lambda: self._select_all_text(text_widget))
        
        if not readonly:
            menu.add_separator()
            menu.add_command(label=self.t["ctx_clear"],
                            command=lambda: self._clear_text(text_widget))
        
        text_widget.bind("<Button-3>", lambda e: self._show_menu(e, menu, text_widget))
        
        text_widget.bind("<Control-a>", lambda e: self._select_all_text(text_widget) or "break")
        text_widget.bind("<Control-A>", lambda e: self._select_all_text(text_widget) or "break")
        text_widget.bind("<Control-c>", lambda e: self._copy_text(text_widget))
        text_widget.bind("<Control-C>", lambda e: self._copy_text(text_widget))
    
    def _show_menu(self, event, menu, widget):
        widget.focus_set()
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _cut(self, widget):
        widget.event_generate("<<Cut>>")
    
    def _copy(self, widget):
        widget.event_generate("<<Copy>>")
    
    def _paste(self, widget):
        widget.event_generate("<<Paste>>")
    
    def _select_all_entry(self, widget):
        widget.select_range(0, tk.END)
        widget.icursor(tk.END)
    
    def _clear_entry(self, widget):
        widget.delete(0, tk.END)
    
    def _cut_text(self, widget):
        try:
            widget.event_generate("<<Cut>>")
        except Exception:
            pass
    
    def _copy_text(self, widget):
        try:
            if widget.tag_ranges(tk.SEL):
                widget.event_generate("<<Copy>>")
        except Exception:
            pass
    
    def _paste_text(self, widget):
        try:
            widget.event_generate("<<Paste>>")
        except Exception:
            pass
    
    def _select_all_text(self, widget):
        widget.tag_add(tk.SEL, "1.0", tk.END)
        widget.mark_set(tk.INSERT, "1.0")
        widget.see(tk.INSERT)
    
    def _clear_text(self, widget):
        widget.delete("1.0", tk.END)


# ══════════════════════════════════════════════════════════════════════════════
#  ОКНО ВЫБОРА ЯЗЫКА
# ══════════════════════════════════════════════════════════════════════════════

class LanguageSelector:
    def __init__(self):
        self.selected_language = None
        self.root = tk.Tk()
        self.root.title("Language / Язык")
        self.root.resizable(False, False)
        
        width, height = 400, 200
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.configure(bg='#2b2b3d')
        self._create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        title_frame = tk.Frame(self.root, bg='#2b2b3d')
        title_frame.pack(expand=True, fill='both')
        
        tk.Label(title_frame, text="Язык / Language", font=get_available_font(FONT_FAMILY, 24, 'bold'),
                 fg='#ffffff', bg='#2b2b3d').pack(pady=(30, 40))
        
        buttons_frame = tk.Frame(title_frame, bg='#2b2b3d')
        buttons_frame.pack(expand=True)
        
        btn_style = {'font': get_available_font(FONT_FAMILY, 18, 'bold'), 'width': 8, 'height': 2,
                     'cursor': 'hand2', 'relief': 'flat', 'borderwidth': 0}
        
        eng_btn = tk.Button(buttons_frame, text="ENG", command=lambda: self._select_language("en"),
                            bg='#4a90d9', fg='white', activebackground='#357abd', activeforeground='white', **btn_style)
        eng_btn.pack(side='left', padx=20)
        eng_btn.bind('<Enter>', lambda e: eng_btn.configure(bg='#357abd'))
        eng_btn.bind('<Leave>', lambda e: eng_btn.configure(bg='#4a90d9'))
        
        rus_btn = tk.Button(buttons_frame, text="RUS", command=lambda: self._select_language("ru"),
                            bg='#d94a4a', fg='white', activebackground='#bd3737', activeforeground='white', **btn_style)
        rus_btn.pack(side='left', padx=20)
        rus_btn.bind('<Enter>', lambda e: rus_btn.configure(bg='#bd3737'))
        rus_btn.bind('<Leave>', lambda e: rus_btn.configure(bg='#d94a4a'))
    
    def _select_language(self, lang):
        self.selected_language = lang
        self.root.destroy()
    
    def _on_close(self):
        self.selected_language = None
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()
        return self.selected_language


# ══════════════════════════════════════════════════════════════════════════════
#  ДИАЛОГИ ВЫБОРА ФАЙЛОВ/ПАПОК
# ══════════════════════════════════════════════════════════════════════════════

class NativeDialogs:
    def __init__(self, lang="en"):
        self.t = TRANSLATIONS[lang]
    
    def _try_win32_folder(self, initial_dir=None):
        try:
            import pythoncom
            from win32com.shell import shell, shellcon
            fd = pythoncom.CoCreateInstance(shell.CLSID_FileOpenDialog, None,
                                            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IFileOpenDialog)
            fd.SetOptions(fd.GetOptions() | shellcon.FOS_PICKFOLDERS | shellcon.FOS_FORCEFILESYSTEM | shellcon.FOS_PATHMUSTEXIST)
            fd.SetTitle(self.t["select_folder_title"])
            # Установка начальной папки
            if initial_dir and os.path.isdir(initial_dir):
                try:
                    folder_item = shell.SHCreateItemFromParsingName(initial_dir, None, shell.IID_IShellItem)
                    fd.SetFolder(folder_item)
                except Exception:
                    pass
            try:
                fd.Show(0)
                return fd.GetResult().GetDisplayName(shellcon.SIGDN_FILESYSPATH)
            except pythoncom.com_error:
                return None
        except Exception:
            return None
    
    def _try_win32_file(self, initial_dir=None, title=None):
        try:
            import pythoncom
            from win32com.shell import shell, shellcon
            fd = pythoncom.CoCreateInstance(shell.CLSID_FileOpenDialog, None,
                                            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IFileOpenDialog)
            fd.SetOptions(fd.GetOptions() | shellcon.FOS_FORCEFILESYSTEM | shellcon.FOS_FILEMUSTEXIST)
            fd.SetTitle(title or self.t["select_file_title"])
            # Установка начальной папки
            if initial_dir and os.path.isdir(initial_dir):
                try:
                    folder_item = shell.SHCreateItemFromParsingName(initial_dir, None, shell.IID_IShellItem)
                    fd.SetFolder(folder_item)
                except Exception:
                    pass
            try:
                fd.SetFileTypes([("Text files (*.txt)", "*.txt"), ("All files (*.*)", "*.*")])
            except Exception:
                pass
            try:
                fd.Show(0)
                return fd.GetResult().GetDisplayName(shellcon.SIGDN_FILESYSPATH)
            except pythoncom.com_error:
                return None
        except Exception:
            return None
    
    def _tkinter_folder(self, initial_dir=None):
        from tkinter import filedialog
        f = filedialog.askdirectory(title=self.t["select_folder_title"],
                                    initialdir=initial_dir or os.path.expanduser("~"), mustexist=False)
        return f if f else None
    
    def _tkinter_file(self, initial_dir=None, title=None):
        from tkinter import filedialog
        f = filedialog.askopenfilename(title=title or self.t["select_file_title"],
                                       initialdir=initial_dir or os.path.expanduser("~"),
                                       filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        return f if f else None
    
    def select_folder(self, initial_dir=None):
        return self._try_win32_folder(initial_dir) or self._tkinter_folder(initial_dir)
    
    def select_file(self, initial_dir=None, title=None):
        return self._try_win32_file(initial_dir, title) or self._tkinter_file(initial_dir, title)


# ══════════════════════════════════════════════════════════════════════════════
#  ГЛАВНЫЙ КЛАСС ПРИЛОЖЕНИЯ
# ══════════════════════════════════════════════════════════════════════════════

class YouTubeDownloader:
    MODE_CHANNEL = "channel"
    MODE_PLAYLIST = "playlist"
    MODE_VIDEO = "video"
    MODE_AUDIO = "audio"
    
    # Источники для режима аудио
    AUDIO_SOURCE_VIDEO = "audio_video"
    AUDIO_SOURCE_PLAYLIST = "audio_playlist"
    AUDIO_SOURCE_CHANNEL = "audio_channel"
    
    def __init__(self, root, lang="en", settings_manager=None):
        self.root = root
        self.lang = lang
        self.t = TRANSLATIONS[lang]
        self.settings_manager = settings_manager or SettingsManager()
        
        self.root.title(self.t["window_title"])
        self.root.geometry("1000x900")
        self.root.minsize(800, 600)
        
        self.process = None
        # Thread-safe механизм остановки
        self.stop_event = threading.Event()
        self.process_lock = threading.Lock()
        
        self.total_videos = 0
        self.downloaded_videos = 0
        self.current_mode = tk.StringVar(value=self.MODE_CHANNEL)
        self.restart_each_video = tk.BooleanVar(value=False)
        
        self.video_quality = tk.StringVar(value="max")
        self.audio_format = tk.StringVar(value="wav")
        self.audio_bitrate = tk.StringVar(value="max")
        self.audio_source = tk.StringVar(value=self.AUDIO_SOURCE_VIDEO)
        
        self.dialogs = NativeDialogs(lang)
        self.ctx_menu = ContextMenuManager(lang)
        
        # Ссылки на виджеты для управления layout
        self.canvas = None
        self.scrollable_frame = None
        self.content_frame = None
        
        self._setup_styles()
        self._create_widgets()
        self._load_settings()
        
        # Сохранение настроек при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.root.after(200, lambda: threading.Thread(target=self._check_dependencies_thread, daemon=True).start())
    
    def _load_settings(self):
        """Загрузить сохранённые настройки."""
        settings = self.settings_manager.load()
        
        if settings.get("mode") in [self.MODE_CHANNEL, self.MODE_PLAYLIST, 
                                     self.MODE_VIDEO, self.MODE_AUDIO]:
            self.current_mode.set(settings["mode"])
        
        if settings.get("url"):
            self.url_var.set(settings["url"])
        
        if settings.get("outdir"):
            self.outdir_var.set(settings["outdir"])
        
        if settings.get("cookies"):
            self.cookies_var.set(settings["cookies"])
        
        # Валидация качества видео
        valid_qualities = [q[0] for q in VIDEO_QUALITIES]
        if settings.get("video_quality") in valid_qualities:
            self.video_quality.set(settings["video_quality"])
        
        if settings.get("audio_format") in AUDIO_FORMATS:
            self.audio_format.set(settings["audio_format"])
        
        # Валидация битрейта
        valid_bitrates = [b[0] for b in AUDIO_BITRATES]
        if settings.get("audio_bitrate") in valid_bitrates:
            self.audio_bitrate.set(settings["audio_bitrate"])
        
        # Валидация источника аудио
        valid_audio_sources = [self.AUDIO_SOURCE_VIDEO, self.AUDIO_SOURCE_PLAYLIST, self.AUDIO_SOURCE_CHANNEL]
        if settings.get("audio_source") in valid_audio_sources:
            self.audio_source.set(settings["audio_source"])
        
        self.restart_each_video.set(settings.get("restart_each_video", False))
        
        # Обновляем UI под загруженный режим
        self._on_mode_change()
        self._on_audio_format_change()
    
    def _save_settings(self):
        """Сохранить текущие настройки."""
        settings = {
            "mode": self.current_mode.get(),
            "url": self.url_var.get(),
            "outdir": self.outdir_var.get(),
            "cookies": self.cookies_var.get(),
            "video_quality": self.video_quality.get(),
            "audio_format": self.audio_format.get(),
            "audio_bitrate": self.audio_bitrate.get(),
            "audio_source": self.audio_source.get(),
            "restart_each_video": self.restart_each_video.get(),
        }
        self.settings_manager.save(settings)
    
    def _on_close(self):
        """Обработчик закрытия окна."""
        self._save_settings()
        
        # Останавливаем процесс если запущен
        self.stop_event.set()
        with self.process_lock:
            if self.process:
                try:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=PROCESS_TERMINATE_TIMEOUT)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait(timeout=PROCESS_KILL_TIMEOUT)
                except Exception:
                    pass
        
        self.root.destroy()
    
    def _setup_styles(self):
        style = ttk.Style()
        for theme in ['vista', 'winnative', 'clam']:
            if theme in style.theme_names():
                style.theme_use(theme)
                break
        
        # Используем кроссплатформенные шрифты
        style.configure('Title.TLabel', font=get_available_font(FONT_FAMILY, 16, 'bold'))
        style.configure('Header.TLabel', font=get_available_font(FONT_FAMILY, 11, 'bold'))
        style.configure('Hint.TLabel', font=get_available_font(FONT_FAMILY, 9), foreground='gray')
        style.configure('ModeDesc.TLabel', font=get_available_font(FONT_FAMILY, 9), foreground='#666666')
        style.configure('Progress.TLabel', font=get_available_font(FONT_FAMILY, 12, 'bold'))
        style.configure('Big.TButton', font=get_available_font(FONT_FAMILY, 11), padding=10)
        style.configure('Mode.TRadiobutton', font=get_available_font(FONT_FAMILY, 10))
        style.configure('Option.TCheckbutton', font=get_available_font(FONT_FAMILY, 10))
        style.configure('Quality.TRadiobutton', font=get_available_font(FONT_FAMILY, 9))
    
    def _create_widgets(self):
        # Настраиваем корневое окно для растяжения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Основной контейнер
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Canvas для прокрутки
        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        # Прокручиваемый фрейм
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Привязка для обновления scrollregion
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        
        # Создаём окно в canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Привязка для растяжения по ширине
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем canvas и scrollbar
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Прокрутка колёсиком мыши
        self._bind_mousewheel()
        
        # Основной контент
        self.content_frame = ttk.Frame(self.scrollable_frame, padding="20")
        self.content_frame.pack(fill="both", expand=True)
        self.content_frame.columnconfigure(0, weight=1)
        
        self._create_content()
    
    def _on_frame_configure(self, event=None):
        """Обновить scrollregion при изменении размера содержимого."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Растянуть содержимое по ширине canvas."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _bind_mousewheel(self):
        """Привязать прокрутку колёсиком мыши (кроссплатформенно)."""
        def _on_mousewheel_windows(event):
            if self.canvas.bbox("all"):
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _on_mousewheel_linux(event):
            if self.canvas.bbox("all"):
                if event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
        
        def _on_mousewheel_macos(event):
            if self.canvas.bbox("all"):
                self.canvas.yview_scroll(int(-1 * event.delta), "units")
        
        def _bind_to_mousewheel(event):
            if sys.platform == 'win32':
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel_windows)
            elif sys.platform == 'darwin':
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel_macos)
            else:
                # Linux
                self.canvas.bind_all("<Button-4>", _on_mousewheel_linux)
                self.canvas.bind_all("<Button-5>", _on_mousewheel_linux)
        
        def _unbind_from_mousewheel(event):
            if sys.platform == 'win32':
                self.canvas.unbind_all("<MouseWheel>")
            elif sys.platform == 'darwin':
                self.canvas.unbind_all("<MouseWheel>")
            else:
                self.canvas.unbind_all("<Button-4>")
                self.canvas.unbind_all("<Button-5>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def _create_content(self):
        """Создание всего содержимого интерфейса."""
        row = 0
        
        # === ЗАГОЛОВОК ===
        header_frame = ttk.Frame(self.content_frame)
        header_frame.grid(row=row, column=0, sticky="ew", pady=(0, 15))
        header_frame.columnconfigure(0, weight=1)
        
        ttk.Label(header_frame, text=self.t["main_title"], style='Title.TLabel').pack(anchor="center")
        ttk.Label(header_frame, text=self.t["subtitle"], style='Hint.TLabel').pack(anchor="center", pady=(5, 0))
        row += 1
        
        # === РЕЖИМ СКАЧИВАНИЯ ===
        mode_frame = ttk.LabelFrame(self.content_frame, text=self.t["mode_label"], padding="10")
        mode_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        mode_frame.columnconfigure((0, 1, 2, 3), weight=1)
        row += 1
        
        modes = [
            (self.MODE_CHANNEL, "mode_channel", "mode_channel_desc"),
            (self.MODE_PLAYLIST, "mode_playlist", "mode_playlist_desc"),
            (self.MODE_VIDEO, "mode_video", "mode_video_desc"),
            (self.MODE_AUDIO, "mode_audio", "mode_audio_desc"),
        ]
        
        for col, (mode_val, mode_key, desc_key) in enumerate(modes):
            frame = ttk.Frame(mode_frame)
            frame.grid(row=0, column=col, sticky="w", padx=5)
            ttk.Radiobutton(frame, text=self.t[mode_key], variable=self.current_mode,
                           value=mode_val, command=self._on_mode_change, style='Mode.TRadiobutton').pack(anchor="w")
            ttk.Label(frame, text=self.t[desc_key], style='ModeDesc.TLabel').pack(anchor="w", padx=(18, 0))
        
        # === КАЧЕСТВО ВИДЕО ===
        self.video_quality_frame = ttk.LabelFrame(self.content_frame, text=self.t["video_quality_label"], padding="10")
        self.video_quality_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        self.video_quality_frame.columnconfigure(0, weight=1)
        row += 1
        
        quality_row1 = ttk.Frame(self.video_quality_frame)
        quality_row1.pack(fill="x", pady=(0, 5))
        quality_row2 = ttk.Frame(self.video_quality_frame)
        quality_row2.pack(fill="x")
        
        for i, (q_val, q_key, _) in enumerate(VIDEO_QUALITIES):
            parent = quality_row1 if i < 5 else quality_row2
            ttk.Radiobutton(parent, text=self.t[q_key], variable=self.video_quality,
                           value=q_val, style='Quality.TRadiobutton').pack(side="left", padx=(0, 15))
        
        # === НАСТРОЙКИ АУДИО ===
        self.audio_settings_frame = ttk.LabelFrame(self.content_frame, text=self.t["audio_format_label"], padding="10")
        self.audio_settings_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        self.audio_settings_frame.columnconfigure(0, weight=1)
        row += 1
        
        # Источник аудио (откуда скачивать)
        source_container = ttk.Frame(self.audio_settings_frame)
        source_container.pack(fill="x", pady=(0, 5))
        
        source_frame = ttk.Frame(source_container)
        source_frame.pack(fill="x")
        
        ttk.Label(source_frame, text=self.t["audio_source_label"], style='Header.TLabel').pack(side="left", padx=(0, 15))
        
        audio_sources = [
            (self.AUDIO_SOURCE_VIDEO, "audio_source_video"),
            (self.AUDIO_SOURCE_PLAYLIST, "audio_source_playlist"),
            (self.AUDIO_SOURCE_CHANNEL, "audio_source_channel"),
        ]
        
        for src_val, src_key in audio_sources:
            ttk.Radiobutton(source_frame, text=self.t[src_key], variable=self.audio_source,
                           value=src_val, style='Quality.TRadiobutton',
                           command=self._on_audio_source_change).pack(side="left", padx=10)
        
        # Описание выбранного источника
        self.audio_source_desc = ttk.Label(source_container, text=self.t["audio_source_video_desc"], style='ModeDesc.TLabel')
        self.audio_source_desc.pack(anchor="w", pady=(5, 0))
        
        # Разделитель
        ttk.Separator(self.audio_settings_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Формат аудио
        format_frame = ttk.Frame(self.audio_settings_frame)
        format_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(format_frame, text=self.t["audio_format_label"], style='Header.TLabel').pack(side="left", padx=(0, 15))
        
        for fmt in AUDIO_FORMATS:
            ttk.Radiobutton(format_frame, text=fmt.upper(), variable=self.audio_format,
                           value=fmt, style='Quality.TRadiobutton',
                           command=self._on_audio_format_change).pack(side="left", padx=10)
        
        # Битрейт
        self.bitrate_frame = ttk.Frame(self.audio_settings_frame)
        self.bitrate_frame.pack(fill="x")
        
        ttk.Label(self.bitrate_frame, text=self.t["audio_bitrate_label"], style='Header.TLabel').pack(side="left", padx=(0, 15))
        
        for b_val, b_key, _ in AUDIO_BITRATES:
            ttk.Radiobutton(self.bitrate_frame, text=self.t[b_key], variable=self.audio_bitrate,
                           value=b_val, style='Quality.TRadiobutton').pack(side="left", padx=5)
        
        self.audio_settings_frame.grid_remove()
        
        # === ОПЦИИ ===
        options_frame = ttk.LabelFrame(self.content_frame, text=self.t["options_label"], padding="10")
        options_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        options_frame.columnconfigure(0, weight=1)
        row += 1
        
        restart_frame = ttk.Frame(options_frame)
        restart_frame.pack(anchor="w")
        
        ttk.Checkbutton(restart_frame, text=self.t["restart_each_video"],
                       variable=self.restart_each_video, style='Option.TCheckbutton').pack(side="left")
        ttk.Label(restart_frame, text=self.t["restart_each_video_hint"], style='Hint.TLabel').pack(side="left", padx=(10, 0))
        
        # === URL ===
        url_frame = ttk.Frame(self.content_frame)
        url_frame.grid(row=row, column=0, sticky="ew", pady=(10, 0))
        url_frame.columnconfigure(0, weight=1)
        row += 1
        
        self.url_label = ttk.Label(url_frame, text=self.t["url_label_channel"], style='Header.TLabel')
        self.url_label.pack(anchor="w", pady=(0, 5))
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=get_available_font(FONT_MONO, 11))
        self.url_entry.pack(fill="x", pady=(0, 5))
        self.ctx_menu.bind_entry(self.url_entry)
        
        self.url_hint = ttk.Label(url_frame, text=self.t["url_hint_channel"], style='Hint.TLabel')
        self.url_hint.pack(anchor="w")
        
        # === ПАПКА ЗАГРУЗКИ ===
        outdir_container = ttk.Frame(self.content_frame)
        outdir_container.grid(row=row, column=0, sticky="ew", pady=(15, 0))
        outdir_container.columnconfigure(0, weight=1)
        row += 1
        
        ttk.Label(outdir_container, text=self.t["outdir_label"], style='Header.TLabel').pack(anchor="w", pady=(0, 5))
        
        outdir_frame = ttk.Frame(outdir_container)
        outdir_frame.pack(fill="x")
        outdir_frame.columnconfigure(0, weight=1)
        
        self.outdir_var = tk.StringVar()
        self.outdir_entry = ttk.Entry(outdir_frame, textvariable=self.outdir_var, font=get_available_font(FONT_MONO, 11))
        self.outdir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.ctx_menu.bind_entry(self.outdir_entry)
        self._browse_outdir_btn = ttk.Button(outdir_frame, text=self.t["browse_folder"], command=self.browse_outdir, width=28)
        self._browse_outdir_btn.grid(row=0, column=1)
        
        # === COOKIES ===
        cookies_container = ttk.Frame(self.content_frame)
        cookies_container.grid(row=row, column=0, sticky="ew", pady=(15, 0))
        cookies_container.columnconfigure(0, weight=1)
        row += 1
        
        ttk.Label(cookies_container, text=self.t["cookies_label"], style='Header.TLabel').pack(anchor="w", pady=(0, 5))
        
        cookies_frame = ttk.Frame(cookies_container)
        cookies_frame.pack(fill="x")
        cookies_frame.columnconfigure(0, weight=1)
        
        self.cookies_var = tk.StringVar()
        self.cookies_entry = ttk.Entry(cookies_frame, textvariable=self.cookies_var, font=get_available_font(FONT_MONO, 11))
        self.cookies_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.ctx_menu.bind_entry(self.cookies_entry)
        self._browse_cookies_btn = ttk.Button(cookies_frame, text=self.t["browse_file"], command=self.browse_cookies, width=28)
        self._browse_cookies_btn.grid(row=0, column=1)
        
        ttk.Label(cookies_container, text=self.t["cookies_hint"], style='Hint.TLabel').pack(anchor="w", pady=(5, 0))
        
        # === ЗАВИСИМОСТИ ===
        deps_frame = ttk.LabelFrame(self.content_frame, text=self.t["deps_frame"], padding="10")
        deps_frame.grid(row=row, column=0, sticky="ew", pady=(15, 10))
        deps_frame.columnconfigure(1, weight=1)
        row += 1
        
        ttk.Label(deps_frame, text="yt-dlp:", font=get_available_font(FONT_FAMILY, 10, 'bold')).grid(row=0, column=0, sticky="w", pady=2)
        self.ytdlp_status = ttk.Label(deps_frame, text=self.t["checking"])
        self.ytdlp_status.grid(row=0, column=1, sticky="w", padx=15, pady=2)
        self.update_btn = ttk.Button(deps_frame, text=self.t["update_ytdlp_btn"], command=self.update_ytdlp, width=20)
        self.update_btn.grid(row=0, column=2, pady=2, padx=5)
        
        ttk.Label(deps_frame, text="ffmpeg:", font=get_available_font(FONT_FAMILY, 10, 'bold')).grid(row=1, column=0, sticky="w", pady=2)
        self.ffmpeg_status = ttk.Label(deps_frame, text=self.t["checking"])
        self.ffmpeg_status.grid(row=1, column=1, sticky="w", padx=15, pady=2)
        
        # pywin32 актуален только для Windows
        if sys.platform == 'win32':
            ttk.Label(deps_frame, text="pywin32:", font=get_available_font(FONT_FAMILY, 10, 'bold')).grid(row=2, column=0, sticky="w", pady=2)
            self.pywin32_status = ttk.Label(deps_frame, text=self.t["checking"])
            self.pywin32_status.grid(row=2, column=1, sticky="w", padx=15, pady=2)
        else:
            self.pywin32_status = None
        
        # === КНОПКИ ===
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.grid(row=row, column=0, pady=15)
        row += 1
        
        self.start_btn = ttk.Button(btn_frame, text=self.t["start_btn"], command=self.start_download, style='Big.TButton', width=22)
        self.start_btn.pack(side="left", padx=10)
        self.stop_btn = ttk.Button(btn_frame, text=self.t["stop_btn"], command=self.stop_download, style='Big.TButton', state="disabled", width=18)
        self.stop_btn.pack(side="left", padx=10)
        ttk.Button(btn_frame, text=self.t["clear_log_btn"], command=self.clear_log, width=18).pack(side="left", padx=10)
        
        # === ЛОГ ===
        log_container = ttk.LabelFrame(self.content_frame, text=self.t["log_frame"], padding="10")
        log_container.grid(row=row, column=0, sticky="nsew", pady=(0, 10))
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(0, weight=1)
        self.content_frame.rowconfigure(row, weight=1)
        row += 1
        
        self.log_text = scrolledtext.ScrolledText(log_container, height=15, wrap=tk.WORD, 
                                                   font=get_available_font(FONT_MONO, 10),
                                                   bg='#1a1a2e', fg='#e0e0e0', insertbackground='white',
                                                   selectbackground='#4a4a6a', relief='flat', borderwidth=0)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled")
        self.ctx_menu.bind_text(self.log_text, readonly=True)
        
        # === ПРОГРЕСС ===
        progress_frame = ttk.Frame(self.content_frame)
        progress_frame.grid(row=row, column=0, sticky="ew", pady=(5, 0))
        
        ttk.Label(progress_frame, text=self.t["progress_label"], style='Header.TLabel').pack(side="left", padx=(0, 10))
        self.progress_value = ttk.Label(progress_frame, text=self.t["progress_idle"], style='Progress.TLabel', foreground='#4a90d9')
        self.progress_value.pack(side="left")
        
        self._show_welcome()
        self._on_audio_format_change()
    
    def _on_mode_change(self):
        """Обработчик смены режима скачивания."""
        mode = self.current_mode.get()
        
        if mode == self.MODE_AUDIO:
            self.video_quality_frame.grid_remove()
            self.audio_settings_frame.grid()
            # Обновляем URL label/hint в зависимости от источника аудио
            self._on_audio_source_change()
        else:
            labels = {
                self.MODE_CHANNEL: ("url_label_channel", "url_hint_channel"),
                self.MODE_PLAYLIST: ("url_label_playlist", "url_hint_playlist"),
                self.MODE_VIDEO: ("url_label_video", "url_hint_video"),
            }
            lbl, hint = labels[mode]
            self.url_label.config(text=self.t[lbl])
            self.url_hint.config(text=self.t[hint])
            self.video_quality_frame.grid()
            self.audio_settings_frame.grid_remove()
        
        self.root.after(10, self._on_frame_configure)
    
    def _on_audio_source_change(self):
        """Обработчик смены источника аудио."""
        source = self.audio_source.get()
        labels = {
            self.AUDIO_SOURCE_VIDEO: ("url_label_audio_video", "url_hint_audio_video", "audio_source_video_desc"),
            self.AUDIO_SOURCE_PLAYLIST: ("url_label_audio_playlist", "url_hint_audio_playlist", "audio_source_playlist_desc"),
            self.AUDIO_SOURCE_CHANNEL: ("url_label_audio_channel", "url_hint_audio_channel", "audio_source_channel_desc"),
        }
        lbl, hint, desc = labels.get(source, ("url_label_audio_video", "url_hint_audio_video", "audio_source_video_desc"))
        self.url_label.config(text=self.t[lbl])
        self.url_hint.config(text=self.t[hint])
        # Обновляем описание источника
        if hasattr(self, 'audio_source_desc'):
            self.audio_source_desc.config(text=self.t[desc])
    
    def _on_audio_format_change(self):
        fmt = self.audio_format.get()
        if fmt == "wav":
            for child in self.bitrate_frame.winfo_children():
                if isinstance(child, ttk.Radiobutton):
                    child.configure(state="disabled")
        else:
            for child in self.bitrate_frame.winfo_children():
                if isinstance(child, ttk.Radiobutton):
                    child.configure(state="normal")
    
    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        
        # Ограничение количества строк для экономии памяти
        line_count = int(self.log_text.index('end-1c').split('.')[0])
        if line_count > LOG_MAX_LINES:
            # Удаляем первые 500 строк
            self.log_text.delete('1.0', f'{line_count - LOG_MAX_LINES + 500}.0')
        
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
    
    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self._show_welcome()
    
    def _show_welcome(self):
        self.log("=" * 70)
        self.log("  YouTube Downloader".center(70))
        self.log(f"  {self.t['welcome_line2']}".center(70))
        self.log("=" * 70)
        self.log("")
    
    def _reset_progress(self):
        self.total_videos = 0
        self.downloaded_videos = 0
        self.progress_value.config(text=self.t["progress_idle"])
    
    def _update_progress_display(self):
        if self.total_videos > 0:
            text = self.t["progress_format"].format(downloaded=self.downloaded_videos, total=self.total_videos)
            color = '#228B22' if self.downloaded_videos >= self.total_videos else '#4a90d9'
            self.progress_value.config(text=text, foreground=color)
        else:
            self.progress_value.config(text=self.t["progress_scanning"], foreground='#FF8C00')
    
    def _parse_progress_from_line(self, line):
        """Парсинг прогресса с использованием предкомпилированного regex."""
        match = PROGRESS_REGEX.search(line)
        if match:
            self.total_videos = int(match.group(2))
            # Защита от переполнения
            self.downloaded_videos = min(int(match.group(1)) - 1, self.total_videos)
            self.root.after(0, self._update_progress_display)
            return True
        
        # Для прогресса считаем и скачанные, и пропущенные из архива
        if self._is_download_complete_line(line) or self._is_archive_skip_line(line):
            if self.total_videos > 0 and self.downloaded_videos < self.total_videos:
                self.downloaded_videos = min(self.downloaded_videos + 1, self.total_videos)
                self.root.after(0, self._update_progress_display)
            return True
        
        return False
    
    def _is_download_complete_line(self, line):
        """Проверить, является ли строка индикатором РЕАЛЬНОГО завершения скачивания."""
        return any(pattern in line for pattern in DOWNLOAD_COMPLETE_PATTERNS)
    
    def _is_archive_skip_line(self, line):
        """Проверить, является ли строка индикатором пропуска из-за архива."""
        return any(pattern in line for pattern in ARCHIVE_SKIP_PATTERNS)
    
    def browse_outdir(self):
        # Блокируем кнопку на время работы диалога
        if hasattr(self, '_browse_outdir_btn'):
            self._browse_outdir_btn.config(state="disabled")
        try:
            folder = self.dialogs.select_folder(self.outdir_var.get() or os.path.expanduser("~"))
            if folder:
                self.outdir_var.set(folder)
                self.log(f"{self.t['folder_selected']}{folder}")
        finally:
            if hasattr(self, '_browse_outdir_btn'):
                self._browse_outdir_btn.config(state="normal")
    
    def browse_cookies(self):
        # Блокируем кнопку на время работы диалога
        if hasattr(self, '_browse_cookies_btn'):
            self._browse_cookies_btn.config(state="disabled")
        try:
            current = self.cookies_var.get()
            file = self.dialogs.select_file(os.path.dirname(current) if current else os.path.expanduser("~"), self.t["select_file_title"])
            if file:
                self.cookies_var.set(file)
                self.log(f"{self.t['file_selected']}{file}")
        finally:
            if hasattr(self, '_browse_cookies_btn'):
                self._browse_cookies_btn.config(state="normal")
    
    def check_dependencies(self):
        """Проверка зависимостей (вызывается из главного потока)."""
        self.log(self.t["checking_deps"])
        self.log("")
        
        try:
            result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, 
                                    creationflags=SUBPROCESS_FLAGS, timeout=SUBPROCESS_TIMEOUT)
            self.ytdlp_status.config(text=f"✅ {result.stdout.strip()}", foreground="#228B22")
            self.log(f"{self.t['ytdlp_found']}{result.stdout.strip()}")
        except FileNotFoundError:
            self.ytdlp_status.config(text=self.t["not_found"], foreground="#DC143C")
            self.log(self.t["ytdlp_not_found"])
            self.log(self.t["ytdlp_install_hint"])
        except Exception as e:
            self.ytdlp_status.config(text=f"❌ Error: {e}", foreground="#DC143C")
        
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, 
                          creationflags=SUBPROCESS_FLAGS, timeout=SUBPROCESS_TIMEOUT)
            self.ffmpeg_status.config(text=self.t["installed"], foreground="#228B22")
            self.log(self.t["ffmpeg_found"])
        except FileNotFoundError:
            self.ffmpeg_status.config(text=self.t["not_found"], foreground="#DC143C")
            self.log(self.t["ffmpeg_not_found"])
            self.log(self.t["ffmpeg_install_hint"])
        except Exception:
            self.ffmpeg_status.config(text="❌ Error", foreground="#DC143C")
        
        # pywin32 проверяется только на Windows
        if sys.platform == 'win32' and self.pywin32_status is not None:
            try:
                import pythoncom
                from win32com.shell import shell
                self.pywin32_status.config(text=self.t["pywin32_ok"], foreground="#228B22")
                self.log(self.t["pywin32_found"])
            except ImportError:
                self.pywin32_status.config(text=self.t["pywin32_no"], foreground="#FF8C00")
                self.log(self.t["pywin32_not_found"])
                self.log(self.t["pywin32_install_hint"])
        
        self.log("")
        self.log("-" * 50)
        self.log("")
    
    def _check_dependencies_thread(self):
        """Потокобезопасная проверка зависимостей."""
        self.root.after(0, lambda: self.log(self.t["checking_deps"]))
        self.root.after(0, lambda: self.log(""))
        
        # yt-dlp
        try:
            result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, 
                                    creationflags=SUBPROCESS_FLAGS, timeout=SUBPROCESS_TIMEOUT)
            version = result.stdout.strip()
            self.root.after(0, lambda: self.ytdlp_status.config(text=f"✅ {version}", foreground="#228B22"))
            self.root.after(0, lambda: self.log(f"{self.t['ytdlp_found']}{version}"))
        except FileNotFoundError:
            self.root.after(0, lambda: self.ytdlp_status.config(text=self.t["not_found"], foreground="#DC143C"))
            self.root.after(0, lambda: self.log(self.t["ytdlp_not_found"]))
            self.root.after(0, lambda: self.log(self.t["ytdlp_install_hint"]))
        except Exception as e:
            self.root.after(0, lambda: self.ytdlp_status.config(text=f"❌ Error: {e}", foreground="#DC143C"))
        
        # ffmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, 
                          creationflags=SUBPROCESS_FLAGS, timeout=SUBPROCESS_TIMEOUT)
            self.root.after(0, lambda: self.ffmpeg_status.config(text=self.t["installed"], foreground="#228B22"))
            self.root.after(0, lambda: self.log(self.t["ffmpeg_found"]))
        except FileNotFoundError:
            self.root.after(0, lambda: self.ffmpeg_status.config(text=self.t["not_found"], foreground="#DC143C"))
            self.root.after(0, lambda: self.log(self.t["ffmpeg_not_found"]))
            self.root.after(0, lambda: self.log(self.t["ffmpeg_install_hint"]))
        except Exception:
            self.root.after(0, lambda: self.ffmpeg_status.config(text="❌ Error", foreground="#DC143C"))
        
        # pywin32 (только Windows)
        if sys.platform == 'win32' and self.pywin32_status is not None:
            try:
                import pythoncom
                from win32com.shell import shell
                self.root.after(0, lambda: self.pywin32_status.config(text=self.t["pywin32_ok"], foreground="#228B22"))
                self.root.after(0, lambda: self.log(self.t["pywin32_found"]))
            except ImportError:
                self.root.after(0, lambda: self.pywin32_status.config(text=self.t["pywin32_no"], foreground="#FF8C00"))
                self.root.after(0, lambda: self.log(self.t["pywin32_not_found"]))
                self.root.after(0, lambda: self.log(self.t["pywin32_install_hint"]))
        
        self.root.after(0, lambda: self.log(""))
        self.root.after(0, lambda: self.log("-" * 50))
        self.root.after(0, lambda: self.log(""))
    
    def update_ytdlp(self):
        self.log(self.t["updating_ytdlp"])
        self.log(self.t["updating_cmd"])
        self.log("")
        threading.Thread(target=self._update_ytdlp_thread, daemon=True).start()
    
    def _update_ytdlp_thread(self):
        try:
            process = subprocess.Popen(["yt-dlp", "-U", "--update-to", "master"],
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                       text=True, creationflags=SUBPROCESS_FLAGS)
            for line in process.stdout:
                self.root.after(0, self.log, "   " + line.strip())
            process.wait()
            self.root.after(0, self.log, "")
            self.root.after(0, self.log, self.t["update_done"])
            self.root.after(0, self.log, "")
            self.root.after(100, self.check_dependencies)
        except Exception as e:
            self.root.after(0, self.log, f"{self.t['update_error']}{e}")
    
    def normalize_url(self, url, mode):
        """Нормализация URL с исправленной проверкой суффиксов."""
        url = url.strip().rstrip('/')
        if not url:
            return ""
        
        if mode == self.MODE_CHANNEL:
            known_suffixes = ['/videos', '/shorts', '/streams', '/playlists', 
                            '/community', '/about', '/featured', '/channels']
            
            url_lower = url.lower()
            has_suffix = any(url_lower.endswith(s) for s in known_suffixes)
            has_special_path = '/watch?' in url or '/playlist?' in url
            
            if not has_suffix and not has_special_path:
                url += '/videos'
                self.log(self.t["url_videos_added"])
        
        return url
    
    def _is_valid_url_format(self, url):
        """Базовая проверка формата URL."""
        url = url.strip().lower()
        if not url:
            return False
        # Должен начинаться с http(s):// или содержать известный домен
        if url.startswith(('http://', 'https://')):
            return True
        if any(domain in url for domain in ['youtube.com', 'youtu.be', 'www.']):
            return True
        # Проверка на наличие точки и похожесть на домен
        if '.' in url and not url.startswith('.') and ' ' not in url:
            return True
        return False
    
    def validate_inputs(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror(self.t["error_input"], self.t["error_no_url"])
            return False
        
        # Базовая проверка формата URL
        if not self._is_valid_url_format(url):
            messagebox.showerror(self.t["error_input"], self.t["error_invalid_url"])
            return False
        
        if 'youtube.com' not in url.lower() and 'youtu.be' not in url.lower():
            if not messagebox.askyesno(self.t["warning"], self.t["warn_not_youtube"]):
                return False
        
        # Предупреждение при скачивании аудио со всего канала
        mode = self.current_mode.get()
        if mode == self.MODE_AUDIO and self.audio_source.get() == self.AUDIO_SOURCE_CHANNEL:
            if not messagebox.askyesno(self.t["warning"], self.t["warn_audio_channel"]):
                return False
        
        outdir = self.outdir_var.get().strip()
        if not outdir:
            messagebox.showerror(self.t["error_input"], self.t["error_no_outdir"])
            return False
        if not os.path.exists(outdir):
            try:
                os.makedirs(outdir, exist_ok=True)
                self.log(f"{self.t['folder_created']}{outdir}")
            except Exception as e:
                messagebox.showerror(self.t["error"], self.t["error_create_folder"].format(path=outdir, error=e))
                return False
        
        cookies = self.cookies_var.get().strip()
        if cookies and not os.path.exists(cookies):
            messagebox.showerror(self.t["error"], self.t["error_cookies_not_found"].format(path=cookies))
            return False
        
        return True
    
    def _get_output_template(self, outdir, mode):
        if mode == self.MODE_CHANNEL:
            return os.path.join(outdir, "%(uploader)s", "%(playlist_autonumber)05d. %(title)s [%(id)s].%(ext)s")
        elif mode == self.MODE_PLAYLIST:
            return os.path.join(outdir, "%(uploader)s", "%(playlist_title)s", "%(playlist_autonumber)05d. %(title)s [%(id)s].%(ext)s")
        elif mode == self.MODE_AUDIO:
            # Разные шаблоны для разных источников аудио
            source = self.audio_source.get()
            if source == self.AUDIO_SOURCE_CHANNEL:
                return os.path.join(outdir, "%(uploader)s", "%(playlist_autonumber)05d. %(title)s [%(id)s].%(ext)s")
            elif source == self.AUDIO_SOURCE_PLAYLIST:
                return os.path.join(outdir, "%(uploader)s", "%(playlist_title)s", "%(playlist_autonumber)05d. %(title)s [%(id)s].%(ext)s")
            else:
                return os.path.join(outdir, "%(title)s [%(id)s].%(ext)s")
        else:
            return os.path.join(outdir, "%(title)s [%(id)s].%(ext)s")
    
    def _get_mode_display_name(self, mode):
        return {
            self.MODE_CHANNEL: self.t["mode_channel"],
            self.MODE_PLAYLIST: self.t["mode_playlist"],
            self.MODE_VIDEO: self.t["mode_video"],
            self.MODE_AUDIO: self.t["mode_audio"],
        }.get(mode, mode)
    
    def _get_folder_structure_desc(self, mode):
        if mode == self.MODE_AUDIO:
            # Разные описания для разных источников аудио
            source = self.audio_source.get()
            fmt = self.audio_format.get()
            if source == self.AUDIO_SOURCE_CHANNEL:
                return self.t["folder_struct_audio_channel"].format(format=fmt)
            elif source == self.AUDIO_SOURCE_PLAYLIST:
                return self.t["folder_struct_audio_playlist"].format(format=fmt)
            else:
                return self.t["folder_struct_audio_video"].format(format=fmt)
        
        return {
            self.MODE_CHANNEL: self.t["folder_struct_channel"],
            self.MODE_PLAYLIST: self.t["folder_struct_playlist"],
            self.MODE_VIDEO: self.t["folder_struct_video"],
        }.get(mode, "")
    
    def _get_video_format_string(self, quality):
        if quality == "max":
            return "bv*+ba/b"
        
        height = None
        for q_val, _, q_height in VIDEO_QUALITIES:
            if q_val == quality:
                height = q_height
                break
        
        if height:
            return f"bv*[height<={height}]+ba/b[height<={height}]/b"
        
        return "bv*+ba/b"
    
    def _get_quality_display_name(self, quality):
        for q_val, q_key, _ in VIDEO_QUALITIES:
            if q_val == quality:
                return self.t[q_key]
        return quality
    
    def _get_bitrate_display_name(self, bitrate):
        for b_val, b_key, _ in AUDIO_BITRATES:
            if b_val == bitrate:
                return self.t[b_key]
        return bitrate
    
    def _build_command(self, mode, url, cookies, output_template, archive_path, max_downloads=None):
        cmd = [
            "yt-dlp", "-o", output_template,
            "--continue", "--no-overwrites", "--no-post-overwrites",
            "--retries", "infinite", "--fragment-retries", "infinite",
            "--extractor-retries", "infinite", "--file-access-retries", "infinite",
            "--retry-sleep", "5", "--progress", "--newline",
        ]
        
        # Cookies опциональны
        if cookies:
            cmd.extend(["--cookies", cookies])
        
        if mode == self.MODE_AUDIO:
            audio_fmt = self.audio_format.get()
            bitrate = self.audio_bitrate.get()
            source = self.audio_source.get()
            
            cmd.extend(["-f", "bestaudio/best", "-x"])
            
            if audio_fmt == "wav":
                cmd.extend(["--audio-format", "wav"])
            elif audio_fmt == "mp3":
                cmd.extend(["--audio-format", "mp3"])
                # Установка битрейта для MP3
                if bitrate != "max":
                    # Используем только -b:a для конкретного битрейта (CBR)
                    cmd.extend(["--postprocessor-args", f"ffmpeg:-b:a {bitrate}k"])
                else:
                    # Максимальное качество VBR
                    cmd.extend(["--audio-quality", "0"])
            elif audio_fmt == "ogg":
                # OGG Vorbis формат
                cmd.extend(["--audio-format", "vorbis"])
                # Установка битрейта для OGG
                if bitrate != "max":
                    cmd.extend(["--postprocessor-args", f"ffmpeg:-b:a {bitrate}k"])
                else:
                    cmd.extend(["--audio-quality", "0"])
            
            # Настройки в зависимости от источника
            if source == self.AUDIO_SOURCE_VIDEO:
                cmd.append("--no-playlist")
            elif source in (self.AUDIO_SOURCE_PLAYLIST, self.AUDIO_SOURCE_CHANNEL):
                cmd.extend(["--playlist-reverse"])
                if archive_path:
                    cmd.extend(["--download-archive", archive_path])
            
        elif mode == self.MODE_VIDEO:
            quality = self.video_quality.get()
            format_string = self._get_video_format_string(quality)
            cmd.extend(["-f", format_string, "--no-playlist"])
        else:
            quality = self.video_quality.get()
            format_string = self._get_video_format_string(quality)
            cmd.extend(["-f", format_string, "--playlist-reverse", "--download-archive", archive_path])
        
        if max_downloads:
            cmd.extend(["--max-downloads", str(max_downloads)])
        
        cmd.append(url)
        return cmd
    
    def start_download(self):
        # Защита от двойного нажатия
        if str(self.start_btn.cget('state')) == 'disabled':
            return
        
        if not self.validate_inputs():
            return
        
        # Сохраняем настройки перед началом загрузки
        self._save_settings()
        
        self._reset_progress()
        self.stop_event.clear()
        
        mode = self.current_mode.get()
        audio_source = self.audio_source.get() if mode == self.MODE_AUDIO else None
        
        # Определяем, нужен ли archive для этого режима
        uses_archive = mode in (self.MODE_CHANNEL, self.MODE_PLAYLIST) or \
                       (mode == self.MODE_AUDIO and audio_source in (self.AUDIO_SOURCE_PLAYLIST, self.AUDIO_SOURCE_CHANNEL))
        
        # Нормализация URL (для каналов добавляем /videos)
        url = self.url_var.get().strip()
        if mode == self.MODE_CHANNEL or (mode == self.MODE_AUDIO and audio_source == self.AUDIO_SOURCE_CHANNEL):
            url = self.normalize_url(url, self.MODE_CHANNEL)
        else:
            url = url.strip().rstrip('/')
        
        outdir = self.outdir_var.get().strip()
        cookies = self.cookies_var.get().strip()
        archive_path = os.path.join(outdir, "archive.txt") if uses_archive else None
        output_template = self._get_output_template(outdir, mode)
        restart_enabled = self.restart_each_video.get()
        
        # Сводка
        self.log("")
        self.log("=" * 70)
        self.log(f"{self.t['settings_summary']}".center(70))
        self.log("=" * 70)
        
        mode_name = self._get_mode_display_name(mode)
        if mode == self.MODE_AUDIO:
            # Добавляем источник к названию режима
            source_names = {
                self.AUDIO_SOURCE_VIDEO: self.t["audio_source_video"],
                self.AUDIO_SOURCE_PLAYLIST: self.t["audio_source_playlist"],
                self.AUDIO_SOURCE_CHANNEL: self.t["audio_source_channel"],
            }
            mode_name = f"{mode_name} ({source_names.get(audio_source, '')})"
        
        url_display = url[:45] + '...' if len(url) > 45 else url
        outdir_display = outdir[:45] + '...' if len(outdir) > 45 else outdir
        cookies_display = os.path.basename(cookies) if cookies else "—"
        
        self.log(f"{self.t['setting_mode']}{mode_name}")
        self.log(f"{self.t['setting_url']}{url_display}")
        self.log(f"{self.t['setting_folder']}{outdir_display}")
        self.log(f"{self.t['setting_cookies']}{cookies_display}")
        
        if uses_archive:
            self.log(self.t['setting_archive'])
        else:
            self.log(self.t['setting_no_archive'])
        
        self.log("-" * 70)
        self.log(f"{self.t['folder_structure']}{self._get_folder_structure_desc(mode)}")
        
        if mode == self.MODE_AUDIO:
            audio_fmt = self.audio_format.get().upper()
            bitrate = self._get_bitrate_display_name(self.audio_bitrate.get())
            if self.audio_format.get() == "wav":
                self.log(f"{self.t['setting_audio_format']}{audio_fmt}{self.t['audio_no_compression']}")
            else:
                self.log(f"{self.t['setting_audio_format']}{audio_fmt}")
                self.log(f"{self.t['setting_bitrate']}{bitrate}")
        else:
            quality = self._get_quality_display_name(self.video_quality.get())
            format_str = self._get_video_format_string(self.video_quality.get())
            self.log(f"{self.t['setting_quality']}{quality}")
            self.log(f"{self.t['setting_format']}{format_str}")
        
        if uses_archive:
            self.log(self.t['setting_order'])
        else:
            self.log(self.t['setting_order_single'])
        
        self.log(self.t['setting_retries'])
        
        if uses_archive:
            if restart_enabled:
                self.log(self.t['setting_restart'])
            else:
                self.log(self.t['setting_no_restart'])
        
        self.log("=" * 70)
        self.log("")
        self.log(self.t["starting_download"])
        self.log("")
        
        # Счётчик прогресса: 1 только для одиночных файлов
        is_single_file = mode == self.MODE_VIDEO or (mode == self.MODE_AUDIO and audio_source == self.AUDIO_SOURCE_VIDEO)
        if is_single_file:
            self.total_videos = 1
            self._update_progress_display()
        
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.update_btn.config(state="disabled")
        
        params = {
            'mode': mode, 'url': url, 'cookies': cookies,
            'output_template': output_template, 'archive_path': archive_path,
            'restart_enabled': restart_enabled and uses_archive,
        }
        
        threading.Thread(target=self._download_thread, args=(params,), daemon=True).start()
    
    def _download_thread(self, params):
        mode = params['mode']
        url = params['url']
        cookies = params['cookies']
        output_template = params['output_template']
        archive_path = params['archive_path']
        restart_enabled = params['restart_enabled']
        
        try:
            if restart_enabled:
                self._download_with_restart(mode, url, cookies, output_template, archive_path)
            else:
                cmd = self._build_command(mode, url, cookies, output_template, archive_path)
                self._run_single_process(cmd)
        except Exception as e:
            self.root.after(0, self.log, f"{self.t['download_error']}{e}")
        finally:
            self.root.after(0, self._download_finished)
    
    def _run_single_process(self, cmd):
        with self.process_lock:
            if self.stop_event.is_set():
                return
            
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, encoding='utf-8', errors='replace',
                creationflags=SUBPROCESS_FLAGS
            )
        
        try:
            for line in self.process.stdout:
                if self.stop_event.is_set():
                    break
                line = line.rstrip()
                if line:
                    self._parse_progress_from_line(line)
                    self.root.after(0, self.log, line)
        finally:
            try:
                if self.process.stdout:
                    self.process.stdout.close()
            except Exception:
                pass
        
        self.process.wait()
        exit_code = self.process.returncode
        
        self.root.after(0, self.log, "")
        if exit_code == 0:
            self.root.after(0, self.log, "=" * 70)
            self.root.after(0, self.log, f"{self.t['download_success']}".center(70))
            self.root.after(0, self.log, "=" * 70)
            if self.total_videos > 0:
                self.downloaded_videos = self.total_videos
                self.root.after(0, self._update_progress_display)
        elif not self.stop_event.is_set():
            self.root.after(0, self.log, f"{self.t['download_exit_code']}{exit_code}")
            self.root.after(0, self.log, self.t["download_exit_hint"])
    
    def _download_with_restart(self, mode, url, cookies, output_template, archive_path):
        videos_downloaded_this_session = 0
        consecutive_empty_runs = 0
        
        while not self.stop_event.is_set():
            cmd = self._build_command(mode, url, cookies, output_template, archive_path, max_downloads=1)
            
            with self.process_lock:
                if self.stop_event.is_set():
                    break
                
                self.process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1, encoding='utf-8', errors='replace',
                    creationflags=SUBPROCESS_FLAGS
                )
            
            downloaded_in_this_run = False
            archive_skips_in_this_run = 0
            
            try:
                for line in self.process.stdout:
                    if self.stop_event.is_set():
                        break
                    line = line.rstrip()
                    if line:
                        self._parse_progress_from_line(line)
                        self.root.after(0, self.log, line)
                        # Только РЕАЛЬНЫЕ скачивания считаем для restart
                        if self._is_download_complete_line(line):
                            downloaded_in_this_run = True
                        # Считаем архивные пропуски отдельно
                        elif self._is_archive_skip_line(line):
                            archive_skips_in_this_run += 1
            finally:
                try:
                    if self.process.stdout:
                        self.process.stdout.close()
                except Exception:
                    pass
            
            self.process.wait()
            exit_code = self.process.returncode
            
            if self.stop_event.is_set():
                break
            
            if downloaded_in_this_run:
                videos_downloaded_this_session += 1
                consecutive_empty_runs = 0
                self.root.after(0, self.log, "")
                self.root.after(0, self.log, self.t["restarting_process"].format(count=videos_downloaded_this_session))
                self.root.after(0, self.log, "")
            else:
                # Если были только архивные пропуски или вообще ничего — это пустой запуск
                consecutive_empty_runs += 1
                
                # Выходим если: успешный код ИЛИ много пустых запусков ИЛИ много архивных пропусков подряд
                should_stop = (
                    exit_code == 0 or 
                    consecutive_empty_runs >= MAX_CONSECUTIVE_EMPTY_RUNS or
                    archive_skips_in_this_run > 0  # Все видео уже в архиве
                )
                
                if should_stop:
                    self.root.after(0, self.log, "")
                    self.root.after(0, self.log, "=" * 70)
                    self.root.after(0, self.log, f"{self.t['all_videos_downloaded']}".center(70))
                    self.root.after(0, self.log, "=" * 70)
                    if self.total_videos > 0:
                        self.downloaded_videos = self.total_videos
                        self.root.after(0, self._update_progress_display)
                    break
    
    def _download_finished(self):
        with self.process_lock:
            self.process = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_btn.config(state="normal")
    
    def stop_download(self):
        with self.process_lock:
            if self.process and not self.stop_event.is_set():
                self.log("")
                self.log(self.t["stopping_download"])
                self.log(self.t["stop_hint"])
                
                self.stop_event.set()
                
                try:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=PROCESS_TERMINATE_TIMEOUT)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait(timeout=PROCESS_KILL_TIMEOUT)
                except Exception:
                    pass


# ══════════════════════════════════════════════════════════════════════════════
#  ТОЧКА ВХОДА
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # DPI awareness для Windows
    if sys.platform == 'win32':
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                from ctypes import windll
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    
    # Всегда показываем выбор языка при запуске
    lang_selector = LanguageSelector()
    selected_lang = lang_selector.run()
    
    if selected_lang is None:
        sys.exit(0)
    
    # Загружаем настройки
    settings_manager = SettingsManager()
    
    root = tk.Tk()
    
    # Центрируем окно
    width, height = 1000, 900
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    YouTubeDownloader(root, lang=selected_lang, settings_manager=settings_manager)
    root.mainloop()


if __name__ == "__main__":
    main()
