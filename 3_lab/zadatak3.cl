__kernel void jacobi_step(__global double *psinew, __global const double *psi, const int m, const int n)
{
	int i = get_global_id(0) + 1;
    int j = get_global_id(1) + 1;
    if(i<=m){
        if(j<=n){
            psinew[i*(m+2)+j]=0.25*(psi[(i-1)*(m+2)+j]+psi[(i+1)*(m+2)+j]+psi[i*(m+2)+j-1]+psi[i*(m+2)+j+1]);
        }
    }
	
}

__kernel void deltasq(__global double *newArr, __global double *oldArr, __global double *tmp, const unsigned int m, const unsigned int n, const unsigned int N)
{
    int i = get_global_id(0) + 1;
    int j = get_global_id(1) + 1;
    double temp;
    temp = newArr[i * (m + 2) + j] - oldArr[i * (m + 2) + j];
    tmp[i * (m + 2) + j] = temp * temp;
}

__kernel void copy_arrays(__global const double *psinew, __global double *psi, int m, int n)
{
    int i = get_global_id(0) + 1;
    int j = get_global_id(1) + 1;
    psi[i*(m+2)+j]=psinew[i*(m+2)+j];

}