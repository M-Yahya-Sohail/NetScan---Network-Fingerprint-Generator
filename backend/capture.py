import scapy.all as scapy
import threading
import requests
import socket
import time

def get_ip(url):
    """URL se IP address nikalna"""
    try:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        return socket.gethostbyname(domain)
    except Exception:
        return None

def capture_with_request(url, duration=10):
    """Capture karo aur saath mein website ko request bhi bhejo"""
    target_ip = get_ip(url)
    if not target_ip:
        target_ip = "Unknown" # Agar resolve na ho toh fail na ho
    
    packets_result = []
    
    # Direct object use kar rahe hain
    try:
        my_iface = scapy.IFACES.dev_from_index(13)
    except Exception:
        my_iface = 'Wi-Fi'
    
    def do_capture():
        # IP ka filter hata diya. BPF filter se sirf Web traffic capture hoga!
        captured = scapy.sniff(
            timeout=duration, 
            iface=my_iface,
            filter="tcp port 80 or tcp port 443"
        )
        packets_result.extend(captured)
    
    capture_thread = threading.Thread(target=do_capture)
    capture_thread.start()
    
    # Scapy ko sun-na shuru karne ke liye 2 seconds do
    time.sleep(2)
    
    # Website ko request bhejo
    try:
        requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=duration-3, verify=False)
    except Exception:
        pass
    
    capture_thread.join()
    return packets_result, target_ip