# -*- coding: utf-8 -*-
"""캔버스 아트보드를 팀별 슬라이드쇼 HTML(+PDF)로 묶는다 — **강의 순서**로.
순서의 정본은 ../../tools/build_course_docs.py 의 ORDER (워크북·강사 가이드의 슬라이드 번호와 같은 순서).
발표자 노트는 ../../deck/notes.json (같은 스크립트가 만든다) — 슬라이드쇼에서 N 키로 켜고 끈다.
사용: python3 build_deck.py  → ../../deck/A판.html, B판.html
PDF:  chrome --headless=new --no-pdf-header-footer --print-to-pdf=A판.pdf A판.html"""
import json, os, sys, html
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, ".."); AX = os.path.abspath(os.path.join(D, ".."))
OUT = os.path.join(AX, "deck")
sys.path.insert(0, os.path.join(AX, "tools"))
from build_course_docs import ORDER, SESSION_BREAKS  # noqa: E402 — import 시 notes.json · *_순서.txt 도 갱신된다
NOTES = json.load(open(os.path.join(OUT, "notes.json"), encoding="utf-8"))

def root_of(stem):
    s = open(os.path.join(D, stem + ".dc.html"), encoding="utf-8").read()
    i = s.index('<div style="width: 1280px; height: 720px;')
    j = s.rindex("</x-dc>")
    return s[i:j].rstrip()

CSS = """
html,body{margin:0;background:#2a2927;font-family:'IBM Plex Sans KR','Apple SD Gothic Neo','Noto Sans KR','Malgun Gothic',sans-serif;-webkit-font-smoothing:antialiased}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace}
a{color:#1c3f94}
.stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
body.notes-on .stage{inset:0 0 200px 0}
.slide{width:1280px;height:720px;flex-shrink:0;transform-origin:center center;box-shadow:0 12px 40px rgba(0,0,0,.4);display:none}
.slide.on{display:block}
.hud{position:fixed;right:16px;bottom:12px;color:#c9c5bd;font-size:13px;opacity:.7}
body.notes-on .hud{bottom:212px}
.notes{position:fixed;left:0;right:0;bottom:0;height:200px;box-sizing:border-box;padding:14px 24px;background:#111821;color:#fbfaf7;font-size:16px;line-height:1.55;overflow:auto;border-top:1px solid #3a3f47;display:none}
body.notes-on .notes{display:block}
.notes b{color:#e88b8b;font-weight:600}
.notes .t{color:#c9c5bd;font-size:13px;margin-bottom:6px}
.help{position:fixed;left:16px;bottom:12px;color:#c9c5bd;font-size:12px;opacity:.5}
body.notes-on .help{bottom:212px}
@media print{
  @page{size:1280px 720px;margin:0}
  html,body{background:#fff}
  .stage{position:static;display:block}
  .slide{display:block!important;transform:none!important;box-shadow:none;page-break-after:always;break-after:page;margin:0}
  .hud,.notes,.help{display:none!important}
}
"""
JS = """
const slides=[...document.querySelectorAll('.slide')];let i=0;
function fit(){const s=Math.min(innerWidth/1280,(innerHeight-(document.body.classList.contains('notes-on')?200:0))/720);slides.forEach(el=>el.style.transform='scale('+s+')')}
function show(n){i=(n+slides.length)%slides.length;slides.forEach((el,k)=>el.classList.toggle('on',k===i));
  const s=slides[i];document.querySelector('.hud').textContent=(i+1)+' / '+slides.length+' · '+s.dataset.session+' · '+s.dataset.name;
  const nt=document.querySelector('.notes');nt.innerHTML='<div class="t">'+(i+1)+' · '+s.dataset.name+' · '+s.dataset.session+'</div>'+(NOTES[String(i+1)]||[]).map(x=>'<div>'+x.replace(/^(파일|신호|되묻기):/,'<b>$1</b> ')+'</div>').join('');
  location.hash=i+1}
addEventListener('resize',fit);
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key))show(i+1);if(['ArrowLeft','PageUp'].includes(e.key))show(i-1);if(e.key==='Home')show(0);if(e.key==='End')show(slides.length-1);
  if(e.key==='n'||e.key==='N'){document.body.classList.toggle('notes-on');fit()}});
addEventListener('click',e=>{if(e.target.closest('.notes'))return;show(e.clientX>innerWidth/2?i+1:i-1)});
fit();show(parseInt(location.hash.slice(1)||'1',10)-1);
"""
os.makedirs(OUT, exist_ok=True)
for name, names in ORDER.items():
    parts = []; session = "1교시"
    for k, stem in enumerate(names, 1):
        session = SESSION_BREAKS[name].get(k, session)
        parts.append(f'<section class="slide" data-name="{html.escape(stem)}" data-session="{session}">\n{root_of(stem)}\n</section>')
    notes = {k: v for k, v in NOTES[name].items()}
    doc = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>삼성 B2B 영업 AI 에이전트 실습 — {name} ({len(names)}장)</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style></head>
<body><div class="stage">
{chr(10).join(parts)}
</div><div class="hud"></div><div class="help">← → 넘김 · N 노트 · Home/End</div><aside class="notes"></aside>
<script>const NOTES={json.dumps(notes, ensure_ascii=False)};{JS}</script></body></html>"""
    open(os.path.join(OUT, f"{name}.html"), "w", encoding="utf-8").write(doc)
    print(name, len(names), "장 — 강의 순서 · 노트", sum(1 for v in notes.values() if v), "장")
