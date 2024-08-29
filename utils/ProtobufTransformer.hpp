#include <iostream>
#include "Messages.pb.h"

typedef struct System_struct
{
    std::string whoami;
    std::string status;
}Sys_struct;

typedef struct Information_struct
{
    std::string info;
    std::string status;
}Info_struct;

typedef struct Motors_struct
{
    float alpha;
    float beta;
}Motors_struct;

typedef struct Tx_struct
{
    float freq;
    float power;
    std::string wavetype;
    bool onoff;
}Tx_struct;

typedef struct Freq_struct
{
    float freq;
}Freq_struct;


typedef struct Sample_struct
{
    bool onoff;
}Sample_struct;

typedef struct Rssi_struct
{
    float rssi;
    int samples;
    float std;
}Rssi_struct;

std::string encode_sys_msg(const std::string &whoami, const std::string &status);
std::string encode_info_msg(const std::string &info);
std::string encode_motors_msg(const float alpha, const float beta);
std::string encode_tx_msg(const float freq, const float power, const std::string &wave_type, const bool onoff);
std::string encode_freq_msg(const float freq);
std::string encode_sample_msg(const bool onoff);
std::string encode_rssi_msg(const float rssi, const int samples, const float std);

int get_type(const std::string& serialized_data);
Sys_struct decode_sys_msg(const std::string& serialized_data);
Info_struct decode_info_msg(const std::string& serialized_data);
Motors_struct decode_motors_msg(const std::string& serialized_data);
Tx_struct decode_tx_msg(const std::string& serialized_data);
Freq_struct decode_freq_msg(const std::string& serialized_data);
Sample_struct decode_sample_msg(const std::string& serialized_data);
Rssi_struct decode_rssi_msg(const std::string& serialized_data);




