with open("input.txt") as f:
    matrix = [list(map(int, line.split())) for line in f if line.strip()]

n = len(matrix)
m = len(matrix[0]) if n else 0
seen = [[False] * m for _ in range(n)]
squares = circles = 0

for i in range(n):
    for j in range(m):
        if matrix[i][j] == 1 and not seen[i][j]:
            stack = [(i, j)]
            seen[i][j] = True
            cells = []
            while stack:
                r, c = stack.pop()
                cells.append((r, c))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < m:
                        if matrix[nr][nc] == 1 and not seen[nr][nc]:
                            seen[nr][nc] = True
                            stack.append((nr, nc))
            rs = [r for r, _ in cells]
            cs = [c for _, c in cells]
            h = max(rs) - min(rs) + 1
            w = max(cs) - min(cs) + 1
            if h == w and len(cells) == h * w:
                squares += 1
            else:
                circles += 1

print(squares, circles)