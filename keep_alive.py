import time
import requests
import sys

# Replace with your Render URL
URL = "https://agentic-honeypot-1vei.onrender.com/health"
INTERVAL = 840  # 14 minutes (Render sleeps after 15 mins of inactivity)

def keep_alive():
    print(f"🚀 Starting keep-alive service for: {URL}")
    print(f"⏰ Pinging every {INTERVAL/60} minutes to prevent sleep...")
    
    while True:
        try:
            start = time.time()
            response = requests.get(URL)
            duration = time.time() - start
            
            if response.status_code == 200:
                print(f"✅ [{time.ctime()}] Ping Success! Status: {response.status_code} (took {duration:.2f}s)")
            else:
                print(f"⚠️ [{time.ctime()}] Ping Returned Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ [{time.ctime()}] Ping Failed: {e}")
            
        # Wait for the next interval
        time.sleep(INTERVAL)

if __name__ == "__main__":
    print("Press Ctrl+C to stop.")
    try:
        keep_alive()
    except KeyboardInterrupt:
        print("\n👋 Keep-alive script stopped.")
        sys.exit(0)
