from typing import AnyStr, AsyncGenerator, Tuple, Optional

from aredis import StrictRedis

from ._base import _BaseMapping
from .types import RedCollection, TTL
from ._exc import UnsupportedOperation


class AioRedisBuffer(_BaseMapping):

    def __init__(self, redis: StrictRedis):
        super().__init__(redis, "")

    @classmethod
    def new(cls, url: str, db: int = 0, **kwargs) -> 'AioRedisBuffer':
        redis = StrictRedis.from_url(url, db, **kwargs)
        return cls(redis)

    def red_hash(self, resource: AnyStr) -> 'RedHash':
        return RedHash(self.redis, resource)

    async def delete(self, key: AnyStr, *name: AnyStr) -> int:
        return await self.redis.delete(key, *name)

    async def find(self, match: AnyStr = None) -> AsyncGenerator[bytes, None]:
        cursor = 0
        while True:
            cursor, rows = await self.redis.scan(cursor=cursor, match=match)
            for row in rows:
                yield row
            if not cursor:
                break

    async def set(self, key: AnyStr, value: AnyStr, ex: TTL = None) -> int:
        return await self.redis.set(key, value, ex=ex)

    async def __aiter__(self) -> AsyncGenerator[bytes, None]:
        async for row in self.find():
            yield row

    async def has(self, key: AnyStr) -> bool:
        return await self.redis.exists(key)

    async def get(self, key: AnyStr, default_value: AnyStr = None) -> bytes:
        return ret if (ret := await self.redis.get(key)) is not None else default_value

    async def clear(self):
        await self.redis.flushdb()

    async def incr(self, key: AnyStr, value: int = 1) -> int:
        return await self.redis.incrby(key, value)

    def read_set(self, resource: AnyStr) -> 'RedSet':
        return RedSet(self.redis, resource)

    def red_list(self, resource: AnyStr) -> 'RedList':
        return RedList(self.redis, resource)

    async def size(self) -> int:
        return await self.redis.dbsize()


class RedHash(_BaseMapping):

    async def remove(self):
        await self.redis.delete(self._resource)

    async def __aenter__(self) -> 'RedHash':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.remove()
        if exc_val:
            raise exc_val

    async def has(self, key: AnyStr) -> bool:
        return await self.redis.hexists(key)

    async def set(self, key: AnyStr, value: AnyStr, ex: TTL = None) -> int:
        if ex:
            raise UnsupportedOperation("Can't set TTL for key of Hash table")
        return await self.redis.hset(self._resource, key, value)

    async def get(self, key: AnyStr, default_value: AnyStr = None) -> bytes:
        ret = await self.redis.hget(self._resource, key)
        return default_value if ret is None else ret

    async def find(self, match: AnyStr = None) -> AsyncGenerator[Tuple[bytes, bytes], None]:
        cursor = 0
        while True:
            cursor, rows = await self.redis.hscan(self._resource, cursor=cursor, match=match)
            for row in rows.items():
                yield row
            if not cursor:
                break

    async def __aiter__(self):
        async for row in self.find():
            yield row

    async def size(self) -> int:
        return await self.redis.hlen(self.resource)

    async def incr(self, key: AnyStr, value: int = 1) -> int:
        return await self.redis.hincrby(self.resource, key, value)

    async def delete(self, key: AnyStr, *args: AnyStr) -> int:
        return await self.redis.hdel(self.resource, key, *args)


class RedSet(RedCollection):
    async def add(self, value: AnyStr, *args: AnyStr) -> int:
        return await self.redis.sadd(self.resource, value, *args)

    async def remove(self, value: str) -> int:
        return await self.redis.srem(value)

    async def __aiter__(self) -> AsyncGenerator[bytes, None]:
        cursor = 0
        while True:
            items = await self.redis.sscan(self.resource, cursor=cursor)
            for item in items:
                yield item

    async def size(self) -> int:
        return await self.redis.scard(self.resource)


class RedList(RedCollection):
    async def add(self, value: AnyStr, *args: AnyStr) -> int:
        return await self.lpush(value, *args)

    async def lpush(self, value: AnyStr, *args: AnyStr) -> int:
        return await self.redis.lpush(self.resource, value, *args)

    async def rpush(self, value: AnyStr, *args: AnyStr) -> int:
        return await self.redis.rpush(self.resource, value, *args)

    async def lpop(self) -> Optional[bytes]:
        return await self.redis.lpop(self.resource)

    async def rpop(self) -> Optional[bytes]:
        return await self.redis.rpop(self.resource)

    async def remove(self, value: str) -> int:
        return await self.rm_(value)

    async def rm_(self, value: str, count: int = 0) -> int:
        return await self.redis.lrem(self.resource, value, count=count)

    async def __aiter__(self) -> AsyncGenerator[bytes, None]:
        async for item in self.iterator():
            yield item

    async def iterator(self, read_size: int = 1000) -> AsyncGenerator[bytes, None]:
        t = 0
        while True:
            x, y = t * read_size, (t + 1) * read_size
            items = await self.redis.lrange(self.resource, x, y)
            for item in items:
                yield item
            if len(items) < read_size:
                break

    async def size(self) -> int:
        return await self.redis.llen(self.resource)
