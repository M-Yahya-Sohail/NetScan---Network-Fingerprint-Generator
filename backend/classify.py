# # def classify_behavior(url, features):
# #     """
# #     Layer 7 DPI + Statistical Classification
# #     Combines URL Heuristics with actual network traffic stats for 100% accuracy.
# #     """
# #     url_lower = url.lower()
    
# #     total_bytes = features.get("total_bytes", 0)
# #     total_packets = features.get("total_packets", 0)
# #     data_kb = total_bytes / 1024

# #     # ==========================================
# #     # PHASE 1: LAYER 7 URL/DOMAIN HEURISTICS (Industry Standard)
# #     # ==========================================
# #     if(True):
# #         if any(x in url_lower for x in ["youtube", "vimeo", "twitch", "netflix", "dailymotion", "soundcloud"]):
# #             pass
# #     #         return "Streaming", 95
            
# #     #     if any(x in url_lower for x in ["facebook", "instagram", "twitter", "reddit", "linkedin", "pinterest", "tiktok", "tumblr"]):
# #     #         return "Social Media", 95
            
# #     #     if any(x in url_lower for x in ["api", "json", "reqres", "pokeapi", "catfact"]):
# #     #         return "API-Heavy", 95

# #     # ==========================================
# #     # PHASE 2: STATISTICAL FALLBACK
# #     # Agar koi nayi website aaye jo oopar list mein na ho
# #     # ==========================================
# #     score = {"Streaming": 0, "Social Media": 0, "Static Content": 0, "API-Heavy": 0}

# #     if data_kb < 1400 and total_packets < 1500:
# #         score["Static Content"] += 60
        
# #     if data_kb > 3000 or total_packets > 3500:
# #         score["Streaming"] += 60
        
# #     if 1400 <= data_kb <= 4500 and 1200 <= total_packets <= 3500:
# #         score["Social Media"] += 60

# #     best_label = max(score, key=score.get)
# #     confidence = score[best_label]
    
# #     # Default to Static Content if traffic is too low to judge
# #     if confidence == 0:
# #         return "Static Content", 40
        
# #     return best_label, confidence


def classify_behavior(url, features):
    """
    Network-Adaptive Statistical Classifier (V2).
    Uses Ratios (Mean Packet Size) which don't break when network speed changes.
    """
    total_bytes = features.get("total_bytes", 0)
    total_packets = features.get("total_packets", 0)
    data_kb = total_bytes / 1024
    
    # RATIO: Yeh network speed par depend nahi karta!
    mps = total_bytes / total_packets if total_packets > 0 else 0

    score = {"Streaming": 0, "Social Media": 0, "Static Content": 0, "API-Heavy": 0}

    # ==========================================
    # ADAPTIVE STATISTICAL THRESHOLDS
    # ==========================================

    # 1. Streaming Check: Packet size is huge (Video chunks) regardless of slow/fast net
    if mps > 800 or data_kb > 2000:
        score["Streaming"] += 60
        
    # 2. Social Media Check: Medium sized packets, continuous flow
    if 400 < mps <= 800 and total_packets > 300:
        score["Social Media"] += 60

    # 3. API-Heavy: Very small packets (JSON text), usually under 400 bytes
    if mps < 400 and total_packets > 50:
        score["API-Heavy"] += 60

    # 4. Static Content Check: Barely any traffic
    if data_kb < 500 and total_packets < 200:
        score["Static Content"] += 60

    best_label = max(score, key=score.get)
    confidence = score[best_label]
    
    if confidence == 0:
        return "Static Content", 40
        
    return best_label, confidence