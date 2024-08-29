#include "RxMeas.hpp"
#include <csignal>
#include <unistd.h>


static RxMeas* rxm_ptr = nullptr;
void signalHandler(int signum)
{
    if (rxm_ptr)
    {
        rxm_ptr->sig_msg();
        rxm_ptr->stop_recv_loop();
        while(true)
        {   
            if(!rxm_ptr->get_status())
            {
                rxm_ptr->stop();
                break;
            }
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }
    exit(signum);
}

int main()
{
    
    signal(SIGINT, signalHandler);
    RxMeas rxm(5555, 900000000);
    rxm_ptr = &rxm;
    signal(SIGINT, signalHandler);
    while(true)
    {   
        if(!rxm.get_status())
        {
            rxm.stop();
            break;
        }
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    return 0;
}

    
