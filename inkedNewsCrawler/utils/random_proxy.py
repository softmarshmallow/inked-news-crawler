import os
import random

from inkedNewsCrawler.settings import BASE_DIR



path = os.path.join(BASE_DIR, 'proxies.txt')
data = open(path, 'r').read()
lines = data.split('\n')
proxies_list = [x for x in lines]


def get_random_proxy_for_requests():

    proxy = random.choice(proxies_list)
    proxies = {
        'http': proxy,
        'https': proxy,
    }
    return proxies


if __name__ == "__main__":
    proxies = get_random_proxy_for_requests()
    print(proxies)