import pyopencl as cl
import numpy as np
import time


def worker_task():
    x = 0.0
    sum = 0.0

    for i in range(N):
        x = h * (i - 0.5)
        sum += 4.0 / (1.0 + x*x)
    sum= h * sum
    return sum

if __name__ == "__main__":
    
    N = int(input("Unesite broj elemenata reda: "))
    h = 1.0/N

    start=time.time()
    sum = worker_task()
    end=time.time()
    print("Time: ", end - start)
    print(sum)


