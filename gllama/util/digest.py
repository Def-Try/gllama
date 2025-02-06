import hashlib
import asyncio

async def sha256(file, block_size=(1024*1024*16)):
    sha = hashlib.sha256()
    while (file_buffer := file.read(block_size)):
        sha.update(file_buffer)
        await asyncio.sleep(0.01)
    return sha.hexdigest()
