#include <iostream>
#include <string>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>


class UDPcommunicator
{
public:
    UDPcommunicator();
    UDPcommunicator(int recv_port);
    ~UDPcommunicator();
    void init(int recv_port);
    void send_msg(const std::string &data);
    void recv_msg();
    std::string get_data();
private:
    int sockfd;
    struct timeval tv;
    struct sockaddr_in serverAddr;
    struct sockaddr_in clientAddr;
    std::string recv_data;
};
