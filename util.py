import time
import asyncio

class RateLimiter:
    """
    Limit rate request speed. 
    """
    START = time.monotonic()

    def __init__(self, session, rate):
        '''
        rate: int, number of requests per second
        '''
        if rate < 2: 
            raise ValueError('Rate must larger than 2')
        self.session = session
        self.rate = rate #
        self.max_token = self.rate // 2
        self.token_bucket = self.max_token

        self.updated_at = time.monotonic()

    async def get(self, *args, **kwargs):
        await self.wait_for_token()
        now = time.monotonic() - self.START
        return self.session.get(*args, **kwargs)

    async def wait_for_token(self):
        while self.token_bucket < 1:
            self.add_new_tokens()
            await asyncio.sleep(3)     
        self.token_bucket -= 1
        

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.rate
        if self.token_bucket + new_tokens >= 1:
            self.token_bucket = min(self.token_bucket + new_tokens, self.max_token)
            self.updated_at = now



def async_mesure_time_excute(func):
    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **params)
        else:
            raise TypeError(f'{func} is not coroutine')

    async def helper(*args, **params):
        start = time.time()
        result = await process(func, *args, **params)
        if isinstance(args[1],list):
            print(f'Get data from {len(args[1])} asin took {round(time.time() - start,4)} seconds')
        else:
            print(f'Get data from {args[1]} asin took {round(time.time() - start,4)} seconds')

        return result

    return helper