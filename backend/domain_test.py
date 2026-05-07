import socket
from urllib.parse import urlparse

def check_domain_exists(url):
    """
    Check karta hai ke domain exist karta hai ya nahi.
    Return 1 if exists, 0 if not.
    """
    try:
        # 1. Extract domain from URL (e.g., https://google.com -> google.com)
        domain = urlparse(url).netloc
        
        # If URL don't have schema the urlprase becomes empty
        if not domain:
            domain = url.split('/')[0]

        # 2. Check DNS resolution
        socket.gethostbyname(domain)
        return 1
    except (socket.gaierror, Exception):
        return 0

# --- Testing ---
print(f"Google Test: {check_domain_exists('https://www.google.com')}") # Output: 1
print(f"Fake Domain Test: {check_domain_exists('https://random123.aplhabeta')}") # Output: 0