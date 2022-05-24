from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='aio_redisbuffer',
    packages=find_packages(),
    author="kamalyes",
    version="0.1.1",
    auth_email="mryu168@163.com",
    python_requires=">=3.8",
    description="基于异步IO的Redis缓存操作工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kamalyes/aio_redisbuffer",
    platforms='any',
    license="MIT"
)
