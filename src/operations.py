import os
import shutil
from datetime import datetime
from ansi import Colors


class ShellCommands:
    def __init__(self, core):
        self.core = core

    def ls(self, path=None, flag_l=False):
        try:
            work_dir = path if path else self.core.current_dir

            elems = os.listdir(work_dir)
            if not flag_l:
                print("\n".join(elems))
            else:
                for elem in elems:
                    full_path = os.path.join(work_dir, elem)
                    stat = os.stat(full_path)
                    print(
                        f"{elem} \t{stat.st_size}\t{datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\t{oct(stat.st_mode)[-3:]}"
                    )

            self.core.log(f"ls {'-l ' if flag_l else ''}{path if path else ''}")
            self.core.history_add("ls", [path] if path else [])

        except OSError as e:
            error_msg = f"ls: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.core.log(
                f"ls {'-l ' if flag_l else ''}{path if path else ''}", False, error_msg
            )
            self.core.history_add("ls", [path] if path else [], False)


    def cd(self, path):
        try:
            if path == "..":
                new_dir = os.path.dirname(self.core.current_dir)
            elif path == "~":
                new_dir = os.path.expanduser("~")
            else:
                new_dir = os.path.abspath(os.path.join(self.core.current_dir, path))

            if not os.path.exists(new_dir):
                raise FileNotFoundError(f"Directory '{new_dir}' doesn't exist")

            os.chdir(new_dir)
            self.core.current_dir = new_dir
            self.core.log(f"cd {path}")
            self.core.history_add("cd", [path])

        except OSError as e:
            error_msg = f"cd: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.core.log(f"cd {path}", False, error_msg)
            self.core.history_add("cd", [path], False)


    def cat(self, path):
        try:
            full_path = os.path.join(self.core.current_dir, path)

            if os.path.isdir(full_path):
                raise IsADirectoryError(f"{path} is a directory")

            with open(full_path, "r", encoding="utf-8") as f:
                print(f"{Colors.BLUE}{f.read()}{Colors.RESET}")

            self.core.log(f"cat {path}")
            self.core.history_add("cat", [path])

        except OSError as e:
            error_msg = f"cat: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.core.log(f"cat {path}", False, error_msg)
            self.core.history_add("cat", [path], False)

    def cp(self, src, dst, flag_r=False):
        try:
            src_path = os.path.join(self.core.current_dir, src)
            dst_path = os.path.join(self.core.current_dir, dst)

            if not os.path.exists(src_path):
                raise FileNotFoundError(f"File '{src}' doesn't exist")

            if os.path.isdir(dst_path):
                dst_path = os.path.join(dst_path, os.path.basename(src_path))

            if os.path.isdir(src_path) and not flag_r:
                raise IsADirectoryError(f"'{src}' is a directory")

            if flag_r and os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

            self.core.log(f"cp {'-r ' if flag_r else ''}{src} {dst}")
            self.core.history_add(
                "cp",
                [src, dst, "-r"] if flag_r else [src, dst],
                other_data={"src_path": src_path, "dst_path": dst_path},
            )

        except OSError as e:
            error_msg = f"cp: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.core.log(f"cp {'-r ' if flag_r else ''}{src} {dst}", False, error_msg)
            self.core.history_add("cp", ["-r", src, dst] if flag_r else [src, dst], False)

    def mv(self, src, dst):
        try:
            src_path = os.path.join(self.core.current_dir, src)
            dst_path = os.path.join(self.core.current_dir, dst)

            if not os.path.exists(src_path):
                raise FileNotFoundError(f"File '{src}' doesn't exist")

            if os.path.isdir(dst_path):
                dst_path = os.path.join(dst_path, os.path.basename(src_path))

            shutil.move(src_path, dst_path)
            self.core.log(f"mv {src} {dst}")
            self.core.history_add(
                "mv",
                [src, dst],
                other_data={"src_path": src_path, "dst_path": dst_path},
            )

        except OSError as e:
            error_msg = f"mv: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.core.log(f"mv {src} {dst}", False, error_msg)
            self.core.history_add("mv", [src, dst], False)

    def rm(self, file, flag_r=False):
        try:
            path = os.path.join(self.core.current_dir, file)

            if not os.path.exists(path):
                raise FileNotFoundError(f"File '{file}' doesn't exist")

            if file in ["/", ".."] or os.path.abspath(path) == os.path.abspath("/"):
                raise PermissionError("Can't delete root directory")

            if not os.path.exists(self.core.trash_dir):
                os.makedirs(self.core.trash_dir)

            time = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.basename(path)
            trash_path = os.path.join(self.core.trash_dir, f"{base_name}_{time}")

            rel_path = os.path.relpath(path, self.core.current_dir)
            if os.path.dirname(rel_path) and os.path.dirname(rel_path) != ".":
                trash_subdir = os.path.join(self.core.trash_dir, os.path.dirname(rel_path))
                if not os.path.exists(trash_subdir):
                    os.makedirs(trash_subdir, exist_ok=True)
                trash_path = os.path.join(trash_subdir, f"{base_name}_{time}")

            if flag_r and os.path.isdir(path):
                confirm = input(f"Remove directory '{file}' recursively? (y/n): ")
                if confirm.lower() == "y":
                    shutil.move(path, trash_path)
                else:
                    print("Operation cancelled")
                    return
            else:
                if os.path.isdir(path):
                    raise IsADirectoryError(f"'{file}' is a directory")

                try:
                    shutil.copy2(path, trash_path)
                    os.remove(path)
                except Exception:
                    shutil.move(path, trash_path)

            self.core.log(f"rm {'-r ' if flag_r else ''}{file}")
            self.core.history_add(
                "rm",
                [file, "-r"] if flag_r else [file],
                other_data={"path": path, "trash_path": trash_path},
            )

        except OSError as e:
            error_msg = f"rm: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.core.log(f"rm {'-r ' if flag_r else ''}{file}", False, error_msg)
            self.core.history_add("rm", [file, "-r"] if flag_r else [file], False)


    def show_history(self, count=5):
        try:
            history = self.core.history
            if not history:
                print(f"{Colors.YELLOW}No command in history{Colors.RESET}")
                return

            start_idx = max(0, len(history) - count)

            i = start_idx + 1
            for info in history[start_idx:]:
                status = "SUCCESS" if info.get("status", True) else "ERROR"
                time = datetime.fromisoformat(info["time"]).strftime("%H:%M:%S")
                str_args = " ".join([str(arg) for arg in info["args"]])
                print(f"{i} {status} [{time}] {info['command']} {str_args}")
                i += 1

            self.core.log(f"history {count}")
            self.core.history_add("history", [str(count)])
        except Exception as e:
            error_msg = f"history: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.core.log(f"history {count}", False, error_msg)
            self.core.history_add("history", [str(count)], False)

    def undo(self):
        try:
            history = self.core.history
            if not history:
                print(f"{Colors.YELLOW}No commands to cancel{Colors.RESET}")
                return

            last_command = None
            for info in reversed(history):
                if info["command"] in ["cp", "mv", "rm"] and info.get("status", True):
                    last_command = info
                    break

            if not last_command:
                print(f"{Colors.YELLOW}No cancellable successful commands found{Colors.RESET}")
                return

            command = last_command["command"]
            other_data = last_command.get("other_data", {})
            success = True

            if command == "cp":
                dst_path = other_data.get("dst_path")
                if dst_path and os.path.exists(dst_path):
                    if os.path.isfile(dst_path):
                        os.remove(dst_path)
                    elif os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                else:
                    success = False

            elif command == "mv":
                src_path = other_data.get("src_path")
                dst_path = other_data.get("dst_path")
                if dst_path and os.path.exists(dst_path) and src_path:
                    shutil.move(dst_path, src_path)
                else:
                    success = False

            elif command == "rm":
                trash_path = other_data.get("trash_path")
                path = other_data.get("path")
                if os.path.exists(trash_path) and not os.path.exists(path):
                    shutil.move(trash_path, path)
                else:
                    success = False

            if success:
                history.remove(last_command)
                self.core.history_save()
                self.core.log("undo")
                self.core.history_add("undo", [])
            else:
                print(f"{Colors.RED}Couldn't cancel operation for command '{command}'.{Colors.RESET}")
                self.core.log("undo", False, f"Failed to cancel {command}")
                self.core.history_add("undo", [], False)

        except OSError as e:
            error_msg = f"undo: {str(e)}"
            print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            self.core.log("undo", False, error_msg)
            self.core.history_add("undo", [], False)