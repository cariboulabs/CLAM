#include "UDPcommunicator.hpp"

UDPcommunicator::UDPcommunicator()
{
    int recv_port=5555;
    this->init(recv_port);
}
UDPcommunicator::UDPcommunicator(int recv_port)
{
    this->init(recv_port);
}


void UDPcommunicator::send_msg(const std::string &data)
{
    if (std::string(inet_ntoa(this->clientAddr.sin_addr)) == "0.0.0.0") 
    {
        return;
    }
    socklen_t clientAddrLen = sizeof(this->clientAddr);
    ssize_t sentBytes = sendto(this->sockfd, data.c_str(), data.size(), 0, (struct sockaddr *)&this->clientAddr, clientAddrLen);
    if (sentBytes < 0) 
    {
        std::cerr << "Failed to send data" << std::endl;
    }
}

void UDPcommunicator::recv_msg()
{
    char buffer[1024];
    socklen_t clientAddrLen = sizeof(this->clientAddr);
    ssize_t receivedBytes = recvfrom(this->sockfd, buffer, 1024, 0, (struct sockaddr *)&this->clientAddr, &clientAddrLen);
    if (receivedBytes < 0)
    {
        std::cerr << "Didn't receive any data from ControlPC\n" << std::endl;
        this->recv_data = "Expired";
    }
    else this->recv_data = std::string(buffer, receivedBytes);
}

std::string UDPcommunicator::get_data()
{
    return this->recv_data;
}

UDPcommunicator::~UDPcommunicator()
{
    std::cout << "Clear comm" << std::endl;
    close(this->sockfd);
}

void UDPcommunicator::init(int recv_port)
{
    this->recv_data = "";
    memset(&this->clientAddr, 0, sizeof(clientAddr));
    this->sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (this->sockfd < 0)
    {
        std::cerr << "Failed to create socket" << std::endl;
        return;
    }
    this->tv.tv_sec = 4;
    this->tv.tv_usec = 0;
    setsockopt(this->sockfd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&this->tv, sizeof(this->tv));
    // Set socket option to allow broadcast
    int broadcast_enable = 1;
    if (setsockopt(this->sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast_enable, sizeof(broadcast_enable)) < 0)
    {
        perror("Failed to set SO_BROADCAST option");
        exit(EXIT_FAILURE);
    }
    memset(&this->serverAddr, 0, sizeof(this->serverAddr));
    this->serverAddr.sin_family = AF_INET;
    this->serverAddr.sin_addr.s_addr = INADDR_ANY; // Bind to any available address
    this->serverAddr.sin_port = htons(recv_port);
    if (bind(this->sockfd, (struct sockaddr *)&this->serverAddr, sizeof(this->serverAddr)) < 0)
    {
        std::cerr << "Failed to bind socket" << std::endl;
        close(this->sockfd);
        return;
    }
}
