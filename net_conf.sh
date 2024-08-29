#!/bin/bash

# Update and install necessary packages
sudo apt update
sudo apt install -y hostapd dnsmasq iptables

# Stop services to configure them
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Configure the static IP for wlan0
sudo cat <<EOF > /etc/dhcpcd.conf
interface wlan0
    static ip_address=192.168.2.2/24
    nohook wpa_supplicant
EOF

# Restart dhcpcd
sudo systemctl restart dhcpcd

# Configure dnsmasq
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo cat <<EOF > /etc/dnsmasq.conf
interface=wlan0
  dhcp-range=192.168.2.10,192.168.2.100,255.255.255.0,24h
EOF

# Configure hostapd
sudo cat <<EOF > /etc/hostapd/hostapd.conf
interface=wlan0
driver=nl80211
ssid=CL_ANTPATTERN
hw_mode=g
channel=6
ieee80211n=1
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=CaribouAntenna4321
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF

# Edit /etc/default/hostapd to point to the config file
sudo sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

# Enable IP forwarding
sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sudo sysctl -p

# Set up NAT using iptables
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Configure the system to restore iptables rules on boot
sudo cat <<EOF > /etc/rc.local
#!/bin/sh -e
iptables-restore < /etc/iptables.ipv4.nat
exit 0
EOF

# Enable and start services
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
sudo systemctl restart dnsmasq

echo "Access Point Setup Complete!"
echo "SSID: RPi_AP"
echo "Gateway: 192.168.2.0"
