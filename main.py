import asyncio
from task1 import scheduler
from task2 import bot_runner

async def main():
    task1 = asyncio.create_task(scheduler())
    task2 = asyncio.create_task(bot_runner())
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(main())
