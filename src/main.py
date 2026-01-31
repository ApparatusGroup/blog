from orchestrator import Orchestrator
from scheduler import SchedulerService
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='AI Agents Blog runner')
    parser.add_argument('--mode', choices=['once', 'local'], default=os.getenv('RUN_MODE', 'once'), help='Run mode')
    parser.add_argument('--interval', type=int, default=60, help='Interval minutes for local mode')
    args = parser.parse_args()

    orch = Orchestrator()
    svc = SchedulerService(orch)

    if args.mode == 'once':
        svc.run_once()
    elif args.mode == 'local':
        svc.run_local(interval_minutes=args.interval)


if __name__ == "__main__":
    main()
