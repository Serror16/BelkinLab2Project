import os
import logging
import logging.config
import json
from datetime import datetime
from config import LOGGING_CONFIG
from ansi import Colors


def setup_logging():
    """Загружает конфигурацию для логирования из файла config.py и возвращает логгер."""
    try:
        logging.config.dictConfig(LOGGING_CONFIG)
        return logging.getLogger("shell_logger")
    except Exception as e:
        print(f"{Colors.RED}Ошибка при настройке логирования: {e}{Colors.RESET}")
        return logging.getLogger("default") # Возвращаем дефолтный на случай ошибки

def add_log(logger, command, status=True, error_msg=""):
    """
    Добавляет записи в лог-файл shell.log.
    """
    status_str = "SUCCESS" if status else f"ERROR: {error_msg}"
    logger.info(f"{command} - {status_str}")


def check_history(history_file, history_list):
    """Загружает историю команд из файла."""
    try:
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                history_list.extend(json.load(f))
    except OSError:
        print(f"{Colors.RED}Файл истории не найден или ошибка чтения.{Colors.RESET}")


def save_history(history_file, history_list):
    """Сохраняет последние 10 команд из списка в файл."""
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history_list[-10:], f, ensure_ascii=False, indent=4)
    except OSError:
        print(f"{Colors.YELLOW}Не удалось сохранить историю команд.{Colors.RESET}")

def add_to_history(history_list, history_file, command, args, status=True, other_data=None):
    """
    Добавляет команду и информацию о ней в список и сохраняет историю.
    """
    command_history_info = {
        "time": datetime.now().isoformat(),
        "command": command,
        "args": args,
        "status": status,
        "other_data": other_data or {},
    }
    history_list.append(command_history_info)
    save_history(history_file, history_list)