# /// script
# requires-python = ">=3.10"
# dependencies = ["atlassian-python-api>=3.41.0", "python-dotenv>=1.0.0", "requests>=2.31.0"]
# ///
"""Submit one K1 Jira issue from a UTF-8 JSON file."""

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ALLOWED = {
    "summary", "feature", "department", "bug_level", "version",
    "affect_version", "description", "expected", "actual", "assignee",
    "related_function", "attachment", "is_online_bug", "feedback_source",
    "reproduce_rate", "verify", "media_from_issue", "auto_media",
}
REQUIRED = {
    "summary", "feature", "department", "bug_level", "version",
    "affect_version", "description", "expected", "actual", "assignee",
    "reproduce_rate",
}


def read_payload(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    extra = set(payload) - ALLOWED
    missing = {key for key in REQUIRED if not isinstance(payload.get(key), str)
               or not payload[key].strip()}
    if extra or missing:
        raise ValueError(f"unknown fields: {sorted(extra)}; missing fields: {sorted(missing)}")
    if payload["department"] not in {"策划", "客户端", "服务器", "运营", "测试"}:
        raise ValueError("department must be a K1 Jira department")
    if payload["bug_level"] not in {"A", "B", "C", "D"}:
        raise ValueError("bug_level must be A, B, C or D")
    if payload["reproduce_rate"] not in {"Always", "High", "Medium", "Low", "Once"}:
        raise ValueError("invalid reproduce_rate")
    attachments = payload.get("attachment", [])
    if isinstance(attachments, str):
        attachments = [attachments]
    if not isinstance(attachments, list) or any(not isinstance(p, str) for p in attachments):
        raise ValueError("attachment must be a path or list of paths")
    absent = [p for p in attachments if not Path(p).is_file()]
    if absent:
        raise ValueError(f"missing attachment files: {absent}")
    payload["attachment"] = attachments
    payload.setdefault("auto_media", False)
    payload.setdefault("verify", True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    parser.add_argument("--check", action="store_true", help="validate locally without Jira access")
    args = parser.parse_args()
    try:
        payload = read_payload(args.json_file)
        if args.check:
            print("Payload valid; no Jira request sent")
            return 0
        module_path = Path(__file__).with_name("create-bug-cn.py")
        spec = importlib.util.spec_from_file_location("k1_jira_creator", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        result = module.SmartBugCreator(project="NK").create_bug(**payload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("success") else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
