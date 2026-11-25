"""Read, apply, restore, or undo the Windows cursor color workaround."""

import argparse
import ctypes
from ctypes import wintypes
import json
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "apply", "restore", "undo"), nargs="?", default="status")
    action = parser.parse_args().action
    if sys.platform != "win32":
        parser.exit(1, "This helper requires Windows.\n")

    import winreg

    spi = ctypes.WinDLL("user32", use_last_error=True).SystemParametersInfoW
    spi.argtypes = (wintypes.UINT, wintypes.UINT, wintypes.LPVOID, wintypes.UINT)
    spi.restype = wintypes.BOOL

    def read_live():
        value = ctypes.c_int()
        if not spi(0x005E, 0, ctypes.byref(value), 0):
            raise ctypes.WinError(ctypes.get_last_error())
        return value.value

    def read_saved():
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse") as key:
            try:
                return winreg.QueryValueEx(key, "MouseTrails")
            except FileNotFoundError:
                return None, None

    def set_live(value):
        if not spi(0x005D, value & 0xFFFFFFFF, None, 2):
            raise ctypes.WinError(ctypes.get_last_error())

    def verify(expected_saved, expected_live):
        if read_saved() != expected_saved or read_live() != expected_live:
            raise OSError("Saved or live MouseTrails did not match the expected value.")

    def change_saved_and_live(saved, before, target):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", 0, winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE) as key:
            if winreg.QueryValueEx(key, "MouseTrails") != saved:
                raise OSError("The saved value changed before application.")
            winreg.SetValueEx(key, "MouseTrails", 0, winreg.REG_SZ, str(target))
            try:
                set_live(target)
                verify((str(target), winreg.REG_SZ), target)
            except OSError as error:
                try:
                    winreg.SetValueEx(key, "MouseTrails", 0, saved[1], saved[0])
                    set_live(before)
                    verify(saved, before)
                except OSError as rollback_error:
                    raise OSError(f"{error} Rollback failed: {rollback_error}") from rollback_error
                raise

    try:
        saved = read_saved()
        before = read_live()
        if action == "status":
            print(json.dumps({"saved": saved[0], "registry_type": saved[1], "live": before}))
            return
        expected_saved = "0" if action == "apply" else "-1"
        if saved != (expected_saved, winreg.REG_SZ):
            parser.exit(2, f"{action} requires saved MouseTrails {expected_saved!r}. Found {saved!r}.\n")
        if action == "apply" and before != 0:
            parser.exit(2, f"Apply requires live MouseTrails 0. Found {before}.\n")

        target = 0 if action == "undo" else -1
        if action == "restore":
            if before != target:
                set_live(target)
            verify(saved, target)
        else:
            change_saved_and_live(saved, before, target)
        print(json.dumps({
            "saved_before": saved[0], "saved_after": read_saved()[0],
            "live_before": before, "live_after": read_live(),
        }))
    except OSError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
