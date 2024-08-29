#include "RxMeas.hpp"

RxMeas::RxMeas()
{
    this->init_params();
}

RxMeas::RxMeas(int recv_port, float freq) : comm(recv_port), sgr(freq)
{
    this->init_params();
}
void RxMeas::init_params()
{
    this->active = true;
    this->stop_looping = true;
    this->recv_thread = std::thread(&RxMeas::handle_recv_msg, this);
}
void RxMeas::handle_recv_msg()
{
    try
    {
        while(true)
        {
            this->comm.recv_msg();
            std::string ser_data = this->comm.get_data();
            if(!this->stop_looping)
            {
                this->active = false;
                break;
            }
            if(ser_data == "Expired") continue;
            int msg_type = get_type(ser_data);
            if(msg_type == SYSTEM)
            {
                Sys_struct sys_msg = decode_sys_msg(ser_data);
                std::string status = sys_msg.status;
                std::cout << "Whoami: " << sys_msg.whoami << " | Status: " << sys_msg.status << "\n" << std::endl;
                if(status == "Ready?")
                {
                    this->comm.send_msg(encode_sys_msg("RxMeas", "Ready"));
                }
                // else if (sys_msg.whoami == "RxMeas")
                // {
                //     break;
                // }
                else // Close RxMeas
                {
                    this->active = false;
                    this->comm.send_msg(encode_info_msg("Finished"));
                    break;
                }
            }
            else if(msg_type == SET_FREQUENCY)
            {
                Freq_struct freq_msg = decode_freq_msg(ser_data);
                try
                {
                    this->sgr.set_freq(freq_msg.freq);
                    this->comm.send_msg(encode_info_msg("Changed frequency"));
                }
                catch(...)
                {
                        this->comm.send_msg(encode_info_msg("Can't changed frequency, not in range"));
                }
            }
            else if(msg_type == SAMPLING)
            {
                Sample_struct sample_msg = decode_sample_msg(ser_data);
                try
                {
                    bool state = sample_msg.onoff;
                    if(state)
                    {
                        this->comm.send_msg(encode_info_msg("Started sampling"));
                        float stat_arr[3];

                        this->sgr.flusher();
                        this->sgr.getsamples(10, this->rssi_arr);
                        calc_statistical_data(this->rssi_arr, 10, stat_arr);
                        this->comm.send_msg(encode_rssi_msg(stat_arr[0], static_cast<int>(round(stat_arr[1])), stat_arr[2]));
                    }
                }
                catch(...)
                {
                    this->comm.send_msg(encode_info_msg("Can't control sampling"));
                }
            }
            else
            {
                this->comm.send_msg(encode_info_msg("Wrong data"));
            }
            //std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }
    catch(...)
    {
        std::cout << "Problem here" << std::endl;
    }
}

void RxMeas::stop()
{
    std::cout << "RXM stopped was called " << std::endl;
    this->recv_thread.join();

}

void RxMeas::stop_recv_loop()
{
    this->stop_looping = false;
}

bool RxMeas::get_status()
{
    return this->active;
}

void RxMeas::sig_msg()
{
    this->comm.send_msg(encode_sys_msg("RxMeas", "System disturbed"));
}


RxMeas::~RxMeas()
{
}
