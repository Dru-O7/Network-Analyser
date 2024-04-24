# for testing features before adding them to main.py
import sys
from scapy.all import *
import pandas as pd
from tqdm import tqdm
import socket

def read_pcap(pcap_file):
    try:
        packets = rdpcap(pcap_file)
    except FileNotFoundError:
        print(f"PCAP file not found: {pcap_file}")
        sys.exit(1)
    except Scapy_Exception as e:
        print(f"Error reading PCAP file: {e}")
        sys.exit(1)
    return packets

def extract_packet_data(packets):
    packet_data = []

    for packet in tqdm(packets, desc="Processing packets", unit="packet"):
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            protocol = packet[IP].proto
            size = len(packet)

            # Resolve domain names from IP addresses
            try:
                src_domain = socket.gethostbyaddr(src_ip)[0]
            except socket.herror:
                src_domain = "Unknown"

            try:
                dst_domain = socket.gethostbyaddr(dst_ip)[0]
            except socket.herror:
                dst_domain = "Unknown"

            packet_data.append({"src_ip": src_ip, "src_domain": src_domain, "dst_ip": dst_ip, "dst_domain": dst_domain, "protocol": protocol, "size": size})

    return pd.DataFrame(packet_data)

def extract_dns_requests(packets):
    dns_requests = []

    for packet in tqdm(packets, desc="Extracting DNS Requests", unit="packet"):
        if DNS in packet and packet[DNS].qr == 0:  # Check if DNS packet is a request
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            query = packet[DNS].qd.qname.decode('utf-8').rstrip('.')  # Remove trailing dot from domain name
            dns_requests.append({"Source IP": src_ip, "Destination IP": dst_ip, "Query": query})

    return pd.DataFrame(dns_requests)

# Main Function
def main(pcap_file):
    packets = read_pcap(pcap_file)
    df = extract_packet_data(packets)
    dns_requests_df = extract_dns_requests(packets)

    # Save to CSV
    dns_requests_df.to_csv('dns_requests.csv', index=False)

# Command Line Argument Parsing
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <pcap_file>")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    main(pcap_file)
