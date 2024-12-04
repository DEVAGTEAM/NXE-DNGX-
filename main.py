import os
import random
import string
import uuid
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from pystyle import Write, Colors
from colorama import Fore, init

# Initialize Colorama for cross-platform color support
init(autoreset=True)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)

class ConsoleColors:
    RESET = Fore.RESET
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    GREEN = Fore.GREEN
    RED = Fore.RED
    LIGHT_BLUE = Fore.LIGHTBLUE_EX
    YELLOW = Fore.YELLOW

class NXEDNGXGenerator:
    def __init__(self, owner, promo_link):
        self.chrome_version = random.randint(115, 121)
        self.owner = owner
        self.promo_link = promo_link
        self.proxy_file = "proxies.txt"
        self.promo_file = "promos.txt"
        self.session_headers = {
            "Origin": "https://www.opera.com",
            "Content-Type": "application/json",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.chrome_version}.0.0.0 Safari/537.36 OPR/105.0.0.0"
        }

        # Initialize proxies
        self._fetch_proxies()

    def _fetch_proxies(self):
        url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all"
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(self.proxy_file, "w") as f:
                f.write(response.text)
            logging.info("Proxies fetched successfully.")
        except requests.RequestException as e:
            logging.error(f"Error fetching proxies: {e}")

    def _get_proxy(self):
        if os.path.exists(self.proxy_file):
            with open(self.proxy_file, "r") as f:
                proxies = f.read().splitlines()
                if proxies:
                    return random.choice(proxies)
        return None

    def _create_session(self):
        proxy = self._get_proxy()
        session = requests.Session()
        if proxy:
            session.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        return session

    @staticmethod
    def _get_current_time():
        return datetime.datetime.now().strftime("%H:%M:%S")

    def _validate_promo(self, promo_url):
        try:
            response = requests.get(promo_url)
            if response.status_code == 200:
                logging.info(f"Promo validated: {promo_url}")
            else:
                logging.warning(f"Promo invalid: {promo_url}")
        except requests.RequestException as e:
            logging.error(f"Error validating promo: {e}")

    def generate_promo(self):
        session = self._create_session()
        data = {"partnerUserId": str(uuid.uuid4())}
        try:
            response = session.post(
                "https://api.discord.gx.games/v1/direct-fulfillment",
                headers=self.session_headers,
                json=data
            )
            response.raise_for_status()
            token = response.json().get('token', 'N/A')
            promo_url = f"{self.promo_link}{token}"
            with open(self.promo_file, "a") as f:
                f.write(promo_url + "\n")
            logging.info(f"Generated promo: {promo_url}")
            self._validate_promo(promo_url)
        except requests.RequestException as e:
            logging.error(f"Error generating promo: {e}")

def main():
    owner = "Imon XD Dev"
    promo_link = "https://discord.com/billing/partner-promotions/1180231712274387115/"
    generator = NXEDNGXGenerator(owner, promo_link)

    # User Configurations
    max_threads = int(input("Enter the number of threads to use (e.g., 100): "))
    promo_quantity = int(input("Enter the number of promo codes to generate: "))

    Write.Print(
        f"""
        ╔═╗╦  ╔═╗  ╦  ╔╗╔╔═╗╦ ╦
        ║ ║║  ║ ║  ║  ║║║╠═╣╚╦╝
        ╚═╝╩═╝╚═╝  ╩═╝╝╚╝╩ ╩ ╩  
        ╔╦╗╔═╗╔╦╗  ╔╦╗╔═╗╔═╗╦  ╔═╗
         ║║║╣  ║║   ║║║╣ ║ ║║  ╚═╗
        ═╩╝╚═╝═╩╝  ═╩╝╚═╝╚═╝╩═╝╚═╝
         NXE DNGX Promo Gen - github.com/{owner}
        """, Colors.blue_to_purple, interval=0.01
    )

    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(generator.generate_promo) for _ in range(promo_quantity)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in thread: {e}")

if __name__ == "__main__":
    main()
