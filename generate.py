import random
import argparse
from datetime import datetime, timedelta

METHODS = ['GET', 'POST']
URLS = ['/index.html', '/about', '/contact', '/login', '/dashboard']
STATUS_CODES = [200, 301, 404, 500]
USER_AGENTS = ['Mozilla/5.0', 'curl/7.68.0', 'sqlmap/1.4.6']

def random_ip():
    return '.'.join(str(random.randint(1, 255)) for _ in range(4))

def random_timestamp(start, offset_mins=60):
    random_time = start + timedelta(seconds=random.randint(0, offset_mins * 60))
    return random_time.strftime('%d/%b/%Y:%H:%M:%S -0500')

def generate_log_line(timestamp):
    ip = random_ip()
    method = random.choice(METHODS)
    url = random.choice(URLS)
    status_code = random.choice(STATUS_CODES)
    size = random.randint(200, 5000)
    return f'{ip} - - [{timestamp}] "{method} {url} HTTP/1.1" {status_code} {size}'

def generate_brute_force_logs(ip, start_time, attempts=20):
    lines = []
    for _ in range(attempts):
        timestamp = random_timestamp(start_time, 1)
        line = f'{ip} - - [{timestamp}] "POST /login HTTP/1.1" 401 {random.randint(200, 400)}'
        lines.append(line)
    return lines

def generate_bot_traffic(ip, start_time, hits=10):
    lines = []
    for _ in range(hits):
        timestamp = random_timestamp(start_time, 10)
        url = f"/admin.php?id={random.randint(1, 100)} OR 1=1"
        line = f'{ip} - - [{timestamp}] "GET {url} HTTP/1.1" 200 {random.randint(300, 1000)}'
        lines.append(line)
    return lines

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A script that generates fake Apache server log files.')
    parser.add_argument('-c', '--count', type=int, default=100, help='The number of lines to generate.')
    parser.add_argument('-bf', '--bruteforce', action='store_true', help='Simulate brute force logs.')
    parser.add_argument('-b', '--bot', action='store_true', help='Simulate bot traffic logs.')

    args = parser.parse_args()

    now = datetime.now()
    with open('access_log.txt', 'w') as f:
        for _ in range(args.count):
            timestamp = random_timestamp(now)
            log_line = generate_log_line(timestamp)
            f.write(log_line + '\n')

        bf_count = 20
        bot_count = 10

        # generate brute force logs
        if args.bruteforce:
            bad_ip = random_ip()
            brute_logs = generate_brute_force_logs(bad_ip, now, bf_count)
            for line in brute_logs:
                f.write(line + '\n')

        # generate bot traffic
        if args.bot:
            bot_ip = random_ip()
            bot_logs = generate_bot_traffic(bot_ip, now, bot_count)
            for line in bot_logs:
                f.write(line + '\n')
