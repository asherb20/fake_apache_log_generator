import random
import argparse
import string
import urllib.parse
from datetime import datetime, timedelta

METHODS = ['GET', 'POST']
URLS = ['/index.html', '/about', '/contact', '/login', '/dashboard']
STATUS_CODES = [200, 301, 404, 500]
# USER_AGENTS = ['Mozilla/5.0', 'curl/7.68.0', 'sqlmap/1.4.6']

def gen_rand_ip():
    return '.'.join(str(random.randint(1, 255)) for _ in range(4))

def gen_rand_ts(start, offset_mins=60):
    rand_time = start + timedelta(seconds=random.randint(0, offset_mins * 60))
    return rand_time.strftime('%d/%b/%Y:%H:%M:%S -0500')

def gen_log_line(ip: str, timestamp: str, method: str, path: str, params: dict[str, str], status_code: int):
    url = path
    if params and isinstance(params, dict) and len(params) > 0:
        q_param_str = urllib.parse.urlencode(params)
        url = f'{url}?{q_param_str}'
    size = random.randint(200, 5000)
    return f'{ip} - - [{timestamp}] "{method} {url} HTTP/1.1" {status_code} {size}'

def gen_rand_str(len: int):
    chars = string.ascii_lowercase
    rand_str = ''.join(random.choice(chars) for i in range(len))
    return rand_str

def gen_params(config: list[dict[str, str]]):
    params = {}

    if config and isinstance(config, list) and len(config) > 0:
        for c in config:
            map = {
                'str': gen_rand_str(8),
                'int': random.randint(1, 100)
            }

            params[c['key']] = map[c['type']]

    return params

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
                { 'key': 'id', 'type': 'int' }
            ],
            'status_codes': [200, 404]
        },
        {
            'method': 'POST',
            'path': '/login',
            'params': [
                { 'key': 'username', 'type': 'str' },
                { 'key': 'password', 'type': 'str' }
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
    current_session = init_session.copy()
    with open('access_log.txt', 'w') as f:
        for i in range(args.count):
            # handle session ip address
            current_ip = current_session.get('ip')
            if current_ip is None:
                ip = gen_rand_ip()
                current_session['ip'] = ip

            # decide bruteforce or bot traffic
            if args.bruteforce:
                current_session['bruteforce'] = random.choice([True, False])
            if args.bot and current_session['bruteforce'] is not True:
                current_session['bot'] = random.choice([True, False])

            # rand_sqlis = [' OR 1=1']

            path = paths[random.randint(0, len(paths) - 1)]
            if current_session['bruteforce']:
                for p in paths:
                    if p['method'] == 'POST' and p['path'] == '/login':
                        path = p
            if current_session['bot']:
                for p in paths:
                    if p['method'] == 'GET' and p['path'] == '/users':
                        path = p
            params = gen_params(path.get('params'))
            
            line = gen_log_line(current_session['ip'], gen_rand_ts(now, 5), path['method'], path['path'], params, random.choice(path['status_codes']))
            f.write(line + '\n')

            # start new session upon limit hit
            current_session['request_count'] += 1
            if current_session['request_count'] == current_session['max_requests']:
                current_session = init_session.copy()
