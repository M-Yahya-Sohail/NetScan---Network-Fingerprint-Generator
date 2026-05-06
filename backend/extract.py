import scapy.all as scapy


def extract_features(packets):
    """Packets se saari information nikalna"""

    if not packets:
        return get_empty_features()

    sizes = []  # Har packet ka size
    protocols = {}  # Protocol counts
    dest_ips = set()  # Unique destination IPs
    dns_queries = []  # DNS requests
    timestamps = []  # Time of each packet

    for pkt in packets:
        # Size store karo
        sizes.append(len(pkt))
        timestamps.append(float(pkt.time))

        # Protocol identify karo
        if scapy.DNS in pkt:
            protocols["DNS"] = protocols.get("DNS", 0) + 1
            # DNS query naam nikalo
            if pkt[scapy.DNS].qd:
                dns_queries.append(pkt[scapy.DNS].qd.qname.decode())
        elif scapy.TCP in pkt:
            if pkt[scapy.TCP].dport == 443 or pkt[scapy.TCP].sport == 443:
                protocols["HTTPS"] = protocols.get("HTTPS", 0) + 1
            else:
                protocols["TCP"] = protocols.get("TCP", 0) + 1
        elif scapy.UDP in pkt:
            protocols["UDP"] = protocols.get("UDP", 0) + 1
        elif scapy.ICMP in pkt:
            protocols["ICMP"] = protocols.get("ICMP", 0) + 1

        # Destination IP nikalo
        if scapy.IP in pkt:
            dest_ips.add(pkt[scapy.IP].dst)

    # Protocol percentages calculate karo
    total = len(packets)
    protocol_dist = {k: round((v / total) * 100, 1) for k, v in protocols.items()}

    # Inter-arrival times (packets ke beech ka waqt)
    inter_arrivals = []
    for i in range(1, len(timestamps)):
        inter_arrivals.append(timestamps[i] - timestamps[i - 1])

    # Per-second traffic calculate karo (timeline ke liye)
    timeline = calculate_timeline(packets, timestamps)

    return {
        "total_packets": total,
        "total_bytes": sum(sizes),
        "packet_sizes": sizes,
        "mean_packet_size": round(sum(sizes) / len(sizes), 2),
        "min_packet_size": min(sizes),
        "max_packet_size": max(sizes),
        "protocol_distribution": protocol_dist,
        "unique_ips": list(dest_ips),
        "dns_queries": list(set(dns_queries)),  # Duplicates hata do
        "inter_arrival_times": inter_arrivals,
        "timeline": timeline,
        "size_histogram": calculate_histogram(sizes),
    }


def calculate_histogram(sizes):
    """Packet sizes ko buckets mein daalna"""
    buckets = {"0-100": 0, "101-500": 0, "501-1000": 0, "1001-1500": 0, "1500+": 0}
    for s in sizes:
        if s <= 100:
            buckets["0-100"] += 1
        elif s <= 500:
            buckets["101-500"] += 1
        elif s <= 1000:
            buckets["501-1000"] += 1
        elif s <= 1500:
            buckets["1001-1500"] += 1
        else:
            buckets["1500+"] += 1
    return buckets


def calculate_timeline(packets, timestamps):
    """Har second mein kitne bytes gaye"""
    if not timestamps:
        return []
    start = min(timestamps)
    timeline = {}
    for i, pkt in enumerate(packets):
        second = int(timestamps[i] - start)
        timeline[second] = timeline.get(second, 0) + len(pkt)
    # Sorted list return karo
    return [{"second": k, "bytes": v} for k, v in sorted(timeline.items())]


def get_empty_features():
    return {
        "total_packets": 0,
        "total_bytes": 0,
        "packet_sizes": [],
        "mean_packet_size": 0,
        "min_packet_size": 0,
        "max_packet_size": 0,
        "protocol_distribution": {},
        "unique_ips": [],
        "dns_queries": [],
        "inter_arrival_times": [],
        "timeline": [],
        "size_histogram": {},
    }
