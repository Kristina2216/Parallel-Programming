import pyopencl as cl
import numpy as np
import time

if __name__ == "__main__":
    

    N= int(input("Unesite broj gradova: "))
    M= int(input("Unesite velicinu grupe: "))

    X= np.array([(np.random.rand()) for i in range(N)], dtype=np.float32)
    Y= np.array([(np.random.rand()) for i in range(N)], dtype=np.float32)
    D=np.array([0 for i in range(N)], dtype=np.float32)

    #pripremi instrukcije, stvori kontekst
    code = open('zadatak1.cl', 'r').read()
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)

    #ucitaj iz zajednicke memorije za OpenCL
    buffX = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=X) 
    buffY = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=Y) 
    buffD = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, D.nbytes)
   
    prg = cl.Program(ctx, code).build()  
    global_size = (N // M, )
    start = time.time()
    prg.calc_distance(queue, global_size, None, np.int32(N), buffX, buffY, buffD) #zovi kernel f-ju, arg: queue, glob_size, local size + definirani
    cl.enqueue_copy(queue, D, buffD) #prepisi rezultat nazad u globalnu
    end=time.time()
    print("Time: ", end - start)
    print(np.mean(D))


