import importlib.util
from pathlib import Path
from datetime import time as dt_time
import uuid

from adaptive_executor.criteria import CpuCriterion, MemoryCriterion, TimeCriterion


def _load_config_management_module():
    module_path = (
        Path(__file__).resolve().parents[1] / "examples" / "config_management.py"
    )
    spec = importlib.util.spec_from_file_location(
        "examples.config_management", module_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_load_configuration_from_fixture():
    module = _load_config_management_module()
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "scaling_config.json"

    criteria = module.load_configuration(fixture_path)

    assert len(criteria) == 3
    assert isinstance(criteria[0], TimeCriterion)
    assert isinstance(criteria[1], CpuCriterion)
    assert isinstance(criteria[2], MemoryCriterion)

    assert criteria[0].worker_count == 8
    assert criteria[0].active_start == dt_time(22, 0)
    assert criteria[0].active_end == dt_time(6, 0)
    assert criteria[0].tz.zone == "America/New_York"
    assert criteria[1].threshold == 75.0
    assert criteria[1].workers == 4
    assert criteria[2].threshold == 85.0
    assert criteria[2].workers == 6


def test_save_configuration_round_trip():
    module = _load_config_management_module()
    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    config_path = tmp_dir / f"roundtrip_config_{uuid.uuid4().hex}.json"

    source_criteria = [
        TimeCriterion(
            worker_count=5,
            active_start=dt_time(9, 0),
            active_end=dt_time(17, 0),
            timezone="UTC",
        ),
        CpuCriterion(threshold=60.0, workers=3),
        MemoryCriterion(threshold=70.0, workers=2),
    ]

    module.save_configuration(source_criteria, config_path)
    loaded = module.load_configuration(config_path)

    assert len(loaded) == 3
    assert loaded[0].to_dict() == source_criteria[0].to_dict()
    assert loaded[1].to_dict() == source_criteria[1].to_dict()
    assert loaded[2].to_dict() == source_criteria[2].to_dict()

    config_path.unlink(missing_ok=True)
