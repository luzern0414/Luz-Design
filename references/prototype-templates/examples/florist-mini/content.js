/* ===== 花间集小程序：内容模块 =====
 * 由 mini 模板 + spec.json + 本文件生成。模板只画手机框、状态栏、导航栏、标签栏、弹层与提示；
 * 这里只有花店的页面正文、业务计算与动作。状态放在模块变量 S 里，「重置演示数据」时由 init 重建。
 * 本文件被包进 (function (K, LIB) { … })(K, LIB) 运行；类名一律带 fl- 前缀，不与组件库的类名冲突。 */
const { tileHTML, critter } = LIB
const esc = K.esc

/* 花店专属的线性图标（库里没有这六个） */
Object.assign(LIB.LINE, {
  bouquet: '<path d="M7 8c0 4 1.5 7 5 7s5-3 5-7c-1.5 1-3 .5-5-1.5C10 8.5 8.5 9 7 8z"/><path d="M12 15v6M12 19c-2.5 0-4-1-4.5-3 2.5 0 4 1 4.5 3z"/>',
  plant: '<path d="M7.5 15h9l-1 6h-7zM12 11c-3 0-5-1.5-5-4.5 3 0 5 1.5 5 4.5zM12 9c0-3 2-5 5-5 0 3-2 5-5 5z"/><path d="M12 15V9"/>',
  vase: '<path d="M9.5 8h5v2c2.5 1 3.5 3 3.5 5.5 0 3.5-2.5 5.5-6 5.5s-6-2-6-5.5c0-2.5 1-4.5 3.5-5.5z"/><path d="M12 8V4M12 6c1.5-1 3-1 4-2"/>',
  shears: '<circle cx="6" cy="18.5" r="2.5"/><circle cx="18" cy="18.5" r="2.5"/><path d="m8 16.5 10-12M16 16.5 6 4.5"/>',
  watering: '<path d="M5 11h9l-1 8H6z"/><path d="M14 13h3l3-5"/><path d="M5 11V9a3 3 0 0 1 3-3h3"/>',
  seedling: '<path d="M12 21v-9"/><path d="M12 12c0-3-2-5-6-5 0 3 2 5 6 5z"/><path d="M12 14c0-3 2-5 6-5 0 3-2 5-6 5z"/>',
})
const sv = (n, cls = '') => `<svg class="fl-svg ${cls.split(' ').filter(Boolean).map((c) => 'fl-' + c).join(' ')}" viewBox="0 0 24 24" aria-hidden="true">${LIB.LINE[n] || ''}</svg>`
const prod = (i) => LIB.ASSETS.prod[i]
const money = (n) => `<span class="price"><small>¥</small><b>${n}</b></span>`
const tgHot = (t) => (t ? `<span class="tg tg-hot">${t}</span>` : '')

/* ---------- 状态与数据（init 时从 K.data 建立） ---------- */
let D = null, S = null
let PRODUCTS, CATS, PACKS, ADDRS, STORES, COUPONS, POINTS, DAYS, SLOTS, SLOT_STATE, ORDER_ST, REVIEWS, FAQ, LEGAL, CHIPS, LISTMAP

function init(data) {
  D = data
  ;({ products: PRODUCTS, cats: CATS, packs: PACKS, addrs: ADDRS, stores: STORES, coupons: COUPONS, points: POINTS, days: DAYS, slots: SLOTS, slotState: SLOT_STATE, orderSt: ORDER_ST, reviews: REVIEWS, faq: FAQ, legal: LEGAL, chips: CHIPS, listMap: LISTMAP } = data)
  S = {
    cart: K.clone(data.cart),
    fav: { 0: 1, 2: 1, 4: 1, 8: 1 },
    spec: { p: 0, si: 0, pk: 0, q: 1, mode: 'cart' }, buy: null,
    co: { mode: 'deliver', addr: 0, store: 0, day: 0, slot: 4, coupon: 0, points: false, card: '', anon: false, note: '', oid: '' },
    payFrom: '', orders: K.clone(data.orders),
    cate: 0, chip: 0, hotPill: 0, sortBy: 0, dayTmp: 0, slotTmp: 4, cpTmp: 0,
    stype: 0, sreason: 0, rate: 5, rtags: [0], anonR: false, sw: { sub1: true, sub2: false, pers: true }, kw: '',
  }
  data.S = S
  Object.defineProperty(data, 'cartCount', { get: () => cartCount(), enumerable: true, configurable: true })
}

/* ---------- 业务计算 ---------- */
const cartPicked = () => S.cart.filter((i) => i.on && !i.bad)
const cartCount = () => (S ? S.cart.reduce((s, i) => s + (i.bad ? 0 : i.q), 0) : 0)
const priceOf = (p, si = 0, pk = 0) => PRODUCTS[p].sizes[si][1] + PACKS[pk][1]
const itemPrice = (i) => priceOf(i.p, i.si, i.pk)
const orderTotal = (o) => o.its.reduce((s, [p, sp, q]) => s + (PRODUCTS[p].sizes.find((z) => z[0] === sp) || PRODUCTS[p].sizes[0])[1] * q, 0)
const orderBy = (id) => S.orders.find((o) => o.id === id) || S.orders[0]
const cnt = (st) => S.orders.filter((o) => (Array.isArray(st) ? st.includes(o.st) : o.st === st)).length
const coItems = () => (S.buy ? [S.buy] : cartPicked())
const couponOk = (c, sub, items) => sub >= c.min && (c.id !== 2 || items.some((i) => PRODUCTS[i.p].cat === 1))
function bestCoupon(sub, items) {
  let best = -1, v = 0
  COUPONS.forEach((c, i) => { if (couponOk(c, sub, items) && c.amt > v) { best = i; v = c.amt } })
  return best
}
function coCalc() {
  const items = coItems(), sub = items.reduce((s, i) => s + itemPrice(i) * i.q, 0)
  if (S.co.coupon === -2) S.co.coupon = bestCoupon(sub, items)
  const fee = S.co.mode === 'pickup' ? 0 : sub >= 199 ? 0 : 10
  const cp = S.co.coupon >= 0 ? COUPONS[S.co.coupon] : null
  const cpv = cp && couponOk(cp, sub, items) ? cp.amt : 0
  const pts = S.co.points ? Math.min(Math.floor(POINTS / 100), Math.floor((sub - cpv) * 0.1)) : 0
  return { items, sub, fee, cpv, pts, pay: Math.max(0, sub + fee - cpv - pts), low: S.co.mode === 'deliver' && sub < 68 }
}
const slotText = () => {
  const [d, dt] = DAYS[S.co.day]
  return `${d} ${dt === '11-04' ? '' : dt + ' '}${SLOTS[S.co.slot]}`.replace('  ', ' ')
}
const isEmptyCart = () => K.scene('cart') === 'empty' || S.cart.length === 0
const listIds = (kw) => {
  const m = LISTMAP[kw]
  if (m) return PRODUCTS.map((p, i) => i).filter((i) => m.includes(PRODUCTS[i].cat))
  const f = PRODUCTS.map((p, i) => i).filter((i) => PRODUCTS[i].n.includes(kw))
  return f.length ? f : PRODUCTS.map((p, i) => i)
}
const ensureCheckout = () => { if (!S.buy && !cartPicked().length) S.buy = { p: 0, si: 0, pk: 0, q: 1 } }

/* ---------- 公共片段 ---------- */
/* 自定义渲染里的每一块都包上最接近的库组件编号（display:contents，不影响布局），审计按 data-cid 核对控件来源 */
const C = (cid, h) => `<div class="fl-cid" data-cid="${cid}">${h}</div>`
const empty = (ic, t, d, btn, cid = 'MP-ORD-002') => C(cid, `<div class="fl-empty">${tileHTML(ic, K.cfg.iconTile)}<h3>${t}</h3><p>${d}</p>${btn || ''}</div>`)
const pcard = (i) => {
  const p = PRODUCTS[i]
  return `<div class="fl-pcard" data-pt-go="detail:${i}"><div class="fl-im"><img src="${prod(i)}" alt="">${tgHot(p.t)}<button type="button" class="fl-fav ${S.fav[i] ? 'fl-on' : ''}" data-pt-act="fav:${i}" aria-label="收藏">${sv('heart')}</button></div><div class="fl-bd"><h4>${p.n}</h4><div class="fl-meta">${p.d}</div><div class="fl-pr"><div>${LIB.priceHTML(p.p, p.o)}</div><button type="button" class="fl-add" data-pt-sheet="sheet-spec:${i}:cart" aria-label="加入购物车">${sv('plus')}</button></div></div></div>`
}
const lrow = (i) => {
  const p = PRODUCTS[i]
  return `<div class="fl-lrow" data-pt-go="detail:${i}"><img src="${prod(i)}" alt=""><div class="fl-t"><h4>${p.n}</h4><div class="fl-meta">${p.d} · ${p.s}</div><div style="margin-top:6px">${p.t ? tgHot(p.t) : '<span class="tg tg-soft">当日达</span>'}</div><div class="fl-pr"><div>${LIB.priceHTML(p.p, p.o)}</div><button type="button" class="fl-add" data-pt-sheet="sheet-spec:${i}:cart" aria-label="加入购物车">${sv('plus')}</button></div></div></div>`
}
const thumbs = (o) => o.its.map(([p]) => `<img src="${prod(p)}" alt="">`).join('')
const stTag = (st) => `<b class="fl-stt fl-st-${st}">${ORDER_ST[st][0]}</b>`
const cell = (ic, t, v, go) => `<button type="button" class="fl-cell" data-pt-go="${go}">${sv(ic, 'i')}<span>${t}</span>${v ? `<em class="fl-v">${v}</em>` : ''}${sv('chev', 'chev')}</button>`
const fbar = (inner) => C('MP-BTN-009', `<div class="fl-fbar">${inner}</div>`)

const pages = {}

/* ---------- 首页 ---------- */
pages.home = () => {
  const dark = K.cfg.header === 'light'
  const entries = [['bouquet', '同城鲜花'], ['giftbox', '节日礼盒'], ['plant', '绿植盆栽'], ['vase', '周期订花'], ['shears', '花艺定制']].map(([n, t]) => `<button type="button" data-pt-go="list:${t}">${tileHTML(n, K.cfg.iconTile)}<span>${t}</span></button>`).join('')
  const pills = ['热销', '新品', '礼盒', '绿植'].map((t, i) => `<button class="fl-pill ${S.hotPill === i ? 'fl-on' : ''}" type="button" data-pt-act="hotpill:${i}">${t}</button>`).join('')
  const ids = [[0, 1, 2, 3, 4, 5], [1, 6, 8, 3, 2, 0], [8, 7, 1, 0, 3, 2], [5, 4, 6, 5, 4, 6]][S.hotPill]
  const claim = K.scene('newc') === 'got' ? '' : `<div class="fl-newc"><div class="fl-l"><h4>新人礼券</h4><div class="fl-big"><small>¥</small>20</div><small class="fl-s">满 99 可用</small></div>${LIB.icon('coupon')}<button class="btn btn-p btn-sm" type="button" data-pt-act="claim">立即领取</button></div>`
  return `${C('MP-HDR-007', `<div class="fl-hdr ${dark ? 'fl-dark' : ''}"><button class="fl-loc" type="button" data-pt-go="store">${sv('pin')}<span><b>配送至 建国路 88 号</b><em>建国路店 · 营业至 21:00</em></span>${sv('down')}</button>
   <button class="fl-search" type="button" data-pt-go="search">${sv('search')}<span>搜索花束、绿植、礼盒</span></button>
   <div class="fl-hero"><div><span class="fl-tagline">春日鲜花节</span><h2>把春天带回家</h2><p>同城 2 小时达<br>满 199 免配送费</p><button class="btn" type="button" data-pt-go="list:春日鲜花节">去选花 ›</button></div>
     ${K.cfg.header === 'image' ? '<div></div>' : `<div class="fl-pic"><img src="${prod(1)}" alt=""><b>热卖 TOP1</b></div>`}</div></div>`)}
  <div class="fl-notice">${sv('clock')}<span>今日 17:00 截单，现在下单最早 17:00–19:00 送达</span></div>
  ${C('MP-ENT-001', `<div class="fl-entry">${entries}</div>`)}${claim && C('MP-MKT-001', claim)}
  ${C('MP-CARD-001', `<div class="fl-sec"><h3>当季热卖</h3><button type="button" class="fl-more" data-pt-go="list:当季热卖">全部 ›</button></div>`)}
  ${C('MP-NAV-003', `<div class="fl-pills">${pills}</div>`)}${C('MP-CARD-001', `<div class="fl-grid2">${ids.map(pcard).join('')}</div>`)}
  <p class="fl-end">没有更多了</p>`
}

/* ---------- 分类 ---------- */
pages.cat = () => {
  const rail = CATS.map(([n, t], i) => `<button type="button" class="${S.cate === i ? 'fl-on' : ''}" data-pt-act="cate:${i}">${tileHTML(n, K.cfg.iconTile)}${t}</button>`).join('')
  const ch = CHIPS[S.cate], chips = ch.length > 1 ? `<div class="fl-chips">${ch.map((t, i) => `<button class="fl-chip ${S.chip === i ? 'fl-on' : ''}" type="button" data-pt-act="chip:${i}">${t}</button>`).join('')}</div>` : ''
  const ids = PRODUCTS.map((p, i) => i).filter((i) => PRODUCTS[i].cat === S.cate && (S.chip === 0 || PRODUCTS[i].n.includes(ch[S.chip])))
  return `<div class="fl-cat">${C('MP-FORM-001', `<div class="fl-cat-top"><button class="fl-search" type="button" data-pt-go="search">${sv('search')}<span>搜索花束、绿植、礼盒</span></button></div>`)}
  <div class="fl-cat-wrap">${C('MP-NAV-004', `<div class="fl-rail" id="flRail">${rail}</div>`)}<div class="fl-cat-main"><h3 class="fl-ct">${CATS[S.cate][1]}</h3>${C('MP-NAV-003', chips)}${ids.length ? C('MP-CARD-002', ids.map(lrow).join('')) : empty('bouquet', '暂无商品', '该分类商品正在上新', '', 'MP-CARD-002')}</div></div></div>`
}

/* ---------- 购物车 ---------- */
pages.cart = () => {
  const items = isEmptyCart() ? [] : S.cart
  const ok = items.filter((i) => !i.bad), bad = items.filter((i) => i.bad)
  const sel = ok.filter((i) => i.on), sub = sel.reduce((s, i) => s + itemPrice(i) * i.q, 0)
  const row = (i, k) => `<div class="fl-crow"><button type="button" class="fl-ck ${i.on ? 'fl-on' : ''}" data-pt-act="cartToggle:${k}" aria-label="选择">${i.on ? sv('check') : ''}</button><img src="${prod(i.p)}" alt="" data-pt-go="detail:${i.p}"><div class="fl-t"><h4>${PRODUCTS[i.p].n}</h4><div class="fl-meta">${PRODUCTS[i.p].sizes[i.si][0]} · ${PACKS[i.pk][0]}</div><div class="fl-pr"><div>${money(itemPrice(i))}</div><div class="fl-qty"><button type="button" data-pt-act="qty:${k}:-1" aria-label="减少">${sv('minus')}</button><b>${i.q}</b><button type="button" data-pt-act="qty:${k}:1" aria-label="增加">${sv('plus')}</button></div></div></div><button type="button" class="fl-del" data-pt-act="cartDel:${k}" aria-label="删除">${sv('trash')}</button></div>`
  const tipOv = sub >= 199
    ? { text: { '.t span!': '同城配送 · 已享受免配送费' }, hide: ['.t a'], attrs: { '.pg i': { style: 'width:100%' } } }
    : { text: { '.t span!': `同城配送 · 再买 ¥${199 - sub} 免配送费` }, go: { '.t a': 'list:当季热卖' }, attrs: { '.pg i': { style: `width:${Math.min(100, Math.round(sub / 199 * 100))}%` } } }
  const body = items.length ? `${K.block('MP-MKT-004', tipOv)}
    ${C('MP-ORD-001', `<div class="fl-card fl-cgrp"><h4 class="fl-store">${sv('pin')}花间集 · 建国路店</h4>${ok.map((i) => row(i, S.cart.indexOf(i))).join('')}</div>`)}
    ${bad.length ? C('MP-ORD-001', `<div class="fl-card fl-cgrp"><h4 class="fl-store fl-gray">失效商品 ${bad.length}<button type="button" class="fl-lnk" data-pt-act="cartClear">清空失效</button></h4>${bad.map((i) => `<div class="fl-crow fl-off"><img src="${prod(i.p)}" alt=""><div class="fl-t"><h4>${PRODUCTS[i.p].n}</h4><div class="fl-meta">已售罄，暂时无法购买</div><button type="button" class="btn btn-s btn-sm" data-pt-go="list:花艺定制" style="align-self:flex-start;margin-top:8px">找相似</button></div></div>`).join('')}</div>`) : ''}` : empty('cart', '购物车是空的', '挑几束喜欢的花吧', `<button class="btn btn-p" type="button" data-pt-go="list:当季热卖">去逛逛</button>`)
  return body
}
pages.cartBar = () => {
  if (isEmptyCart()) return ''
  const ok = S.cart.filter((i) => !i.bad), sel = ok.filter((i) => i.on), sub = sel.reduce((s, i) => s + itemPrice(i) * i.q, 0)
  const all = ok.length && ok.every((i) => i.on)
  return C('MP-ORD-002', `<div class="fl-sbar"><button type="button" class="fl-ck ${all ? 'fl-on' : ''}" data-pt-act="cartAll" aria-label="全选">${all ? sv('check') : ''}</button><span class="fl-all">全选</span><div class="fl-tot"><div class="fl-l1">合计 ${money(sub)}</div><em>不含配送费</em></div><button type="button" class="btn btn-p" data-pt-act="checkout" data-pt-primary>去结算${sel.length ? `（${sel.reduce((s, i) => s + i.q, 0)}）` : ''}</button></div>`)
}

/* ---------- 我的 ---------- */
pages.me = () => {
  const dark = K.cfg.header === 'light'
  const o = [['receipt', '待付款', ['pay']], ['giftbox', '备货中', ['make']], ['truck', '配送中', ['ship']], ['star', '待评价', ['done']], ['refresh', '退款/售后', ['refund']]]
  const ent = o.map(([ic, t, st]) => `<button type="button" data-pt-go="orders:${st[0]}">${sv(ic)}<span>${t}</span>${cnt(st) ? `<b>${cnt(st)}</b>` : ''}</button>`).join('')
  const m = D.member
  return `${C('MP-HDR-008', `<div class="fl-hdr fl-me ${dark ? 'fl-dark' : ''}"><div class="fl-who">${critter(0, 60)}<div><h3>林小满</h3><p>微信用户 · 已绑定手机号</p></div></div>
   <button type="button" class="fl-mcard" data-pt-go="member"><div class="fl-r1"><b>${m.level}</b><span>${m.points.toLocaleString('en-US')} 积分</span></div><div class="fl-prog"><i style="width:${Math.round(m.growth / m.target * 100)}%"></i></div><div class="fl-r2">再获 ${(m.target - m.growth).toLocaleString('en-US')} 成长值升级${m.next}</div></button></div>`)}
  ${C('MP-ENT-009', `<div class="fl-card fl-ord"><div class="fl-oh"><h4>我的订单</h4><button type="button" class="fl-more" data-pt-go="orders:all">全部订单 ›</button></div><div class="fl-oent">${ent}</div></div>`)}
  ${C('MP-ENT-010', `<div class="fl-cells">${cell('coupon', '优惠券', '3 张可用', 'coupons')}${cell('heart', '我的收藏', `${Object.values(S.fav).filter(Boolean).length} 件`, 'favs')}${cell('pin', '收货地址', '', 'address')}</div>
  <div class="fl-cells">${cell('chat', '联系客服', '', 'help')}${cell('gear', '设置', '', 'settings')}</div>`)}`
}

/* ---------- 搜索（用库的搜索导航组件：热搜词、最近搜索、联想） ---------- */
pages.search = () => {
  const ov = { hide: ['.top .loc', '.top .wx'], text: {}, act: {}, attrs: { 'input': { 'data-pt-enter': 'searchEnter', 'data-pt-inp': 'kw' } } }
  D.hotWords.forEach((w, i) => { ov.text[`.hot@0 .ws button@${i}`] = w; ov.act[`.hot@0 .ws button@${i}`] = `hist:${w}` })
  D.hist.slice(0, 3).forEach((w, i) => { ov.text[`.hot@1 .ws button@${i}`] = w; ov.act[`.hot@1 .ws button@${i}`] = `hist:${w}` })
  ov.text['.sug .ls button@0'] = '红玫瑰花束'; ov.text['.sug .ls button@1'] = '粉芍药花束'; ov.text['.sug .ls button@2'] = '向日葵花束'
  ov.text['.sug .ls button@3'] = '白郁金香'; ov.text['.sug .ls button@4'] = '蓝绣球盆栽'; ov.text['.sug .ls button@5'] = '多肉组合'
  ov.text['.rl'] = '红玫瑰花束'
  return K.block('MP-NAV-006', ov)
}

/* ---------- 商品列表 ---------- */
pages.list = (f) => {
  const a = f.a
  const ids = listIds(a)
  const ord = S.sortBy === 1 ? [...ids].sort((x, y) => PRODUCTS[y].p - PRODUCTS[x].p) : S.sortBy === 2 ? [...ids].sort((x, y) => PRODUCTS[x].p - PRODUCTS[y].p) : ids
  const fl = ['综合', '价格高', '价格低'].map((t, i) => `<button type="button" class="${S.sortBy === i ? 'fl-on' : ''}" data-pt-act="sort:${i}">${t}</button>`).join('')
  return `<h3 class="fl-ct fl-lt">${esc(a || '商品列表')}</h3>${C('MP-NAV-005', `<div class="fl-fbar2">${fl}<button type="button" class="fl-flt" data-pt-say="已筛选：只看当日可送达">${sv('filter')}当日达</button></div>`)}${C('MP-CARD-001', `<div class="fl-grid2" style="margin-top:10px">${ord.map(pcard).join('')}</div>`)}<p class="fl-end">没有更多了</p>`
}

/* ---------- 商品详情 ---------- */
pages.detail = (f) => {
  const i = +f.a || 0, p = PRODUCTS[i], sp = p.sizes[0]
  const svc = [['scooter', '同城配送'], ['seedling', '保鲜 7 天'], ['giftbox', '免费贺卡']].map(([n, t]) => `<div>${tileHTML(n, K.cfg.iconTile)}${t}</div>`).join('')
  return `${C('MP-GOODS-001', `<div class="fl-gal"><img src="${prod(i)}" alt=""><span class="fl-cnt">1 / 5</span></div>`)}
  <div class="fl-pbar"><div class="fl-pp"><small>¥</small><b>${sp[1]}</b>${p.o ? `<s>¥${p.o}</s>` : ''}</div><div class="fl-lt">限时直降<b>02:15:08</b></div></div>
  <div class="fl-dcard"><h2>${p.n} · ${sp[0]}</h2><p class="fl-sub">${p.desc}</p><div class="fl-tags">${p.t ? tgHot(p.t) : ''}<span class="tg tg-soft">同城当日达</span><span class="tg tg-red">${p.s}</span></div></div>
  ${C('MP-GOODS-007', `<div class="fl-cells"><button type="button" class="fl-cell" data-pt-sheet="sheet-spec:${i}:pick">${sv('tag', 'i')}<span>规格</span><em class="fl-v">${sp[0]} · 牛皮纸</em>${sv('chev', 'chev')}</button>
   <button type="button" class="fl-cell" data-pt-go="store">${sv('truck', 'i')}<span>送至</span><em class="fl-v">建国路 88 号 · 今日 17:00 起</em>${sv('chev', 'chev')}</button>
   <button type="button" class="fl-cell" data-pt-go="legal:购买须知">${sv('shield', 'i')}<span>服务</span><em class="fl-v">缺损包赔 · 鲜度保证</em>${sv('chev', 'chev')}</button></div>`)}
  <div class="fl-dcard"><div class="fl-svc">${svc}</div></div>
  ${C('MP-GOODS-004', `<div class="fl-dcard"><div class="fl-oh"><h4>商品评价（2,386）</h4><button type="button" class="fl-more" data-pt-go="reviews:${i}">查看全部 ›</button></div><div class="fl-rv1"><div class="fl-rt">${critter(1, 28)}<b>小**满</b><span class="fl-stars">${'★'.repeat(5)}</span></div><p>${REVIEWS[0].t}</p></div></div>`)}
  <div class="fl-dcard"><div class="fl-oh"><h4>商品详情</h4></div><img class="fl-dimg" src="${prod((i + 1) % 9)}" alt=""><img class="fl-dimg" src="${prod((i + 2) % 9)}" alt=""></div>`
}
pages.detailBar = (f) => {
  const i = +f.a || 0
  const out = K.scene('stock') === 'out'
  const main = out
    ? `<button type="button" class="btn btn-p fl-grow" data-pt-say="已登记到货提醒，到货后第一时间通知你">到货提醒</button>`
    : `<div class="fl-split"><button class="fl-a" type="button" data-pt-sheet="sheet-spec:${i}:cart">加入购物车</button><button class="fl-b" type="button" data-pt-sheet="sheet-spec:${i}:buy" data-pt-primary>立即购买</button></div>`
  return C('MP-GOODS-010', `<div class="fl-dbar"><button type="button" class="fl-mini ${S.fav[i] ? 'fl-on' : ''}" data-pt-act="fav:${i}">${sv('heart')}收藏</button><button type="button" class="fl-mini" data-pt-go="help">${sv('chat')}客服</button>${main}</div>`)
}

/* ---------- 商品评价（评分汇总用库的评价摘要组件） ---------- */
pages.reviews = () => {
  const ov = { text: { 'h3': '商品评价', 'h3 em': '2,386 条', '.sc small': '好评率 98.6%', '.im': '大家印象' }, hide: ['.hd button'] }
  ;['花朵新鲜', '包装精美', '送达准时', '贺卡好看'].forEach((t, i) => { ov.text[`.tgs .it@${i}`] = t })
  ov.hide.push('.tgs .it@4', '.tgs .it@5')
  return `${K.block('MP-GOODS-004', ov)}${REVIEWS.map((r, k) => `<div class="fl-card fl-rvc"><div class="fl-rt">${critter(k, 32)}<b>${r.n}</b><span class="fl-stars">${'★'.repeat(r.s)}${'☆'.repeat(5 - r.s)}</span></div><p>${r.t}</p><div class="fl-meta">${r.sp} · ${r.d}</div></div>`).join('')}<p class="fl-end">没有更多了</p>`
}

/* ---------- 配送地址与门店 ---------- */
pages.store = () => `${C('MP-ORD-003', `<div class="fl-cells"><button type="button" class="fl-cell" data-pt-go="address-pick">${sv('pin', 'i')}<span><b>${ADDRS[S.co.addr].a.slice(0, 11)}…</b><small>${ADDRS[S.co.addr].n} ${ADDRS[S.co.addr].ph}</small></span>${sv('chev', 'chev')}</button></div>`)}
  <div class="fl-map">${sv('pin', 'mp1')}${sv('pin', 'mp2')}${sv('pin', 'mp3')}<span>配送范围：门店 8 km 内</span></div>
  <h3 class="fl-gt">附近门店</h3>${C('MP-CARD-010', STORES.map((s, i) => `<button type="button" class="fl-card fl-srow ${S.co.store === i ? 'fl-on' : ''}" data-pt-act="storePick:${i}"><div class="fl-r1"><h4>${s.n}</h4><span>${s.d}</span></div><div class="fl-meta">营业 ${s.t}</div><div class="fl-r3"><span class="tg ${s.ok ? 'tg-soft' : 'tg-red'}">${s.ok ? '可同城配送' : '仅自提'}</span><em>${s.s}</em></div></button>`).join(''))}`

/* ---------- 确认订单 ---------- */
pages.checkout = () => {
  ensureCheckout()
  const c = coCalc(), A = ADDRS[S.co.addr], st = STORES[S.co.store], pk = S.co.mode === 'pickup'
  const far = !pk && K.scene('range') === 'out'
  const cp = S.co.coupon >= 0 ? COUPONS[S.co.coupon] : null
  const addr = pk ? `<button type="button" class="fl-card fl-addr" data-pt-go="store">${sv('pin', 'i')}<div><h4>${st.n}</h4><p>营业 ${st.t} · 距你 ${st.d}</p></div>${sv('chev', 'chev')}</button>` : `<button type="button" class="fl-card fl-addr" data-pt-go="address-pick">${sv('pin', 'i')}<div><h4>${A.n} ${A.ph}${A.tag ? `<span class="tg tg-soft">${A.tag}</span>` : ''}</h4><p>${A.a}</p>${far ? '<p class="fl-warn">该地址超出门店配送范围，请改选门店自提或更换地址</p>' : ''}</div>${sv('chev', 'chev')}</button>`
  const rows = c.items.map((i) => `<div class="fl-orow"><img src="${prod(i.p)}" alt=""><div class="fl-t"><h4>${PRODUCTS[i.p].n}</h4><div class="fl-meta">${PRODUCTS[i.p].sizes[i.si][0]}${i.pk ? ' · ' + PACKS[i.pk][0] : ''} × ${i.q}</div></div>${money(itemPrice(i) * i.q)}</div>`).join('')
  return `${C('MP-ORD-005', `<div class="fl-card fl-seg-card"><div class="fl-seg2 fl-big"><button type="button" aria-pressed="${!pk}" data-pt-act="mode:deliver">${sv('truck')}同城配送</button><button type="button" aria-pressed="${pk}" data-pt-act="mode:pickup">${sv('pin')}门店自提</button></div></div>`)}
   ${C('MP-ORD-003', addr)}
   ${C('MP-ORD-005', `<div class="fl-cells"><button type="button" class="fl-cell" data-pt-sheet="sheet-time">${sv('clock', 'i')}<span>${pk ? '自提时间' : '送达时间'}</span><em class="fl-v fl-hl">${slotText()}</em>${sv('chev', 'chev')}</button></div>`)}
   ${C('MP-ORD-006', `<div class="fl-card">${rows}</div>`)}
   ${C('MP-FORM-003', `<div class="fl-card fl-cardmsg"><div class="fl-oh"><h4>贺卡留言</h4><span class="fl-meta">免费 · 随花送出</span></div><textarea data-pt-inp="card" maxlength="50" placeholder="写一句祝福语（选填，最多 50 字）">${esc(S.co.card)}</textarea><div class="fl-row2"><span>匿名送花（收花人看不到你的名字）</span><button type="button" class="fl-tgl ${S.co.anon ? 'fl-on' : ''}" data-pt-act="anon" role="switch" aria-checked="${S.co.anon}"></button></div></div>`)}
   ${C('MP-ORD-007', `<div class="fl-cells"><button type="button" class="fl-cell" data-pt-sheet="sheet-coupon">${sv('coupon', 'i')}<span>优惠券</span><em class="fl-v ${cp && c.cpv ? 'fl-hl' : ''}">${cp && c.cpv ? '-¥' + c.cpv : cp ? '不满足条件' : '不使用'}</em>${sv('chev', 'chev')}</button>
    <div class="fl-cell">${sv('star', 'i')}<span>积分抵扣<small>${POINTS} 积分，100 积分抵 ¥1</small></span><button type="button" class="fl-tgl ${S.co.points ? 'fl-on' : ''}" data-pt-act="points" role="switch" aria-checked="${S.co.points}"></button></div></div>`)}
   ${C('MP-ORD-017', `<div class="fl-card fl-sum"><div><span>商品金额</span><b>¥${c.sub}</b></div><div><span>${pk ? '自提免配送费' : '配送费'}</span><b>${c.fee ? '¥' + c.fee : '免费'}</b></div>${c.cpv ? `<div><span>优惠券</span><b class="fl-neg">-¥${c.cpv}</b></div>` : ''}${c.pts ? `<div><span>积分抵扣</span><b class="fl-neg">-¥${c.pts}</b></div>` : ''}<div class="fl-t"><span>应付金额</span>${money(c.pay)}</div></div>
   <p class="fl-legal-tip">${sv('info')}鲜花为易损鲜活商品，签收后 24 小时内可申请售后。提交订单即表示同意<button type="button" class="fl-lnk" data-pt-go="legal:购买须知">《购买须知》</button></p>`)}`
}
pages.checkoutBar = () => {
  ensureCheckout()
  const c = coCalc(), far = S.co.mode === 'deliver' && K.scene('range') === 'out'
  const dis = c.low || far
  return fbar(`<div class="fl-tot"><div class="fl-l1">应付 ${money(c.pay)}</div>${c.cpv + c.pts ? `<em>已优惠 ¥${c.cpv + c.pts}</em>` : ''}</div><button type="button" class="btn btn-p ${dis ? 'fl-dis' : ''}" data-pt-act="submit" data-pt-primary>${far ? '超出配送范围' : c.low ? '未达起送价' : '提交订单'}</button>`)
}

/* ---------- 支付结果 ---------- */
const resultBody = (o, ring, h, extra) => `<div class="fl-res"><div class="fl-ring fl-${ring}">${sv(ring === 'ok' ? 'check' : ring === 'wait' ? 'clock' : 'close')}</div><h2>${h}</h2>${extra}</div>`
pages.result = (f) => {
  const [oid, mode] = f.a.split(':'), o = orderBy(oid), amt = o.pay || orderTotal(o) + o.ship
  if (mode === 'wait') return resultBody(o, 'wait', '支付结果确认中', `<p class="fl-why">正在向支付渠道确认，最多等待 10 秒。仍未确认也不会重复扣款，请稍后在订单中查看。</p><div class="fl-card fl-info"><div><span>订单金额</span><b>¥${amt}</b></div><div><span>订单状态</span><b>待付款（确认中）</b></div></div>`)
  return resultBody(o, 'ok', '支付成功', `<div class="fl-amt">${money(amt)}</div>
    <div class="fl-card fl-info"><div><span>送达时间</span><b>${o.slot}</b></div><div><span>${S.co.mode === 'pickup' ? '自提门店' : '配送至'}</span><b>${S.co.mode === 'pickup' ? STORES[S.co.store].n : ADDRS[o.addr].a.slice(0, 14) + '…'}</b></div><div><span>订单状态</span><b>门店已接单，备货中</b></div></div>`)
}
const FAIL_WHY = { 'fail-timeout': '支付超时或未在有效期内完成', 'fail-cancel': '你取消了本次支付', 'fail-balance': '支付账户余额不足，请更换支付方式' }
pages['result-fail'] = (f) => {
  const o = orderBy(f.a), amt = o.pay || orderTotal(o) + o.ship
  const why = FAIL_WHY[K.scene('pay')] || FAIL_WHY['fail-timeout']
  return resultBody(o, 'bad', '支付未完成', `<p class="fl-why">原因：${why}。订单已为你保留 29 分钟，请在有效期内重新支付，超时将自动取消，库存会释放。</p><div class="fl-card fl-info"><div><span>订单金额</span><b>¥${amt}</b></div><div><span>剩余支付时间</span><b>29 分 12 秒</b></div></div>`)
}
pages.resultBar = (f) => {
  const [oid, mode] = f.a.split(':'), o = orderBy(oid)
  return fbar(`<button type="button" class="btn btn-s" data-pt-act="finish">完成</button><button type="button" class="btn btn-p" data-pt-go="order:${o.id}" data-pt-primary>查看订单</button>`)
}
pages.resultFailBar = (f) => {
  const o = orderBy(f.a)
  return fbar(`<button type="button" class="btn btn-s" data-pt-go="order:${o.id}">查看订单</button><button type="button" class="btn btn-p" data-pt-sheet="sheet-pay:${o.id}" data-pt-primary>重新支付</button>`)
}

/* ---------- 订单列表 ---------- */
const OTABS = [['all', '全部', null], ['pay', '待付款', ['pay']], ['make', '备货中', ['make']], ['ship', '配送中', ['ship']], ['done', '待评价', ['done']], ['refund', '售后', ['refund']]]
const oActs = (o) => {
  const b = (t, act, p) => `<button type="button" class="btn ${p ? 'btn-p' : 'btn-s'} btn-sm" ${act}>${t}</button>`
  return {
    pay: b('取消订单', `data-pt-act="cancelAsk:${o.id}"`) + b('去支付', `data-pt-sheet="sheet-pay:${o.id}"`, 1),
    make: b('联系门店', 'data-pt-go="help"') + b('取消订单', `data-pt-act="cancelAsk:${o.id}"`),
    ship: b('联系骑手', 'data-pt-say="已拨打骑手电话（示例）"') + b('确认收货', `data-pt-act="recv:${o.id}"`, 1),
    done: b('申请售后', `data-pt-go="service:${o.id}"`) + b('去评价', `data-pt-go="review:${o.id}"`, 1),
    finished: b('再来一单', `data-pt-act="again:${o.id}"`, 1),
    refund: b('联系客服', 'data-pt-go="help"'),
    cancel: b('再来一单', `data-pt-act="again:${o.id}"`, 1),
  }[o.st]
}
pages.ordersTabs = (f) => C('MP-ORD-013', `<div class="fl-utabs">${OTABS.map(([k, n]) => `<button type="button" class="${(f.a || 'fl-all') === k ? 'fl-on' : ''}" data-pt-act="ordTab:${k}">${n}</button>`).join('')}</div>`)
pages.orders = (f) => {
  const t = OTABS.find((x) => x[0] === (f.a || 'all')) || OTABS[0]
  const list = S.orders.filter((o) => (t[2] ? t[2].includes(o.st) : true))
  const cards = list.map((o) => `<div class="fl-card fl-ocard"><div class="fl-oh"><span class="fl-store2">${sv('pin')}花间集 · 建国路店</span>${stTag(o.st)}</div><div class="fl-thumbs" data-pt-go="order:${o.id}">${thumbs(o)}<div class="fl-tp"><span>共 ${o.its.reduce((s, x) => s + x[2], 0)} 件</span>${money(o.pay || orderTotal(o) + o.ship)}</div></div><div class="fl-oact">${oActs(o)}</div></div>`).join('')
  return `${cards ? C('MP-ORD-013', cards) : empty('giftcard', '还没有相关订单', '去挑一束喜欢的花吧', `<button class="btn btn-p" type="button" data-pt-go="list:当季热卖">去逛逛</button>`, 'MP-ORD-013')}${cards ? '<p class="fl-end">没有更多了</p>' : ''}`
}

/* ---------- 订单详情 ---------- */
const FLOW5 = ['已下单', '已支付', '备货中', '配送中', '已送达']
const stepIdx = { pay: 0, make: 2, ship: 3, done: 4, finished: 4 }
pages.order = (f) => {
  const o = orderBy(f.a), [stn, sd] = ORDER_ST[o.st], A = ADDRS[o.addr], tot = orderTotal(o), pay = o.pay || tot + o.ship
  const steps = stepIdx[o.st] !== undefined ? `<div class="fl-card fl-steps">${FLOW5.map((s, k) => `<div class="${k <= stepIdx[o.st] ? 'fl-on' : ''}"><i>${k <= stepIdx[o.st] ? sv('check') : ''}</i><span>${s}</span></div>`).join('<hr>')}</div>` : o.st === 'refund' ? `<div class="fl-card fl-steps">${['已申请', '商家审核', '退款中', '已退款'].map((s, k) => `<div class="${k <= 2 ? 'fl-on' : ''}"><i>${k <= 2 ? sv('check') : ''}</i><span>${s}</span></div>`).join('<hr>')}</div>` : ''
  const rider = o.st === 'ship' ? `<div class="fl-card fl-rider">${critter(2, 40)}<div><h4>骑手 张师傅</h4><p>正在配送 · 距你 1.2 km</p></div><button type="button" class="fl-ph" data-pt-say="已拨打骑手电话（示例）" aria-label="联系骑手">${sv('phone')}</button></div>` : ''
  const items = o.its.map(([p, sp, q]) => `<div class="fl-orow"><img src="${prod(p)}" alt=""><div class="fl-t"><h4>${PRODUCTS[p].n}</h4><div class="fl-meta">${sp} × ${q}</div></div>${money((PRODUCTS[p].sizes.find((z) => z[0] === sp) || PRODUCTS[p].sizes[0])[1] * q)}</div>`).join('')
  const info = [['订单编号', o.id], ['下单时间', '2026-' + o.at], ['支付方式', o.st === 'pay' || o.st === 'cancel' ? '—' : '微信支付'], ['送达时间', o.slot]].concat(o.card ? [['贺卡内容', o.card]] : [])
  return `<div class="fl-ost fl-${o.st}"><h2>${stn}</h2><p>${sd}</p></div>${C('MP-ORD-010', steps)}${C('MP-ORD-011', rider)}
   <div class="fl-card fl-addr fl-static">${sv('pin', 'i')}<div><h4>${A.n} ${A.ph}</h4><p>${A.a}</p></div></div>
   <div class="fl-card">${items}</div>
   <div class="fl-card fl-sum"><div><span>商品金额</span><b>¥${tot}</b></div><div><span>配送费</span><b>${o.ship ? '¥' + o.ship : '免费'}</b></div><div class="fl-t"><span>${o.st === 'pay' ? '应付金额' : '实付金额'}</span>${money(pay)}</div></div>
   <div class="fl-card fl-kvs">${info.map(([k, v]) => `<div><span>${k}</span><b>${v}</b></div>`).join('')}</div>`
}
pages.orderBar = (f) => fbar(oActs(orderBy(f.a)))

/* ---------- 申请售后（用库的售后申请表） ---------- */
pages.service = (f) => {
  const o = orderBy(f.a), p = o.its[0][0], sp = o.its[0][1]
  const ov = {
    text: { '.pd .nm': PRODUCTS[p].n, '.pd .sp2': `${sp} × ${o.its[0][2]}`, '.ty@0 b': '仅退款', '.ty@0 span': '花材有损坏或未送达', '.ty@1 b': '重新补发', '.ty@1 span': '门店重新包扎并配送', '.menu [data-o]@0': '花材枯萎或有损坏', '.menu [data-o]@1': '包装破损', '.menu [data-o]@2': '与商品描述不符', '.menu [data-o]@3': '少发或错发', '.menu [data-o]@4': '配送延误', '.menu [data-o]@5': '其他原因' },
    img: { '.pd img': p }, hide: ['.ty@2'],
  }
  return `${K.block('MP-ORD-014', ov)}<p class="fl-legal-tip">${sv('info')}签收后 24 小时内可申请；鲜花类需上传 1–3 张照片；商家将在 24 小时内处理，退款原路退回。</p>`
}

/* ---------- 评价（用库的评价提交表单） ---------- */
pages.review = (f) => {
  const o = orderBy(f.a), p = o.its[0][0]
  const ov = { text: { '.pd .nm': PRODUCTS[p].n, '.pd .sp2': o.its[0][1] }, img: { '.pd img': p }, hide: ['[data-tags] button@5'] }
  ;['花朵新鲜', '包装精美', '送达准时', '贺卡好看', '配送员服务好'].forEach((t, i) => { ov.text[`[data-tags] button@${i}`] = t })
  ov.text['.mini>div@0 span'] = '配送服务'; ov.attrs = { textarea: { placeholder: '花的新鲜度、包装与配送体验如何？' } }
  return K.block('MP-ORD-015', ov)
}

/* ---------- 收货地址 ---------- */
const addrRows = (choose) => C('MP-ORD-004', ADDRS.map((x, i) => `<div class="fl-card fl-arow ${choose && S.co.addr === i ? 'fl-sel' : ''}"><button type="button" class="fl-main" ${choose ? `data-pt-act="addrPick:${i}"` : `data-pt-go="addredit:${i}"`}><h4>${x.n} <span>${x.ph}</span>${x.def ? '<span class="tg tg-soft">默认</span>' : ''}${x.tag ? `<span class="tg tg-soft">${x.tag}</span>` : ''}</h4><p>${x.a}</p></button>${choose ? `<button type="button" class="fl-ed" data-pt-go="addredit:${i}" aria-label="编辑">${sv('edit')}</button>` : ''}</div>`).join(''))
pages.address = () => addrRows(false)
pages['address-pick'] = () => addrRows(true)
pages.addressBar = () => fbar(`<button type="button" class="btn btn-p fl-wide" data-pt-go="addredit:new" data-pt-primary>${sv('plus')}新增地址</button>`)

/* ---------- 编辑地址（用库的地址表单） ---------- */
pages.addredit = (f) => {
  const a = f.a, x = a === 'new' || a === '' ? { n: '', ph: '', a: '', tag: '家', def: false } : ADDRS[+a]
  const ov = {
    attrs: { '[data-k=name] input': { value: x.n }, '[data-k=tel] input': { value: x.ph.replace(/\*+/g, '0000'), placeholder: '收花人手机号，仅用于配送联系' }, '[data-k=addr] textarea': { placeholder: '街道、楼栋、门牌号' } },
    text: { '.rg .v': '北京市 朝阳区', '[data-k=addr] textarea': x.a },
    act: { '.go': 'saveAddr' },
  }
  return `${K.block('MP-FORM-005', ov)}<p class="fl-legal-tip">${sv('info')}姓名与手机号仅用于本次配送联系，配送完成后不再向骑手展示。</p>`
}
pages.addreditBar = (f) => (f.a === 'new' || f.a === '' ? '' : fbar(`<button type="button" class="btn btn-s fl-wide" data-pt-say="已删除该地址（示例，演示数据不变）">删除地址</button>`))

/* ---------- 我的优惠券 ---------- */
pages.couponsTabs = (f) => C('MP-NAV-003', `<div class="fl-utabs">${[['ok', '可使用'], ['used', '已使用'], ['exp', '已过期']].map(([k, n]) => `<button type="button" class="${(f.a || 'fl-ok') === k ? 'fl-on' : ''}" data-pt-act="cpTab:${k}">${n}</button>`).join('')}</div>`)
pages.coupons = (f) => {
  const tab = f.a || 'ok', list = tab === 'ok' ? COUPONS : []
  const tick = (c) => `<div class="fl-tick"><div class="fl-amt"><small>¥</small><b>${c.amt}</b><span>满 ${c.min} 可用</span></div><div class="fl-inf"><h4>${c.n}</h4><p>${c.cat}</p><p>${c.e}</p></div><button type="button" class="btn btn-p btn-sm" data-pt-go="list:当季热卖">去使用</button></div>`
  return list.length ? C('MP-MKT-001', list.map(tick).join('')) : empty('coupon', '暂无优惠券', tab === 'used' ? '用过的券会显示在这里' : '过期的券会显示在这里', '', 'MP-MKT-001')
}
pages.favs = () => {
  const ids = PRODUCTS.map((p, i) => i).filter((i) => S.fav[i])
  return ids.length ? C('MP-CARD-001', `<div class="fl-grid2" style="margin-top:2px">${ids.map(pcard).join('')}</div>`) : empty('heart', '还没有收藏', '点商品上的心形，就能在这里找到它', `<button class="btn btn-p" type="button" data-pt-go="list:当季热卖">去逛逛</button>`, 'MP-CARD-001')
}
pages.member = () => {
  const m = D.member
  return `${C('MP-CARD-009', `<div class="fl-mcard fl-flat"><div class="fl-r1"><b>${m.level}</b><span>成长值 ${m.growth} / ${m.target.toLocaleString('en-US')}</span></div><div class="fl-prog"><i style="width:${Math.round(m.growth / m.target * 100)}%"></i></div><div class="fl-r2">再获 ${(m.target - m.growth).toLocaleString('en-US')} 成长值升级${m.next}</div></div>`)}
  <div class="fl-card"><div class="fl-oh"><h4>会员权益</h4></div><div class="fl-eq">${[['giftcard', '生日礼券'], ['scooter', '每月免配送'], ['star', '积分双倍日'], ['coupon', '会员专享券']].map(([n, t]) => `<div>${tileHTML(n, K.cfg.iconTile)}<span>${t}</span></div>`).join('')}</div></div>
  <div class="fl-card"><div class="fl-oh"><h4>每日签到</h4><span class="fl-meta">连续 3 天，第 7 天得 20 积分</span></div><div class="fl-sign">${[1, 2, 3, 4, 5, 6, 7].map((d) => `<div class="${d <= 3 ? 'fl-on' : ''}">${d <= 3 ? sv('check') : '+' + (d === 7 ? 20 : 5)}<em>第${d}天</em></div>`).join('')}</div></div>
  <div class="fl-card"><div class="fl-oh"><h4>积分明细</h4><span class="fl-meta">可用 ${m.points.toLocaleString('en-US')}</span></div><div class="fl-kvs">${[['订单获得', '+168'], ['每日签到', '+5'], ['订单抵扣', '-500']].map(([k, v]) => `<div><span>${k}</span><b>${v}</b></div>`).join('')}</div></div>`
}
pages.settings = () => {
  const sw = (k, t, d) => `<div class="fl-cell"><span>${t}${d ? `<small>${d}</small>` : ''}</span><button type="button" class="fl-tgl ${S.sw[k] ? 'fl-on' : ''}" data-pt-act="sw:${k}" role="switch" aria-checked="${S.sw[k]}"></button></div>`
  return `${C('MP-FORM-010', `<div class="fl-cells">${sw('sub1', '配送进度通知', '下单、接单、配送、送达时提醒')}${sw('sub2', '活动与优惠通知')}</div>
   <div class="fl-cells">${sw('pers', '个性化推荐', '关闭后仍可浏览，推荐内容不再按偏好排序')}<button type="button" class="fl-cell" data-pt-say="已撤回授权（示例）">${sv('shield', 'i')}<span>撤回位置与手机号授权</span>${sv('chev', 'chev')}</button></div>`)}
   ${C('MP-ENT-010', `<div class="fl-cells">${cell('file', '用户协议', '', 'legal:用户协议')}${cell('shield', '隐私政策', '', 'legal:隐私政策')}${cell('receipt', '购买须知', '', 'legal:购买须知')}${cell('chat', '联系客服', '', 'help')}</div>
   <div class="fl-cells"><button type="button" class="fl-cell fl-danger" data-pt-say="注销需先完成未结订单">${sv('trash', 'i')}<span>注销账号</span></button></div>`)}<p class="fl-end">花间集 v1.0.3</p>`
}
pages.legal = (f) => `<div class="fl-card fl-doc"><h3>${esc(f.a || '购买须知')}</h3>${(LEGAL[f.a] || LEGAL['购买须知']).map((t) => `<p>${t}</p>`).join('')}</div>`
pages.help = () => `${C('MP-ENT-010', `<div class="fl-cells"><button type="button" class="fl-cell" data-pt-say="正在接入在线客服（示例）">${sv('chat', 'i')}<span>在线客服<small>9:00–21:00，平均 2 分钟内回复</small></span>${sv('chev', 'chev')}</button><button type="button" class="fl-cell" data-pt-say="将拨打 400 客服电话（示例）">${sv('phone', 'i')}<span>电话客服<small>400-000-0000（示例号码）</small></span>${sv('chev', 'chev')}</button></div>`)}
  ${C('MP-ENT-010', `<div class="fl-card"><div class="fl-oh"><h4>常见问题</h4></div><div class="fl-faq">${FAQ.map((q) => `<button type="button" data-pt-say="${q}（示例）"><span>${q}</span>${sv('chev', 'chev')}</button>`).join('')}</div></div>`)}`

/* ---------- 弹层（正文；标题、关闭、遮罩由模板给） ---------- */
pages['sheet-spec'] = () => {
  const s = S.spec, p = PRODUCTS[s.p], price = priceOf(s.p, s.si, s.pk)
  const sz = p.sizes.map(([n], i) => `<button type="button" class="${s.si === i ? 'fl-on' : ''} ${p.soldout === i ? 'fl-no' : ''}" ${p.soldout === i ? 'disabled' : `data-pt-act="specSet:si:${i}"`}>${n}${p.soldout === i ? ' 售罄' : ''}</button>`).join('')
  const pk = PACKS.map(([n, pr], i) => `<button type="button" class="${s.pk === i ? 'fl-on' : ''}" data-pt-act="specSet:pk:${i}">${n}${pr ? ` +¥${pr}` : ''}</button>`).join('')
  return `<div class="fl-sbp">${C('MP-GOODS-003', `<div class="fl-sp-top"><img src="${prod(s.p)}" alt=""><div>${money(price)}<p>已选：${p.sizes[s.si][0]} · ${PACKS[s.pk][0]}</p></div></div><h4 class="fl-gt0">规格</h4><div class="fl-chips2">${sz}</div><h4 class="fl-gt0">包装</h4><div class="fl-chips2">${pk}</div><div class="fl-row2"><span>数量</span><div class="fl-qty"><button type="button" data-pt-act="specQty:-1" aria-label="减少">${sv('minus')}</button><b>${s.q}</b><button type="button" data-pt-act="specQty:1" aria-label="增加">${sv('plus')}</button></div></div>`)}</div>`
}
pages.specBar = () => {
  const lab = S.spec.mode === 'buy' ? '立即购买' : S.spec.mode === 'pick' ? '确定' : '加入购物车'
  return `<button type="button" class="btn btn-p fl-wide" data-pt-act="specConfirm" data-pt-primary>${lab}</button>`
}
pages['sheet-time'] = () => {
  const pk = S.co.mode === 'pickup'
  const days = DAYS.map(([d, dt], i) => `<button type="button" class="${S.dayTmp === i ? 'fl-on' : ''}" data-pt-act="day:${i}"><b>${d}</b><span>${dt}</span></button>`).join('')
  const slots = SLOTS.map((t, i) => { const st = SLOT_STATE[S.dayTmp][i]; return `<button type="button" class="${S.slotTmp === i && st === 0 ? 'fl-on' : ''}" ${st ? 'disabled' : `data-pt-act="slot:${i}"`}><span>${t}</span><em>${st === 1 ? '已约满' : st === 2 ? '已截单' : S.slotTmp === i ? '已选' : ''}</em></button>` }).join('')
  return `<div class="fl-sbp">${C('MP-ORD-005', `<div class="fl-days">${days}</div><div class="fl-slots">${slots}</div>`)}<p class="fl-meta">${pk ? '备花约 1 小时，到店出示订单即可取花' : '今日 17:00 前下单；配送时段需至少提前 2 小时预约，高峰日会提前通知'}</p></div>`
}
pages.timeBar = () => `<button type="button" class="btn btn-p fl-wide" data-pt-act="slotOk" data-pt-primary>确定</button>`
pages['sheet-coupon'] = () => {
  const c = coCalc()
  const row = (x) => { const ok = couponOk(x, c.sub, c.items); return `<button type="button" class="fl-tick fl-small ${S.cpTmp === x.id ? 'fl-sel' : ''} ${ok ? '' : 'fl-dis'}" ${ok ? `data-pt-act="cpPick:${x.id}"` : 'disabled'}><div class="fl-amt"><small>¥</small><b>${x.amt}</b><span>满 ${x.min}</span></div><div class="fl-inf"><h4>${x.n}</h4><p>${ok ? x.e : x.min > c.sub ? `还差 ¥${x.min - c.sub} 可用` : x.cat}</p></div><i class="fl-rad"></i></button>` }
  return `<div class="fl-sbp">${C('MP-ORD-007', `${COUPONS.map(row).join('')}<button type="button" class="fl-none ${S.cpTmp === -1 ? 'fl-on' : ''}" data-pt-act="cpPick:-1"><span>不使用优惠券</span><i class="fl-rad"></i></button>`)}</div>`
}
pages.couponBar = () => `<button type="button" class="btn btn-p fl-wide" data-pt-act="cpOk" data-pt-primary>确定</button>`
pages['sheet-pay'] = (f) => {
  const o = orderBy(f.a || S.co.oid), amt = o.pay || orderTotal(o) + o.ship
  return `<div class="fl-sbp">${C('MP-ORD-008', `<div class="fl-payamt">${money(amt)}<p>订单剩余支付时间 29:58</p></div><div class="fl-cells fl-flat"><div class="fl-cell">${sv('wallet2', 'i')}<span>微信支付</span><i class="fl-rad fl-on"></i></div></div>`)}<p class="fl-meta">支付前请再次确认收货地址与送达时间。退款将原路退回。</p></div>`
}
pages.payBar = (f) => {
  const o = orderBy(f.a || S.co.oid), amt = o.pay || orderTotal(o) + o.ship
  return `<button type="button" class="btn btn-p fl-wide" data-pt-act="pay" data-pt-primary>确认支付 ¥${amt}</button>`
}
pages['sheet-cancel'] = (f) => `<p class="pt-confirm">取消后订单将关闭，已使用的优惠券与积分会退回；备货前取消全额退款。确定取消吗？</p>`
pages.cancelBar = (f) => `<div class="pt-confirm-row"><button type="button" data-pt-close>再想想</button><button type="button" class='danger' data-pt-act="cancelOk:${f.a}">确认取消</button></div>`

/* ---------- 动作 ---------- */
const acts = {
  claim() { K.setScene('newc', 'got'); K.toast('已领取，可在“我的·优惠券”查看') },
  fav(p) { S.fav[p] = S.fav[p] ? 0 : 1; K.render(); K.toast(S.fav[p] ? '已收藏' : '已取消收藏') },
  hotpill(i) { S.hotPill = +i; K.render() },
  cate(i) { S.cate = +i; S.chip = 0; K.render() },
  chip(i) { S.chip = +i; K.render() },
  sort(i) { S.sortBy = +i; K.render() },
  cartToggle(i) { S.cart[i].on = !S.cart[i].on; K.render() },
  cartAll() { const all = S.cart.filter((c) => !c.bad).every((c) => c.on); S.cart.forEach((c) => { if (!c.bad) c.on = !all }); K.render() },
  qty(i, d) { const c = S.cart[i]; c.q = Math.max(1, Math.min(9, c.q + +d)); K.render() },
  cartDel(i) { S.cart.splice(+i, 1); K.render(); K.toast('已删除') },
  cartClear() { S.cart = S.cart.filter((c) => !c.bad); K.render() },
  specSet(k, v) { S.spec[k] = +v; K.render() },
  specQty(d) { S.spec.q = Math.max(1, Math.min(9, S.spec.q + +d)); K.render() },
  specConfirm() {
    const s = S.spec
    if (s.mode === 'pick') { K.closeSheet(); return }
    if (s.mode === 'buy') { S.buy = { p: s.p, si: s.si, pk: s.pk, q: s.q }; S.co.coupon = -2; K.closeSheet(); K.go('checkout'); return }
    const f = S.cart.find((c) => c.p === s.p && c.si === s.si && c.pk === s.pk)
    if (f) f.q = Math.min(9, f.q + s.q); else S.cart.push({ p: s.p, si: s.si, pk: s.pk, q: s.q, on: true })
    if (K.scene('cart') === 'empty') K.setScene('cart', 'full')
    K.closeSheet(); K.toast('已加入购物车')
  },
  checkout() {
    if (!cartPicked().length) { K.toast('请先勾选商品', 'warn'); return }
    S.buy = null; S.co.coupon = -2; K.go('checkout')
  },
  mode(m) { S.co.mode = m; if (m === 'pickup') { S.co.slot = 4; S.co.day = 0 } K.render() },
  card(v) { S.co.card = v },
  points() { S.co.points = !S.co.points; K.render() },
  anon() { S.co.anon = !S.co.anon; K.render() },
  day(i) { S.dayTmp = +i; K.render() },
  slot(i) { S.slotTmp = +i; K.render() },
  slotOk() { S.co.day = S.dayTmp; S.co.slot = S.slotTmp; K.closeSheet() },
  cpPick(i) { S.cpTmp = +i; K.render() },
  cpOk() { S.co.coupon = S.cpTmp; K.closeSheet() },
  addrPick(i) { S.co.addr = +i; K.back() },
  storePick(i) { S.co.store = +i; K.back() },
  submit() {
    const c = coCalc()
    if (S.co.mode === 'deliver' && K.scene('range') === 'out') { K.toast('超出门店配送范围，请改选自提或更换地址', 'warn'); return }
    if (c.low) { K.toast('未达起送价 ¥68', 'warn'); return }
    const o = { id: 'HJ' + (2026110400200 + S.orders.length), st: 'pay', its: c.items.map((i) => [i.p, PRODUCTS[i.p].sizes[i.si][0], i.q]), ship: c.fee, slot: slotText(), addr: S.co.addr, card: S.co.card, at: '11-04 14:08', pay: c.pay }
    S.orders.unshift(o); S.co.oid = o.id; S.payFrom = 'checkout'; K.openSheet('sheet-pay', o.id)
  },
  pay() {
    const o = orderBy(K.S.sheet ? K.S.sheet.a : S.co.oid), cur = K.cur().id, sc = K.scene('pay')
    S.co.oid = o.id
    if (cur === 'checkout') S.payFrom = 'checkout'; else if (cur !== 'result-fail') S.payFrom = 'orders'
    K.closeSheet()
    const open = (id, a) => (cur === 'checkout' || cur === 'result-fail' || cur === 'result' ? K.replace(id, a) : K.go(id, a))
    if (sc === 'ok') { o.st = 'make'; if (!S.buy && S.payFrom === 'checkout') S.cart = S.cart.filter((c) => !(c.on && !c.bad)); open('result', o.id) }
    else if (sc === 'processing') open('result', o.id + ':wait')
    else open('result-fail', o.id)
  },
  finish() { if (S.payFrom === 'orders') K.back(); else K.done('buy') },
  ordTab(t) { K.replace('orders', t) },
  cancelAsk(id) { K.openSheet('sheet-cancel', id) },
  cancelOk(id) { orderBy(id).st = 'cancel'; K.closeSheet(); K.toast('订单已取消') },
  recv(id) { orderBy(id).st = 'done'; K.render(); K.toast('已确认收货') },
  again(id) { orderBy(id).its.forEach(([p, sp, q]) => { const si = Math.max(0, PRODUCTS[p].sizes.findIndex((z) => z[0] === sp)); const f = S.cart.find((c) => c.p === p && c.si === si && c.pk === 0); if (f) f.q = Math.min(9, f.q + q); else S.cart.push({ p, si, pk: 0, q, on: true }) }); K.render(); K.toast('已加入购物车，可在购物车结算') },
  stype(i) { S.stype = +i; K.render() },
  sreason(i) { S.sreason = +i; K.render() },
  svcOk(id) { orderBy(id).st = 'refund'; K.back(); K.toast('已提交，商家将在 24 小时内处理') },
  rvOk(id) { orderBy(id).st = 'finished'; K.back(); K.toast('评价已提交') },
  cpTab(t) { K.replace('coupons', t) },
  setDef(i) { ADDRS.forEach((a, k) => { a.def = k === +i }); K.render() },
  saveAddr() { K.toast('地址已保存'); K.back() },
  sw(k) { S.sw[k] = !S.sw[k]; K.render() },
  kw(v) { S.kw = v },
  hist(v) { S.kw = v; K.go('list', v) },
  searchEnter(v) { S.kw = v; K.go('list', v || '热销') },
}

/* ---------- 钩子：弹层打开时初始化它的临时状态；渲染后滚动分类栏；售后与评价表单的提交 ---------- */
K.on('sheet', (sh) => {
  if (!sh || !S) return
  if (sh.id === 'sheet-spec') { const [p, mode] = sh.a.split(':'); S.spec = { p: +p || 0, si: 0, pk: 0, q: 1, mode: mode || 'cart' } }
  else if (sh.id === 'sheet-time') { S.dayTmp = S.co.day; S.slotTmp = S.co.slot }
  else if (sh.id === 'sheet-coupon') { coCalc(); S.cpTmp = S.co.coupon }
  else if (sh.id === 'sheet-pay') { ensureCheckout(); S.co.oid = sh.a || S.co.oid || S.orders[0].id }
})
K.on('render', (c) => {
  if (c.id === 'cat') { const r = document.getElementById('flRail'), on = r && r.querySelector('.fl-on'); if (r && on) r.scrollTop = Math.max(0, on.offsetTop - 120) }
})
document.addEventListener('click', (e) => {
  const b = e.target.closest('.mpord014 [data-submit], .mpord015 [data-submit]')
  if (!b || b.getAttribute('aria-disabled') === 'true' || !S) return
  const id = K.cur().a
  if (b.closest('.mpord014')) setTimeout(() => { if (K.cur().id === 'service') acts.svcOk(id) }, 700)
  else setTimeout(() => { if (K.cur().id === 'review') acts.rvOk(id) }, 700)
})

K.content({ init, pages, acts })
