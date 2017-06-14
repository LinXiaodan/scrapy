import random


def get_userresponse(a, b):
    c = b[32:]
    d = []
    e = 0
    while e < len(c):
        f = ord(c[e])
        d.append(f - 87 if f > 57 else f - 48)
        e += 1
    c = 36 * d[0] + d[1]
    g = int(round(a) + c)
    b = b[0:32]
    h = None
    i = [[], [], [], [], []]
    j = {}
    k = 0
    e = 0
    l = len(b)
    while e < l:
        h = b[e]
        if h not in j:
            j[h] = 1
            i[k].append(h)
            k += 1
            k = 0 if 5 == k else k
        e += 1
    m = None
    n = g
    o = 4
    p = ''
    q = [1, 2, 5, 10, 50]
    while n > 0:
        if n - q[o] >= 0:
            m = int(random.random() * len(i[o]))
            p += i[o][m]
            n -= q[o]
        else:
            i = i[0:o] + i[o + 1:-1]
            q = q[0:o] + q[o + 1:-1]
            o -= 1
    return p


def c(a):
    b = None
    c = None
    d = None
    e = []
    f = 0
    g = []
    h = 0
    i = len(a)-1
    while h < i:
        b = round(a[h+1][0]-a[h][0])
        c = round(a[h + 1][1] - a[h][1])
        d = round(a[h + 1][2] - a[h][2])
        g.append([b, c, d])
        if 0 == b and 0 == c and 0 == d:
            pass
        elif 0 == b and 0 == c:
            f += d
        else:
            e.append([b, c, d + f])
            f = 0
        h += 1
    if 0 != f:
        e.append([b, c, f])
    return e


def d(a):
    b = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr"
    c = len(b)
    d = ''
    e = abs(a)
    f = int(e / c)
    if f >= c:
        f = c - 1
    if f:
        d = b[f]
    e %= c
    g = ""
    if a < 0:
        g += "!"
    if d:
        g += "$"
    return g + d + b[int(e)]


def e(a):
    b = [
        [1, 0],
        [2, 0],
        [1, -1],
        [1, 1],
        [0, 1],
        [0, -1],
        [3, 0],
        [2, -1],
        [2, 1]
    ]
    c = "stuvwxyz~"
    d = 0
    e = len(b)
    while d < e:
        if a[0] == b[d][0] and a[1] == b[d][1]:
            return c[d]
        d += 1
    return 0


def get_a(arr):
    b = None
    f = c(arr)
    g = []
    h = []
    i = []
    j = 0
    k = len(f)
    while j < k:
        b = e(f[j])
        if b:
            h.append(b)
        else:
            g.append(d(f[j][0]))
            h.append(d(f[j][1]))
        i.append(d(f[j][2]))
        j += 1
    return "".join(g)+"!!"+"".join(h)+"!!"+"".join(i)
