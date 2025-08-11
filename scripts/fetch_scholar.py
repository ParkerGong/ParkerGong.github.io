from scholarly import scholarly
from jinja2 import Template
import json, pathlib

USER_ID = "nAjSpe0AAAAJ"  # 你的 Scholar user id
OUT_JSON = pathlib.Path("publications.json")
OUT_HTML = pathlib.Path("publications.html")

def fetch_pubs(uid):
    author = scholarly.search_author_id(uid)
    author = scholarly.fill(author, sections=["publications"])
    pubs = []
    for p in author["publications"]:
        bib = p.get("bib", {})
        pubs.append({
            "title": bib.get("title",""),
            "year": bib.get("pub_year") or bib.get("year"),
            "venue": bib.get("venue",""),
            "authors": bib.get("author",""),
            "cites": p.get("num_citations",0),
            "eprint": bib.get("eprint") or "",
            "url": p.get("pub_url") or "",
        })
    # 按年份降序
    pubs.sort(key=lambda x: (x["year"] or 0, x["cites"]), reverse=True)
    return pubs

TEMPLATE = Template("""
<!doctype html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Publications — Taiyuan (Parker) Gong</title>
<style>body{font:16px/1.6 system-ui;margin:24px auto;max-width:900px;padding:0 16px}
h1{margin:0 0 12px} .year{margin-top:18px;font-weight:700}
li{margin:8px 0}</style></head><body>
<h1>Publications</h1>
<p>Auto-synced from Google Scholar. Full profile:
<a href="https://scholar.google.com/citations?user={{ uid }}">Scholar</a></p>
{% for y, items in groups %}
<div class="year">{{ y }}</div>
<ol>
{% for p in items %}
<li><b>{{ p.title }}</b><br>
<em>{{ p.authors }}</em>. {{ p.venue }} ({{ p.year }})
{% if p.url %} · <a href="{{ p.url }}">Link</a>{% endif %}
{% if p.eprint %} · <a href="{{ p.eprint }}">PDF</a>{% endif %}
 · Cited by {{ p.cites }}
</li>
{% endfor %}
</ol>
{% endfor %}
</body></html>
""")

if __name__ == "__main__":
    pubs = fetch_pubs(USER_ID)
    OUT_JSON.write_text(json.dumps(pubs, ensure_ascii=False, indent=2))
    # 分组
    groups = {}
    for p in pubs:
        y = p["year"] or "In press"
        groups.setdefault(y, []).append(p)
    groups = sorted(groups.items(), key=lambda kv: str(kv[0]), reverse=True)
    OUT_HTML.write_text(TEMPLATE.render(uid=USER_ID, groups=groups), encoding="utf-8")
