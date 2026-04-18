"""
Colab bootstrap: mount Drive, set HF_TOKEN, ensure /content paths exist,
start a background rsync from /content/ckpt to Drive every 5 minutes.

Usage (from a Colab cell):
    !git clone https://github.com/<your-user>/lotl-fusion.git
    %cd lotl-fusion
    !pip install -q -r requirements.txt
    from scripts.colab_bootstrap import bootstrap
    bootstrap()
"""

import os
import subprocess
import time
import threading
from pathlib import Path


def _mount_drive():
    try:
        from google.colab import drive
        drive.mount('/content/drive', force_remount=True)
        print("Drive mounted at /content/drive")
    except ImportError:
        print("Not running in Colab — skipping Drive mount")
    except Exception as e:
        print(f"Drive mount failed: {type(e).__name__}: {e}")
        print("Retry this cell. If it keeps failing, checkpoints will live in "
              "/content/ckpt only (lost on session end).")


def _set_hf_token():
    try:
        from google.colab import userdata
        token = userdata.get('HF_TOKEN')
        if token:
            os.environ['HF_TOKEN'] = token
            os.environ['HUGGINGFACE_HUB_TOKEN'] = token
            print("HF_TOKEN loaded from Colab Secrets")
        else:
            print("HF_TOKEN not set in Colab Secrets — "
                  "unauthenticated rate limits will apply")
    except ImportError:
        pass
    except Exception as e:
        print(f"HF_TOKEN load failed: {e}")


def _ensure_dirs():
    for p in [
        '/content/data',
        '/content/ckpt',
        '/content/drive/MyDrive/lotl-fusion/data',
        '/content/drive/MyDrive/lotl-fusion/ckpt',
        '/content/drive/MyDrive/lotl-fusion/logs',
        '/content/drive/MyDrive/lotl-fusion/artifacts',
    ]:
        try:
            Path(p).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Could not create {p}: {e}")


def _rsync_loop(src, dst, interval_sec):
    while True:
        try:
            subprocess.run(
                ['rsync', '-a', '--delete-after', f'{src}/', f'{dst}/'],
                capture_output=True, timeout=60,
            )
        except Exception as e:
            print(f"[rsync] {e}")
        time.sleep(interval_sec)


def _start_rsync_daemon():
    src = '/content/ckpt'
    dst = '/content/drive/MyDrive/lotl-fusion/ckpt'
    if not Path(dst).parent.exists():
        print("Drive not mounted — rsync daemon not started")
        return
    t = threading.Thread(
        target=_rsync_loop, args=(src, dst, 300), daemon=True,
    )
    t.start()
    print(f"rsync daemon: {src} -> {dst} every 5 minutes")


def bootstrap(start_rsync=True):
    """One-call setup for Colab training notebooks."""
    _mount_drive()
    _set_hf_token()
    _ensure_dirs()
    if start_rsync:
        _start_rsync_daemon()
    print("\nBootstrap complete.")


if __name__ == '__main__':
    bootstrap()
