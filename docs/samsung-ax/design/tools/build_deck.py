# -*- coding: utf-8 -*-
"""캔버스 아트보드를 팀별 슬라이드쇼 HTML(+PDF)로 묶는다.
A판 = 오프닝 · 일 보는 법·방법론 · D · A · C · Skill·클로징, B판 = A 대신 B.
사용: python3 build_deck.py  → ../deck/A판.html, B판.html (PDF는 별도 chrome 호출)"""
import json, os, re, html
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, ".."); OUT = os.path.join(D, "..", "deck")
canvas = json.load(open(os.path.join(D, "canvas.json"), encoding="utf-8"))
by_page = {}
for a in canvas["artboards"]:
    by_page.setdefault(a.get("page", "page-1"), []).append(a)
for pg in by_page: by_page[pg].sort(key=lambda a: (a["y"], a["x"]))
DECKS = {"A판": ["page-2", "page-3", "page-4", "page-5", "page-7", "page-8"],
         "B판": ["page-2", "page-3", "page-4", "page-6", "page-7", "page-8"]}
PAGE_NAME = {p["id"]: p["name"] for p in canvas.get("pages", [])}

def root_of(file):
    s = open(os.path.join(D, file), encoding="utf-8").read()
    i = s.index('<div style="width: 1280px; height: 720px;')
    j = s.rindex("</x-dc>")
    return s[i:j].rstrip()

CSS = """
html,body{margin:0;background:#2a2927;font-family:'IBM Plex Sans KR','Apple SD Gothic Neo','Noto Sans KR','Malgun Gothic',sans-serif;-webkit-font-smoothing:antialiased}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace}
a{color:#1c3f94}
.stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
.slide{width:1280px;height:720px;flex-shrink:0;transform-origin:center center;box-shadow:0 12px 40px rgba(0,0,0,.4);display:none}
.slide.on{display:block}
.hud{position:fixed;right:16px;bottom:12px;color:#c9c5bd;font-size:13px;opacity:.7}
@media print{
  @page{size:1280px 720px;margin:0}
  html,body{background:#fff}
  .stage{position:static;display:block}
  .slide{display:block!important;transform:none!important;box-shadow:none;page-break-after:always;break-after:page;margin:0}
  .hud{display:none}
}
"""
JS = """
const slides=[...document.querySelectorAll('.slide')];let i=0;
function fit(){const s=Math.min(innerWidth/1280,innerHeight/720);slides.forEach(el=>el.style.transform='scale('+s+')')}
function show(n){i=(n+slides.length)%slides.length;slides.forEach((el,k)=>el.classList.toggle('on',k===i));document.querySelector('.hud').textContent=(i+1)+' / '+slides.length+' · '+slides[i].dataset.name;location.hash=i+1}
addEventListener('resize',fit);addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key))show(i+1);if(['ArrowLeft','PageUp'].includes(e.key))show(i-1);if(e.key==='Home')show(0);if(e.key==='End')show(slides.length-1)});
addEventListener('click',e=>{show(e.clientX>innerWidth/2?i+1:i-1)});
fit();show(parseInt(location.hash.slice(1)||'1',10)-1);
"""
os.makedirs(OUT, exist_ok=True)
for name, pages in DECKS.items():
    parts = []; count = 0; order = []
    for pg in pages:
        for a in by_page.get(pg, []):
            stem = a["file"][:-8]; count += 1; order.append(f"{count:02d} {stem}")
            parts.append(f'<section class="slide" data-name="{html.escape(stem)}">\n{root_of(a["file"])}\n</section>')
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>삼성 B2B 영업 AI 에이전트 실습 — {name} ({count}장)</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style></head>
<body><div class="stage">
{chr(10).join(parts)}
</div><div class="hud"></div><script>{JS}</script></body></html>"""
    open(os.path.join(OUT, f"{name}.html"), "w", encoding="utf-8").write(doc)
    open(os.path.join(OUT, f"{name}_순서.txt"), "w", encoding="utf-8").write("\n".join(order) + "\n")
    print(name, count, "장")
