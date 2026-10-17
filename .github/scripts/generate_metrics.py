#!/usr/bin/env python3
"""
Clean, GitHub-Native Languages & Telemetry Generator
Generates:
  - assets/languages.svg (Proportional, sleek 38px language bar)
Runs via GitHub Actions or locally with zero third-party dependencies.
"""

import os
import sys
import json
import urllib.request
import subprocess

def get_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        try:
            token = subprocess.check_output(["gh", "auth", "token"]).decode().strip()
        except Exception:
            token = None
    return token

def fetch_github_data(token, username="chandranshB"):
    query = """query {
      user(login: "%s") {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
          totalCount
          nodes {
            name
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node { name color }
              }
            }
          }
        }
      }
    }""" % username

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "User-Agent": "Chandransh-Profile-Metrics/4.0"
        }
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
    return res["data"]["user"]

def generate_languages_bar_svg(data):
    """
    Generates a proportional, 38px tall, transparent language bar.
    100% native to GitHub.
    """
    repos = data["repositories"]["nodes"]

    repo_counts = {}
    lang_colors = {
        "TypeScript": "#3178c6",
        "Python": "#3572A5",
        "Rust": "#dea584",
        "Kotlin": "#A97BFF",
        "Astro": "#ff5a03",
        "Dart": "#00B4AB"
    }

    for r in repos:
        langs = set()
        for edge in r.get("languages", {}).get("edges", []):
            langs.add(edge["node"]["name"])
        for l in langs:
            repo_counts[l] = repo_counts.get(l, 0) + 1

    featured_langs = ["TypeScript", "Python", "Rust", "Kotlin", "Astro", "Dart"]
    counts = {k: repo_counts.get(k, 1) for k in featured_langs}
    total_core = sum(counts.values()) or 1

    bar_width = 832
    segments = []
    current_x = 0
    items = []
    for k in featured_langs:
        c = counts[k]
        pct = (c / total_core) * 100
        items.append((k, c, pct, lang_colors.get(k, "#8b949e")))

    for name, count, pct, color in items:
        w = max(16, (pct / 100) * bar_width)
        segments.append((name, count, pct, current_x, w, color))
        current_x += w

    # Scale to exactly bar_width
    scale = bar_width / sum(s[4] for s in segments)
    adjusted_segments = []
    acc_x = 0
    for name, count, pct, _, w, color in segments:
        new_w = w * scale
        adjusted_segments.append((name, count, pct, acc_x, new_w, color))
        acc_x += new_w

    bar_rects = []
    for name, count, pct, x, w, color in adjusted_segments:
        bar_rects.append(f'<rect x="{x:.1f}" y="2" width="{w:.1f}" height="6" fill="{color}" rx="3"/>')
    bar_str = "\n    ".join(bar_rects)

    legend_items = []
    lx = 0
    for name, count, pct, _, _, color in adjusted_segments:
        legend_items.append(f'''    <circle cx="{lx + 5}" cy="26" r="4" fill="{color}"/>
    <text x="{lx + 14}" y="30" fill="#e6edf3">{name} <tspan fill="#7d8590">{pct:.0f}%</tspan></text>''')
        lx += 138
    legend_str = "\n".join(legend_items)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 38" width="100%" height="38" fill="none">
  <!-- GitHub Native Proportional Language Bar -->
  <g>
    {bar_str}
  </g>

  <!-- Clean Typographic Legend -->
  <g font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="11" font-weight="500">
{legend_str}
  </g>
</svg>'''
    return svg

def main():
    token = get_token()
    if not token:
        print("Error: No GitHub token available.")
        sys.exit(1)

    print("Fetching GitHub statistics for chandranshB...")
    data = fetch_github_data(token, "chandranshB")

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    assets_dir = os.path.join(repo_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    print("Generating assets/languages.svg...")
    with open(os.path.join(assets_dir, "languages.svg"), "w", encoding="utf-8") as f:
        f.write(generate_languages_bar_svg(data))

    print("Done generating clean assets/languages.svg!")

if __name__ == "__main__":
    main()
