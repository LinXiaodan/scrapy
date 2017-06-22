#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import random


def getX(a):
    if len(a) == 5:
        b = 200
        c = int(a, base=16) or 0
        d = c % b
        if d < 40:
            d = 40
        return d


def unsigned_right_shift(a, b):
    return (a & 0xffffffff) >> b


def md5(a):
    def b(a, b):
        return a << b | unsigned_right_shift(a, 32-b)

    def c(a, b):
        e = 2147483648 & a
        f = 2147483648 & b
        c = 1073741824 & a
        d = 1073741824 & b
        g = (1073741823 & a) + (1073741823 & b)
        if c & d:
            return 2147483648 ^ g ^ e ^ f
        else:
            if c | d:
                if 1073741824 & g:
                    return 3221225472 ^ g ^ e ^ f
                else:
                    return 1073741824 ^ g ^ e ^ f
            else:
                return g ^ e ^ f

    def d(a, b, c):
        return a & b | ~a & c

    def e(a, b, c):
        return a & c | b & ~c

    def f(a, b, c):
        return a ^ b ^ c

    def g(a, b, c):
        return b ^ (a | ~c)

    def h(a, e, f, g, h, i, j):
        a = c(a, c(c(d(e, f, g), h), j))
        return c(b(a, i), e)

    def i(a, d, f, g, h, i, j):
        a = c(a, c(c(e(d, f, g), h), j))
        return c(b(a, i), d)

    def j(a, d, e, g, h, i, j):
        a = c(a, c(c(f(d, e, g), h), j))
        return c(b(a, i), d)

    def k(a, d, e, f, h, i, j):
        a = c(a, c(c(g(d, e, f), h), j))
        return c(b(a, i), d)

    def l(a):
        c = len(a)
        d = c + 8
        e = (d - d % 64)/64
        f = 16 * (e + 1)
        g = [0] * (f-1)
        h = 0
        i = 0
        while i < c:
            b = (i - i % 4) / 4
            h = i % 4 * 8
            g[b] = g[b] | ord(a[i]) << h
            i += 1
        b = (i - i % 4) / 4
        h = i % 4 * 8
        g[b] = g[b] | 128 << h
        g[f - 2] = c << 3
        g.append(unsigned_right_shift(c, 29))
        return g

    def m(a):
        d = ''
        e = ''
        for c in range(0, 4):
            b = unsigned_right_shift(a, 8 * c) & 255
            e = '0' + '{0:x}'.format(b)
            d += e[-2:]
        return d

    def n(a):
        a = a.replace('\r\n', '\n')
        b = ''
        for c in range(0, len(a)):
            d = ord(a[c])
            if d < 128:
                b += chr(d)
            else:
                if d > 127 and d < 2048:
                    b += chr(d >> 6 | 192)
                    b += chr(63 & d | 128)
                else:
                    b += chr(d >> 12 | 224)
                    b += chr(d >> 6 & 63 | 128)
                    b += chr(63 & d | 128)
        return b

    x, y, z, A, B, C, D, E, F, G, H, I, J, K, L, M, N = [], 7, 12, 17, 22, 5, 9, 14, 20, 4, 11, 16, 23, 6, 10, 15, 21
    a = n(a)
    x = l(a)
    t = 1732584193
    u = 4023233417
    v = 2562383102
    w = 271733878
    for o in range(0, len(x), 16):
        p = t
        q = u
        r = v
        s = w
        t = h(t, u, v, w, x[o + 0], y, 3614090360)
        w = h(w, t, u, v, x[o + 1], z, 3905402710)
        v = h(v, w, t, u, x[o + 2], A, 606105819)
        u = h(u, v, w, t, x[o + 3], B, 3250441966)
        t = h(t, u, v, w, x[o + 4], y, 4118548399)
        w = h(w, t, u, v, x[o + 5], z, 1200080426)
        v = h(v, w, t, u, x[o + 6], A, 2821735955)
        u = h(u, v, w, t, x[o + 7], B, 4249261313)
        t = h(t, u, v, w, x[o + 8], y, 1770035416)
        w = h(w, t, u, v, x[o + 9], z, 2336552879)
        v = h(v, w, t, u, x[o + 10], A, 4294925233)
        u = h(u, v, w, t, x[o + 11], B, 2304563134)
        t = h(t, u, v, w, x[o + 12], y, 1804603682)
        w = h(w, t, u, v, x[o + 13], z, 4254626195)
        v = h(v, w, t, u, x[o + 14], A, 2792965006)
        u = h(u, v, w, t, x[o + 15], B, 1236535329)
        t = i(t, u, v, w, x[o + 1], C, 4129170786)
        w = i(w, t, u, v, x[o + 6], D, 3225465664)
        v = i(v, w, t, u, x[o + 11], E, 643717713)
        u = i(u, v, w, t, x[o + 0], F, 3921069994)
        t = i(t, u, v, w, x[o + 5], C, 3593408605)
        w = i(w, t, u, v, x[o + 10], D, 38016083)
        v = i(v, w, t, u, x[o + 15], E, 3634488961)
        u = i(u, v, w, t, x[o + 4], F, 3889429448)
        t = i(t, u, v, w, x[o + 9], C, 568446438)
        w = i(w, t, u, v, x[o + 14], D, 3275163606)
        v = i(v, w, t, u, x[o + 3], E, 4107603335)
        u = i(u, v, w, t, x[o + 8], F, 1163531501)
        t = i(t, u, v, w, x[o + 13], C, 2850285829)
        w = i(w, t, u, v, x[o + 2], D, 4243563512)
        v = i(v, w, t, u, x[o + 7], E, 1735328473)
        u = i(u, v, w, t, x[o + 12], F, 2368359562)
        t = j(t, u, v, w, x[o + 5], G, 4294588738)
        w = j(w, t, u, v, x[o + 8], H, 2272392833)
        v = j(v, w, t, u, x[o + 11], I, 1839030562)
        u = j(u, v, w, t, x[o + 14], J, 4259657740)
        t = j(t, u, v, w, x[o + 1], G, 2763975236)
        w = j(w, t, u, v, x[o + 4], H, 1272893353)
        v = j(v, w, t, u, x[o + 7], I, 4139469664)
        u = j(u, v, w, t, x[o + 10], J, 3200236656)
        t = j(t, u, v, w, x[o + 13], G, 681279174)
        w = j(w, t, u, v, x[o + 0], H, 3936430074)
        v = j(v, w, t, u, x[o + 3], I, 3572445317)
        u = j(u, v, w, t, x[o + 6], J, 76029189)
        t = j(t, u, v, w, x[o + 9], G, 3654602809)
        w = j(w, t, u, v, x[o + 12], H, 3873151461)
        v = j(v, w, t, u, x[o + 15], I, 530742520)
        u = j(u, v, w, t, x[o + 2], J, 3299628645)
        t = k(t, u, v, w, x[o + 0], K, 4096336452)
        w = k(w, t, u, v, x[o + 7], L, 1126891415)
        v = k(v, w, t, u, x[o + 14], M, 2878612391)
        u = k(u, v, w, t, x[o + 5], N, 4237533241)
        t = k(t, u, v, w, x[o + 12], K, 1700485571)
        w = k(w, t, u, v, x[o + 3], L, 2399980690)
        v = k(v, w, t, u, x[o + 10], M, 4293915773)
        u = k(u, v, w, t, x[o + 1], N, 2240044497)
        t = k(t, u, v, w, x[o + 8], K, 1873313359)
        w = k(w, t, u, v, x[o + 15], L, 4264355552)
        v = k(v, w, t, u, x[o + 6], M, 2734768916)
        u = k(u, v, w, t, x[o + 13], N, 1309151649)
        t = k(t, u, v, w, x[o + 4], K, 4149444226)
        w = k(w, t, u, v, x[o + 11], L, 3174756917)
        v = k(v, w, t, u, x[o + 2], M, 718787259)
        u = k(u, v, w, t, x[o + 9], N, 3951481745)
        t = c(t, p)
        u = c(u, q)
        v = c(v, r)
        w = c(w, s)
    O = m(t) + m(u) + m(v) + m(w)
    return O.lower()


def ra(a, b):
    c = b[32:]
    d = []
    for e in range(0, len(c)):
        f = ord(c[e])
        if f > 57:
            d.append(f - 87)
        else:
            d.append(f - 48)
    c = 36 * d[0] + d[1]
    g = round(a) + c
    b = b[0: 32]
    i = [[], [], [], [], []]
    j = {}
    k = 0
    for e in range(0, len(b)):
        h = b[e]
        if h not in j or not j[h]:
            j[h] = 1
            i[k].append(h)
            k += 1
            if k == 5:
                k = 0
    n = g
    o = 4
    p = ''
    q = [1, 2, 5, 10, 50]
    while n > 0:
        if n - q[o] >= 0:
            m = int(random() * len(i[o]))
            p += i[o][m]
            n -= q[o]
        else:
            i = i[:o] + i[o+1:]
            q = q[:o] + q[o+1:]
            o -= 1
    return p


def ajax(challenge):
    rand0 = int(6 * random())
    rand1 = int(300 * random())
    f = md5(str(rand0))[0: 9]
    g = md5(str(rand1))[10: 19]
    h = ''
    for i in range(0, 9):
        if i % 2 == 0:
            h += f[i]
        else:
            h += g[i]
    k = h[4:]
    x_pos = getX(k)
    validate = ra(x_pos, challenge) + '_' + ra(rand0, challenge) + '_' + ra(rand1, challenge)
    return validate