s = input().strip()
if not s.isdigit() or int(s) == 0:
    print("Natural number was expected")
else:
    n = int(s)
    row = [1]
    for _ in range(n):
        print(" ".join(map(str, row)))
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]