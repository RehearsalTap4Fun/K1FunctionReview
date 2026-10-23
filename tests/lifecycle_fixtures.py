import json
import subprocess
import shutil
import uuid
from copy import deepcopy
from pathlib import Path
import pytest
from conftest import run_git
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "review-k1-function/scripts/render-fast-precheck.py"
DISCLAIMER = "这是静态预审结果，不代表功能验收通过。"


def completed_alignment(metadata):
    return {
        "schemaVersion": 1,
        "status": "completed",
        "comparisonSummary": "逐条覆盖需求 REQ-01 至 REQ-04，并核对三端累计变更及最终状态；无需求变化。",
        "document": {
            "source": metadata["documentSource"],
            "beforeVersion": metadata["documentVersion"],
            "afterVersion": metadata["documentVersion"],
            "writeStatus": "unchanged",
            "readBackVerified": True,
        },
        "repositories": metadata["repositories"],
        "changes": [],
    }

def evidence(repository: str, path: str, summary: str) -> dict[str, str]:
    return {
        "repository": repository,
        "ref": "2" * 40,
        "path": path,
        "locator": "L10",
        "summary": summary,
    }

def valid_payload() -> dict[str, object]:
    payload = {
        "metadata": {
            "feature": "NK-8604",
            "documentSource": "https://example.invalid/dev-doc",
            "documentVersion": "doc-sha256",
            "startedAt": "2026-08-04T01:00:00Z",
            "finishedAt": "2026-08-04T01:05:21Z",
            "elapsedSeconds": 321,
            "deadlineSeconds": None,
            "testcaseDocumentVersion": "doc-sha256",
            "cache": {"hit": False, "kinds": []},
            "repositories": [
                {"role": "client", "base": "1" * 40, "target": "2" * 40},
                {"role": "server", "base": "1" * 40, "target": "2" * 40},
                {"role": "config", "base": "1" * 40, "target": "2" * 40},
            ],
            "disclaimer": DISCLAIMER,
        },
        "requirements": [
            {
                "id": "REQ-01",
                "title": "主流程 <script>alert(1)</script>",
                "documentLocator": "功能/主流程",
                "expectation": "请求与返回闭环",
                "testcaseIds": ["TC-MAIN-01"],
                "evidence": [evidence("client", "ui/main.lua", "调用请求")],
                "result": "静态证据充分",
                "explanation": "客户端和服务端契约一致",
                "runtimeAction": "运行验收主流程",
            },
            {
                "id": "REQ-02",
                "title": "配置边界",
                "documentLocator": "功能/配置",
                "expectation": "正式表包含目标 ID",
                "testcaseIds": ["TC-BOUNDARY-01"],
                "evidence": [evidence("config", "Table.xlsx", "目标 ID 缺失")],
                "result": "存在明显缺口",
                "explanation": "正式配置缺少必需行",
                "runtimeAction": "修正后核对配置",
            },
            {
                "id": "REQ-03",
                "title": "异常返回",
                "documentLocator": "功能/异常",
                "expectation": "资源不足返回错误码",
                "testcaseIds": ["TC-ABNORMAL-01"],
                "evidence": [evidence("server", "handler.ts", "存在保护分支")],
                "result": "证据不完整",
                "explanation": "一跳内未见客户端提示映射",
                "runtimeAction": "验证错误提示",
            },
            {
                "id": "REQ-04",
                "title": "动画表现",
                "documentLocator": "功能/表现",
                "expectation": "播放完成动画",
                "testcaseIds": ["TC-ANIMATION-01"],
                "evidence": [],
                "result": "无法确认",
                "explanation": "必须运行确认",
                "runtimeAction": "观察动画与时序",
            },
        ],
        "findings": [
            {
                "id": "FIND-01",
                "type": "阻断",
                "requirementIds": ["REQ-02"],
                "title": "正式配置缺行",
                "evidence": [evidence("config", "Table.xlsx", "目标 ID 缺失")],
                "impact": "功能无法按文档开启",
                "action": "补齐正式配置后再提测",
            },
            {
                "id": "FIND-02",
                "type": "风险",
                "requirementIds": ["REQ-03"],
                "title": "提示映射证据不完整",
                "evidence": [evidence("server", "handler.ts", "只见服务端错误码")],
                "impact": "客户端可能无明确反馈",
                "action": "运行验收错误路径",
            },
            {
                "id": "FIND-03",
                "type": "无法确认",
                "requirementIds": ["REQ-04"],
                "title": "动画需运行确认",
                "evidence": [],
                "impact": "静态证据不能判断表现",
                "action": "运行客户端观察",
            },
        ],
        "reviewChecks": [],
        "testcases": [
            {
                "id": "TC-ANIMATION-01", "category": "主流程", "requirementIds": ["REQ-04"],
                "precondition": "功能主流程结束", "action": "运行客户端观察动画",
                "expected": "按文档播放完成动画", "source": "开发文档/表现", "note": "需运行验收",
            },
            {
                "id": "TC-MAIN-01",
                "category": "主流程",
                "requirementIds": ["REQ-01"],
                "precondition": "功能开启",
                "action": "执行核心操作",
                "expected": "请求与返回符合开发文档",
                "source": "开发文档/主流程",
                "note": "运行行为另行验收",
            },
            {
                "id": "TC-BOUNDARY-01",
                "category": "关键边界",
                "requirementIds": ["REQ-02"],
                "precondition": "配置 ID=n",
                "action": "检查正式配置目标行",
                "expected": "与开发文档一致",
                "source": "开发文档/配置",
                "note": "配置仓库目标引用为准",
            },
            {
                "id": "TC-ABNORMAL-01",
                "category": "明显异常",
                "requirementIds": ["REQ-03"],
                "precondition": "资源不足",
                "action": "检查错误分支",
                "expected": "返回文档定义错误",
                "source": "开发文档/异常",
                "note": "客户端提示运行确认",
            },
        ],
        "overall": {
            "verdict": "建议修正后再提测",
            "reason": "发现一个有直接证据的阻断问题",
        },
        "readonlyCheck": {
            "beforeDigest": {"client": "a" * 64, "server": "b" * 64, "config": "c" * 64},
            "afterDigest": {"client": "a" * 64, "server": "b" * 64, "config": "c" * 64},
            "unchanged": True,
        },
        "limits": [
            {
                "source": "runtime",
                "reason": "动画必须运行确认",
                "affectedRequirementIds": ["REQ-04"],
            }
        ],
    }
    payload["alignment"] = completed_alignment(payload["metadata"])
    return payload

def renderer_source(project_tmp, payload):
    """Give presentation tests real frozen code instead of fabricated citations."""
    payload = deepcopy(payload)
    repo = project_tmp / "renderer-source"
    if not repo.exists():
        run_git(project_tmp, "init", str(repo))
        run_git(repo, "config", "user.name", "Renderer test")
        run_git(repo, "config", "user.email", "renderer@example.invalid")
        (repo / "ui").mkdir()
        (repo / "ui/main.lua").write_text("request()\n", encoding="utf-8")
        (repo / "handler.ts").write_text("throwError();\n", encoding="utf-8")
        run_git(repo, "add", ".")
        run_git(repo, "commit", "-m", "report evidence")
    target = run_git(repo, "rev-parse", "HEAD").stdout.strip()
    manifest = {"repositories": []}
    for item in payload["metadata"]["repositories"]:
        assert item["target"] == "2" * 40, "Use explicit manifest for non-placeholder snapshots"
        item["target"] = target
        manifest["repositories"].append({
            "role": item["role"], "repository": str(repo), "targetSha": target,
            "source": item.get("source", "local"),
        })
    snippets = {"ui/main.lua": "request()", "handler.ts": "throwError();"}
    owners = [*payload["requirements"], *payload["findings"], *payload["reviewChecks"],
              *payload.get("alignment", {}).get("changes", [])]
    for owner in owners:
        for entry in owner["evidence"]:
            entry["ref"] = target
            if entry["path"] in snippets:
                entry["snippet"] = snippets[entry["path"]]
    return payload, manifest

def run_renderer(
    project_tmp,
    reports_root,
    payload,
    *,
    env=None,
    manifest=None,
    git_evidence=None,
    rules=None,
):
    if manifest is None:
        payload, manifest = renderer_source(project_tmp, payload)
    manifest_path = project_tmp / f"manifest-{uuid.uuid4().hex}.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    if git_evidence is None:
        git_evidence = {
            "schemaVersion": 1,
            "status": "ok",
            "repositories": [
                {
                    "role": item["role"],
                    "target": {"sha": item["targetSha"]},
                    "changes": [],
                }
                for item in manifest["repositories"]
            ],
        }
    evidence_path = project_tmp / f"git-evidence-{uuid.uuid4().hex}.json"
    evidence_path.write_text(json.dumps(git_evidence), encoding="utf-8")
    rules_path = project_tmp / f"review-rules-{uuid.uuid4().hex}.json"
    rules_path.write_text(
        json.dumps(rules or {"schemaVersion": 1, "rules": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    input_path = project_tmp / f"result-{uuid.uuid4().hex}.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    completed = subprocess.run(
        [
            "python",
            str(SCRIPT),
            "--input",
            str(input_path),
            "--reports-root",
            str(reports_root),
            "--evidence-manifest",
            str(manifest_path),
            "--git-evidence",
            str(evidence_path),
            "--review-rules",
            str(rules_path),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    return completed

@pytest.fixture
def reports_root():
    root = PROJECT_ROOT / "reports" / f".pytest-{uuid.uuid4().hex}"
    root.mkdir(parents=True)
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)
