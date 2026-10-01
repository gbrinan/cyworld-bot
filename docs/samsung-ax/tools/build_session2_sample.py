# -*- coding: utf-8 -*-
"""세션2(D 데이터 분석)의 정본 데이터를 만든다.
삼성이 공유한 매출 헤더 16열 · 2025-01 ~ 2026-09 일 단위 · 고객사 6곳 · 판매처(대리점) 3곳.
전년비 · 전월비 · 일 매출 · 판매처별 관리 수요처를 볼 수 있어야 하므로 2년치를 일 단위로 만든다.
시드 고정이라 몇 번을 돌려도 같은 값이 나온다.
사용: python3 docs/samsung-ax/tools/build_session2_sample.py"""
import os, csv, random, datetime as dt, collections, json, calendar
HERE=os.path.dirname(os.path.abspath(__file__)); AX=os.path.abspath(os.path.join(HERE,".."))
MOD=os.path.join(AX,"context_pack","modules","D_analysis")
D1=os.path.join(MOD,"01_데이터"); D3=os.path.join(MOD,"03_테스트")
D4=os.path.join(MOD,"04_기준본"); D6=os.path.join(MOD,"06_붙여넣기")
for d in (D1,D3,D4,D6): os.makedirs(d, exist_ok=True)
random.seed(9001)            # 이 시드에서 아래 '심어 둔 흐름'이 모두 성립한다 (tools 아래 점검이 확인)

HEADER=["영업기회 번호","영업기회 유형","그룹명","파트명","판매처코드","판매처명","판매처 주소",
        "수요처코드","수요처명","영업기회명","매출일자","품목구분","모델명","주문유형","매출금액","매출수량"]

START=dt.date(2025,1,2)
CUTOFF=dt.date(2026,9,24)      # 데이터 추출일. 9월은 24일까지만 있다 — 당월 비교는 '동기간'으로 해야 한다

# 고객사 6곳 — 세션1·2·3 공통. 판매처(대리점)는 수요처마다 정해져 있다.
# 남해정보통신 3곳 · 동백시스템 2곳 · 가야네트웍스 2곳. 한울종합건설은 대리점 두 곳이 같이 맡는다.
ACCOUNTS={
 "해솔호텔":    dict(code="1000101", vert="호텔", part="직판1파트", direct=0.55, dealers=["남해정보통신"], w=1.0),
 "대성건설":    dict(code="1000204", vert="건설", part="직판1파트", direct=0.70, dealers=["남해정보통신"], w=1.2),
 "한울종합건설": dict(code="1000311", vert="건설", part="직판1파트", direct=0.40, dealers=["남해정보통신","가야네트웍스"], w=1.0),
 "미래로병원":  dict(code="1000425", vert="병원", part="직판2파트", direct=0.50, dealers=["동백시스템"], w=1.0),
 "세종교육재단": dict(code="1000538", vert="교육", part="직판2파트", direct=0.30, dealers=["가야네트웍스"], w=0.8),
 "서진리테일":  dict(code="1000642", vert="유통", part="직판2파트", direct=0.20, dealers=["동백시스템"], w=0.8),
}
DEALERS={"남해정보통신":("2000071","부산광역시 해운대구 센텀중앙로 45"),
         "동백시스템":("2000088","부산광역시 해운대구 좌동순환로 12"),
         "가야네트웍스":("2000095","경상남도 김해시 분성로 221")}
GROUP_DIRECT="한국총괄 B2B영업그룹"; GROUP_CHANNEL="한국총괄 B2B유통그룹"; PART_CHANNEL="경로1파트"

# (모델명, 단가, 규격표기) — 단가는 매출금액을 만들 때만 쓰고 파일에는 넣지 않는다 (헤더에 단가 열이 없다)
ITEMS={"TV":[("HX-55T",1420000,"55인치"),("HX-65T",1980000,"65인치"),("BX-65S",2340000,"65인치")],
       "사이니지":[("SG-43C",1150000,"43인치"),("SG-55C",1760000,"55인치")],
       "모니터":[("MN-27Q",430000,"27인치"),("MN-32U",690000,"32인치")],
       "PC":[("DP-i5N",890000,"데스크톱"),("NB-i7P",1540000,"노트북")],
       "에어컨":[("AC-18W",1120000,"18평형")],
       "청소기":[("VC-20B",280000,"업소용"),("VC-35H",460000,"대용량")]}
QTY={"TV":[2,4,6,10,16],"사이니지":[1,2,3,4,6],"모니터":[5,8,12,20],"PC":[5,8,10,15,20],
     "에어컨":[2,3,4,6],"청소기":[2,4,6,10]}
VERT_ITEMS={"호텔":{"TV":5,"사이니지":3,"에어컨":1,"청소기":1},
            "건설":{"사이니지":3,"에어컨":3,"모니터":2,"TV":1},
            "병원":{"PC":4,"모니터":3,"TV":2,"사이니지":1},
            "교육":{"PC":4,"모니터":2,"사이니지":2,"에어컨":1},
            "유통":{"사이니지":4,"청소기":3,"PC":2,"에어컨":1}}

def wpick(d):
    ks=list(d); return random.choices(ks, weights=[d[k] for k in ks])[0]

def item_weights(vert, day):
    w=dict(VERT_ITEMS[vert])
    if day.year==2026:
        # 심어 둔 흐름 ① 사이니지는 올해 늘고(호텔 리뉴얼 · 건설 현장), TV는 준다
        if "사이니지" in w: w["사이니지"]*=1.8
        if "TV" in w: w["TV"]*=0.85
    return w

def acct_weight(name, day):
    w=ACCOUNTS[name]["w"]
    # 심어 둔 흐름 ② 미래로병원은 2026-05부터 구매가 확 준다 (신관 증축 공사 중 — 세션1 기사와 이어진다)
    if name=="미래로병원" and day>=dt.date(2026,5,1): w*=0.45
    return w

rows=[]
def add(day, acct, item, model, unit, spec, qty, direct, name_override=None, kind=None):
    a=ACCOUNTS[acct]
    if direct:
        grp,part,ord_="한국총괄 B2B영업그룹",a["part"],"직판주문"
        scode,sname,saddr=a["code"],acct,"—"          # 헤더 설명: 유통이 없으면 판매처 = 수요처
    else:
        dealer=random.choice(a["dealers"])
        grp,part,ord_=GROUP_CHANNEL,PART_CHANNEL,"유통주문"
        scode,(saddr)=DEALERS[dealer][0],DEALERS[dealer][1]; sname=dealer
    rows.append(dict(day=day, kind=kind or random.choices(["선행영업","트렌드"],[3,7])[0], grp=grp, part=part,
                     scode=scode, sname=sname, saddr=saddr, ccode=a["code"], cname=acct,
                     oname=name_override or f"{acct} {spec} {item} 납품건", item=item, model=model,
                     ord=ord_, amt=unit*qty, qty=qty))

day=START
while day<=CUTOFF:
    if day.weekday()<5:                                  # 영업일만
        n=random.choice([1,1,2,2,2,3])
        if day.year==2026 and random.random()<0.45: n+=1  # 올해 거래가 조금 늘었다 (연 누계 전년비 플러스)
        if day.day>=25: n+=random.choice([1,2,2,3])       # 심어 둔 흐름 ③ 월말에 매출이 몰린다
        names=list(ACCOUNTS)
        for _ in range(n):
            acct=random.choices(names, weights=[acct_weight(x,day) for x in names])[0]
            item=wpick(item_weights(ACCOUNTS[acct]["vert"], day))
            model,unit,spec=random.choice(ITEMS[item])
            qty=random.choice(QTY[item])
            add(day, acct, item, model, unit, spec, qty, random.random()<ACCOUNTS[acct]["direct"])
    day+=dt.timedelta(days=1)

# 심어 둔 흐름 ④ 작년 9월 미래로병원 노트북 일괄 교체 — 일회성. 올해 9월 전년비가 크게 빠지는 '기저효과'의 원인이다.
for d_,q in [(dt.date(2025,9,8),40),(dt.date(2025,9,11),40),(dt.date(2025,9,16),40),(dt.date(2025,9,19),30)]:
    add(d_, "미래로병원", "PC", "NB-i7P", 1540000, "노트북", q, True,
        name_override="미래로병원 노트북 일괄 교체 납품건", kind="선행영업")

rows.sort(key=lambda r:(r["day"], r["cname"]))
seq=collections.Counter()
for r in rows:
    seq[r["day"].year]+=1; r["opp"]=f"OPP-{r['day'].year}-{seq[r['day'].year]:04d}"

def as_list(r):
    return [r["opp"],r["kind"],r["grp"],r["part"],r["scode"],r["sname"],r["saddr"],r["ccode"],r["cname"],
            r["oname"],r["day"].isoformat(),r["item"],r["model"],r["ord"],r["amt"],r["qty"]]
ROWS=[as_list(r) for r in rows]

# ───────── 파일 쓰기 ─────────
def write_csv(path, header, body):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(header); w.writerows(body)

write_csv(os.path.join(D1,"매출데이터.csv"), HEADER, ROWS)
TOTAL=sum(r[14] for r in ROWS)
print(f"01_데이터/매출데이터.csv  {len(ROWS)}행 · {ROWS[0][10]} ~ {ROWS[-1][10]} · 합계 {TOTAL:,}원")

# 소계 — 단가 열이 없어 '단가 × 수량 = 금액' 검산을 못 하므로, 축별 합계를 따로 주고 대조하게 한다.
SUB_AXES=[("품목구분",11),("주문유형",13),("수요처명",8),("파트명",3),("판매처명",5)]
SUB=[]
for col,idx in SUB_AXES:
    agg=collections.Counter(); cnt=collections.Counter()
    for r in ROWS: agg[r[idx]]+=r[14]; cnt[r[idx]]+=1
    for k,v in sorted(agg.items(), key=lambda x:-x[1]): SUB.append([col,k,cnt[k],v])
SUB.append(["전체","합계",len(ROWS),TOTAL])
write_csv(os.path.join(D1,"매출데이터_소계.csv"), ["축","값","건수","합계"], SUB)
print(f"01_데이터/매출데이터_소계.csv  {len(SUB)}행 · 축 {len(SUB_AXES)}개 + 전체")

# 함정 — 일부러 어긋낸 판. 행 번호를 손으로 박지 않고 조건으로 찾는다.
trap=[list(r) for r in ROWS]; TRAPS=[]
def find(pred, start=0):
    for k in range(start,len(trap)):
        if pred(trap[k]): return k
    raise SystemExit("함정을 심을 행을 못 찾았다")
k=find(lambda r: r[10].startswith("2026-02")); trap[k][10]=trap[k][10].replace("-","/")
TRAPS.append((k+2,"매출일자 형식 혼재",f"{trap[k][10]} — 다른 행은 YYYY-MM-DD"))
k=find(lambda r: r[8]=="대성건설" and r[10].startswith("2026")); trap[k][8]="대성 건설"
TRAPS.append((k+2,"수요처명 표기 불일치",f"'대성 건설' — 같은 코드 {trap[k][7]}의 다른 행은 '대성건설'"))
k=find(lambda r: r[10].startswith("2026-06")); trap[k][0]=trap[k-1][0]
TRAPS.append((k+2,"영업기회 번호 중복",f"{trap[k][0]} — 바로 앞 행과 같다"))
k=find(lambda r: r[10].startswith("2026-07") and r[14]>0); trap[k][14]=-trap[k][14]
TRAPS.append((k+2,"매출금액 음수",f"{trap[k][14]:,}"))
k=find(lambda r: r[10].startswith("2026-08") and r[15]>0); trap[k][15]=0
TRAPS.append((k+2,"매출수량 0","금액은 그대로"))
write_csv(os.path.join(D3,"매출데이터_함정.csv"), HEADER, trap)
TRAP_TOTAL=sum(int(r[14]) for r in trap)
print(f"03_테스트/매출데이터_함정.csv  {len(trap)}행 · 합계 {TRAP_TOTAL:,} (소계와 {TRAP_TOTAL-TOTAL:+,})")
for t in TRAPS: print("   -", t)

# 붙여넣기본 — 업로드가 막힌 환경용. 1천 행을 채팅창에 붙일 수는 없으므로 월 × 품목 집계로 준다.
def md_table(h, body):
    out=["| "+" | ".join(map(str,h))+" |","|"+"|".join("---" for _ in h)+"|"]
    out+=["| "+" | ".join(map(str,r))+" |" for r in body]; return "\n".join(out)
ITEM_ORDER=[k for k,_ in collections.Counter({r[11]:0 for r in ROWS}).items()]
ITEM_ORDER=sorted({r[11] for r in ROWS}, key=lambda k:-sum(r[14] for r in ROWS if r[11]==k))
mon=collections.defaultdict(collections.Counter)
for r in ROWS: mon[r[10][:7]][r[11]]+=r[14]
body=[[m]+[f"{mon[m][i]//10000:,}" for i in ITEM_ORDER]+[f"{sum(mon[m].values())//10000:,}"] for m in sorted(mon)]
open(os.path.join(D6,"매출데이터.md"),"w",encoding="utf-8").write(
 "# 매출데이터 (붙여넣기본 — 월 × 품목 집계)\n\n"
 f"> 업로드가 막힌 환경에서 채팅창에 붙여넣는 표입니다. 원본 `01_데이터/매출데이터.csv`는 {len(ROWS):,}행이라 붙여넣을 수 없어 **월 × 품목구분 합계**만 담았습니다.\n"
 "> 단위는 **만원**(원 단위 버림)입니다. 이 표로는 **일별 · 판매처별 · 파트별 화면을 만들 수 없습니다.** 업로드가 되는 환경에서 원본을 쓰십시오.\n"
 f"> 2026-09는 **{CUTOFF.day}일까지**만 들어 있습니다.\n\n"
 + md_table(["매출월"]+ITEM_ORDER+["합계"], body) + "\n")
open(os.path.join(D6,"매출데이터_소계.md"),"w",encoding="utf-8").write(
 "# 매출데이터 소계 (붙여넣기본)\n\n> 축별 합계입니다. **검산 대조용**이고, 원본에서 직접 더한 값과 한 줄씩 맞춰 봅니다.\n\n"
 + md_table(["축","값","건수","합계"], [[a,b,c,f"{d:,}"] for a,b,c,d in SUB]) + "\n")
for n in ("매출데이터.md","매출데이터_소계.md"):
    sz=os.path.getsize(os.path.join(D6,n)); print(f"06_붙여넣기/{n}  {sz:,}B"+("  ← 6KB 초과!" if sz>6*1024 else ""))

# ───────── 심어 둔 흐름이 실제로 성립하는지 확인한다 ─────────
# 숫자를 손보다가 이야기가 깨지면 교재 전체(리뷰 기준본 · 테스트 · 슬라이드)가 틀린 말을 하게 된다. 여기서 막는다.
D_=dt.date
def S(f,t,pred=lambda r:True): return sum(r["amt"] for r in rows if f<=r["day"]<=t and pred(r))
cd=CUTOFF.day
F=dict(
  total=TOTAL, rows=len(ROWS),
  mtd=S(D_(2026,9,1),CUTOFF), pm_same=S(D_(2026,8,1),D_(2026,8,cd)), pm_full=S(D_(2026,8,1),D_(2026,8,31)),
  py_same=S(D_(2025,9,1),D_(2025,9,cd)), ytd=S(D_(2026,1,1),CUTOFF), pytd=S(D_(2025,1,1),D_(2025,9,cd)),
  aug_tail=S(D_(2026,8,25),D_(2026,8,31)),
  oneoff=sum(r["amt"] for r in rows if r["oname"]=="미래로병원 노트북 일괄 교체 납품건"),
)
def dlt(key):
    c=collections.Counter(); p=collections.Counter()
    for r in rows:
        k=r[key] if not (key=="sname" and r["ord"]=="직판주문") else "직판"
        if D_(2026,9,1)<=r["day"]<=CUTOFF: c[k]+=r["amt"]
        if D_(2025,9,1)<=r["day"]<=D_(2025,9,cd): p[k]+=r["amt"]
    return {k:c[k]-p[k] for k in set(c)|set(p)}
F["yoy_by_acct"]=dlt("cname"); F["yoy_by_item"]=dlt("item")
def ytd_item(n): return S(D_(2026,1,1),CUTOFF,lambda r:r["item"]==n), S(D_(2025,1,1),D_(2025,9,cd),lambda r:r["item"]==n)
F["sign_ytd"]=ytd_item("사이니지")
pct=lambda a,b:(a/b-1)*100
F["r_pm_same"]=pct(F["mtd"],F["pm_same"]); F["r_pm_full"]=pct(F["mtd"],F["pm_full"])
F["r_py"]=pct(F["mtd"],F["py_same"]); F["r_ytd"]=pct(F["ytd"],F["pytd"])
F["mirae_share"]=F["yoy_by_acct"]["미래로병원"]/(F["mtd"]-F["py_same"])*100
F["tail_share"]=F["aug_tail"]/F["pm_full"]*100
STORY=[
 ("연 누계는 전년보다 늘었다", F["r_ytd"]>0),
 ("그런데 9월은 전년 동월 동기간 대비 크게 빠졌다 (-30% 아래)", F["r_py"]<-30),
 ("그 감소의 대부분 이상이 미래로병원 한 곳이다 (80% 이상)", F["mirae_share"]>=80),
 ("전월 동기간과 견주면 큰 차이가 없다 (±10% 안)", abs(F["r_pm_same"])<10),
 ("전월 '전체'와 견주면 크게 줄어 보인다 (-20% 아래) — 월말 몰림 때문", F["r_pm_full"]<-20),
 ("사이니지는 연 누계 기준 30% 넘게 늘었다", pct(*F["sign_ytd"])>30),
]
bad=[s for s,ok in STORY if not ok]
if bad: raise SystemExit("심어 둔 흐름이 깨졌다:\n  - "+"\n  - ".join(bad))
print("심어 둔 흐름 6개 모두 성립")
print(f"  9월 1~{cd}일 {F['mtd']:,} · 전월 동기간 {F['pm_same']:,} ({F['r_pm_same']:+.1f}%) · 전월 전체 {F['pm_full']:,} ({F['r_pm_full']:+.1f}%)")
print(f"  전년 동월 동기간 {F['py_same']:,} ({F['r_py']:+.1f}%) · 미래로병원 기여 {F['mirae_share']:.0f}% · 작년 일회성 {F['oneoff']:,}")
print(f"  연 누계 {F['ytd']:,} vs {F['pytd']:,} ({F['r_ytd']:+.1f}%) · 8월 25일 이후 비중 {F['tail_share']:.0f}% · 사이니지 연누계 {pct(*F['sign_ytd']):+.0f}%")

# ───────── 대시보드 기준본 ─────────
# 삼성 요구: 총 · 판매처별 · 수요처별 · 파트별 · 모델/품목별 · 월별 · 일별 · 전년 매출 /
#           드릴다운(버튼 선택 시 값 변경) / 보직장 = 일 매출 · 피벗 / 임원 = 전년비 · 전월비 · '왜' /
#           품목 담당 = 품목별 / 판매처 1곳이 수요처 몇 곳을 맡나
import html as H
def dealer_of(r): return r["sname"] if r["ord"]=="유통주문" else "직판"
LK={k:[] for k in "SCPIMON"}
def ix(k,v):
    L=LK[k]
    if v not in L: L.append(v)
    return L.index(v)
# 표시 순서를 고정한다 — 필터로 순서가 바뀌어도 색과 자리가 따라 움직이지 않게
for v in ["남해정보통신","동백시스템","가야네트웍스","직판"]: ix("S",v)
for v in ACCOUNTS: ix("C",v)
for v in ["직판1파트","직판2파트",PART_CHANNEL]: ix("P",v)
for v in ITEM_ORDER: ix("I",v)
for v in ["직판주문","유통주문"]: ix("O",v)
PAY=[]
for n,r in enumerate(rows, start=2):                      # n = 파일 행 번호 (헤더가 1행)
    d=r["day"]
    PAY.append([d.year*10000+d.month*100+d.day, ix("S",dealer_of(r)), ix("C",r["cname"]), ix("P",r["part"]),
                ix("I",r["item"]), ix("M",r["model"]), ix("O",r["ord"]), r["amt"], n, ix("N",r["oname"])])

# 소계 대조 — 기준본은 직접 대조한 결과를 화면에 적는다
def sub_ok():
    for col,idx in SUB_AXES:
        agg=collections.Counter()
        for r in ROWS: agg[r[idx]]+=r[14]
        for a,b,c,d in SUB:
            if a==col and agg[b]!=d: return False
    return True
SUB_OK=sub_ok()

CSS=r"""
:root{--paper:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--mute:#7a7873;--line:#e4e2db;--panel:#f3f2ee;--rule:#d9d7d0;
--field:#fff;--grid:#ebe9e3;--s1:#2a78d6;--s2:#eb6834;--pos:#2a78d6;--neg:#e34948;--mid:#f0efec;--hl:#e8f0fb}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#1a1a19;--ink:#fff;--ink2:#c3c2b7;
--mute:#9b998f;--line:#343330;--panel:#242320;--rule:#3a3936;--field:#2b2a27;--grid:#2c2b28;--s1:#3987e5;
--s2:#d95926;--pos:#3987e5;--neg:#e66767;--mid:#383835;--hl:#1f2b3b}}
:root[data-theme="dark"]{--paper:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mute:#9b998f;--line:#343330;--panel:#242320;
--rule:#3a3936;--field:#2b2a27;--grid:#2c2b28;--s1:#3987e5;--s2:#d95926;--pos:#3987e5;--neg:#e66767;--mid:#383835;--hl:#1f2b3b}
html{color-scheme:light dark}
body{margin:0;background:var(--paper);color:var(--ink);font-size:14px;line-height:1.55;
font-family:'IBM Plex Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:28px 16px 64px}
.eyebrow{font-size:12px;letter-spacing:.1em;color:var(--s1);font-weight:600}
h1{font-size:24px;margin:4px 0 2px;line-height:1.3}
.src{color:var(--mute);font-size:13px;margin:0 0 14px}
h2{font-size:17px;margin:30px 0 4px;padding-top:14px;border-top:1px solid var(--rule);display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
h2 .who{font-size:12px;font-weight:600;color:var(--ink2);background:var(--panel);border:1px solid var(--line);padding:1px 8px;border-radius:10px}
.sub{color:var(--ink2);font-size:13px;margin:0 0 10px}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12.5px}
.bar-row{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:flex-end;background:var(--panel);border:1px solid var(--line);padding:10px 12px}
.bar-row label{display:flex;flex-direction:column;gap:3px;font-size:12px;color:var(--mute)}
select,button{font:inherit;font-size:13px;color:var(--ink);background:var(--field);border:1px solid var(--rule);border-radius:3px;padding:5px 8px}
button{cursor:pointer}
button:hover{background:var(--panel)}
button:focus-visible,select:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--s1);outline-offset:1px}
.seg{display:inline-flex;border:1px solid var(--rule);border-radius:3px;overflow:hidden}
.seg button{border:0;border-right:1px solid var(--rule);border-radius:0;background:var(--field);padding:5px 10px}
.seg button:last-child{border-right:0}
.seg button[aria-pressed="true"]{background:var(--ink);color:var(--paper);font-weight:600}
.how{font-size:13.5px;color:var(--ink2);margin:0 0 8px}
.hint{color:var(--mute);font-size:12px}
.scope{font-size:13px;color:var(--ink2);margin:8px 0 0;padding:8px 12px;border-left:3px solid var(--s1);background:var(--panel);display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.chip{display:inline-flex;align-items:center;gap:4px;background:var(--field);border:1px solid var(--rule);border-radius:12px;padding:1px 4px 1px 9px;font-size:12.5px;color:var(--ink)}
.chip button{border:0;background:transparent;padding:0 5px;font-size:13px;line-height:1.2;color:var(--ink2)}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:10px 0 4px}
@media(max-width:760px){.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}}
.tile{background:var(--panel);border:1px solid var(--line);padding:12px 13px;min-width:0}
.tile .k{font-size:12px;color:var(--mute);margin-bottom:4px}
.tile .v{font-size:20px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.2;overflow-wrap:anywhere}
.tile .s{font-size:12px;color:var(--ink2);margin-top:4px}
.chart{width:100%;height:auto;display:block;touch-action:pan-y}
.legend{display:flex;gap:14px;font-size:12.5px;color:var(--ink2);margin:2px 0 4px;flex-wrap:wrap}
.legend .k{display:inline-flex;align-items:center;gap:6px}
.legend i{display:inline-block;width:16px;height:0;border-top:2px solid}
.note{font-size:12.5px;color:var(--ink2);margin:6px 0 0}
.tw{overflow-x:auto;border:1px solid var(--line);margin-top:8px}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:6px 9px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}
thead th{font-size:12px;color:var(--mute);font-weight:600;background:var(--panel);position:sticky;top:0}
.num{text-align:right;font-variant-numeric:tabular-nums}
tbody tr.drill{cursor:pointer}
tbody tr.drill:hover,tbody tr.drill:focus{background:var(--hl)}
tbody tr.tot td,tbody tr.tot th{font-weight:700;background:var(--panel)}
.ctl{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin:4px 0 0;font-size:12.5px;color:var(--mute)}
.why{display:grid;grid-template-columns:minmax(90px,150px) 1fr 120px 78px;gap:4px 10px;align-items:center;margin-top:10px;font-size:13px}
.why .lbl{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.why .track{position:relative;height:14px;background:linear-gradient(var(--rule),var(--rule)) center/1px 100% no-repeat}
.why .b{position:absolute;top:2px;height:10px}
.why .b.p{left:50%;background:var(--pos);border-radius:0 4px 4px 0}
.why .b.n{right:50%;background:var(--neg);border-radius:4px 0 0 4px}
.why .v{text-align:right;font-variant-numeric:tabular-nums}
.why .c{text-align:right;color:var(--ink2);font-variant-numeric:tabular-nums}
.say{background:var(--panel);border:1px solid var(--line);padding:10px 12px;margin-top:8px;font-size:14px}
.say b{font-weight:700}
.flag{font-weight:700}
.chk{background:var(--panel);border-left:3px solid var(--s1);padding:10px 14px;font-size:13px;margin-top:8px}
.chk p{margin:3px 0}
.empty{border:1px dashed var(--rule);padding:16px;color:var(--ink2);margin-top:12px}
.foot{margin-top:40px;padding-top:10px;border-top:1px solid var(--rule);font-size:12px;color:var(--mute)}
#tip{position:fixed;z-index:9;pointer-events:none;opacity:0;transition:opacity .08s;background:var(--ink);color:var(--paper);
font-size:12.5px;line-height:1.5;padding:7px 10px;border-radius:4px;box-shadow:0 2px 10px rgba(0,0,0,.22);max-width:280px}
#tip b{font-size:13.5px;font-variant-numeric:tabular-nums}
#tip .r{display:flex;align-items:center;gap:6px}
#tip .r i{display:inline-block;width:12px;height:0;border-top:2px solid}
#tip .m{opacity:.75}
[hidden]{display:none!important}
"""

JS=r"""
const LK=__LK__, R=__ROWS__, LAST=__LAST__, Y=2026, PY=2025;
const LASTM=Math.floor(LAST/100)%100, LASTD=LAST%100;
const DIM={S:{i:1,n:'판매처'},C:{i:2,n:'수요처'},P:{i:3,n:'파트'},I:{i:4,n:'품목'},M:{i:5,n:'모델'}};
const NEXT={S:'C',C:'I',P:'C',I:'M',M:null};
const FKEY={S:'dealer',C:'acct',P:'part',I:'item'};
const st={m:LASTM,part:-1,dealer:-1,acct:-1,item:-1,dim:'S',day:0};
const $=id=>document.getElementById(id), tip=$('tip');
const nf=new Intl.NumberFormat('ko-KR');
const won=n=>nf.format(Math.round(n));
const mil=n=>(Math.round(n/1e5)/10).toLocaleString('ko-KR',{minimumFractionDigits:1,maximumFractionDigits:1});
const short=n=>{const a=Math.abs(n),s=n<0?'−':'';return a>=1e8?s+(a/1e8).toFixed(1).replace(/\.0$/,'')+'억':a>=1e4?s+nf.format(Math.round(a/1e4))+'만':s+nf.format(a)};
const rate=(a,b)=>b===0?(a>0?'이전 0':'—'):((a/b-1)*100>=0?'+':'−')+Math.abs((a/b-1)*100).toFixed(1)+'%';
const signed=n=>(n>=0?'+':'−')+won(Math.abs(n));
const ymd=(y,m,d)=>y*10000+m*100+d, dim=(y,m)=>new Date(y,m,0).getDate();
const cutoffDay=m=>m===LASTM?LASTD:dim(Y,m);
const WD='일월화수목금토';
/* 한국어 조사 — 받침에 따라 은/는, (으)로 */
const jong=w=>{const c=w.charCodeAt(w.length-1)-0xAC00;return c>=0&&c<11172?c%28:0};
const eun=w=>w+(jong(w)?'은':'는'), ro=w=>{const j=jong(w);return w+(j&&j!==8?'으로':'로')};
function el(t,c,x){const n=document.createElement(t);if(c)n.className=c;if(x!=null)n.textContent=String(x);return n}
function svg(t,a){const n=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)n.setAttribute(k,a[k]);return n}

/* 기간 — 이번 달은 1일부터 기준일까지. 비교하는 쪽도 같은 날짜까지만 자른다 */
function periods(m){
  const cd=cutoffDay(m), pmY=m===1?PY:Y, pmM=m===1?12:m-1;
  return {cd,
    cur:[ymd(Y,m,1),ymd(Y,m,cd)],
    pm:[ymd(pmY,pmM,1),ymd(pmY,pmM,Math.min(cd,dim(pmY,pmM)))],
    pmFull:[ymd(pmY,pmM,1),ymd(pmY,pmM,dim(pmY,pmM))], pmLabel:pmM+'월',
    py:[ymd(PY,m,1),ymd(PY,m,Math.min(cd,dim(PY,m)))],
    ytd:[ymd(Y,1,1),ymd(Y,m,cd)], pytd:[ymd(PY,1,1),ymd(PY,m,Math.min(cd,dim(PY,m)))]};
}
const inP=(r,p)=>r[0]>=p[0]&&r[0]<=p[1];
const sum=(rows,p)=>{let s=0;for(const r of rows)if(inP(r,p))s+=r[7];return s};
function base(){return R.filter(r=>(st.part<0||r[3]===st.part)&&(st.dealer<0||r[1]===st.dealer)&&(st.acct<0||r[2]===st.acct)&&(st.item<0||r[4]===st.item))}

/* 툴팁 — 값이 먼저, 이름은 뒤. 라벨은 데이터라 textContent로만 넣는다 */
function showTip(x,y,lines){
  tip.replaceChildren();
  for(const [val,label,color,muted] of lines){
    const r=el('div','r'+(muted?' m':''));
    if(color){const i=el('i');i.style.borderColor=color;r.appendChild(i)}
    if(val!=null)r.appendChild(el('b',null,val));
    if(label)r.appendChild(el('span',null,label));
    tip.appendChild(r);
  }
  tip.style.opacity='1';
  const w=tip.offsetWidth,h=tip.offsetHeight;
  tip.style.left=Math.max(8,Math.min(x+14,innerWidth-w-8))+'px';
  tip.style.top=Math.max(8,y-h-12)+'px';
}
const hideTip=()=>{tip.style.opacity='0'};

/* 컨트롤 */
function fillSelect(id,list,label){
  const s=$(id);s.replaceChildren();
  const o=el('option',null,label||'전체');o.value='-1';s.appendChild(o);
  list.forEach((v,i)=>{const p=el('option',null,v);p.value=String(i);s.appendChild(p)});
}
function setupControls(){
  const ms=$('fm');for(let m=1;m<=LASTM;m++){const o=el('option',null,Y+'년 '+m+'월'+(m===LASTM?' ('+LASTD+'일까지)':''));o.value=m;ms.appendChild(o)}
  fillSelect('fp',LK.P);fillSelect('fc',LK.C);fillSelect('fi',LK.I);
  [['fm','m'],['fp','part'],['fc','acct'],['fi','item']].forEach(([id,k])=>
    $(id).addEventListener('change',e=>{st[k]=+e.target.value;st.day=0;render()}));
  $('reset').addEventListener('click',()=>{Object.assign(st,{m:LASTM,part:-1,dealer:-1,acct:-1,item:-1,dim:'S',day:0});render()});
  const host=$('dimSeg');
  for(const k of ['S','C','P','I','M']){const b=el('button',null,DIM[k].n+'별');b.type='button';b.dataset.v=k;
    b.addEventListener('click',()=>{st.dim=k;render()});host.appendChild(b)}
}
function syncControls(){
  $('fm').value=st.m;$('fp').value=st.part;$('fc').value=st.acct;$('fi').value=st.item;
  $('dimSeg').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===st.dim)));
}

/* 지금 보고 있는 것 */
function renderScope(rows,P){
  const host=$('scope');host.replaceChildren();
  host.appendChild(el('strong',null,'지금 보는 범위 —'));
  host.appendChild(el('span',null,Y+'년 '+st.m+'월 1~'+P.cd+'일'));
  let any=false;
  for(const [k,f,n] of [['P','part','파트'],['S','dealer','판매처'],['C','acct','수요처'],['I','item','품목']]){
    if(st[f]<0)continue;any=true;
    const c=el('span','chip',n+' = '+LK[k][st[f]]);const x=el('button',null,'✕');x.type='button';
    x.setAttribute('aria-label',n+' 조건 풀기');x.addEventListener('click',()=>{st[f]=-1;render()});c.appendChild(x);host.appendChild(c);
  }
  if(!any)host.appendChild(el('span',null,'· 전체'));
  else host.appendChild(el('span','hint','(✕를 누르면 그 조건이 풀립니다)'));
  const all=sum(R,P.ytd), mine=sum(rows,P.ytd);
  if(any)host.appendChild(el('span',null,'| 올해 누계 '+short(all)+'원 중 '+short(mine)+'원 ('+(all?(mine/all*100).toFixed(1):'0')+'%)'));
}

/* 한눈에 */
function renderTiles(rows,P){
  const host=$('tiles');host.replaceChildren();
  const cur=sum(rows,P.cur),pm=sum(rows,P.pm),py=sum(rows,P.py),ytd=sum(rows,P.ytd),pytd=sum(rows,P.pytd);
  const T=[
    ['이번 달 ('+st.m+'/1~'+st.m+'/'+P.cd+')',won(cur)+'원',P.cd+'일까지 들어온 매출'],
    ['지난달 같은 날짜까지와 비교',rate(cur,pm),P.pmLabel+' 1~'+Math.min(P.cd,31)+'일 '+short(pm)+'원 → '+short(cur)+'원'],
    ['작년 같은 달 같은 날짜까지와 비교',rate(cur,py),PY+'년 '+st.m+'월 1~'+P.cd+'일 '+short(py)+'원 → '+short(cur)+'원'],
    ['올해 누계 (1/1~'+st.m+'/'+P.cd+')',won(ytd)+'원','작년 같은 기간 '+short(pytd)+'원 대비 '+rate(ytd,pytd)],
  ];
  for(const [k,v,s] of T){const t=el('div','tile');t.append(el('div','k',k),el('div','v',v),el('div','s',s));host.appendChild(t)}
  const pmf=sum(rows,P.pmFull);
  $('tileNote').textContent=P.cd<dim(Y,st.m)
    ? '이번 달은 '+P.cd+'일까지만 들어 있습니다. '+P.pmLabel+' 한 달 전체('+short(pmf)+'원)와 견주면 '+rate(cur,pmf)+'로 보이지만, '+P.pmLabel+'도 '+P.cd+'일까지만 자르면 '+rate(cur,pm)+'입니다. 이 화면의 비교는 전부 같은 날짜까지 자른 값입니다.'
    : '이 화면의 비교는 전부 같은 날짜까지 자른 값입니다. 증감률 옆에 원래 금액 두 개를 같이 적었습니다.';
}

/* 월별 — 올해와 작년 */
function niceStep(v){if(v<=0)return 1;const p=Math.pow(10,Math.floor(Math.log10(v))),f=v/p;return (f<=1?1:f<=2?2:f<=2.5?2.5:f<=5?5:10)*p}
/* 눈금 n칸에 맞춰 위쪽을 깔끔한 수로 올린다 → {max, n} */
function ticks(v,n){const st=niceStep(Math.max(v,1)/n),k=Math.max(1,Math.ceil(Math.max(v,1)/st));return {max:st*k,n:k}}
function renderTrend(rows,P){
  const host=$('trend');host.replaceChildren();
  const W=880,H=270,L=58,Rr=64,T=18,B=30,w=W-L-Rr,h=H-T-B;
  const val=(y,m)=>{if(y===Y&&m>LASTM)return null;const e=y===Y&&m===LASTM?LASTD:dim(y,m);return sum(rows,[ymd(y,m,1),ymd(y,m,e)])};
  const a=[],b=[];for(let m=1;m<=12;m++){a.push(val(Y,m));b.push(val(PY,m))}
  const tk=ticks(Math.max(...a.filter(v=>v!=null),...b,1),4),mx=tk.max;
  const X=m=>L+(m-0.5)*(w/12), Yp=v=>T+h-(v/mx)*h;
  const s=svg('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img','aria-label':'월별 매출 '+PY+'년과 '+Y+'년 비교'});
  for(let i=0;i<=tk.n;i++){const v=mx*i/tk.n,y=Yp(v);
    s.appendChild(svg('line',{x1:L,x2:L+w,y1:y,y2:y,stroke:'var(--grid)','stroke-width':1}));
    const t=svg('text',{x:L-8,y:y+4,'text-anchor':'end','font-size':11,fill:'var(--mute)'});t.textContent=short(v);s.appendChild(t)}
  for(let m=1;m<=12;m++){const t=svg('text',{x:X(m),y:H-10,'text-anchor':'middle','font-size':11,fill:m===st.m?'var(--ink)':'var(--mute)','font-weight':m===st.m?700:400});t.textContent=m+'월';s.appendChild(t)}
  s.appendChild(svg('rect',{x:X(st.m)-w/24,y:T,width:w/12,height:h,fill:'var(--hl)',opacity:.7}));
  const path=(arr,col,dash)=>{let d='';arr.forEach((v,i)=>{if(v==null)return;d+=(d?'L':'M')+X(i+1)+' '+Yp(v)});
    s.appendChild(svg('path',{d,fill:'none',stroke:col,'stroke-width':2,'stroke-linejoin':'round','stroke-linecap':'round','stroke-dasharray':dash||''}))};
  path(b,'var(--s2)','6 4');path(a,'var(--s1)');
  const dots=(arr,col,partialAt)=>arr.forEach((v,i)=>{if(v==null)return;const p=i+1===partialAt;
    s.appendChild(svg('circle',{cx:X(i+1),cy:Yp(v),r:4.5,fill:p?'var(--paper)':col,stroke:p?col:'var(--paper)','stroke-width':2}))});
  dots(b,'var(--s2)',0);dots(a,'var(--s1)',LASTM);
  const lab=(x,y,txt)=>{const t=svg('text',{x,y:y+4,'font-size':12,fill:'var(--ink2)'});t.textContent=txt;s.appendChild(t)};
  lab(X(LASTM)+9,Yp(a[LASTM-1]),Y+'');lab(X(12)+9,Yp(b[11]),PY+'');
  const cross=svg('line',{y1:T,y2:T+h,stroke:'var(--ink2)','stroke-width':1,opacity:0});s.appendChild(cross);
  const hit=svg('rect',{x:L,y:T,width:w,height:h,fill:'transparent',tabindex:0,style:'cursor:pointer'});
  let cur=st.m;
  const show=(m,cx,cy)=>{cur=m;cross.setAttribute('x1',X(m));cross.setAttribute('x2',X(m));cross.setAttribute('opacity',.5);
    const av=a[m-1],bv=b[m-1],lines=[[m+'월',null,null,true]];
    lines.push([av==null?'—':won(av)+'원',Y+(m===LASTM?' ('+LASTD+'일까지)':''),'var(--s1)']);
    lines.push([won(bv)+'원',PY+'','var(--s2)']);
    if(av!=null&&m!==LASTM)lines.push([rate(av,bv),'전년비',null,true]);
    if(m===LASTM)lines.push([rate(av,sum(rows,[ymd(PY,m,1),ymd(PY,m,LASTD)])),'전년 동기간 대비',null,true]);
    showTip(cx,cy,lines)};
  hit.addEventListener('pointermove',e=>{const r=s.getBoundingClientRect(),sx=(e.clientX-r.left)*W/r.width;
    const m=Math.max(1,Math.min(12,Math.round((sx-L)/(w/12)+0.5)));show(m,e.clientX,e.clientY)});
  hit.addEventListener('pointerleave',()=>{cross.setAttribute('opacity',0);hideTip()});
  hit.addEventListener('click',()=>{if(cur<=LASTM){st.m=cur;st.day=0;render()}});
  hit.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){cur=Math.max(1,Math.min(12,cur+(e.key==='ArrowRight'?1:-1)));
    const r=s.getBoundingClientRect();show(cur,r.left+X(cur)*r.width/W,r.top+T*r.height/H+20);e.preventDefault()}
    if(e.key==='Enter'&&cur<=LASTM){st.m=cur;st.day=0;render()}});
  hit.addEventListener('blur',hideTip);
  s.appendChild(hit);host.appendChild(s);
}

/* 일별 — 보직장 */
function renderDaily(rows,P){
  const host=$('daily');host.replaceChildren();
  const m=st.m,dm=dim(Y,m),cd=P.cd;
  const v=[],n=[];for(let d=1;d<=dm;d++){v.push(0);n.push(0)}
  for(const r of rows){if(r[0]>=ymd(Y,m,1)&&r[0]<=ymd(Y,m,cd)){const d=r[0]%100;v[d-1]+=r[7];n[d-1]++}}
  const W=880,H=220,L=58,Rr=16,T=14,B=28,w=W-L-Rr,h=H-T-B,band=w/dm,bw=Math.min(24,band*0.62);
  const tk=ticks(Math.max(...v,1),3),mx=tk.max,X=d=>L+(d-0.5)*band,Yp=x=>T+h-(x/mx)*h;
  const s=svg('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img','aria-label':m+'월 일별 매출'});
  for(let i=0;i<=tk.n;i++){const val=mx*i/tk.n,y=Yp(val);s.appendChild(svg('line',{x1:L,x2:L+w,y1:y,y2:y,stroke:'var(--grid)','stroke-width':1}));
    const t=svg('text',{x:L-8,y:y+4,'text-anchor':'end','font-size':11,fill:'var(--mute)'});t.textContent=short(val);s.appendChild(t)}
  if(cd<dm){const x0=L+cd*band;s.appendChild(svg('rect',{x:x0,y:T,width:L+w-x0,height:h,fill:'var(--panel)'}));
    const t=svg('text',{x:(x0+L+w)/2,y:T+h/2,'text-anchor':'middle','font-size':12,fill:'var(--mute)'});t.textContent='집계 전';s.appendChild(t)}
  const sel=st.day||(()=>{for(let d=cd;d>=1;d--)if(n[d-1])return d;return cd})();
  for(let d=1;d<=dm;d++){
    const dow=new Date(Y,m-1,d).getDay();
    if(d===1||d%5===0||d===dm){const t=svg('text',{x:X(d),y:H-9,'text-anchor':'middle','font-size':11,fill:'var(--mute)'});t.textContent=d;s.appendChild(t)}
    if(d>cd)continue;
    if(v[d-1]>0){const y=Yp(v[d-1]),hh=T+h-y,r=Math.min(4,hh);
      s.appendChild(svg('path',{d:`M${X(d)-bw/2} ${T+h}V${y+r}Q${X(d)-bw/2} ${y} ${X(d)-bw/2+r} ${y}H${X(d)+bw/2-r}Q${X(d)+bw/2} ${y} ${X(d)+bw/2} ${y+r}V${T+h}Z`,
        fill:'var(--s1)',opacity:d===sel?1:.55}))}
    const hit=svg('rect',{x:X(d)-band/2,y:T,width:band,height:h,fill:'transparent',tabindex:v[d-1]>0?0:-1,style:'cursor:pointer'});
    const lines=[[won(v[d-1])+'원',m+'월 '+d+'일 ('+WD[dow]+')'],[n[d-1]+'건',null,null,true]];
    hit.addEventListener('pointermove',e=>showTip(e.clientX,e.clientY,lines));
    hit.addEventListener('focus',()=>{const r=s.getBoundingClientRect();showTip(r.left+X(d)*r.width/W,r.top+Yp(v[d-1])*r.height/H,lines)});
    hit.addEventListener('pointerleave',hideTip);hit.addEventListener('blur',hideTip);
    hit.addEventListener('click',()=>{st.day=d;render()});
    hit.addEventListener('keydown',e=>{if(e.key==='Enter'){st.day=d;render()}});
    s.appendChild(hit);
  }
  host.appendChild(s);
  // 월말 몰림 — 이번 달이 덜 찼으면 지난달로 보여 준다
  const refM=cd<dm?(m===1?null:m-1):m;
  let note='';
  if(refM){const e=dim(Y,refM),tail=sum(rows,[ymd(Y,refM,25),ymd(Y,refM,e)]),all=sum(rows,[ymd(Y,refM,1),ymd(Y,refM,e)]);
    if(all>0)note=refM+'월은 25일 이후 7일에 한 달 매출의 '+(tail/all*100).toFixed(0)+'%가 몰렸습니다. 월 중순 숫자로 한 달을 판단하지 마십시오.'}
  $('dailyNote').textContent=note;
  // 그날 내역
  const dh=$('dayRows');dh.replaceChildren();
  const list=rows.filter(r=>r[0]===ymd(Y,m,sel)).sort((a,b)=>b[7]-a[7]);
  dh.appendChild(el('p','sub',m+'월 '+sel+'일 ('+WD[new Date(Y,m-1,sel).getDay()]+') 내역 — '+list.length+'건 · '+won(list.reduce((s,r)=>s+r[7],0))+'원. 막대를 누르면 그날로 바뀝니다.'));
  if(!list.length)return;
  const tw=el('div','tw'),t=el('table'),hd=el('thead'),tr=el('tr');
  for(const [x,c] of [['행','num'],['수요처',''],['판매처',''],['품목',''],['모델',''],['영업기회명',''],['매출금액(원)','num']])tr.appendChild(el('th',c,x));
  hd.appendChild(tr);t.appendChild(hd);const tb=el('tbody');
  for(const r of list){const row=el('tr');
    row.append(el('td','num mono',r[8]),el('td',null,LK.C[r[2]]),el('td',null,LK.S[r[1]]),el('td',null,LK.I[r[4]]),el('td','mono',LK.M[r[5]]),el('td',null,LK.N[r[9]]),el('td','num',won(r[7])));tb.appendChild(row)}
  t.appendChild(tb);tw.appendChild(t);dh.appendChild(tw);
}

/* 나눠 보기 — 줄을 누르면 그 값으로 걸러지고 한 단계 안으로 들어간다 */
function group(rows,k){const g=new Map();for(const r of rows){const key=r[DIM[k].i];if(!g.has(key))g.set(key,[]);g.get(key).push(r)}return g}
function renderPivot(rows,P){
  const host=$('pivot');host.replaceChildren();
  const k=st.dim,g=group(rows,k);
  const keys=[...g.keys()].sort((a,b)=>sum(g.get(b),P.ytd)-sum(g.get(a),P.ytd));
  $('pivotHint').textContent=NEXT[k]?'줄을 누르면 그 '+DIM[k].n+' 안으로 들어가 '+DIM[NEXT[k]].n+'별로 보여 줍니다.':'모델이 가장 안쪽입니다. 위의 ✕를 누르면 다시 나옵니다.';
  const cols=[['이번 달',r=>mil(sum(r,P.cur))],['지난달 대비',r=>rate(sum(r,P.cur),sum(r,P.pm))],['작년 대비',r=>rate(sum(r,P.cur),sum(r,P.py))],
              ['올해 누계',r=>mil(sum(r,P.ytd))],['누계 작년 대비',r=>rate(sum(r,P.ytd),sum(r,P.pytd))]];
  const tw=el('div','tw'),t=el('table'),hd=el('thead'),tr=el('tr');
  tr.appendChild(el('th',null,DIM[k].n));for(const [n] of cols)tr.appendChild(el('th','num',n));
  hd.appendChild(tr);t.appendChild(hd);const tb=el('tbody');
  for(const key of keys){const rr=g.get(key),row=el('tr',NEXT[k]?'drill':'');
    row.appendChild(el('th',null,LK[k][key]+(NEXT[k]?' ›':'')));for(const [,f] of cols)row.appendChild(el('td','num',f(rr)));
    if(NEXT[k]){row.tabIndex=0;row.setAttribute('role','button');row.setAttribute('aria-label',LK[k][key]+' 안으로 들어가기');
      const go=()=>{st[FKEY[k]]=key;st.dim=NEXT[k];render();$('sec-pivot').scrollIntoView({block:'start'})};
      row.addEventListener('click',go);row.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}})}
    tb.appendChild(row)}
  const tot=el('tr','tot');tot.appendChild(el('th',null,'합계'));for(const [,f] of cols)tot.appendChild(el('td','num',f(rows)));tb.appendChild(tot);
  t.appendChild(tb);tw.appendChild(t);host.appendChild(tw);
  $('pivotUnit').textContent='금액 단위: 백만원 · 비교는 전부 '+st.m+'월 '+P.cd+'일까지 같은 날짜로 자른 값';
}

/* 왜 이렇게 됐나 — 임원. 증감을 '어디서' 났는지로 쪼갠다 */
function renderWhy(rows,P){
  const host=$('why');host.replaceChildren();
  const A=P.cur,Bp=P.py,lab='작년 같은 달 같은 날짜까지('+PY+'년 '+st.m+'월 1~'+P.cd+'일)';
  const k=st.acct>=0?'I':'C',g=group(rows,k),items=[];
  for(const [key,rr] of g){const a=sum(rr,A),b=sum(rr,Bp);if(a||b)items.push({key,a,b,d:a-b})}
  const tot=sum(rows,A)-sum(rows,Bp);
  items.sort((x,y)=>Math.abs(y.d)-Math.abs(x.d));
  const say=el('div','say');
  if(!items.length){say.textContent='비교할 매출이 없습니다.';host.appendChild(say);return}
  const top=items.find(x=>tot&&Math.sign(x.d)===Math.sign(tot))||items[0],sh=tot?top.d/tot*100:0;
  say.append(el('span',null,lab+' 대비 '),el('b',null,signed(tot)+'원 ('+rate(sum(rows,A),sum(rows,Bp))+')'),el('span',null,'. 가장 크게 '+(tot<0?'줄어든':'늘어난')+' '+eun(DIM[k].n)+' '),
    el('b',null,LK[k][top.key]),el('span',null,' ('+signed(top.d)+'원)'));
  if(tot!==0&&Math.sign(top.d)===Math.sign(tot)){
    say.append(el('span',null,' — '+(tot<0?'감소':'증가')+'분의 '),el('b',null,sh.toFixed(0)+'%'),el('span',null,'입니다.'));
    if(sh>100){const rest=tot-top.d;say.append(el('span',null,' 나머지는 합쳐서 '+signed(rest)+'원으로 오히려 '+(rest>0?'늘었습니다':'줄었습니다')+'.'))}
  }else say.append(el('span',null,'.'));
  host.appendChild(say);
  const mx=Math.max(...items.map(x=>Math.abs(x.d)),1),grid=el('div','why');
  for(const it of items.slice(0,8)){
    const name=el('div','lbl',LK[k][it.key]);name.title=LK[k][it.key];
    const tr=el('div','track'),b=el('div','b '+(it.d>=0?'p':'n'));b.style.width=(Math.abs(it.d)/mx*50)+'%';tr.appendChild(b);
    tr.tabIndex=0;const lines=[[signed(it.d)+'원',LK[k][it.key]],[won(it.b)+' → '+won(it.a),null,null,true]];
    tr.addEventListener('pointermove',e=>showTip(e.clientX,e.clientY,lines));tr.addEventListener('pointerleave',hideTip);
    tr.addEventListener('focus',()=>{const r=tr.getBoundingClientRect();showTip(r.left+r.width/2,r.top,lines)});tr.addEventListener('blur',hideTip);
    const sh=tot?it.d/tot*100:0;
    grid.append(name,tr,el('div','v',signed(it.d)),el('div','c',!tot?'—':sh>=0?sh.toFixed(0)+'%':'상쇄'))}
  host.appendChild(grid);
  host.appendChild(el('p','note','파란 막대는 늘어난 곳, 빨간 막대는 줄어든 곳 · 오른쪽 %는 전체 증감 중 그곳의 몫 · 전체와 반대로 움직인 곳은 \'상쇄\'로 적습니다.'));
  // 기저효과를 볼 수 있게 — 비교 기간 쪽의 큰 건을 그대로 보여 준다
  const biggest=rows.filter(r=>inP(r,Bp)&&r[DIM[k].i]===top.key).sort((x,y)=>y[7]-x[7]).slice(0,4);
  if(top.d<0&&biggest.length){
    host.appendChild(el('p','sub','작년 이 기간 '+LK[k][top.key]+'의 큰 건 — 올해가 나빠진 게 아니라 작년이 유난히 컸을 수 있습니다(기저효과).'));
    const tw=el('div','tw'),t=el('table'),hd=el('thead'),trh=el('tr');
    for(const [x,c] of [['행','num'],['매출일자',''],['수요처',''],['품목',''],['영업기회명',''],['매출금액(원)','num']])trh.appendChild(el('th',c,x));
    hd.appendChild(trh);t.appendChild(hd);const tb=el('tbody');
    for(const r of biggest){const d=String(r[0]),row=el('tr');row.append(el('td','num mono',r[8]),el('td','mono',d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6)),
      el('td',null,LK.C[r[2]]),el('td',null,LK.I[r[4]]),el('td',null,LK.N[r[9]]),el('td','num',won(r[7])));tb.appendChild(row)}
    t.appendChild(tb);tw.appendChild(t);host.appendChild(tw)}
}

/* 판매처(대리점) 1곳이 수요처 몇 곳을 맡나 — 보직장 */
function renderDealer(rows,P){
  const host=$('dealer');host.replaceChildren();
  const ch=rows.filter(r=>LK.S[r[1]]!=='직판'&&inP(r,P.ytd));
  const ds=LK.S.map((n,i)=>i).filter(i=>LK.S[i]!=='직판'&&ch.some(r=>r[1]===i));
  const cs=LK.C.map((n,i)=>i).filter(i=>ch.some(r=>r[2]===i));
  if(!ds.length){host.appendChild(el('div','empty','이 조건에는 유통주문(대리점 경유) 매출이 없습니다.'));return}
  const tw=el('div','tw'),t=el('table'),hd=el('thead'),tr=el('tr');
  tr.appendChild(el('th',null,'판매처 \\ 수요처'));for(const c of cs)tr.appendChild(el('th','num',LK.C[c]));
  tr.appendChild(el('th','num','맡은 수요처'));tr.appendChild(el('th','num','연 누계'));hd.appendChild(tr);t.appendChild(hd);
  const tb=el('tbody');
  for(const d of ds){const row=el('tr');row.appendChild(el('th',null,LK.S[d]));let k=0,tot=0;
    for(const c of cs){const v=ch.filter(r=>r[1]===d&&r[2]===c).reduce((s,r)=>s+r[7],0);if(v){k++;tot+=v}row.appendChild(el('td','num',v?mil(v):'—'))}
    row.appendChild(el('td','num flag',k+'곳'));row.appendChild(el('td','num',mil(tot)));tb.appendChild(row)}
  const f=el('tr','tot');f.appendChild(el('th',null,'이 수요처를 맡은 대리점'));const multi=[];
  for(const c of cs){const k=new Set(ch.filter(r=>r[2]===c).map(r=>r[1])).size;if(k>1)multi.push(LK.C[c]);f.appendChild(el('td','num',k+'곳'+(k>1?' ●':'')))}
  f.appendChild(el('td'));f.appendChild(el('td','num',mil(ch.reduce((s,r)=>s+r[7],0))));tb.appendChild(f);
  t.appendChild(tb);tw.appendChild(t);host.appendChild(tw);
  const dir=rows.filter(r=>LK.S[r[1]]==='직판'&&inP(r,P.ytd)).reduce((s,r)=>s+r[7],0),all=sum(rows,P.ytd);
  host.appendChild(el('p','note','단위: 백만원 · 연 누계(1/1~'+st.m+'/'+P.cd+') · 유통주문만. 직판('+(all?(dir/all*100).toFixed(0):0)+'%)은 판매처 = 수요처라 이 표에 없습니다.'+
    (multi.length?' ● '+eun(multi.join(', '))+' 대리점 두 곳 이상이 같이 맡고 있습니다 — 담당이 겹치는지 확인할 자리입니다.':'')));
}

function render(){
  syncControls();
  const rows=base(),P=periods(st.m);
  renderScope(rows,P);
  const has=rows.some(r=>inP(r,P.ytd)||inP(r,P.pytd));
  $('empty').hidden=has;document.querySelectorAll('.sec').forEach(s=>s.hidden=!has);
  if(!has){$('empty').textContent='이 조건에 맞는 매출이 없습니다. 위에서 조건 하나를 ✕로 풀면 다시 보입니다.';return}
  renderTiles(rows,P);renderTrend(rows,P);renderDaily(rows,P);renderPivot(rows,P);renderWhy(rows,P);renderDealer(rows,P);
}
setupControls();render();
"""

HTML=r"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>매출 대시보드 — 기준본</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600;700&family=IBM+Plex+Mono:wght@400&display=swap">
<style>__CSS__</style></head><body><div class="wrap">
<div class="eyebrow">세션 2 · 대시보드 기준본</div>
<h1>한국총괄 B2B영업 매출 대시보드</h1>
<p class="src">자료 <span class="mono">매출데이터.csv</span> __N__행 · __FROM__ ~ __TO__ · 기준일 __TO__ · 모든 값은 가상입니다</p>

<p class="how">위에서 조건을 고르면 아래 화면이 <b>전부 같이</b> 바뀝니다. 표의 줄을 누르면 그 안으로 들어가고, ✕를 누르면 다시 나옵니다.</p>
<div class="bar-row" role="group" aria-label="조건">
<label>기준월<select id="fm"></select></label>
<label>파트<select id="fp"></select></label>
<label>수요처<select id="fc"></select></label>
<label>품목<select id="fi"></select></label>
<button id="reset" type="button">처음 화면으로</button>
</div>
<div class="scope" id="scope"></div>
<div class="empty" id="empty" hidden></div>

<section class="sec"><h2>1. 한눈에 <span class="who">모두</span></h2>
<div class="tiles" id="tiles"></div><p class="note" id="tileNote"></p></section>

<section class="sec" id="sec-trend"><h2>2. 월별 매출 — 올해와 작년 <span class="who">임원</span></h2>
<p class="sub">달 위에 마우스를 올리면 금액이, 누르면 그 달이 기준월이 됩니다. 속이 빈 점은 아직 덜 찬 달입니다.</p>
<div class="legend"><span class="k"><i style="border-color:var(--s1)"></i>__Y__년</span><span class="k"><i style="border-color:var(--s2);border-top-style:dashed"></i>__PY__년</span></div>
<div id="trend"></div></section>

<section class="sec" id="sec-day"><h2>3. 일별 매출 <span class="who">보직장</span></h2>
<p class="sub">기준월의 하루하루입니다. 막대를 누르면 그날 무엇이 팔렸는지 아래 표에 나옵니다.</p>
<div id="daily"></div><p class="note" id="dailyNote"></p><div id="dayRows"></div></section>

<section class="sec" id="sec-pivot"><h2>4. 나눠 보기 <span class="who">보직장 · 품목 담당</span></h2>
<div class="ctl"><span class="seg" id="dimSeg" role="group" aria-label="무엇별로 나눌지"></span></div>
<p class="note" id="pivotHint"></p><div id="pivot"></div><p class="note" id="pivotUnit"></p></section>

<section class="sec" id="sec-why"><h2>5. 왜 이렇게 됐나 — 작년보다 어디서 달라졌나 <span class="who">임원</span></h2>
<div id="why"></div>
<p class="note">여기서 알 수 있는 것은 <b>'어디서'</b>까지입니다. <b>'왜'</b>는 가설로 적고 영업 담당에게 확인합니다 — 예: 작년에 한 번뿐인 큰 납품이 있었나, 그 고객에게 공사 · 이전 같은 일이 있나.</p></section>

<section class="sec" id="sec-dealer"><h2>6. 판매처(대리점) 1곳이 수요처 몇 곳을 맡나 <span class="who">보직장</span></h2>
<div id="dealer"></div></section>

<section class="sec"><h2>확인 필요</h2><div class="chk">
<p>· 소계 대조 — 품목구분 · 주문유형 · 수요처명 · 파트명 · 판매처명 다섯 축을 <span class="mono">매출데이터_소계.csv</span>와 맞춰 봤고 <b>__SUBOK__</b>.</p>
<p>· 이 헤더에는 <b>단가 열이 없어</b> <span class="mono">단가 × 수량 = 금액</span> 검산을 할 수 없습니다. 소계 대조가 그 자리를 대신합니다.</p>
<p>· 데이터는 <b>__TO__까지</b>입니다. 이번 달 비교는 모두 같은 날짜까지 자른 값입니다.</p>
<p>· 직판주문은 헤더 설명대로 판매처 = 수요처라, 판매처별로 볼 때 '직판' 한 줄로 묶었습니다. 직판일 때 판매처 주소는 비어 있습니다.</p>
<p>· 파트명과 주문유형이 1:1입니다(경로1파트 = 유통주문). 실제로 섞이는지 확인 필요.</p>
<p>· 모델명은 가상입니다. 실제 조회 가능한 모델명이 들어오면 그대로 반영됩니다.</p>
</div></section>

<div class="foot">세션 2 기준본 · 모든 수요처명 · 판매처명 · 모델명 · 금액은 가상이며 삼성전자 실제 정보와 무관합니다</div>
</div><div id="tip" role="status" aria-live="polite"></div>
<script>__JS__</script></body></html>"""

js=(JS.replace("__LK__",json.dumps(LK,ensure_ascii=False)).replace("__ROWS__",json.dumps(PAY,separators=(",",":")))
      .replace("__LAST__",str(CUTOFF.year*10000+CUTOFF.month*100+CUTOFF.day)))
page=(HTML.replace("__CSS__",CSS).replace("__JS__",js).replace("__N__",f"{len(ROWS):,}")
          .replace("__FROM__",ROWS[0][10]).replace("__TO__",CUTOFF.isoformat()).replace("__Y__","2026").replace("__PY__","2025")
          .replace("__SUBOK__","전부 일치합니다" if SUB_OK else "어긋나는 곳이 있습니다"))
open(os.path.join(D4,"대시보드.html"),"w",encoding="utf-8").write(page)
print(f"04_기준본/대시보드.html  {os.path.getsize(os.path.join(D4,'대시보드.html'))//1024}KB · 소계 대조 {'일치' if SUB_OK else '불일치'}")
