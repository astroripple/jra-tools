import numpy as np


class Labelref:
    def __init__(self):
        ur = np.zeros([18, 18])
        s0 = 1
        for i in range(18):
            for j in range(i + 1, 18):
                if i != j:
                    ur[i, j] = s0
                    s0 += 1
        self.umaren_ref = ur

        ut = np.zeros([18, 18])
        s1 = 1
        for i in range(18):
            for j in range(18):
                if i != j:
                    ut[i, j] = s1
                    s1 += 1
        self.umatan_ref = ut

        sp = np.zeros([18, 18, 18])
        s2 = 1
        for i in range(18):
            for j in range(i + 1, 18):
                for k in range(j + 1, 18):
                    sp[i, j, k] = s2
                    s2 += 1
        self.sanrenpuku_ref = sp

        st = np.zeros([18, 18, 18])
        s3 = 1
        for i in range(18):
            for j in range(18):
                if i != j:
                    for k in range(18):
                        if j != k and k != i:
                            st[i, j, k] = s3
                            s3 += 1
        self.sanrentan_ref = st

    def getUmarenNumbers(self, n):
        one = 0
        two = 0
        if n == 1:
            one = 1
            two = 2
        else:
            for i in range(18):
                for j in range(i + 1, 18):
                    if self.umaren_ref[i, j] == n:
                        one = i + 1
                        two = j + 1
                        break
        return (one, two)

    def getUmarenCatnumber(self, n, m):
        return int(self.umaren_ref[n - 1, m - 1])

    def getUmatanNumbers(self, n):
        one = 0
        two = 0
        if n == 1:
            one = 1
            two = 2
        else:
            for i in range(18):
                for j in range(18):
                    if self.umatan_ref[i, j] == n:
                        one = i + 1
                        two = j + 1
                        break
        return (one, two)

    def getUmatanCatnumber(self, n, m):
        return int(self.umatan_ref[n - 1, m - 1])

    def getSanrenpukuNumbers(self, n):
        one = 0
        two = 0
        three = 0
        if n == 1:
            one = 1
            two = 2
            three = 3
        else:
            for i in range(18):
                for j in range(i + 1, 18):
                    for k in range(j + 1, 18):
                        if self.sanrenpuku_ref[i, j, k] == n:
                            one = i + 1
                            two = j + 1
                            three = k + 1
                            break
        return (one, two, three)

    def getSanrenpukuCatnumber(self, n, m, l):
        return int(self.sanrenpuku_ref[n - 1, m - 1, l - 1])

    def getSanrentanNumbers(self, n):
        one = 0
        two = 0
        three = 0
        if n == 1:
            one = 1
            two = 2
            three = 3
        else:
            for i in range(18):
                for j in range(18):
                    if i != j:
                        for k in range(18):
                            if self.sanrentan_ref[i, j, k] == n:
                                one = i + 1
                                two = j + 1
                                three = k + 1
                                break
        return (one, two, three)

    def getSanrentanCatnumber(self, n, m, l):
        return int(self.sanrentan_ref[n - 1, m - 1, l - 1])
