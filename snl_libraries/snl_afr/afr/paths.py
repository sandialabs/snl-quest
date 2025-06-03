import os
import sys

def get_path():
    """
    Determines the base path of the application.

    If the application is running in a frozen state (e.g., packaged with PyInstaller),
    it returns the directory containing the executable. Otherwise, it returns the
    directory containing the current script.

    :return: The base path of the application.
    :rtype: str
    """
    if getattr(sys, 'frozen', False):
        exe_path = os.path.dirname(sys.executable)
        base_path = os.path.join(exe_path, 'anaylsis_for_regulators')
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return base_path