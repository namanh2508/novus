import asyncio

from agentic_pentest.application.use_cases.intent_router import NaturalLanguageIntentRouter
from agentic_pentest.presentation.chat import InteractiveChatSession


async def test_natural_language_chat():
    print("=== TESTING SMART OFFLINE SECURITY INTELLIGENCE ===")
    session = InteractiveChatSession(target_url="http://127.0.0.1:8888")

    # 1. Test BOLA/IDOR inquiry in Vietnamese
    print("\n[TEST 1] Asking about BOLA:")
    await session.ask_ai("BOLA là gì và code khắc phục thế nào?")

    # 2. Test JWT inquiry
    print("\n[TEST 2] Asking about JWT alg=none:")
    await session.ask_ai("JWT có những lỗi nào và alg=none là sao?")

    # 3. Test Race Condition inquiry
    print("\n[TEST 3] Asking about Race Condition / TOCTOU:")
    await session.ask_ai("Làm thế nào để phòng chống lỗi Race condition khi nhận coupon?")

    # 4. Test Memory / ASLR inquiry
    print("\n[TEST 4] Asking about ASLR and ROP:")
    await session.ask_ai("ASLR và ROP chain hoạt động như thế nào?")

    # 5. Test Natural Language IP & Port Intent Routing
    print("\n=== TESTING NATURAL LANGUAGE TARGET PARSING & INTENT DISPATCH ===")
    router = NaturalLanguageIntentRouter()

    prompts = [
        "Kiểm thử target 127.0.0.1:8888 xem có bị dính BOLA không",
        "Hãy quét an ninh mục tiêu ip 192.168.1.50 port 8080",
        "Target là 10.0.0.1 cổng 8888",
        "Quét toàn bộ hệ thống trên http://localhost:8888",
    ]

    for p in prompts:
        route = router.route(p)
        print(f"Prompt: '{p}'")
        print(f"  -> Extracted Target: {route.extracted_url}")
        print(
            f"  -> Intent: {route.intent.value} | Tool: {route.recommended_tool} | Confidence: {route.confidence}"
        )
        assert route.extracted_url is not None, f"Failed to extract target from '{p}'"

    print("\n[SUCCESS] ALL NATURAL LANGUAGE CHAT & ROUTING TESTS PASSED!")


if __name__ == "__main__":
    asyncio.run(test_natural_language_chat())
