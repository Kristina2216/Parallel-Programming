__kernel void worker_task(__global double* sums, const int N, const int M, const double h){
    int global_id = get_global_id(0);
    double x = 0.0;
    double sum = 0.0;

    for(int i =  M*global_id+1; i<M*global_id+1 + M; i=i+1){
        if(i==N+1){
            break;
        }
        x = h * ((double)i - 0.5);
        sum += 4.0 / (1.0 + x*x);
    }
    sums[global_id] = h * sum;
}