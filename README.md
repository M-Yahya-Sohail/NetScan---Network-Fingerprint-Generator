🛡️ NetScan: Advanced Network Fingerprint & Behavior Profiler
NetScan is a sophisticated network analysis tool that generates unique digital fingerprints for websites based on their live traffic patterns. By combining deep packet inspection (DPI) with headless browser automation, NetScan classifies network behavior into distinct categories such as Streaming, Social Media, and API-Heavy traffic.

🚀 Key FeaturesDual-Engine Capture: Integrates Scapy for raw packet sniffing and Selenium (Headless Chrome) to trigger authentic JavaScript-driven network traffic.Behavioral Profiling: Automatically classifies websites using statistical heuristics (packet size distribution, IP diversity, and data volume).Deep Feature Extraction: Extracts over 10+ network features, including Protocol Distribution (TCP/UDP/DNS/HTTPS), Inter-Arrival Times, and Payload Sizes.Side-by-Side Comparison: A dedicated mode to compare the network footprints of two different URLs simultaneously.Cyberpunk Dashboard: A premium, dark-themed UI featuring interactive Chart.js visualizations for real-time data analysis.Robust Error Handling: Built-in DNS pre-checking to prevent analysis of non-existent domains.

🛠️ System ArchitectureNetScan is built with a modular backend to ensure scalability and academic precision:ModuleResponsibilitycapture.pyOrchestrates Selenium automation and Scapy's multi-threaded sniffing.extract.pyProcesses raw .pcap data into structured statistical features.classify.pyThe brain of the project; applies rule-based logic to determine behavior.fingerprint.pyAggregates all data into a standardized JSON fingerprint format.app.pyProvides a secure REST API for the frontend dashboard.

📊 Classification CategoriesOur refined statistical engine identifies traffic patterns based on the following profiles:📺 Streaming: Characterized by high data volume (>2.5MB) and sustained high-packet frequency.📱 Social Media: Identified by massive unique IP counts and heavy DNS query bursts from various CDNs.⚡ API-Heavy: Recognized by small, rapid packet bursts with a very low mean packet size.📄 Static Content: Minimalist traffic profiles with low packet counts and limited unique IP interactions.

⚙️ Installation & Setup
1. PrerequisitesPython 3.9+Npcap (Required for Scapy on Windows) Google Chrome (For Selenium automation)

2. Clone and InstallBash
# Clone the repository
git clone https://github.com/m-yahya-sohail/NetScan.git
cd NetScan

# Install Python dependencies
pip install -r requirements.txt
3. Run the DashboardBashcd backend
python app.py
Open your browser and go to: http://127.0.0.1:5000🧪 Automated TestingTo ensure the integrity of the classification engine, run the automated stress-test suite:Bashpython backend/test_netscan.py
This script validates the system against 25+ real-world domains to ensure a high accuracy rate.👤 DeveloperMuhammad Yahya Sohail Software Engineering Student at PUCIT