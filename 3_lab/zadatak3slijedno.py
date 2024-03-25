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

def jacobi_step(psi, m, n):
    psinew = np.zeros((m + 2)* (n + 2))
    for i in range(m):
        for j in range(n):
            psinew[i*(m+2)+j]=0.25*(psi[(i-1)*(m+2)+j]+psi[(i+1)*(m+2)+j]+psi[i*(m+2)+j-1]+psi[i*(m+2)+j+1])
    return psinew

def deltasq(newArr, oldArr, m, n):
    dsq=0.0
    for i in range(m):
             for j in range (n):
                tmp = newArr[i*(m+2)+j]-oldArr[i*(m+2)+j]
                dsq += tmp*tmp
    return dsq

def copy_arrays(psitmp, psi, m, n):
    for i in range(m):
        for j in range(n):
            psi[i*(m+2)+j]=psitmp[i*(m+2)+j]
    return psi

if __name__ == "__main__":
    
    printfreq=100 #output frequency
    tolerance=0.0005 #tolerance for convergence. <=0 means do not check

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


    print("Running CFD on %d x %d grid in serial\n",m,n)
    psi = np.zeros(((m + 2) * (n + 2)))
    psi=boundarypsi(psi, m, n, b, h, w)   
    bnorm = np.sqrt(psi @ psi.T)

    error = float('inf')

    print("Starting main loop...")
    start=time.time()
    for iteration in range(1, numIter + 1):
        psitmp = jacobi_step(psi, m, n)

        if checkerr or iteration == numIter:
            tmp = np.zeros(psitmp.shape[0], dtype=np.double)
            tmp = deltasq(psitmp, psi, m, n)
            error = math.sqrt(tmp)/bnorm

        if checkerr:
            if error < tolerance:
                print(f"Converged on iter {iteration}")
                break
        
        psi = copy_arrays(psitmp, psi, m, n)
        print(psi)
        
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