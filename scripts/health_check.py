import requests

SERVICES = {
    "HTTPBin-200": "https://httpbin.org/status/200",
    "HTTPBin-404": "https://httpbin.org/status/404",
    "GitHub": "https://github.com"
}


def check_service(name, url):
    try:
        res = requests.get(url, timeout=5)
        status = "OK" if res.status_code == 200 else f"FAIL ({res.status_code})"
    except Exception as e:
        status = f"ERROR ({e})"
    return f"[{name}] Status: {status}"


def check_services():
    results = []
    for name, url in SERVICES.items():
        print(name)
        result = check_service(name, url)
        print(result)
        results.append(result)
    return results


def get_version():
    with open('VERSION') as f:
        return f.read().strip()


if __name__ == "__main__":
    print("Running Health Check Script - Version:", get_version())
    print("Running health checks...")
    check_services()
