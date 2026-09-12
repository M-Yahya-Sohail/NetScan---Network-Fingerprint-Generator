import scapy.all as scapy
import threading
import requests
import socket
import time
from urllib.parse import urlparse

# ==========================================
# PERFORMANCE FIX: ONE-TIME GLOBAL SETUP
# ==========================================
SELENIUM_AVAILABLE = False
CHROME_DRIVER_PATH = None

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    # Server start hotay hi sirf ek dafa driver cache karega
    CHROME_DRIVER_PATH = ChromeDriverManager().install()
    SELENIUM_AVAILABLE = True
except Exception:
    pass


def check_domain_exists(url):
    try:
        domain = urlparse(url).netloc
        if not domain:
            domain = url.split("/")[0]
        socket.gethostbyname(domain)
        return 1
    except (socket.gaierror, Exception):
        return 0


def get_ip(url):
    try:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        return socket.gethostbyname(domain)
    except Exception:
        return None


def capture_with_request(url, duration=10):
    if check_domain_exists(url) == 0:
        raise ValueError(
            "The specified domain does not exist or DNS resolution failed!"
        )

    target_ip = get_ip(url)
    if not target_ip:
        target_ip = "Unknown"

    packets_result = []

    try:
        my_iface = scapy.IFACES.dev_from_index(13)
    except Exception:
        my_iface = "Wi-Fi"

    def do_capture():
        captured = scapy.sniff(
            timeout=duration, iface=my_iface, filter="tcp or udp or icmp"
        )
        packets_result.extend(captured)

    capture_thread = threading.Thread(target=do_capture)
    capture_thread.start()

    time.sleep(1)  # Scapy setup delay

    selenium_success = False

    if SELENIUM_AVAILABLE:
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--mute-audio")
            chrome_options.add_argument("--no-sandbox")  # Startup speed boost
            chrome_options.add_argument("--disable-dev-shm-usage")

            # SPEED FIX: Wait only for DOM, not images/videos
            chrome_options.page_load_strategy = "eager"
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )

            # Reuse pre-downloaded path
            service = Service(CHROME_DRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.set_page_load_timeout(duration - 2)

            try:
                driver.get(url)
            except Exception:
                pass

            capture_thread.join()
            driver.quit()
            selenium_success = True

        except Exception:
            pass

    if not selenium_success:
        try:
            requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=duration - 2,
                verify=False,
            )
        except Exception:
            pass
        capture_thread.join()

    return packets_result, target_ip
