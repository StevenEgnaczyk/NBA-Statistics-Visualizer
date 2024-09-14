import requests

# Replace with the proxy you selected
# Replace with the proxy you selected
proxy = {
    'http': '162.223.90.130:80',
}


try:
    response = requests.get('https://stats.nba.com/stats/leaguegamefinder', timeout=30)
    response.raise_for_status()
    print("Proxy is working!")
    print(response.text[:500])  # Print first 500 characters of the response
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
