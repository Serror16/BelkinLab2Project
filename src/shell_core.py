import os
from logging_procces import setup_logging, check_history, add_log, save_history, add_to_history

class System_Shell:
    """Основной класс shell. Управляет логированием и историей."""

    def __init__(self):
        """Инициализирует текущую директорию, историю команд, настраивает логирование,
        создает корзину и загружает историю."""
        self.current_dir = os.getcwd()
        self.history = []
        self.history_file = ".history"
        self.trash_dir = ".trash"
        self.logger = setup_logging()

        if not os.path.exists(self.trash_dir):
            os.makedirs(self.trash_dir)

        check_history(self.history_file, self.history)

   
    def log(self, command, status=True, error_msg=""):
        add_log(self.logger, command, status, error_msg)

    def history_add(self, command, args, status=True, other_data=None):
        add_to_history(self.history, self.history_file, command, args, status, other_data)

    def history_save(self):
        save_history(self.history_file, self.history)