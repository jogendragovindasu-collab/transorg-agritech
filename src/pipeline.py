"""
pipeline.py
------------
Purpose:
    - Orchestrate the full data pipeline:
        1. Load raw data from data/raw/
        2. Run all cleaning steps (crop, mandi, date, price, unit, weather)
        3. Run validation checks
        4. Save cleaned data to data/processed/
    - Designed to be run as:  python -m src.pipeline

TODO: Wire up cleaning and validation modules once they are implemented.
"""


def run_pipeline():
    """Execute the full cleaning + validation pipeline."""
    print("🌾 Pipeline not yet implemented. Waiting for cleaning modules.")


if __name__ == "__main__":
    run_pipeline()
