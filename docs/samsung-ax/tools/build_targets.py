# -*- coding: utf-8 -*-
"""세션3-1 대시보드용 '목표' 시트와 '시뮬레이션 샘플값' 시트를 만든다 (전부 가상).

- 매출목표.csv : 유통구분(직판/유통) × 품목구분 × 모델명 의 2026년 1~12월 월별 목표 금액
  · 줄 순서는 유통구분 → 품목 → 모델, 각각 매출데이터(시트1)에 처음 나온 순서 — 두 시트를 나란히 놓고 찾기 쉽게
  · 값 = 2025년 같은 달 실적 × 1.05, 10만원 단위 반올림. 2025년 그달 실적이 0이면 2025년 월평균 × 1.05
    (실제 사업계획이 없으니 '작년 같은 달 + 5%'라는 흔한 목표 설정 방식을 흉내 낸 샘플값이다)
- 시뮬레이션_샘플값.csv : 타사 이벤트 대응 시뮬레이션의 기본값 · 범위 · 어떻게 정했나 · 왜 필요한가
참가자는 아무것도 입력하지 않아도 이 값으로 결과를 보고, 원하면 숫자만 바꾼다.
"""
import csv, os, collections
AX = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(AX, "context_pack", "modules", "D_analysis", "01_데이터")
rows = list(csv.DictReader(open(os.path.join(D, "매출데이터.csv"), encoding="utf-8-sig")))

def ch(r): return "직판" if r["주문유형"] == "직판주문" else "유통"
order, act = [], collections.defaultdict(int)
for r in rows:
    k = (ch(r), r["품목구분"], r["모델명"])
    if k not in order: order.append(k)
    if r["매출일자"].startswith("2025-"):
        act[(k, int(r["매출일자"][5:7]))] += int(r["매출금액"])

# 유통구분 → 품목 → 모델 순으로 묶되, 각각 시트1에 처음 나온 순서를 따른다
def first(seq):
    return {v: i for i, v in enumerate(dict.fromkeys(seq))}
oc, oi, om = first(ch(r) for r in rows), first(r["품목구분"] for r in rows), first(r["모델명"] for r in rows)
order.sort(key=lambda k: (oc[k[0]], oi[k[1]], om[k[2]]))
def r10(v): return int(round(v / 100000.0)) * 100000
months = list(range(1, 13))
out = []
for k in order:
    avg = sum(act[(k, m)] for m in months) / 12.0
    vals = [r10((act[(k, m)] or avg) * 1.05) for m in months]
    out.append(list(k) + vals + [sum(vals)])
hdr = ["유통구분", "품목구분", "모델명"] + [f"2026-{m:02d} 목표" for m in months] + ["2026 연간 목표"]
with open(os.path.join(D, "매출목표.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(out)

SIM = [
 ("타사 이벤트 기간", "2026-10-01 ~ 2026-10-14", "날짜 두 개", "가상의 타사 할인 행사 2주", "언제 우리 매출이 흔들릴지 정해야 대응 기간을 잡을 수 있다"),
 ("겹치는 제품군", "모니터, PC", "품목구분에서 고름", "타사 행사 품목과 우리 품목 중 겹치는 것(가정)", "모든 품목이 아니라 겹치는 품목만 영향을 받는다"),
 ("시뮬레이션 기간", "2026-10-01 ~ 2026-10-31", "날짜 두 개", "타사 행사 + 끝난 뒤 2주", "행사가 끝난 뒤의 회복까지 봐야 손익이 보인다"),
 ("온라인 비중", "30%", "0 ~ 100%", "매출 파일에 온·오프라인 구분 열이 없어 가정", "온·오프라인 상승률을 나눠 적용하려면 비중이 필요하다"),
 ("온라인 상승률", "8%", "-20 ~ 30%", "대응 판촉 시 온라인 판매량 변화(가정)", "온라인은 가격 비교가 쉬워 반응이 크다고 가정"),
 ("오프라인 상승률", "3%", "-20 ~ 30%", "대응 판촉 시 오프라인 판매량 변화(가정)", "오프라인은 반응이 작다고 가정"),
 ("가격 탄력성", "1.5", "0 ~ 3", "가격 1% 낮추면 판매량 1.5% 증가(교육용 가정)", "가격보상이 판매량을 얼마나 움직이는지 계산하려면 필요"),
 ("가격보상", "5%", "0 ~ 10% (슬라이더)", "거래선에 보전해 주는 가격 인하율", "타사 행사에 맞설 때 가장 먼저 검토하는 수단"),
 ("판촉비율", "3%", "0 ~ 10%", "매출 대비 판촉비(가정)", "판촉을 하면 비용이 생긴다 — 매출 증분만 보면 안 된다"),
 ("공헌이익률", "18%", "5 ~ 40%", "매출 대비 공헌이익(가정, 실제 마진 아님)", "매출이 늘어도 이익이 남는지 판단하는 기준"),
]
with open(os.path.join(D, "시뮬레이션_샘플값.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["항목", "샘플값", "바꿀 수 있는 범위", "어떻게 정했나", "왜 필요한가"]); w.writerows(SIM)
print(f"매출목표.csv {len(out)}줄 (유통·품목·모델) · 2026 연간 목표 합계 {sum(o[-1] for o in out):,}원 · 시뮬레이션 샘플값 {len(SIM)}항목")

# ───────── 기준본 대시보드에 7. 목표 대비 · 8. 타사 이벤트 대응 시뮬레이션을 붙인다 (다시 돌려도 한 번만) ─────────
import json, re
D4 = os.path.join(AX, "context_pack", "modules", "D_analysis", "04_기준본", "대시보드.html")
CUT = "2026-09-24"
ytd_act = collections.defaultdict(int)
for r in rows:
    if "2026-01-01" <= r["매출일자"] <= CUT: ytd_act[(ch(r), r["품목구분"], r["모델명"])] += int(r["매출금액"])
tg = [dict(c=o[0], i=o[1], m=o[2], mon=o[3:15], ytdT=sum(o[3:11]) + round(o[11] * 24 / 30), ytdA=ytd_act[tuple(o[:3])]) for o in out]
sim = {"base_months": {o[1]: 0 for o in out}}
for o in out: sim["base_months"][o[1]] = sim["base_months"].get(o[1], 0)
BY_ITEM_MONTH = collections.defaultdict(lambda: [0] * 12)
for o in out:
    for m in range(12): BY_ITEM_MONTH[o[1]][m] += o[3 + m]
DATA = {"tg": tg, "items": list(dict.fromkeys(o[1] for o in out)), "itemMonth": BY_ITEM_MONTH,
        "sim": {"evFrom": "2026-10-01", "evTo": "2026-10-14", "from": "2026-10-01", "to": "2026-10-31", "items": ["모니터", "PC"],
                "on": 30, "upOn": 8, "upOff": 3, "el": 1.5, "pc": 5, "pr": 3, "cm": 18},
        "how": {r[0]: r[3] for r in SIM}}
SEC = """<!--TS-->
<section class="sec" id="sec-target"><h2>7. 목표 대비 <span class="who">임원 · 보직장</span></h2>
<p class="sub">2026년 1월 1일 ~ 기준일 9월 24일 누계. 9월 목표는 24/30만 넣었습니다. 줄 순서는 유통 → 품목 → 모델, 각각 매출데이터 시트1에 처음 나온 순서입니다.</p>
<div id="tgt"></div><p class="note"><b>가정</b> · 목표는 2025년 같은 달 실적 +5%로 만든 <b>샘플값</b>입니다(실제 사업계획 아님). 작년 그달 실적이 0이면 작년 월평균 +5%. 실제 목표가 있으면 <span class="mono">목표_2026</span> 시트 숫자만 바꾸면 됩니다.</p></section>
<section class="sec" id="sec-sim"><h2>8. 타사 이벤트 대응 시뮬레이션 <span class="who">가정 · 직접 조작</span></h2>
<p class="sub">아무것도 입력하지 않아도 샘플값으로 계산됩니다. 슬라이더를 움직이면 바로 다시 계산합니다. 계산은 <b>시뮬레이션 기간</b> 기준이고 타사 이벤트 기간은 참고 표시입니다. 모든 값은 <b>가정</b>입니다.</p>
<div class="bar-row" id="simIn"></div><div id="simOut"></div><p class="note" id="simNote"></p></section>
<!--/TS-->"""
JS = """<!--TSJ--><script>
(function(){const T=__DATA__;const f=n=>Math.round(n).toLocaleString('ko-KR');const M=n=>(Math.round(n/1e5)/10).toLocaleString('ko-KR',{minimumFractionDigits:1});
let h='<div class="tw"><table><thead><tr><th>유통</th><th>품목</th><th>모델</th><th class="num">누계 목표</th><th class="num">누계 실적</th><th class="num">달성률</th></tr></thead><tbody>';let a=0,b=0;
T.tg.forEach(r=>{a+=r.ytdT;b+=r.ytdA;const p=r.ytdT?r.ytdA/r.ytdT*100:0;h+=`<tr><td>${r.c}</td><td>${r.i}</td><td class="mono">${r.m}</td><td class="num">${M(r.ytdT)}</td><td class="num">${M(r.ytdA)}</td><td class="num">${r.ytdT?p.toFixed(1)+'%':'목표 0'}</td></tr>`});
h+=`<tr><th colspan="3">합계</th><th class="num">${M(a)}</th><th class="num">${M(b)}</th><th class="num">${(b/a*100).toFixed(1)}%</th></tr></tbody></table></div><p class="note">단위: 백만원</p>`;document.getElementById('tgt').innerHTML=h;
const S=Object.assign({},T.sim);const sl=[['pc','가격보상',0,10,.5,'%'],['on','온라인 비중',0,100,5,'%'],['upOn','온라인 상승률',-20,30,1,'%'],['upOff','오프라인 상승률',-20,30,1,'%'],['el','가격 탄력성',0,3,.1,''],['pr','판촉비율',0,10,.5,'%'],['cm','공헌이익률',5,40,1,'%']];
let ih=`<label>타사 이벤트<span class="mono"><input type="date" id="evF" value="${S.evFrom}"> ~ <input type="date" id="evT" value="${S.evTo}"></span></label><label>시뮬레이션 기간<span class="mono"><input type="date" id="sF" value="${S.from}"> ~ <input type="date" id="sT" value="${S.to}"></span></label><label>겹치는 제품군<span>${T.items.map(i=>`<label style="display:inline;margin-right:6px"><input type="checkbox" class="it" value="${i}" ${S.items.includes(i)?'checked':''}>${i}</label>`).join('')}</span></label>`;
sl.forEach(([k,n,lo,hi,st,u])=>{ih+=`<label>${n} <b id="v_${k}">${S[k]}${u}</b><input type="range" id="r_${k}" min="${lo}" max="${hi}" step="${st}" value="${S[k]}"></label>`});
document.getElementById('simIn').innerHTML=ih+'<button id="simReset">샘플값으로</button>';
function base(){const F=new Date(document.getElementById('sF').value),E=new Date(document.getElementById('sT').value);const its=[...document.querySelectorAll('.it:checked')].map(x=>x.value);let s=0;
 for(let d=new Date(F);d<=E;d.setDate(d.getDate()+1)){if(d.getFullYear()!==2026)continue;const m=d.getMonth(),dim=new Date(2026,m+1,0).getDate();its.forEach(i=>{s+=T.itemMonth[i][m]/dim})}return [s,its]}
function calc(pc){const [B]=base();const on=S.on/100,inc=B*(on*(S.upOn/100+S.el*pc)+(1-on)*(S.upOff/100+S.el*pc)),tot=B+inc,comp=tot*pc,pro=tot*S.pr/100;return {B,inc,comp,pro,ci:inc*S.cm/100-comp-pro}}
function run(){sl.forEach(([k,,,,,u])=>{S[k]=+document.getElementById('r_'+k).value;document.getElementById('v_'+k).textContent=S[k]+u});const r=calc(S.pc/100),[,its]=base();
 const card=(t,v,neg)=>`<div class="tile"><div class="k">${t}</div><div class="v" style="color:${neg&&v<0?'var(--neg)':'inherit'}">${f(v)}원</div></div>`;
 let pts=[],be=null;for(let p=0;p<=10.001;p+=.5){const c=calc(p/100).ci;pts.push([p,c]);if(be===null&&p>0&&c<0&&calc((p-.5)/100).ci>=0)be=p-.5}
 const lo=Math.min(...pts.map(x=>x[1]),0),hi=Math.max(...pts.map(x=>x[1]),0),W=640,H=140,x=p=>30+p/10*(W-40),y=v=>10+(hi-v)/((hi-lo)||1)*(H-30);
 const svg=`<svg viewBox="0 0 ${W} ${H}" width="100%" style="max-width:${W}px"><line x1="30" x2="${W-10}" y1="${y(0)}" y2="${y(0)}" stroke="var(--rule)"/><polyline fill="none" stroke="var(--s1)" stroke-width="2" points="${pts.map(q=>x(q[0])+','+y(q[1])).join(' ')}"/><circle cx="${x(S.pc)}" cy="${y(r.ci)}" r="5" fill="var(--s2)"/><text x="30" y="${H-4}" font-size="11" fill="var(--mute)">가격보상 0%</text><text x="${W-80}" y="${H-4}" font-size="11" fill="var(--mute)">10%</text></svg>`;
 document.getElementById('simOut').innerHTML=`<p class="sub">기준 매출(시뮬레이션 기간 · ${its.join(', ')||'제품군 없음'} 목표) <b>${f(r.B)}원</b></p><div class="tiles">${card('증분 매출',r.inc)}${card('가격보상 비용',r.comp)}${card('판촉비',r.pro)}${card('공헌이익 증감',r.ci,true)}</div>${svg}<p class="note">선 = 가격보상률별 공헌이익 증감 · 점 = 지금 값</p>`;
 const all=pts.every(q=>q[1]<0),none=pts.every(q=>q[1]>=0);
 document.getElementById('simNote').innerHTML=(all?'<b>손익분기 가격보상률: 없음</b> — 이 가정에서는 가격보상을 0%로 해도 판촉비만큼 손해이고, 올릴수록 손해가 커집니다. 판촉비율 · 탄력성 · 공헌이익률을 바꿔 보십시오.':none?'<b>손익분기:</b> 10%까지 모두 이익':`<b>손익분기 가격보상률 ≈ ${be}%</b>`)+' · 가정 출처: '+Object.entries(T.how).filter(([k])=>!/기간|제품군/.test(k)).map(([k,v])=>k+' — '+v).join(' / ')}
document.getElementById('simIn').addEventListener('input',run);document.getElementById('simReset').onclick=()=>{location.hash='';sl.forEach(([k])=>document.getElementById('r_'+k).value=T.sim[k]);run()};run()})();
</script><!--/TSJ-->"""
page = open(D4, encoding="utf-8").read()
page = re.sub(r"<!--TS-->.*?<!--/TS-->\n?", "", page, flags=re.S)
page = re.sub(r"<!--TSJ-->.*?<!--/TSJ-->", "", page, flags=re.S)
anchor = '<section class="sec"><h2>확인 필요</h2>'
assert anchor in page
page = page.replace(anchor, SEC + "\n" + anchor, 1)
page = page.replace("</body></html>", JS.replace("__DATA__", json.dumps(DATA, ensure_ascii=False)) + "</body></html>", 1)
open(D4, "w", encoding="utf-8").write(page)
print("04_기준본/대시보드.html 에 7 · 8번 추가")
