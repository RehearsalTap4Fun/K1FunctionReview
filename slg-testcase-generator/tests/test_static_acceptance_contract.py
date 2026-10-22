import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "static_acceptance_contract.py"


def valid_payload() -> dict:
    return {
        "schemaVersion": 1,
        "metadata": {
            "featureName": "合成验收功能",
            "documentSource": "C:\\fixture\\requirement.md",
            "documentHash": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "featureType": "B",
            "generatedAt": "2026-08-03T10:00:00+08:00",
            "manualSources": [],
        },
        "requirements": [{
            "requirementId": "REQ-001", "module": "次数限制",
            "requirement": "每日操作次数由配置控制", "documentLocator": "§2.1 次数限制",
            "expectedEnds": ["Client", "Server", "Config"],
            "conditions": [
                {"conditionId": "REQ-001-C01", "text": "服务端拒绝超过配置上限的请求", "core": True, "decisive": True, "verificationKind": "static"},
                {"conditionId": "REQ-001-C02", "text": "达到上限后按钮表现符合 UX", "core": False, "decisive": False, "verificationKind": "runtime"},
            ],
            "boundaries": ["n-1", "n", "n+1"], "dependencies": ["次数配置字段"],
        }],
        "staticCases": [{
            "caseId": "TC-REQ-001-S01", "requirementId": "REQ-001", "conditionIds": ["REQ-001-C01"],
            "module": "次数限制", "precondition": "当前次数=n",
            "checkAction": "检查服务端请求处理器在次数达到配置上限时拒绝请求且不写入状态",
            "expectedResult": "服务端以正式配置值为上限并保持状态不变", "expectedEnds": ["Server", "Config"],
            "documentLocator": "§2.1 次数限制", "priority": "P1", "remarks": "配置值使用 n，不写死示例值",
        }],
        "runtimeCases": [{
            "caseId": "TC-REQ-001-R01", "requirementId": "REQ-001", "conditionIds": ["REQ-001-C02"],
            "module": "次数限制", "precondition": "当前次数=n", "steps": "进入功能界面并观察达到上限后的按钮",
            "expectedResult": "按钮表现与权威 UX 一致", "expectedEnds": ["Client"],
            "documentLocator": "§2.1 次数限制", "priority": "常规", "remarks": "运行时验收",
        }],
        "manualCaseReconciliation": {"added": [], "unsupported": [], "conflicts": []},
    }


def run_contract(request: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(request), "--output", str(output)],
        capture_output=True, text=True, encoding="utf-8",
    )


def invoke_payload(tmp_path: Path, payload: dict):
    tmp_path.mkdir(parents=True, exist_ok=True)
    request = tmp_path / "request.json"
    output = tmp_path / "testcases.md"
    request.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return run_contract(request, output), output


def render_once(tmp_path: Path, payload: dict) -> bytes:
    result, output = invoke_payload(tmp_path, deepcopy(payload))
    assert result.returncode == 0
    return output.read_bytes()


def test_renders_five_section_markdown_with_stable_req_tc_links(tmp_path: Path):
    request = tmp_path / "request.json"
    output = tmp_path / "testcases.md"
    request.write_text(json.dumps(valid_payload(), ensure_ascii=False), encoding="utf-8")

    result = run_contract(request, output)

    assert result.returncode == 0
    assert json.loads(result.stdout)["code"] == "STATIC_TESTCASES_RENDERED"
    text = output.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("## ")] == [
        "## 1. 元数据",
        "## 2. 需求覆盖表",
        "## 3. 静态验收用例",
        "## 4. 运行验收附录",
        "## 5. 一致性结果",
    ]
    assert "| TC-REQ-001-S01 | REQ-001 |" in text
    assert "| TC-REQ-001-R01 | REQ-001 |" in text


def test_rejects_uncovered_decisive_static_condition_without_output(tmp_path: Path):
    payload = valid_payload()
    payload["staticCases"][0]["conditionIds"] = []
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_INVALID"
    assert {error["code"] for error in receipt["errors"]} == {"STATIC_CONDITION_UNCOVERED"}
    assert not output.exists()


def test_rejects_duplicate_case_id_and_dangling_requirement_in_one_receipt(tmp_path: Path):
    payload = valid_payload()
    duplicate = dict(payload["staticCases"][0])
    duplicate["requirementId"] = "REQ-999"
    payload["staticCases"].append(duplicate)
    result, output = invoke_payload(tmp_path, payload)
    codes = {error["code"] for error in json.loads(result.stdout)["errors"]}
    assert result.returncode == 1
    assert {"CASE_ID_DUPLICATE", "CASE_REQUIREMENT_UNKNOWN"} <= codes
    assert not output.exists()


def test_runtime_condition_cannot_be_claimed_by_static_case(tmp_path: Path):
    payload = valid_payload()
    payload["staticCases"][0]["conditionIds"] = ["REQ-001-C02"]
    result, _ = invoke_payload(tmp_path, payload)
    assert "CONDITION_KIND_MISMATCH" in {
        error["code"] for error in json.loads(result.stdout)["errors"]
    }


def test_invalid_payload_does_not_replace_existing_output(tmp_path: Path):
    payload = valid_payload()
    payload["staticCases"][0]["conditionIds"] = []
    output = tmp_path / "testcases.md"
    output.write_text("keep", encoding="utf-8")
    request = tmp_path / "request.json"
    request.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    result = run_contract(request, output)
    assert result.returncode == 1
    assert output.read_text(encoding="utf-8") == "keep"


def test_unsupported_manual_case_renders_only_in_consistency_section(tmp_path: Path):
    payload = valid_payload()
    payload["manualCaseReconciliation"]["unsupported"] = [{
        "source": "manual.md#M-7",
        "originalCaseId": "M-7",
        "reason": "开发文档没有定义离线补发",
    }]
    result, output = invoke_payload(tmp_path, payload)
    text = output.read_text(encoding="utf-8")
    static_section = text.split("## 3. 静态验收用例", 1)[1].split("## 4.", 1)[0]
    runtime_section = text.split("## 4. 运行验收附录", 1)[1].split("## 5.", 1)[0]
    assert result.returncode == 0
    assert "M-7" not in static_section + runtime_section
    assert "manual.md#M-7" in text.split("## 5. 一致性结果", 1)[1]


def test_supported_manual_case_keeps_source_after_merge(tmp_path: Path):
    payload = valid_payload()
    added_case = deepcopy(payload["staticCases"][0])
    added_case["caseId"] = "TC-REQ-001-S02"
    added_case["precondition"] = "当前次数=n+1"
    added_case["remarks"] = "人工来源 manual.md#M-2"
    payload["staticCases"].append(added_case)
    payload["manualCaseReconciliation"]["added"] = [{
        "source": "manual.md#M-2",
        "originalCaseId": "M-2",
        "caseId": "TC-REQ-001-S02",
        "reason": "补充文档支持的 n+1 边界",
    }]
    result, output = invoke_payload(tmp_path, payload)
    text = output.read_text(encoding="utf-8")
    assert result.returncode == 0
    static_section = text.split("## 3. 静态验收用例", 1)[1].split("## 4.", 1)[0]
    assert "TC-REQ-001-S02" in static_section
    assert "人工来源 manual.md#M-2" in static_section
    assert "补充文档支持的 n+1 边界" in text.split("## 5. 一致性结果", 1)[1]


def test_same_payload_renders_identical_bytes(tmp_path: Path):
    first = render_once(tmp_path / "first", valid_payload())
    second = render_once(tmp_path / "second", valid_payload())
    assert first == second


def test_case_order_is_canonical_not_input_order(tmp_path: Path):
    payload = valid_payload()
    second = deepcopy(payload["staticCases"][0])
    second["caseId"] = "TC-REQ-001-S02"
    payload["staticCases"] = [second, payload["staticCases"][0]]
    text = render_once(tmp_path, payload).decode("utf-8")
    assert text.index("TC-REQ-001-S01") < text.index("TC-REQ-001-S02")


def test_non_object_root_returns_an_invalid_json_receipt(tmp_path: Path):
    result, output = invoke_payload(tmp_path, [])
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_INVALID"
    assert not output.exists()


def test_invalid_case_id_type_returns_an_invalid_json_receipt(tmp_path: Path):
    payload = valid_payload()
    payload["staticCases"][0]["caseId"] = []
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_INVALID"
    assert "ID_FORMAT_INVALID" in {error["code"] for error in receipt["errors"]}
    assert not output.exists()


def test_missing_remarks_returns_invalid_receipt_without_replacing_output(tmp_path: Path):
    payload = valid_payload()
    del payload["staticCases"][0]["remarks"]
    output = tmp_path / "testcases.md"
    output.write_text("keep", encoding="utf-8")
    request = tmp_path / "request.json"
    request.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    result = run_contract(request, output)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_INVALID"
    assert output.read_text(encoding="utf-8") == "keep"


def test_case_without_any_conditions_is_rejected_even_when_static_condition_is_optional(tmp_path: Path):
    payload = valid_payload()
    payload["requirements"][0]["conditions"][0]["core"] = False
    payload["requirements"][0]["conditions"][0]["decisive"] = False
    payload["staticCases"][0]["conditionIds"] = []
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert "FIELD_REQUIRED" in {error["code"] for error in receipt["errors"]}
    assert not output.exists()


def test_missing_top_level_fields_are_aggregated_in_one_receipt(tmp_path: Path):
    result, output = invoke_payload(tmp_path, {"schemaVersion": 1})
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert {error["path"] for error in receipt["errors"]} == {
        "metadata", "requirements", "staticCases", "runtimeCases", "manualCaseReconciliation",
    }
    assert not output.exists()


def test_rejects_boolean_schema_version_and_non_string_content_fields(tmp_path: Path):
    payload = valid_payload()
    payload["schemaVersion"] = True
    payload["metadata"]["featureName"] = 1
    payload["requirements"][0]["requirement"] = ["not text"]
    payload["requirements"][0]["conditions"][0]["text"] = {"not": "text"}
    payload["staticCases"][0]["checkAction"] = 3
    payload["staticCases"][0]["expectedResult"] = False
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_INVALID"
    assert {error["path"] for error in receipt["errors"]} >= {
        "schemaVersion", "metadata.featureName", "requirements[0].requirement",
        "requirements[0].conditions[0].text", "staticCases[0].checkAction",
        "staticCases[0].expectedResult",
    }
    assert not output.exists()


def test_invalid_utf8_returns_one_json_error_receipt_without_output(tmp_path: Path):
    request = tmp_path / "request.json"
    output = tmp_path / "testcases.md"
    request.write_bytes(b"\xff")
    result = run_contract(request, output)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_ERROR"
    assert len(receipt["errors"]) == 1
    assert not output.exists()


def test_empty_reconciliation_does_not_claim_semantic_consistency(tmp_path: Path):
    result, output = invoke_payload(tmp_path, valid_payload())
    text = output.read_text(encoding="utf-8")
    assert result.returncode == 0
    assert "未提供人工用例对账项" in text
    assert "未发现差异" not in text


def test_invalid_schema_and_missing_top_level_fields_are_aggregated(tmp_path: Path):
    result, output = invoke_payload(tmp_path, {"schemaVersion": True})
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert {error["path"] for error in receipt["errors"]} == {
        "schemaVersion", "metadata", "requirements", "staticCases", "runtimeCases",
        "manualCaseReconciliation",
    }
    assert not output.exists()


def test_malformed_json_returns_one_json_error_receipt_without_output(tmp_path: Path):
    request = tmp_path / "request.json"
    output = tmp_path / "testcases.md"
    request.write_text("{", encoding="utf-8")
    result = run_contract(request, output)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_ERROR"
    assert len(receipt["errors"]) == 1
    assert not output.exists()


def test_output_filesystem_failure_returns_one_json_error_receipt(tmp_path: Path):
    request = tmp_path / "request.json"
    output = tmp_path / "missing" / "testcases.md"
    request.write_text(json.dumps(valid_payload(), ensure_ascii=False), encoding="utf-8")
    result = run_contract(request, output)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_ERROR"
    assert len(receipt["errors"]) == 1
    assert not output.exists()


def test_uncovered_runtime_condition_returns_invalid_receipt_without_output(tmp_path: Path):
    payload = valid_payload()
    payload["runtimeCases"][0]["conditionIds"] = []
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_INVALID"
    assert "RUNTIME_CONDITION_UNCOVERED" in {error["code"] for error in receipt["errors"]}
    assert not output.exists()


def test_case_id_embedded_requirement_mismatch_returns_invalid_receipt(tmp_path: Path):
    payload = valid_payload()
    payload["staticCases"][0]["caseId"] = "TC-REQ-999-S01"
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert "CASE_ID_REQUIREMENT_MISMATCH" in {error["code"] for error in receipt["errors"]}
    assert not output.exists()


def test_cross_requirement_condition_returns_invalid_receipt(tmp_path: Path):
    payload = valid_payload()
    second_requirement = deepcopy(payload["requirements"][0])
    second_requirement["requirementId"] = "REQ-002"
    second_requirement["conditions"][0]["conditionId"] = "REQ-002-C01"
    second_requirement["conditions"][1]["conditionId"] = "REQ-002-C02"
    payload["requirements"].append(second_requirement)
    payload["staticCases"][0]["conditionIds"] = ["REQ-002-C01"]
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert "CASE_CONDITION_REQUIREMENT_MISMATCH" in {error["code"] for error in receipt["errors"]}
    assert not output.exists()


def test_invalid_expected_ends_and_priority_return_invalid_receipt(tmp_path: Path):
    payload = valid_payload()
    payload["staticCases"][0]["expectedEnds"] = ["Database"]
    payload["staticCases"][0]["priority"] = "P9"
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert {"EXPECTED_END_INVALID", "FIELD_REQUIRED"} <= {
        error["code"] for error in receipt["errors"]
    }
    assert not output.exists()


def test_invalid_manual_reconciliation_returns_invalid_receipt(tmp_path: Path):
    payload = valid_payload()
    payload["manualCaseReconciliation"]["unsupported"] = [{
        "source": "", "originalCaseId": "M-9", "reason": "missing source",
    }]
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert "MANUAL_RECONCILIATION_INVALID" in {error["code"] for error in receipt["errors"]}
    assert not output.exists()


def test_missing_top_level_branch_does_not_hide_invalid_provided_branch(tmp_path: Path):
    payload = valid_payload()
    del payload["runtimeCases"]
    payload["metadata"]["featureName"] = 1
    result, output = invoke_payload(tmp_path, payload)
    receipt = json.loads(result.stdout)
    assert result.returncode == 1
    assert receipt["code"] == "STATIC_TESTCASES_INVALID"
    assert [(error["code"], error["path"]) for error in receipt["errors"]] == [
        ("FIELD_REQUIRED", "runtimeCases"),
        ("FIELD_REQUIRED", "metadata.featureName"),
    ]
    assert not output.exists()
