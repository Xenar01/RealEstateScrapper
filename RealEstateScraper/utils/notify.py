import sys

try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except Exception:  # non-Windows or missing package
    toaster = None


def notify(title: str, message: str) -> None:
    if toaster:
        try:
            toaster.show_toast(title, message, threaded=True, duration=5)
        except Exception:
            pass
    else:
        print(f"{title}: {message}")
