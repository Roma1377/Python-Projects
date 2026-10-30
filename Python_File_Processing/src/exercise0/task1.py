import multiprocessing as mp
import os
import random
import sys
import time

GOLDEN = (1 + 5 ** 0.5) / 2


def enable_ansi():
    if os.name == "nt":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def calc_probs(n):
    probs = []
    remaining = 1.0
    for _ in range(n - 1):
        p = remaining / GOLDEN
        probs.append(p)
        remaining -= p
    probs.append(remaining)
    return probs


def read_files():
    base = os.path.dirname(os.path.abspath(__file__))

    examiners = []
    students = []
    questions = []

    with open(os.path.join(base, "examiners.txt"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, gender = line.split()
            examiners.append({"name": name, "gender": gender})

    with open(os.path.join(base, "students.txt"), encoding="utf-8") as f:
        pos = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, gender = line.split()
            students.append({"name": name, "gender": gender, "position": pos})
            pos += 1

    with open(os.path.join(base, "questions.txt"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(line)

    return examiners, students, questions


def pick_answer(gender, words):
    probs = calc_probs(len(words))
    weights = probs if gender == "М" else list(reversed(probs))
    return random.choices(words, weights=weights, k=1)[0]


def pick_correct(words):
    correct = set()
    remaining = words[:]
    first = random.choice(remaining)
    correct.add(first)
    remaining.remove(first)
    while remaining and random.random() < 1 / 3:
        nxt = random.choice(remaining)
        correct.add(nxt)
        remaining.remove(nxt)
    return correct


def examiner_worker(ex_idx, students, examiners, questions, correct_counts,
                    queue, queue_lock, q_lock, start_time):
    name = examiners[ex_idx]["name"]
    lunch_taken = False

    while True:
        with queue_lock:
            if not queue:
                break
            s_idx = queue[0]
            del queue[0]

        student_name = students[s_idx]["name"]
        student_gender = students[s_idx]["gender"]

        examiners[ex_idx]["current"] = student_name

        correct = incorrect = 0
        for _ in range(3):
            q_idx = random.randrange(len(questions))
            words = questions[q_idx].split()
            chosen = pick_answer(student_gender, words)
            correct_set = pick_correct(words)
            if chosen in correct_set:
                correct += 1
                with q_lock:
                    correct_counts[q_idx] = correct_counts[q_idx] + 1
            else:
                incorrect += 1

        exam_time = random.uniform(len(name) - 1, len(name) + 1)
        time.sleep(exam_time)

        mood = random.random()
        if mood < 1 / 8:
            passed = False
        elif mood < 3 / 8:
            passed = True
        else:
            passed = correct > incorrect

        now = time.time() - start_time

        with queue_lock:
            examiners[ex_idx]["current"] = "-"
            examiners[ex_idx]["total"] = examiners[ex_idx]["total"] + 1
            if not passed:
                examiners[ex_idx]["failed"] = examiners[ex_idx]["failed"] + 1
            students[s_idx]["status"] = "Сдал" if passed else "Провалил"
            students[s_idx]["finish_time"] = now

        if not lunch_taken and time.time() - start_time >= 30:
            with queue_lock:
                more = bool(queue)
            if more:
                lunch_taken = True
                time.sleep(random.uniform(12, 18))

    with queue_lock:
        examiners[ex_idx]["current"] = "-"
        examiners[ex_idx]["finished"] = True
        examiners[ex_idx]["finish_time"] = time.time() - start_time


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


def render_during(students, examiners, start_time):
    q_list = sorted([s for s in students if s["status"] == "Очередь"],
                    key=lambda s: s["position"])
    p_list = sorted([s for s in students if s["status"] == "Сдал"],
                    key=lambda s: s["position"])
    f_list = sorted([s for s in students if s["status"] == "Провалил"],
                    key=lambda s: s["position"])

    s_table = format_table(
        ["Студент", "Статус"],
        [(s["name"], s["status"]) for s in q_list + p_list + f_list],
        ["left", "center"],
    )

    e_rows = []
    for e in examiners:
        if e["finished"]:
            wt = e["finish_time"]
        else:
            wt = time.time() - start_time
        e_rows.append((e["name"], e["current"], e["total"], e["failed"], f"{wt:.2f}"))

    e_table = format_table(
        ["Экзаменатор", "Текущий студент", "Всего студентов", "Завалил", "Время работы"],
        e_rows,
        ["left", "left", "center", "center", "center"],
    )

    n_left = len(q_list)
    total = len(students)
    elapsed = time.time() - start_time

    return "\n".join([
        s_table, "",
        e_table, "",
        f"Осталось в очереди: {n_left} из {total}",
        f"Время с момента начала экзамена: {elapsed:.2f}",
    ])


def render_final(students, examiners, questions, correct_counts, total_time):
    p_list = sorted([s for s in students if s["status"] == "Сдал"],
                    key=lambda s: s["position"])
    f_list = sorted([s for s in students if s["status"] == "Провалил"],
                    key=lambda s: s["position"])

    s_table = format_table(
        ["Студент", "Статус"],
        [(s["name"], s["status"]) for s in p_list + f_list],
        ["left", "center"],
    )

    e_rows = []
    for e in examiners:
        wt = e["finish_time"] if e["finish_time"] is not None else total_time
        e_rows.append((e["name"], e["total"], e["failed"], f"{wt:.2f}"))

    e_table = format_table(
        ["Экзаменатор", "Всего студентов", "Завалил", "Время работы"],
        e_rows,
        ["left", "center", "center", "center"],
    )

    if p_list:
        min_t = min(s["finish_time"] for s in p_list)
        best_students = [s["name"] for s in p_list if abs(s["finish_time"] - min_t) < 1e-9]
    else:
        best_students = []

    rates = []
    for e in examiners:
        rate = e["failed"] / e["total"] if e["total"] > 0 else 0.0
        rates.append((rate, e["name"]))
    if rates:
        min_r = min(r for r, _ in rates)
        best_examiners = [n for r, n in rates if abs(r - min_r) < 1e-9]
    else:
        best_examiners = []

    if f_list:
        min_ft = min(s["finish_time"] for s in f_list)
        expelled = [s["name"] for s in f_list if abs(s["finish_time"] - min_ft) < 1e-9]
    else:
        expelled = []

    q_list = list(questions)
    counts = list(correct_counts)
    if q_list:
        max_c = max(counts)
        best_q = [q for q, c in zip(q_list, counts) if c == max_c]
    else:
        best_q = []

    n_passed = len(p_list)
    n_total = len(students)
    conclusion = ("экзамен удался"
                  if (n_total and n_passed / n_total > 0.85)
                  else "экзамен не удался")

    return "\n".join([
        s_table, "",
        e_table, "",
        f"Время с момента начала экзамена и до момента и его завершения: {total_time:.2f}",
        f"Имена лучших студентов: {', '.join(best_students)}",
        f"Имена лучших экзаменаторов: {', '.join(best_examiners)}",
        f"Имена студентов, которых после экзамена отчислят: {', '.join(expelled)}",
        f"Лучшие вопросы: {', '.join(best_q)}",
        f"Вывод: {conclusion}",
    ])

def main():
    examiners, students, questions = read_files()

    if not examiners:
        print("Нет экзаменаторов")
        return
    if not students:
        print("Нет студентов")
        return
    if not questions:
        print("Нет вопросов")
        return

    manager = mp.Manager()

    shared_examiners = manager.list()
    for e in examiners:
        shared_examiners.append(manager.dict({
            "name": e["name"], "gender": e["gender"],
            "current": "-", "total": 0, "failed": 0,
            "finished": False, "finish_time": None,
        }))

    shared_students = manager.list()
    for s in students:
        shared_students.append(manager.dict({
            "name": s["name"], "gender": s["gender"], "position": s["position"],
            "status": "Очередь", "finish_time": None,
        }))

    shared_questions = manager.list(questions)
    correct_counts = manager.list([0] * len(questions))
    queue = manager.list(list(range(len(students))))

    queue_lock = manager.Lock()
    q_lock = manager.Lock()

    start_time = time.time()

    processes = []
    for i in range(len(examiners)):
        p = mp.Process(
            target=examiner_worker,
            args=(i, shared_students, shared_examiners, shared_questions,
                  correct_counts, queue, queue_lock, q_lock, start_time),
        )
        p.start()
        processes.append(p)

    while any(p.is_alive() for p in processes):
        text = render_during(shared_students, shared_examiners, start_time)
        sys.stdout.write("\033[H\033[J")
        sys.stdout.write(text + "\n")
        sys.stdout.flush()
        time.sleep(0.3)

    for p in processes:
        p.join()

    total_time = time.time() - start_time

    text = render_final(shared_students, shared_examiners,
                        shared_questions, correct_counts, total_time)

    sys.stdout.write("\033[H\033[J")
    sys.stdout.write(text + "\n")
    sys.stdout.flush()

    manager.shutdown()


if __name__ == "__main__":
    main()