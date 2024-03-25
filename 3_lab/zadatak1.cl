__kernel void calc_distance(const int N, const __global float* X, const __global float* Y, __global float* D){
    int global_id = get_global_id(0);
    int step = get_global_size(0);
        for (int i = global_id; i < N; i = i + step) {
            float sum = 0.0f;
            float sroot = 0.0f;
            for (int j = i; j < N; j++) {
                float x_dist = X[i] - X[j];
                float y_dist = Y[i] - Y[j];
                sroot = sqrt(x_dist*x_dist + y_dist*y_dist);
                sum = sum + sroot;
            }
            D[i] = sum/(N-i);
    }
}

