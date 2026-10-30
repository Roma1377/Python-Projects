s = input().strip()
i, n = 0, len(s)
sign = 1

if i < n and s[i] in "+-":
    if s[i] == "-":
        sign = -1
    i += 1

int_part = ""
while i < n and s[i].isdigit():
    int_part += s[i]
    i += 1

frac_part = ""
if i < n and s[i] == ".":
    i += 1
    while i < n and s[i].isdigit():
        frac_part += s[i]
        i += 1

ok = bool(int_part or frac_part)
exp = 0

if ok and i < n and s[i] in "eE":
    i += 1
    esign = 1
    if i < n and s[i] in "+-":
        if s[i] == "-":
            esign = -1
        i += 1
    e_digits = ""
    while i < n and s[i].isdigit():
        e_digits += s[i]
        i += 1
    if not e_digits:
        ok = False
    else:
        e_val = 0
        for d in e_digits:
            e_val = e_val * 10 + (ord(d) - ord('0'))
        exp = esign * e_val

if i != n:
    ok = False

if not ok:
    print("Invalid input")
else:
    num = 0
    for d in int_part:
        num = num * 10 + (ord(d) - ord('0'))
    for d in frac_part:
        num = num * 10 + (ord(d) - ord('0'))
    num = num / (10 ** len(frac_part))
    num = num * (10 ** exp) * sign
    print(f"{num * 2:.3f}")