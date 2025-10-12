from .core import run_monitor

def main():
    from unifi2mqtt.lib.app_argparse import parse_args
    parse_args()
    run_monitor()

if __name__ == "__main__":
    main()