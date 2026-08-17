#!/usr/bin/env python3
import os
import sys
from ftplib import FTP

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_FILES = ("index.html", "support.js", "method.md", "faq.md")
REMOTE_DIR = "public_html/governments"


def _env(name):
    v = os.environ.get(name)
    if not v:
        sys.exit(
            f"{name} is not set. Copy .env.example to .env and fill it in, then\n"
            f"    set -a; source .env; set +a\n"
            f"before running this."
        )
    return v


def connect():
    ftp = FTP(_env("FTP_HOST"), timeout=30)
    ftp.login(_env("FTP_USER"), _env("FTP_PASS"))
    ftp.set_pasv(True)
    return ftp


def main():
    missing = [f for f in SITE_FILES if not os.path.isfile(os.path.join(HERE, f))]
    if missing:
        sys.exit(f"missing in {HERE}: {', '.join(missing)}")

    # support.js is generated from runtime/. A stale bundle silently ships the
    # previous UI, which looks like "my change did nothing" rather than an error.
    bundle = os.path.join(HERE, "support.js")
    newer = [
        f
        for f in ("index.html",)
        if os.path.getmtime(os.path.join(HERE, f)) > os.path.getmtime(bundle) + 3600
    ]
    if newer and os.path.isdir(os.path.join(HERE, "runtime")):
        print(f"note: {', '.join(newer)} is much newer than support.js —")
        print("      rebuild the runtime first if you changed it.")

    ftp = connect()
    try:
        for name in SITE_FILES:
            print(f"→ {REMOTE_DIR}/{name}")
            with open(os.path.join(HERE, name), "rb") as fp:
                ftp.storbinary(f"STOR {REMOTE_DIR}/{name}", fp)
    finally:
        ftp.quit()


if __name__ == "__main__":
    main()
