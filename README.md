# aio_redisbuffer

Redis缓存工具[redisbuffer](https://github.com/kamalyes/redisbuffer) 的 asyncio 版本.

## 安装

```shell script
$ pip install aio_redis_buffer
```

## 示例

### 初始化

```python
import aio_redisbuffer

aio_redisbuffer.new("redis://redis:6379", db=0)

```
或:

```python
from aio_redisbuffer import AioRedisBuffer
from aredis import StrictRedis

redis = StrictRedis(**{})
aio_redis_buffer = AioRedisBuffer(redis)
```

### 一般操作

```python
import aio_redisbuffer
import asyncio

aio_redis_buffer = aio_redisbuffer.new("redis://redis", db=0)


async def simple_operations():
    # 设置
    await aio_redis_buffer.set("hello", "world", ex=180)
    # 查询字段
    print(await aio_redis_buffer.get("hello", default_value="WORLD!"))
    # 删除字段
    await aio_redis_buffer.delete("hello")


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(simple_operations())

```
### Hash

```python
import asyncio

import aio_redisbuffer

aio_redis_buffer = aio_redisbuffer.new("redis://redis", db=0)
hs = aio_redis_buffer.red_hash("red::hash")


async def simple_operations():
    # 设置
    await hs.set("hello", "world", ex=180)
    # 查询字段
    print(await hs.get("hello", default_value="WORLD!"))
    # 删除字段
    await hs.delete("hello")


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(simple_operations())

```

###缓存

```python
import asyncio

import aio_redisbuffer

aio_redis_buffer = aio_redisbuffer.new("redis://redis", db=0)


# 缓存函数返回值
@aio_redis_buffer.cache_it(lambda asset_id: "asset::cache:key:{}".format(asset_id), ttl=180)
async def read_data(asset_id: int) -> dict:
    await asyncio.sleep(0.1)
    return dict(zip(range(10), range(10)))


# 删除缓存
@aio_redis_buffer.remove_it(lambda asset_id: "asset::cache:key:{}".format(asset_id), by_return=True)
async def update_date(asset_id: int) -> int:
    await asyncio.sleep(0.1)
    return asset_id


async def main():
    await read_data(10)
    await update_date(10)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
```

#### 基于HASH的缓存

```python
import asyncio

import aio_redisbuffer

aio_redis_buffer = aio_redisbuffer.new("redis://redis", db=0)
hs = aio_redis_buffer.red_hash("red::hash")


# 缓存函数返回值
@hs.cache_it(lambda asset_id: "asset::cache:key:{}".format(asset_id), ttl=180)
async def read_data(asset_id: int) -> dict:
    await asyncio.sleep(0.1)
    return dict(zip(range(10), range(10)))


# 删除缓存
@hs.remove_it(lambda asset_id: "asset::cache:key:{}".format(asset_id), by_return=True)
async def update_date(asset_id: int) -> int:
    await asyncio.sleep(0.1)
    return asset_id


async def main():
    await read_data(10)
    await update_date(10)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

```

