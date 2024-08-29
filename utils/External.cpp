#include "External.hpp"

bool detect_board()
{
    CaribouLite::SysVersion ver;
    std::string name;
    std::string guid;

    if (CaribouLite::DetectBoard(&ver, name, guid))
    {
        return true;
    }
    else
    {
        return false;
    }
}

float calc_rssi(const std::complex<float>* signal, size_t num_of_samples)
{
    if (num_of_samples == 0)
    {
        return 0.0f;
    }

    float sum_of_squares = 0.0f;
    for (size_t i = 0; i < num_of_samples; ++i)
    {
        float vrmsp2 = (signal[i].real() * signal[i].real()) + (signal[i].imag() * signal[i].imag());
        sum_of_squares += vrmsp2 / 100.0;
    }

    float mean_of_squares = sum_of_squares / num_of_samples;

    // Convert RMS value to dBm
    return 10 * log10(mean_of_squares);
}

void calc_statistical_data(float* data, size_t size, float* stat_arr) 
{
    std::vector<float>cutting_samples;
    int mid = size/2;
    float q1, q3;
    std::sort(data, data + size);
    float maximum = data[size - 1];
    float variance = 0.0;
    for(int i = 0; i < size; i++)
    {
        if(data[i] <= maximum && data[i] > maximum - 5)
        {
            cutting_samples.push_back(data[i]);
        }
    }
    stat_arr[1] = cutting_samples.size();
    stat_arr[0] = std::accumulate(cutting_samples.begin(), cutting_samples.end(), 0.0)/ stat_arr[1];
    for (double value : cutting_samples)
    {
        variance += std::pow(value - stat_arr[0], 2);
    }
    variance /= stat_arr[1];

    stat_arr[2] = std::sqrt(variance);
}
