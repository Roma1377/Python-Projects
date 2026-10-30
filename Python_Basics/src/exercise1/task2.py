n = int(input())
if n < 0:
    print(False)
else:
    x, rev = n, 0
    while x:
        rev = rev * 10 + x % 10
        x //= 10
    print(rev == n)