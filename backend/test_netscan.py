import requests
import time

BASE_URL = "http://localhost:5000"

# Terminal ko khoobsurat aur readable banane ke liye ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_result(test_name, passed, details=""):
    if passed:
        print(f"{GREEN}[PASS]{RESET} {test_name} {details}")
    else:
        print(f"{RED}[FAIL]{RESET} {test_name} {details}")

print(f"{CYAN}===================================================={RESET}")
print(f"{CYAN}   NetScan Automated Worst-Case Tester (API V1)   {RESET}")
print(f"{CYAN}===================================================={RESET}")
print(f"{YELLOW}Note: Har valid network test mein ~10-12 seconds lagenge (Packet Capture Window)...{RESET}\n")

# ==========================================
# TEST 1: The "Dumb User" Test (Missing Scheme)
# ==========================================
print("Running Test 1: Missing 'http://' Scheme...")
res = requests.post(f"{BASE_URL}/api/analyze", json={"url": "google.com"})
if res.status_code == 400 and "Error" in res.json():
    print_result("Missing Scheme Test", True, "-> Backend blocked invalid URL properly.")
else:
    print_result("Missing Scheme Test", False, f"-> Expected 400, got {res.status_code}")

# ==========================================
# TEST 2: The "Dead End" Test (Fake Domain)
# ==========================================
print("\nRunning Test 2: Fake Domain / DNS Failure...")
res = requests.post(f"{BASE_URL}/api/analyze", json={"url": "https://thiswebsitedoesnotexist12345.com"})
if res.status_code == 500:
    print_result("Dead Domain Test", True, "-> Backend caught the failure and returned 500 Server Error.")
else:
    print_result("Dead Domain Test", False, f"-> Expected 500, got {res.status_code}")

# ==========================================
# TEST 3: The "Happy Path" (Valid Single URL)
# ==========================================
print("\nRunning Test 3: Valid Single URL (https://pu.edu.pk) [Capturing for 10s]...")
start_time = time.time()
res = requests.post(f"{BASE_URL}/api/analyze", json={"url": "https://pu.edu.pk"})
elapsed = time.time() - start_time

if res.status_code == 200 and "behavior_label" in res.json():
    data = res.json()
    details = f"-> Captured {data['total_packets']} packets in {elapsed:.1f}s. Classified as: {data['behavior_label']}"
    print_result("Valid Single URL Test", True, details)
else:
    print_result("Valid Single URL Test", False, f"-> Failed with status {res.status_code}")

# ==========================================
# TEST 4: The "Impatient User" Test (Missing Compare Input)
# ==========================================
print("\nRunning Test 4: Missing URLs in Compare Mode...")
res = requests.post(f"{BASE_URL}/api/compare", json={"url1": "https://google.com", "url2": ""})
if res.status_code == 400 and "error" in res.json():
    print_result("Missing Compare Input Test", True, "-> Backend blocked empty comparison properly.")
else:
    print_result("Missing Compare Input Test", False, f"-> Expected 400, got {res.status_code}")

# ==========================================
# TEST 5: The Ultimate Comparison (Valid A/B Test)
# ==========================================
print("\nRunning Test 5: Compare Mode (Google vs Wikipedia) [Capturing for ~20s]...")
start_time = time.time()
res = requests.post(f"{BASE_URL}/api/compare", json={
    "url1": "https://google.com", 
    "url2": "https://wikipedia.org"
})
elapsed = time.time() - start_time

if res.status_code == 200 and "diff" in res.json():
    diff = res.json()["diff"]
    details = f"-> Completed in {elapsed:.1f}s. Larger packets sent by: {diff['larger_packets']}"
    print_result("Compare Mode Test", True, details)
else:
    print_result("Compare Mode Test", False, f"-> Failed with status {res.status_code}")

print(f"\n{CYAN}===================================================={RESET}")
print(f"{GREEN}Testing Completed! Evaluation Ready!{RESET}")


# ==========================================
# TEST 6: Bulk Classification / Worst-Case Accuracy Test (Large Data)
# ==========================================
print(f"\n{CYAN}===================================================={RESET}")
print(f"{CYAN}   NetScan Bulk Classification Tester (Stress Test) {RESET}")
print(f"{CYAN}===================================================={RESET}")

TEST_SITES = {
    "Streaming": [
        "https://www.youtube.com", 
        "https://vimeo.com", 
        "https://www.twitch.tv",
        "https://www.netflix.com", 
        "https://www.dailymotion.com", 
        "https://soundcloud.com"
    ],
    "Social Media": [
        "https://www.facebook.com", 
        "https://www.instagram.com", 
        "https://twitter.com",
        "https://www.reddit.com", 
        "https://www.linkedin.com", 
        "https://www.pinterest.com",
        "https://www.tiktok.com", 
        "https://www.tumblr.com"
    ],
    "Static Content": [
        "https://en.wikipedia.org", 
        "https://www.pu.edu.pk", 
        "https://www.example.com",
        "https://www.gnu.org", 
        "https://www.w3.org", 
        "https://info.cern.ch"
    ],
    "API-Heavy": [
        "https://api.github.com", 
        "https://jsonplaceholder.typicode.com", 
        "https://reqres.in", 
        "https://dummyjson.com", 
        "https://pokeapi.co",
        "https://catfact.ninja"
    ]
}

total_urls = sum(len(urls) for urls in TEST_SITES.values())
print(f"Total websites to test: {total_urls}")
print(f"{YELLOW}Warning: Bulk testing mein {total_urls * 10} seconds lag sakte hain...{RESET}\n")

passed_bulk_tests = 0
total_bulk_tests = 0

for expected_category, urls in TEST_SITES.items():
    print(f"\n{YELLOW}--- Testing Expected Category: {expected_category} ---{RESET}")
    
    for url in urls:
        total_bulk_tests += 1
        print(f"Scanning {url} ... ", end="", flush=True)
        
        try:
            start_bulk = time.time()
            res = requests.post(f"{BASE_URL}/api/analyze", json={"url": url}, timeout=20)
            elapsed_bulk = time.time() - start_bulk
            
            if res.status_code == 200 and "behavior_label" in res.json():
                data = res.json()
                predicted_label = data.get("behavior_label", "Error")
                confidence = data.get("confidence", 0)
                packets = data.get("total_packets", 0)
                bytes_kb = data.get("total_bytes", 0) / 1024
                
                if predicted_label == expected_category:
                    passed_bulk_tests += 1
                    print(f"{GREEN}[MATCH]{RESET} Predicted: {predicted_label} ({confidence}%) | Pkts: {packets} | {bytes_kb:.1f} KB")
                else:
                    print(f"{RED}[FAIL]{RESET} Predicted: {predicted_label} ({confidence}%) | Expected: {expected_category} | Pkts: {packets} | {bytes_kb:.1f} KB")
            else:
                print(f"{RED}[ERROR]{RESET} API returned HTTP {res.status_code}")
                
        except Exception as e:
            print(f"{RED}[CRASH]{RESET} {str(e)}")

print(f"\n{CYAN}===================================================={RESET}")
print(f"Final Bulk Accuracy: {passed_bulk_tests}/{total_bulk_tests} ({(passed_bulk_tests/total_bulk_tests)*100:.1f}%)")
print(f"{CYAN}===================================================={RESET}")
print(f"{GREEN}All Automated & Bulk Tests Completed!{RESET}")