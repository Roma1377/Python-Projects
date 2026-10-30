n, x = input().split()
n = int(n)
x = float(x)
coeffs = [float(input()) for _ in range(n + 1)]

d = 0.0
for i in range(n):
    d += coeffs[i] * (n - i) * (x ** (n - i - 1))

print(f"{d:.3f}")