import json
import importlib.util
from pathlib import Path


def _load_sync_agent_config():
    root = Path(__file__).resolve().parents[1]
    script_path = root / "scripts" / "sync_agent_config.py"
    spec = importlib.util.spec_from_file_location("sync_agent_config", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sync_agent_config_accepts_allow_agents_key(tmp_path, monkeypatch):
    sync_agent_config = _load_sync_agent_config()

    cfg = {
        "agents": {
            "defaults": {"model": "openai/gpt-4o"},
            "list": [
                {
                    "id": "taizi",
                    "workspace": str(tmp_path / "ws-taizi"),
                    "allowAgents": ["zhongshu"]
                }
            ]
        }
    }

    cfg_path = tmp_path / "openclaw.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False))

    monkeypatch.setattr(sync_agent_config, "OPENCLAW_CFG", cfg_path)
    monkeypatch.setattr(sync_agent_config, "DATA", tmp_path / "data")

    sync_agent_config.main()

    out = json.loads((tmp_path / "data" / "agent_config.json").read_text())
    taizi = next(agent for agent in out["agents"] if agent["id"] == "taizi")
    assert taizi["allowAgents"] == ["zhongshu"]


def test_sync_agent_config_uses_updated_role_definitions(tmp_path, monkeypatch):
    sync_agent_config = _load_sync_agent_config()

    cfg = {
        "agents": {
            "defaults": {"model": "openai/gpt-4o"},
            "list": [
                {"id": "taizi", "workspace": str(tmp_path / "ws-taizi")},
                {"id": "zaochao", "workspace": str(tmp_path / "ws-zaochao")},
                {"id": "duzhisi", "workspace": str(tmp_path / "ws-duzhisi")},
                {"id": "jinengdaoshi", "workspace": str(tmp_path / "ws-jinengdaoshi")},
            ]
        }
    }

    cfg_path = tmp_path / "openclaw.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False))

    monkeypatch.setattr(sync_agent_config, "OPENCLAW_CFG", cfg_path)
    monkeypatch.setattr(sync_agent_config, "DATA", tmp_path / "data")

    sync_agent_config.main()

    out = json.loads((tmp_path / "data" / "agent_config.json").read_text())
    agents = {agent["id"]: agent for agent in out["agents"]}

    assert agents["taizi"]["duty"] == "统一入口、接旨立项、意图提炼与最终回奏"
    assert agents["zaochao"]["role"] == "早朝官"
    assert agents["zaochao"]["duty"] == "定时播报、异常播报与关键变化提醒"
    assert agents["duzhisi"]["duty"] == "token/API/流量/配额统计与资源用量治理"
    assert agents["jinengdaoshi"]["duty"] == "能力缺口识别、补能编排与技能治理"
