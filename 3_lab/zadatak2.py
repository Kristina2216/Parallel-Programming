import pyopencl as cl
import numpy as np
import time

M = 1
L = 100

if __name__ == "__main__":
    
    N = int(input("Unesite broj elemenata reda: "))
    h = 1.0/N
    sums = np.array([0 for i in range(int(N/M))], dtype=np.float64)

    #pripremi instrukcije, stvori kontekst
    code = open('zadatak2.cl', 'r').read()
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)

    #ucitaj iz zajednicke memorije za OpenCL
    buffSum = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, sums.nbytes)
   
    prg = cl.Program(ctx, code).build()
    global_size = (int(N / M), )
    local_size = (L, )
    start = time.time()
    prg.worker_task(queue, global_size, local_size, buffSum, np.int32(N), np.int32(M), np.float64(h)) #zovi kernel f-ju, arg: queue, glob_size, local size + definirani
    cl.enqueue_copy(queue, sums, buffSum).wait() #prepisi rezultat nazad u globalnu
    end=time.time()
    print("Time: ", end - start)
    print(np.sum(sums))


