import requests
# import time
import sys

BASE_URL = "http://localhost:5000"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def check_server():
    """Check if Flask server is actually running before starting tests"""
    try:
        requests.get(BASE_URL, timeout=2)
        return True
    except Exception:
        return False

# ==========================================
# BULK TEST DATA
# ==========================================
TEST_SITES = {
    "Streaming": [
        "https://www.youtube.com", 
        "https://vimeo.com", 
        "https://www.twitch.tv"
    ],
    "Social Media": [
        "https://www.facebook.com", 
        "https://www.instagram.com", 
        "https://www.reddit.com"
    ],
    "Static Content": [
        "https://en.wikipedia.org", 
        "https://www.pu.edu.pk", 
        "https://www.example.com"
    ],
    "API-Heavy": [
        "https://api.github.com", 
        "https://jsonplaceholder.typicode.com", 
        "https://catfact.ninja"
    ]
}

print(f"\n{CYAN}========================================================================{RESET}")
print(f"{CYAN}       NetScan Bulk Classification Tester (Detailed Analytics)          {RESET}")
print(f"{CYAN}========================================================================{RESET}")

if not check_server():
    print(f"{RED}[CRITICAL ERROR] Flask server is NOT running!{RESET}")
    print(f"{YELLOW}Please run 'python backend/app.py' in another terminal first.{RESET}")
    sys.exit()

total_urls = sum(len(urls) for urls in TEST_SITES.values())
print(f"Total websites to test: {total_urls}")
print(f"{YELLOW}Each test takes ~12s. Analyzing packets, bytes, MPS, and IPs...{RESET}\n")

passed_bulk_tests = 0
total_bulk_tests = 0

for expected_category, urls in TEST_SITES.items():
    print(f"\n{YELLOW}--- Expected Category: {expected_category} ---{RESET}")
    
    for url in urls:
        total_bulk_tests += 1
        clean_url = url.replace('https://', '').replace('www.', '')
        
        # Terminal formatting setup
        print(f"Scanning {clean_url:<20}...", end=" ", flush=True)
        
        try:
            res = requests.post(f"{BASE_URL}/api/analyze", json={"url": url}, timeout=45)
            
            if res.status_code == 200:
                data = res.json()
                
                # Extracting ALL important features
                predicted = data.get("behavior_label", "Unknown")
                conf = data.get("confidence", 0)
                pkts = data.get("total_packets", 0)
                bytes_kb = data.get("total_bytes", 0) / 1024
                mps = data.get("mean_packet_size", 0)
                
                # Handle unique IPs (it might be a list or a count depending on frontend JSON)
                ips_data = data.get("unique_ips", [])
                ips = len(ips_data) if isinstance(ips_data, list) else ips_data
                
                # Detailed stats string
                stats_info = f"Pkts: {pkts:<4} | Data: {bytes_kb:>6.1f} KB | MPS: {mps:>4} B | IPs: {ips:<2}"
                
                if predicted == expected_category:
                    passed_bulk_tests += 1
                    print(f"\n  {GREEN}➔ [MATCH]{RESET} Pred: {predicted} ({conf}%)")
                    print(f"    {CYAN}↳ Stats:{RESET} {stats_info}")
                else:
                    print(f"\n  {RED}➔ [MISMATCH]{RESET} Pred: {predicted} ({conf}%) | Expected: {expected_category}")
                    print(f"    {CYAN}↳ Stats:{RESET} {stats_info}")
            else:
                error_msg = res.json().get('error', 'Unknown Error')
                print(f"\n  {RED}➔ [API ERROR]{RESET} {res.status_code}: {error_msg}")
                
        except requests.exceptions.Timeout:
            print(f"\n  {RED}➔ [TIMEOUT]{RESET} Server took too long to respond.")
        except Exception as e:
            print(f"\n  {RED}➔ [CRASH]{RESET} Connection refused. Error: {str(e)[:30]}")

# Final Results
print(f"\n{CYAN}========================================================================{RESET}")
accuracy = (passed_bulk_tests / total_bulk_tests) * 100
color = GREEN if accuracy > 75 else YELLOW
print(f"Final Accuracy: {color}{passed_bulk_tests}/{total_bulk_tests} ({accuracy:.1f}%){RESET}")
print(f"{CYAN}========================================================================{RESET}")