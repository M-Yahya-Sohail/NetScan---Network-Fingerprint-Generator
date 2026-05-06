# import scapy.all as scapy
# import threading
# import requests
# import socket
# import time

# def get_ip(url):
#     """URL se IP address nikalna"""
#     try:
#         domain = url.replace("https://", "").replace("http://", "").split("/")[0]
#         return socket.gethostbyname(domain)
#     except Exception:
#         return None

# def capture_with_request(url, duration=10):
#     """Capture karo aur saath mein website ko request bhi bhejo"""
#     target_ip = get_ip(url)
#     if not target_ip:
#         raise ValueError("The specified domain does not exist or DNS resolution failed.!")
    
#     packets_result = []
    
#     # Direct object use kar rahe hain
#     try:
#         my_iface = scapy.IFACES.dev_from_index(13)
#     except Exception:
#         my_iface = 'Wi-Fi'
    
#     def do_capture():
#         # IP ka filter hata diya. BPF filter se sirf Web traffic capture hoga! Background traafic nahi hoga
#         bpf_filter = "tcp or udp or icmp"
        
#         captured = scapy.sniff(
#             timeout=duration, 
#             iface=my_iface,
#             filter=bpf_filter
#         )
#         packets_result.extend(captured)
    
#     capture_thread = threading.Thread(target=do_capture)
#     capture_thread.start()
    
#     # Scapy ko sun-na shuru karne ke liye 2 seconds do
#     time.sleep(2)
    
#     # Website ko request bhejo
#     try:
#         requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=duration-3, verify=False)
#     except Exception:
#         pass
    
#     capture_thread.join()
#     return packets_result, target_ip



import scapy.all as scapy
import threading
import requests
import socket
import time

def get_ip(url):
    try:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        return socket.gethostbyname(domain)
    except Exception:
        return None

def capture_with_request(url, duration=10):
    target_ip = get_ip(url)
    if not target_ip:
        target_ip = "Unknown" 
    
    packets_result = []
    
    try:
        my_iface = scapy.IFACES.dev_from_index(13)
    except Exception:
        my_iface = 'Wi-Fi'
    
    def do_capture():
        captured = scapy.sniff(
            timeout=duration, 
            iface=my_iface,
            filter="tcp or udp or icmp"
        )
        packets_result.extend(captured)
    
    # 1. Sniffer ko alag thread mein start karo
    capture_thread = threading.Thread(target=do_capture)
    capture_thread.start()
    
    time.sleep(1) # Scapy ko sun-na shuru karne ke liye 1 second do
    
    selenium_success = False
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # FIX: Driver ko strictly timeout do taake woh infinite wait na kare
        driver.set_page_load_timeout(duration - 2)
        
        try:
            driver.get(url) # Yeh page load karega
        except Exception:
            pass # Agar timeout ho jaye toh ignore karo, traffic toh capture ho chuka hai!
            
        # FIX: Oopar ka fuzool time.sleep() hata diya!
        # Ab main thread sirf tab tak wait karegi jab tak Scapy ke 10 second pooray nahi hotay
        capture_thread.join() 
        driver.quit()
        selenium_success = True
        
    except Exception:
        print("\n[Fallback Triggered] Browser engine failed. Using basic requests.")
        
    if not selenium_success:
        try:
            requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=duration-2, verify=False)
        except Exception:
            pass
        capture_thread.join()
        
    return packets_result, target_ip