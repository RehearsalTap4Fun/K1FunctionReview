"""Record a version requirement conclusion and immediately drain its DingTalk outbox."""
import argparse
import json
from pathlib import Path
import sys

from acceptance.core import WorkflowError, read_json
from acceptance.progress import ProgressStore
from acceptance.robot import RobotClient


def execute(action, request, root, config_path=None):
    if action == 'check-config':
        return RobotClient(config_path).check()
    store = ProgressStore(root)
    if action == 'init':
        return store.initialize(request)
    if action == 'sync':
        return store.sync(request)
    if action == 'status':
        return store.status()
    if action == 'resolve':
        return store.resolve(request)
    if action == 'preview':
        return {'messages': [e['payload'] for e in store.read()['outbox'] if e['delivery'] != 'sent']}
    if action not in {'record', 'flush'}:
        raise WorkflowError('COMMAND_NOT_SUPPORTED')
    result = store.record(request) if action == 'record' else store.status()
    try:
        result['notification'] = store.flush(RobotClient(config_path))
    except (WorkflowError, OSError) as error:
        # A notification outage must not undo an accepted, durably recorded conclusion.
        result['notification'] = {'error': error.code if isinstance(error, WorkflowError) else 'NOTIFICATION_IO_ERROR'}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check-config', 'init', 'sync', 'record', 'flush', 'status', 'resolve', 'preview'])
    parser.add_argument('--store-dir', type=Path)
    parser.add_argument('--request', type=Path)
    parser.add_argument('--config', type=Path)
    args = parser.parse_args()
    if args.action != 'check-config' and not args.store_dir:
        parser.error('--store-dir is required')
    try:
        result = execute(args.action, read_json(args.request) if args.request else {}, args.store_dir, args.config)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (WorkflowError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': error.code if isinstance(error, WorkflowError) else type(error).__name__}))
        return 1


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
