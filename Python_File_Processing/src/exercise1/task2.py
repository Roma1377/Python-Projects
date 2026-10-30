import os
import threading
import urllib.request


def format_table(headers, rows, aligns):
    widths = []
    for i, h in enumerate(headers):
        w = len(h)
        for row in rows:
            w = max(w, len(str(row[i])))
        widths.append(w + 2)

    sep = "+" + "+".join("-" * w for w in widths) + "+"

    def row_line(cells):
        parts = []
        for i, c in enumerate(cells):
            text = str(c)
            inner = widths[i] - 2
            if len(text) > inner:
                text = text[:inner]
            a = aligns[i]
            if a == "left":
                parts.append(" " + text.ljust(inner) + " ")
            elif a == "right":
                parts.append(" " + text.rjust(inner) + " ")
            else:
                parts.append(" " + text.center(inner) + " ")
        return "|" + "|".join(parts) + "|"

    lines = [sep, row_line(headers), sep]
    for r in rows:
        lines.append(row_line(r))
    lines.append(sep)
    return "\n".join(lines)


def ask_path():
    """Спрашивает путь, пока не получит корректный и доступный для записи."""
    while True:
        path = input("Введите путь для сохранения: ").strip()
        path = os.path.expanduser(path)
        try:
            os.makedirs(path, exist_ok=True)
            test = os.path.join(path, ".test_perm")
            with open(test, "w") as f:
                f.write("ok")
            os.remove(test)
            return path
        except Exception:
            print("Некорректный путь или нет доступа. Попробуйте другой.")


def download_image(url, path, idx, results, lock):
    
    save_path = None
    try:
        ext = os.path.splitext(url.split("?")[0])[1]
        if not ext or len(ext) > 5:
            ext = ".jpg"
        save_path = os.path.join(path, f"image_{idx}{ext}")
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
        with open(save_path, "wb") as f:
            f.write(data)
        status = "Успех"
    except Exception:
        status = "Ошибка"
        if save_path and os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception:
                pass
    with lock:
        results.append((idx, url, status))

def main():
    path = ask_path()
    print("Введите ссылки на изображения (пустая строка — конец):")

    results = []
    lock = threading.Lock()
    threads = []

    idx = 0
    while True:
        try:
            url = input().strip()
        except EOFError:
            break
        if not url:
            break
        t = threading.Thread(
            target=download_image,
            args=(url, path, idx, results, lock),
            daemon=True,
        )
        t.start()
        threads.append(t)
        idx += 1

    if idx == 0:
        return

    if any(t.is_alive() for t in threads):
        print("Не все изображения загружены, ожидание завершения...")

    for t in threads:
        t.join()

    results.sort(key=lambda r: r[0])
    rows = [(url, status) for _, url, status in results]

    print("Сводка об успешных и неуспешных загрузках")
    print()
    print(format_table(["Ссылка", "Статус"], rows, ["left", "left"]))


if __name__ == "__main__":
    main()