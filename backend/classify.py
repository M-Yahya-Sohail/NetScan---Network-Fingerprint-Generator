def classify_behavior(features):
    """
    Rules ke basis pe website ka type identify karna:
    - Streaming: YouTube jaise
    - Social Media: Facebook jaise
    - Static Content: Simple news page
    - API-Heavy: REST API wali sites
    """

    total_bytes = features.get("total_bytes", 0)
    mean_size = features.get("mean_packet_size", 0)
    unique_ips = len(features.get("unique_ips", []))
    proto = features.get("protocol_distribution", {})
    total_packets = features.get("total_packets", 0)

    https_pct = proto.get("HTTPS", 0)
    tcp_pct = proto.get("TCP", 0)

    score = {"Streaming": 0, "Social Media": 0, "Static Content": 0, "API-Heavy": 0}

    # Streaming rules
    if total_bytes > 500000:
        score["Streaming"] += 30
    if mean_size > 1000:
        score["Streaming"] += 30
    if tcp_pct + https_pct > 80:
        score["Streaming"] += 20
    if total_packets > 500:
        score["Streaming"] += 20

    # Social Media rules
    if unique_ips > 10:
        score["Social Media"] += 35
    if mean_size < 500:
        score["Social Media"] += 25
    if len(features.get("dns_queries", [])) > 5:
        score["Social Media"] += 20
    if total_packets > 200:
        score["Social Media"] += 20

    # Static Content rules
    if total_packets < 50:
        score["Static Content"] += 40
    if total_bytes < 50000:
        score["Static Content"] += 30
    if len(features.get("dns_queries", [])) < 3:
        score["Static Content"] += 30

    # API-Heavy rules
    if mean_size < 300:
        score["API-Heavy"] += 30
    if https_pct > 90:
        score["API-Heavy"] += 35
    if total_packets > 100 and total_bytes < 200000:
        score["API-Heavy"] += 35

    best_label = max(score, key=score.get)
    confidence = min(score[best_label], 100)

    if confidence < 20:
        return "Unknown", 0

    return best_label, confidence
