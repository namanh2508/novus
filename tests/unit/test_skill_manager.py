"""Unit tests for Progressive Skill Manager and LoadSkillTool."""

from __future__ import annotations

import pytest

from agentic_pentest.application.skills.skill_manager import SkillManager
from agentic_pentest.application.use_cases.tool_registry import LoadSkillTool


def test_skill_manager_lists_and_loads_playbooks() -> None:
    mgr = SkillManager()
    skills = mgr.list_skills()

    assert len(skills) >= 4
    assert "bola_idor" in skills
    assert "bfla_privilege_escalation" in skills
    assert "jwt_cryptographic_flaws" in skills
    assert "race_condition_toctou" in skills

    bola_content = mgr.get_skill("bola_idor")
    assert "Broken Object Level Authorization" in bola_content
    assert "3-Way Differential Proof" in bola_content

    missing = mgr.get_skill("non_existent_skill_xyz")
    assert "Skill 'non_existent_skill_xyz' not found" in missing


@pytest.mark.asyncio
async def test_load_skill_tool_execution() -> None:
    tool = LoadSkillTool()
    assert tool.metadata.name == "load_skill"

    # List all skills when no arg
    res_list = await tool.execute()
    assert "Available specialized playbooks" in res_list
    assert "bola_idor" in res_list

    # Load specific skill
    res_skill = await tool.execute(skill_name="jwt_cryptographic_flaws")
    assert "JSON Web Token" in res_skill
    assert "Algorithm Confusion" in res_skill
