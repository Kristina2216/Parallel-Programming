from cmath import sqrt
import math
import pyopencl as cl
import numpy as np
import time


def boundarypsi(psi, m, n, b, h, w):

    for i in range(b + 1, b + w):
        psi[i * (m + 2)] = i - b

    for i in range(b + w, m + 1):
        psi[i * (m + 2)] = w

    for i in range(1, h + 1):
        psi[(m + 1) * (m + 2) + i] = w

    for i in range(h + 1, h + w):
        psi[(m + 1) * (m + 2) + i] = w - i + h

    return psi

if __name__ == "__main__":
    
    printfreq=100 #output frequency
    tolerance=0.0 #tolerance for convergence. <=0 means do not check

    #simulation sizes
    bbase=10
    hbase=15
    wbase=5
    mbase=32
    nbase=32

    rotational = 1
    checkerr = 0

    if tolerance > 0:
        checkerr = 1

    scale = int(input("Unesite faktor skaliranja: "))
    numIter = int(input("Unesite broj iteracija: "))
    
    b = bbase * scale
    h = hbase * scale
    w = wbase * scale
    m = mbase * scale
    n = nbase * scale

    #pripremi instrukcije, stvori kontekst
    code = open('zadatak3.cl', 'r').read()
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)
    prg = cl.Program(ctx, code).build()

    print("Running CFD on %d x %d grid in serial\n",m,n)
    psi = np.zeros(((m + 2) * (n + 2)))
    psi=boundarypsi(psi, m, n, b, h, w)
    buffPsi = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=psi)

    psitmp = np.zeros((m + 2) * (n + 2))
    buffPsitmp = cl.Buffer(ctx,  cl.mem_flags.WRITE_ONLY, psitmp.nbytes)
    bnorm = np.sqrt(psi @ psi.T)

    error = float('inf')

    print("Starting main loop...")
    start=time.time()
    for iteration in range(1, numIter + 1):
        prg.jacobi_step(queue, (m, n), (2, 2), buffPsitmp, buffPsi, np.int32(m), np.int32(n))
        cl.enqueue_copy(queue, psitmp, buffPsitmp).wait()

        if checkerr or iteration == numIter:
            tmp = np.zeros(psitmp.shape[0], dtype=np.double)
            buffTmp = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, tmp.nbytes)
            prg.deltasq( queue, (m,n), (2,2), buffPsitmp, buffPsi, buffTmp, np.int32(m), np.int32(n), np.int32(n))
            cl.enqueue_copy(queue, tmp, buffTmp).wait()
            error = math.sqrt(np.sum(tmp))/bnorm

        if checkerr:
            if error < tolerance:
                print(f"Converged on iter {iteration}")
                break
        
        prg.copy_arrays(queue, (m, n), (2, 2), buffPsitmp, buffPsi, np.int32(m), np.int32(n))
        cl.enqueue_copy(queue, psi, buffPsi).wait()
        
        if iteration % printfreq == 0:
            if checkerr:
                print(f"Iteration: {iteration}, Error: {error}")
            else:
                print(f"Completed iteration {iteration}")

    end= time.time()
    print(f"""
    Finished after {numIter} iterations, the error is {error:.8f}
    Time for {numIter} iterations was {(end-start):.2f} seconds
    """)