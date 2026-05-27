#!/usr/bin/env python3
"""
Extract all text content from TdxQuant documentation pages.
Pages are VuePress SSR-rendered, so HTML contains the full content.
"""

import re
import time
import json
import tempfile
import subprocess
from pathlib import Path
from html.parser import HTMLParser

BASE_URL = "https://help.tdx.com.cn/quant"
ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "docs" / "web_docs"
CACHE_DIR = Path(tempfile.gettempdir())
ROUTE_FILE = CACHE_DIR / "tdxquant_content_pages.txt"
APP_JS_FILE = CACHE_DIR / "tdxquant_app.js"


def extract_routes_from_js(js_path=APP_JS_FILE):
    """Extract /docs/markdown/ routes from the VuePress app JS bundle."""
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    routes = set()
    for m in re.finditer(r'path:"(/docs/markdown/[^"]*)"', content):
        path = m.group(1)
        # Skip directory indexes and trailing slashes
        if path.endswith("/"):
            continue
        if path.endswith("/index.html"):
            continue
        # Skip .html duplicates - keep the canonical path
        if path.endswith(".html"):
            canonical = path[:-5]
            routes.add(canonical)
        else:
            routes.add(path)

    return sorted(routes)


def classify_pages(routes):
    """Split routes into content pages and section indexes."""
    sections = {}  # section_path -> [child_pages]
    standalone = []  # pages without children

    for r in routes:
        parts = r.split("/")
        # e.g. /docs/markdown/mindoc-xxx/child or /docs/markdown/TdxQuant.md/child
        if len(parts) == 5:  # has a parent section
            parent = "/".join(parts[:4])
            if parent not in sections:
                sections[parent] = []
            sections[parent].append(r)
        elif len(parts) == 4:  # top-level page or section index
            pass

    return sections


class ContentExtractor(HTMLParser):
    """Extract text from VuePress SSR-rendered HTML."""

    def __init__(self):
        super().__init__()
        self.in_content = False
        self.content_depth = 0
        self.skip_tags = {"script", "style"}
        self.skip_depth = 0
        self.parts = []
        self.title = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if "theme-default-content" in cls or "content__default" in cls:
            self.in_content = True
            self.content_depth = 0

        if self.in_content:
            self.content_depth += 1
            # Convert headings and table cells to text with spacing
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self.parts.append("\n\n## ")
            elif tag == "tr":
                self.parts.append("\n| ")
            elif tag in ("td", "th"):
                self.parts.append(" ")
            elif tag == "li":
                self.parts.append("\n- ")
            elif tag == "p":
                self.parts.append("\n\n")
            elif tag == "br":
                self.parts.append("\n")
            elif tag == "code":
                self.parts.append("`")
            elif tag == "pre":
                self.parts.append("\n```\n")

        if tag in self.skip_tags:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip_depth = max(0, self.skip_depth - 1)

        if self.in_content:
            self.content_depth -= 1
            if tag == "code":
                self.parts.append("`")
            elif tag == "pre":
                self.parts.append("\n```\n")
            if self.content_depth <= 0:
                self.in_content = False

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        if self.in_content:
            self.parts.append(data)

    def get_text(self):
        text = "".join(self.parts)
        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" +", " ", text)
        return text.strip()


def fetch_page(path):
    """Fetch a VuePress page and extract its text content."""
    # Try .html first, then try path as-is for .md suffixes
    if path.endswith(".md"):
        url = f"{BASE_URL}{path}"
    else:
        url = f"{BASE_URL}{path}.html"
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "15", url],
            capture_output=True, text=True, timeout=20
        )
        html = result.stdout
    except Exception as e:
        return None, f"fetch error: {e}"

    if not html or "404" in html[:500]:
        return None, "404 or empty"

    # Extract title
    title_match = re.search(r"<title>(.*?)</title>", html)
    title = title_match.group(1) if title_match else ""

    # Extract content
    parser = ContentExtractor()
    try:
        parser.feed(html)
    except Exception as e:
        return None, f"parse error: {e}"

    text = parser.get_text()
    if not text or len(text) < 20:
        return None, f"no content (len={len(text)})"

    return {"title": title, "text": text, "url": url, "path": path}, None


def get_section_name(path, all_pages_data):
    """Try to determine a readable section name from the path."""
    # Map of known section paths to names
    section_map = {
        "mindoc-1cfsjkbf8f3is": "TdxQuant概述",
        "ctx.stock.md": "通用函数",
        "mindoc-1ctuhthaq5qmg": "行情类信息",
        "TdxQuant.md": "财务类数据",
        "mindoc-1ctuhttn72svo": "分类板块成份股",
        "mindoc-1h139a4ckchkk": "自选股自定义板块",
        "mindoc-1h13a594nhvb4": "ETF可转债期货数据",
        "mindoc-1h3hrvkp4sc0g": "调用通达信公式",
        "mindoc-1h7k4iqb1grk4": "交易函数",
        "mindoc-1h1525ci3mnkc": "场景化示例",
        "gzh0122inweixinwenz": "公众号文章例子",
    }
    parts = path.strip("/").split("/")
    if len(parts) >= 3:
        section_key = parts[2]
        return section_map.get(section_key, section_key)
    return path


def main():
    print("=== TdxQuant Documentation Extractor ===\n")

    # Step 1: Get routes
    if ROUTE_FILE.exists():
        with open(ROUTE_FILE, encoding="utf-8") as f:
            routes = [l.strip() for l in f if l.strip()]
        print(f"Loaded {len(routes)} routes from cache")
    else:
        print("Extracting routes from JS bundle...")
        # Fetch fresh JS bundle
        js_url = f"{BASE_URL}/assets/js/app.effacf9c.js"
        subprocess.run(
            ["curl", "-s", "-o", str(APP_JS_FILE), js_url],
            capture_output=True, timeout=30
        )
        routes = extract_routes_from_js()
        print(f"Found {len(routes)} content routes")

    # Step 2: Filter out section indexes (pages that are just parents of children)
    # A section index like /docs/markdown/TdxQuant.md has children like /docs/markdown/TdxQuant.md/mindoc-xxx
    child_parents = set()
    for r in routes:
        parts = r.strip("/").split("/")
        if len(parts) >= 4:
            parent = "/" + "/".join(parts[:3])
            child_parents.add(parent)

    # Section indexes will be fetched too (they may have content)
    content_pages = [r for r in routes if not r.endswith("/")]

    # Step 3: Fetch all pages
    print(f"\nFetching {len(content_pages)} pages...")
    OUTPUT_DIR.mkdir(exist_ok=True)

    results = {}
    failed = []

    for i, path in enumerate(content_pages):
        section = get_section_name(path, results)
        url = f"{BASE_URL}{path}.html"
        print(f"  [{i+1}/{len(content_pages)}] {path}", end=" ... ", flush=True)

        data, err = fetch_page(path)
        if err:
            print(f"SKIP ({err})")
            failed.append((path, err))
            continue

        results[path] = data
        print(f"OK ({len(data['text'])} chars)")

        # Small delay to be polite
        if (i + 1) % 5 == 0:
            time.sleep(0.5)

    # Step 4: Organize and save
    print(f"\n=== Results ===")
    print(f"Successfully extracted: {len(results)} pages")
    print(f"Failed: {len(failed)} pages")

    # Save individual files organized by section
    sections_dir = OUTPUT_DIR / "sections"
    sections_dir.mkdir(exist_ok=True)

    # Group by section
    by_section = {}
    for path, data in results.items():
        section = get_section_name(path, results)
        if section not in by_section:
            by_section[section] = []
        by_section[section].append(data)

    for section, pages in sorted(by_section.items()):
        safe_name = re.sub(r"[^\w\-.]", "_", section)
        section_file = sections_dir / f"{safe_name}.md"
        with open(section_file, "w", encoding="utf-8") as f:
            f.write(f"# {section}\n\n")
            for p in pages:
                f.write(f"## {p['title']}\n\n")
                f.write(f"> Source: {p['url']}\n\n")
                f.write(p["text"])
                f.write("\n\n---\n\n")
        print(f"  Saved: {section_file} ({len(pages)} pages)")

    # Save one combined file
    combined_file = OUTPUT_DIR / "all_docs.md"
    with open(combined_file, "w", encoding="utf-8") as f:
        f.write("# TdxQuant 完整文档\n\n")
        f.write(f"Extracted from {BASE_URL}/docs/markdown/\n\n")
        f.write(f"Total pages: {len(results)}\n\n---\n\n")

        for section, pages in sorted(by_section.items()):
            f.write(f"# {section}\n\n")
            for p in pages:
                f.write(f"## {p['title']}\n\n")
                f.write(p["text"])
                f.write("\n\n---\n\n")

    print(f"\n  Combined: {combined_file}")

    # Save structured JSON
    json_file = OUTPUT_DIR / "docs.json"
    json_data = []
    for path, data in sorted(results.items()):
        json_data.append({
            "path": path,
            "url": data["url"],
            "title": data["title"],
            "text": data["text"],
        })
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"  JSON: {json_file}")

    if failed:
        print(f"\nFailed pages:")
        for path, err in failed:
            print(f"  {path}: {err}")

    print("\nDone!")


if __name__ == "__main__":
    main()
