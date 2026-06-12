import argparse
from pipeline import send_file, receive_file


def main():
    parser = argparse.ArgumentParser(
        description="End-to-end encrypted file sharing."
    )
    parser.add_argument("action", choices=["send", "receive"])
    parser.add_argument("target", help="File path (send) or share link (receive)")
    parser.add_argument("--output", default="received_file",
                        help="Output filename for receive (default: received_file)")
    args = parser.parse_args()

    if args.action == "send":
        send_file(args.target)
    else:
        receive_file(args.target, args.output)


if __name__ == "__main__":
    main()
