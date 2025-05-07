from .core import run_monitor

def main():
    import argparse
    from .utils import parse_args
    args = parse_args()
    run_monitor(args)

if __name__ == "__main__":
    main()