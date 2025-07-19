import random
import argparse
import string
import urllib.parse
from datetime import datetime, timedelta

METHODS = ['GET', 'POST']
URLS = ['/index.html', '/about', '/contact', '/login', '/dashboard']
STATUS_CODES = [200, 301, 404, 500]
# USER_AGENTS = ['Mozilla/5.0', 'curl/7.68.0', 'sqlmap/1.4.6']

def random_ip():
    return '.'.join(str(random.randint(1, 255)) for _ in range(4))

def random_timestamp(start, offset_mins=60):
    random_time = start + timedelta(seconds=random.randint(0, offset_mins * 60))
    return random_time.strftime('%d/%b/%Y:%H:%M:%S -0500')

def generate_log_line(ip: str, timestamp: str, method: str, url: str, status_code: int):
    size = random.randint(200, 5000)
    return f'{ip} - - [{timestamp}] "{method} {url} HTTP/1.1" {status_code} {size}'

def generate_bruteforce_log_line(ip: str, method: str, path: str, params: dict[str, str], status_code: int, timestamp: str):
    url = f'{path}?{urllib.parse.urlencode(params)}'
    return f'{ip} - - [{timestamp}] "{method} {url} HTTP/1.1" {status_code} {random.randint(200, 400)}'

def generate_bot_log_line(ip: str, method: str, path: str, params: dict[str, str], status_code: int, timestamp: str):
    url = f'{path}?{urllib.parse.urlencode(params)}'
    return f'{ip} - - [{timestamp}] "{method} {url} HTTP/1.1" {status_code} {random.randint(200, 400)}'

def generate_random_string(len: int):
    chars = string.ascii_lowercase
    rand_str = ''.join(random.choice(chars) for i in range(len))
    return rand_str

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A script that generates fake Apache server log files.')
    parser.add_argument('-c', '--count', type=int, default=100, help='The number of lines to generate.')
    parser.add_argument('-bf', '--bruteforce', action='store_true', help='Simulate brute force logs.')
    parser.add_argument('-b', '--bot', action='store_true', help='Simulate bot traffic logs.')

    args = parser.parse_args()

    paths = [
        { 'method': 'GET', 'path': '/', 'status_codes': [200] },
        { 'method': 'GET', 'path': '/about', 'status_codes': [200] },
        { 'method': 'GET', 'path': '/contact', 'status_codes': [200] },
        { 'method': 'GET', 'path': '/login', 'status_codes': [200] },
        {
            'method': 'GET',
            'path': '/users',
            'params': [
                { 'key': 'id' }
            ],
            'status_codes': [200, 404]
        },
        {
            'method': 'POST',
            'path': '/login',
            'params': [
                { 'key': 'username' },
                { 'key': 'password' }
            ],
            'status_codes': [200, 401]
        },
        { 'method': 'GET', 'path': '/dashboard', 'status_codes': [200, 401] },
    ]

    now = datetime.now()
    init_session = {
        'request_count': 0,
        'max_requests': 10,
        'ip': None,
        'bruteforce': False,
        'bot': False
    }
    current_session = init_session
    with open('access_log.txt', 'w') as f:
        for i in range(args.count):
            # handle session ip address
            current_ip = current_session.get('ip')
            if current_ip is None:
                ip = random_ip()
                current_session['ip'] = ip

            # decide bruteforce or bot traffic
            if args.bruteforce:
                current_session['bruteforce'] = random.choice([True, False])
            if args.bot and current_session['bruteforce'] is not True:
                current_session['bot'] = random.choice([True, False])

            # STOPPED HERE: continue building on logic
            rand_path = paths[random.randint(0, len(paths) - 1)]
            rand_sqlis = [' OR 1=1']

            if rand_path['method'] == 'POST' and rand_path['path'] == '/login':
                params = {}
                for param in rand_path['params']:
                    params[param['key']] = generate_random_string(8)
                line = generate_bruteforce_log_line(current_session['ip'], rand_path['method'], rand_path['path'], params, random.choice(rand_path['status_codes']), random_timestamp(now, 1))
            if rand_path['method'] == 'GET' and rand_path['path'] == '/users':
                params = {}
                for param in rand_path['params']:
                    if param['key'] == 'id':
                        params['id'] = f'{random.randint(1, 100)} {random.choice(rand_sqlis)}'
                line = generate_bot_log_line(current_session['ip'], rand_path['method'], rand_path['path'], params, random.choice(rand_path['status_codes']), random_timestamp(now, 5))
                        

            # start new session upon limit hit
            current_session['request_count'] += 1
            if current_session['request_count'] == current_session['max_requests']:
                current_session = init_session
