#!/usr/bin/env python3
"""
post_editor.py — a local WYSIWYG editor for writing Dev Journal drafts.

USAGE
    python3 scripts/post_editor.py
    (or double-click scripts/post_editor.bat)

Starts a small local web server and opens a writing tool in your browser.
Type your post, use the toolbar for headers/bold/italic/links, and click
"Insert Photo" to drop images in right where you're writing — you'll see
them inline as you go. Hit Save and it writes a draft folder straight into
drafts\, in the exact format scripts/new_post.py expects. From there, run
new_post.bat (or sync it in with --all) like any other draft.

Nothing here talks to the internet — it's a local server on your own
machine, at http://localhost:8934, only reachable from this computer.
"""

import base64
import json
import mimetypes
import os
import re
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

REPO_ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = REPO_ROOT / "drafts"
EDITOR_HTML = Path(__file__).resolve().parent / "post_editor.html"
PORT = 8934

MIME_EXT = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
}


def slugify(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "untitled"


def parse_frontmatter(text: str):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, val = line.split(":", 1)
        fm[key.strip()] = val.strip()
    return fm, body


def find_drafts():
    """Return a list of {slug, title, date, desc, skip} for every draft with a matching .md file."""
    results = []
    if not DRAFTS_DIR.exists():
        return results
    for md_path in sorted(DRAFTS_DIR.glob("*/*.md")):
        slug = md_path.parent.name
        if md_path.stem != slug:
            continue  # not this editor/script's naming convention, skip
        try:
            fm, _ = parse_frontmatter(md_path.read_text(encoding="utf-8"))
        except Exception:
            fm = {}
        results.append({
            "slug": slug,
            "title": fm.get("title", slug),
            "date": fm.get("date", ""),
            "desc": fm.get("desc", ""),
            "skip": str(fm.get("skip", "")).strip().lower() in ("true", "yes", "1"),
        })
    return results


def load_draft(slug: str):
    slug = slugify(slug)
    draft_dir = DRAFTS_DIR / slug
    md_path = draft_dir / f"{slug}.md"
    if not md_path.exists():
        return None

    fm, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))

    images = {}
    images_dir = draft_dir / "Images"
    if images_dir.exists():
        for img_path in images_dir.iterdir():
            if not img_path.is_file():
                continue
            mime, _ = mimetypes.guess_type(img_path.name)
            mime = mime or "application/octet-stream"
            b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
            images[img_path.name] = f"data:{mime};base64,{b64}"

    return {"slug": slug, "frontmatter": fm, "body": body, "images": images}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the console quiet

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            if not EDITOR_HTML.exists():
                self._send_json(500, {"ok": False, "error": "post_editor.html not found next to post_editor.py"})
                return
            body = EDITOR_HTML.read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        elif path == "/list-drafts":
            try:
                self._send_json(200, {"ok": True, "drafts": find_drafts()})
            except Exception as e:
                self._send_json(500, {"ok": False, "error": str(e)})
        elif path == "/load":
            qs = parse_qs(parsed.query)
            slug = (qs.get("slug") or [""])[0]
            if not slug:
                self._send_json(400, {"ok": False, "error": "Missing slug."})
                return
            try:
                result = load_draft(slug)
                if result is None:
                    self._send_json(404, {"ok": False, "error": f"No draft found for '{slug}'."})
                else:
                    self._send_json(200, {"ok": True, **result})
            except Exception as e:
                self._send_json(500, {"ok": False, "error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception as e:
            self._send_json(400, {"ok": False, "error": f"Bad request: {e}"})
            return

        if self.path == "/save":
            self._handle_save(data)
        elif self.path == "/open-folder":
            self._handle_open_folder(data)
        else:
            self._send_json(404, {"ok": False, "error": "Unknown endpoint"})

    def _handle_save(self, data: dict):
        try:
            title = (data.get("frontmatter", {}).get("title") or "").strip()
            if not title:
                self._send_json(400, {"ok": False, "error": "Title is required."})
                return

            slug = slugify(data.get("slug") or title)
            draft_dir = DRAFTS_DIR / slug
            images_dir = draft_dir / "Images"
            images_dir.mkdir(parents=True, exist_ok=True)

            # Write images
            for img in data.get("images", []):
                filename = img.get("filename")
                data_url = img.get("dataUrl", "")
                if not filename or "," not in data_url:
                    continue
                header, b64 = data_url.split(",", 1)
                raw_bytes = base64.b64decode(b64)
                (images_dir / filename).write_bytes(raw_bytes)

            # Build frontmatter
            fm = data.get("frontmatter", {})
            fm_lines = ["---"]
            for key in ["title", "date", "read", "desc", "aspect"]:
                val = fm.get(key, "")
                if val:
                    fm_lines.append(f"{key}: {val}")
            fm_lines.append("---")
            frontmatter_block = "\n".join(fm_lines)

            body = data.get("body", "").strip()
            md_content = f"{frontmatter_block}\n\n{body}\n"

            md_path = draft_dir / f"{slug}.md"
            md_path.write_text(md_content, encoding="utf-8")

            self._send_json(200, {"ok": True, "path": str(draft_dir), "slug": slug})
        except Exception as e:
            self._send_json(500, {"ok": False, "error": str(e)})

    def _handle_open_folder(self, data: dict):
        path = data.get("path")
        try:
            if path and Path(path).exists():
                if sys.platform.startswith("win"):
                    os.startfile(path)  # noqa
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["xdg-open", path])
            self._send_json(200, {"ok": True})
        except Exception as e:
            self._send_json(500, {"ok": False, "error": str(e)})


def main():
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Post editor running at {url}")
    print("Press Ctrl+C to stop.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
