from datetime import datetime
from classify import classify_behavior


def generate_fingerprint(url, features):
    """Saari information ko ek JSON mein pack karna"""

    proto = features.get("protocol_distribution", {})
    top_protocol = max(proto, key=proto.get) if proto else "Unknown"

    label, confidence = classify_behavior(url, features)

    return {
        "site_url": url,
        "capture_timestamp": datetime.now().isoformat(),
        "total_packets": features["total_packets"],
        "total_bytes": features["total_bytes"],
        "top_protocol": top_protocol,
        "unique_ips": features["unique_ips"],
        "dns_queries": features["dns_queries"],
        "mean_packet_size": features["mean_packet_size"],
        "max_packet_size": features["max_packet_size"],
        "protocol_distribution": features["protocol_distribution"],
        "size_histogram": features["size_histogram"],
        "timeline": features["timeline"],
        "behavior_label": label,
        "confidence": confidence,
    }
