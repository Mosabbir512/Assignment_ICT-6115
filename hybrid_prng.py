
MASK64 = (1 << 64) - 1

def rol64(x, r):
    return ((x << r) & MASK64) | (x >> (64 - r))

def xorshift64_step(xs):
    xs ^= (xs << 13) & MASK64
    xs ^= (xs >> 7) & MASK64
    xs ^= (xs << 17) & MASK64
    return xs & MASK64

class HybridPRNG:
    def __init__(self, seed_lfsr=1, seed_xs=0xDEADBEEFCAFEBABE, seed_cnt=0):
        self.lfsr = seed_lfsr & MASK64 or 1
        self.xs = seed_xs & MASK64 or 0xCAFEBABE1234567
        self.cnt = seed_cnt & MASK64

    def seed(self, seed_lfsr=None, seed_xs=None, seed_cnt=None):
        if seed_lfsr is not None:
            self.lfsr = seed_lfsr & MASK64 or 1
        if seed_xs is not None:
            self.xs = seed_xs & MASK64 or 0xCAFEBABE1234567
        if seed_cnt is not None:
            self.cnt = seed_cnt & MASK64

    def _lfsr_step(self):
        b63 = (self.lfsr >> 63) & 1
        b61 = (self.lfsr >> 61) & 1
        b60 = (self.lfsr >> 60) & 1
        b0  = self.lfsr & 1
        feedback = b63 ^ b61 ^ b60 ^ b0
        self.lfsr = ((self.lfsr << 1) & MASK64) | (feedback & 1)
        return self.lfsr

    def _mix(self, a, b, c):
        m = (a * 0x2545F4914F6CDD1D) & MASK64
        m = (m + b) & MASK64
        m = (m + c) & MASK64
        return rol64(m, 17)

    def next(self):
        self._lfsr_step()
        self.xs = xorshift64_step(self.xs)
        self.cnt = (self.cnt + 1) & MASK64
        return self._mix(self.xs, self.lfsr, self.cnt)

    def rand64(self):
        return self.next()

    def rand_bytes(self, nbytes):
        out = bytearray()
        while len(out) < nbytes:
            val = self.next()
            out.extend(val.to_bytes(8, 'little'))
        return bytes(out[:nbytes])

if __name__ == '__main__':
    prng = HybridPRNG()
    prng.seed(1, 0xCAFEBABE12345678, 0)
    for i in range(16):
        print(f"{i:2d}: {prng.rand64()}")
    