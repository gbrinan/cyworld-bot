# -*- coding: utf-8 -*-
"""세션2용 — 삼성이 공유한 매출 데이터 헤더(16열)로 가상 데이터와 대시보드를 만든다.
세션2 전반(대시보드)과 후반(데이터 분석·인사이트)이 같은 파일을 쓴다.
시드 고정이라 몇 번을 돌려도 같은 값이 나온다.
사용: python3 tools/build_session2_sample.py"""
import os, csv, random, datetime, collections
HERE=os.path.dirname(os.path.abspath(__file__)); AX=os.path.abspath(os.path.join(HERE,".."))
MOD=os.path.join(AX,"context_pack","modules","D_analysis")
D1=os.path.join(MOD,"01_데이터"); D3=os.path.join(MOD,"03_테스트")
D4=os.path.join(MOD,"04_기준본"); D6=os.path.join(MOD,"06_붙여넣기")
for d in (D1,D3,D4,D6): os.makedirs(d, exist_ok=True)
OUT=D4                                   # 대시보드 기준본이 나가는 곳
random.seed(20261002)

HEADER=["영업기회 번호","영업기회 유형","그룹명","파트명","판매처코드","판매처명","판매처 주소",
        "수요처코드","수요처명","영업기회명","매출일자","품목구분","모델명","주문유형","매출금액","매출수량"]

# 수요처 6곳 — 삼성 메일의 "고객사 숫자는 일관성 있게 6개로 유지" 안에 맞춤. 전부 가상.
ACCOUNTS=[("1000101","해솔호텔","호텔"),("1000204","대성건설","건설"),("1000311","한울종합건설","건설"),
          ("1000425","미래로병원","병원"),("1000538","세종교육재단","교육"),("1000642","서진리테일","유통")]
# 판매처 = 대리점. 헤더 설명의 "판매한 대리점 이름 (ex. oo정보통신)"을 따른다.
DEALERS=[("2000071","남해정보통신","부산광역시 해운대구 센텀중앙로 45"),
         ("2000088","동백시스템","부산광역시 해운대구 좌동순환로 12"),
         ("2000095","가야네트웍스","경상남도 김해시 분성로 221")]
ORG=[("한국총괄 B2B영업그룹","직판1파트"),("한국총괄 B2B영업그룹","직판2파트"),("한국총괄 B2B유통그룹","경로1파트")]

# (품목구분, [(모델명, 단가, 규격표기)]) — 규격표기는 영업기회명을 삼성 예시 형식으로 만들 때 쓴다.
# 품목구분은 헤더 설명의 예시(청소기, PC, TV 등)를 따라 청소기를 포함했다.
ITEMS=[("TV",[("HX-55T",1420000,"55인치"),("HX-65T",1980000,"65인치"),("BX-65S",2340000,"65인치")]),
       ("사이니지",[("SG-43C",1150000,"43인치"),("SG-55C",1760000,"55인치")]),
       ("모니터",[("MN-27Q",430000,"27인치"),("MN-32U",690000,"32인치")]),
       ("PC",[("DP-i5N",890000,"데스크톱"),("NB-i7P",1540000,"노트북")]),
       ("에어컨",[("AC-18W",1120000,"18평형")]),
       ("청소기",[("VC-20B",280000,"업소용"),("VC-35H",460000,"대용량")])]

rows=[]; seq=1
for mi in range(1,10):                      # 2026-01 ~ 2026-09
    # 3분기(7~9월)는 9월까지만 집계된 '덜 찬 분기'다. 건수도 금액도 작게 둬야
    # "덜 찬 기간을 다 찬 기간과 나란히 놓으면 줄어 보인다"는 실습 포인트가 성립한다.
    n = 7 if mi<=6 else 4
    for _ in range(n):
        code,acct,vert = random.choice(ACCOUNTS)
        item,models = random.choice(ITEMS)
        model,unit,spec = random.choice(models)
        qty = random.choice([2,3,4,5,8,10,12,20,30] if mi<=6 else [2,3,4,5,8,10])
        direct = random.random() < 0.6
        # 헤더 설명: "유통이 중간에 없다면 수요처명과 동일한 값이 들어감" — 직판이면 판매처 = 수요처
        if direct: scode,sname,saddr = code,acct,"—"
        else:      scode,sname,saddr = random.choice(DEALERS)
        grp,part = ORG[0] if direct and vert!="유통" else (ORG[2] if not direct else ORG[1])
        day = random.randint(1,28)
        # 영업기회명 — 헤더 설명의 예시 "해솔호텔 50인치 TV 납품건" 형식을 그대로 따른다
        rows.append([f"OPP-2026-{seq:04d}", random.choice(["선행영업","트렌드","트렌드"]), grp, part,
                     scode, sname, saddr, code, acct,
                     f"{acct} {spec} {item} 납품건", f"2026-{mi:02d}-{day:02d}",
                     item, model, "직판주문" if direct else "유통주문", unit*qty, qty])
        seq+=1
rows.sort(key=lambda r: r[10])

def write_csv(name, header, body, where=None):
    p=os.path.join(where or D1, name)
    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(header); w.writerows(body)
    return p

write_csv("매출데이터.csv", HEADER, rows)
TOTAL=sum(r[14] for r in rows)
print(f"01_데이터/매출데이터.csv  {len(rows)}행 · 수요처 {len({r[8] for r in rows})}곳 · "
      f"품목 {len({r[11] for r in rows})}종 · 합계 {TOTAL:,}원")

# ───────── 소계 파일 ─────────
# 이 헤더에는 단가 열이 없어 '단가 × 수량 = 금액' 검산을 할 수 없다.
# 대신 축별 소계를 따로 내려 주고, 참가자가 원본에서 다시 더해 대조하게 한다. 그게 이 모듈의 검산 장치다.
SUB=[]
for col,idx in [("품목구분",11),("주문유형",13),("수요처명",8)]:
    agg=collections.Counter(); cntc=collections.Counter()
    for r in rows: agg[r[idx]]+=r[14]; cntc[r[idx]]+=1
    for k,v in sorted(agg.items(), key=lambda x:-x[1]):
        SUB.append([col,k,cntc[k],v])
SUB.append(["전체","합계",len(rows),TOTAL])
write_csv("매출데이터_소계.csv", ["축","값","건수","합계"], SUB)
print(f"01_데이터/매출데이터_소계.csv  {len(SUB)}행 · 축 3개 + 전체 합계")

# ───────── 함정 파일 ─────────
# 일부러 어긋낸 판. 0번 점검이 무엇을 잡아야 하는지 가르치는 용도다.
# 단가가 없어 검산식을 못 쓰는 대신, 이 헤더에서 실제로 생길 수 있는 어긋남만 넣었다.
trap=[list(r) for r in rows]
TRAPS=[]

def find(pred, start=0):
    """조건에 맞는 첫 행을 찾는다. 행 번호를 손으로 박아 두면 데이터가 바뀔 때 조용히 엉뚱한 행이 망가진다."""
    for k in range(start, len(trap)):
        if pred(trap[k]): return k
    raise SystemExit("함정을 심을 행을 못 찾았다")

# ① 날짜 형식만 다르게 — 날짜 자체는 그대로 둔다
k=find(lambda r: r[10].startswith("2026-02"))
trap[k][10]=trap[k][10].replace("-","/")
TRAPS.append(f"{k+2}행 매출일자 {trap[k][10]} — 다른 행과 형식이 다름")

# ② 같은 수요처코드에 표기만 다른 이름 — 띄어쓰기 하나 차이여야 '표기 불일치'가 된다
k=find(lambda r: r[8]=="대성건설")
trap[k][8]="대성 건설"
TRAPS.append(f"{k+2}행 수요처명이 '대성 건설' — 같은 코드 {trap[k][7]}의 다른 행은 '대성건설'")

# ③ 영업기회 번호 중복
k=find(lambda r: True, 30)
trap[k][0]=trap[k-1][0]
TRAPS.append(f"{k+2}행 영업기회 번호가 {trap[k][0]}로 바로 앞 행과 중복")

# ④ 매출금액 음수
k=find(lambda r: int(r[14])>0, 40); trap[k][14]=-int(trap[k][14])
TRAPS.append(f"{k+2}행 매출금액이 음수")

# ⑤ 매출수량 0 — 금액은 그대로라 금액÷수량이 0으로 나뉜다
k=find(lambda r: int(r[15])>0, 48); trap[k][15]=0
TRAPS.append(f"{k+2}행 매출수량이 0")

write_csv("매출데이터_함정.csv", HEADER, trap, D3)
print(f"03_테스트/매출데이터_함정.csv  {len(trap)}행 · 심어 둔 어긋남 {len(TRAPS)}가지 "
      f"(합계 {sum(int(r[14]) for r in trap):,}원 — 소계 파일과 안 맞음)")
for t in TRAPS: print("   -", t)

# ───────── 붙여넣기본 ─────────
# 업로드가 막힌 환경에서 채팅창에 붙여넣는 표. 6KB를 넘으면 붙여넣기 자체가 실패한다.
# 16열을 그대로 담으면 한참 넘으므로 집계에 쓰는 열만 추린다. 무엇을 뺐는지 표 위에 적는다.
PASTE_COLS=["영업기회 번호","수요처명","매출일자","품목구분","모델명","주문유형","매출금액","매출수량"]
def md_table(header, body):
    out=["| "+" | ".join(header)+" |", "|"+"|".join("---" for _ in header)+"|"]
    for r in body: out.append("| "+" | ".join(str(c) for c in r)+" |")
    return "\n".join(out)

idx=[HEADER.index(c) for c in PASTE_COLS]
paste=md_table(PASTE_COLS, [[r[i] for i in idx] for r in rows])
open(os.path.join(D6,"매출데이터.md"),"w",encoding="utf-8").write(
 "# 매출데이터 (붙여넣기본)\n\n"
 "> 업로드가 막힌 환경에서 채팅창에 붙여넣는 표입니다. 원본은 `01_데이터/매출데이터.csv` 16열이고,\n"
 "> 여기에는 **집계에 쓰는 8열만** 담았습니다. 뺀 열: 영업기회 유형 · 그룹명 · 파트명 · 판매처코드 ·\n"
 "> 판매처명 · 판매처 주소 · 수요처코드 · 영업기회명.\n"
 "> **조직 필터는 이 표로 못 만듭니다.** 파트명이 빠져 있기 때문입니다. 업로드가 되는 환경에서는 원본을 쓰십시오.\n\n"
 + paste + "\n")
open(os.path.join(D6,"매출데이터_소계.md"),"w",encoding="utf-8").write(
 "# 매출데이터 소계 (붙여넣기본)\n\n"
 "> 축별 합계입니다. **검산 대조용**이고, 원본에서 직접 더한 값과 한 줄씩 맞춰 봅니다.\n\n"
 + md_table(["축","값","건수","합계"], SUB) + "\n")
for n in ("매출데이터.md","매출데이터_소계.md"):
    sz=os.path.getsize(os.path.join(D6,n))
    print(f"06_붙여넣기/{n}  {sz:,}B" + ("  ← 6KB 초과!" if sz>6*1024 else ""))
# ───────── 대시보드 HTML — 필터가 붙은 판 ─────────
import html as H, json

def qof(d): return d[:4] + "-Q" + str((int(d[5:7]) - 1) // 3 + 1)

D = [dict(zip(HEADER, r)) for r in rows]
for i, r in enumerate(D):
    r["매출금액"] = int(r["매출금액"]); r["매출수량"] = int(r["매출수량"])
    r["_n"] = i + 2                                   # 파일 행 번호. 헤더가 1행이다.

ROWS = [{"n": r["_n"], "q": qof(r["매출일자"]), "part": r["파트명"], "ord": r["주문유형"],
         "item": r["품목구분"], "acct": r["수요처명"], "amt": r["매출금액"],
         "qty": r["매출수량"], "opp": r["영업기회 번호"]} for r in D]

TOT = sum(r["amt"] for r in ROWS); CNT = len(ROWS)

# 품목구분 색은 '전체 데이터 기준'으로 한 번 정하고 고정한다.
# 필터로 순위가 바뀌어도 색이 따라 움직이면 안 된다 — 색은 항목을 따라가지 순위를 따라가지 않는다.
_amt = collections.Counter()
for r in ROWS: _amt[r["item"]] += r["amt"]
ITEM_ORDER = [k for k, _ in _amt.most_common()]
SLOTS = 6                                             # CSS에 정의된 --i0..--i5
if len(ITEM_ORDER) > SLOTS:
    raise SystemExit(f"품목구분이 {len(ITEM_ORDER)}종인데 색 슬롯은 {SLOTS}개다. CSS에 --i{SLOTS} 이상을 더하고 검증기를 다시 돌려라.")
ITEM_VAR = {k: "var(--i%d)" % i for i, k in enumerate(ITEM_ORDER)}

QS    = sorted({r["q"] for r in ROWS})
PARTS = sorted({r["part"] for r in ROWS})
ORDS  = sorted({r["ord"] for r in ROWS})
LASTQ = QS[-1]                                        # 9월까지만 들어 있는 덜 찬 분기

def opts(vals):
    return "".join('<option value="%s">%s</option>' % (H.escape(v), H.escape(v))
                   for v in ["전체"] + list(vals))

CSS = """
:root{--paper:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--mute:#7a7873;--line:#e4e2db;--panel:#f3f2ee;
--accent:#2a78d6;--accent2:#eb6834;--good:#1baf7a;--bad:#c0392b;--rule:#d9d7d0;--field:#fff;
--i0:#2a78d6;--i1:#eb6834;--i2:#1baf7a;--i3:#eda100;--i4:#e87ba4;--i5:#008300}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mute:#9b998f;
--line:#343330;--panel:#242320;--accent:#3987e5;--accent2:#d95926;--good:#199e70;--bad:#e06a5a;--rule:#3a3936;--field:#2b2a27;
--i0:#3987e5;--i1:#d95926;--i2:#199e70;--i3:#c98500;--i4:#d55181;--i5:#008300}}
:root[data-theme="dark"]{--paper:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mute:#9b998f;--line:#343330;--panel:#242320;
--accent:#3987e5;--accent2:#d95926;--good:#199e70;--bad:#e06a5a;--rule:#3a3936;--field:#2b2a27;
--i0:#3987e5;--i1:#d95926;--i2:#199e70;--i3:#c98500;--i4:#d55181;--i5:#008300}
html{color-scheme:light dark}
body{margin:0;background:var(--paper);color:var(--ink);font-size:15px;line-height:1.6;
font-family:'IBM Plex Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:900px;margin:0 auto;padding:36px 20px 72px}
.eyebrow{font-size:12px;letter-spacing:.1em;color:var(--accent);font-weight:600;text-transform:uppercase}
h1{font-size:26px;margin:6px 0 4px;line-height:1.3}
.src{color:var(--mute);font-size:13px;margin:0 0 20px}
h2{font-size:17px;margin:34px 0 10px;padding-top:14px;border-top:1px solid var(--rule)}
h3{font-size:15px;margin:22px 0 4px;color:var(--ink2)}
/* 필터 — 차트 위 한 줄. 차트 안에 넣지 않는다. */
.filters{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:flex-end;
background:var(--panel);border:1px solid var(--line);padding:12px 14px;margin:0 0 10px}
.filters label{display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--mute)}
.filters select{font:inherit;font-size:14px;color:var(--ink);background:var(--field);
border:1px solid var(--rule);border-radius:3px;padding:6px 8px;min-width:132px}
.filters button{font:inherit;font-size:13px;color:var(--ink2);background:transparent;
border:1px solid var(--rule);border-radius:3px;padding:7px 12px;cursor:pointer}
.filters button:hover{background:var(--field)}
.scope{font-size:13px;color:var(--ink2);margin:0 0 4px;padding:9px 12px;
border-left:3px solid var(--accent);background:var(--panel)}
.scope strong{color:var(--ink)}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:18px 0 6px}
@media(max-width:700px){.tiles{grid-template-columns:repeat(2,1fr)}.filters select{min-width:0}}
.tile{background:var(--panel);border:1px solid var(--line);padding:13px 14px}
.tile .k{font-size:12px;color:var(--mute);margin-bottom:5px}
.tile .v{font-size:21px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.2}
.tile .s{font-size:12px;color:var(--ink2);margin-top:5px}
table{border-collapse:collapse;width:100%;margin:8px 0 4px;font-size:14px}
th,td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}
thead th{font-size:12px;color:var(--mute);font-weight:600;border-bottom:1px solid var(--rule)}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.barcell{width:168px;padding-right:0;cursor:default}
.barcell:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.bar{display:block;height:9px;border-radius:0 4px 4px 0;min-width:2px}
/* 구성 막대 — 칸 사이는 2px 바탕색으로 띄운다 */
.stack{display:flex;height:28px;margin:10px 0 8px;background:var(--paper)}
.seg{height:100%;margin-right:2px;min-width:3px;cursor:default}
.seg:last-child{margin-right:0}
.seg:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;color:var(--ink2);margin:0 0 4px}
.legend span.k{display:inline-flex;align-items:center;gap:6px}
.legend i{width:11px;height:11px;border-radius:2px;display:inline-block}
.note{font-size:13px;color:var(--ink2);margin:6px 0 0}
.up{color:var(--good);font-weight:600}.down{color:var(--bad);font-weight:600}
.chk{background:var(--panel);border-left:3px solid var(--accent);padding:12px 15px;font-size:14px;margin-top:10px}
.chk p{margin:4px 0}
.empty{border:1px dashed var(--rule);padding:18px;color:var(--ink2);font-size:14px;margin:18px 0}
.empty p{margin:4px 0}
[hidden]{display:none}
.foot{margin-top:46px;padding-top:12px;border-top:1px solid var(--rule);font-size:12px;color:var(--mute)}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:13px}
#tip{position:fixed;z-index:9;pointer-events:none;opacity:0;transition:opacity .08s;
background:var(--ink);color:var(--paper);font-size:13px;line-height:1.45;padding:7px 10px;border-radius:4px;
box-shadow:0 2px 10px rgba(0,0,0,.22);max-width:260px}
#tip b{font-size:14px;font-variant-numeric:tabular-nums}
#tip .l{display:flex;align-items:center;gap:6px;color:#bdbbb3}
#tip .l i{width:12px;height:2px;display:inline-block}
"""

JS = r"""
const ROWS = __ROWS__, COLOR = __COLOR__, ITEM_ORDER = __ITEMS__,
      QS = __QS__, LASTQ = __LASTQ__, TOT = __TOT__, CNT = __CNT__;
const nf = new Intl.NumberFormat('ko-KR');
const $ = id => document.getElementById(id);
const fq = $('fq'), fp = $('fp'), fo = $('fo'), tip = $('tip');

function el(tag, cls, text){
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined && text !== null) n.textContent = String(text);  // 라벨은 데이터다. textContent로만 넣는다.
  return n;
}
function pct(a, b){ return b ? (a / b * 100) : 0; }

/* 툴팁 — 마크보다 넓은 칸 전체가 과녁이다 */
function bindTip(node, label, value, share, hue){
  const show = ev => {
    tip.replaceChildren();
    const l = el('div', 'l');
    if (hue){ const i = el('i'); i.style.background = hue; l.appendChild(i); }
    l.appendChild(el('span', null, label));
    tip.appendChild(el('b', null, nf.format(value) + '원'));
    if (share !== null) tip.appendChild(el('div', null, share.toFixed(1) + '%'));
    tip.appendChild(l);
    const r = node.getBoundingClientRect();
    const x = (ev && ev.clientX !== undefined) ? ev.clientX : r.left + r.width / 2;
    tip.style.opacity = '1';
    tip.style.left = Math.min(x + 14, innerWidth - tip.offsetWidth - 10) + 'px';
    tip.style.top  = Math.max(r.top - tip.offsetHeight - 8, 8) + 'px';
  };
  node.addEventListener('pointermove', show);
  node.addEventListener('focus', show);
  const hide = () => { tip.style.opacity = '0'; };
  node.addEventListener('pointerleave', hide);
  node.addEventListener('blur', hide);
}

function agg(list, key){
  const m = new Map();
  for (const r of list){
    const k = r[key], o = m.get(k) || { n: 0, v: 0 };
    o.n++; o.v += r.amt; m.set(k, o);
  }
  return [...m].map(([k, o]) => ({ k, n: o.n, v: o.v })).sort((a, b) => b.v - a.v);
}

function barTable(host, colName, items, sum, hue){
  const t = el('table'), th = el('thead'), tr = el('tr');
  for (const [lab, cls] of [[colName, ''], ['건수', 'num'], ['매출금액', 'num'], ['비중', 'num'], ['', '']])
    tr.appendChild(Object.assign(el('th', cls, lab), { scope: 'col' }));
  th.appendChild(tr); t.appendChild(th);
  const tb = el('tbody'), mx = Math.max(...items.map(i => i.v), 1);
  for (const it of items){
    const row = el('tr');
    row.appendChild(Object.assign(el('th', null, it.k), { scope: 'row' }));
    row.appendChild(el('td', 'num', nf.format(it.n)));
    row.appendChild(el('td', 'num', nf.format(it.v)));
    const sh = pct(it.v, sum);
    row.appendChild(el('td', 'num', sh.toFixed(1) + '%'));
    const cell = el('td', 'barcell'); cell.tabIndex = 0;
    const b = el('span', 'bar');
    const col = hue || COLOR[it.k] || 'var(--accent)';
    b.style.width = (it.v / mx * 100).toFixed(1) + '%'; b.style.background = col;
    cell.appendChild(b); bindTip(cell, it.k, it.v, sh, col);
    row.appendChild(cell); tb.appendChild(row);
  }
  t.appendChild(tb); host.appendChild(t);
}

function skewNote(items, sum){
  if (items.length <= 1) return items.length ? items[0].k + ' 하나뿐입니다.' : '';
  if (items.length === 2)   // 값이 둘뿐이면 "상위 2개가 100%"는 뜻이 없다. 격차를 적는다.
    return items[0].k + '이 ' + items[1].k + '보다 ' +
           (pct(items[0].v - items[1].v, sum)).toFixed(0) + '%p 큽니다.';
  return '상위 2개가 전체의 ' + pct(items[0].v + items[1].v, sum).toFixed(0) + '%.';
}

function render(){
  const s = { q: fq.value, p: fp.value, o: fo.value };
  const keep = (r, ignoreQ) =>
    (ignoreQ || s.q === '전체' || r.q === s.q) &&
    (s.p === '전체' || r.part === s.p) &&
    (s.o === '전체' || r.ord === s.o);

  const sel = ROWS.filter(r => keep(r, false));     // 화면 대부분이 보는 집합
  const cmp = ROWS.filter(r => keep(r, true));      // 분기 비교용 — 기간 필터만 뺀다

  /* 지금 보고 있는 것 */
  const sum = sel.reduce((a, r) => a + r.amt, 0);
  const scope = $('scope'); scope.replaceChildren();
  const cond = [s.q === '전체' ? '전체 기간' : s.q,
                s.p === '전체' ? '전체 조직' : s.p,
                s.o === '전체' ? '직판·유통 모두' : s.o].join(' · ');
  scope.appendChild(el('strong', null, '지금 보고 있는 것 — ' + cond));
  scope.appendChild(el('span', null,
    '  |  ' + nf.format(CNT) + '건 중 ' + nf.format(sel.length) + '건 · ' +
    '전체 금액 ' + nf.format(TOT) + '원의 ' + pct(sum, TOT).toFixed(1) + '%'));

  const ids = ['tiles', 'axes', 'quarters', 'notable'];
  ids.forEach(i => $(i).replaceChildren());
  const secs = ['s1', 's2', 's3', 's4'], box = $('emptybox');

  /* 0건이면 0을 그리지 않는다. 섹션을 통째로 접고 한 번만 알려 준다. */
  if (!sel.length){
    secs.forEach(i => { $(i).hidden = true; });
    box.hidden = false; box.replaceChildren();
    box.appendChild(el('p', null, '이 조건에 맞는 건이 없습니다.'));
    const loose = [];
    if (s.q !== '전체') loose.push('기간');
    if (s.p !== '전체') loose.push('조직');
    if (s.o !== '전체') loose.push('주문유형');
    box.appendChild(el('p', null,
      loose.join(' · ') + ' 중 하나를 "전체"로 되돌리면 다시 보입니다. ' +
      '빈 화면에 0을 그려 두면 실적이 0인 것처럼 보여서, 아예 비워 두고 이렇게 적습니다.'));
    location.hash = hashOf(s);
    return;
  }
  secs.forEach(i => { $(i).hidden = false; });
  box.hidden = true;

  /* 한눈에 */
  const cur  = s.q !== '전체' ? s.q : QS[QS.length - 2];   // 덜 찬 마지막 분기는 기본에서 뺀다
  const pi   = QS.indexOf(cur), prev = pi > 0 ? QS[pi - 1] : null;
  const qsum = q => cmp.filter(r => r.q === q).reduce((a, r) => a + r.amt, 0);
  const cv = qsum(cur), pvv = prev ? qsum(prev) : 0;
  const d  = (prev && pvv) ? (cv / pvv - 1) * 100 : null;

  const tiles = [
    ['매출금액 합계', nf.format(sum), '이 조건에서 직접 합산'],
    ['건수', nf.format(sel.length), '영업기회 ' + new Set(sel.map(r => r.opp)).size + '건'],
    ['건당 평균', nf.format(Math.round(sum / sel.length)), '합계 ÷ 건수'],
  ];
  for (const [k, v, sub] of tiles){
    const t = el('div', 'tile');
    t.appendChild(el('div', 'k', k)); t.appendChild(el('div', 'v', v)); t.appendChild(el('div', 's', sub));
    $('tiles').appendChild(t);
  }
  const t4 = el('div', 'tile');
  t4.appendChild(el('div', 'k', cur));
  t4.appendChild(el('div', 'v', nf.format(cv)));
  const s4 = el('div', 's');
  if (d === null) s4.appendChild(el('span', null, '비교 기간 데이터 없음'));
  else {
    s4.appendChild(el('span', d < 0 ? 'down' : 'up', (d >= 0 ? '+' : '') + d.toFixed(1) + '%'));
    s4.appendChild(el('span', null, ' · ' + prev + ' ' + nf.format(pvv)));
  }
  t4.appendChild(s4); $('tiles').appendChild(t4);

  /* 어디서 나왔나 */
  const axes = $('axes');
  const items = agg(sel, 'item');
  axes.appendChild(el('h3', null, '무엇이 팔렸나 · 품목구분'));

  const stack = el('div', 'stack');
  const byOrder = ITEM_ORDER.map(k => items.find(i => i.k === k)).filter(Boolean);  // 색 순서 고정
  for (const it of byOrder){
    const seg = el('div', 'seg'); seg.tabIndex = 0;
    seg.style.width = pct(it.v, sum).toFixed(2) + '%';
    seg.style.background = COLOR[it.k];
    seg.setAttribute('aria-label', it.k + ' ' + pct(it.v, sum).toFixed(1) + '%');
    bindTip(seg, it.k, it.v, pct(it.v, sum), COLOR[it.k]);
    stack.appendChild(seg);
  }
  axes.appendChild(stack);
  const lg = el('div', 'legend');
  for (const it of byOrder){
    const k = el('span', 'k'); const i = el('i'); i.style.background = COLOR[it.k];
    k.appendChild(i); k.appendChild(el('span', null, it.k + ' ' + pct(it.v, sum).toFixed(1) + '%'));
    lg.appendChild(k);
  }
  axes.appendChild(lg);
  if (byOrder.length < ITEM_ORDER.length)
    axes.appendChild(el('p', 'note',
      '필터로 ' + (ITEM_ORDER.length - byOrder.length) + '개 품목이 빠졌습니다. ' +
      '남은 품목의 색은 그대로입니다 — 색은 항목을 따라가지 순위를 따라가지 않습니다.'));
  barTable(axes, '품목구분', items, sum, null);
  axes.appendChild(el('p', 'note', skewNote(items, sum)));

  for (const [col, title, hue] of [['ord', '직판인가 유통인가 · 주문유형', 'var(--accent2)'],
                                   ['acct', '어느 고객에서 · 수요처명', 'var(--accent)']]){
    axes.appendChild(el('h3', null, title));
    const it = agg(sel, col);
    barTable(axes, col === 'ord' ? '주문유형' : '수요처명', it, sum, hue);
    axes.appendChild(el('p', 'note', skewNote(it, sum)));
  }

  /* 지난 기간과 견주면 — 기간 필터는 빼고 계산한다 */
  const qh = $('quarters');
  const qa = agg(cmp, 'q').sort((a, b) => a.k < b.k ? -1 : 1);
  const qtot = cmp.reduce((a, r) => a + r.amt, 0);
  const t = el('table'), th = el('thead'), tr = el('tr');
  for (const [lab, cls] of [['분기', ''], ['건수', 'num'], ['매출금액', 'num'], ['비중', 'num']])
    tr.appendChild(Object.assign(el('th', cls, lab), { scope: 'col' }));
  th.appendChild(tr); t.appendChild(th);
  const tb = el('tbody');
  for (const it of qa){
    const row = el('tr');
    row.appendChild(Object.assign(el('th', null, it.k + (it.k === LASTQ ? ' (덜 찬 분기)' : '')), { scope: 'row' }));
    row.appendChild(el('td', 'num', nf.format(it.n)));
    row.appendChild(el('td', 'num', nf.format(it.v)));
    row.appendChild(el('td', 'num', pct(it.v, qtot).toFixed(1) + '%'));
    tb.appendChild(row);
  }
  t.appendChild(tb); qh.appendChild(t);
  qh.appendChild(el('p', 'note',
    LASTQ + '은 9월까지만 들어 있어 분기 비교에서 뺐습니다. 덜 찬 기간을 다 찬 기간과 나란히 놓으면 무조건 줄어든 것처럼 보입니다.'));
  if (s.q !== '전체')
    qh.appendChild(el('p', 'note',
      '이 표만은 기간 필터를 빼고 계산합니다. 기간을 ' + s.q + '로 걸어 둔 채 분기를 견주면 비교할 상대가 사라집니다. 조직·주문유형 필터는 그대로 걸려 있습니다.'));

  /* 눈에 띄는 것 */
  const nh = $('notable');
  if (!prev){
    nh.appendChild(el('p', 'note', cur + ' 앞 분기가 없어 비교하지 못했습니다.'));
  } else {
    const pm = new Map(agg(cmp.filter(r => r.q === prev), 'item').map(i => [i.k, i.v]));
    const cm = new Map(agg(cmp.filter(r => r.q === cur),  'item').map(i => [i.k, i.v]));
    const out = [];
    for (const k of new Set([...pm.keys(), ...cm.keys()])){
      const a = pm.get(k) || 0, b = cm.get(k) || 0;
      if (!a){ out.push({ k, a, b, d: null }); continue; }
      const dd = (b / a - 1) * 100;
      if (Math.abs(dd) >= 20) out.push({ k, a, b, d: dd });
    }
    out.sort((x, y) => Math.abs(y.d ?? 999) - Math.abs(x.d ?? 999));
    nh.appendChild(el('p', 'note', prev + ' → ' + cur + ', 품목구분 기준 ±20% 이상 변동.'));
    const t2 = el('table'), th2 = el('thead'), tr2 = el('tr');
    for (const [lab, cls] of [['품목구분', ''], [prev, 'num'], [cur, 'num'], ['변동', 'num']])
      tr2.appendChild(Object.assign(el('th', cls, lab), { scope: 'col' }));
    th2.appendChild(tr2); t2.appendChild(th2);
    const tb2 = el('tbody');
    if (!out.length){
      const row = el('tr'), td = el('td', null, '기준에 걸린 항목 없음');
      td.colSpan = 4; td.style.color = 'var(--mute)'; row.appendChild(td); tb2.appendChild(row);
    }
    for (const o of out.slice(0, 5)){
      const row = el('tr');
      row.appendChild(Object.assign(el('th', null, o.k), { scope: 'row' }));
      row.appendChild(el('td', 'num', nf.format(o.a)));
      row.appendChild(el('td', 'num', nf.format(o.b)));
      row.appendChild(el('td', 'num', o.d === null ? '신규' : (o.d >= 0 ? '+' : '') + o.d.toFixed(0) + '%'));
      tb2.appendChild(row);
    }
    t2.appendChild(tb2); nh.appendChild(t2);
    nh.appendChild(el('p', 'note', '원인은 쓰지 않았습니다. 쓰려면 "가설"로 표시하고 확인 방법을 같이 적습니다.'));
  }
  location.hash = hashOf(s);
}

/* 걸어 둔 조건은 주소에 남는다 — 회의에서 "그거 다시" 할 때 링크 하나면 된다 */
function hashOf(s){
  return 'q=' + encodeURIComponent(s.q) + '&p=' + encodeURIComponent(s.p) + '&o=' + encodeURIComponent(s.o);
}
function readHash(){
  const h = new URLSearchParams(location.hash.replace(/^#/, ''));
  const put = (selEl, v) => { if (v && [...selEl.options].some(o => o.value === v)) selEl.value = v; };
  put(fq, h.get('q')); put(fp, h.get('p')); put(fo, h.get('o'));
}
[fq, fp, fo].forEach(n => n.addEventListener('change', render));
$('reset').addEventListener('click', () => { fq.value = fp.value = fo.value = '전체'; render(); });
readHash(); render();
"""

JS = (JS.replace("__ROWS__",  json.dumps(ROWS, ensure_ascii=False))
        .replace("__COLOR__", json.dumps(ITEM_VAR, ensure_ascii=False))
        .replace("__ITEMS__", json.dumps(ITEM_ORDER, ensure_ascii=False))
        .replace("__QS__",    json.dumps(QS, ensure_ascii=False))
        .replace("__LASTQ__", json.dumps(LASTQ, ensure_ascii=False))
        .replace("__TOT__",   str(TOT)).replace("__CNT__", str(CNT)))

html = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>영업 현황 대시보드 — 기준본</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600;700&family=IBM+Plex+Mono:wght@400&display=swap">
<style>__CSS__</style></head><body><div class="wrap">
<div class="eyebrow">세션 2 · 대시보드 기준본</div>
<h1>한국총괄 B2B영업 매출 현황 — 2026-01 ~ 2026-09</h1>
<p class="src">자료 <span class="mono">매출데이터.csv</span> __CNT__행 · 수요처 6곳 · 모든 값은 가상입니다</p>

<div class="filters" role="group" aria-label="필터">
<label>기간<select id="fq">__OQ__</select></label>
<label>조직<select id="fp">__OP__</select></label>
<label>주문유형<select id="fo">__OO__</select></label>
<button id="reset" type="button">전체로 되돌리기</button>
</div>
<p class="scope" id="scope"></p>
<p class="note">필터는 <strong>차트 위 한 줄</strong>에만 둡니다. 표마다 따로 달면 숫자끼리 안 맞는 화면이 됩니다.</p>

<div class="empty" id="emptybox" hidden></div>

<section id="s1"><h2>한눈에</h2>
<div class="tiles" id="tiles"></div>
<p class="note">증감률 옆에 <strong>원래 값 두 개</strong>를 같이 둡니다. 비율만 있으면 크기를 알 수 없습니다.</p></section>

<section id="s2"><h2>어디서 나왔나</h2>
<div id="axes"></div></section>

<section id="s3"><h2>지난 기간과 견주면</h2>
<div id="quarters"></div></section>

<section id="s4"><h2>눈에 띄는 것</h2>
<div id="notable"></div></section>

<h2>확인 필요</h2>
<div class="chk">
<p>· 이 헤더에는 <strong>단가 열이 없어</strong> <span class="mono">단가 × 수량 = 금액</span> 검산을 할 수 없습니다. 대신 <span class="mono">매출데이터_소계.csv</span>의 축별 합계와 대조했고 <strong>전부 일치</strong>합니다. 단가 열을 넣을지 확인 필요.</p>
<p>· 모델명은 가상입니다. 헤더 설명이 "인터넷에 조회되는 그 제품 모델명"이라, <strong>실제 모델명으로 바꿔 주시면 그대로 반영</strong>하겠습니다. 세션3에서 사양을 찾아보는 흐름과도 이어집니다.</p>
<p>· 판매처 주소는 직판주문일 때 값이 없어 <span class="mono">—</span>로 두었습니다.</p>
<p>· 영업기회 번호가 한 건에 하나씩이라 영업기회 단위 집계와 매출 단위 집계가 같습니다. 한 영업기회에 여러 번 매출이 잡히는 경우가 실제로 있는지 확인 필요.</p>
<p>· 파트명과 주문유형이 1:1로 묶여 있습니다(직판파트는 직판주문만, 경로파트는 유통주문만). 실제로 직판파트가 유통주문을 가져가는 경우가 있는지 확인 필요.</p>
<p>· 필터는 셋만 뒀습니다. 기간 · 조직 · 주문유형입니다. 품목구분과 수요처명은 표에서 바로 보이니 필터로 또 두지 않았습니다.</p>
<p>· 걸어 둔 조건은 주소창에 남습니다. 링크를 그대로 복사해 보내면 상대도 같은 화면을 봅니다.</p>
</div>

<div class="foot">세션 2 기준본 · 모든 수요처명 · 모델명 · 금액은 가상이며 삼성전자 실제 정보와 무관합니다</div>
</div><div id="tip" role="status" aria-live="polite"></div>
<script>__JS__</script></body></html>"""

html = (html.replace("__CSS__", CSS).replace("__CNT__", str(CNT))
            .replace("__OQ__", opts(QS)).replace("__OP__", opts(PARTS)).replace("__OO__", opts(ORDS))
            .replace("__JS__", JS))
open(os.path.join(OUT, "대시보드.html"), "w", encoding="utf-8").write(html)
print("04_기준본/대시보드.html  필터 3개(기간·조직·주문유형) · 합계 %s원 · %d행" % (f"{TOT:,}", CNT))
