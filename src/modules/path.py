#!/usr/bin/python3
"""
Fixes Hardcoded tray icons in Linux.

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Contributors : Andreas Angerer, Joshua Fogg
Version : 3.8
Website : https://github.com/bil-elmoussaoui/Hardcode-Tray
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of Hardcode-Tray.
Hardcode-Tray is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Hardcode-Tray is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Hardcode-Tray. If not, see <http://www.gnu.org/licenses/>.
"""
from os import listdir, path

from src.const import ARCH, USERHOME


def get_exact_folder(key, directory, condition):
    """
        Get subdirs and apply a condition on each until one is found.
    """
    dirs = directory.split(key)
    exact_directory = ""

    if path.isdir(dirs[0]):
        directories = listdir(dirs[0])
        for dir_ in directories:
            if condition(path.join(dirs[0], dir_, "")):
                exact_directory = dir_
                break

    if exact_directory:
        directory = directory.replace(key, exact_directory)

    return directory


def dropbox_callack(directory):
    """
    Correct the hardcoded dropbox directory.

    Args:
        directory(str): the default dropbox directory
    """
    if path.isdir(directory):
        sub_dir = directory.split("-")
        return len(sub_dir) > 1 and sub_dir[0].lower() == "dropbox"
    return False


def hangouts_callback(directory):
    """
    Correct the hardcoded dropbox directory.

    Args:
        directory(str): the default dropbox directory
    """
    return path.isdir(directory)


class Path:
    """
        Path class:
        Check if paths do exists
    """

    DB_VARIABLES = {
        "{userhome}": USERHOME,
        "{size}": 22,
        "{arch}": ARCH,
        "{dropbox}": dropbox_callack,
        "{hangouts}": hangouts_callback
    }

    def __init__(self, absolute_path, parser, path_key):
        self._path = absolute_path
        self._parser = parser
        self.type = path_key
        self._exists = True
        self._validate()

    def __add__(self, filename):
        return self.path + filename

    def __radd__(self, filename):
        return filename + self.path

    @property
    def parser(self):
        """Return Parser instance."""
        return self._parser

    @property
    def path(self):
        """Return the path."""
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def exists(self):
        """Return wether the path exists or not."""
        return self._exists

    def _validate(self):
        """
            Check wether a folder path exists or not.
        """
        from src.app import App

        Path.DB_VARIABLES["{size}"] = App.icon_size()

        for key, value in Path.DB_VARIABLES.items():
            if hasattr(value, "__call__"):  # Check wether it's a function or not
                self.path = get_exact_folder(key, self.path, value)
            else:
                self.path = self.path.replace(key, str(value))

        if self.parser.is_script and self.type == "icons_path":
            binary_file = path.join(self.path, self.parser.binary)
            if not path.exists(self.path) or not path.exists(binary_file):
                self._exists = False
        else:
            if not path.exists(self.path):
                self._exists = False
