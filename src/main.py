from config import LOGGING_CONFIG
import os
import shutil
import logging
import logging.config
from datetime import datetime
from ansi import Colors
import json 

class System_Shell:
    '''Основной класс shell'''
    def __init__(self):
        '''Функция инициализатор. Инициализирует текущую директорию, историю команд, 
        настраивает логирование, создает корзину и загружает историю.'''
        self.current_dir = os.getcwd()
        self.history = []  
        self.history_file = ".history" 
        self.trash_dir = ".trash"  

        if not os.path.exists(self.trash_dir):
            os.makedirs(self.trash_dir)

        self.setup_logging()
        self.check_history()

    def setup_logging(self):
        '''Функция которая загружает конфигурацию для логирования из файла config.py'''  
        logging.config.dictConfig(LOGGING_CONFIG)
        self.logger = logging.getLogger('shell_logger')
        
    def add_log(self, command, status=True, error_msg=""):
        '''
            Функция которая добавляет записи в лог-файл shell.log.

            Принимает:
                1. command (str) - выполненная команда
                2. status (bool) - статус выполнения(успех / неудача)
                3. error_msg (str) - сообщение об ошибке

            Вывод: None
        '''
        status = "SUCCESS" if status else f"ERROR: {error_msg}"
        self.logger.info(f"{command} - {status}")


    def check_history(self):
        '''Функция которая загружает историю команд из файла .history.'''
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except OSError as e:
            print(f"{Colors.RED}File with history didn't find{Colors.RESET}")


    def save_history(self):
        '''Функция которая сохраняет последние 10 команд из списка в файл .history.'''
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history[-10:], f)
        except OSError as e:
            print(f"{Colors.YELLOW}Could't save command history{Colors.RESET}")


    def add_to_history(self, command, args, status=True, other_data=None):
        '''
            Функция которая добавляет команду и информацию о ней в список команд.
        
            Принимает:
                1. command (str) - Название команды
                2. args (list) - Список аргументов команды
                3. status (bool) - Статус выполнения команды
                4. other_data (dict) - Дополнительные данные о команде

            Вывод: None
        '''
        command_history_info = {
            'time': datetime.now().isoformat(),
            'command': command,
            'args': args,
            'status': status,
            'current_dir': self.current_dir,
            'other_data': other_data or {}
        }
        self.history.append(command_history_info)
        self.save_history()

    def ls(self, path=None, flag_l=False):
        '''
            Функция которая выводит список содержимого в директории.

            Принимает:
                1. path (str) - Путь к директории. Если None, используется текущая директория.
                2. flag_l (bool) - Флаг подробного вывода. 

            Вывод:
                При отсутствии флага -l выводит список файлов и директорий в указаной папке.
                Если есть флаг - l, то выводит подробный список файлов и директорий в указаной папке(размер, время последнего изменения, права доступа).
        '''
        try:
            if path:
                work_dir = path
            else:
                work_dir = self.current_dir

            elems = os.listdir(work_dir)
            if not flag_l:
                print("\n".join(elems))
            else:
                for elem in elems:
                    full_path = os.path.join(work_dir, elem)
                    stat = os.stat(full_path)
                    print(f"{elem} \t{stat.st_size}\t{datetime.fromtimestamp(stat.st_mtime)}\t{oct(stat.st_mode)[-3:]}")
            
            self.add_log(f"ls {'-l ' if flag_l else ''}{path if path else ''}")
            self.add_to_history('ls', [path] if path else [])

        except OSError as e:
            error_msg = f"ls: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.add_log(f"ls {'-l ' if flag_l else ''}{path if path else ''}", False, error_msg)
            self.add_to_history('ls', [path] if path else [], False)


    def cd(self, path):
        '''
            Функция которая осуществляет смену рабочей директории.

            Принимает:
                1. path (str) - Путь к новой директории

            Вывод: None
        '''
        try:
            if path == "..":
                new_dir = os.path.dirname(self.current_dir)
            elif path == "~":
                new_dir = os.path.expanduser("~")
            else:
                new_dir = os.path.abspath(os.path.join(self.current_dir, path))
            
            if not os.path.exists(new_dir):
                raise FileNotFoundError(f"Directory '{new_dir}' doesn't exist")
            
            os.chdir(new_dir)
            self.current_dir = new_dir
            self.add_log(f"cd {path}")
            self.add_to_history('cd', [path])

        except OSError as e:
            error_msg = f"cd: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.add_log(f"cd {path}", False, error_msg)
            self.add_to_history('cd', [path], False)

    def cat(self, path):
        '''
            Функция которая выводит содержимое указанного файла.

            Приниимает:
                1. path (str) - Путь к файлу
            
            Вывод:
                Выводит содержимое указанного файла. Если путь указан на директорию, то выводит ошибку.         
        '''
        try:
            full_path = os.path.join(self.current_dir, path)
            
            if os.path.isdir(full_path):
                raise IsADirectoryError(f"{path} is a directory")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                print(f"{Colors.BLUE}{f.read()}{Colors.RESET}")
            
            self.add_log(f"cat {path}")
            self.add_to_history('cat', [path])

        except OSError as e:
            error_msg = f"cat: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.add_log(f"cat {path}", False, error_msg)
            self.add_to_history('cat', [path], False)

    def cp(self, src, dst, flag_r=False):
        '''
            Функция которая копирует файлы или директории.

            Принимает:
                1. src (str) - Путь к исходному файлу или директории
                2. dst (str) -  Путь к целевому файлу или директории
                3. flag_r (bool) - Флаг рекурсивного копирования, работает только для директорий

            Вывод: None.
        '''
        try:
            src_path = os.path.join(self.current_dir, src)
            dst_path = os.path.join(self.current_dir, dst)

            if not os.path.exists(src_path):
                raise FileNotFoundError(f"File '{src}' doesn't exist")
            
            if os.path.isdir(dst_path):
                dst_path = os.path.join(dst_path, src_path.name)
            
            if os.path.exists(dst_path):
                if os.path.isfile(dst_path):
                    os.remove(dst_path)
                elif os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)

            if flag_r and os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            
            self.add_log(f"cp {'-r ' if flag_r else ''}{src} {dst}")
            self.add_to_history('cp', [src, dst, '-r'] if flag_r else [src, dst], other_data={'src_path': src_path, 'dst_path': dst_path})
        
        except OSError as e:
            error_msg = f"cp: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.add_log(f"cp {'-r ' if flag_r else ''}{src} {dst}", False, error_msg)
            self.add_to_history('cp', ['-r', src, dst] if flag_r else [src, dst], False)

    def mv(self, src, dst):
        '''
            Функция которая перемещяет или переименовывает файлы или директории.

            Принимает:
                1. src (str) - Путь к исходному файлу или директории
                2. dst (str) - Путь к целевому файлу или директории
            
                Вывод: None.
        '''
        try:
            src_path = os.path.join(self.current_dir, src)
            dst_path = os.path.join(self.current_dir, dst)

            if not os.path.exists(src_path):
                raise FileNotFoundError(f"File '{src}' doesn't exist")
            
            if os.path.isdir(dst_path):
                dst_path = os.path.join(dst_path, src_path.name)
            
            if os.path.exists(dst_path):
                if os.path.isfile(dst_path):
                    os.remove(dst_path)
                elif os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)
            
            shutil.move(src_path, dst_path)
            self.add_log(f"mv {src} {dst}")
            self.add_to_history('mv', [src, dst], other_data={'src_path': src_path, 'dst_path': dst_path})
        
        except OSError as e:
            error_msg = f"mv: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.add_log(f"mv {src} {dst}", False, error_msg)
            self.add_to_history('mv', [src, dst], False)

    def rm(self, file, flag_r=False):
        '''
            Функция которая удаляет указанный файл или директорию.

            Принимает:
                1. file (str) - Имя файла или директории для удаления
                2. flag_r (bool) - Флаг рекурсивного удаления директории. Работает только для директорий.

            Вывод: None.
        '''
        try:
            path = os.path.join(self.current_dir, file)

            if not os.path.exists(path):
                raise FileNotFoundError(f"File '{file}' doesn't exist")


            if file in ["/", ".."] or os.path.abspath(path) == os.path.abspath("/"):
                raise PermissionError("Can't delete root directory")

            if not os.path.exists(self.trash_dir):
                os.makedirs(self.trash_dir)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            trash_path = os.path.join(self.trash_dir, f"{file}_{timestamp}")

            if flag_r and os.path.isdir(path):
                confirm = input(f"Remove directory '{file}' recursivly? (y/n): ")
                if confirm.lower() == 'y':
                    shutil.move(path, trash_path)
                else:
                    print("Operation cancelled")
                    return
            else:
                shutil.move(path, trash_path)
            
            self.add_log(f"rm {'-r ' if flag_r else ''}{file}")
            self.add_to_history('rm', [file, '-r'] if flag_r else [file], other_data={'path': path, 'trash_path': trash_path})
        
        except OSError as e:
            error_msg = f"rm: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.add_log(f"rm {'-r ' if flag_r else ''}{file}", False, error_msg)
            self.add_to_history('rm', [file, '-r'] if flag_r else [file], False)

    def show_history(self, count=5):
        '''
            Функция которая выводит историю выполненных команд.

            Принимает:
                1. count (int) - Количество команд для показеа (по умолчанию 5)
            
            Вывод:
                Выводит команды в порядке от новой к старым(статус, время выполнения, аргументами).
        '''
        try:
            if not self.history:
                print(f"{Colors.YELLOW}No command in history{Colors.RESET}")
                return
            
            if len(self.history) > count:
                start_idx = len(self.history) - count
            else:
                start_idx = 0

            i = start_idx + 1
            for info in self.history[start_idx:]:
                if info.get('status', True):
                    status = "SUCCESS"
                else:
                    status = "ERROR"
                    
                timestamp = datetime.fromisoformat(info['time']).strftime('%H:%M:%S')
                args = []
                for arg in info['args']:
                    args.append(str(arg))
                str_args = ' '.join(args)
                    
                print(f"{i} {status} [{timestamp}] {info['command']} {str_args}")
                i += 1
                
            self.add_log(f"history {count}")
            self.add_to_history('history', [str(count)])
        except OSError as e:
            error_msg = f"history: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.add_log(f"history {count}", False, error_msg)
            self.add_to_history('history', [str(count)], False)

    def undo_last(self):
        '''
            Функция которая отменяет результат выполнения последней команды.(последней команды со статусом success).
            Поддерживает отмену команд: cp, rm, mv.
        '''
        try:
            if not self.history:
                print(f"{Colors.YELLOW}No commands to cancel{Colors.RESET}")
                return

            last_command = None
            for info in reversed(self.history):
                if info['command'] in ['cp', 'mv', 'rm'] and info.get('status', True):
                    last_command = info
                    break
            
            if not last_command:
                print(f"{Colors.YELLOW}No commands to cansel{Colors.RESET}")
                return
            
            command = last_command['command']
            args = last_command['args']
            other_data = last_command.get('other_data', {})
            
            
            if command == 'cp':
                dst_path = other_data.get('dst_path')
                if dst_path and os.path.exists(dst_path):
                    if os.path.isfile(dst_path):
                        os.remove(dst_path)
                    elif os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
            
            elif command == 'mv':
                src_path = other_data.get('src_path')
                dst_path = other_data.get('dst_path')
                if dst_path and os.path.exists(dst_path) and src_path:
                    if not os.path.exists(src_path):
                        shutil.move(dst_path, src_path)
            
            elif command == 'rm':
                trash_path = other_data.get('trash_path')
                path = other_data.get('path')
                if os.path.exists(trash_path) and not os.path.exists(path):
                    shutil.move(trash_path, path)
                else:
                    print(f"{Colors.RED}Couldn't cancel operation{Colors.RESET}")
            
            self.history.remove(last_command)
            self.save_history()
            self.add_log("undo")
            self.add_to_history('undo', [])
            
        except OSError as e:
            error_msg = f"undo: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.add_log("undo", False, error_msg)
            self.add_to_history('undo', [], False)


    def run(self):
        '''Функция которая запускает основной цикл выполнения программы.
            Также функция обрабатывает пользовательский ввод, парсит команды и в соответствии с результатами парсинга вызывает соответствующие функции.
        '''
        print("System_Shell started. Type 'exit' to quit.")
        while True:
            try:
                command = input(f"{Colors.BRIGHT_GREEN}{self.current_dir}{Colors.RESET} $ ").strip().split()
                if not command:
                    continue
                
                cmd = command[0]
                args = command[1:]

                if cmd == "exit":
                    break
                elif cmd == "ls":
                    not_flag_args = [arg for arg in args if arg != "-l"]
                    flag_l = "-l" in args
                    if not_flag_args:
                        path = not_flag_args[0]
                    else:
                        path = None
                    self.ls(path, flag_l)
                elif cmd == "cd":
                    if len(args) != 1:
                        print("cd: not enouth arguments")
                    else:
                        self.cd(args[0])
                elif cmd == "cat":
                    if len(args) != 1:
                        print("cat: not enouth arguments")
                    else:
                        self.cat(args[0])
                elif cmd == "cp":
                    flag_r = "-r" in args
                    files = [arg for arg in args if arg != "-r"]
                    if len(files) != 2:
                        print("cp: not enouth arguments")
                    else:
                        self.cp(files[0], files[1], flag_r)
                elif cmd == "mv":
                    if len(args) != 2:
                        print("mv: not enouth arguments")
                    else:
                        self.mv(args[0], args[1])
                elif cmd == "rm":
                    not_flag_args = [arg for arg in args if arg != "-r"]
                    flag_r = "-r" in args
                    if not_flag_args:
                        path = not_flag_args[0]
                    else:
                        path = None
                    if not path:
                        print("rm: not enouth arguments")
                    else:
                        self.rm(path, flag_r)
                elif cmd == "history":
                    if args and args[0].isdigit():
                        count = int(args[0])
                    else:
                        count = 5
                    self.show_history(count)
                elif cmd == "undo":
                    self.undo_last()
                else:
                    print(f"Unknown command: {cmd}")
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    shell = System_Shell()
    shell.run()