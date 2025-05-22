import csv
import argparse
import time
from datetime import datetime


def replay_dataset(path: str, speed: float = 600.0):
    """Replay dataset rows to stdout at accelerated speed.

    Each row represents a minute. The speed factor represents how many
    dataset minutes pass per real second. Default is 600 (0.1 sec per minute).
    """
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        previous_time = None
        for row in reader:
            current_time = datetime.fromisoformat(row["timestamp"])
            if previous_time is not None:
                delta_minutes = (current_time - previous_time).total_seconds() / 60
                time.sleep(delta_minutes / speed)
            print(row)
            previous_time = current_time


def main():
    parser = argparse.ArgumentParser(description="Replay a FireSight demo dataset")
    parser.add_argument("dataset", help="Path to dataset CSV", default="demo_dataset.csv", nargs="?")
    parser.add_argument("--speed", type=float, default=600.0, help="Dataset minutes per real second")
    args = parser.parse_args()
    replay_dataset(args.dataset, args.speed)


if __name__ == "__main__":
    main()
