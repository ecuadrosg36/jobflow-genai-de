import argparse
from dotenv import load_dotenv
from jobflow.pipeline import run_once

load_dotenv()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--config", default="config/config.yaml")
    args = ap.parse_args()
    run_once(args.config)


if __name__ == "__main__":
    main()
