#!/usr/bin/env python3
"""새 모듈 폴더 만들기 — `_template/`을 복사하고 이름을 채운다.

    python3 docs/samsung-ax/tools/new_module.py E_forecast forecasting-demand-by-region

만든 뒤 순서 (module_spec.md 4장):
    1. 00_requirement.md 를 채운다            ← 여기가 원본. 나머지는 파생물
    2. build_modules.py 에 build_E() 를 추가하고 데이터를 만든다
    3. 02_prompt/ 완성 프롬프트를 쓴다 (자리 0개)
    4. 실제 도구에 돌려 04_answer/ 를 받는다
    5. 03_tests/ 를 실제로 넣어 본다
    6. 05_demo_log.md 를 오간 대화로 채운다
    7. 07_skill/SKILL.md · module.md · CHECK.md 를 마감하고 check_module.py 를 돌린다
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = os.path.normpath(os.path.join(HERE, "..", "context_pack", "modules"))
ID_RE = re.compile(r"^[A-Z]_[a-z][a-z0-9_]*$")
NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    mod_id, skill_name = sys.argv[1], sys.argv[2]
    if not ID_RE.match(mod_id):
        sys.exit(f"모듈 ID 형식이 아닙니다: {mod_id}  (예: E_forecast — 대문자 한 글자 + _ + 소문자)")
    if not NAME_RE.match(skill_name):
        sys.exit(f"스킬 이름 형식이 아닙니다: {skill_name}  (소문자-하이픈, 동명사형. 예: forecasting-demand-by-region)")
    dst = os.path.join(MODULES, mod_id)
    if os.path.exists(dst):
        sys.exit(f"이미 있습니다: {dst}")

    shutil.copytree(os.path.join(MODULES, "_template"), dst)
    for rel in ["00_requirement.md", "module.md", "CHECK.md", "05_demo_log.md",
                os.path.join("07_skill", "SKILL.md")]:
        p = os.path.join(dst, rel)
        txt = open(p, encoding="utf-8").read()
        txt = (txt.replace("X_name", mod_id).replace("{모듈 ID}", mod_id)
                  .replace("doing-something-for-team", skill_name)
                  .replace("{스킬 이름}", skill_name))
        open(p, "w", encoding="utf-8").write(txt)

    print(f"만들었습니다: context_pack/modules/{mod_id}/")
    print(f"  스킬 이름  : {skill_name}")
    print("\n다음 순서")
    print("  1. 00_requirement.md 를 채웁니다 (여기가 원본입니다)")
    print(f"  2. tools/build_modules.py 에 build_{mod_id.split('_')[0]}() 를 추가합니다")
    print(f"  3. python3 docs/samsung-ax/tools/check_module.py {mod_id}  로 남은 것을 확인합니다")


if __name__ == "__main__":
    main()
