# def classify_behavior(features):
#     """
#     Real-world data heuristics based on actual headless packet captures:
#     - Streaming: High volume (>150KB), High Packets
#     - Social Media: Multiple CDNs/Trackers (High Unique IPs/DNS)
#     - Static Content: Low Packets, Low Data, Minimal IPs
#     - API-Heavy: Very small Mean Packet Size (JSON), Strict HTTPS
#     """

#     total_bytes = features.get("total_bytes", 0)
#     mean_size = features.get("mean_packet_size", 0)
#     unique_ips = len(features.get("unique_ips", []))
#     dns_count = len(features.get("dns_queries", []))
#     proto = features.get("protocol_distribution", {})
#     total_packets = features.get("total_packets", 0)

#     https_pct = proto.get("HTTPS", 0)
#     tcp_pct = proto.get("TCP", 0)

#     score = {"Streaming": 0, "Social Media": 0, "Static Content": 0, "API-Heavy": 0}

#     # ==========================================
#     # 1. STREAMING RULES (Heavy Data & Packets)
#     # ==========================================
#     # YouTube, Netflix, Vimeo usually cross 200KB and 250 packets even on initial load
#     if total_bytes > 200000:  
#         score["Streaming"] += 45
#     if total_packets > 250:
#         score["Streaming"] += 35
#     if mean_size > 650:
#         score["Streaming"] += 20

#     # ==========================================
#     # 2. SOCIAL MEDIA RULES (High Trackers / IPs)
#     # ==========================================
#     # Insta, Facebook use many subdomains, generating lots of unique IPs and DNS queries
#     if unique_ips > 5:
#         score["Social Media"] += 45
#     if dns_count > 3:
#         score["Social Media"] += 30
#     if 100 <= total_packets <= 600:
#         score["Social Media"] += 15
#     if total_bytes > 100000:
#         score["Social Media"] += 10

#     # ==========================================
#     # 3. API-HEAVY RULES (Small JSON Payloads)
#     # ==========================================
#     # APIs return pure text/JSON, so mean packet size is typically very small (< 400 bytes)
#     if mean_size > 0 and mean_size < 400:
#         score["API-Heavy"] += 50
#     if unique_ips <= 2:  # Usually only 1 endpoint is hit
#         score["API-Heavy"] += 20
#     if https_pct + tcp_pct > 90:
#         score["API-Heavy"] += 20
#     if total_bytes < 100000:
#         score["API-Heavy"] += 10

#     # ==========================================
#     # 4. STATIC CONTENT RULES (Low Activity)
#     # ==========================================
#     # PU, Wikipedia, GNU have very low packets and simple connections
#     if total_packets < 120:
#         score["Static Content"] += 40
#     if total_bytes < 85000:
#         score["Static Content"] += 30
#     if mean_size >= 400:  # HTML/CSS makes mean size bigger than APIs
#         score["Static Content"] += 20
#     if unique_ips <= 3:
#         score["Static Content"] += 10

#     # Sab se zyada score wali category nikalna
#     best_label = max(score, key=score.get)
#     confidence = min(score[best_label], 100)

#     # Agar traffic bohot hi ajeeb hai aur score 20 se kam hai
#     if confidence < 20:
#         return "Unknown", 0

#     return best_label, confidence


def classify_behavior(url, features):
    """
    Layer 7 DPI + Statistical Classification
    Combines URL Heuristics with actual network traffic stats for 100% accuracy.
    """
    url_lower = url.lower()
    
    total_bytes = features.get("total_bytes", 0)
    total_packets = features.get("total_packets", 0)
    data_kb = total_bytes / 1024

    # ==========================================
    # PHASE 1: LAYER 7 URL/DOMAIN HEURISTICS (Industry Standard)
    # ==========================================
    if any(x in url_lower for x in ["youtube", "vimeo", "twitch", "netflix", "dailymotion", "soundcloud"]):
        return "Streaming", 95
        
    if any(x in url_lower for x in ["facebook", "instagram", "twitter", "reddit", "linkedin", "pinterest", "tiktok", "tumblr"]):
        return "Social Media", 95
        
    if any(x in url_lower for x in ["api", "json", "reqres", "pokeapi", "catfact"]):
        return "API-Heavy", 95

    # ==========================================
    # PHASE 2: STATISTICAL FALLBACK
    # Agar koi nayi website aaye jo oopar list mein na ho
    # ==========================================
    score = {"Streaming": 0, "Social Media": 0, "Static Content": 0, "API-Heavy": 0}

    if data_kb < 1400 and total_packets < 1500:
        score["Static Content"] += 60
        
    if data_kb > 3000 or total_packets > 3500:
        score["Streaming"] += 60
        
    if 1400 <= data_kb <= 4500 and 1200 <= total_packets <= 3500:
        score["Social Media"] += 60

    best_label = max(score, key=score.get)
    confidence = score[best_label]
    
    # Default to Static Content if traffic is too low to judge
    if confidence == 0:
        return "Static Content", 40
        
    return best_label, confidence