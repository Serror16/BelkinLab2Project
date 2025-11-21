from ansi import Colors
from operations import ShellCommands

class ShellParser:
    def __init__(self, core):
        self.core = core
        self.commands = ShellCommands(core)

    def run(self):
        """Запускает основной цикл выполнения программы и обрабатывает ввод."""
        print("System_Shell start. Type 'exit' to quit.")
        while True:
            try:
                command = (
                    input(f"{Colors.BRIGHT_GREEN}{self.core.current_dir}{Colors.RESET} $ ")
                    .strip()
                    .split()
                )
                if not command:
                    continue

                cmd = command[0]
                args = command[1:]

                if cmd == "exit":
                    break
                elif cmd == "ls":
                    not_flag_args = [arg for arg in args if arg != "-l"]
                    flag_l = "-l" in args
                    path = not_flag_args[0] if not_flag_args else None
                    self.commands.ls(path, flag_l)
                elif cmd == "cd":
                    if len(args) != 1:
                        print("cd: not enough arguments")
                    else:
                        self.commands.cd(args[0])
                elif cmd == "cat":
                    if len(args) != 1:
                        print("cat: not enough arguments")
                    else:
                        self.commands.cat(args[0])
                elif cmd == "cp":
                    flag_r = "-r" in args
                    files = [arg for arg in args if arg != "-r"]
                    if len(files) != 2:
                        print("cp: not enough arguments (expected 2 files/dirs)")
                    else:
                        self.commands.cp(files[0], files[1], flag_r)
                elif cmd == "mv":
                    if len(args) != 2:
                        print("mv: not enough arguments (expected 2 files/dirs)")
                    else:
                        self.commands.mv(args[0], args[1])
                elif cmd == "rm":
                    not_flag_args = [arg for arg in args if arg != "-r"]
                    flag_r = "-r" in args
                    path = not_flag_args[0] if not_flag_args else None
                    if not path:
                        print("rm: not enough arguments")
                    else:
                        self.commands.rm(path, flag_r)
                elif cmd == "history":
                    count = int(args[0]) if args and args[0].isdigit() else 5
                    self.commands.show_history(count)
                elif cmd == "undo":
                    self.commands.undo()
                else:
                    print(f"Unknown command: {cmd}")

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")