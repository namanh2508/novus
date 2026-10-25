import asyncio
import sys

sys.path.insert(0, "src")

from agentic_pentest.presentation.chat import InteractiveChatSession


async def test():
    session = InteractiveChatSession(target_url="http://127.0.0.1:8888")

    print("=== TEST 1: 127.0.0.1:8888 là nền tảng gì, dấu hiệu ===")
    await session.ask_ai("127.0.0.1:8888 là nền tảng gì, dấu hiệu")

    print("\n=== TEST 2: có bao nhiêu port trên 127.0.0.1, các vùng đó dùng platform gì ===")
    await session.ask_ai("có bao nhiêu port trên 127.0.0.1, các vùng đó dùng platform gì")


if __name__ == "__main__":
    asyncio.run(test())
