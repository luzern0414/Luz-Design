<!doctype html>
<html lang="zh-CN" data-ic-base="../../kit/assets/icons" data-theme="navy" data-icons="mono" data-bg="none">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@TITLE@</title>
<link rel="stylesheet" href="../../kit/tokens.css">
<link rel="stylesheet" href="../../kit/ui.css">
<link rel="stylesheet" href="../../kit/kit.css">
<link rel="stylesheet" href="../../kit/@END_CSS@.css">
<link rel="stylesheet" href="../../kit/agent.css">
<style>
  /* 分类与搜索下方的组件卡共享对齐网格。 */
  body, body.app-body, body.web-body { margin: 0; background: var(--bg); }
  .lib { padding: 0 var(--s-5) var(--s-8); }
  .bar { position: sticky; top: 0; z-index: 5; display: flex; align-items: center; gap: var(--s-3); margin: 0 calc(var(--s-5) * -1); padding: var(--s-3) var(--s-5); background: color-mix(in srgb, var(--bg) 94%, transparent); backdrop-filter: blur(8px); border-bottom: 1px solid var(--line); }
  .pills { display: flex; flex: 1; gap: var(--s-2); overflow-x: auto; scrollbar-width: none; }
  .pills::-webkit-scrollbar { display: none; }
  .pill { flex: none; display: inline-flex; align-items: center; gap: var(--s-2); min-height: 34px; padding: 0 var(--s-3); border-radius: var(--r-sm); background: var(--surface); box-shadow: inset 0 0 0 1px var(--line); font-size: var(--fs-sm); font-weight: 500; color: var(--ink-2); transition: background var(--dur-quick) var(--ease-out), color var(--dur-quick) var(--ease-out); }
  .pill small { font-size: var(--fs-xs); font-weight: 600; color: var(--ink-3); font-variant-numeric: tabular-nums; }
  .pill:hover { background: var(--zone); }
  .pill[aria-pressed="true"] { background: var(--ink); color: var(--surface); box-shadow: none; }
  .pill[aria-pressed="true"] small { color: color-mix(in srgb, var(--surface) 70%, transparent); }
  .bar .search { flex: none; width: 240px; max-width: 34%; }
  .cat { margin-top: var(--s-6); }
  .cat__head { display: flex; align-items: baseline; gap: var(--s-3); margin-bottom: var(--s-3); padding: 0 var(--s-1); }
  .cat__head h2 { margin: 0; font-size: var(--fs-xl); font-weight: 700; line-height: var(--lh-tight); }
  .cat__head span { font-size: var(--fs-sm); color: var(--ink-3); }
  .cat .gallery { --demo-min: var(--col, @COL@px); grid-auto-flow: row; align-items: stretch; gap: 0 var(--s-3); }
  .cat .gallery > .demo { display: grid; align-content: start; min-width: 0; padding: var(--s-3); gap: var(--s-2); background: var(--surface); border-radius: var(--r-lg); box-shadow: inset 0 0 0 1px var(--line); }
  .demo__head { min-height: 0; padding: 0; align-items: flex-start; }
  .demo__name { font-size: var(--fs-md); font-weight: 600; }
  .demo__meta { display: flex; align-items: center; gap: var(--s-2); flex: none; }
  .demo__copy { min-height: 26px; padding: 0 var(--s-2); border-radius: var(--r-sm); background: var(--zone); color: var(--action-press); font-size: var(--fs-xs); font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: .02em; }
  .demo__copy:hover { background: var(--action-edge); }
  .demo__note { margin: 0; font-size: var(--fs-sm); color: var(--ink-3); line-height: 1.45; }
  .demo__stage { padding: var(--s-3); min-height: 0; background: var(--bg); border-radius: var(--r-md); box-shadow: inset 0 0 0 1px var(--line); overflow: hidden; }
  /* 整行宽：版式壳、宽表格等本来就要几百像素宽的组件，独占一整行；窗口再窄时舞台横向滚动而不是被裁 */
  .cat .gallery > .demo--span2, .cat .gallery > .demo--wide { grid-column: 1 / -1; }
  .demo--span2 .demo__stage, .demo--wide .demo__stage { overflow-x: auto; }
  .demo__stage.is-plain { background: transparent; box-shadow: none; padding: 0; }
  .demo__stage.is-tint { background: var(--action-tint); }
  .demo__stage.is-dark-free { background: var(--surface); }
  .empty-lib { display: none; margin-top: var(--s-8); }
  .empty-lib.on { display: grid; }
</style>
@PART_STYLES@
</head>
<body class="@BODY_CLASS@">
<div class="lib">
  <div class="bar">
    <nav class="pills" id="pills" aria-label="组件分类">@PILLS@</nav>
    <label class="search"><img src="../../kit/assets/line/search.webp" alt=""><input id="q" type="search" placeholder="搜索编号或名称" aria-label="搜索编号或名称"></label>
  </div>
  <main id="cats">
@PARTS@
  </main>
  <div class="empty empty-lib" id="empty"><img data-ic="vase" src="../../kit/assets/icons/flat/vase.webp" alt=""><span>没有匹配的组件</span></div>
</div>
<script src="../../kit/ui.js"></script>
@PART_SCRIPTS@
<script>
  (function () {
    const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
    const state = { cat: 'all', q: '' };
    // 每个组件头部补“复制编号”
    $$('.demo').forEach(d => {
      const head = $('.demo__head', d); if (!head || $('.demo__copy', head)) return;
      const id = d.dataset.cid; const meta = document.createElement('div'); meta.className = 'demo__meta';
      const old = $('.demo__id', head); if (old) old.remove();
      meta.innerHTML = `<button class="demo__copy" data-copy="${id}" aria-label="复制编号 ${id}">${id}</button>`;
      head.appendChild(meta);
    });
    document.addEventListener('click', async e => {
      const b = e.target.closest('.demo__copy[data-copy]'); if (!b) return;
      try { await navigator.clipboard.writeText(b.dataset.copy); Lz.toast('已复制 ' + b.dataset.copy, 'success'); } catch (err) { Lz.toast('复制失败', 'danger'); }
    });
    function draw() {
      const q = state.q.trim().toLowerCase(); let shown = 0;
      $$('.cat').forEach(sec => {
        const catOn = state.cat === 'all' || sec.dataset.cat === state.cat; let n = 0;
        $$('.demo', sec).forEach(d => {
          const on = catOn && (!q || (d.dataset.cid + ' ' + d.dataset.name + ' ' + ($('.demo__note', d) || {}).textContent).toLowerCase().includes(q));
          d.hidden = !on; if (on) n++;
        });
        sec.hidden = n === 0; shown += n;
      });
      $('#empty').classList.toggle('on', shown === 0);
    }
    $('#pills').addEventListener('click', e => { const b = e.target.closest('.pill'); if (!b) return; $$('.pill').forEach(x => x.setAttribute('aria-pressed', String(x === b))); state.cat = b.dataset.cat; draw(); scrollTo(0, 0); });
    $('#q').addEventListener('input', e => { state.q = e.target.value; draw(); });
    draw();
  })();
</script>
</body>
</html>
