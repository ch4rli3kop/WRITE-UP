#/usr/bin/python3

def o(a, b) :
    if (a == 0) :
        return [0, 1];

    r = o(b % a, a);
    return [(r[1] - (((b // a) * r[0]))), r[0]]

def int2str(a):
    res = ''
    for i in range(0, 4):
        res += (chr((a >> (8*i)) & 0xff))
    return res

ans = [0x271986B, 0xA64239C9, 0x271DED4B, 0x1186143, 0xC0FA229F, 0x690E10BF, 0x28DCA257, 0x16C699D1, 0x55A56FFD, 0x7EB870A1, 0xC5C9799F, 0x2F838E65]

res = []
for i in ans:
    res.append(int2str(o(i, 0x100000000)[0]))

print('FLAG is ' + ''.join(res))
#FLAG is CTF{y0u_c4n_k3ep_y0u?_m4gic_1_h4Ue_laser_b3ams!}