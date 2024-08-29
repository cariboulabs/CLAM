#include "ProtobufTransformer.hpp"

std::string encode_sys_msg(const std::string &whoami, const std::string &status)
{
    std::string serialized_data;
    Wrapper wrap_msg;
    wrap_msg.set_type(SYSTEM);
    System* sys_msg = wrap_msg.mutable_sys_msg();
    sys_msg->set_whoami(whoami);
    sys_msg->set_status(status);
    wrap_msg.SerializeToString(&serialized_data);
    return serialized_data;
}

std::string encode_info_msg(const std::string &info)
{
    std::string serialized_data;
    Wrapper wrap_msg;
    wrap_msg.set_type(INFORMATION);
    Information* info_msg = wrap_msg.mutable_info_msg();
    info_msg->set_info(info);
    wrap_msg.SerializeToString(&serialized_data);
    return serialized_data;
}

std::string encode_motors_msg(const float alpha, const float beta)
{
    std::string serialized_data;
    Wrapper wrap_msg;
    wrap_msg.set_type(MOTORS);
    Motors* motors_msg = wrap_msg.mutable_motors_msg();
    motors_msg->set_alpha(alpha);
    motors_msg->set_beta(beta);
    wrap_msg.SerializeToString(&serialized_data);
    return serialized_data;
}

std::string encode_tx_msg(const float freq, const float power, const std::string &wavetype, const bool onoff)
{
    std::string serialized_data;
    Wrapper wrap_msg;
    wrap_msg.set_type(TRANSMIT);
    Transmit* tx_msg = wrap_msg.mutable_tx_msg();
    tx_msg->set_frequency(freq);
    tx_msg->set_power(power);
    tx_msg->set_wavetype(wavetype);
    tx_msg->set_onoff(onoff);
    wrap_msg.SerializeToString(&serialized_data);
    return serialized_data;
}

std::string encode_freq_msg(const float freq)
{
    std::string serialized_data;
    Wrapper wrap_msg;
    wrap_msg.set_type(SET_FREQUENCY);
    SetFrequency* freq_msg = wrap_msg.mutable_freq_msg();
    freq_msg->set_frequency(freq);
    wrap_msg.SerializeToString(&serialized_data);
    return serialized_data;
}

std::string encode_sample_msg(const bool onoff)
{
    std::string serialized_data;
    Wrapper wrap_msg;
    wrap_msg.set_type(SAMPLING);
    Sampling* sample_msg = wrap_msg.mutable_sample_msg();
    sample_msg->set_onoff(onoff);
    wrap_msg.SerializeToString(&serialized_data);
    return serialized_data;
}

std::string encode_rssi_msg(const float rssi, const int samples, const float std)
{
    std::string serialized_data;
    Wrapper wrap_msg;
    wrap_msg.set_type(GET_RSSI);
    GetRssi* rssi_msg = wrap_msg.mutable_rssi_msg();
    rssi_msg->set_rssi(rssi);
    rssi_msg->set_samples(samples);
    rssi_msg->set_std(std);
    wrap_msg.SerializeToString(&serialized_data);
    return serialized_data;
}

int get_type(const std::string &serialized_data)
{
    Wrapper wrap_msg;
    wrap_msg.ParseFromString(serialized_data);
    return wrap_msg.type();
}

Sys_struct decode_sys_msg(const std::string &serialized_data)
{
    Sys_struct sys;
    Wrapper wrap_msg;
    wrap_msg.ParseFromString(serialized_data);
    const System& msg = wrap_msg.sys_msg();
    sys.whoami = msg.whoami();
    sys.status = msg.status();
    return sys;
}

Info_struct decode_info_msg(const std::string &serialized_data)
{
    Info_struct information;
    Wrapper wrap_msg;
    wrap_msg.ParseFromString(serialized_data);
    const Information& msg = wrap_msg.info_msg();
    information.info = msg.info();
    return information;
}

Motors_struct decode_motors_msg(const std::string &serialized_data)
{
    Motors_struct motors;
    Wrapper wrap_msg;
    wrap_msg.ParseFromString(serialized_data);
    const Motors& msg = wrap_msg.motors_msg();
    motors.alpha = msg.alpha();
    motors.beta = msg.beta();
    return motors;
}

Tx_struct decode_tx_msg(const std::string &serialized_data)
{
    Tx_struct tx;
    Wrapper wrap_msg;
    wrap_msg.ParseFromString(serialized_data);
    const Transmit& msg = wrap_msg.tx_msg();
    tx.freq = msg.frequency();
    tx.power = msg.power();
    tx.wavetype = msg.wavetype();
    tx.onoff = msg.onoff();
    return tx;
}

Freq_struct decode_freq_msg(const std::string &serialized_data)
{
    Freq_struct setfreq;
    Wrapper wrap_msg;
    wrap_msg.ParseFromString(serialized_data);
    const SetFrequency& msg = wrap_msg.freq_msg();
    setfreq.freq = msg.frequency();
    return setfreq;
}

Sample_struct decode_sample_msg(const std::string &serialized_data)
{
    Sample_struct sample;
    Wrapper wrap_msg;
    wrap_msg.ParseFromString(serialized_data);
    const Sampling& msg = wrap_msg.sample_msg();
    sample.onoff = msg.onoff();
    return sample;
}

Rssi_struct decode_rssi_msg(const std::string &serialized_data)
{
    Rssi_struct getrssi;
    Wrapper wrap_msg;
    wrap_msg.ParseFromString(serialized_data);
    const GetRssi& msg = wrap_msg.rssi_msg();
    getrssi.rssi = msg.rssi();
    getrssi.samples =  msg.samples();
    getrssi.std =  msg.std();
    return getrssi;
}
