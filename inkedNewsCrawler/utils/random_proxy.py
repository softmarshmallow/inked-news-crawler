import os
import random

from inkedNewsCrawler.settings import BASE_DIR


def get_random_proxy_for_requests():
    path = os.path.join(BASE_DIR, 'proxies.txt')
    data = open(path, 'r').read()
    lines = data.split('\n')
    proxies = [x for x in lines]
    proxy = random.choice(proxies)
    proxies = {
        'http': proxy,
        'https': proxy,
    }
    return proxies


if __name__ == "__main__":
    proxies = get_random_proxy_for_requests()
    print(proxies)