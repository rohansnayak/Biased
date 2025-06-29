import os
import sys
from redis import Redis
from rq import Worker, Queue, Connection

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

listen = ['analysis']
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = Redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(list(map(str, listen)))
        worker.work() 