#include <iostream>
#include <CaribouLite.hpp>
#include <complex>
#include <vector>
#include <algorithm>
#include <cmath>
#include <numeric>

bool detect_board();
float calc_rssi(const std::complex<float>* signal, size_t num_of_samples);
void calc_statistical_data(float* data, size_t size, float* med_arr);
