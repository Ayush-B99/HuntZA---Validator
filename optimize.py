import time
import re
from typing import Tuple, Optional
from collections import defaultdict, deque
import threading

class RateLimitedValidator:
    MAX_TOTAL = 254
    MAX_LOCAL = 64
    MAX_DOMAIN = 255

def __init__(self,
        rate_limit: int = 10,      
        window: int = 60,          
        global_limit: int = 1000,  
        global_window: int = 60,   
        cache_size: int = 10000):
       
        self.rate_limit = rate_limit
        self.window = window
        self.global_limit = global_limit
        self.global_window = global_window
       
        self._email_limits = defaultdict(lambda: deque(maxlen=rate_limit * 2))
        self._global_requests = deque(maxlen=global_limit * 2)
        self._lock = threading.RLock()
       
        self._cache = {}
        self._cache_size = cache_size
        self._cache_lock = threading.RLock()



def _check_rate_limit(self, email: str) -> bool:
        with self._lock:
            now = time.time()
           
            while self._global_requests and now - self._global_requests[0] > self.global_window:
                self._global_requests.popleft()
           
            if len(self._global_requests) >= self.global_limit:
                return False
           
            requests = self._email_limits[email]
            while requests and now - requests[0] > self.window:
                requests.popleft()
           
            if len(requests) >= self.rate_limit:
                return False
           
            self._global_requests.append(now)
            requests.append(now)
            return True
        

def _cache_get(self, email: str):
        with self._cache_lock:
            return self._cache.get(email)
   
def _cache_set(self, email: str, result: Tuple[bool, str]):
        with self._cache_lock:
            if len(self._cache) >= self._cache_size:
                try:
                    del self._cache[next(iter(self._cache))]
                except:
                    pass
            self._cache[email] = result