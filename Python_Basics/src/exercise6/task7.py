n, m = map(int, input().split())
g = [list(map(int, input().split())) for _ in range(n)]

for i in range(n):
    for j in range(m):
        if i == 0 and j == 0:
            continue
        best = -1
        if i > 0:
            best = max(best, g[i - 1][j])
        if j > 0:
            best = max(best, g[i][j - 1])
        g[i][j] += best

print(g[-1][-1])