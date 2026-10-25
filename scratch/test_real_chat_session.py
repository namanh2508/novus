import asyncio

from agentic_pentest.presentation.chat import InteractiveChatSession


async def test_full_chat_session() -> None:
    print("=== STARTING FULL CHAT SESSION TEST (ZERO SETUP, PURE CHAT) ===")

    # Initialize session without any external keys or external services
    session = InteractiveChatSession(
        target_url="http://127.0.0.1:8888",
        permission_mode="auto-approve",
        safe_mode=True,
    )
    print("[1] Session initialized successfully.")

    # 1. Test Help Banner
    session.print_help()
    print("[2] print_help() executed.")

    # 2. Test Status
    session.print_status()
    print("[3] print_status() executed.")

    # 3. Test Tools
    session.show_tools()
    print("[4] show_tools() executed.")

    # 4. Test Memory
    session.show_memory()
    print("[5] show_memory() executed.")

    # 5. Test Headers Audit
    await session.audit_headers("http://127.0.0.1:8888/identity/api/auth/login")
    print("[6] audit_headers() executed.")

    # 6. Test Cookies Audit
    await session.audit_cookies("http://127.0.0.1:8888/identity/api/auth/login")
    print("[7] audit_cookies() executed.")

    # 7. Test CORS Audit
    await session.audit_cors("http://127.0.0.1:8888/identity/api/auth/login")
    print("[8] audit_cors() executed.")

    # 8. Test JWT Audit
    sample_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    await session.audit_jwt(sample_jwt)
    print("[9] audit_jwt() executed.")

    # 9. Test SSRF Audit
    await session.audit_ssrf("/community/api/v2/coupon/new-coupon")
    print("[10] audit_ssrf() executed.")

    # 10. Test Fuzz Audit
    await session.audit_fuzz("/identity/api/v2/user")
    print("[11] audit_fuzz() executed.")

    # 11. Test Model Check
    await session.check_model()
    print("[12] check_model() executed.")

    # 12. Test Natural Language Greeting & Ask AI
    await session.ask_ai("hello")
    await session.ask_ai("Làm thế nào để phòng chống lỗ hổng BOLA và BFLA?")
    print("[13] ask_ai() executed.")

    # 13. Test Plan Generation
    await session.show_plan()
    print("[14] show_plan() executed.")

    # 14. Test Checkpoint Save & Resume
    session.save_checkpoint("test_live_checkpoint")
    session.resume_checkpoint("test_live_checkpoint")
    print("[15] save/resume checkpoint executed.")

    # 15. Test Evaluation Runner
    await session.run_eval()
    print("[16] run_eval() executed.")

    # 16. Test New SOTA Capabilities
    session.show_coverage()
    print("[17] show_coverage() executed.")

    session.show_cost_traces()
    print("[18] show_cost_traces() executed.")

    session.show_roe()
    print("[19] show_roe() executed.")

    session.show_attack_chain()
    print("[20] show_attack_chain() executed.")

    print("\n=== ALL REAL CHAT WORKFLOWS EXECUTED PERFECTLY WITHOUT ERRORS! ===")


if __name__ == "__main__":
    asyncio.run(test_full_chat_session())
