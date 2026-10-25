import asyncio
import sys

sys.path.insert(0, "src")

from agentic_pentest.presentation.chat import InteractiveChatSession


async def test():
    session = InteractiveChatSession(target_url="http://127.0.0.1:8888")

    print("=== TEST 1: 127.0.0.1:8888 là nền tảng gì, dấu hiệu ===")
    await session.ask_ai("127.0.0.1:8888 là nền tảng gì, dấu hiệu")

    print("\n=== TEST 3: ip của máy này là mấy ===")
    await session.ask_ai("ip của máy này là mấy")

    print("\n=== TEST 4: 127.0.0.1:8888 có lỗi gì, xác định ===")
    await session.ask_ai("127.0.0.1:8888 có lỗi gì, xác định")


if __name__ == "__main__":
    asyncio.run(test())
