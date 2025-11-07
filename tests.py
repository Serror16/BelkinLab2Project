import unittest
from unittest.mock import mock_open
from unittest.mock import patch
import os
import shutil
import json


class ShellTests(unittest.TestCase):
    def test_ls(self):
        with patch("os.listdir") as mock_ls:
            files = ["file_1", "file_2", "file_3"]
            mock_ls.return_value = files

            state = os.listdir("/src/main")

            mock_ls.assert_called_once_with("/src/main")
            self.assertEqual(state, files)
            self.assertEqual(len(state), 3)

    def test_ls_PermissionError(self):
        with patch("os.listdir") as mock_ls:
            mock_ls.side_effect = PermissionError("Permission denied")

            with self.assertRaises(PermissionError):
                os.listdir("/scr/main")

    def test_ls_FileNotFoundError(self):
        with patch("os.listdir") as mock_ls:
            mock_ls.side_effect = FileNotFoundError("File didn't find")

            with self.assertRaises(FileNotFoundError):
                os.listdir("/scr/main")

    def test_cat(self):
        mock_op = mock_open(read_data="info")

        with patch("builtins.open", mock_op) as mock_cat:
            with open("tests.py", "r") as f:
                file = f.read()

            mock_cat.assert_called_once_with("tests.py", "r")
            self.assertEqual(file, "info")

    def test_cat_FileNotFoundError(self):
        with patch("builtins.open") as mock_cat:
            mock_cat.side_effect = FileNotFoundError("File didn't find")

            with self.assertRaises(FileNotFoundError):
                with open("tests.py", "r") as f:
                    f.read()

    def test_cat_PermissionError(self):
        with patch("builtins.open") as mock_cat:
            mock_cat.side_effect = PermissionError("Permission denied")

            with self.assertRaises(PermissionError):
                with open("/src/main", "r") as f:
                    f.read()

    def test_cat_IsADirectoryError(self):
        with patch("builtins.open") as mock_cat:
            mock_cat.side_effect = IsADirectoryError("Is a directory")

            with self.assertRaises(IsADirectoryError):
                with open("/src", "r") as f:
                    f.read()

    def test_rm(self):
        with patch("os.remove") as mock_rm:
            os.remove("tests.py")

            mock_rm.assert_called_once_with("tests.py")

    def test_rm_FileNotFoundError(self):
        with patch("os.remove") as mock_rm:
            mock_rm.side_effect = FileNotFoundError("File didn't find")

            with self.assertRaises(FileNotFoundError):
                os.remove("tests.py")

    def test_rm_PermissionError(self):
        with patch("os.remove") as mock_rm:
            mock_rm.side_effect = PermissionError("Permission denied")

            with self.assertRaises(PermissionError):
                os.remove("/src/main")

    def test_rm_IsADirectoryError(self):
        with patch("os.remove") as mock_rm:
            mock_rm.side_effect = IsADirectoryError("Is a directory")

            with self.assertRaises(IsADirectoryError):
                os.remove("/src")

    def test_mv(self):
        with patch("shutil.move") as mock_mv:
            shutil.move("file_1", "file_2")

            mock_mv.assert_called_once_with("file_1", "file_2")

    def test_mv_FileNotFoundError(self):
        with patch("shutil.move") as mock_mv:
            mock_mv.side_effect = FileNotFoundError("File didn't find")

            with self.assertRaises(FileNotFoundError):
                shutil.move("file_1", "file_2")

    def test_mv_PermissionError(self):
        with patch("shutil.move") as mock_mv:
            mock_mv.side_effect = PermissionError("Permission denied")

            with self.assertRaises(PermissionError):
                shutil.move("file_1", "file_2")

    def test_cd(self):
        with patch("os.chdir") as mock_cd:
            os.chdir("/src")

            mock_cd.assert_called_once_with("/src")

    def test_cd_FileNotFoundError(self):
        with patch("os.chdir") as mock_cd:
            mock_cd.side_effect = FileNotFoundError("File didn't find")

            with self.assertRaises(FileNotFoundError):
                os.chdir("/src")

    def test_cd_PermissionError(self):
        with patch("os.chdir") as mock_cd:
            mock_cd.side_effect = PermissionError("Permission denied")

            with self.assertRaises(PermissionError):
                os.chdir("/src")

    def test_cp_file(self):
        with patch("shutil.copy2") as mock_cp:
            shutil.copy2("file_1", "file_2")

            mock_cp.assert_called_once_with("file_1", "file_2")

    def test_cp_dir(self):
        with patch("shutil.copytree") as mock_cp:
            shutil.copytree("dir_1", "dir_2")

            mock_cp.assert_called_once_with("dir_1", "dir_2")

    def test_cp_FileNotFoundError(self):
        with patch("shutil.copy2") as mock_cp:
            mock_cp.side_effect = FileNotFoundError("File didn't find")

            with self.assertRaises(FileNotFoundError):
                shutil.copy2("file_1", "file_2")

    def test_cp_PermissionError(self):
        with patch("shutil.copy2") as mock_cp:
            mock_cp.side_effect = PermissionError("Permission denied")

            with self.assertRaises(PermissionError):
                shutil.copy2("file_1", "file_2")

    def test_hist_load(self):
        with patch("builtins.open", mock_open(read_data="[]")) as mock_hist:
            with patch("json.load") as mock_load:
                mock_load.return_value = [{"command": "ls", "args": []}]

                info = json.load(mock_hist())
                self.assertEqual(len(info), 1)
                self.assertEqual(info[0]["command"], "ls")

    def test_hist_save(self):
        with patch("builtins.open") as mock_hist:
            mock_hist.side_effect = PermissionError("Can't write in this file")

            with self.assertRaises(PermissionError):
                with open(".history", "w") as f:
                    json.dump([], f)

    def test_hist_FileNotFoundError(self):
        with patch("builtins.open") as mock_hist:
            mock_hist.side_effect = FileNotFoundError("History didn't find")

            with self.assertRaises(FileNotFoundError):
                with open(".history", "r") as f:
                    json.load(f)

if __name__ == "__main__":
    unittest.main()
