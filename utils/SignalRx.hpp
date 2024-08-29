#include "External.hpp"
#include <iostream>
#include <string>
#include <CaribouLite.hpp>
#include <complex>
#include <cmath>
#include <cassert>
#include <vector>
#include <thread>
#include <mutex>
#include <chrono>
#include <algorithm>

class SignalRx
{
private:
    std::complex<float> samples_buffer[128*1024];
    CaribouLite *cl;
    CaribouLiteRadio* s1g;
    bool legit_freq;
    bool cariboulite_connected;
    float freq;
    float rssi;
    int position;
    std::vector<CaribouLiteFreqRange> freq_ranges;
    // std::thread monitor;


public:
    // Ctors
    SignalRx();
    SignalRx(float freq);

    //Init for ctors
    void print_info();
    void init();

    void flusher();
    // Sample or not
    void getsamples(uint8_t num_samples, float* buffer);
    // void start();
    // void sample();
    // void stop();
    
    // Get & Set
    void set_freq(float freq);
    float get_rssi();
    // void set_state(bool on_off);
    // bool get_state();
    bool get_connectivity_status();


    // Dtor
    ~SignalRx();
};