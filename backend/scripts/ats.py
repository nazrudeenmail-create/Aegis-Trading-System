import sys
import os
import argparse
import requests
import asyncio
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API details
API_BASE_URL = "http://localhost:8000/api/v1"
# For now, we'll use a dummy API key for the MVP or rely on defaults
HEADERS = {"X-API-Key": "dummy_key"}

def run_status():
    print("--- ATS System Status ---")
    try:
        res = requests.get(f"{API_BASE_URL}/system/status", headers=HEADERS)
        if res.status_code == 200:
            data = res.json()
            for k, v in data.items():
                print(f"{k.capitalize()}: {v}")
        else:
            print(f"Error fetching status: {res.status_code} - {res.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to ATS backend. Is it running?")

def run_health():
    print("--- ATS Health Check ---")
    try:
        # Assuming the root /health endpoint handles general health checks
        res = requests.get("http://localhost:8000/health")
        if res.status_code == 200:
            print("System OK")
            print(f"Details: {res.json()}")
        else:
            print(f"System degraded: {res.status_code} - {res.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to ATS backend. Is it running?")

def run_backtest(args):
    print(f"--- Running Backtest ---")
    print(f"Strategy: {args.strategy}")
    print(f"From: {args.start}")
    print(f"To: {args.end}")
    print("(Not connected to live engine in this MVP phase)")

def run_demo_trade(args):
    print(f"--- Starting Demo Trading ---")
    print(f"Duration: {args.duration} days")
    print("(Not connected to live engine in this MVP phase)")

def run_report():
    print("--- Strategy Intelligence Report ---")
    # For Phase 11, we will just call the demo_analytics script internally, or query the API.
    # We will run demo_analytics script directly to output the report.
    try:
        from demo_analytics import journal, print_report
        from app.analytics.reports import ReportGenerator
        from demo_analytics import generate_simulated_activity
        
        j = generate_simulated_activity()
        decisions = j.get_all_decisions()
        report = ReportGenerator.generate_intelligence_report(decisions)
        print_report(report)
    except Exception as e:
        print(f"Error generating report: {e}")

def run_logs(args):
    print(f"--- Fetching latest logs ({args.lines} lines) ---")
    log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "ats.log")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            lines = f.readlines()
            for line in lines[-args.lines:]:
                print(line.strip())
    else:
        print(f"Log file not found at {log_file}")

def main():
    parser = argparse.ArgumentParser(description="Aegis Trading System - CLI Utility")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status
    subparsers.add_parser("status", help="Get current ATS system status")

    # Health
    subparsers.add_parser("health", help="Check deployment health")

    # Backtest
    backtest_parser = subparsers.add_parser("backtest", help="Run historical backtest")
    backtest_parser.add_parser("backtest", help="Run historical backtest")
    backtest_parser.add_argument("--strategy", type=str, default="EMA", help="Strategy name")
    backtest_parser.add_argument("--start", type=str, default="2023-01-01", help="Start date (YYYY-MM-DD)")
    backtest_parser.add_argument("--end", type=str, default="2023-12-31", help="End date (YYYY-MM-DD)")

    # Demo Trade
    demo_parser = subparsers.add_parser("demo-trade", help="Start demo trading")
    demo_parser.add_argument("--duration", type=int, default=30, help="Duration in days")

    # Report
    subparsers.add_parser("report", help="Generate Strategy Intelligence Report")

    # Logs
    log_parser = subparsers.add_parser("logs", help="Tail latest system logs")
    log_parser.add_argument("-n", "--lines", type=int, default=50, help="Number of lines to tail")

    args = parser.parse_args()

    if args.command == "status":
        run_status()
    elif args.command == "health":
        run_health()
    elif args.command == "backtest":
        run_backtest(args)
    elif args.command == "demo-trade":
        run_demo_trade(args)
    elif args.command == "report":
        run_report()
    elif args.command == "logs":
        run_logs(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
