<!doctype html>
<html lang="zh-CN" data-ic-base="../../kit/assets/icons" data-icons="mono" data-bg="glow">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>文件模板库</title>
<link rel="icon" href="../../kit/assets/solid/solid-content.webp">
<link rel="stylesheet" href="../../kit/tokens.css">
<link rel="stylesheet" href="../../kit/ui.css">
<link rel="stylesheet" href="../../kit/kit.css">
<link rel="stylesheet" href="../../kit/web.css">
<style>
  /* 文件模板库目录页：数据由 build_documents_index.py 内嵌；类名带 dx 前缀，不引用其它页面的样式 */
  body { background: var(--bg); }
  .dx { max-width: 1480px; margin: 0 auto; padding: 0 var(--s-6) var(--s-12); }

  /* 页面顶部：平面区，主题浅色渐变加花瓣纹理 */
  .dx-top { position: relative; isolation: isolate; margin: 0 calc(var(--s-6) * -1); padding: var(--s-6) var(--s-6) var(--s-5); background: linear-gradient(180deg, var(--action-tint) 0%, var(--bg) 100%); }
  .dx-row { display: flex; align-items: center; justify-content: space-between; gap: var(--s-4); flex-wrap: wrap; }
  .dx-brand { display: flex; align-items: center; gap: var(--s-3); }
  .dx-brand img { width: 44px; height: 44px; object-fit: contain; }
  .dx-brand h1 { font-size: var(--fs-3xl); font-weight: 700; line-height: var(--lh-tight); white-space: nowrap; }
  .dx-tools { display: flex; align-items: center; gap: var(--s-5); flex-wrap: wrap; }
  .dx-tools .search { width: 340px; max-width: 100%; }
  .dx-swatches { display: flex; gap: var(--s-2); }
  .dx-swatch { width: 28px; height: 28px; border-radius: 50%; background: var(--action); box-shadow: inset 0 0 0 2px var(--surface), 0 0 0 1px var(--line-strong); transition: transform var(--dur-quick) var(--ease-out); }
  .dx-swatch[aria-pressed="true"] { box-shadow: inset 0 0 0 3px var(--surface), 0 0 0 2px var(--action); transform: scale(1.1); }

  /* 模块标题放在卡片外上方，左对齐 */
  .dx-mod { margin-top: var(--s-8); }
  .dx-mod__head { display: flex; align-items: baseline; gap: var(--s-3); padding: 0 var(--s-1); }
  .dx-mod__head h2 { font-size: var(--fs-xl); font-weight: 700; line-height: var(--lh-tight); }
  .dx-mod__head span { font-size: var(--fs-sm); color: var(--ink-3); }
  .dx-mod__body { margin-top: var(--s-4); }

  /* 命名规则与目录结构 */
  .dx-rules { display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: var(--s-6); align-items: start; }
  .dx-rules > div { min-width: 0; }
  .dx-rules .dx-mod { margin-top: var(--s-6); }
  .dx-table { table-layout: auto; }
  .dx-table td, .dx-table th { white-space: nowrap; }
  .dx-table td.t-wrap { white-space: normal; overflow: visible; }
  .dx-kind { display: inline-flex; align-items: center; gap: var(--s-2); font-weight: 600; vertical-align: middle; line-height: 1; }
  .dx-kind img { width: 28px; height: 28px; object-fit: contain; flex: none; }
  .dx-tree { padding: var(--s-5); font-size: var(--fs-md); color: var(--ink-2); }
  .dx-tree ul { margin-left: var(--s-5); padding-left: var(--s-4); border-left: 1px solid var(--line-strong); }
  .dx-tree li { position: relative; padding: 3px 0; line-height: 1.6; }
  .dx-tree ul li::before { content: ""; position: absolute; left: calc(var(--s-4) * -1); top: 15px; width: var(--s-3); border-top: 1px solid var(--line-strong); }
  .dx-tree b { color: var(--ink); font-weight: 600; }
  .dx-dirs { display: inline-flex; flex-wrap: wrap; gap: var(--s-1) var(--s-3); }
  .dx-tree small { margin-left: var(--s-2); font-size: var(--fs-sm); color: var(--ink-3); }

  /* 类型标签 */
  .dx-pills { display: flex; gap: var(--s-2); overflow-x: auto; padding: var(--s-6) 2px var(--s-2); scrollbar-width: none; }
  .dx-pills::-webkit-scrollbar { display: none; }
  .dx-pill { flex: none; display: inline-flex; align-items: center; gap: var(--s-2); min-height: 40px; padding: 0 var(--s-4); border-radius: var(--r-full); background: var(--surface); box-shadow: var(--elev-1); font-size: var(--fs-md); font-weight: 500; color: var(--ink-2); transition: background var(--dur-quick) var(--ease-out), color var(--dur-quick) var(--ease-out); }
  .dx-pill small { font-size: var(--fs-xs); font-weight: 600; padding: 1px 7px; border-radius: var(--r-full); background: var(--zone); color: var(--ink-2); }
  .dx-pill[aria-pressed="true"] { background: var(--ink); color: var(--bg); }
  .dx-pill[aria-pressed="true"] small { background: rgba(255, 255, 255, .2); color: var(--bg); }
  .dx-count { margin-left: auto; align-self: center; font-size: var(--fs-sm); color: var(--ink-3); white-space: nowrap; }

  /* 模板卡 */
  .dx-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(400px, 100%), 1fr)); gap: var(--s-4); align-items: start; }
  .dx-card { display: flex; flex-direction: column; gap: var(--s-3); padding: var(--s-4); background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); box-shadow: var(--elev-1); scroll-margin-top: var(--s-6); }
  .dx-card:target { box-shadow: 0 0 0 2px var(--action), var(--elev-2); }
  .dx-thumb { display: grid; place-items: center; aspect-ratio: 16 / 9; border-radius: var(--r-md); overflow: hidden; background: var(--action-tint); border: 1px solid var(--line); }
  .dx-thumb .dx-pv { width: 100%; height: 100%; object-fit: cover; }
  .dx-thumb .dx-ic { width: 72px; height: 72px; object-fit: contain; }
  .dx-card__head { display: flex; align-items: center; gap: var(--s-3); }
  .dx-card__head > img { width: 40px; height: 40px; object-fit: contain; flex: none; }
  .dx-card__head h3 { flex: 1; min-width: 0; font-size: var(--fs-lg); font-weight: 600; line-height: var(--lh-tight); }
  .dx-copy { flex: none; min-height: 28px; padding: 0 var(--s-2); border-radius: var(--r-sm); background: var(--zone); color: var(--action-press); font-size: var(--fs-xs); font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: .02em; transition: background var(--dur-quick) var(--ease-out); }
  .dx-copy:hover { background: var(--action-edge); }
  .dx-use { min-height: calc(var(--fs-sm) * 3.2); font-size: var(--fs-sm); color: var(--ink-2); line-height: 1.6; }
  .dx-links { display: flex; align-items: center; gap: var(--s-2); margin-top: auto; padding-top: var(--s-1); }
  .dx-cmd { border-top: 1px solid var(--line); padding-top: var(--s-2); }
  .dx-cmd summary { display: flex; align-items: center; justify-content: space-between; min-height: 36px; font-size: var(--fs-sm); font-weight: 600; color: var(--ink-2); cursor: pointer; list-style: none; }
  .dx-cmd summary::-webkit-details-marker { display: none; }
  .dx-cmd[open] .chev::after { transform: rotate(45deg); }
  .dx-cmd__body { display: grid; gap: var(--s-2); padding-bottom: var(--s-1); }
  .dx-cmd__row { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: start; gap: var(--s-2); padding: var(--s-2) var(--s-3); background: var(--bg); border: 1px solid var(--line); border-radius: var(--r-md); }
  .dx-cmd__lab { font-size: var(--fs-xs); font-weight: 600; color: var(--action-press); line-height: 28px; white-space: nowrap; }
  .dx-cmd__row code { font: inherit; font-size: var(--fs-sm); color: var(--ink); line-height: 1.6; white-space: pre-wrap; word-break: break-all; padding-top: 2px; }

  /* 复用块表 */
  .dx-parts td.t-l { padding-left: var(--s-5); }
  .dx-chips { display: flex; flex-wrap: wrap; gap: var(--s-1) var(--s-2); }
  .dx-chips a { display: inline-flex; align-items: center; height: 24px; padding: 0 var(--s-2); border-radius: var(--r-sm); background: var(--action-tint); color: var(--action-press); font-size: var(--fs-xs); font-weight: 600; font-variant-numeric: tabular-nums; transition: background var(--dur-quick) var(--ease-out); }
  .dx-chips a:hover { background: var(--action-edge); }
  .dx-parts td.dx-type { background: var(--bg); }

  .dx-empty { display: none; margin-top: var(--s-8); }
  .dx-empty.on { display: grid; }

  @media (max-width: 1000px) { .dx-rules { grid-template-columns: minmax(0, 1fr); gap: 0; } }
  @media (max-width: 760px) { .dx { padding: 0 var(--s-4) var(--s-8); } .dx-top { margin: 0 calc(var(--s-4) * -1); padding: var(--s-4); } .dx-brand h1 { font-size: var(--fs-2xl); } .dx-tools { width: 100%; } .dx-tools .search { width: 100%; } }
</style>
</head>
<body>
<div class="dx">
  <header class="dx-top bgfx">
    <div class="dx-row">
      <div class="dx-brand"><img data-ic="bouquet" src="../../kit/assets/icons/flat/bouquet.webp" alt=""><h1>文件模板库</h1></div>
      <div class="dx-tools">
        <label class="search"><img src="../../kit/assets/line/search.webp" alt=""><input id="q" type="search" placeholder="搜索编号、名称或用途" aria-label="搜索编号、名称或用途"></label>
      </div>
    </div>
  </header>

  <section class="dx-rules" aria-label="命名规则与目录结构">
    <div class="dx-mod">
      <div class="dx-mod__head"><h2>命名规则</h2></div>
      <div class="dx-mod__body card card--flat">
        <div class="table-wrap">
          <table class="table table--static dx-table">
            <thead><tr><th>类型</th><th>编号</th><th>文件名</th><th>目录</th></tr></thead>
            <tbody id="rules"></tbody>
          </table>
        </div>
      </div>
    </div>
    <div class="dx-mod">
      <div class="dx-mod__head"><h2>目录结构</h2></div>
      <div class="dx-mod__body card card--flat">
        <ul class="dx-tree">
          <li><b>templates/documents/</b>
            <ul>
              <li>index.html<small>本页</small></li>
              <li>documents.html<small>目录页</small></li>
              <li>README.md</li>
              <li><span class="dx-dirs"><b>word/</b><b>excel/</b><b>slides/</b><b>pdf/</b><b>reading/</b></span>
                <ul>
                  <li>README.md</li>
                  <li>manifest.json<small>登记表</small></li>
                  <li>specs/<small>描述文件</small></li>
                  <li>specs/parts/<small>可复用块</small></li>
                  <li>samples/<small>样例文件</small></li>
                  <li>tools/<small>补充脚本</small></li>
                </ul>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </section>

  <div class="dx-row">
    <nav class="dx-pills" id="pills" aria-label="文件类型"></nav>
    <span class="dx-count" id="count" role="status"></span>
  </div>

  <main id="cats"></main>

  <section class="dx-mod" id="parts" aria-label="可复用块" hidden>
    <div class="dx-mod__head"><h2>可复用块</h2><span id="partcount"></span></div>
    <div class="dx-mod__body card card--flat">
      <div class="table-wrap">
        <table class="table table--static dx-table dx-parts">
          <thead><tr><th>类型</th><th>编号</th><th>名称</th><th class="t-l">用于哪些模板</th></tr></thead>
          <tbody id="partrows"></tbody>
        </table>
      </div>
    </div>
  </section>

  <div class="empty dx-empty" id="empty"><img data-ic="vase" src="../../kit/assets/icons/flat/vase.webp" alt=""><span id="emptytext">没有匹配的模板</span></div>
</div>
<script src="../../kit/ui.js"></script>
<script>@DATA@</script>
<script>
  (function () {
    const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
    const ORDER = ['word', 'excel', 'slides', 'pdf', 'reading'];
    const META = {
      word: { title: '文字文档', code: 'WD', icon: 'biz-notes' },
      excel: { title: '表格文件', code: 'XL', icon: 'layout' },
      slides: { title: '幻灯片', code: 'SL', icon: 'biz-demo' },
      pdf: { title: 'PDF', code: 'PD', icon: 'biz-review' },
      reading: { title: '阅读网页', code: 'RD', icon: 'solid-content' }
    };
    const types = ((window.LZ_DOCS && window.LZ_DOCS.types) || []).slice().sort((a, b) => ORDER.indexOf(a.type) - ORDER.indexOf(b.type));
    const state = { cat: 'all', q: '' };
    const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const url = (t, p) => encodeURI(t.dir + '/' + p);
    const icon = t => `../../kit/assets/solid/${(META[t.type] || META.word).icon}.webp`;
    const label = t => t.title || (META[t.type] || {}).title || t.type;
    const nameOf = (t, id) => { const hit = t.items.find(i => i.id === id); return hit ? hit.name : id; };

    // 命名规则表：每类一行
    $('#rules').innerHTML = ORDER.map(k => {
      const t = types.find(x => x.type === k), m = META[k];
      return `<tr><td class="t-l"><span class="dx-kind"><img src="../../kit/assets/solid/${m.icon}.webp" alt="">${esc(t ? label(t) : m.title)}</span></td>` +
        `<td>DC-${m.code}-NNN</td><td>${esc(t ? t.naming : 'DC-' + m.code + '-三位序号-中文名')}</td><td>${esc(k)}/</td></tr>`;
    }).join('');

    // 类型标签
    const total = types.reduce((n, t) => n + t.items.length, 0), totalParts = types.reduce((n, t) => n + t.parts.length, 0);
    $('#pills').innerHTML = `<button class="dx-pill" data-cat="all" aria-pressed="true">全部<small>${total}</small></button>` +
      types.map(t => `<button class="dx-pill" data-cat="${esc(t.type)}" aria-pressed="false">${esc(label(t))}<small>${t.items.length}</small></button>`).join('');

    const match = (text) => !state.q.trim() || text.toLowerCase().includes(state.q.trim().toLowerCase());

    function cardHTML(t, it) {
      const thumb = it.preview ? `<div class="dx-thumb"><img class="dx-pv" src="${esc(url(t, it.preview))}" alt="${esc(it.name)}样例"></div>` : '';
      const lead = it.preview ? '' : `<img src="${icon(t)}" alt="">`;
      const checks = (Array.isArray(it.checks) ? it.checks : [it.checks]).filter(Boolean);
      const row = (lab, cmd) => `<div class="dx-cmd__row"><span class="dx-cmd__lab">${lab}</span><code>${esc(cmd)}</code><button class="btn btn--text btn--sm" data-copy="${esc(cmd)}" aria-label="复制${lab}命令">复制</button></div>`;
      return `<article class="dx-card" id="${esc(it.id)}" aria-label="${esc(it.name)}">
        ${thumb}
        <div class="dx-card__head">${lead}<h3 class="one-line">${esc(it.name)}</h3><button class="dx-copy" data-copy="${esc(it.id)}" aria-label="复制编号 ${esc(it.id)}">${esc(it.id)}</button></div>
        <p class="dx-use">${esc(it.use)}</p>
        <div class="dx-links">
          <a class="btn btn--secondary btn--sm" href="${esc(url(t, it.file))}" target="_blank" rel="noopener">样例文件</a>
          <a class="btn btn--text btn--sm" href="${esc(url(t, it.spec))}" target="_blank" rel="noopener">描述文件</a>
        </div>
        <details class="dx-cmd"><summary>生成与检查命令<span class="chev"></span></summary>
          <div class="dx-cmd__body">${row('生成', it.generator)}${checks.map(c => row('检查', c)).join('')}</div>
        </details>
      </article>`;
    }

    function draw() {
      let shown = 0, html = '';
      const rows = [];
      types.forEach(t => {
        if (state.cat !== 'all' && state.cat !== t.type) return;
        const items = t.items.filter(i => match([i.id, i.name, i.use, label(t)].join(' ')));
        if (items.length) {
          shown += items.length;
          const commercial = t.type === 'slides' ? '<a href="slides/commercial-sources.md">商用模板与授权</a>' : '';
          html += `<section class="dx-mod" data-cat="${esc(t.type)}" aria-label="${esc(label(t))}"><div class="dx-mod__head"><h2>${esc(label(t))}</h2><span>${commercial || `${items.length} 个模板`}</span></div><div class="dx-mod__body dx-grid">${items.map(i => cardHTML(t, i)).join('')}</div></section>`;
        }
        const parts = t.parts.filter(p => match([p.id, p.name, label(t)].concat((p.used_in || []).map(u => u + ' ' + nameOf(t, u))).join(' ')));
        if (parts.length) rows.push({ t, parts });
      });
      $('#cats').innerHTML = html;
      const n = rows.reduce((s, r) => s + r.parts.length, 0);
      $('#parts').hidden = n === 0;
      $('#partcount').textContent = n + ' 个';
      $('#partrows').innerHTML = rows.map(({ t, parts }) => parts.map((p, i) =>
        `<tr>${i === 0 ? `<td class="dx-type" rowspan="${parts.length}"><span class="dx-kind"><img src="${icon(t)}" alt="">${esc(label(t))}</span></td>` : ''}` +
        `<td><button class="dx-copy" data-copy="${esc(p.id)}" aria-label="复制编号 ${esc(p.id)}">${esc(p.id)}</button></td>` +
        `<td>${esc(p.name)}</td>` +
        `<td class="t-l t-wrap"><div class="dx-chips">${(p.used_in || []).map(u => `<a href="#${esc(u)}" data-tip="${esc(nameOf(t, u))}" data-go="${esc(t.type)}">${esc(u)}</a>`).join('')}</div></td></tr>`).join('')).join('');
      $('#count').textContent = state.cat === 'all' && !state.q.trim() ? `${total} 个模板　${totalParts} 个复用块` : `${shown} 个模板`;
      const none = shown === 0 && n === 0;
      $('#emptytext').textContent = types.length === 0 || total === 0 ? '还没有登记的模板' : '没有匹配的模板';
      $('#empty').classList.toggle('on', none);
    }

    async function copy(text) {
      try { await navigator.clipboard.writeText(text); }
      catch (e) {
        const a = document.createElement('textarea'); a.value = text; a.style.position = 'fixed'; a.style.opacity = '0'; document.body.appendChild(a); a.select();
        const ok = document.execCommand('copy'); a.remove(); if (!ok) throw e;
      }
    }
    document.addEventListener('click', async e => {
      const b = e.target.closest('[data-copy]');
      if (b) { try { await copy(b.dataset.copy); Lz.toast('已复制 ' + (b.dataset.copy.length > 24 ? '命令' : b.dataset.copy), 'success'); } catch (err) { Lz.toast('复制失败', 'danger'); } return; }
      const go = e.target.closest('[data-go]');
      if (go) { // 复用块指向的模板可能被类型标签或搜索隐藏，先放开再跳转
        e.preventDefault(); const id = go.getAttribute('href').slice(1);
        if (!document.getElementById(id)) { state.cat = 'all'; state.q = ''; $('#q').value = ''; $$('.dx-pill').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.cat === 'all'))); draw(); }
        const el = document.getElementById(id); if (el) { location.hash = id; el.scrollIntoView({ behavior: Lz.reduce ? 'auto' : 'smooth', block: 'center' }); }
      }
    });
    $('#pills').addEventListener('click', e => { const b = e.target.closest('.dx-pill'); if (!b) return; $$('.dx-pill').forEach(x => x.setAttribute('aria-pressed', String(x === b))); state.cat = b.dataset.cat; draw(); });
    $('#q').addEventListener('input', e => { state.q = e.target.value; draw(); });
    draw();
  })();
</script>
</body>
</html>
