#!/usr/bin/env python3
"""Serve the generated local dashboard over the standard library HTTP server."""

from argparse import ArgumentParser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dashboards",
        help="Directory to serve.",
    )
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    os.chdir(args.directory)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), SimpleHTTPRequestHandler)
    print("Serving dashboard from %s on http://127.0.0.1:%s" % (args.directory, args.port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
