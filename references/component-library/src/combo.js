/* ===== 整页组合：同一个通用页面，按槽位换组件 ===== */
const COMBO = '整页组合'
const byName = (n) => BLOCKS.find((b) => b.name === n)
const SLOTS = [
  { id: 'head', label: '头部', opts: [['渐变头图 + 商品图', 'promo'], ['浅色头图 + 大图标', 'calm'], ['图片背景 + 主题遮罩', 'content'], ['玻璃面板叠图', 'premium'], ['轮播横幅（露出两侧）', 'promo'], ['拼贴双栏（一大两小）', 'promo']] },
  { id: 'entry', label: '入口', opts: [['3 × 2 金刚区', 'calm'], ['4 + 3 圆形底', 'calm'], ['大卡片入口', 'promo'], ['横滑胶囊条', 'calm'], ['无底大图标', 'content']] },
  { id: 'card', label: '商品卡', opts: [['标准商品卡', 'calm'], ['横向列表卡', 'calm'], ['大图沉浸卡', 'content'], ['玻璃信息卡', 'premium'], ['极简线框卡', 'premium'], ['暗金奢品卡', 'premium'], ['立体促销卡', 'promo']] },
  { id: 'btn', label: '主按钮', opts: [['渐变实心', 'calm'], ['浅底', 'calm'], ['线框', 'premium'], ['立体厚底', 'promo'], ['金色营销', 'promo']] },
  { id: 'nav', label: '底部导航', opts: [['标准', 'calm'], ['凸起中间按钮', 'promo'], ['悬浮胶囊', 'content']] },
  { id: 'price', label: '价格与标签', opts: [['标准红价 + 渐变标签', 'promo'], ['克制黑价 + 浅底标签', 'calm'], ['金色价格 + 深色标签', 'premium'], ['胶囊价 + 线框标签', 'promo']] },
]
const PRICE_CLS = { '标准红价 + 渐变标签': 'pt-std', '克制黑价 + 浅底标签': 'pt-calm', '金色价格 + 深色标签': 'pt-prem', '胶囊价 + 线框标签': 'pt-pill' }
const BTN_BLOCK = { '渐变实心': ['渐变主按钮', 'b1', 'x'], '浅底': ['浅底与线框按钮', 'b2', 's'], '线框': ['浅底与线框按钮', 'b2', 'o'], '立体厚底': ['立体厚底按钮', 'b5', 'x'], '金色营销': ['金色营销按钮', 'b7', 'x'] }
const TONE_TEXT = {
  calm: ['克制稳妥', '适合日常电商、工具类首页和信息密度高的页面，不抢内容，换主题色最容易。'],
  promo: ['促销感强', '适合大促、拉新、活动页，能把人推向“点一下”；一屏只放一个强对比模块，其余用克制的样式托住。'],
  premium: ['安静高级', '适合高客单价、品牌店和会员制，留白多、促销少，靠质感而不是颜色说话。'],
  content: ['氛围与内容', '适合内容种草、品牌故事和节日专题，图片是主角；价格和按钮要保持清晰，别被图片淹没。'],
}
const COMBO_CSS = `.cmb{width:min(390px,100%);margin:0 auto;background:var(--n3);border-radius:40px;padding:14px 0 0;overflow:hidden;box-shadow:0 0 0 10px var(--ink),0 24px 48px var(--sh20);color:var(--ink)}.cmb-top{display:flex;align-items:center;gap:10px;padding:10px 16px 12px}.cmb-top b{font-size:18px;font-weight:600}.cmb-search{flex:1;height:36px;border-radius:18px;background:var(--card);color:var(--ink2);display:flex;align-items:center;gap:6px;padding:0 12px;font-size:14px}.cmb-search svg{width:16px;height:16px;flex:none}.cmb-sec{display:flex;justify-content:center;padding:6px 0 10px}.cmb-sec .st{min-height:0;border-radius:24px;padding:18px 12px;width:calc(100% - 24px)}.cmb-h{display:flex;align-items:baseline;justify-content:space-between;padding:8px 18px 2px}.cmb-h b{font-size:18px;font-weight:600}.cmb-h a{font-size:14px;color:var(--ink2)}.cmb-cta{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:4px 16px 14px;padding:14px 16px;background:var(--card);border-radius:22px;box-shadow:0 4px 16px var(--sh08)}.cmb-cta>div:first-child{display:flex;flex-direction:column;gap:2px}.cmb-cta b{font-size:16px;font-weight:600}.cmb-cta span{font-size:12px;color:var(--ink2)}.cmb-cta .bt{width:auto;flex:none}.cmb-cta .b1,.cmb-cta .b2,.cmb-cta .b5,.cmb-cta .b7{display:block}.cmb .n2{width:100%;gap:0}.cmb .n2 .t{border-radius:0;box-shadow:0 -4px 14px var(--sh06);padding-bottom:18px}.cmb .n2 .t.fl{margin:0 14px 14px;border-radius:30px;padding:8px 10px;box-shadow:0 10px 24px var(--sh14)}.cmb .n2 .nvw{background:var(--n3)}.cmb.pt-calm .price{color:var(--ink)}.cmb.pt-calm .tg-hot{background:var(--pt);color:var(--p-text)}.cmb.pt-prem .price{color:var(--gold-ink2)}.cmb.pt-prem .tg-hot{background:var(--inv);color:#E6D3A3}.cmb.pt-pill .price{background:var(--pt);color:var(--p-text);padding:5px 9px;border-radius:14px}.cmb.pt-pill .price b{font-size:18px}.cmb.pt-pill .tg-hot{background:var(--card);color:var(--danger);box-shadow:inset 0 0 0 1px #E4B0A8}`
function stageWrap(b) { return b.bg || b.stage === 'dark' ? `<div class="st ${stageClass(b.stage)}" ${b.bg ? `style="background-image:url(${ASSETS.bg[b.bg]})"` : ''}>${b.html()}</div>` : b.html() }
function ctaHTML(v) {
  const [, w, c] = BTN_BLOCK[v]
  const label = v === '立体厚底' ? '立即抢购' : v === '金色营销' ? '立即升级' : '立即购买'
  return `<div class="cmb-cta"><div><b>新人专享</b><span>首单立减 ¥20</span></div><div class="${w}"><button class="bt ${c}" type="button">${label}</button></div></div>`
}
function navHTML(v) {
  const t = (ic, tx, on) => `<button class="${on ? 'on' : ''}" type="button">${sv(ic)}${tx}</button>`
  if (v === '凸起中间按钮') return `<div class="n2"><div class="t">${t('home', '首页', 1)}${t('grid', '分类')}<button class="ctr" type="button"><i>${sv('plus')}</i><span>发布</span></button>${t('chat', '消息')}${t('user', '我的')}</div></div>`
  if (v === '悬浮胶囊') return `<div class="n2"><div class="nvw"><div class="t fl">${t('home', '首页', 1)}${t('grid', '分类')}${t('cart', '购物车')}${t('user', '我的')}</div></div></div>`
  return `<div class="n2"><div class="t">${t('home', '首页', 1)}${t('grid', '分类')}${t('cart', '购物车')}${t('user', '我的')}</div></div>`
}
function comboHTML() {
  const c = S.combo
  return `<div class="cmb ${ICS()} ${PRICE_CLS[c.price]}"><div class="cmb-top"><b>示例品牌</b><span class="cmb-search">${sv('search')}搜索商品、品牌</span></div><div class="cmb-sec">${stageWrap(byName(c.head))}</div><div class="cmb-sec">${stageWrap(byName(c.entry))}</div><div class="cmb-h"><b>为你推荐</b><a>更多 ›</a></div><div class="cmb-sec">${stageWrap(byName(c.card))}</div>${ctaHTML(c.btn)}${navHTML(c.nav)}</div>`
}
function comboNote() {
  const c = S.combo
  const tones = SLOTS.map((s) => s.opts.find((o) => o[0] === c[s.id])[1])
  const n = (k) => tones.filter((t) => t === k).length
  const order = ['promo', 'premium', 'content', 'calm']
  const top = order.slice().sort((a, b) => n(b) - n(a) || order.indexOf(a) - order.indexOf(b))[0]
  let warn = ''
  if (n('promo') >= 4) warn = '促销样式叠得太多，用户不知道该点哪里：换掉 1–2 个，只留头部或按钮其中一个强对比。'
  else if (n('premium') >= 1 && (c.btn === '立体厚底' || c.btn === '金色营销' || c.price === '标准红价 + 渐变标签')) warn = '高端质感的卡片配促销味的按钮或价格，会互相打架：按钮换成“渐变实心”或“线框”，价格换成“克制黑价”或“金色价格”。'
  else if (n('calm') === tones.length) warn = '很稳，但略平：让头部或按钮多一点个性，其余保持克制。'
  return `<div class="cn"><b>这套组合：${TONE_TEXT[top][0]}</b><p>${TONE_TEXT[top][1]}</p>${warn ? `<p class="cw"><em>提醒</em>${warn}</p>` : ''}</div>`
}
function comboPage() {
  const ctl = SLOTS.map((s) => `<div class="sl"><h3>${s.label}</h3><div class="chs">${s.opts.map(([o]) => `<button type="button" class="cc" data-slot="${s.id}" data-opt="${o}" aria-pressed="${S.combo[s.id] === o}">${o}</button>`).join('')}</div></div>`).join('')
  return `<div class="cmbw"><div class="cmbl"><section class="guide cmbc"><h2>整页组合：换组件看效果</h2>${ctl}${comboNote()}<button class="cp" type="button" data-combocopy="1"><svg viewBox="0 0 24 24"><rect x="8" y="8" width="12" height="12" rx="2.5"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>复制这套组合的编号</button></section></div><div class="cmbr">${comboHTML()}</div></div>`
}
function comboIds() {
  const c = S.combo
  const ids = [c.head, c.entry, c.card, BTN_BLOCK[c.btn][0], '标签栏三种形态', '价格样式集'].map((n) => LEGACY[n])
  return ids
}
function copyCombo() {
  const c = S.combo
  const text = comboIds().join(' + ') + `（整页组合：${SLOTS.map((s) => c[s.id]).join(' / ')}）`
  copyText(text, '已复制这套组合的编号')
}
