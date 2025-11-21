from shell_core import System_Shell
from parser import ShellParser

if __name__ == "__main__":
    shell_core = System_Shell()

    shell_parser = ShellParser(shell_core)

    shell_parser.run()