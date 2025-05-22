import csv
import random
from datetime import datetime, timedelta
import argparse


def generate_dataset(output_path: str, start_time: datetime, minutes: int = 1440):
    """Generate a simulated multi-sensor dataset with a fire ignition event."""
    ignition_start = start_time + timedelta(hours=12)
    ignition_end = ignition_start + timedelta(minutes=15)

    fieldnames = [
        "timestamp",
        "temperature_c",
        "humidity_pct",
        "co2_ppm",
        "smoke",
        "flame"
    ]

    with open(output_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        current_time = start_time
        for _ in range(minutes):
            row = {
                "timestamp": current_time.isoformat(),
                "temperature_c": round(random.uniform(18, 25), 2),
                "humidity_pct": round(random.uniform(35, 55), 2),
                "co2_ppm": round(random.uniform(400, 600), 2),
                "smoke": 0,
                "flame": 0,
            }

            if ignition_start <= current_time <= ignition_end:
                # escalate sensor readings to simulate fire
                progress = (current_time - ignition_start).total_seconds() / (
                    ignition_end - ignition_start
                ).total_seconds()
                row["temperature_c"] = round(25 + 75 * progress, 2)
                row["humidity_pct"] = round(30 - 20 * progress, 2)
                row["co2_ppm"] = round(600 + 500 * progress, 2)
                row["smoke"] = 1
                row["flame"] = 1 if progress > 0.3 else 0

            writer.writerow(row)
            current_time += timedelta(minutes=1)


def main():
    parser = argparse.ArgumentParser(description="Generate a demo FireSight dataset")
    parser.add_argument(
        "output",
        help="Path to output CSV file",
        default="demo_dataset.csv",
        nargs="?",
    )
    args = parser.parse_args()
    start = datetime(2025, 5, 11)
    generate_dataset(args.output, start)
    print(f"Dataset written to {args.output}")


if __name__ == "__main__":
    main()
