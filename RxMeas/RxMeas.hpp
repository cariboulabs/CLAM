#include "UDPcommunicator.hpp"
#include "ProtobufTransformer.hpp"
#include "SignalRx.hpp"
#include "External.hpp"

class RxMeas
{
private:
    UDPcommunicator comm;
    SignalRx sgr;
    std::thread recv_thread;
    bool active;
    bool stop_looping;
    float rssi_arr[10];
    int idx;

public:
    //Ctors
    RxMeas();
    RxMeas(int recv_port, float freq);

    // Handle received messages
    void init_params();
    void handle_recv_msg();
    void stop();
    void stop_recv_loop();
    // Get activation status
    bool get_status();
    void sig_msg();
    // Dtor
    ~RxMeas();
};