// 검수 도구 브라우저 점검 — build_test_tool.py가 부른다. 0 = 통과, 1 = 실패, 2 = playwright 없음
let chromium;
try { const pw = process.env.PWPATH || require('child_process').execSync('npm root -g').toString().trim() + '/playwright'; ({chromium} = require(pw)); } catch (e) { console.log('playwright 없음'); process.exit(2); }
const fs = require('fs'), file = process.argv[2];
(async () => {
  const exe = ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find(p => fs.existsSync(p));
  const b = await chromium.launch(exe ? {executablePath: exe} : {});
  const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(300);
  const fail = []; const ok = (c, m) => { if (!c) fail.push(m); };
  const n = await p.$$eval('.nv', x => x.length); ok(n > 0, '단계 목록이 비어 있음');
  const st = async () => [await p.$$eval('.checks .chip.bad', x => x.length), await p.$eval('#sug', e => e.textContent), await p.$$eval('.checks .hint', x => x.length)];
  const set = async v => { await p.fill('#resp', v); await p.dispatchEvent('#resp', 'input'); };
  // 모든 단계: 기대 결과 문장을 그대로 넣으면 자동 제안이 '통과' (! 검사 제외 문장이라도 경쟁사가 없으니 통과)
  for (let i = 1; i <= n; i++) {
    await p.click(`.nv[data-n="${i}"]`);
    const forb = await p.evaluate(k => DATA.steps[k - 1].checks.filter(c => c.startsWith('!')).map(c => c.slice(1)), i);
    let exp = await p.$eval('.exp', e => e.textContent.replace(/^기대 결과/, ''));
    forb.forEach(w => { exp = exp.split(w).join(''); });   // '없어야 함' 단어는 빼고 넣는다
    await set(exp); const [bad, sug] = await st(); ok(bad === 0 && sug.includes('통과'), `${i}단계: 기대 결과를 넣었는데 통과가 아님 (${sug})`);
    await set(''); const [, sug2, hint] = await st(); ok(sug2 === '' && hint === 1, `${i}단계: 응답을 지워도 안내 상태로 안 돌아감`);
    // 음수 검사: 부호를 뗀 응답은 실패해야 한다
    const negs = await p.evaluate(k => DATA.steps[k - 1].checks.filter(c => c.startsWith('-')), i);
    if (negs.length) { await set(exp.replace(/[−-](?=\d)/g, '')); const [b2] = await st(); ok(b2 >= negs.length, `${i}단계: 부호 없는 숫자가 음수 검사를 통과함`); await set(''); }
  }
  // 저장 · 이동 · 보고서
  await p.click('.nv[data-n="1"]'); await set('저장점검'); await p.click('.verdict .b[data-v="part"]');
  await p.click('[data-go="1"]'); ok((await p.$eval('.where', e => e.textContent)).startsWith('2 /'), '다음 단계로 안 넘어감');
  await p.reload(); await p.waitForTimeout(200); await p.click('.nv[data-n="1"]');
  ok((await p.$eval('#resp', e => e.value)) === '저장점검', '새로고침 뒤 응답이 사라짐');
  await p.click('.tab[data-v="report"]'); ok((await p.$eval('#v-report pre', e => e.textContent)).includes('| 1 |') , '보고서에 단계가 없음');
  await p.evaluate(() => localStorage.clear());
  ok(errs.length === 0, '페이지 오류: ' + errs.join(' / '));
  await b.close();
  console.log(fail.length ? '브라우저 점검 실패\n  - ' + fail.join('\n  - ') : `브라우저 점검 통과 — ${n}단계 모두 (기대값 통과 · 삭제 시 안내 복귀 · 음수 부호 · 저장 · 이동 · 보고서)`);
  process.exit(fail.length ? 1 : 0);
})().catch(e => { console.log('점검 중 오류: ' + e.message); process.exit(1); });
