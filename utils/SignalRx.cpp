#include "SignalRx.hpp"


SignalRx::SignalRx()
{
    this->init();
}

SignalRx::SignalRx(float freq)
{
    this->init();
    this->set_freq(freq);
}

void SignalRx::init()
{
    this->rssi = 1;
    this->cariboulite_connected = detect_board();
    if(this->cariboulite_connected)
    {
        std::cout << "Detected CaribouLite!" << std::endl;
    }
    else
    {
        std::cout << "Undetected CaribouLite!" << std::endl;

        // TODO: here the CL is not connected so we need to crash the program
    }
    std::cout << "CaribouLite is ready\n" << std::endl;
    CaribouLite &cl = CaribouLite::GetInstance(false);
    this->cl = &cl;
    this->print_info();
    this->s1g = cl.GetRadioChannel(CaribouLiteRadio::RadioType::S1G);
    std::cout << "First Radio Name: " << this->s1g->GetRadioName() << "  MtuSize: " << std::dec << this->s1g->GetNativeMtuSample() << " Samples" << std::endl;
    this->freq_ranges = this->s1g->GetFrequencyRange();
    for (int i = 0; i < this->freq_ranges.size(); i++)
    {
        std::cout << "  " << i << " : " << this->freq_ranges[i] << std::endl;
    }
    std::cout << "SignalRx is ready\n" << std::endl;

    // TODO: Gain level into a Ini config file
    this->s1g->SetRxGain(35);
    this->s1g->SetAgc(false);
    this->s1g->SetRxSampleRate(4000000);
    this->legit_freq = false;
    this->s1g->SetFrequency(900000000LLU);
    this->s1g->StartReceiving();
}

void SignalRx::print_info()
{
    std::cout << "Initialized CaribouLite: " << this->cl->IsInitialized() << std::endl;
    std::cout << "API Versions: " << this->cl->GetApiVersion() << std::endl;
    std::cout << "Hardware Serial Number: " << std::hex << this->cl->GetHwSerialNumber() << std::endl;
    std::cout << "Hardware Unique ID: " << this->cl->GetHwGuid() << std::endl;
}

void SignalRx::set_freq(float freq)
{
    for (int i = 0; i < this->freq_ranges.size(); i++)
    {
        //std::cout << i << " : " << freq_ranges[i].get_f_min() << std::endl;
        if(this->freq_ranges[i].get_f_min() <= freq && freq <= this->freq_ranges[i].get_f_max())
        {
            
            this->s1g->SetFrequency(freq);
            //std::cout << "Can start sample" << std::endl; 
            this->legit_freq = true;
            return;
        }
    }
    this->legit_freq = false;
}

bool SignalRx::get_connectivity_status()
{
    return this->cariboulite_connected;
}

void SignalRx::flusher()
{
    this->s1g->FlushBuffers();
}

void SignalRx::getsamples(uint8_t num_samples, float* buffer)
{
    for (int i = 0; i < num_samples; i++)
    {
        int ret = s1g->ReadSamples(this->samples_buffer, 
                                   sizeof(this->samples_buffer)/sizeof(std::complex<float>));
        if (ret > 0)
        {
            buffer[i] = calc_rssi(this->samples_buffer, ret);
        }
    }
}

SignalRx::~SignalRx()
{
    this->s1g->StopReceiving();
    std::cout << "Bye - Bye" << std::endl;
}
