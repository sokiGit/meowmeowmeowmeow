import requests

def get_ip_info(ip_address : str):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=156185")
        response.raise_for_status()
        json = response.json()
        return json
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IP info: {e}")
        return None