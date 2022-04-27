def f(x,c):
    # print(c)
    return x ^ c
    # return (x + 1000) % 256


def uf(x,c):
    return x ^ c
    # return (x - 1000) % 256


if __name__ == "__main__":
    n = 243 
    a = f(n)
    print(a)
    print(uf(a))
