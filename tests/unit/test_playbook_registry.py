"""Unit tests for attack playbook registry and YAML validation."""

from pathlib import Path

from agentic_pentest.infrastructure.playbooks.registry import PlaybookRegistry


def test_load_existing_playbooks() -> None:
    playbooks_dir = Path("src/agentic_pentest/infrastructure/playbooks/data")
    assert playbooks_dir.exists(), "Playbook directory missing"

    registry = PlaybookRegistry()
    loaded = registry.load_playbooks(str(playbooks_dir))
    assert len(loaded) >= 2

    # Check BOLA Read playbook
    bola_read = registry.get_playbook("bola_read_01")
    assert bola_read is not None
    assert bola_read.category == "BOLA"
    assert bola_read.requires_shadow_clone is False
    assert len(bola_read.steps) >= 3

    # Check BOLA Write playbook (requires shadow cloning)
    bola_write = registry.get_playbook("bola_write_01")
    assert bola_write is not None
    assert bola_write.requires_shadow_clone is True
