# -*- coding: utf-8 -*-
"""세션2 대시보드 제안용 — 삼성이 공유한 매출 데이터 헤더(16열)로 가상 데이터와 대시보드를 만든다.
시드 고정이라 몇 번을 돌려도 같은 값이 나온다.
사용: python3 tools/build_session2_sample.py"""
import os, csv, random, datetime, collections
HERE=os.path.dirname(os.path.abspath(__file__)); AX=os.path.abspath(os.path.join(HERE,".."))
OUT=os.path.join(AX,"세션2_대시보드_제안"); os.makedirs(OUT, exist_ok=True)
random.seed(20261002)

HEADER=["영업기회 번호","영업기회 유형","그룹명","파트명","판매처코드","판매처명","판매처 주소",
        "수요처코드","수요처명","영업기회명","매출일자","품목구분","모델명","주문유형","매출금액","매출수량"]

# 수요처 6곳 — 삼성 메일의 "고객사 숫자는 일관성 있게 6개로 유지" 안에 맞춤. 전부 가상.
ACCOUNTS=[("1000101","해솔호텔","호텔"),("1000204","대성건설","건설"),("1000311","한울종합건설","건설"),
          ("1000425","미래로병원","병원"),("1000538","세종교육재단","교육"),("1000642","서진리테일","유통")]
DEALERS=[("2000071","남해정보통신","부산광역시 해운대구 센텀중앙로 45"),
         ("2000088","동백시스템","부산광역시 해운대구 좌동순환로 12"),
         ("2000095","가야네트웍스","경상남도 김해시 분성로 221")]
ORG=[("한국총괄 B2B영업그룹","직판1파트"),("한국총괄 B2B영업그룹","직판2파트"),("한국총괄 B2B유통그룹","경로1파트")]
ITEMS=[("TV",[("HX-55T",1420000),("HX-65T",1980000),("BX-65S",2340000)]),
       ("사이니지",[("SG-43C",1150000),("SG-55C",1760000)]),
       ("모니터",[("MN-27Q",430000),("MN-32U",690000)]),
       ("PC",[("DP-i5N",890000),("NB-i7P",1540000)]),
       ("에어컨",[("AC-18W",1120000)])]
PURPOSE={"호텔":["객실 TV 교체","로비 사이니지"],"건설":["신축 현장 회의실","모델하우스 사이니지"],
         "병원":["대기실 사이니지","진료실 모니터"],"교육":["강의실 디스플레이","행정실 PC"],
         "유통":["매장 프로모션 사이니지","백오피스 PC"]}

rows=[]; seq=1
for mi in range(1,10):                      # 2026-01 ~ 2026-09
    n = 7 if mi<=6 else 5                   # 하반기로 갈수록 건수가 줄어드는 흐름
    for _ in range(n):
        code,acct,vert = random.choice(ACCOUNTS)
        item,models = random.choice(ITEMS)
        model,unit  = random.choice(models)
        qty = random.choice([2,3,4,5,8,10,12,20,30])
        direct = random.random() < 0.6
        if direct: scode,sname,saddr = code,acct,"—"
        else:      scode,sname,saddr = random.choice(DEALERS)
        grp,part = ORG[0] if direct and vert!="유통" else (ORG[2] if not direct else ORG[1])
        day = random.randint(1,28)
        rows.append([f"OPP-2026-{seq:04d}", random.choice(["선행영업","트렌드","트렌드"]), grp, part,
                     scode, sname, saddr, code, acct,
                     f"{acct} {random.choice(PURPOSE[vert])}", f"2026-{mi:02d}-{day:02d}",
                     item, model, "직판주문" if direct else "유통주문", unit*qty, qty])
        seq+=1
rows.sort(key=lambda r: r[10])
p=os.path.join(OUT,"매출데이터_예시.csv")
with open(p,"w",encoding="utf-8",newline="") as f:
    w=csv.writer(f); w.writerow(HEADER); w.writerows(rows)
print(f"매출데이터_예시.csv  {len(rows)}행 · 수요처 {len({r[8] for r in rows})}곳 · "
      f"합계 {sum(r[14] for r in rows):,}원")

# ───────── 대시보드 HTML ─────────
import html as H
def won(n): return f"{n:,}"
D=[dict(zip(HEADER,r)) for r in rows]
for r in D: r["매출금액"]=int(r["매출금액"]); r["매출수량"]=int(r["매출수량"])
tot=sum(r["매출금액"] for r in D); cnt=len(D); avg=tot//cnt
def q(d): return f"{d[:4]}-Q{(int(d[5:7])-1)//3+1}"
qs=collections.Counter()
for r in D: qs[q(r["매출일자"])]+=r["매출금액"]
qn=collections.Counter(q(r["매출일자"]) for r in D)
ql=sorted(qs)                      # 2026-Q1 .. Q3
cur,prev=ql[-2],ql[-3] if len(ql)>2 else ql[0]   # Q3는 9월까지만이라 비교에서 뺀다
delta=(qs[cur]/qs[prev]-1)*100

def axis(col):
    a=collections.Counter(); c=collections.Counter()
    for r in D: a[r[col]]+=r["매출금액"]; c[r[col]]+=1
    return [(k, c[k], v, v/tot*100) for k,v in a.most_common()]
AX_=[("품목구분","무엇이 팔렸나"),("주문유형","직판인가 유통인가"),("수요처명","어느 고객에서")]

# 눈에 띄는 것 — 직전 분기 대비 ±20% 이상 (품목구분 기준)
pv=collections.Counter(); cv=collections.Counter()
for r in D:
    if q(r["매출일자"])==prev: pv[r["품목구분"]]+=r["매출금액"]
    if q(r["매출일자"])==cur:  cv[r["품목구분"]]+=r["매출금액"]
notable=[]
for k in set(pv)|set(cv):
    a,b=pv.get(k,0),cv.get(k,0)
    if a==0: notable.append((k,a,b,None)); continue
    d=(b/a-1)*100
    if abs(d)>=20: notable.append((k,a,b,d))
notable.sort(key=lambda x: -(abs(x[3]) if x[3] is not None else 999))

def bars(items, hue="var(--accent)"):
    mx=max(v for _,_,v,_ in items) or 1
    out=[]
    for k,c,v,p in items:
        out.append(f'''<tr><th scope="row">{H.escape(k)}</th><td class="num">{c}</td><td class="num">{won(v)}</td>
<td class="num">{p:.1f}%</td><td class="barcell"><span class="bar" style="width:{v/mx*100:.1f}%;background:{hue}"></span></td></tr>''')
    return "\n".join(out)

CSS="""
:root{--paper:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--mute:#7a7873;--line:#e4e2db;--panel:#f3f2ee;
--accent:#2a78d6;--accent2:#eb6834;--good:#1baf7a;--bad:#c0392b;--rule:#d9d7d0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mute:#9b998f;
--line:#343330;--panel:#242320;--accent:#3987e5;--accent2:#d95926;--good:#199e70;--bad:#e06a5a;--rule:#3a3936}}
:root[data-theme="dark"]{--paper:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mute:#9b998f;--line:#343330;--panel:#242320;
--accent:#3987e5;--accent2:#d95926;--good:#199e70;--bad:#e06a5a;--rule:#3a3936}
html{color-scheme:light dark}
body{margin:0;background:var(--paper);color:var(--ink);font-size:15px;line-height:1.6;
font-family:'IBM Plex Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:900px;margin:0 auto;padding:36px 20px 72px}
.eyebrow{font-size:12px;letter-spacing:.1em;color:var(--accent);font-weight:600;text-transform:uppercase}
h1{font-size:26px;margin:6px 0 4px;line-height:1.3}
.src{color:var(--mute);font-size:13px;margin:0 0 26px}
h2{font-size:17px;margin:34px 0 10px;padding-top:14px;border-top:1px solid var(--rule)}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:18px 0 6px}
@media(max-width:700px){.tiles{grid-template-columns:repeat(2,1fr)}}
.tile{background:var(--panel);border:1px solid var(--line);padding:13px 14px}
.tile .k{font-size:12px;color:var(--mute);margin-bottom:5px}
.tile .v{font-size:21px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.2}
.tile .s{font-size:12px;color:var(--ink2);margin-top:5px}
table{border-collapse:collapse;width:100%;margin:8px 0 4px;font-size:14px}
th,td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}
thead th{font-size:12px;color:var(--mute);font-weight:600;border-bottom:1px solid var(--rule)}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.barcell{width:168px;padding-right:0}
.bar{display:block;height:9px;border-radius:0 4px 4px 0;min-width:2px}
.note{font-size:13px;color:var(--ink2);margin:6px 0 0}
.up{color:var(--good);font-weight:600}.down{color:var(--bad);font-weight:600}
.chk{background:var(--panel);border-left:3px solid var(--accent);padding:12px 15px;font-size:14px;margin-top:10px}
.chk p{margin:4px 0}
.foot{margin-top:46px;padding-top:12px;border-top:1px solid var(--rule);font-size:12px;color:var(--mute)}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:13px}
"""
sec=[]
for col,title in AX_:
    it=axis(col); top2=sum(v for _,_,v,_ in it[:2])/tot*100
    hue="var(--accent2)" if col=="주문유형" else "var(--accent)"
    # 값이 둘뿐인 축에 "상위 2개가 100%"를 쓰면 뜻이 없다. 그때는 둘의 격차를 적는다.
    if len(it)<=2:
        gap=(it[0][2]-it[1][2])/tot*100 if len(it)==2 else 100.0
        note=f"{H.escape(it[0][0])}이 {H.escape(it[1][0])}보다 <strong>{gap:.0f}%p</strong> 큽니다." if len(it)==2 \
             else f"{H.escape(it[0][0])} 하나뿐입니다."
    else:
        note=f"상위 2개가 전체의 <strong>{top2:.0f}%</strong>."
    sec.append(f"""<h3 style="font-size:15px;margin:20px 0 4px;color:var(--ink2)">{title} · {col}</h3>
<table><thead><tr><th>{col}</th><th class="num">건수</th><th class="num">매출금액</th><th class="num">비중</th><th></th></tr></thead>
<tbody>{bars(it,hue)}</tbody></table>
<p class="note">{note}</p>""")

qrows="".join(f'<tr><th scope="row">{k}</th><td class="num">{qn[k]}</td><td class="num">{won(qs[k])}</td>'
              f'<td class="num">{qs[k]/tot*100:.1f}%</td></tr>' for k in ql)
nrows="".join(
  f'<tr><th scope="row">{H.escape(k)}</th><td class="num">{won(a)}</td><td class="num">{won(b)}</td>'
  f'<td class="num">{"신규" if d is None else f"{d:+.0f}%"}</td></tr>' for k,a,b,d in notable) or \
  '<tr><td colspan="4" style="color:var(--mute)">기준에 걸린 항목 없음</td></tr>'

html=f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>영업 현황 대시보드 예시</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600;700&family=IBM+Plex+Mono:wght@400&display=swap">
<style>{CSS}</style></head><body><div class="wrap">
<div class="eyebrow">세션 2 · 대시보드 예시</div>
<h1>한국총괄 B2B영업 매출 현황 — 2026-01 ~ 2026-09</h1>
<p class="src">자료 <span class="mono">매출데이터_예시.csv</span> {cnt}행 · 수요처 6곳 · 모든 값은 가상입니다</p>

<h2>한눈에</h2>
<div class="tiles">
<div class="tile"><div class="k">매출금액 합계</div><div class="v">{won(tot)}</div><div class="s">직접 합산</div></div>
<div class="tile"><div class="k">건수</div><div class="v">{cnt}</div><div class="s">영업기회 {len({r["영업기회 번호"] for r in D})}건</div></div>
<div class="tile"><div class="k">건당 평균</div><div class="v">{won(avg)}</div><div class="s">합계 ÷ 건수</div></div>
<div class="tile"><div class="k">{cur}</div><div class="v">{won(qs[cur])}</div>
<div class="s"><span class="{'down' if delta<0 else 'up'}">{delta:+.1f}%</span> · {prev} {won(qs[prev])}</div></div>
</div>
<p class="note">증감률 옆에 <strong>원래 값 두 개</strong>를 같이 둡니다. 비율만 있으면 크기를 알 수 없습니다.</p>

<h2>어디서 나왔나</h2>
{"".join(sec)}

<h2>지난 기간과 견주면</h2>
<table><thead><tr><th>분기</th><th class="num">건수</th><th class="num">매출금액</th><th class="num">비중</th></tr></thead>
<tbody>{qrows}</tbody></table>
<p class="note"><strong>{ql[-1]}은 9월까지만 들어 있어 분기 비교에서 뺐습니다.</strong> 덜 찬 기간을 다 찬 기간과 나란히 놓으면 무조건 줄어든 것처럼 보입니다.</p>

<h2>눈에 띄는 것</h2>
<p class="note">{prev} → {cur}, 품목구분 기준 ±20% 이상 변동.</p>
<table><thead><tr><th>품목구분</th><th class="num">{prev}</th><th class="num">{cur}</th><th class="num">변동</th></tr></thead>
<tbody>{nrows}</tbody></table>
<p class="note">원인은 쓰지 않았습니다. 쓰려면 <strong>"가설"로 표시하고 확인 방법을 같이</strong> 적습니다.</p>

<h2>확인 필요</h2>
<div class="chk">
<p>· 매출금액 = 단가 × 매출수량 검산 — 이 헤더에는 단가 열이 없어 <strong>검산할 식이 없습니다.</strong> 단가 열을 넣을지 확인 필요.</p>
<p>· 판매처 주소는 직판주문일 때 값이 없어 <span class="mono">—</span>로 두었습니다.</p>
<p>· 영업기회 번호가 한 건에 하나씩이라 영업기회 단위 집계와 매출 단위 집계가 같습니다. 한 영업기회에 여러 번 매출이 잡히는 경우가 실제로 있는지 확인 필요.</p>
<p>· 축을 셋으로 줄였습니다. 그룹명 · 파트명 · 영업기회 유형도 열에 있으나 넣으면 표가 길어집니다.</p>
</div>

<div class="foot">세션 2 대시보드 제안 · 모든 수요처명 · 모델명 · 금액은 가상이며 삼성전자 실제 정보와 무관합니다</div>
</div></body></html>"""
open(os.path.join(OUT,"대시보드_예시.html"),"w",encoding="utf-8").write(html)
print(f"대시보드_예시.html  합계 {won(tot)}원 · {cur} {delta:+.1f}% · 눈에 띄는 것 {len(notable)}건")
