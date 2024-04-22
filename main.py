
# Imports
import sys
import os
import logging
from scapy.all import *
import pandas as pd
from tabulate import tabulate
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import socket
import networkx as nx

if not os.path.exists('public/graphs'):
    os.makedirs('public/graphs')


# Global Variables and Constants
DEFAULT_PORT_SCAN_THRESHOLD = 100

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Helper Functions
def protocol_name(number):
    protocol_dict = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
    return protocol_dict.get(number, f"Unknown({number})")

# Main Functions
def read_pcap(pcap_file):
    try:
        packets = rdpcap(pcap_file)
    except FileNotFoundError:
        logger.error(f"PCAP file not found: {pcap_file}")
        sys.exit(1)
    except Scapy_Exception as e:
        logger.error(f"Error reading PCAP file: {e}")
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

def analyze_packet_data(df):
    total_bandwidth = df["size"].sum()
    protocol_counts = df["protocol"].value_counts(normalize=True) * 100
    protocol_counts.index = protocol_counts.index.map(protocol_name)

    ip_communication = df.groupby(["src_ip", "dst_ip"]).size().sort_values(ascending=False)
    ip_communication_percentage = ip_communication / ip_communication.sum() * 100
    ip_communication_table = pd.concat([ip_communication, ip_communication_percentage], axis=1).reset_index()

    protocol_frequency = df["protocol"].value_counts()
    protocol_frequency.index = protocol_frequency.index.map(protocol_name)

    protocol_counts_df = pd.concat([protocol_frequency, protocol_counts], axis=1).reset_index()
    protocol_counts_df.columns = ["Protocol", "Count", "Percentage"]

    ip_communication_protocols = df.groupby(["src_ip", "dst_ip", "protocol"]).size().reset_index()
    ip_communication_protocols.columns = ["Source IP", "Destination IP", "Protocol", "Count"]
    ip_communication_protocols["Protocol"] = ip_communication_protocols["Protocol"].apply(protocol_name)


    ip_communication_protocols["Percentage"] = ip_communication_protocols.groupby(["Source IP", "Destination IP"])["Count"].transform(lambda x: x / x.sum() * 100)

    return total_bandwidth, protocol_counts_df, ip_communication_table, protocol_frequency, ip_communication_protocols

def extract_packet_data_security(packets):
    packet_data = []

    for packet in tqdm(packets, desc="Processing packets for port scanning activity", unit="packet"):
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            protocol = packet[IP].proto
            size = len(packet)

            if TCP in packet:
                dst_port = packet[TCP].dport
            else:
                dst_port = 0

            packet_data.append({"Source IP": src_ip, "Destination IP": dst_ip, "Protocol": protocol, "Size": size, "dst_port": dst_port})

    return pd.DataFrame(packet_data)

def detect_port_scanning(df, port_scan_threshold):
    port_scan_df = df.groupby(['Source IP', 'dst_port']).size().reset_index(name='count')
    
    # Count the unique ports for each source IP
    unique_ports_per_ip = port_scan_df.groupby('Source IP').size().reset_index(name='unique_ports')
    
    potential_port_scanners = unique_ports_per_ip[unique_ports_per_ip['unique_ports'] >= port_scan_threshold]
    ip_addresses = potential_port_scanners['Source IP'].unique()
    
    if len(ip_addresses) > 0:
        logger.warning(f"Potential port scanning detected from IP addresses: {', '.join(ip_addresses)}")


def format_results_as_html(total_bandwidth, protocol_counts_df, ip_communication_table, ip_communication_protocols):
    html = ""

    if total_bandwidth < 10**9:
        bandwidth_unit = "Mbps"
        total_bandwidth /= 10**6
    else:
        bandwidth_unit = "Gbps"
        total_bandwidth /= 10**9

    html += f"<p>Total bandwidth used: {total_bandwidth:.2f} {bandwidth_unit}</p>"

    html += "<h3>Protocol Distribution:</h3>"
    html += protocol_counts_df.to_html(index=False)

    html += "<h3>Top IP Address Communications:</h3>"
    html += ip_communication_table.to_html(index=False)

    html += "<h3>Share of each protocol between IPs:</h3>"
    html += ip_communication_protocols.to_html(index=False)

    return html


def plot_all_graphs(protocol_counts, ip_communication_protocols):
    plot_protocol_percentage(protocol_counts)
    plot_share_of_protocols_between_ips(ip_communication_protocols)

def plot_share_of_protocols_between_ips(ip_communication_protocols):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Group by source and destination IP addresses and sum the percentage for each protocol
    grouped = ip_communication_protocols.groupby(["Source IP", "Destination IP", "Protocol"])["Percentage"].sum().unstack()

    # Plot stacked bar chart
    grouped.plot(kind='bar', stacked=True, ax=ax)

    ax.set_ylabel("Percentage of Communication")
    ax.set_xlabel("Source and Destination IP Addresses")
    ax.set_title("Share of Each Protocol Between IPs")
    plt.legend(title="Protocol")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the plot as an image in the 'public' directory
    plt.savefig('public/graphs/share_of_protocols_between_ips.png')
    plt.close()

def plot_protocol_percentage(protocol_counts):
    fig, ax = plt.subplots(figsize=(8, 8))
    protocol_counts["Percentage"].plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax)
    ax.set_ylabel("")
    ax.set_title("Distribution of Protocols")
    plt.tight_layout()
    
    # Save the plot as an image in the 'graphs' directory
    plt.savefig('public/graphs/protocol_percentage.png')
    plt.close()


# Main Functions
def main(pcap_file, port_scan_threshold, output_files):
    packets = read_pcap(pcap_file)
    df = extract_packet_data(packets)
    total_bandwidth, protocol_counts, ip_communication_table, protocol_frequency, ip_communication_protocols = analyze_packet_data(df)
    
    # Log the results
    logger.info(f"Total bandwidth used: {total_bandwidth:.2f} Mbps")

    # Save Protocol Distribution to CSV
    protocol_counts_csv = output_files[0]
    protocol_counts.to_csv(protocol_counts_csv, index=False)
    logger.info(f"Protocol Distribution saved to: {protocol_counts_csv}")

    # Save Top IP Address Communications to CSV
    ip_communication_table_csv = output_files[1]
    ip_communication_table.columns = ["Source IP", "Destination IP", "Count", "Percentage"]
    ip_communication_table.to_csv(ip_communication_table_csv, index=False)
    logger.info(f"Top IP Address Communications saved to: {ip_communication_table_csv}")


    # Save Share of each protocol between IPs to CSV
    ip_communication_protocols_csv = output_files[2]
    ip_communication_protocols.to_csv(ip_communication_protocols_csv, index=False)
    logger.info(f"Share of each protocol between IPs saved to: {ip_communication_protocols_csv}")

    df_security = extract_packet_data_security(packets)
    detect_port_scanning(df_security, port_scan_threshold)

    plot_protocol_percentage(protocol_counts)
    plot_share_of_protocols_between_ips(ip_communication_protocols)
    plot_all_graphs(protocol_counts, ip_communication_protocols)

# Command Line Argument Parsing
if __name__ == "__main__":
    if len(sys.argv) < 5:
        logger.error("Please provide the path to the PCAP file and output filenames for Protocol Distribution, Top IP Address Communications, and Share of each protocol between IPs.")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    output_files = sys.argv[2:5]
    
    default_port_scan_threshold = 100

    if len(sys.argv) >= 6:
        try:
            port_scan_threshold = int(sys.argv[5])
        except ValueError:
            logger.error("Invalid port_scan_threshold value. Using the default value.")
            port_scan_threshold = default_port_scan_threshold
    else:
        port_scan_threshold = default_port_scan_threshold
    
    main(pcap_file, port_scan_threshold, output_files)
