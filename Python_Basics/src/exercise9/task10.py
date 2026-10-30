line = input().split()
if len(line) != 2:
    print("Invalid input")
else:
    try:
        n = int(line[0])
        T = int(line[1])
        if n <= 0 or T <= 0:
            raise ValueError
    except ValueError:
        print("Invalid input")
    else:
        devices = []
        ok = True
        for _ in range(n):
            parts = input().split()
            if len(parts) != 3:
                ok = False
                break
            try:
                y = int(parts[0])
                c = int(parts[1])
                t = int(parts[2])
                if y <= 0 or c <= 0 or t <= 0:
                    ok = False
                    break
            except ValueError:
                ok = False
                break
            devices.append((y, c, t))

        if not ok:
            print("Invalid input")
        else:
            best = None
            for i in range(n):
                for j in range(i + 1, n):
                    if devices[i][0] == devices[j][0] and devices[i][2] + devices[j][2] == T:
                        cost = devices[i][1] + devices[j][1]
                        if best is None or cost < best:
                            best = cost
            print(best if best is not None else "Invalid input")