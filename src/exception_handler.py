# exception_handler.py

from ansi import Colors
from functools import wraps

def handle_os_errors(command_name):
    """
    Декоратор для автоматической обработки стандартных ошибок системы (OSError,
    FileNotFoundError и т.д.) для функций класса ShellCommands.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            core = self.core
            
            try:
                return func(self, *args, **kwargs)

            except (OSError, IsADirectoryError, FileNotFoundError, PermissionError) as e:
                error_msg = f"{command_name}: {str(e)}"
                print(f"{Colors.RED}{error_msg}{Colors.RESET}")
                
                command_args = [a for a in args if a is not None]
                full_command = f"{command_name} {' '.join(map(str, command_args))}"
                
                core.log(full_command, False, error_msg)
                core.history_add(command_name, list(args), False)
                
            except Exception as e:
                error_msg = f"{command_name}: Unexpected error: {type(e).__name__}: {str(e)}"
                print(f"{Colors.RED}{error_msg}{Colors.RESET}")
                
                core.log(command_name, False, error_msg)
                core.history_add(command_name, list(args), False)
                
        return wrapper
    return decorator