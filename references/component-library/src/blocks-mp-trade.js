/* ===== 小程序 · 商品详情 GOODS 与 购物车与订单 ORD =====
 * 编号：MP-GOODS-001 起（商品详情）、MP-ORD-001 起（购物车与订单）。整个文件包在一个函数里，避免和别的文件抢全局名字。
 * 内部类名避开页面与基础库已占用的名字（st sl sw seg tab tabs chs lk bar tl ttl fit mt cn price tg btn tile ico 等）。 */
;(() => {
const $ = (r, s) => r.querySelector(s)
const $$ = (r, s) => [...r.querySelectorAll(s)]
const tap = (root, sel, fn) => root.addEventListener('click', (e) => { const m = e.target.closest(sel); if (m && root.contains(m)) fn(m, e) })
const tapAfter = (root, sel, fn) => tap(root, sel, (m, e) => setTimeout(() => fn(m, e), 0)) /* 等 ix.js 处理完状态再读 */
const tt = (root, msg) => IX.toast(root, msg)
const yuan = (n) => (Math.round(n * 100) / 100).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const stars = (n, cls = '') => `<span class="stars ${cls}" aria-label="${n} 星">${[1, 2, 3, 4, 5].map((i) => `<i class="${i <= n ? 'f' : ''}">${sv(i <= n ? 'starf' : 'star')}</i>`).join('')}</span>`
const crops = [[1, 50, 50], [1.7, 22, 28], [2.2, 72, 66], [1.5, 50, 82], [1.35, 82, 18]] /* 同一张商品图的不同裁切，模拟多角度图 */
const cimg = (c, i = 0) => `<img src="${P(i)}" alt="" draggable="false" style="transform:scale(${c[0]});transform-origin:${c[1]}% ${c[2]}%">`

Object.assign(LINE, {
  mt_store: '<path d="M4.5 9.5 5.5 4h13l1 5.5"/><path d="M4.5 9.5a2.7 2.7 0 0 0 5.2 0 2.7 2.7 0 0 0 4.6 0 2.7 2.7 0 0 0 5.2 0"/><path d="M5.5 12.5V20h13v-7.5M10 20v-4.5h4V20"/>',
  mt_headset: '<path d="M4.5 14v-2a7.5 7.5 0 0 1 15 0v2"/><rect x="3.5" y="13" width="4" height="6" rx="1.5"/><rect x="16.5" y="13" width="4" height="6" rx="1.5"/><path d="M18.5 19v.5a2 2 0 0 1-2 2H13"/>',
  mt_return: '<path d="M9 6 4.5 10.5 9 15"/><path d="M4.5 10.5H15a4.5 4.5 0 0 1 0 9h-4"/>',
  mt_thumb: '<path d="M7.5 10.5V20h-3v-9.5z"/><path d="m7.5 10.5 3.5-6.5c1.6 0 2.6 1.1 2.3 2.8L12.8 9.5h5.7a2 2 0 0 1 2 2.4l-1.2 6a2 2 0 0 1-2 1.6H7.5"/>',
  mt_help: '<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.6a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1.1.9-1.1 1.7M12 16.6v.4"/>',
  mt_card: '<rect x="3.5" y="6" width="17" height="12" rx="2.5"/><path d="M3.5 10h17M7 14.5h3"/>',
  mt_bubbles: '<path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h5A2.5 2.5 0 0 1 14 6.5v2a2.5 2.5 0 0 1-2.5 2.5H9L6.5 13v-2A2.5 2.5 0 0 1 4 8.5z"/><path d="M10 14.5v1a2.5 2.5 0 0 0 2.5 2.5H15l2.5 2v-2a2.5 2.5 0 0 0 2.5-2.5v-2a2.5 2.5 0 0 0-2.5-2.5H16"/>',
  mt_yen: '<circle cx="12" cy="12" r="8.5"/><path d="M8.5 8.5 12 12l3.5-3.5M8.5 12h7M8.5 15h7M12 12v5"/>',
  mt_coin: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5v9M9.5 10h3.5a1.8 1.8 0 0 1 0 3.6H9.5"/>',
})

/* def 的本地包装：价格一律不换行（flex 里被挤压时会把“¥”与数字拆成两行）*/
const defx = (o) => {
  const m = /^MP-([A-Z]+)-(\d{3})$/.exec(o.id), c = 'mp' + m[1].toLowerCase() + m[2]
  def({ ...o, css: o.css + `
.${c} .price{white-space:nowrap}` })
}

/* 共用样式片段（按块前缀 c 生成，写出来的选择器都以 .c 开头）*/
const CK = (c) => `.${c} .ck{position:relative;width:22px;height:22px;border-radius:50%;border:1.5px solid var(--n9);background:var(--card);flex:none;transition:background .15s,border-color .15s}.${c} .ck::after{content:"";position:absolute;inset:-11px}.${c} .ck.on,.${c} .ck.part{background:var(--p);border-color:var(--p)}.${c} .ck.on::before{content:"";position:absolute;left:6px;top:2.5px;width:5px;height:9.5px;border:solid var(--card);border-width:0 2px 2px 0;transform:rotate(45deg)}.${c} .ck.part::before{content:"";position:absolute;left:4.5px;top:8.5px;width:10px;height:2px;border-radius:1px;background:var(--card)}.${c} .ck.dis{background:var(--soft);border-color:var(--n6);pointer-events:none}`
const STP = (c) => `.${c} .stp{display:inline-flex;align-items:center;height:28px;border-radius:8px;background:var(--n3);flex:none}.${c} .stp button{position:relative;width:28px;height:28px;display:flex;align-items:center;justify-content:center;color:var(--ink)}.${c} .stp button svg{width:14px;height:14px}.${c} .stp button::after{content:"";position:absolute;inset:-8px -2px}.${c} .stp button.dis{color:var(--ink7)}.${c} .stp b{min-width:28px;text-align:center;font-size:14px;font-weight:600;font-variant-numeric:tabular-nums}`
const STARS = (c) => `.${c} .stars{display:inline-flex;gap:2px}.${c} .stars i{width:14px;height:14px;color:var(--off);display:block}.${c} .stars i.f{color:#C9A15A}`
const LD = (c) => `.${c} .spin{width:18px;height:18px;border-radius:50%;border:2.5px solid rgba(255,255,255,.4);border-top-color:var(--card);animation:${c}s .8s linear infinite}@keyframes ${c}s{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){.${c} .spin{animation:none}}`
const SMALL_BTN = (c) => `.${c} .btn-sm{position:relative;padding:0 14px}.${c} .btn-sm::after{content:"";position:absolute;inset:-6px -2px}.${c} .btn.line{background:var(--card);color:var(--ink2);box-shadow:inset 0 0 0 1px var(--n7)}.${c} .btn[aria-disabled=true]{background:var(--n6);color:var(--ink5);box-shadow:none}`

/* ================= 商品详情 GOODS ================= */

guide('mp', 'GOODS', [
  ['商品详情页首屏', '商品图画廊 + 价格与促销区', '图在上、价在下，先看图再看价；页码和缩略图让用户知道还有几张'],
  ['多规格商品（颜色 / 版本 / 尺码）', '规格选择面板', '多维度联动，缺货的组合直接置灰，价格库存随选项变，避免点到最后才提示没货'],
  ['想让用户相信口碑', '评价摘要卡 → 评价列表', '先给评分和好评率，再让用户按“有图 / 追评 / 差评”自己筛，差评不要藏'],
  ['往下滑的长内容与发货售后', '详情分段标签 + 参数表 + 配送与服务条', '图文、参数、售后分段切换，常用参数放前面；送到哪、何时到、能不能退放价格下面一屏内看完'],
  ['底部购买栏：普通商品', '购买栏·图标双按钮', '店铺、客服、购物车在左，加购与购买并排，是最稳的标配'],
  ['底部购买栏：爆款 / 预约 / 缺货', '购买栏·通栏单键', '一个大按钮随状态变化：购买、到货通知、预约抢购，不让用户点到不可用的按钮'],
  ['底部购买栏：重客服、重收藏的品类', '购买栏·悬浮胶囊', '客服与收藏做成轻图标，悬浮感更强，适合高客单价和需要咨询的商品'],
])

/* ---- 001 商品图画廊 ---- */
defx({
  id: 'MP-GOODS-001', name: '商品图画廊', style: '页码+缩略图',
  fit: '商品详情页首屏：左右滑看大图，页码与缩略图联动，可按“主图 / 细节 / 买家秀”快速跳转',
  avoid: '只有一张图的商品（去掉页码和缩略图）；图片比例不一致时先统一裁成 1:1，否则轮播会跳高度',
  kw: 'gallery 商品图 轮播 画廊 主图 缩略图 页码 详情页 swipe carousel',
  css: `.mpgoods001{width:358px;max-width:100%}
.mpgoods001 .vw{position:relative;border-radius:16px;overflow:hidden;background:var(--ph);box-shadow:0 4px 16px var(--sh06)}
.mpgoods001 .ix-track{gap:0}
.mpgoods001 .slide{width:100%;aspect-ratio:1/1;overflow:hidden;background:var(--ph)}
.mpgoods001 .slide img,.mpgoods001 .thb img{width:100%;height:100%;object-fit:cover;-webkit-user-drag:none;user-select:none}
.mpgoods001 .cnt{position:absolute;right:12px;bottom:12px;height:24px;padding:0 10px;border-radius:12px;background:var(--mask2);color:#fff;font-size:12px;display:flex;align-items:center;font-variant-numeric:tabular-nums}
.mpgoods001 .cnt b{font-weight:600}
.mpgoods001 .kd{position:absolute;left:12px;top:12px;display:flex;padding:3px;border-radius:12px;background:var(--glass2);box-shadow:0 2px 8px var(--sh10)}
.mpgoods001 .kd button{position:relative;height:24px;padding:0 10px;border-radius:8px;font-size:12px;color:var(--ink2);transition:background .2s,color .2s}
.mpgoods001 .kd button::after{content:"";position:absolute;inset:-10px 0}
.mpgoods001 .kd button.on{background:var(--pt);color:var(--p-text);font-weight:600}
.mpgoods001 .thr{display:flex;gap:8px;margin-top:10px}
.mpgoods001 .thb{position:relative;flex:1;max-width:64px;aspect-ratio:1/1;border-radius:8px;overflow:hidden;opacity:.55;transition:opacity .2s}
.mpgoods001 .thb::after{content:"";position:absolute;inset:0;border-radius:8px;box-shadow:inset 0 0 0 2px var(--p);opacity:0;transition:opacity .2s}
.mpgoods001 .thb.on{opacity:1}.mpgoods001 .thb.on::after{opacity:1}`,
  html: () => `<div class="mpgoods001" data-ix="carousel"><div class="vw"><div class="ix-track">${crops.map((c) => `<div class="slide">${cimg(c)}</div>`).join('')}</div><div class="kd"><button type="button" class="on" data-from="0" data-to="1">主图</button><button type="button" data-from="2" data-to="3">细节</button><button type="button" data-from="4" data-to="4">买家秀</button></div><span class="cnt"><b>1</b>/${crops.length}</span></div><div class="thr">${crops.map((c, i) => `<button type="button" class="thb ${i ? '' : 'on'}" aria-label="第 ${i + 1} 张">${cimg(c)}</button>`).join('')}</div></div>`,
  js: (root) => {
    const tr = $(root, '.ix-track'), cnt = $(root, '.cnt b'), ths = $$(root, '.thb'), kd = $$(root, '.kd button')
    const idx = () => Math.max(0, Math.min(ths.length - 1, Math.round(tr.scrollLeft / tr.clientWidth)))
    const sync = () => { const i = idx(); cnt.textContent = i + 1; ths.forEach((t, k) => t.classList.toggle('on', k === i)); kd.forEach((b) => b.classList.toggle('on', i >= +b.dataset.from && i <= +b.dataset.to)) }
    const go = (i) => tr.scrollTo({ left: i * tr.clientWidth, behavior: 'smooth' })
    tr.addEventListener('scroll', sync)
    ths.forEach((t, k) => t.addEventListener('click', () => go(k)))
    kd.forEach((b) => b.addEventListener('click', () => go(+b.dataset.from)))
    sync()
  },
})

/* ---- 002 价格与促销区 ---- */
defx({
  id: 'MP-GOODS-002', name: '价格与促销区', style: '限时+领券',
  fit: '商品标题下方的价格区：现价、划线价、限时倒计时、领券与满减；领券后“券后价”实时变化',
  avoid: '促销信息超过三行时先合并（满减、赠品、换购并成“促销”一行展开）；不要把券、满减、积分都做成醒目色块',
  kw: 'price promotion 价格 促销 领券 满减 倒计时 券后价 标题 限时直降',
  css: `.mpgoods002{width:358px;max-width:100%;border-radius:16px;overflow:hidden;background:var(--card);box-shadow:0 4px 16px var(--sh06)}
.mpgoods002 .band{padding:14px 16px 12px;background:linear-gradient(180deg,var(--pt),var(--card))}
.mpgoods002 .top{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;font-size:12px;color:var(--ink2)}
.mpgoods002 .top .lab{display:inline-flex;align-items:center;gap:4px;font-weight:600;color:var(--p-text)}
.mpgoods002 .top .lab svg{width:14px;height:14px}
.mpgoods002 .cd{display:inline-flex;align-items:center;gap:3px;font-weight:600;color:var(--ink2)}
.mpgoods002 .cd i{min-width:22px;height:22px;padding:0 3px;border-radius:4px;background:var(--pd);color:#fff;font-size:12px;display:inline-flex;align-items:center;justify-content:center;font-variant-numeric:tabular-nums}
.mpgoods002 .pri{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
.mpgoods002 .pri .price b{font-size:32px;font-weight:700}.mpgoods002 .pri .price small{font-size:16px}
.mpgoods002 .pri .strike{margin:0}
.mpgoods002 .pri .sold{margin-left:auto;font-size:12px;color:var(--ink3)}
.mpgoods002 .aft{margin-top:6px;font-size:12px;color:var(--ink2)}.mpgoods002 .aft b{color:var(--price);font-size:14px;font-weight:600}
.mpgoods002 .body{padding:2px 16px 4px}
.mpgoods002 .nm{margin:6px 0 8px;font-size:16px;font-weight:600;line-height:24px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.mpgoods002 .nm .tg{margin-right:6px;vertical-align:2px}
.mpgoods002 .pts{display:flex;gap:6px;flex-wrap:wrap;padding-bottom:12px}
.mpgoods002 .rw{display:flex;gap:12px;padding:11px 0;border-top:1px solid var(--line);font-size:14px;line-height:22px}
.mpgoods002 .rw>em{flex:none;width:32px;color:var(--ink3);font-size:14px}
.mpgoods002 .rw>div{flex:1;min-width:0}
.mpgoods002 .cps{display:flex;gap:8px;flex-wrap:wrap}
.mpgoods002 .cp{position:relative;display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 10px 0 4px;border-radius:8px;background:var(--pt);color:var(--p-text);font-size:12px;font-weight:600;box-shadow:inset 0 0 0 1px var(--pm);transition:background .2s,color .2s}
.mpgoods002 .cp::after{content:"";position:absolute;inset:-8px -2px}
.mpgoods002 .cp .a{height:20px;padding:0 6px;border-radius:5px;background:var(--p);color:#fff;font-size:12px;display:inline-flex;align-items:center}
.mpgoods002 .cp.on{background:var(--n3);color:var(--ink3);box-shadow:inset 0 0 0 1px var(--line)}.mpgoods002 .cp.on .a{background:var(--n9)}
.mpgoods002 .pro [data-h]{display:flex;align-items:center;gap:8px;width:100%;text-align:left;min-height:22px}
.mpgoods002 .pro [data-h] span{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mpgoods002 .pro [data-h] svg{width:16px;height:16px;flex:none;color:var(--ink3);transition:transform .25s cubic-bezier(.2,0,0,1)}
.mpgoods002 .pro .ix-ai.open [data-h] svg{transform:rotate(180deg)}
.mpgoods002 .pro ul{margin:8px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px;font-size:14px;color:var(--ink2)}
.mpgoods002 .pro li{display:flex;gap:8px;align-items:flex-start}.mpgoods002 .pro li .tg{margin-top:1px;flex:none}`,
  html: () => `<div class="mpgoods002"><div class="band"><div class="top"><span class="lab">${sv('bolt')}限时直降</span><span class="cd" data-ix="count" data-sec="8130">距结束 <i data-h>02</i>:<i data-m>15</i>:<i data-s>30</i></span></div><div class="pri"><span class="price"><small>¥</small><b>599</b></span><span class="strike">¥799</span><span class="tg tg-red">直降 ¥200</span><span class="sold">已售 2,386</span></div><div class="aft">领券后最低 <b>¥549</b></div></div><div class="body"><h2 class="nm"><span class="tg tg-hot">自营</span>无线降噪耳机 主动降噪 蓝牙 5.3 超长续航 头戴式 通勤出差运动通用 石墨灰</h2><div class="pts"><span class="tg tg-soft">降噪 42dB</span><span class="tg tg-soft">续航 40h</span><span class="tg tg-soft">多点连接</span></div>
<div class="rw"><em>领券</em><div class="cps"><button type="button" class="cp" data-min="500" data-off="50" data-name="满 500 减 50 券"><i class="a">领</i>满 500 减 50</button><button type="button" class="cp" data-min="300" data-off="30" data-name="满 300 减 30 券"><i class="a">领</i>满 300 减 30</button><button type="button" class="cp" data-min="1" data-off="20" data-name="新人 20 元券"><i class="a">领</i>新人 ¥20</button></div></div>
<div class="rw pro" data-ix="acc"><em>促销</em><div class="ix-ai"><button type="button" data-h><span><i class="tg tg-red">满减</i> 2 件 9 折，3 件 8.5 折，加价购赠品</span>${sv('down')}</button><div class="ix-ab"><div><ul><li><i class="tg tg-red">满减</i>同店满 2 件 9 折，满 3 件 8.5 折</li><li><i class="tg tg-soft">赠品</i>下单即赠收纳袋，赠完即止</li><li><i class="tg tg-soft">换购</i>加 ¥29 换购原装充电线</li></ul></div></div></div></div>
<div class="rw"><em>积分</em><div>下单预计获得 599 积分，可抵 ¥6</div></div></div></div>`,
  js: (root) => {
    const price = 599, cps = $$(root, '.cp'), aft = $(root, '.aft')
    const upd = () => {
      const got = cps.filter((c) => c.classList.contains('on') && price >= +c.dataset.min).map((c) => +c.dataset.off)
      const best = got.length ? Math.max(...got) : 0
      aft.innerHTML = best ? `券后 <b>¥${price - best}</b>，已享立减 ¥${best}` : `领券后最低 <b>¥${price - 50}</b>`
    }
    tap(root, '.cp', (c) => {
      if (c.classList.contains('on')) { tt(root, '已领取，可在“我的优惠券”查看'); return }
      c.classList.add('on'); $(c, '.a').textContent = '已领'; tt(root, `已领取 ${c.dataset.name}`); upd()
    })
  },
})

/* ---- 003 规格选择面板 ---- */
const SKU = {
  colors: [['石墨灰', '#5B6169'], ['云白', '#E6E3DC'], ['雾蓝', '#8EA3B8'], ['酒红', '#9B5A5E']],
  vers: ['标准版', '降噪版', '套装版'],
  price: [[599, 699, 799], [599, 699, 799], [619, 719, 819], [619, 719, 819]],
  stock: [[128, 46, 3], [60, 0, 12], [22, 8, 0], [0, 0, 0]],
  limit: 5,
}
defx({
  id: 'MP-GOODS-003', name: '规格选择面板', style: '多维联动',
  fit: '多规格商品：颜色、版本等多个维度联动，缺货组合置灰，价格与库存随选项变化，数量不超过库存与限购',
  avoid: '规格超过三个维度时改成分步选择；只有一个维度时直接用普通单选，不需要联动',
  kw: 'sku 规格 选择 库存 联动 多规格 颜色 版本 尺码 数量',
  css: `.mpgoods003{width:358px;max-width:100%;background:var(--card);border-radius:22px 22px 16px 16px;padding:16px 16px 18px;box-shadow:0 8px 24px var(--sh10)}
.mpgoods003 .hd{display:flex;gap:12px}
.mpgoods003 .im{width:88px;height:88px;border-radius:12px;overflow:hidden;flex:none;background:var(--ph)}.mpgoods003 .im img{width:100%;height:100%;object-fit:cover}
.mpgoods003 .inf{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:flex-end;gap:3px}
.mpgoods003 .pr{display:flex;align-items:baseline;gap:4px}.mpgoods003 .pr .price b{font-size:28px;font-weight:700}.mpgoods003 .pr em{font-size:12px;color:var(--price);font-weight:600}
.mpgoods003 .stk{font-size:12px;color:var(--ink3)}.mpgoods003 .stk.low{color:var(--warn)}
.mpgoods003 .pick{font-size:14px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mpgoods003 .pick span{color:var(--ink2)}
.mpgoods003 .grp{padding-top:16px}
.mpgoods003 h4{margin:0 0 10px;font-size:14px;font-weight:600}
.mpgoods003 .opts{display:flex;flex-wrap:wrap;gap:8px}
.mpgoods003 .ch{position:relative;display:inline-flex;align-items:center;gap:6px;height:36px;padding:0 14px;border-radius:8px;background:var(--n3);color:var(--ink);font-size:14px;transition:background .15s,color .15s,box-shadow .15s}
.mpgoods003 .ch::before{content:"";position:absolute;inset:-4px}
.mpgoods003 .ch .dot{width:14px;height:14px;border-radius:50%;box-shadow:inset 0 0 0 1px var(--sh14);flex:none}
.mpgoods003 .ch.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1px var(--p)}
.mpgoods003 .ch.dis{color:var(--ink5);box-shadow:none;font-weight:400}.mpgoods003 .ch.dis .dot{opacity:.45}
.mpgoods003 .ch.dis::after{content:"缺货";font-size:12px}
.mpgoods003 .qty{display:flex;align-items:center;gap:8px;padding-top:18px}.mpgoods003 .qty h4{margin:0}.mpgoods003 .qty .lim{flex:1;font-size:12px;color:var(--ink3)}
${STP('mpgoods003')}
.mpgoods003 .ft{display:flex;gap:10px;margin-top:20px}.mpgoods003 .ft .btn{flex:1;padding:0 8px}
.mpgoods003 .btn[aria-disabled=true]{background:var(--n6);color:var(--ink5);box-shadow:none}`,
  html: () => `<div class="mpgoods003"><div class="hd"><div class="im"><img src="${P(0)}" alt=""></div><div class="inf"><div class="pr"><span class="price"><small>¥</small><b data-pr>599</b></span><em data-pt></em></div><div class="stk" data-stk>库存 128 件</div><div class="pick">已选：<span data-pick>石墨灰 / 标准版</span></div></div></div>
<div class="grp"><h4>颜色</h4><div class="opts" data-g="c">${SKU.colors.map((c, i) => `<button type="button" class="ch ${i ? '' : 'on'}" data-i="${i}"><i class="dot" style="background:${c[1]}"></i>${c[0]}</button>`).join('')}</div></div>
<div class="grp"><h4>版本</h4><div class="opts" data-g="v">${SKU.vers.map((v, i) => `<button type="button" class="ch ${i ? '' : 'on'}" data-i="${i}">${v}</button>`).join('')}</div></div>
<div class="qty"><h4>数量</h4><span class="lim" data-lim></span><div class="stp" data-ix="stepper" data-min="1" data-max="5"><button type="button" data-d="-1" class="dis" aria-label="减少">${sv('minus')}</button><b data-val>1</b><button type="button" data-d="1" aria-label="增加">${sv('plus')}</button></div></div>
<div class="ft"><button type="button" class="btn btn-s" data-add>加入购物车</button><button type="button" class="btn btn-p" data-buy>立即购买</button></div></div>`,
  js: (root) => {
    const S = { c: 0, v: 0 }, D = SKU
    const chips = { c: $$(root, '[data-g=c] .ch'), v: $$(root, '[data-g=v] .ch') }
    const stp = $(root, '.stp'), val = $(stp, '[data-val]'), ft = $$(root, '.ft .btn')
    const avail = (dim, i) => (dim === 'c' ? (S.v >= 0 ? [S.v] : [0, 1, 2]).some((v) => D.stock[i][v] > 0) : (S.c >= 0 ? [S.c] : [0, 1, 2, 3]).some((c) => D.stock[c][i] > 0))
    const render = () => {
      ;['c', 'v'].forEach((d) => chips[d].forEach((el, i) => { el.classList.toggle('on', S[d] === i); el.classList.toggle('dis', !avail(d, i)) }))
      const both = S.c >= 0 && S.v >= 0
      const combos = []
      D.stock.forEach((row, c) => row.forEach((st, v) => { if (st > 0 && (S.c < 0 || S.c === c) && (S.v < 0 || S.v === v)) combos.push(D.price[c][v]) }))
      const lo = Math.min(...combos), hi = Math.max(...combos)
      $(root, '[data-pr]').textContent = lo
      $(root, '[data-pt]').textContent = both || lo === hi ? '' : '起'
      const miss = [S.c < 0 ? '颜色' : '', S.v < 0 ? '版本' : ''].filter(Boolean)
      $(root, '[data-pick]').textContent = both ? `${D.colors[S.c][0]} / ${D.vers[S.v]}` : `请选择 ${miss.join('、')}`
      const stk = $(root, '[data-stk]'); let mx = D.limit
      if (both) { const st = D.stock[S.c][S.v]; mx = Math.min(st, D.limit); stk.textContent = st <= 5 ? `仅剩 ${st} 件，抓紧下单` : `库存 ${st} 件`; stk.classList.toggle('low', st <= 5); $(root, '[data-lim]').textContent = st > D.limit ? `每人限购 ${D.limit} 件` : '' }
      else { stk.textContent = `请选择 ${miss.join('、')} 后查看库存`; stk.classList.remove('low'); $(root, '[data-lim]').textContent = '' }
      stp.dataset.max = mx; let q = +val.textContent; if (q > mx) { q = mx; val.textContent = q }
      $$(stp, '[data-d]').forEach((b) => b.classList.toggle('dis', (+b.dataset.d < 0 && q <= 1) || (+b.dataset.d > 0 && q >= mx)))
      ft.forEach((b) => b.setAttribute('aria-disabled', !both))
    }
    tap(root, '.ch', (el) => {
      const d = el.parentNode.dataset.g, i = +el.dataset.i
      if (el.classList.contains('dis')) { tt(root, '该规格暂时缺货'); return }
      S[d] = S[d] === i ? -1 : i; render()
    })
    tap(root, '[data-d="1"]', (b) => { if (b.classList.contains('dis')) tt(root, S.c >= 0 && S.v >= 0 ? `最多可购买 ${stp.dataset.max} 件` : '请先选择规格') })
    tap(root, '[data-add],[data-buy]', (b) => {
      if (b.getAttribute('aria-disabled') === 'true') { const m = [S.c < 0 ? '颜色' : '', S.v < 0 ? '版本' : ''].filter(Boolean); tt(root, `请选择 ${m.join('、')}`); return }
      tt(root, b.hasAttribute('data-add') ? `已加入购物车 ×${val.textContent}` : '前往确认订单')
    })
    render()
  },
})

/* ---- 004 评价摘要卡 ---- */
defx({
  id: 'MP-GOODS-004', name: '评价摘要卡', style: '评分+分布',
  fit: '详情页中段的口碑概览：综合评分、好评率、星级分布与印象标签；点星级行看对应评价条数',
  avoid: '评价少于 10 条时不要展示分布条（显得单薄）；不要只展示好评标签而把差评占比藏起来',
  kw: 'review summary 评价 评分 好评率 分布 星级 印象标签 口碑 详情页',
  css: `.mpgoods004{width:358px;max-width:100%;background:var(--card);border-radius:16px;padding:16px;box-shadow:0 4px 16px var(--sh06)}
.mpgoods004 .hd{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.mpgoods004 .hd h3{margin:0;font-size:16px;font-weight:600}.mpgoods004 .hd h3 em{margin-left:6px;font-size:12px;font-weight:400;color:var(--ink3)}
.mpgoods004 .hd button{display:inline-flex;align-items:center;gap:2px;font-size:12px;color:var(--ink2);position:relative}.mpgoods004 .hd button::after{content:"";position:absolute;inset:-14px -8px}.mpgoods004 .hd button svg{width:14px;height:14px}
.mpgoods004 .sum{display:flex;gap:18px;align-items:center}
.mpgoods004 .sc{flex:none;width:92px;text-align:center}
.mpgoods004 .sc b{display:block;font-size:32px;line-height:38px;font-weight:700;font-variant-numeric:tabular-nums}
.mpgoods004 .sc small{display:block;margin-top:6px;font-size:12px;color:var(--ink3)}
${STARS('mpgoods004')}.mpgoods004 .sc .stars{margin-top:4px}
.mpgoods004 .dist{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px}
.mpgoods004 .dr{position:relative;display:flex;align-items:center;gap:8px;height:26px;padding:0 6px;margin:0 -6px;border-radius:8px;font-size:12px;color:var(--ink3);transition:background .2s}
.mpgoods004 .dr::after{content:"";position:absolute;inset:-1px -6px}
.mpgoods004 .dr .lb{flex:none;width:28px}.mpgoods004 .dr .tk{flex:1;height:6px;border-radius:3px;background:var(--n4);overflow:hidden}
.mpgoods004 .dr .tk i{display:block;height:100%;border-radius:3px;background:var(--n9);transition:background .2s}
.mpgoods004 .dr .pc{flex:none;width:36px;text-align:right;font-variant-numeric:tabular-nums}
.mpgoods004 .dr.on{background:var(--pt);color:var(--p-text);font-weight:600}.mpgoods004 .dr.on .tk i{background:var(--p)}
.mpgoods004 .im{margin:14px 0 0;font-size:14px;font-weight:600}
.mpgoods004 .tgs{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.mpgoods004 .it{position:relative;height:28px;padding:0 10px;border-radius:8px;background:var(--n3);color:var(--ink);font-size:12px;transition:background .15s,color .15s,box-shadow .15s}
.mpgoods004 .it::after{content:"";position:absolute;inset:-8px -2px}
.mpgoods004 .it em{margin-left:4px;color:var(--ink3);font-size:12px}
.mpgoods004 .it.on{background:var(--pt);color:var(--p-text);box-shadow:inset 0 0 0 1px var(--pm);font-weight:600}.mpgoods004 .it.on em{color:var(--p-text)}
.mpgoods004 .res{margin-top:14px;padding-top:12px;border-top:1px solid var(--line);font-size:12px;color:var(--ink2)}.mpgoods004 .res b{color:var(--ink);font-weight:600}`,
  html: () => {
    const rows = [[5, 83, '1,982'], [4, 12, '286'], [3, 3, '72'], [2, 1, '24'], [1, 1, '22']]
    return `<div class="mpgoods004"><div class="hd"><h3>商品评价<em>2,386 条</em></h3><button type="button" data-toast="进入全部评价">全部${sv('chev')}</button></div><div class="sum"><div class="sc"><b>4.9</b>${stars(5)}<small>好评率 98.6%</small></div><div class="dist">${rows.map((r) => `<button type="button" class="dr" data-n="${r[0]}" data-c="${r[2]}"><span class="lb">${r[0]} 星</span><span class="tk"><i style="width:${r[1]}%"></i></span><span class="pc">${r[1]}%</span></button>`).join('')}</div></div>
<p class="im">大家印象</p><div class="tgs" data-ix="multi">${[['音质好', 862], ['降噪强', 615], ['续航久', 438], ['佩戴舒适', 390], ['做工精致', 254], ['发货快', 188]].map((t, i) => `<button type="button" class="it ${i === 0 ? 'on' : ''}" data-o>${t[0]}<em>${t[1]}</em></button>`).join('')}</div><div class="res" data-res>显示 <b>全部</b> 评价，共 2,386 条</div></div>`
  },
  js: (root) => {
    const res = $(root, '[data-res]')
    const upd = () => {
      const r = $(root, '.dr.on'), tg = $$(root, '.it.on').map((t) => t.firstChild.textContent)
      const a = r ? `${r.dataset.n} 星评价 ${r.dataset.c} 条` : '全部评价，共 2,386 条'
      res.innerHTML = `显示 <b>${a}</b>${tg.length ? `，并含“${tg.join('、')}”` : ''}`
    }
    tap(root, '.dr', (b) => { const was = b.classList.contains('on'); $$(root, '.dr').forEach((x) => x.classList.remove('on')); if (!was) b.classList.add('on'); upd() })
    tapAfter(root, '.it', upd); upd()
  },
})

/* ---- 005 评价列表 ---- */
const RVS = [
  { n: 0, nm: '林*满', st: 5, at: '2 天前', sp: '石墨灰 · 降噪版', k: 'img good', long: true, tx: '通勤地铁上降噪效果很明显，报站声都听得很清楚，戴了一下午耳朵也不胀。续航比想象中好，上周充过一次到现在还有电，连手机和电脑切换也很顺，客服回复也很快，包装很扎实，送人自用都合适，会推荐给同事。', pics: [0, 1, 2] },
  { n: 1, nm: '陈*雨', st: 4, at: '5 天前', sp: '云白 · 标准版', k: 'good', tx: '音质干净，低频不糊。就是头梁有点紧，戴久了需要掰一掰。', pics: [] },
  { n: 2, nm: '王*豪', st: 5, at: '1 周前', sp: '石墨灰 · 套装版', k: 'img add good', tx: '收到就用上了，赠的收纳包很实用。', add: '用了两周追评：续航稳定，没有断连，值得入手。', pics: [3, 4] },
  { n: 3, nm: '李*然', st: 2, at: '2 周前', sp: '雾蓝 · 标准版', k: 'bad', tx: '偶尔会断连一两秒，联系客服后给了新固件，更新后好一些，先观察。', pics: [] },
  { n: 0, nm: '周*帆', st: 5, at: '3 周前', sp: '云白 · 降噪版', k: 'img', tx: '外观很好看，质感不错。', pics: [4] },
]
defx({
  id: 'MP-GOODS-005', name: '评价列表', style: '标签筛选',
  fit: '评价明细页或详情页评价段：标签筛选（全部 / 有图 / 追评 / 好评 / 差评），带图、追评、有用数，点图看大图',
  avoid: '默认只展示好评；筛选后没有结果时要给空态提示，不能留一片空白',
  kw: 'review list 评价 列表 筛选 标签 带图 追评 差评 买家秀',
  css: `.mpgoods005{width:358px;max-width:100%;background:var(--card);border-radius:16px;padding:14px 16px 6px;box-shadow:0 4px 16px var(--sh06)}
.mpgoods005 .flt{display:flex;flex-wrap:wrap;gap:8px;padding-bottom:12px}
.mpgoods005 .flt button{position:relative;height:28px;padding:0 10px;border-radius:8px;background:var(--n3);color:var(--ink2);font-size:12px;transition:background .15s,color .15s}
.mpgoods005 .flt button::after{content:"";position:absolute;inset:-8px -2px}
.mpgoods005 .flt button em{margin-left:4px;color:var(--ink3)}
.mpgoods005 .flt button.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1px var(--pm)}.mpgoods005 .flt button.on em{color:var(--p-text)}
.mpgoods005 .rvl{display:flex;flex-direction:column}
.mpgoods005 .rv{display:flex;gap:10px;padding:14px 0;border-top:1px solid var(--line)}
.mpgoods005 .rv .mn{flex:1;min-width:0}
.mpgoods005 .who{display:flex;align-items:center;justify-content:space-between;font-size:14px;font-weight:600}.mpgoods005 .who span{font-size:12px;font-weight:400;color:var(--ink3)}
${STARS('mpgoods005')}.mpgoods005 .sp{display:flex;align-items:center;gap:8px;margin-top:2px;font-size:12px;color:var(--ink3)}
.mpgoods005 .tx{margin:8px 0 0;font-size:14px;line-height:22px;color:var(--ink)}
.mpgoods005 .tx.cl{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.mpgoods005 .mo{margin-top:2px;font-size:12px;color:var(--p-text);position:relative}.mpgoods005 .mo::after{content:"";position:absolute;inset:-12px -8px}
.mpgoods005 .zp{margin-top:8px;padding:8px 10px;border-radius:8px;background:var(--n3);font-size:12px;line-height:20px;color:var(--ink2)}.mpgoods005 .zp b{color:var(--ink);font-weight:600}
.mpgoods005 .pics{display:flex;gap:6px;margin-top:8px}
.mpgoods005 .pic{position:relative;width:64px;height:64px;border-radius:8px;overflow:hidden;background:var(--ph);flex:none}
.mpgoods005 .pic img,.mpgoods005 .pv img{width:100%;height:100%;object-fit:cover;-webkit-user-drag:none}
.mpgoods005 .pic.on::after{content:"";position:absolute;inset:0;border-radius:8px;box-shadow:inset 0 0 0 2px var(--p)}
.mpgoods005 .pv{margin-top:8px;aspect-ratio:4/3;border-radius:12px;overflow:hidden;background:var(--ph)}
.mpgoods005 .ac{display:flex;justify-content:flex-end;margin-top:6px}
.mpgoods005 .lkb{position:relative;display:inline-flex;align-items:center;gap:4px;font-size:12px;color:var(--ink3)}.mpgoods005 .lkb::after{content:"";position:absolute;inset:-14px -8px}
.mpgoods005 .lkb svg{width:16px;height:16px}.mpgoods005 .lkb.on{color:var(--p-text);font-weight:600}.mpgoods005 .lkb.on svg{fill:var(--pt)}
.mpgoods005 .none{padding:28px 0;text-align:center;font-size:14px;color:var(--ink3)}
.mpgoods005 .endt{padding:6px 0 12px;text-align:center;font-size:12px;color:var(--ink3)}`,
  html: () => `<div class="mpgoods005"><div class="flt" data-ix="tabs" data-list=".rvl">${[['all', '全部', '2,386'], ['img', '有图', '312'], ['add', '追评', '86'], ['good', '好评', '2,310'], ['bad', '差评', '12']].map((t, i) => `<button type="button" data-t="${t[0]}" class="${i ? '' : 'on'}">${t[1]}<em>${t[2]}</em></button>`).join('')}</div>
<div class="rvl">${RVS.map((r) => `<div class="rv" data-k="${r.k}">${critter(r.n, 32)}<div class="mn"><div class="who">${r.nm}<span>${r.at}</span></div><div class="sp">${stars(r.st)}${r.sp}</div><p class="tx ${r.long ? 'cl' : ''}">${r.tx}</p>${r.long ? '<button type="button" class="mo">全文</button>' : ''}${r.add ? `<div class="zp"><b>追评</b>　${r.add}</div>` : ''}${r.pics.length ? `<div class="pics">${r.pics.map((p) => `<button type="button" class="pic" aria-label="查看大图">${cimg(crops[p % 5])}</button>`).join('')}</div><div class="pv" hidden></div>` : ''}<div class="ac"><button type="button" class="lkb" data-ix="like">${sv('mt_thumb')}有用 <span data-n>${(r.n + 3) * 7 % 40 + 2}</span></button></div></div></div>`).join('')}</div>
<div class="none" hidden>暂无该类评价</div><div class="endt">没有更多了</div></div>`,
  js: (root) => {
    const items = $$(root, '.rv'), none = $(root, '.none'), endt = $(root, '.endt')
    tapAfter(root, '.flt [data-t]', () => { const any = items.some((i) => !i.hidden); none.hidden = any; endt.hidden = !any })
    tap(root, '.mo', (b) => { const tx = b.previousElementSibling; const open = tx.classList.toggle('cl'); b.textContent = open ? '全文' : '收起' })
    tap(root, '.pic', (p) => {
      const rv = p.closest('.rv'), pv = $(rv, '.pv'), was = p.classList.contains('on')
      $$(rv, '.pic').forEach((x) => x.classList.remove('on'))
      if (was) { pv.hidden = true; return }
      p.classList.add('on'); pv.innerHTML = p.innerHTML; pv.hidden = false
    })
  },
})

/* ---- 006 详情分段标签 ---- */
const PARAMS_S = [['品牌', '示例品牌'], ['型号', 'NC-40 Pro'], ['佩戴方式', '头戴式'], ['降噪深度', '最高 42dB'], ['单次续航', '开启降噪约 40 小时'], ['蓝牙版本', '5.3']]
defx({
  id: 'MP-GOODS-006', name: '详情分段标签', style: '下划线滑动',
  fit: '商品详情长页的分段：图文详情、规格参数、售后保障、问答，点击切换并有滑动下划线',
  avoid: '分段超过 5 个（改成横滑标签）；每段内容都很长时不要全部预渲染，用懒加载',
  kw: 'tabs 分段 标签页 详情 参数 售后 问答 图文详情 sticky 下划线',
  css: `.mpgoods006{width:358px;max-width:100%;background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh06)}
.mpgoods006 .tbs{position:relative;display:flex;border-bottom:1px solid var(--line)}
.mpgoods006 .tbs button{position:relative;flex:1;height:48px;font-size:14px;color:var(--ink2);transition:color .2s}
.mpgoods006 .tbs button.on{color:var(--ink);font-weight:600}
.mpgoods006 .tbs button em{margin-left:3px;font-size:12px;color:var(--ink3);font-weight:400}
.mpgoods006 .tbs .ink{position:absolute;bottom:-1px;left:0;width:0;height:3px;border-radius:2px;background:var(--p);transition:left .25s cubic-bezier(.2,0,0,1),width .25s cubic-bezier(.2,0,0,1)}
.mpgoods006 .pn{padding:16px}
.mpgoods006 .dt h4{margin:0 0 6px;font-size:16px;font-weight:600}.mpgoods006 .dt p{margin:0 0 12px;font-size:14px;line-height:22px;color:var(--ink2)}
.mpgoods006 .dt .pic{height:150px;border-radius:12px;overflow:hidden;margin-bottom:12px;background:var(--ph)}.mpgoods006 .dt .pic img{width:100%;height:100%;object-fit:cover}
.mpgoods006 .kv{margin:0;display:flex;flex-direction:column}
.mpgoods006 .kv div{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--line);font-size:14px;line-height:22px}
.mpgoods006 .kv div:last-child{border-bottom:0}.mpgoods006 .kv dt{flex:none;width:76px;color:var(--ink3)}.mpgoods006 .kv dd{margin:0;flex:1;min-width:0}
.mpgoods006 .gu{display:flex;flex-direction:column;gap:14px}
.mpgoods006 .gu div{display:flex;gap:12px}
.mpgoods006 .gu i{flex:none;width:36px;height:36px;border-radius:12px;background:var(--pt);color:var(--p-text);display:flex;align-items:center;justify-content:center}.mpgoods006 .gu i svg{width:20px;height:20px}
.mpgoods006 .gu b{display:block;font-size:14px;font-weight:600;line-height:22px}.mpgoods006 .gu span{display:block;font-size:12px;line-height:20px;color:var(--ink3)}
.mpgoods006 .qs{display:flex;flex-direction:column;gap:12px}
.mpgoods006 .qs div{font-size:14px;line-height:22px}.mpgoods006 .qs b{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;margin-right:8px;border-radius:5px;background:var(--pt);color:var(--p-text);font-size:12px;font-weight:600;vertical-align:1px}
.mpgoods006 .qs p{margin:4px 0 0 28px;color:var(--ink2)}
.mpgoods006 .more{display:block;margin:14px auto 0;font-size:14px;color:var(--p-text)}`,
  html: () => `<div class="mpgoods006"><div class="tbs" data-ix="tabs"><button type="button" data-t="d" class="on">商品详情</button><button type="button" data-t="p">规格参数</button><button type="button" data-t="s">售后保障</button><button type="button" data-t="q">问答<em>28</em></button><i class="ink"></i></div>
<div class="pn dt" data-p="d"><h4>主动降噪，通勤更安静</h4><p>双麦克风实时采集环境噪声，地铁、街道、办公室都能压低一截。</p><div class="pic">${cimg(crops[1])}</div><h4>40 小时长续航</h4><p>充电 10 分钟可听约 5 小时，出差和长途通勤不焦虑。</p><div class="pic">${cimg(crops[2])}</div></div>
<div class="pn" data-p="p" hidden><dl class="kv">${PARAMS_S.map((r) => `<div><dt>${r[0]}</dt><dd>${r[1]}</dd></div>`).join('')}</dl></div>
<div class="pn" data-p="s" hidden><div class="gu">${[['mt_return', '7 天无理由退货', '未拆封、不影响二次销售可退，运费险已含'], ['shield', '1 年全国联保', '非人为损坏，凭订单到店或寄回免费维修'], ['box', '48 小时内发货', '延迟发货可获得店铺补偿券'], ['check', '正品保障', '品牌授权，假一赔三']].map((g) => `<div><i>${sv(g[0])}</i><p style="margin:0"><b>${g[1]}</b><span>${g[2]}</span></p></div>`).join('')}</div></div>
<div class="pn" data-p="q" hidden><div class="qs"><div><b>问</b>可以同时连接手机和电脑吗？<p>可以，支持多点连接，来电会自动切换。</p></div><div><b>问</b>降噪会不会有压耳感？<p>自适应降噪，多数用户反馈压耳感很轻。</p></div></div><button type="button" class="more" data-toast="查看全部 28 个问题">查看全部问答 ›</button></div></div>`,
})

/* ---- 007 配送与服务条 ---- */
const ADDR = [['北京市朝阳区 望京街道', '明天（11月5日）送达', '有货', 1], ['上海市浦东新区 张江镇', '11月6日（周五）送达', '有货', 1], ['新疆乌鲁木齐市 天山区', '11月10日（周二）前送达，运费 ¥12', '有货', 1], ['西藏拉萨市 城关区', '该地区暂不支持配送', '不可送', 0]]
defx({
  id: 'MP-GOODS-007', name: '配送与服务条', style: '送达+服务',
  fit: '价格下方一屏内说清：送到哪、何时到、运费、能不能退；点“送至”切换地址，到达时间随之变化',
  avoid: '服务承诺超过四条时只展示前三条加“更多”；不可配送的地址要明确写出，不要让用户加购后才发现',
  kw: 'delivery service 配送 送达 服务 地址 运费 退货 保障 无理由',
  css: `.mpgoods007{width:358px;max-width:100%;background:var(--card);border-radius:16px;padding:2px 16px;box-shadow:0 4px 16px var(--sh06)}
.mpgoods007 .ix-ai+.ix-ai,.mpgoods007 .ix-ai+.rw,.mpgoods007 .rw+.ix-ai,.mpgoods007 .rw+.rw{border-top:1px solid var(--line)}
.mpgoods007 .rw{display:flex;gap:12px;align-items:flex-start;width:100%;padding:12px 0;font-size:14px;line-height:22px;text-align:left}
.mpgoods007 .rw>em{flex:none;width:32px;color:var(--ink3)}.mpgoods007 .rw .bd{flex:1;min-width:0}
.mpgoods007 .rw .cv{flex:none;width:16px;height:16px;margin-top:3px;color:var(--ink3);transition:transform .25s cubic-bezier(.2,0,0,1)}
.mpgoods007 .ix-ai.open .cv{transform:rotate(90deg)}
.mpgoods007 .ad{font-weight:600}.mpgoods007 .loc{display:inline-flex;width:16px;height:16px;margin:3px 4px 0 0;vertical-align:top;color:var(--p-text)}
.mpgoods007 .sub{display:block;font-size:12px;color:var(--ink3);line-height:20px}
.mpgoods007 .eta{color:var(--ink);font-weight:600}.mpgoods007 .eta.no{color:var(--danger)}
.mpgoods007 .tg.no{background:var(--danger-bg);color:var(--danger)}.mpgoods007 .tg.ok{background:var(--ok-bg);color:var(--ok)}
.mpgoods007 .svc{display:flex;flex-wrap:wrap;gap:4px 12px}.mpgoods007 .svc span{display:inline-flex;align-items:center;gap:3px;font-size:12px;color:var(--ink2)}.mpgoods007 .svc svg{width:14px;height:14px;color:var(--ok)}
.mpgoods007 .opt{display:flex;align-items:center;gap:10px;width:100%;min-height:44px;padding:6px 0;text-align:left;font-size:14px}
.mpgoods007 .opt .rd{flex:none;width:18px;height:18px;border-radius:50%;border:1.5px solid var(--n9);position:relative}
.mpgoods007 .opt.on .rd{border-color:var(--p)}.mpgoods007 .opt.on .rd::after{content:"";position:absolute;inset:3px;border-radius:50%;background:var(--p)}
.mpgoods007 .opt.on{font-weight:600}.mpgoods007 .opt i{margin-left:auto;font-size:12px;color:var(--ink3)}
.mpgoods007 .lst{margin:0 0 8px 44px;padding:0;list-style:none;display:flex;flex-direction:column;gap:10px}
.mpgoods007 .lst li{font-size:14px;line-height:22px}.mpgoods007 .lst b{font-weight:600}.mpgoods007 .lst span{display:block;font-size:12px;color:var(--ink3);line-height:20px}`,
  html: () => `<div class="mpgoods007" data-ix="acc" data-single>
<div class="ix-ai"><button type="button" class="rw" data-h><em>送至</em><span class="bd"><i class="loc">${sv('pin')}</i><span class="ad">${ADDR[0][0]}</span> <i class="tg ok" data-tag>有货</i></span><i class="cv">${sv('chev')}</i></button><div class="ix-ab"><div><div class="lst" style="margin:0 0 8px" data-ix="radio" data-bind=".ad">${ADDR.map((a, i) => `<button type="button" class="opt ${i ? '' : 'on'}" data-o data-v="${a[0]}" data-eta="${a[1]}" data-tag="${a[2]}" data-ok="${a[3]}"><span class="rd"></span>${a[0]}${a[3] ? '' : '<i>不可配送</i>'}</button>`).join('')}</div></div></div></div>
<div class="rw"><em>配送</em><span class="bd"><span class="eta" data-eta>${ADDR[0][1]}</span><span class="sub">今日 18:00 前下单 · 满 99 元包邮，不满收 ¥6 运费</span></span></div>
<div class="ix-ai"><button type="button" class="rw" data-h><em>服务</em><span class="bd"><span class="svc"><span>${sv('check')}7 天无理由</span><span>${sv('check')}运费险</span><span>${sv('check')}正品保障</span><span>${sv('check')}1 年联保</span></span></span><i class="cv">${sv('chev')}</i></button><div class="ix-ab"><div><ul class="lst"><li><b>7 天无理由退货</b><span>签收后 7 天内，未拆封且不影响二次销售可退</span></li><li><b>退货运费险</b><span>符合条件的退货，运费由平台承担</span></li><li><b>1 年全国联保</b><span>非人为损坏免费维修，凭订单即可</span></li></ul></div></div></div>
<div class="rw"><em>发货</em><span class="bd">示例品牌旗舰店 · 广东东莞仓发货并提供售后</span></div></div>`,
  js: (root) => {
    tapAfter(root, '.opt', (o) => {
      const eta = $(root, '.eta'), tag = $(root, '[data-h] [data-tag]'), ok = o.dataset.ok === '1'
      eta.textContent = o.dataset.eta; eta.classList.toggle('no', !ok)
      tag.textContent = o.dataset.tag; tag.className = 'tg ' + (ok ? 'ok' : 'no')
      setTimeout(() => o.closest('.ix-ai').classList.remove('open'), 180)
    })
  },
})

/* ---- 008 参数表 ---- */
defx({
  id: 'MP-GOODS-008', name: '参数表', style: '分组+展开',
  fit: '规格参数的完整清单：按“基础 / 续航 / 连接”分组，常用的先展示，其余一键展开',
  avoid: '参数少于 6 项时不用分组和展开；值很长时让值换行而不是缩小字号',
  kw: 'params 参数 规格 表格 分组 展开 key value 详情 清单',
  css: `.mpgoods008{width:358px;max-width:100%;background:var(--card);border-radius:16px;padding:14px 16px 4px;box-shadow:0 4px 16px var(--sh06)}
.mpgoods008 h3{margin:0 0 4px;font-size:16px;font-weight:600}
.mpgoods008 .gp{margin:14px 0 2px;display:flex;align-items:center;gap:8px;font-size:12px;font-weight:600;color:var(--p-text)}.mpgoods008 .gp::before{content:"";width:3px;height:12px;border-radius:2px;background:var(--p)}
.mpgoods008 .kv{margin:0}.mpgoods008 .kv div{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--line);font-size:14px;line-height:22px}
.mpgoods008 .kv dt{flex:none;width:84px;color:var(--ink3)}.mpgoods008 .kv dd{margin:0;flex:1;min-width:0;overflow-wrap:anywhere}
.mpgoods008 .tgl{display:flex;align-items:center;justify-content:center;gap:4px;width:100%;height:48px;font-size:14px;color:var(--p-text)}
.mpgoods008 .tgl svg{width:16px;height:16px;transition:transform .25s cubic-bezier(.2,0,0,1)}.mpgoods008 .ix-ai.open .tgl svg{transform:rotate(180deg)}`,
  html: () => {
    const g = (t, rows) => `<div class="gp">${t}</div><dl class="kv">${rows.map((r) => `<div><dt>${r[0]}</dt><dd>${r[1]}</dd></div>`).join('')}</dl>`
    return `<div class="mpgoods008" data-ix="acc"><h3>规格参数</h3>${g('基础信息', [['品牌', '示例品牌'], ['型号', 'NC-40 Pro 石墨灰'], ['佩戴方式', '头戴式，可折叠'], ['重量', '约 258g（含电池）']])}<div class="ix-ai"><div class="ix-ab"><div>${g('降噪与音质', [['降噪方式', '混合主动降噪，支持自适应降噪 / 通透模式 / 关闭三档'], ['降噪深度', '最高 42dB'], ['驱动单元', '40mm 动圈'], ['频响范围', '20Hz - 20kHz']])}${g('续航与连接', [['蓝牙版本', '5.3，支持多点连接'], ['单次续航', '开降噪约 40 小时，关闭约 60 小时'], ['充电接口', 'Type-C，快充 10 分钟听 5 小时'], ['包装清单', '耳机 ×1、收纳包 ×1、充电线 ×1、说明书 ×1']])}</div></div><button type="button" class="tgl" data-h><span data-lb>展开全部参数</span>${sv('down')}</button></div></div>`
  },
  js: (root) => { tapAfter(root, '[data-h]', (h) => { $(h, '[data-lb]').textContent = h.closest('.ix-ai').classList.contains('open') ? '收起参数' : '展开全部参数' }) },
})

/* ---- 009 同类推荐横滑 ---- */
const REC = [1, 2, 5, 6, 7, 8, 3]
defx({
  id: 'MP-GOODS-009', name: '同类推荐横滑', style: '横滑卡片',
  fit: '详情页底部“看了又看 / 同类推荐”：横向滑动，点右下 + 直接加购，“换一批”重排',
  avoid: '推荐位放在购买栏上方抢主流程；一屏内同时露出的卡片少于 2.5 张，用户不知道能滑',
  kw: 'recommend 推荐 看了又看 同类 横滑 横向滚动 加购 换一批 猜你喜欢',
  css: `.mpgoods009{width:358px;max-width:100%;background:var(--card);border-radius:16px;padding:14px 0 14px;box-shadow:0 4px 16px var(--sh06);overflow:hidden}
.mpgoods009 .hd{display:flex;align-items:center;justify-content:space-between;padding:0 16px 12px}
.mpgoods009 .hd h3{margin:0;font-size:16px;font-weight:600}
.mpgoods009 .rf{position:relative;display:inline-flex;align-items:center;gap:4px;font-size:12px;color:var(--ink2)}.mpgoods009 .rf::after{content:"";position:absolute;inset:-14px -8px}
.mpgoods009 .rf svg{width:14px;height:14px;transition:transform .35s cubic-bezier(.2,0,0,1)}.mpgoods009 .rf.sp svg{transform:rotate(180deg)}
.mpgoods009 .ix-track{gap:10px;padding:0 16px;scroll-padding:0 16px;scroll-snap-type:x proximity}.mpgoods009 .ix-track>*{scroll-snap-align:start}
.mpgoods009 .rc{position:relative;width:112px;display:flex;flex-direction:column}
.mpgoods009 .rc .pimg{width:112px;height:112px;border-radius:12px;overflow:hidden;background:var(--ph)}.mpgoods009 .rc img{width:100%;height:100%;object-fit:cover;-webkit-user-drag:none;user-select:none}
.mpgoods009 .rc h4{margin:8px 0 6px;font-size:14px;font-weight:400;line-height:20px;height:40px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.mpgoods009 .rc .pr{display:flex;align-items:center;justify-content:space-between}.mpgoods009 .rc .price b{font-size:16px}
.mpgoods009 .rc .ad{position:relative;width:28px;height:28px;border-radius:50%;background:var(--pt);color:var(--p-text);display:flex;align-items:center;justify-content:center}.mpgoods009 .rc .ad svg{width:16px;height:16px}.mpgoods009 .rc .ad::after{content:"";position:absolute;inset:-8px}
.mpgoods009 .rc .ad:active{background:var(--pm)}
.mpgoods009 .mr{width:72px;align-items:center;justify-content:center;gap:8px;background:var(--n3);border-radius:12px;font-size:12px;color:var(--ink2);text-align:center;height:112px}.mpgoods009 .mr svg{width:20px;height:20px}
.mpgoods009 .pg{position:relative;width:36px;height:3px;margin:12px auto 0;border-radius:2px;background:var(--n6)}.mpgoods009 .pg i{position:absolute;left:var(--x,0%);top:0;width:40%;height:100%;border-radius:2px;background:var(--p);transition:left .1s}`,
  html: () => `<div class="mpgoods009"><div class="hd"><h3>看了又看</h3><button type="button" class="rf" data-ref>${sv('refresh')}换一批</button></div><div class="ix-track" data-ix="drag">${recCards(REC)}</div><div class="pg"><i></i></div></div>`,
  js: (root) => {
    const tr = $(root, '.ix-track'), bar = $(root, '.pg i'); let off = 0
    const prog = () => { const m = tr.scrollWidth - tr.clientWidth; bar.style.setProperty('--x', (m > 0 ? tr.scrollLeft / m * 60 : 0) + '%') }
    tr.addEventListener('scroll', prog)
    tap(root, '[data-ref]', (b) => { off = (off + 3) % REC.length; tr.innerHTML = recCards(REC.map((_, i) => REC[(i + off) % REC.length])); tr.scrollTo({ left: 0 }); b.classList.toggle('sp'); prog() })
    prog()
  },
})
function recCards(list) {
  const mk = (i, k) => { const p = PRODUCTS[i]; return `<div class="rc"><div class="pimg"><img src="${P(i)}" alt="" draggable="false"></div><h4>${p.n} ${p.d}</h4><div class="pr"><span class="price"><small>¥</small><b>${p.p}</b></span><button type="button" class="ad" data-toast="已加入购物车" aria-label="加入购物车">${sv('plus')}</button></div></div>` }
  return list.map(mk).join('') + `<button type="button" class="rc mr" data-toast="查看更多推荐">${sv('arrowright')}查看更多</button>`
}

/* ---- 010 购买栏·图标双按钮 ---- */
const BUYBASE = (c) => `.${c}{width:358px;max-width:100%}`
defx({
  id: 'MP-GOODS-010', name: '购买栏·图标双按钮', style: '标准',
  fit: '多数商品的详情页底栏：店铺、客服、购物车三个图标在左，“加入购物车 / 立即购买”并排，加购后角标 +1',
  avoid: '图标超过 4 个（挤压按钮）；只有一个购买动作时用“购买栏·通栏单键”',
  kw: 'buy bar 购买栏 底栏 加入购物车 立即购买 店铺 客服 购物车 角标',
  css: `${BUYBASE('mpgoods010')}
.mpgoods010 .bb{position:relative;display:flex;align-items:center;gap:6px;padding:8px 12px 24px;background:var(--card);border-radius:16px;box-shadow:0 -2px 16px var(--sh06),0 4px 16px var(--sh06)}
.mpgoods010 .bb::after{content:"";position:absolute;left:50%;bottom:8px;width:112px;height:4px;margin-left:-56px;border-radius:2px;background:color-mix(in srgb,var(--scrim) 18%,transparent)}
.mpgoods010 .ic{position:relative;width:44px;height:44px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:12px;color:var(--ink2);flex:none}
.mpgoods010 .ic svg{width:22px;height:22px}
.mpgoods010 .ic b{position:absolute;right:2px;top:0;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--pd);color:#fff;font-size:12px;font-weight:600;display:flex;align-items:center;justify-content:center;font-variant-numeric:tabular-nums;box-shadow:0 0 0 2px var(--card)}
.mpgoods010 .ic.bump svg{animation:mpgoods010b .32s cubic-bezier(.2,0,0,1)}@keyframes mpgoods010b{40%{transform:scale(1.25)}}
.mpgoods010 .acts{flex:1;display:flex;gap:8px;margin-left:4px}.mpgoods010 .acts .btn{flex:1;height:44px;padding:0 6px;font-size:16px}
.mpgoods010 .acts .btn-s{background:var(--pm);color:var(--p-text)}`,
  html: () => `<div class="mpgoods010"><div class="bb"><button type="button" class="ic" data-toast="进入店铺">${sv('mt_store')}店铺</button><button type="button" class="ic" data-toast="联系客服">${sv('mt_headset')}客服</button><button type="button" class="ic" data-cart>${sv('cart')}购物车<b>3</b></button><div class="acts"><button type="button" class="btn btn-s" data-add>加入购物车</button><button type="button" class="btn btn-p" data-toast="前往确认订单">立即购买</button></div></div></div>`,
  js: (root) => {
    tap(root, '[data-add]', () => {
      const c = $(root, '[data-cart]'), b = $(c, 'b'), n = Math.min(99, +b.textContent + 1)
      b.textContent = n; c.classList.remove('bump'); void c.offsetWidth; c.classList.add('bump'); tt(root, '已加入购物车')
    })
    tap(root, '[data-cart]', () => tt(root, '进入购物车'))
  },
})

/* ---- 011 购买栏·通栏单键 ---- */
defx({
  id: 'MP-GOODS-011', name: '购买栏·通栏单键', style: '随状态变化',
  fit: '爆款、预约、缺货等一个主动作的场景：按钮随状态变成“立即购买 / 到货通知 / 预约抢购 / 已限购”，不让用户点到不可用的按钮',
  avoid: '普通商品（要同时给加购和购买）；状态文案超过 8 个字时放到按钮上方的提示行',
  kw: 'buy bar 购买栏 单按钮 预约 到货通知 缺货 限购 状态按钮 底栏',
  css: `${BUYBASE('mpgoods011')}
.mpgoods011 .demo{display:flex;align-items:center;gap:6px;margin-bottom:10px;font-size:12px;color:var(--ink3)}
.mpgoods011 .demo button{position:relative;height:28px;padding:0 10px;border-radius:8px;background:var(--glass0);color:var(--ink2);font-size:12px}.mpgoods011 .demo button::after{content:"";position:absolute;inset:-8px -2px}
.mpgoods011 .demo button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:inset 0 0 0 1px var(--ink3)}
.mpgoods011 .bb{position:relative;display:flex;align-items:center;gap:12px;padding:10px 12px 24px 16px;background:var(--card);border-radius:16px;box-shadow:0 -2px 16px var(--sh06),0 4px 16px var(--sh06)}
.mpgoods011 .bb::after{content:"";position:absolute;left:50%;bottom:8px;width:112px;height:4px;margin-left:-56px;border-radius:2px;background:color-mix(in srgb,var(--scrim) 18%,transparent)}
.mpgoods011 .info{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px}
.mpgoods011 .info .price b{font-size:22px;font-weight:700}.mpgoods011 .info .price small{font-size:14px}
.mpgoods011 .info span.t{font-size:12px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mpgoods011 .info strong{font-size:14px;font-weight:600;line-height:22px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mpgoods011 .btn{min-width:148px;height:44px;flex:none}
${LD('mpgoods011')}
.mpgoods011 .btn.line{background:var(--card);color:var(--p-text);box-shadow:inset 0 0 0 1.5px var(--p)}.mpgoods011 .btn.done{background:var(--ok-bg);color:var(--ok);box-shadow:none}
.mpgoods011 .btn[aria-disabled=true]{background:var(--n6);color:var(--ink5);box-shadow:none}`,
  html: () => `<div class="mpgoods011"><div class="demo" data-ix="tabs" data-g="stt"><span>状态预览</span><button type="button" data-t="sale" class="on">在售</button><button type="button" data-t="out">缺货</button><button type="button" data-t="pre">预约</button><button type="button" data-t="lim">限购</button></div>
<div class="bb" data-p="sale" data-g="stt"><div class="info"><span class="price"><small>¥</small><b>549</b></span><span class="t">券后价 · 已减 ¥50</span></div><button type="button" class="btn btn-p" data-act="buy">立即购买</button></div>
<div class="bb" data-p="out" data-g="stt" hidden><div class="info"><strong>暂时无货</strong><span class="t">到货后第一时间通知你</span></div><button type="button" class="btn line" data-act="notify">到货通知</button></div>
<div class="bb" data-p="pre" data-g="stt" hidden><div class="info"><strong>11月8日 10:00 开售</strong><span class="t">已有 12,386 人预约</span></div><button type="button" class="btn btn-p" data-act="book">预约抢购</button></div>
<div class="bb" data-p="lim" data-g="stt" hidden><div class="info"><strong>已达限购上限</strong><span class="t">每人限购 2 件，已购买 2 件</span></div><button type="button" class="btn" data-act="none" aria-disabled="true">已限购</button></div></div>`,
  js: (root) => {
    tap(root, '[data-act]', (b) => {
      const a = b.dataset.act
      if (a === 'none') { tt(root, '该商品每人限购 2 件'); return }
      if (a === 'buy') {
        if (b.classList.contains('busy')) return
        b.classList.add('busy'); b.innerHTML = '<span class="spin"></span>提交中'
        setTimeout(() => { b.classList.remove('busy'); b.textContent = '立即购买'; tt(root, '已进入确认订单') }, 900); return
      }
      const on = b.classList.toggle('done'); b.classList.toggle('line', !on && a === 'notify'); b.classList.toggle('btn-p', !on && a === 'book')
      b.textContent = a === 'notify' ? (on ? '已设置提醒' : '到货通知') : (on ? '已预约' : '预约抢购'); tt(root, on ? (a === 'notify' ? '到货后会通知你' : '开售前 5 分钟提醒你') : '已取消')
    })
  },
})

/* ---- 012 购买栏·悬浮胶囊 ---- */
defx({
  id: 'MP-GOODS-012', name: '购买栏·悬浮胶囊', style: '客服+收藏',
  fit: '高客单价、需要咨询的商品：客服与收藏做成轻图标，右侧是双色一体的胶囊按钮；悬浮感强，不遮底部内容',
  avoid: '需要显示价格的购买栏（价格放不下，用通栏单键）；客服图标无人值守时不要放红点',
  kw: 'buy bar 购买栏 胶囊 悬浮 客服 收藏 加入购物车 立即购买 高客单价',
  css: `${BUYBASE('mpgoods012')}
.mpgoods012 .cap{position:relative;display:flex;align-items:center;gap:2px;height:60px;padding:0 8px 0 6px;background:var(--card);border-radius:22px;box-shadow:0 10px 28px var(--sh14)}
.mpgoods012 .ic{position:relative;width:48px;height:48px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:12px;color:var(--ink2);flex:none}
.mpgoods012 .ic svg{width:22px;height:22px;transition:transform .2s cubic-bezier(.2,0,0,1)}
.mpgoods012 .ic i.dot{position:absolute;left:26px;top:6px;width:8px;height:8px;border-radius:50%;background:var(--pd);box-shadow:0 0 0 2px var(--card)}
.mpgoods012 .ic.on{color:var(--p-text);font-weight:600}.mpgoods012 .ic.on svg{fill:var(--pm);transform:scale(1.1)}
.mpgoods012 .sp{flex:1;display:flex;height:44px;margin-left:6px;border-radius:22px;overflow:hidden}
.mpgoods012 .sp button{flex:1;font-size:16px;font-weight:600;transition:filter .15s}.mpgoods012 .sp button:active{filter:brightness(.95)}
.mpgoods012 .sp .a{background:var(--pm);color:var(--p-text)}.mpgoods012 .sp .b{background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff}`,
  html: () => `<div class="mpgoods012"><div class="cap"><button type="button" class="ic" data-service>${sv('mt_headset')}客服<i class="dot"></i></button><button type="button" class="ic" data-fav>${sv('heart')}<span>收藏</span></button><div class="sp"><button type="button" class="a" data-toast="已加入购物车">加入购物车</button><button type="button" class="b" data-toast="前往确认订单">立即购买</button></div></div></div>`,
  js: (root) => {
    tap(root, '[data-service]', (b) => { const d = $(b, '.dot'); if (d) d.remove(); tt(root, '正在接入客服…') })
    tap(root, '[data-fav]', (b) => { const on = b.classList.toggle('on'); $(b, 'span').textContent = on ? '已收藏' : '收藏'; tt(root, on ? '已加入收藏' : '已取消收藏') })
  },
})

/* ---- 013 买家问答区 ---- */
defx({
  id: 'MP-GOODS-013', name: '买家问答区', style: '提问+回答',
  fit: '详情页的“大家问”：展示高赞问题与首条回答，可展开其余回答，也能直接提问',
  avoid: '没有人回答的问题排在最前（会显得冷清），按回答数和有用数排序；提问框不要强制登录后才能看到',
  kw: 'qa 问答 提问 回答 买家问答 大家问 咨询 有用 展开 详情页',
  css: `.mpgoods013{width:358px;max-width:100%;background:var(--card);border-radius:16px;padding:14px 16px 6px;box-shadow:0 4px 16px var(--sh06)}
.mpgoods013 .hd{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}.mpgoods013 .hd h3{margin:0;font-size:16px;font-weight:600}.mpgoods013 .hd em{margin-left:6px;font-size:12px;font-weight:400;color:var(--ink3)}
.mpgoods013 .ask{display:flex;gap:8px;align-items:center;margin-bottom:6px}
.mpgoods013 .ask input{flex:1;min-width:0;height:40px;padding:0 14px;border-radius:20px;border:1px solid transparent;background:var(--n3);font:inherit;font-size:14px;color:var(--ink);outline:none}
.mpgoods013 .ask input::placeholder{color:var(--ink3)}.mpgoods013 .ask input:focus{border-color:var(--ink2)}.mpgoods013 .ask input.err{border-color:var(--danger)}
.mpgoods013 .ask .btn{height:40px;padding:0 16px;font-size:14px}
.mpgoods013 .qa{padding:12px 0;border-top:1px solid var(--line)}
.mpgoods013 .q,.mpgoods013 .a{display:flex;gap:8px;font-size:14px;line-height:22px}.mpgoods013 .q span,.mpgoods013 .a span{flex:1;min-width:0}
.mpgoods013 .q span{font-weight:600}.mpgoods013 .a{margin-top:6px;color:var(--ink2)}
.mpgoods013 .lbl{flex:none;width:20px;height:20px;margin-top:1px;border-radius:5px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600}
.mpgoods013 .q .lbl{background:var(--p);color:#fff}.mpgoods013 .a .lbl{background:var(--pt);color:var(--p-text)}
.mpgoods013 .meta{display:flex;align-items:center;gap:12px;margin:6px 0 0 28px;font-size:12px;color:var(--ink3)}
.mpgoods013 .meta .tg{height:18px}
.mpgoods013 .meta .lkb{position:relative;display:inline-flex;align-items:center;gap:3px;margin-left:auto;color:var(--ink3)}.mpgoods013 .meta .lkb::after{content:"";position:absolute;inset:-14px -8px}
.mpgoods013 .meta .lkb svg{width:14px;height:14px}.mpgoods013 .meta .lkb.on{color:var(--p-text);font-weight:600}
.mpgoods013 .exp{display:flex;align-items:center;gap:4px;margin:8px 0 0 28px;font-size:12px;color:var(--p-text);position:relative}.mpgoods013 .exp::after{content:"";position:absolute;inset:-12px -8px}
.mpgoods013 .exp svg{width:14px;height:14px;transition:transform .25s}.mpgoods013 .ix-ai.open .exp svg{transform:rotate(180deg)}
.mpgoods013 .ix-ab .a:first-child{margin-top:6px}
.mpgoods013 .new{animation:mpgoods013n .35s cubic-bezier(.2,0,0,1)}@keyframes mpgoods013n{from{opacity:0;transform:translateY(-6px)}}
.mpgoods013 .wait{margin:6px 0 0 28px;font-size:12px;color:var(--ink3)}
.mpgoods013 .endt{padding:6px 0 12px;text-align:center;font-size:12px;color:var(--ink3)}`,
  html: () => `<div class="mpgoods013"><div class="hd"><h3>大家问<em>28 个问题</em></h3></div><div class="ask"><input type="text" maxlength="50" placeholder="想了解什么？问问买过的人" aria-label="提问"><button type="button" class="btn btn-p" data-ask>提问</button></div>
<div class="qlist"><div class="qa" data-ix="acc"><div class="q"><i class="lbl">问</i><span>可以同时连接手机和电脑吗？切换时需要重新配对吗</span></div><div class="a"><i class="lbl">答</i><span>可以，支持多点连接，手机来电会自动切换，不需要重新配对。</span></div><div class="meta"><span class="tg tg-soft">店铺回复</span>2 天前<button type="button" class="lkb" data-ix="like">${sv('mt_thumb')}有用 <span data-n>24</span></button></div><div class="ix-ai"><div class="ix-ab"><div><div class="a"><i class="lbl">答</i><span>我用的 Win 电脑加 iPhone，切换挺顺，偶尔需要手动点一下。</span></div><div class="meta">买家 · 一周前</div><div class="a"><i class="lbl">答</i><span>Mac 也可以，系统要在 12 以上。</span></div><div class="meta">买家 · 2 周前</div></div></div><button type="button" class="exp" data-h>查看其余 2 个回答${sv('down')}</button></div></div>
<div class="qa"><div class="q"><i class="lbl">问</i><span>降噪会不会有压耳感？</span></div><div class="a"><i class="lbl">答</i><span>自适应降噪，压耳感很轻，我戴一下午没有不适。</span></div><div class="meta"><span class="tg tg-soft">买家</span>5 天前<button type="button" class="lkb" data-ix="like">${sv('mt_thumb')}有用 <span data-n>9</span></button></div></div></div><div class="endt">没有更多了</div></div>`,
  js: (root) => {
    const inp = $(root, '.ask input'), list = $(root, '.qlist')
    const submit = () => {
      const v = inp.value.trim()
      if (!v) { inp.classList.add('err'); tt(root, '请先输入你的问题'); return }
      const d = document.createElement('div'); d.className = 'qa new'
      d.innerHTML = `<div class="q"><i class="lbl">问</i><span></span></div><div class="wait">刚刚 · 等待回答，有回复会通知你</div>`
      $(d, '.q span').textContent = v; list.insertBefore(d, list.firstChild); inp.value = ''; tt(root, '提问成功')
    }
    inp.addEventListener('input', () => inp.classList.remove('err'))
    inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') submit() })
    tap(root, '[data-ask]', submit)
    tapAfter(root, '[data-h]', (h) => { const o = h.closest('.ix-ai').classList.contains('open'); h.firstChild.textContent = o ? '收起回答' : '查看其余 2 个回答' })
  },
})

/* ================= 购物车与订单 ORD ================= */

const TGB = (c) => `.${c} .tgb{position:relative;flex:none;width:44px;height:26px;border-radius:13px;background:var(--n7);transition:background .2s}.${c} .tgb::before{content:"";position:absolute;inset:-9px -4px}.${c} .tgb::after{content:"";position:absolute;left:2px;top:2px;width:22px;height:22px;border-radius:50%;background:var(--card);box-shadow:0 1px 3px var(--sh25);transition:transform .2s cubic-bezier(.2,0,0,1)}.${c} .tgb.on{background:var(--p)}.${c} .tgb.on::after{transform:translateX(18px)}`
const RD = (c) => `.${c} .rdo{flex:none;position:relative;width:20px;height:20px;border-radius:50%;border:1.5px solid var(--n9);transition:border-color .15s}.${c} .rdo::after{content:"";position:absolute;inset:3px;border-radius:50%;background:var(--p);transform:scale(0);transition:transform .15s cubic-bezier(.2,0,0,1)}.${c} .on>.rdo,.${c} .rdo.on{border-color:var(--p)}.${c} .on>.rdo::after,.${c} .rdo.on::after{transform:scale(1)}`
const emptyTile = (ic, t, d, btn) => `<div class="mt0">${tileHTML(ic, 'ci')}<b>${t}</b><span>${d}</span>${btn || ''}</div>`
const MT0 = (c) => `.${c} .mt0{display:flex;flex-direction:column;align-items:center;gap:6px;padding:28px 16px 30px;text-align:center}.${c} .mt0 b{margin-top:6px;font-size:16px;font-weight:600}.${c} .mt0 span{font-size:14px;color:var(--ink3)}.${c} .mt0 .btn{margin-top:10px;height:36px;padding:0 20px;font-size:14px}`
const G = {
  ear: { n: '无线降噪耳机 主动降噪 蓝牙 5.3 超长续航 头戴式 通勤出差运动通用', sp: '石墨灰 / 降噪版', p: 699, i: 0 },
  shoe: { n: '轻量跑鞋 缓震透气 男女同款', sp: '云白 / 42 码', p: 329, i: 1 },
  mug: { n: '陶瓷马克杯', sp: '手作釉面 · 350ml', p: 69, i: 2 },
  tote: { n: '帆布托特包', sp: '原色 · 大号', p: 159, i: 3 },
  watch: { n: '机械腕表 钢壳皮带', sp: '银色 / 40mm', p: 899, i: 4 },
  lamp: { n: '护眼台灯', sp: '无频闪 · 三档调光', p: 219, i: 5 },
  bottle: { n: '保温水杯', sp: '鼠尾草绿 · 500ml', p: 89, i: 6 },
}

guide('mp', 'ORD', [
  ['购物车页面', '购物车商品行 + 购物车结算栏', '左滑删除、步进、勾选与合计联动；结算栏带凑单进度，差多少一眼看见'],
  ['确认订单页', '收货地址卡 → 配送方式切换 → 确认订单商品清单 → 订单金额明细', '地址在最上、商品在中间、金额在下，最后接提交订单栏，顺序和用户的核对习惯一致'],
  ['选优惠券、选地址、选支付方式', '优惠券选择 / 地址选择列表 / 支付方式选择', '单选列表，选中态明确，不可用项写原因，不是直接隐藏'],
  ['支付环节', '收银台', '金额、倒计时、支付方式、确认按钮一屏内，支付中、失败重试、成功都有状态'],
  ['订单进度', '订单状态步骤条 + 物流时间线', '步骤条看大状态，时间线看每一站；最新一条高亮，旧的折叠'],
  ['订单列表', '订单状态标签列表 + 订单卡', '标签筛选状态，卡片按状态变按钮：只给一个主按钮，其余线框'],
  ['售后、评价、发票这类表单页', '售后申请表 / 评价提交 / 发票信息', '先选类型再按需出现字段：售后先选原因，评价按星级换标签且差评须说明，发票企业才要税号，保存前逐项校验'],
])

/* ---- 001 购物车商品行 ---- */
const crow = (g, o = {}) => {
  const q = o.q || 1, mx = o.max || 99
  if (o.inv) return `<div class="row inv" data-ix="swipe" data-w="66"><div class="sf"><span class="ck dis" aria-hidden="true"></span><div class="pimg"><img src="${P(g.i)}" alt=""></div><div class="inf"><div class="nm"><span class="tg tg-soft">失效</span>${g.n}</div><span class="spc">${g.sp}</span><div class="lw"><span class="gone">商品已下架</span><button type="button" class="btn btn-s btn-sm" data-toast="为你找相似商品">找相似</button></div></div></div><div class="sa"><button type="button" class="del" data-del aria-label="删除">删除</button></div></div>`
  return `<div class="row" data-ix="swipe" data-w="132" data-price="${g.p}"><div class="sf"><button type="button" class="ck ${o.on ? 'on' : ''}" data-c aria-label="选择商品"></button><div class="pimg"><img src="${P(g.i)}" alt=""></div><div class="inf"><div class="nm">${g.n}</div><button type="button" class="spc" data-toast="选择规格">${g.sp}${sv('down')}</button><div class="lw"><span class="price"><small>¥</small><b>${g.p}</b></span><div class="stp" data-ix="stepper" data-min="1" data-max="${mx}" data-tip="${o.tip || '已达库存上限'}"><button type="button" data-d="-1" class="${q <= 1 ? 'dis' : ''}" aria-label="减少">${sv('minus')}</button><b data-val>${q}</b><button type="button" data-d="1" class="${q >= mx ? 'dis' : ''}" aria-label="增加">${sv('plus')}</button></div></div></div></div><div class="sa"><button type="button" class="fav" data-del data-toast="已移入收藏">收藏</button><button type="button" class="del" data-del>删除</button></div></div>`
}
defx({
  id: 'MP-ORD-001', name: '购物车商品行', style: '左滑+步进+勾选',
  fit: '购物车页的商品列表：勾选、数量步进、左滑出“收藏 / 删除”，失效商品置灰不可选，小计随勾选与数量实时联动',
  avoid: '一行里放超过两个可点区域以外的操作（规格、数量、价格各一个就够）；库存不足时不要静默改数量，要提示',
  kw: 'cart 购物车 商品行 左滑删除 步进器 勾选 全选 小计 失效商品 库存',
  css: `.mpord001{width:358px;max-width:100%;background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh06)}
${CK('mpord001')}${STP('mpord001')}${MT0('mpord001')}
.mpord001 .hd{display:flex;align-items:center;gap:10px;padding:14px 16px 12px;font-size:14px}.mpord001 .hd svg{width:18px;height:18px;flex:none}.mpord001 .hd b{font-weight:600;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mpord001 .hd .mg{position:relative;font-size:12px;color:var(--p-text);font-weight:600}.mpord001 .hd .mg::after{content:"";position:absolute;inset:-14px -8px}
.mpord001 .row{border-top:1px solid var(--line)}
.mpord001 .sf{display:flex;align-items:center;gap:12px;padding:14px 16px;background:var(--card)}
.mpord001 .pimg{position:relative;width:88px;height:88px;border-radius:12px;overflow:hidden;flex:none;background:var(--ph)}.mpord001 .pimg img{width:100%;height:100%;object-fit:cover;-webkit-user-drag:none}
.mpord001 .inf{flex:1;min-width:0;min-height:88px;display:flex;flex-direction:column;gap:4px}
.mpord001 .nm{font-size:14px;line-height:20px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.mpord001 .nm .tg{margin-right:6px;vertical-align:1px}
.mpord001 .spc{align-self:flex-start;display:inline-flex;align-items:center;gap:2px;max-width:100%;height:22px;padding:0 4px 0 8px;border-radius:4px;background:var(--n3);font-size:12px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mpord001 .spc svg{width:12px;height:12px;flex:none}
.mpord001 .lw{margin-top:auto;display:flex;align-items:center;justify-content:space-between;gap:8px}.mpord001 .price b{font-size:18px}
.mpord001 .sa button{width:66px;color:#fff;font-size:14px;font-weight:600}.mpord001 .sa .fav{background:#6A727D}.mpord001 .sa .del{background:var(--danger-fill)}
.mpord001 .row.inv .nm,.mpord001 .row.inv .gone{color:var(--ink3)}.mpord001 .row.inv .pimg img{filter:grayscale(1);opacity:.55}.mpord001 .gone{font-size:12px}
.mpord001 .btn-sm{position:relative;height:30px;padding:0 12px;font-size:12px}.mpord001 .btn-sm::after{content:"";position:absolute;inset:-7px -2px}
.mpord001 .ft{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-top:1px solid var(--line);background:var(--n1);font-size:14px;color:var(--ink2)}.mpord001 .ft b{color:var(--ink);font-weight:600}.mpord001 .ft .price b{color:var(--price);font-size:22px}.mpord001 .ft .price{display:inline-flex;align-items:baseline;gap:1px}`,
  html: () => `<div class="mpord001" data-ix="checks"><div class="hd"><button type="button" class="ck part" data-all aria-label="全选本店商品"></button>${sv('mt_store')}<b>示例品牌旗舰店</b><button type="button" class="mg" data-toast="领取店铺优惠券">领券</button></div>
<div class="rows">${crow(G.ear, { on: 1 })}${crow(G.shoe, { on: 1, q: 2, max: 10 })}${crow(G.mug, { q: 1, max: 2, tip: '仅剩 2 件，不能再加了' })}${crow(G.tote, { inv: 1 })}</div>
<div class="ft" data-ft><span>已选 <b class="fn">3</b> 件</span><span>小计 <span class="price"><small>¥</small><b class="sum">1,357.00</b></span></span></div>
<div class="empty" hidden>${emptyTile('cart', '购物车是空的', '去挑几件喜欢的商品吧', '<button type="button" class="btn btn-p" data-toast="返回首页">去逛逛</button>')}</div></div>`,
  js: (root) => {
    const recalc = () => {
      const rs = $$(root, '.row:not(.inv)'), all = $(root, '[data-all]'), items = $$(root, '[data-c]')
      let n = 0, sum = 0
      rs.forEach((r) => { if ($(r, '[data-c]').classList.contains('on')) { const q = +$(r, '[data-val]').textContent; n += q; sum += q * +r.dataset.price } })
      const on = items.filter((c) => c.classList.contains('on')).length
      all.classList.toggle('on', on === items.length && on > 0); all.classList.toggle('part', on > 0 && on < items.length)
      $(root, '.fn').textContent = n; $(root, '.sum').textContent = yuan(sum)
      const none = $$(root, '.row').length === 0
      $(root, '.empty').hidden = !none; $(root, '.rows').hidden = none; $(root, '[data-ft]').hidden = none; $(root, '.hd').hidden = none
    }
    tap(root, '[data-d="1"]', (b) => { if (b.classList.contains('dis')) tt(root, b.closest('.stp').dataset.tip) })
    tapAfter(root, '[data-c],[data-all],[data-d]', recalc)
    tapAfter(root, '[data-del]', () => setTimeout(recalc, 320))
    recalc()
  },
})

/* ---- 002 购物车结算栏 ---- */
const CART2 = [[G.bottle, 2, 1], [G.tote, 1, 1], [G.mug, 1, 0]]
defx({
  id: 'MP-ORD-002', name: '购物车结算栏', style: '凑单+管理',
  fit: '购物车底部：全选、合计、去结算，上方是满减凑单进度；点“管理”切到批量删除 / 移入收藏，勾选联动合计与数量',
  avoid: '合计里混入未选商品；“去结算”的数字和购物车角标含义不同（一个是件数一个是种类）时不要同时出现',
  kw: 'cart bar 结算栏 全选 合计 去结算 凑单 满减 管理 批量删除',
  css: `.mpord002{width:358px;max-width:100%;background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh06)}
${CK('mpord002')}${LD('mpord002')}${MT0('mpord002')}
.mpord002 .hd{display:flex;align-items:center;justify-content:space-between;padding:14px 16px 4px}.mpord002 .hd h3{margin:0;font-size:16px;font-weight:600}.mpord002 .hd h3 em{margin-left:6px;font-size:12px;font-weight:400;color:var(--ink3)}
.mpord002 .hd .mgb{position:relative;font-size:14px;color:var(--p-text);font-weight:600}.mpord002 .hd .mgb::after{content:"";position:absolute;inset:-12px -8px}
.mpord002 .tip{margin:8px 16px 0;padding:10px 12px;border-radius:12px;background:var(--pt)}
.mpord002 .tip .ln{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:12px;color:var(--ink2)}.mpord002 .tip b{color:var(--p-text);font-weight:600}
.mpord002 .tip .go{position:relative;flex:none;color:var(--p-text);font-weight:600}.mpord002 .tip .go::after{content:"";position:absolute;inset:-14px -8px}
.mpord002 .tip .pgb{margin-top:8px;height:6px;border-radius:3px;background:var(--card2);overflow:hidden}.mpord002 .tip .pgb i{display:block;height:100%;width:100%;border-radius:3px;background:var(--p);transition:width .3s cubic-bezier(.2,0,0,1)}
.mpord002 .it{display:flex;align-items:center;gap:12px;padding:12px 16px;transition:opacity .2s}
.mpord002 .it .pimg{width:52px;height:52px;border-radius:8px;overflow:hidden;flex:none;background:var(--ph)}.mpord002 .it .pimg img{width:100%;height:100%;object-fit:cover}
.mpord002 .it .tx{flex:1;min-width:0}.mpord002 .it .nm{font-size:14px;line-height:20px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mpord002 .it .sp2{font-size:12px;color:var(--ink3)}
.mpord002 .it .pq{flex:none;text-align:right;font-size:12px;color:var(--ink3)}.mpord002 .it .pq .price b{font-size:16px}.mpord002 .it .pq .price{display:block;margin-bottom:2px}
.mpord002 .pay{display:flex;align-items:center;gap:12px;padding:10px 16px 12px;border-top:1px solid var(--line);background:var(--card)}
.mpord002 .all{display:flex;align-items:center;gap:8px;font-size:14px;flex:none}
.mpord002 .tot{flex:1;min-width:0;display:flex;flex-direction:column;align-items:flex-end;font-size:12px;color:var(--ink3)}.mpord002 .tot .ln1{display:flex;align-items:baseline;gap:2px;color:var(--ink);font-size:14px}.mpord002 .tot .price b{font-size:22px;font-weight:700}
.mpord002 .go2{flex:none;min-width:108px;height:44px;padding:0 14px;font-size:16px}.mpord002 .go2[aria-disabled=true]{background:var(--n6);color:var(--ink5);box-shadow:none}
.mpord002 .mgr{display:none;flex:1;justify-content:flex-end;gap:8px}.mpord002 .mgr .btn{height:36px;padding:0 14px;font-size:14px;position:relative}.mpord002 .mgr .btn::after{content:"";position:absolute;inset:-4px -2px}
.mpord002 .mgr .ln2{background:var(--card);color:var(--ink2);box-shadow:inset 0 0 0 1px var(--n7)}.mpord002 .mgr .dl{background:var(--danger-fill);color:#fff}
.mpord002.mg .tot,.mpord002.mg .go2,.mpord002.mg .tip{display:none}.mpord002.mg .mgr{display:flex}`,
  html: () => `<div class="mpord002" data-ix="checks"><div class="hd"><h3>购物车<em class="cnt">${CART2.length} 件商品</em></h3><button type="button" class="mgb" data-mg>管理</button></div>
<div class="tip"><div class="ln"><span class="msg">已满 ¥300，已减 ¥30</span><button type="button" class="go" data-toast="去凑单：满 300 减 30 专区">去凑单 ›</button></div><div class="pgb"><i></i></div></div>
<div class="items">${CART2.map(([g, q, on]) => `<div class="it" data-price="${g.p}" data-q="${q}"><button type="button" class="ck ${on ? 'on' : ''}" data-c aria-label="选择商品"></button><div class="pimg"><img src="${P(g.i)}" alt=""></div><div class="tx"><div class="nm">${g.n}</div><div class="sp2">${g.sp}</div></div><div class="pq"><span class="price"><small>¥</small><b>${g.p}</b></span>×${q}</div></div>`).join('')}</div>
<div class="empty" hidden>${emptyTile('cart', '购物车是空的', '选中的商品已全部删除')}</div>
<div class="pay"><div class="all"><button type="button" class="ck part" data-all aria-label="全选"></button>全选</div><div class="tot"><span class="ln1">合计<span class="price"><small>¥</small><b class="sum">307.00</b></span></span><span class="sv">已减 ¥30，不含运费</span></div><button type="button" class="btn btn-p go2" data-go>去结算(3)</button><div class="mgr"><button type="button" class="btn ln2" data-fav>移入收藏</button><button type="button" class="btn dl" data-rm>删除</button></div></div></div>`,
  js: (root) => {
    const TH = 300, OFF = 30
    const recalc = () => {
      const its = $$(root, '.it'), items = $$(root, '[data-c]'), all = $(root, '[data-all]')
      let n = 0, sub = 0
      its.forEach((r) => { if ($(r, '[data-c]').classList.contains('on')) { n += +r.dataset.q; sub += +r.dataset.price * +r.dataset.q } })
      const on = items.filter((c) => c.classList.contains('on')).length
      all.classList.toggle('on', on === items.length && on > 0); all.classList.toggle('part', on > 0 && on < items.length)
      const hit = sub >= TH, off = hit ? OFF : 0
      $(root, '.sum').textContent = yuan(sub - off); $(root, '.sv').textContent = off ? `已减 ¥${OFF}，不含运费` : '不含运费'
      $(root, '.msg').innerHTML = hit ? `已满 ¥${TH}，已减 <b>¥${OFF}</b>` : (sub > 0 ? `还差 <b>¥${TH - sub}</b> 可减 ¥${OFF}` : `满 ¥${TH} 减 ¥${OFF}，去凑单`)
      $(root, '.pgb i').style.width = Math.min(100, sub / TH * 100) + '%'
      const g = $(root, '[data-go]'); g.setAttribute('aria-disabled', n === 0); g.textContent = n ? `去结算(${n})` : '去结算'
      $(root, '.cnt').textContent = its.length + ' 件商品'
      const none = its.length === 0; $(root, '.empty').hidden = !none; $(root, '.items').hidden = none; $(root, '.tip').hidden = none || $(root, '.mpord002').classList.contains('mg')
    }
    tapAfter(root, '[data-c],[data-all]', recalc)
    tap(root, '[data-mg]', (b) => { const on = $(root, '.mpord002').classList.toggle('mg'); b.textContent = on ? '完成' : '管理'; recalc() })
    tap(root, '[data-go]', (b) => { tt(root, b.getAttribute('aria-disabled') === 'true' ? '请先选择商品' : '前往确认订单') })
    tap(root, '[data-rm],[data-fav]', (b) => {
      const sel = $$(root, '.it').filter((r) => $(r, '[data-c]').classList.contains('on'))
      if (!sel.length) { tt(root, '请先选择商品'); return }
      sel.forEach((r) => r.remove()); tt(root, b.hasAttribute('data-rm') ? `已删除 ${sel.length} 件商品` : `已移入收藏 ${sel.length} 件`); recalc()
    })
    recalc()
  },
})

/* ---- 003 收货地址卡 ---- */
const ADDR_FILLED = (n, ph, tags, ad) => `<span class="pin">${sv('pin')}</span><div class="bd"><div class="who"><b>${n}</b><span>${ph}</span>${tags.map((t) => `<i class="tg tg-soft">${t}</i>`).join('')}</div><p>${ad}</p></div><i class="cv">${sv('chev')}</i><i class="strip"></i>`
defx({
  id: 'MP-ORD-003', name: '收货地址卡', style: '信封条纹',
  fit: '确认订单页最顶部：显示默认收货地址，整卡可点进入地址选择；没有地址时显示“添加”态，可一键用微信地址',
  avoid: '把电话号码完整显示（中间用 **** 遮住）；地址很长时不要截成一行，最多两行再省略',
  kw: 'address 收货地址 地址卡 默认地址 添加地址 微信地址 确认订单 信封 条纹',
  css: `.mpord003{width:358px;max-width:100%;display:flex;flex-direction:column;gap:12px}
.mpord003 .ac{position:relative;display:flex;align-items:center;gap:12px;width:100%;padding:16px 16px 18px;background:var(--card);border-radius:16px;text-align:left;box-shadow:0 4px 16px var(--sh06);overflow:hidden;transition:transform .15s cubic-bezier(.2,0,0,1)}
.mpord003 .ac:active{transform:scale(.99)}
.mpord003 .pin{flex:none;width:36px;height:36px;border-radius:12px;background:var(--pt);color:var(--p-text);display:flex;align-items:center;justify-content:center}.mpord003 .pin svg{width:20px;height:20px}
.mpord003 .bd{flex:1;min-width:0}
.mpord003 .who{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:16px}.mpord003 .who b{font-weight:600}.mpord003 .who span{font-size:14px;color:var(--ink2)}
.mpord003 .bd p{margin:4px 0 0;font-size:14px;line-height:22px;color:var(--ink2);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.mpord003 .cv{flex:none;width:16px;height:16px;color:var(--ink3)}
.mpord003 .strip{position:absolute;left:0;right:0;bottom:0;height:4px;background:repeating-linear-gradient(135deg,var(--p) 0 10px,var(--card) 10px 15px,var(--pm) 15px 25px,var(--card) 25px 30px)}
.mpord003 .ac.empty{border:1.5px dashed var(--pm);box-shadow:none;background:var(--glass0)}.mpord003 .ac.empty .pin{background:var(--p);color:#fff}
.mpord003 .ac.empty .bd b{display:block;font-size:16px;font-weight:600}.mpord003 .ac.empty .bd span{display:block;margin-top:2px;font-size:12px;color:var(--ink3)}
.mpord003 .fill-in{animation:mpord003f .35s cubic-bezier(.2,0,0,1)}@keyframes mpord003f{from{opacity:0;transform:translateY(6px)}}`,
  html: () => `<div class="mpord003"><div class="ac" role="button" tabindex="0" data-toast="前往选择收货地址">${ADDR_FILLED('林小满', '138****5206', ['默认', '公司'], '北京市朝阳区望京街道阜通东大街 6 号院 3 号楼 1204 室（前台代收，送到请电话联系）')}</div><button type="button" class="ac empty" data-wx><span class="pin">${sv('plus')}</span><span class="bd"><b>添加收货地址</b><span>点这里，用微信地址一键填入</span></span><i class="cv">${sv('chev')}</i></button></div>`,
  js: (root) => {
    tap(root, '[data-wx]', (b) => {
      const d = document.createElement('div'); d.className = 'ac fill-in'; d.setAttribute('role', 'button'); d.dataset.toast = '前往选择收货地址'
      d.innerHTML = ADDR_FILLED('陈晓雨', '186****3392', ['微信地址'], '上海市浦东新区张江镇科苑路 88 号 2 栋 305'); b.replaceWith(d); tt(root, '已使用微信地址')
    })
  },
})

/* ---- 004 地址选择列表 ---- */
const ADS = [['林小满', '138****5206', ['默认', '公司'], '北京市朝阳区望京街道阜通东大街 6 号院 3 号楼 1204 室', '林小满 · 望京街道'], ['林小满', '138****5206', ['家'], '北京市海淀区中关村南大街 5 号 2 号楼 801', '林小满 · 中关村'], ['陈晓雨', '186****3392', [], '新疆乌鲁木齐市天山区解放北路 120 号', '']]
defx({
  id: 'MP-ORD-004', name: '地址选择列表', style: '单选+编辑',
  fit: '从地址卡进入的选择页：单选一条、可编辑、可新增；超出配送范围的地址置灰并写原因，不直接隐藏',
  avoid: '把编辑入口做成整行（和选中冲突）；新增入口放在列表最底下被长列表淹没，保持底部固定',
  kw: 'address list 地址选择 地址列表 单选 编辑 新增地址 配送范围 默认 家',
  css: `.mpord004{width:358px;max-width:100%;background:var(--card);border-radius:22px 22px 16px 16px;box-shadow:0 8px 24px var(--sh10);overflow:hidden}
${RD('mpord004')}
.mpord004 .hd{display:flex;align-items:center;justify-content:space-between;padding:16px 16px 6px}.mpord004 .hd h3{margin:0;font-size:16px;font-weight:600}.mpord004 .hd span{font-size:12px;color:var(--ink3)}
.mpord004 .ad{position:relative;display:flex;align-items:center;gap:12px;width:100%;padding:14px 16px;text-align:left;border-bottom:1px solid var(--line);cursor:pointer;transition:background .15s}
.mpord004 .ad.on{background:var(--pt)}
.mpord004 .ad .bd{flex:1;min-width:0}.mpord004 .who{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:14px}.mpord004 .who b{font-weight:600}.mpord004 .who span{color:var(--ink2)}
.mpord004 .ad p{margin:4px 0 0;font-size:14px;line-height:22px;color:var(--ink2)}
.mpord004 .ed{position:relative;flex:none;width:28px;height:28px;display:flex;align-items:center;justify-content:center;color:var(--ink3)}.mpord004 .ed::after{content:"";position:absolute;inset:-8px}.mpord004 .ed svg{width:18px;height:18px}
.mpord004 .ad.off{cursor:not-allowed}.mpord004 .ad.off .who,.mpord004 .ad.off p{color:var(--ink5)}.mpord004 .ad.off .rdo{background:var(--soft);border-color:var(--n6)}
.mpord004 .why{display:inline-block;margin-top:4px;font-size:12px;color:var(--danger)}
.mpord004 .nw{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;height:48px;font-size:14px;color:var(--p-text);font-weight:600;border-bottom:1px solid var(--line)}.mpord004 .nw svg{width:16px;height:16px}
.mpord004 .ft{display:flex;align-items:center;gap:12px;padding:12px 16px 16px}.mpord004 .ft .cur{flex:1;min-width:0;font-size:12px;color:var(--ink3)}.mpord004 .ft .cur b{display:block;font-size:14px;color:var(--ink);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mpord004 .ft .btn{flex:none;min-width:112px}`,
  html: () => `<div class="mpord004"><div class="hd"><h3>选择收货地址</h3><span>共 ${ADS.length} 个</span></div><div data-ix="radio" data-bind=".cur b">${ADS.map((a, i) => {
    const off = !a[4]
    return `<div class="ad ${i === 0 ? 'on' : ''} ${off ? 'off' : ''}" ${off ? '' : `data-o data-v="${a[4]}"`} role="radio" aria-checked="${i === 0}"><span class="rdo"></span><div class="bd"><div class="who"><b>${a[0]}</b><span>${a[1]}</span>${a[2].map((t) => `<i class="tg tg-soft">${t}</i>`).join('')}</div><p>${a[3]}</p>${off ? '<span class="why">超出配送范围，请更换地址</span>' : ''}</div><button type="button" class="ed" aria-label="编辑地址">${sv('edit')}</button></div>`
  }).join('')}</div><button type="button" class="nw" data-toast="新增收货地址">${sv('plus')}新增收货地址</button><div class="ft"><div class="cur">配送至<b>林小满 · 望京街道</b></div><button type="button" class="btn btn-p" data-ok>确定</button></div></div>`,
  js: (root) => {
    tap(root, '.ed', (b, e) => { e.stopPropagation(); tt(root, '编辑地址') })
    tap(root, '.ad.off', () => tt(root, '该地址超出配送范围，请更换'))
    tap(root, '[data-ok]', () => tt(root, '已选择：' + $(root, '.cur b').textContent))
    tapAfter(root, '.ad[data-o]', (o) => $$(root, '.ad').forEach((x) => x.setAttribute('aria-checked', x === o)))
  },
})

/* ---- 005 配送方式切换 ---- */
defx({
  id: 'MP-ORD-005', name: '配送方式切换', style: '配送/自提',
  fit: '确认订单页的“快递配送 / 到店自提”：切换后下方内容整体替换（地址与时间，或门店与自提时间），运费随之变化',
  avoid: '两种方式都要填地址的场景；自提门店很多时用“选择门店”页，不要在这里放长列表',
  kw: 'delivery 配送方式 快递 自提 到店自提 门店 取货 运费 切换 外送',
  css: `.mpord005{width:358px;max-width:100%;background:var(--card);border-radius:16px;padding:16px;box-shadow:0 4px 16px var(--sh06)}
.mpord005 .sg{position:relative;display:flex;padding:3px;border-radius:12px;background:var(--soft)}
.mpord005 .sg button{position:relative;z-index:1;flex:1;height:38px;display:flex;align-items:center;justify-content:center;gap:6px;font-size:14px;color:var(--ink2);transition:color .2s}.mpord005 .sg button::after{content:"";position:absolute;inset:-3px 0}
.mpord005 .sg button svg{width:18px;height:18px}.mpord005 .sg button.on{color:var(--ink);font-weight:600}
.mpord005 .sg .ink{position:absolute;top:3px;bottom:3px;left:0;width:0;border-radius:9px;background:var(--card);box-shadow:0 2px 6px var(--sh12);transition:left .25s cubic-bezier(.2,0,0,1),width .25s cubic-bezier(.2,0,0,1)}
.mpord005 .pn{padding-top:14px}
.mpord005 .ad{display:flex;align-items:center;gap:10px;padding:12px;border-radius:12px;background:var(--n2)}
.mpord005 .ad svg{flex:none;width:18px;height:18px;color:var(--p-text)}.mpord005 .ad .bd{flex:1;min-width:0;font-size:14px;line-height:22px}.mpord005 .ad b{font-weight:600}.mpord005 .ad span{color:var(--ink2)}
.mpord005 .ad .cv{width:16px;height:16px;color:var(--ink3)}
.mpord005 .ad .km{font-size:12px;color:var(--ink3);display:block}
.mpord005 h4{margin:14px 0 8px;font-size:14px;font-weight:600}
.mpord005 .ts{display:flex;flex-wrap:wrap;gap:8px}
.mpord005 .ts button{position:relative;height:36px;padding:0 12px;border-radius:8px;background:var(--n3);font-size:14px;color:var(--ink);transition:background .15s,box-shadow .15s}.mpord005 .ts button::after{content:"";position:absolute;inset:-4px -2px}
.mpord005 .ts button.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1px var(--p)}
.mpord005 .nt{margin:10px 0 0;font-size:12px;line-height:20px;color:var(--ink3)}
.mpord005 .call{position:relative;flex:none;width:32px;height:32px;border-radius:50%;background:var(--card);color:var(--p-text);display:flex;align-items:center;justify-content:center}.mpord005 .call::after{content:"";position:absolute;inset:-6px}.mpord005 .call svg{width:16px;height:16px}
.mpord005 .fee{display:flex;align-items:center;justify-content:space-between;margin-top:14px;padding-top:12px;border-top:1px solid var(--line);font-size:14px;color:var(--ink2)}.mpord005 .fee b{font-weight:600;color:var(--ink)}.mpord005 .fee small{font-size:12px;color:var(--ink3);margin-left:6px}`,
  html: () => `<div class="mpord005"><div class="sg" data-ix="tabs"><button type="button" data-t="ex" class="on">${sv('truck')}快递配送</button><button type="button" data-t="pk">${sv('mt_store')}到店自提</button><i class="ink"></i></div>
<div class="pn" data-p="ex"><button type="button" class="ad" style="width:100%;text-align:left" data-toast="更换收货地址">${sv('pin')}<span class="bd"><b>林小满</b> 138****5206<br><span>北京市朝阳区望京街道阜通东大街 6 号院 3 号楼 1204 室</span></span><i class="cv">${sv('chev')}</i></button><h4>送达时间</h4><div class="ts" data-ix="radio"><button type="button" class="on" data-o>尽快送达（明天 11-05）</button><button type="button" data-o>周末（11-07）</button><button type="button" data-o>工作日（11-09）</button></div><p class="nt">11-04 18:00 前下单，次日送达；偏远地区会延迟 1-2 天。</p></div>
<div class="pn" data-p="pk" hidden><div class="ad">${sv('mt_store')}<span class="bd"><b>示例品牌 · 望京中心店</b><span class="km">距你 1.2 km · 营业 09:00-22:00</span><span class="km">朝阳区望京街道阜通东大街 10 号</span></span><button type="button" class="call" data-toast="拨打门店电话" aria-label="拨打电话">${sv('phone')}</button></div><h4>自提时间</h4><div class="ts" data-ix="radio"><button type="button" class="on" data-o>今天 18:00 后</button><button type="button" data-o>明天 10:00 后</button><button type="button" data-o>明天 14:00 后</button></div><p class="nt">下单后会生成取货码，到店出示即可，商品为你保留 3 天。</p></div>
<div class="fee"><span>运费</span><span><b class="fv">¥6.00</b><small class="fn">满 ¥99 包邮</small></span></div></div>`,
  js: (root) => {
    tapAfter(root, '.sg [data-t]', (b) => { const ex = b.dataset.t === 'ex'; $(root, '.fv').textContent = ex ? '¥6.00' : '¥0.00'; $(root, '.fn').textContent = ex ? '满 ¥99 包邮' : '自提免运费' })
  },
})

/* ---- 006 确认订单商品清单 ---- */
const OL = [[G.ear, 1], [G.shoe, 1], [G.mug, 2], [G.tote, 1]]
defx({
  id: 'MP-ORD-006', name: '确认订单商品清单', style: '折叠+留言',
  fit: '确认订单页的商品区：先展示前两件，其余折叠；赠品、运费险开关、买家留言放在同一张卡里，小计随开关变化',
  avoid: '把商品价格和优惠、运费混在同一行；留言框不限字数（要有计数）；折叠后不告诉用户还有几件',
  kw: 'order confirm 确认订单 商品清单 赠品 运费险 买家留言 折叠 小计 店铺',
  css: `.mpord006{width:358px;max-width:100%;background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh06)}
${TGB('mpord006')}
.mpord006 .hd{display:flex;align-items:center;gap:8px;padding:14px 16px 4px;font-size:14px;font-weight:600}.mpord006 .hd svg{width:18px;height:18px;flex:none}.mpord006 .hd svg:last-child{width:14px;height:14px;color:var(--ink3)}
.mpord006 .it{display:flex;gap:12px;padding:12px 16px}
.mpord006 .it .pimg{width:72px;height:72px;border-radius:12px;overflow:hidden;flex:none;background:var(--ph)}.mpord006 .it .pimg img{width:100%;height:100%;object-fit:cover}
.mpord006 .it .tx{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px}.mpord006 .it .nm{font-size:14px;line-height:20px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.mpord006 .it .sp2{font-size:12px;color:var(--ink3)}
.mpord006 .it .pq{flex:none;text-align:right;font-size:12px;color:var(--ink3)}.mpord006 .it .price{display:block;margin-bottom:4px}.mpord006 .it .price b{font-size:16px}
.mpord006 .mr{display:flex;align-items:center;justify-content:center;gap:4px;width:100%;height:40px;font-size:12px;color:var(--ink2)}.mpord006 .mr svg{width:14px;height:14px;transition:transform .25s cubic-bezier(.2,0,0,1)}.mpord006 .ix-ai.open .mr svg{transform:rotate(180deg)}
.mpord006 .gf{display:flex;align-items:center;gap:8px;margin:0 16px 4px;padding:10px 12px;border-radius:8px;background:var(--n2);font-size:12px;color:var(--ink2)}.mpord006 .gf span:last-child{margin-left:auto}
.mpord006 .rw{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:48px;padding:0 16px;border-top:1px solid var(--line);font-size:14px}.mpord006 .rw .sub1{display:block;font-size:12px;color:var(--ink3)}.mpord006 .rw .v{color:var(--ink2);display:flex;align-items:center;gap:4px}.mpord006 .rw .v svg{width:14px;height:14px}
.mpord006 .msg{display:flex;align-items:center;gap:12px;padding:12px 16px;border-top:1px solid var(--line);font-size:14px}.mpord006 .msg label{flex:none}
.mpord006 .msg input{flex:1;min-width:0;height:36px;padding:0 10px;border-radius:8px;border:1px solid transparent;background:var(--n3);font:inherit;font-size:14px;color:var(--ink);outline:none}.mpord006 .msg input::placeholder{color:var(--ink3)}.mpord006 .msg input:focus{border-color:var(--ink2)}.mpord006 .msg em{flex:none;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
.mpord006 .sub{display:flex;align-items:baseline;justify-content:flex-end;gap:6px;padding:12px 16px 14px;border-top:1px solid var(--line);font-size:14px;color:var(--ink2)}.mpord006 .sub .price b{font-size:18px}`,
  html: () => {
    const it = ([g, q]) => `<div class="it"><div class="pimg"><img src="${P(g.i)}" alt=""></div><div class="tx"><div class="nm">${g.n}</div><div class="sp2">${g.sp}</div></div><div class="pq"><span class="price"><small>¥</small><b>${g.p}</b></span>×${q}</div></div>`
    return `<div class="mpord006" data-ix="acc"><div class="hd">${sv('mt_store')}示例品牌旗舰店${sv('chev')}</div>${OL.slice(0, 2).map(it).join('')}<div class="ix-ai"><div class="ix-ab"><div>${OL.slice(2).map(it).join('')}</div></div><button type="button" class="mr" data-h><span data-lb>共 ${OL.reduce((a, b) => a + b[1], 0)} 件，展开另外 2 种</span>${sv('down')}</button></div>
<div class="gf"><span class="tg tg-soft">赠品</span><span>收纳袋 ×1</span><span>¥0.00</span></div>
<div class="rw"><span>配送方式</span><span class="v">快递免邮${sv('chev')}</span></div>
<div class="rw"><span>运费险<small class="sub1">退货时运费最高赔付 ¥10</small></span><div style="display:flex;align-items:center;gap:10px"><span class="price"><small>¥</small><b style="font-size:14px">1.50</b></span><button type="button" class="tgb on" data-ix="toggle" role="switch" aria-checked="true" aria-label="运费险"></button></div></div>
<div class="msg"><label for="mpord006m">买家留言</label><input id="mpord006m" type="text" maxlength="50" placeholder="选填，建议先和商家协商"><em class="ct">0/50</em></div>
<div class="sub"><span>共 <b class="qn">5</b> 件，小计</span><span class="price"><small>¥</small><b class="sm">1,326.50</b></span></div></div>`
  },
  js: (root) => {
    const base = OL.reduce((a, [g, q]) => a + g.p * q, 0), n = OL.reduce((a, b) => a + b[1], 0)
    const inp = $(root, '.msg input'), ct = $(root, '.ct')
    const upd = () => { const ins = $(root, '.tgb').classList.contains('on'); $(root, '.sm').textContent = yuan(base + (ins ? 1.5 : 0)); $(root, '.qn').textContent = n }
    inp.addEventListener('input', () => { ct.textContent = inp.value.length + '/50' })
    tapAfter(root, '.tgb', upd)
    tapAfter(root, '[data-h]', (h) => { $(h, '[data-lb]').textContent = h.closest('.ix-ai').classList.contains('open') ? '收起' : `共 ${n} 件，展开另外 2 种` })
    upd()
  },
})

/* ---- 007 优惠券选择 ---- */
const CPS = [['30', '满 300 可用', '店铺满减券', '全场通用 · 不与店铺满减叠加', '有效期至 11-30', '-¥30.00'], ['60', '满 500 可用', '数码品类券', '仅限降噪耳机、腕表等数码商品', '有效期至 11-20', '-¥60.00'], ['20', '无门槛', '新人专享券', '全场通用，首单可用', '有效期至 11-10', '-¥20.00']]
const CPX = [['150', '满 1000 可用', '数码大额券', '仅限降噪耳机、腕表等数码商品', '数码商品合计 ¥699，还差 ¥301'], ['40', '满 200 可用', '服饰品类券', '仅限服饰类商品', '本单商品不适用']]
defx({
  id: 'MP-ORD-007', name: '优惠券选择', style: '票券+单选',
  fit: '确认订单页选券：可用 / 不可用分页，单选一张，可选“不使用”；不可用的券写清原因，底部汇总本次抵扣',
  avoid: '默认勾选抵扣最小的券（要默认最优）；不可用券不写原因；叠加规则不说明',
  kw: 'coupon 优惠券 选择 票券 可用 不可用 抵扣 满减 无门槛 确认订单',
  css: `.mpord007{width:358px;max-width:100%;background:var(--bg);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh08)}
${RD('mpord007')}
.mpord007 .tbs{position:relative;display:flex;background:var(--card);border-bottom:1px solid var(--line)}.mpord007 .tbs button{flex:1;height:48px;font-size:14px;color:var(--ink2);transition:color .2s}.mpord007 .tbs button.on{color:var(--ink);font-weight:600}.mpord007 .tbs .ink{position:absolute;bottom:-1px;left:0;width:0;height:3px;border-radius:2px;background:var(--p);transition:left .25s cubic-bezier(.2,0,0,1),width .25s cubic-bezier(.2,0,0,1)}
.mpord007 .pn{padding:12px;display:flex;flex-direction:column;gap:10px}
.mpord007 .tk{position:relative;display:flex;align-items:stretch;min-height:88px;background:var(--card);border-radius:12px;cursor:pointer;transition:box-shadow .15s}
.mpord007 .tk::before,.mpord007 .tk::after{content:"";position:absolute;left:92px;width:14px;height:14px;margin-left:-7px;border-radius:50%;background:var(--n3)}.mpord007 .tk::before{top:-7px}.mpord007 .tk::after{bottom:-7px}
.mpord007 .tk.on{box-shadow:inset 0 0 0 1.5px var(--p)}
.mpord007 .am{flex:none;width:92px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;border-right:1px dashed var(--pm);color:var(--price)}.mpord007 .am .price b{font-size:28px;font-weight:700}.mpord007 .am i{font-size:12px;color:var(--ink2)}
.mpord007 .inf{flex:1;min-width:0;padding:12px;display:flex;flex-direction:column;justify-content:center;gap:2px}.mpord007 .inf b{font-size:14px;font-weight:600}.mpord007 .inf span{font-size:12px;line-height:18px;color:var(--ink3)}
.mpord007 .tk .rdo{align-self:center;margin-right:12px}
.mpord007 .no{display:flex;align-items:center;gap:12px;min-height:52px;padding:0 16px;border-radius:12px;background:var(--card);font-size:14px;cursor:pointer;box-shadow:none}.mpord007 .no.on{box-shadow:inset 0 0 0 1.5px var(--p)}.mpord007 .no span{flex:1}
.mpord007 .tk.dim{cursor:not-allowed}.mpord007 .tk.dim .am,.mpord007 .tk.dim .inf b{color:var(--ink5)}.mpord007 .tk.dim .price{color:var(--ink5)}.mpord007 .tk.dim .am i{color:var(--ink5)}
.mpord007 .why{display:inline-block;margin-top:4px;padding:0 6px;height:20px;line-height:20px;border-radius:4px;background:var(--soft);color:var(--ink2);font-size:12px;align-self:flex-start}
.mpord007 .ft{display:flex;align-items:center;gap:12px;padding:12px 16px 16px;background:var(--card);border-top:1px solid var(--line)}.mpord007 .ft .sm{flex:1;font-size:12px;color:var(--ink3)}.mpord007 .ft .sm b{display:block;font-size:16px;color:var(--price);font-weight:600}.mpord007 .ft .btn{flex:none;min-width:112px}`,
  html: () => `<div class="mpord007"><div class="tbs" data-ix="tabs"><button type="button" data-t="a" class="on">可用 (${CPS.length})</button><button type="button" data-t="x">不可用 (${CPX.length})</button><i class="ink"></i></div>
<div class="pn" data-p="a" data-ix="radio" data-bind=".cur"><div class="no" data-o data-v="未使用"><span>不使用优惠券</span><i class="rdo"></i></div>${CPS.map((c, i) => `<div class="tk ${i === 0 ? 'on' : ''}" data-o data-v="${c[5]}" role="radio"><div class="am"><span class="price"><small>¥</small><b>${c[0]}</b></span><i>${c[1]}</i></div><div class="inf"><b>${c[2]}</b><span>${c[3]}</span><span>${c[4]}</span></div><i class="rdo"></i></div>`).join('')}</div>
<div class="pn" data-p="x" hidden>${CPX.map((c) => `<div class="tk dim" data-why="${c[4]}"><div class="am"><span class="price"><small>¥</small><b>${c[0]}</b></span><i>${c[1]}</i></div><div class="inf"><b>${c[2]}</b><span>${c[3]}</span><em class="why">${c[4]}</em></div></div>`).join('')}</div>
<div class="ft"><div class="sm">已优惠<b class="cur">-¥30.00</b></div><button type="button" class="btn btn-p" data-ok>确定</button></div></div>`,
  js: (root) => {
    tap(root, '.tk.dim', (t) => tt(root, t.dataset.why))
    tap(root, '[data-ok]', () => tt(root, '已选择：' + $(root, '.cur').textContent))
  },
})

/* ---- 008 支付方式选择 ---- */
const PAYM = [['mt_bubbles', '微信支付', '推荐，免输密码', 0], ['mt_yen', '支付宝', '余额 / 花呗 / 银行卡', 0], ['mt_card', '工商银行 储蓄卡（3069）', '单笔限额 ¥500', 500]]
defx({
  id: 'MP-ORD-008', name: '支付方式选择', style: '单选+余额抵扣',
  fit: '提交订单后、收银台前的支付方式选择：账户余额可开关抵扣，银行卡超限额时自动置灰，按钮金额实时变化',
  avoid: '默认选中用户从没用过的方式；置灰项不写原因（用户不知道为什么不能选）',
  kw: 'payment 支付方式 微信 支付宝 银行卡 余额 抵扣 限额 单选 收银台',
  css: `.mpord008{width:358px;max-width:100%;background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh06)}
${RD('mpord008')}${TGB('mpord008')}
.mpord008 .amt{padding:18px 16px 14px;text-align:center;background:linear-gradient(180deg,var(--pt),var(--card))}.mpord008 .amt small{display:block;font-size:12px;color:var(--ink3)}.mpord008 .amt .price{display:inline-flex;align-items:baseline;gap:2px;margin-top:4px}.mpord008 .amt .price b{font-size:32px;font-weight:700}.mpord008 .amt .price small{display:inline;font-size:16px;color:var(--price)}
.mpord008 .bal{display:flex;align-items:center;gap:12px;min-height:56px;padding:0 16px;border-top:1px solid var(--line)}.mpord008 .bal .ic{flex:none;width:36px;height:36px;border-radius:12px;background:var(--pt);color:var(--p-text);display:flex;align-items:center;justify-content:center}.mpord008 .bal .ic svg{width:20px;height:20px}
.mpord008 .bal .tx{flex:1;min-width:0;font-size:14px}.mpord008 .bal .tx small{display:block;font-size:12px;color:var(--ink3)}
.mpord008 .pm{display:flex;align-items:center;gap:12px;width:100%;min-height:60px;padding:0 16px;border-top:1px solid var(--line);text-align:left;cursor:pointer;transition:background .15s}
.mpord008 .pm.on{background:var(--pt)}.mpord008 .pm .ic{flex:none;width:36px;height:36px;border-radius:12px;background:var(--n3);color:var(--ink2);display:flex;align-items:center;justify-content:center}.mpord008 .pm.on .ic{background:var(--lift);color:var(--p-text)}.mpord008 .pm .ic svg{width:20px;height:20px}
.mpord008 .pm .tx{flex:1;min-width:0;font-size:14px;font-weight:600}.mpord008 .pm .tx small{display:block;margin-top:1px;font-size:12px;font-weight:400;color:var(--ink3)}
.mpord008 .pm.off{cursor:not-allowed}.mpord008 .pm.off .tx,.mpord008 .pm.off .ic{color:var(--ink5)}.mpord008 .pm.off .rdo{background:var(--soft);border-color:var(--n6)}.mpord008 .pm.off .tx small{color:var(--danger)}
.mpord008 .ft{padding:12px 16px 16px;border-top:1px solid var(--line)}.mpord008 .ft .btn{width:100%}`,
  html: () => `<div class="mpord008"><div class="amt"><small>应付金额</small><span class="price"><small>¥</small><b class="pay">628.00</b></span></div>
<div class="bal"><span class="ic">${sv('wallet')}</span><div class="tx">使用账户余额<small>可用余额 ¥128.50，本单可抵 ¥128.50</small></div><button type="button" class="tgb" data-ix="toggle" role="switch" aria-checked="false" aria-label="使用余额"></button></div>
<div data-ix="radio">${PAYM.map((m, i) => `<div class="pm ${i === 0 ? 'on' : ''}" data-o data-v="${m[1]}" data-lim="${m[3]}" role="radio"><span class="ic">${sv(m[0])}</span><div class="tx">${m[1]}<small>${m[2]}</small></div><i class="rdo"></i></div>`).join('')}</div>
<div class="ft"><button type="button" class="btn btn-p" data-pay>确认支付 ¥628.00</button></div></div>`,
  js: (root) => {
    const TOTAL = 628, BAL = 128.5
    const pms = $$(root, '.pm')
    const upd = () => {
      const bal = $(root, '.tgb').classList.contains('on'), pay = TOTAL - (bal ? BAL : 0)
      $(root, '.pay').textContent = yuan(pay); $(root, '[data-pay]').textContent = `确认支付 ¥${yuan(pay)}`
      pms.forEach((p) => {
        const lim = +p.dataset.lim, off = lim > 0 && pay > lim
        p.classList.toggle('off', off); p.toggleAttribute('data-o', !off)
        const s = $(p, 'small'); if (!p.dataset.sub) p.dataset.sub = s.textContent
        s.textContent = off ? `超出单笔限额 ¥${lim}，可开启余额抵扣` : p.dataset.sub
      })
      const cur = pms.find((p) => p.classList.contains('on'))
      if (cur && cur.classList.contains('off')) { cur.classList.remove('on'); pms[0].classList.add('on') }
    }
    tapAfter(root, '.tgb', upd)
    tap(root, '.pm.off', (p) => tt(root, `超出单笔限额 ¥${p.dataset.lim}`))
    tap(root, '[data-pay]', () => tt(root, `发起支付：${$(root, '.pm.on').dataset.v} ¥${$(root, '.pay').textContent}`))
    upd()
  },
})

/* ---- 009 收银台 ---- */
defx({
  id: 'MP-ORD-009', name: '收银台', style: '三态切换',
  fit: '拉起支付的页面：金额、剩余时间、支付方式、确认按钮一屏内；点击后进入“支付中”，成功跳到结果，失败原地重试',
  avoid: '支付中仍可重复点击；失败只弹一个“失败”而不说原因与下一步；倒计时到 0 后不置灰按钮',
  kw: 'cashier 收银台 支付 付款 倒计时 支付中 支付成功 支付失败 重试 确认支付',
  css: `.mpord009{width:358px;max-width:100%}
${RD('mpord009')}${LD('mpord009')}
.mpord009 .card{background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh06)}
.mpord009 .hd{padding:20px 16px 14px;text-align:center;background:linear-gradient(180deg,var(--pt),var(--card))}.mpord009 .hd .shop{font-size:14px;color:var(--ink2)}
.mpord009 .hd .price{display:inline-flex;align-items:baseline;gap:2px;margin-top:6px}.mpord009 .hd .price b{font-size:32px;font-weight:700}.mpord009 .hd .price small{font-size:16px}
.mpord009 .hd .cdt{margin-top:6px;font-size:12px;color:var(--ink3)}.mpord009 .hd .cdt b{display:inline-block;min-width:62px;font-weight:600;color:var(--p-text);font-variant-numeric:tabular-nums}
.mpord009 .err{display:flex;align-items:flex-start;gap:8px;margin:0 16px 10px;padding:10px 12px;border-radius:8px;background:var(--danger-bg);color:var(--danger);font-size:12px;line-height:20px}.mpord009 .err svg{flex:none;width:16px;height:16px;margin-top:2px}
.mpord009 .pm{display:flex;align-items:center;gap:12px;width:100%;min-height:56px;padding:0 16px;border-top:1px solid var(--line);text-align:left;cursor:pointer}
.mpord009 .pm .ic{flex:none;width:32px;height:32px;border-radius:8px;background:var(--pt);color:var(--p-text);display:flex;align-items:center;justify-content:center}.mpord009 .pm .ic svg{width:18px;height:18px}
.mpord009 .pm .tx{flex:1;min-width:0;font-size:14px;font-weight:600}.mpord009 .pm .tx small{display:block;font-size:12px;font-weight:400;color:var(--ink3)}
.mpord009 .ft{padding:12px 16px 16px}.mpord009 .ft .btn{width:100%}.mpord009 .btn.busy{pointer-events:none}.mpord009 .btn .spin{margin-right:2px}
.mpord009 .done{padding:28px 16px 20px;text-align:center}.mpord009 .done .okc{width:64px;height:64px;margin:0 auto;border-radius:50%;background:var(--ok-bg);color:var(--ok);display:flex;align-items:center;justify-content:center;animation:mpord009p .4s cubic-bezier(.2,0,0,1)}.mpord009 .done .okc svg{width:34px;height:34px}@keyframes mpord009p{from{transform:scale(.6);opacity:0}}
.mpord009 .done h3{margin:14px 0 0;font-size:22px;font-weight:700}.mpord009 .done .amt{margin-top:4px;font-size:16px;font-weight:600;color:var(--ink)}
.mpord009 .done dl{margin:16px 0 0;padding:12px;border-radius:12px;background:var(--n2);text-align:left;font-size:12px;line-height:22px}.mpord009 .done dl div{display:flex;justify-content:space-between;gap:12px}.mpord009 .done dt{color:var(--ink3)}.mpord009 .done dd{margin:0;color:var(--ink2)}
.mpord009 .done .acts{display:flex;gap:10px;margin-top:16px}.mpord009 .done .acts .btn{flex:1;padding:0 8px}.mpord009 .done .acts .line{background:var(--card);color:var(--ink2);box-shadow:inset 0 0 0 1px var(--n7)}
.mpord009 .done .re{margin-top:12px;font-size:12px;color:var(--ink3);position:relative}.mpord009 .done .re::after{content:"";position:absolute;inset:-14px -8px}
.mpord009 .demo{display:flex;align-items:center;justify-content:center;gap:6px;margin-top:12px;font-size:12px;color:var(--ink3)}
.mpord009 .demo button{position:relative;height:28px;padding:0 12px;border-radius:8px;background:var(--glass0);font-size:12px;color:var(--ink2)}.mpord009 .demo button::after{content:"";position:absolute;inset:-8px -2px}.mpord009 .demo button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:inset 0 0 0 1px var(--ink3)}`,
  html: () => `<div class="mpord009"><div class="card"><div class="cashier"><div class="hd"><div class="shop">示例品牌旗舰店</div><span class="price"><small>¥</small><b>628.00</b></span><div class="cdt">支付剩余时间 <b data-ix="count" data-sec="899">00:14:59</b></div></div>
<p class="err" hidden>${sv('alert')}<span>支付未完成：银行卡账户余额不足。请更换支付方式，或稍后重试。</span></p>
<div data-ix="radio" class="pms">${[['mt_bubbles', '微信支付', '推荐'], ['mt_yen', '支付宝', ''], ['mt_card', '工商银行储蓄卡（3069）', '']].map((m, i) => `<div class="pm ${i === 0 ? 'on' : ''}" data-o data-v="${m[1]}" role="radio"><span class="ic">${sv(m[0])}</span><div class="tx">${m[1]}${m[2] ? `<small>${m[2]}</small>` : ''}</div><i class="rdo"></i></div>`).join('')}</div>
<div class="ft"><button type="button" class="btn btn-p" data-go>确认支付 ¥628.00</button></div></div>
<div class="done" hidden><div class="okc">${sv('check')}</div><h3>支付成功</h3><div class="amt">¥628.00</div><dl><div><dt>订单编号</dt><dd>SO2026110400128</dd></div><div><dt>支付方式</dt><dd class="how">微信支付</dd></div><div><dt>预计送达</dt><dd>11-05 前</dd></div></dl><div class="acts"><button type="button" class="btn line" data-toast="返回首页">返回首页</button><button type="button" class="btn btn-p" data-toast="查看订单详情">查看订单</button></div><button type="button" class="re" data-reset>重新演示</button></div></div>
<div class="demo" data-ix="radio"><span>模拟支付结果</span><button type="button" class="on" data-o data-r="ok">成功</button><button type="button" data-o data-r="fail">失败</button></div></div>`,
  js: (root) => {
    const go = $(root, '[data-go]'), err = $(root, '.err'), cash = $(root, '.cashier'), done = $(root, '.done')
    tap(root, '[data-go]', () => {
      if (go.classList.contains('busy')) return
      go.classList.add('busy'); err.hidden = true; go.innerHTML = '<span class="spin"></span>支付中…'
      setTimeout(() => {
        go.classList.remove('busy')
        if ($(root, '.demo .on').dataset.r === 'fail') { err.hidden = false; go.textContent = '重新支付 ¥628.00'; return }
        $(root, '.how').textContent = $(root, '.pms .on').dataset.v; cash.hidden = true; done.hidden = false
      }, 1100)
    })
    tap(root, '[data-reset]', () => { done.hidden = true; cash.hidden = false; go.textContent = '确认支付 ¥628.00' })
  },
})

/* ---- 010 订单状态步骤条 ---- */
const STEPS = [['receipt', '已下单', '11-04 09:12'], ['wallet', '已付款', '11-04 09:14'], ['truck', '配送中', '11-04 14:20'], ['box', '已签收', '预计 11-05']]
const STEP_TXT = [['订单已提交', '请在 29 分钟内完成支付，超时订单将自动取消。'], ['已付款，等待商家发货', '商家正在备货，预计今天内发出。'], ['商家已发货，正在配送', '包裹由顺丰速运配送，预计明天（11-05）送达。'], ['已签收，感谢你的购买', '商品有问题可在 7 天内申请售后，评价还能领积分。']]
defx({
  id: 'MP-ORD-010', name: '订单状态步骤条', style: '四段+说明',
  fit: '订单详情页顶部：用四个节点说明订单走到哪一步，当前节点高亮、已完成节点连线，上方一句话告诉用户下一步会发生什么',
  avoid: '节点超过 5 个（改用时间线）；已取消、已退款这类分支状态不要硬塞进同一条步骤，另用状态横幅',
  kw: 'steps 订单状态 步骤条 进度 订单详情 已下单 已付款 配送中 已签收 状态说明',
  css: `.mpord010{width:358px;max-width:100%;background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh06)}
.mpord010 .hero{padding:18px 16px 16px;background:linear-gradient(180deg,var(--pt),var(--card))}.mpord010 .hero h3{margin:0;font-size:18px;font-weight:600;line-height:26px}.mpord010 .hero p{margin:4px 0 0;font-size:14px;line-height:22px;color:var(--ink2)}
.mpord010 .trk{display:flex;padding:8px 8px 14px}
.mpord010 .sp{position:relative;flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;text-align:center}
.mpord010 .sp::before{content:"";position:absolute;top:17px;left:calc(-50% + 24px);right:calc(50% + 24px);height:2px;border-radius:1px;background:var(--n6);transition:background .25s}
.mpord010 .sp:first-child::before{display:none}.mpord010 .sp.done::before,.mpord010 .sp.on::before{background:var(--p)}
.mpord010 .dt{position:relative;z-index:1;width:36px;height:36px;border-radius:50%;background:var(--soft);color:var(--ink5);display:flex;align-items:center;justify-content:center;transition:background .25s,color .25s,box-shadow .25s}.mpord010 .dt svg{width:18px;height:18px}
.mpord010 .sp.done .dt{background:var(--pt);color:var(--p-text)}.mpord010 .sp.on .dt{background:var(--p);color:#fff;box-shadow:0 0 0 4px var(--pt)}
.mpord010 .sp b{margin-top:8px;font-size:14px;font-weight:400;color:var(--ink3)}.mpord010 .sp.on b,.mpord010 .sp.done b{color:var(--ink);font-weight:600}.mpord010 .sp span{margin-top:2px;font-size:12px;color:var(--ink3)}
.mpord010 .ctl{display:flex;align-items:center;justify-content:center;gap:16px;padding:10px 16px 14px;border-top:1px solid var(--line);font-size:12px;color:var(--ink3)}
.mpord010 .ctl button{position:relative;font-size:12px;color:var(--p-text);font-weight:600}.mpord010 .ctl button::after{content:"";position:absolute;inset:-14px -8px}.mpord010 .ctl button:disabled{color:var(--ink6);cursor:not-allowed}`,
  html: () => `<div class="mpord010" data-ix="steps"><div class="hero">${STEP_TXT.map((t) => `<div data-s hidden><h3>${t[0]}</h3><p>${t[1]}</p></div>`).join('')}</div><div class="trk">${STEPS.map((s, i) => `<div class="sp ${i === 2 ? 'on' : ''}"><i class="dt">${sv(s[0])}</i><b>${s[1]}</b><span>${s[2]}</span></div>`).join('')}</div><div class="ctl"><span>示例切换</span><button type="button" data-d="-1">‹ 上一状态</button><button type="button" data-d="1">下一状态 ›</button></div></div>`,
})

/* ---- 011 物流时间线 ---- */
const TL = [
  ['派送中', '今天 08:42', '朝阳区望京营业部的快递员王师傅（138****0031）正在为你派送，请保持电话畅通。', 1],
  ['已到达', '今天 06:15', '快件已到达【北京朝阳望京营业部】。'],
  ['运输中', '今天 02:30', '快件已离开【北京转运中心】，发往【北京朝阳望京营业部】。'],
  ['已到达', '11-03 21:10', '快件已到达【北京转运中心】。'],
  ['运输中', '11-03 11:20', '快件已离开【东莞转运中心】，发往【北京转运中心】。'],
  ['已揽收', '11-02 18:05', '【东莞黄江营业点】的快递员已揽收。'],
  ['已发货', '11-02 16:40', '商家已发货，包裹已出库，等待快递揽收。'],
]
const tlNode = (n, i, last) => `<div class="nd ${i === 0 ? 'now' : ''} ${last ? 'last' : ''}"><i class="pt"></i><div class="hd2"><b>${n[0]}</b><span>${n[1]}</span></div><p>${n[2]}</p>${n[3] ? `<button type="button" class="call" data-toast="拨打快递员电话">${sv('phone')}联系快递员</button>` : ''}</div>`
defx({
  id: 'MP-ORD-011', name: '物流时间线', style: '最新高亮+折叠',
  fit: '订单详情的物流跟踪：顶部是承运商与运单号（可复制），下面按时间倒序，最新一站高亮，较早的折叠起来',
  avoid: '把所有节点平铺（订单一长页面就没法看）；最新节点没有预计送达时间或联系方式',
  kw: 'logistics 物流 时间线 快递 运单号 派送 跟踪 timeline 复制单号 联系快递员',
  css: `.mpord011{width:358px;max-width:100%;background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh06)}
.mpord011 .hd{display:flex;align-items:center;gap:12px;padding:16px}
.mpord011 .hd .ic{flex:none;width:40px;height:40px;border-radius:12px;background:var(--pt);color:var(--p-text);display:flex;align-items:center;justify-content:center}.mpord011 .hd .ic svg{width:22px;height:22px}
.mpord011 .hd .tx{flex:1;min-width:0}.mpord011 .hd b{display:block;font-size:16px;font-weight:600}.mpord011 .hd span{display:block;margin-top:2px;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
.mpord011 .hd .cp{position:relative;display:inline-flex;align-items:center;gap:4px;height:28px;padding:0 10px;border-radius:8px;background:var(--n3);font-size:12px;color:var(--ink2)}.mpord011 .hd .cp::after{content:"";position:absolute;inset:-8px -2px}.mpord011 .hd .cp svg{width:14px;height:14px}
.mpord011 .sm{margin:0 16px;padding:10px 12px;border-radius:12px;background:var(--pt);font-size:14px;color:var(--p-text);font-weight:600}.mpord011 .sm small{font-weight:400;color:var(--ink2);font-size:12px;margin-left:6px}
.mpord011 .tlc{padding:16px 16px 4px}
.mpord011 .nd{position:relative;padding:0 0 18px 24px}
.mpord011 .nd::before{content:"";position:absolute;left:4px;top:18px;bottom:-2px;width:2px;background:var(--n6)}.mpord011 .nd.last::before{display:none}
.mpord011 .pt{position:absolute;left:0;top:5px;width:10px;height:10px;border-radius:50%;background:var(--n9)}
.mpord011 .nd.now .pt{top:4px;width:12px;height:12px;left:-1px;background:var(--p);box-shadow:0 0 0 4px var(--pm)}
.mpord011 .hd2{display:flex;align-items:baseline;justify-content:space-between;gap:8px}.mpord011 .hd2 b{font-size:14px;font-weight:600;color:var(--ink2)}.mpord011 .hd2 span{font-size:12px;color:var(--ink3)}
.mpord011 .nd.now .hd2 b{font-size:16px;color:var(--p-text)}
.mpord011 .nd p{margin:4px 0 0;font-size:12px;line-height:20px;color:var(--ink3)}.mpord011 .nd.now p{font-size:14px;line-height:22px;color:var(--ink)}
.mpord011 .call{position:relative;display:inline-flex;align-items:center;gap:4px;margin-top:8px;height:32px;padding:0 12px;border-radius:16px;background:var(--pt);color:var(--p-text);font-size:12px;font-weight:600}.mpord011 .call::after{content:"";position:absolute;inset:-6px -2px}.mpord011 .call svg{width:14px;height:14px}
.mpord011 .mr{display:flex;align-items:center;justify-content:center;gap:4px;width:100%;height:44px;border-top:1px solid var(--line);font-size:12px;color:var(--ink2)}.mpord011 .mr svg{width:14px;height:14px;transition:transform .25s cubic-bezier(.2,0,0,1)}.mpord011 .mr.open svg{transform:rotate(180deg)}.mpord011 .tlc.collapsed>.nd:nth-child(3)::before{display:none}`,
  html: () => `<div class="mpord011"><div class="hd"><span class="ic">${sv('truck')}</span><div class="tx"><b>顺丰速运</b><span>运单号 SF1360482174821</span></div><button type="button" class="cp" data-copy>${sv('copy')}复制</button></div>
<div class="sm">派送中<small>预计今天 18:00 前送达</small></div>
<div class="tlc collapsed">${TL.slice(0, 3).map((n, i) => tlNode(n, i, false)).join('')}<div class="ix-ai"><div class="ix-ab"><div>${TL.slice(3).map((n, i) => tlNode(n, i + 3, i === TL.length - 4)).join('')}</div></div></div></div>
<button type="button" class="mr" data-more><span data-lb>查看更多物流信息（${TL.length - 3}）</span>${sv('down')}</button></div>`,
  js: (root) => {
    tap(root, '[data-copy]', () => { try { navigator.clipboard && navigator.clipboard.writeText('SF1360482174821').catch(() => {}) } catch (e) {} tt(root, '已复制运单号') })
    tap(root, '[data-more]', (b) => { const ai = $(root, '.tlc .ix-ai'), o = ai.classList.toggle('open'); b.classList.toggle('open', o); $(root, '.tlc').classList.toggle('collapsed', !o); $(b, '[data-lb]').textContent = o ? '收起' : `查看更多物流信息（${TL.length - 3}）` })
  },
})

/* ---- 012 订单卡（状态按钮） ---- */
const OST = {
  pay: { t: '待付款', c: 'var(--warn)', note: '<b data-ix="count" data-sec="1788">00:29:48</b> 后自动取消', sum: '需付款', btns: [['取消订单', 'cancel', 'line'], ['去支付', 'pay', 'p']] },
  ship: { t: '待发货', c: 'var(--p-text)', note: '商家备货中，预计 11-06 前发货', sum: '实付款', btns: [['申请退款', 'refund', 'line'], ['提醒发货', 'remind', 'p']] },
  recv: { t: '待收货', c: 'var(--p-text)', note: '快递派送中，预计明天送达', sum: '实付款', btns: [['查看物流', 'track', 'line'], ['确认收货', 'recv', 'p']] },
  done: { t: '已完成', c: 'var(--ok)', note: '已于 11-02 签收，7 天内可申请售后', sum: '实付款', btns: [['删除订单', 'del', 'line'], ['再次购买', 'again', 'line'], ['评价', 'rate', 'p']] },
  cancel: { t: '已取消', c: 'var(--ink3)', note: '超时未支付，订单已自动关闭', sum: '订单金额', btns: [['删除订单', 'del', 'line'], ['重新购买', 'again', 'p']] },
}
const ocCard = (k) => {
  const s = OST[k]
  return `<div class="oh"><span class="sh">${sv('mt_store')}示例品牌旗舰店${sv('chev')}</span><b style="color:${s.c}">${s.t}</b></div>
<div class="oi"><div class="pimg"><img src="${P(0)}" alt=""></div><div class="tx"><div class="nm">${G.ear.n}</div><div class="sp2">${G.ear.sp}</div></div><div class="pq"><span class="price"><small>¥</small><b>699</b></span>×1</div></div>
<p class="note">${s.note}</p>
<div class="of"><span class="tl2">共 2 件，${s.sum}<span class="price"><small>¥</small><b>628.00</b></span></span></div>
<div class="oa">${s.btns.map((b) => `<button type="button" class="btn btn-sm ${b[2] === 'p' ? 'btn-p' : 'line'}" data-a="${b[1]}">${b[0]}</button>`).join('')}</div>`
}
defx({
  id: 'MP-ORD-012', name: '订单卡', style: '按状态变按钮',
  fit: '订单列表与订单详情的单张订单卡：状态文字、提示行、操作按钮都随订单状态变化，一张卡只有一个主按钮，其余线框',
  avoid: '同一状态下放超过三个按钮；破坏性操作（取消、删除）做成主按钮；状态变化后不更新提示行',
  kw: 'order card 订单卡 订单状态 待付款 待发货 待收货 已完成 已取消 操作按钮',
  css: `.mpord012{width:358px;max-width:100%}
${SMALL_BTN('mpord012')}
.mpord012 .demo{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:10px;font-size:12px;color:var(--ink3)}
.mpord012 .demo button{position:relative;height:28px;padding:0 10px;border-radius:8px;background:var(--glass0);font-size:12px;color:var(--ink2)}.mpord012 .demo button::after{content:"";position:absolute;inset:-8px -2px}.mpord012 .demo button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:inset 0 0 0 1px var(--ink3)}
.mpord012 .oc{background:var(--card);border-radius:16px;padding:14px 16px;box-shadow:0 4px 16px var(--sh06)}
.mpord012 .oh{display:flex;align-items:center;justify-content:space-between;font-size:14px}.mpord012 .oh .sh{display:inline-flex;align-items:center;gap:6px;font-weight:600}.mpord012 .oh .sh svg{width:18px;height:18px}.mpord012 .oh .sh svg:last-child{width:14px;height:14px;color:var(--ink3)}.mpord012 .oh b{font-weight:600}
.mpord012 .oi{display:flex;gap:12px;margin-top:12px}.mpord012 .oi .pimg{width:72px;height:72px;border-radius:12px;overflow:hidden;flex:none;background:var(--ph)}.mpord012 .oi .pimg img{width:100%;height:100%;object-fit:cover}
.mpord012 .oi .tx{flex:1;min-width:0}.mpord012 .oi .nm{font-size:14px;line-height:20px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.mpord012 .oi .sp2{margin-top:2px;font-size:12px;color:var(--ink3)}
.mpord012 .oi .pq{flex:none;text-align:right;font-size:12px;color:var(--ink3)}.mpord012 .oi .price{display:block;margin-bottom:4px}.mpord012 .oi .price b{font-size:16px}
.mpord012 .note{margin:12px 0 0;padding:8px 10px;border-radius:8px;background:var(--n2);font-size:12px;line-height:20px;color:var(--ink2)}.mpord012 .note b{font-weight:600;color:var(--warn);font-variant-numeric:tabular-nums}
.mpord012 .of{display:flex;justify-content:flex-end;margin-top:12px;font-size:12px;color:var(--ink2)}.mpord012 .tl2{display:inline-flex;align-items:baseline;gap:4px}.mpord012 .tl2 .price b{font-size:18px}
.mpord012 .oa{display:flex;justify-content:flex-end;gap:10px;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}
.mpord012 .gone{display:flex;flex-direction:column;align-items:center;gap:4px;padding:22px 0;font-size:14px;color:var(--ink3)}.mpord012 .gone button{position:relative;color:var(--p-text);font-weight:600}.mpord012 .gone button::after{content:"";position:absolute;inset:-14px -12px}
.mpord012 .oc.chg{animation:mpord012c .3s cubic-bezier(.2,0,0,1)}@keyframes mpord012c{from{opacity:.4;transform:translateY(4px)}}`,
  html: () => `<div class="mpord012"><div class="demo" data-ix="tabs"><span>示例状态</span>${Object.entries(OST).map(([k, s], i) => `<button type="button" data-t="${k}" class="${i ? '' : 'on'}">${s.t}</button>`).join('')}</div><div class="oc">${ocCard('pay')}</div></div>`,
  js: (root) => {
    const oc = $(root, '.oc'); let cur = 'pay'
    const render = (k, anim) => { cur = k; oc.innerHTML = ocCard(k); IX.init(oc); $$(root, '.demo [data-t]').forEach((x) => x.classList.toggle('on', x.dataset.t === k)); if (anim) { oc.classList.remove('chg'); void oc.offsetWidth; oc.classList.add('chg') } }
    tap(root, '.demo [data-t]', (b) => render(b.dataset.t, true))
    const say = { pay: '正在拉起收银台…', refund: '进入退款申请', remind: '已提醒商家尽快发货', track: '查看物流', again: '已加入购物车', rate: '去评价' }
    tap(root, '[data-a]', (b) => {
      const a = b.dataset.a
      if (a === 'cancel') { render('cancel', true); tt(root, '订单已取消'); return }
      if (a === 'recv') { render('done', true); tt(root, '已确认收货'); return }
      if (a === 'del') { oc.innerHTML = `<div class="gone"><span>订单已删除</span><button type="button" data-undo>撤销</button></div>`; return }
      tt(root, say[a])
    })
    tap(root, '[data-undo]', () => render(cur, true))
    IX.init(oc)
  },
})

/* ---- 013 订单状态标签列表 ---- */
const OL2 = [
  { k: 'pay', t: '待付款', c: 'var(--warn)', its: [G.ear, G.mug, G.tote], n: 4, tot: '927.00', btns: [['取消订单', 'line'], ['去支付', 'p']], note: '29 分钟后自动取消' },
  { k: 'ship', t: '待发货', c: 'var(--p-text)', its: [G.lamp], n: 1, tot: '219.00', btns: [['申请退款', 'line'], ['提醒发货', 'p']] },
  { k: 'recv', t: '待收货', c: 'var(--p-text)', its: [G.shoe], n: 1, tot: '329.00', btns: [['查看物流', 'line'], ['确认收货', 'p']] },
  { k: 'rate', t: '待评价', c: 'var(--ok)', its: [G.watch], n: 1, tot: '899.00', btns: [['删除订单', 'line'], ['再次购买', 'line'], ['评价', 'p']] },
]
const olCard = (o) => `<div class="oc" data-k="${o.k}"><div class="oh"><span class="sh">${sv('mt_store')}示例品牌旗舰店${sv('chev')}</span><b style="color:${o.c}">${o.t}</b></div>${o.its.length === 1 ? `<div class="oi"><div class="pimg"><img src="${P(o.its[0].i)}" alt=""></div><div class="tx"><div class="nm">${o.its[0].n}</div><div class="sp2">${o.its[0].sp}</div></div><div class="pq"><span class="price"><small>¥</small><b>${o.its[0].p}</b></span>×1</div></div>` : `<div class="oi th">${o.its.map((g) => `<div class="pimg"><img src="${P(g.i)}" alt=""></div>`).join('')}<span class="nn">共 ${o.n} 件</span></div>`}${o.note ? `<p class="note">${o.note}</p>` : ''}<div class="of">实付款<span class="price"><small>¥</small><b>${o.tot}</b></span></div><div class="oa">${o.btns.map((b) => `<button type="button" class="btn btn-sm ${b[1] === 'p' ? 'btn-p' : 'line'}" data-toast="${b[0]}">${b[0]}</button>`).join('')}</div></div>`
defx({
  id: 'MP-ORD-013', name: '订单状态标签列表', style: '标签筛选+空态',
  fit: '“我的订单”页：顶部状态标签（带待处理数量）点击过滤列表，每张订单卡按状态给按钮；没有该状态订单时显示空态',
  avoid: '标签超过 6 个又不能横滑；过滤后列表为空却不提示；多商品订单把每件都展开（用缩略图条加“共 N 件”）',
  kw: 'order list 订单列表 状态标签 筛选 待付款 待发货 待收货 待评价 售后',
  css: `.mpord013{width:358px;max-width:100%;background:var(--bg);border-radius:16px;overflow:hidden;box-shadow:0 4px 16px var(--sh08)}
${SMALL_BTN('mpord013')}
.mpord013 .tbs{position:relative;display:flex;overflow-x:auto;scrollbar-width:none;background:var(--card);box-shadow:inset 0 -1px 0 var(--line)}.mpord013 .tbs::-webkit-scrollbar{display:none}
.mpord013 .tbs button{position:relative;flex:none;height:48px;padding:0 18px;font-size:14px;color:var(--ink2);transition:color .2s}.mpord013 .tbs button.on{color:var(--ink);font-weight:600}
.mpord013 .tbs .bdg{position:absolute;right:-4px;top:3px;min-width:16px;height:16px;padding:0 4px;border-radius:8px;background:var(--pd);color:#fff;font-size:12px;font-weight:600;line-height:16px;text-align:center}
.mpord013 .tbs .ink{position:absolute;bottom:0;left:0;width:0;height:3px;border-radius:2px;background:var(--p);transition:left .25s cubic-bezier(.2,0,0,1),width .25s cubic-bezier(.2,0,0,1)}
.mpord013 .ol{display:flex;flex-direction:column;gap:10px;padding:10px 12px 0}
.mpord013 .oc{background:var(--card);border-radius:12px;padding:12px 14px}
.mpord013 .oh{display:flex;align-items:center;justify-content:space-between;font-size:14px}.mpord013 .oh .sh{display:inline-flex;align-items:center;gap:6px;font-weight:600}.mpord013 .oh .sh svg{width:16px;height:16px}.mpord013 .oh .sh svg:last-child{width:12px;height:12px;color:var(--ink3)}.mpord013 .oh b{font-weight:600;font-size:14px}
.mpord013 .oi{display:flex;gap:12px;margin-top:10px}.mpord013 .oi .pimg{width:64px;height:64px;border-radius:8px;overflow:hidden;flex:none;background:var(--ph)}.mpord013 .oi .pimg img{width:100%;height:100%;object-fit:cover}
.mpord013 .oi .tx{flex:1;min-width:0}.mpord013 .oi .nm{font-size:14px;line-height:20px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.mpord013 .oi .sp2{margin-top:2px;font-size:12px;color:var(--ink3)}
.mpord013 .oi .pq{flex:none;text-align:right;font-size:12px;color:var(--ink3)}.mpord013 .oi .price{display:block;margin-bottom:4px}.mpord013 .oi .price b{font-size:16px}
.mpord013 .oi.th{align-items:center;gap:8px}.mpord013 .oi.th .nn{margin-left:auto;font-size:12px;color:var(--ink3);white-space:nowrap}
.mpord013 .note{margin:8px 0 0;font-size:12px;color:var(--warn)}
.mpord013 .of{display:flex;align-items:baseline;justify-content:flex-end;gap:4px;margin-top:8px;font-size:12px;color:var(--ink2)}.mpord013 .of .price b{font-size:16px}
.mpord013 .oa{display:flex;justify-content:flex-end;gap:8px;margin-top:10px}
.mpord013 .nodata{padding:6px 0 4px}${MT0('mpord013')}
.mpord013 .endt{padding:14px 0 16px;text-align:center;font-size:12px;color:var(--ink3)}`,
  html: () => `<div class="mpord013"><div class="tbs" data-ix="tabs" data-list=".ol">${[['all', '全部', 0], ['pay', '待付款', 1], ['ship', '待发货', 1], ['recv', '待收货', 1], ['rate', '待评价', 1], ['after', '退款/售后', 0]].map((t, i) => `<button type="button" data-t="${t[0]}" class="${i ? '' : 'on'}">${t[1]}${t[2] ? `<i class="bdg">${t[2]}</i>` : ''}</button>`).join('')}<i class="ink"></i></div>
<div class="ol">${OL2.map(olCard).join('')}</div><div class="nodata" hidden>${emptyTile('bag', '暂无相关订单', '去商城逛逛，下单后会显示在这里')}</div><div class="endt">没有更多了</div></div>`,
  js: (root) => {
    const cards = $$(root, '.oc'), nd = $(root, '.nodata'), endt = $(root, '.endt')
    tapAfter(root, '.tbs [data-t]', () => { const any = cards.some((c) => !c.hidden); nd.hidden = any; endt.hidden = !any })
  },
})

/* ---- 014 售后申请表 ---- */
const REASONS = ['拍错了 / 不想要了', '商品质量问题', '与描述不符', '少件 / 漏发', '收到商品破损', '其他原因']
const FORM_BASE = (c) => `.${c} h4{margin:16px 0 8px;font-size:14px;font-weight:600}.${c} h4 i{color:var(--danger);margin-left:2px}.${c} h4 small{font-weight:400;font-size:12px;color:var(--ink3);margin-left:6px}
.${c} .pd{display:flex;align-items:center;gap:12px}.${c} .pd .pimg{width:64px;height:64px;border-radius:12px;overflow:hidden;flex:none;background:var(--ph)}.${c} .pd .pimg img{width:100%;height:100%;object-fit:cover}.${c} .pd .tx{flex:1;min-width:0}.${c} .pd .nm{font-size:14px;line-height:20px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.${c} .pd .sp2{margin-top:2px;font-size:12px;color:var(--ink3)}
.${c} .ta{position:relative}.${c} textarea{display:block;width:100%;height:84px;padding:10px 12px 24px;border-radius:12px;border:1px solid transparent;background:var(--n3);font:inherit;font-size:14px;line-height:22px;color:var(--ink);resize:none;outline:none}.${c} textarea::placeholder{color:var(--ink3)}.${c} textarea:focus{border-color:var(--ink2)}.${c} textarea.err{border-color:var(--danger)}.${c} .ta em{position:absolute;right:12px;bottom:8px;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
.${c} .ups{display:flex;flex-wrap:wrap;gap:10px;padding-top:6px}.${c} .addp{width:72px;height:72px;border-radius:10px;border:1.5px dashed var(--n9);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:12px;color:var(--ink3)}.${c} .addp svg{width:22px;height:22px}
.${c} .okp{padding:30px 16px 22px;text-align:center}.${c} .okp .okc{width:60px;height:60px;margin:0 auto;border-radius:50%;background:var(--ok-bg);color:var(--ok);display:flex;align-items:center;justify-content:center}.${c} .okp .okc svg{width:32px;height:32px}.${c} .okp h3{margin:14px 0 4px;font-size:18px;font-weight:600}.${c} .okp p{margin:0;font-size:14px;line-height:22px;color:var(--ink2)}.${c} .okp .acts{display:flex;gap:10px;margin-top:18px}.${c} .okp .acts .btn{flex:1;padding:0 8px}
.${c} .btn.line{background:var(--card);color:var(--ink2);box-shadow:inset 0 0 0 1px var(--n7)}.${c} .btn[aria-disabled=true]{background:var(--n6);color:var(--ink5);box-shadow:none}`
defx({
  id: 'MP-ORD-014', name: '售后申请表', style: '类型+原因+凭证',
  fit: '申请退款 / 退货 / 换货：先选服务类型与原因，再补充说明与上传凭证；没选原因不能提交，提交后给结果页',
  avoid: '把所有字段都设为必填（说明与图片可选）；提交按钮不说明为什么不可点（点按钮要提示缺哪一项）',
  kw: 'after-sales 售后 退款 退货 换货 申请 原因 上传 凭证 说明',
  css: `.mpord014{width:358px;max-width:100%;background:var(--card);border-radius:16px;box-shadow:0 4px 16px var(--sh06)}
${FORM_BASE('mpord014')}
.mpord014 .form{padding:16px}.mpord014 .form h4:first-of-type{margin-top:16px}
.mpord014 .types{display:flex;gap:8px}.mpord014 .ty{position:relative;flex:1;min-width:0;padding:10px 10px;border-radius:12px;background:var(--n3);text-align:left;transition:background .15s,box-shadow .15s}.mpord014 .ty b{display:block;font-size:14px;font-weight:600}.mpord014 .ty span{display:block;margin-top:2px;font-size:12px;line-height:18px;color:var(--ink3)}.mpord014 .ty.on{background:var(--pt);box-shadow:inset 0 0 0 1px var(--p)}.mpord014 .ty.on b{color:var(--p-text)}
.mpord014 .dd .pick{display:flex;align-items:center;justify-content:space-between;gap:8px;width:100%;height:44px;padding:0 14px;border-radius:12px;background:var(--n3);border:1px solid transparent;font-size:14px;text-align:left}.mpord014 .dd .pick .hold{color:var(--ink3)}.mpord014 .dd .pick svg{width:16px;height:16px;color:var(--ink3);flex:none;transition:transform .2s}.mpord014 .dd.open .pick svg{transform:rotate(180deg)}.mpord014 .dd.open .pick{border-color:var(--ink2)}.mpord014 .dd.err .pick{border-color:var(--danger)}
.mpord014 .dd .menu{padding:4px;border-radius:12px;background:var(--card2);box-shadow:0 10px 28px var(--sh16)}.mpord014 .dd .menu [data-o]{display:flex;align-items:center;height:44px;padding:0 10px;border-radius:8px;font-size:14px;cursor:pointer}.mpord014 .dd .menu [data-o].on{background:var(--pt);color:var(--p-text);font-weight:600}
.mpord014 .amtr{display:flex;align-items:baseline;gap:8px;margin-top:14px;padding:12px;border-radius:12px;background:var(--n2);font-size:14px;color:var(--ink2)}.mpord014 .amtr .price b{font-size:22px;font-weight:700}.mpord014 .amtr small{margin-left:auto;font-size:12px;color:var(--ink3)}
.mpord014 .sub{width:100%;margin-top:20px}`,
  html: () => `<div class="mpord014"><div class="form"><div class="pd"><div class="pimg"><img src="${P(0)}" alt=""></div><div class="tx"><div class="nm">${G.ear.n}</div><div class="sp2">${G.ear.sp} · ×1</div></div></div>
<h4>服务类型</h4><div class="types" data-ix="radio"><button type="button" class="ty on" data-o><b>仅退款</b><span>未收到货或协商一致</span></button><button type="button" class="ty" data-o><b>退货退款</b><span>已收到货，需寄回</span></button><button type="button" class="ty" data-o><b>换货</b><span>换同款或其他规格</span></button></div>
<h4>申请原因<i>*</i></h4><div class="dd" data-ix="dd"><button type="button" class="pick" data-tg><span class="hold" data-label>请选择申请原因</span>${sv('down')}</button><div class="menu">${REASONS.map((r) => `<div data-o>${r}</div>`).join('')}</div></div>
<div class="amtr"><span data-al>退款金额</span><span class="price" data-ap><small>¥</small><b>699.00</b></span><small data-an>最多可退 ¥699.00</small></div>
<h4>补充说明<small>选填</small></h4><div class="ta"><textarea maxlength="200" placeholder="请描述具体问题，便于商家更快处理"></textarea><em>0/200</em></div>
<h4>上传凭证<small>选填，最多 3 张</small></h4><div class="ups" data-ix="upload" data-max="3"><button type="button" class="addp" data-add>${sv('camera')}上传</button></div>
<button type="button" class="btn btn-p sub" aria-disabled="true" data-submit>提交申请</button></div>
<div class="okp" hidden><div class="okc">${sv('check')}</div><h3>申请已提交</h3><p>商家将在 48 小时内处理，处理结果会通过消息通知你。</p><div class="acts"><button type="button" class="btn line" data-reset>重新填写</button><button type="button" class="btn btn-p" data-toast="查看售后进度">查看进度</button></div></div></div>`,
  js: (root) => {
    const ta = $(root, 'textarea'), cnt = $(root, '.ta em'), sub = $(root, '[data-submit]'), dd = $(root, '.dd')
    const picked = () => $(root, '[data-label]').textContent !== '请选择申请原因'
    const sync = () => { sub.setAttribute('aria-disabled', !picked()) }
    ta.addEventListener('input', () => { cnt.textContent = ta.value.length + '/200' })
    tapAfter(root, '.dd [data-o]', () => { dd.classList.remove('err'); $(root, '[data-label]').classList.remove('hold'); sync() })
    tapAfter(root, '.ty', (t) => { const i = $$(root, '.ty').indexOf(t); $(root, '[data-al]').textContent = i === 2 ? '处理方式' : '退款金额'; $(root, '[data-ap]').hidden = i === 2; $(root, '[data-an]').textContent = i === 2 ? '无需退款，商家将重新发货' : '最多可退 ¥699.00' })
    tap(root, '[data-submit]', (b) => {
      if (b.getAttribute('aria-disabled') === 'true') { dd.classList.add('err'); tt(root, '请选择申请原因'); return }
      $(root, '.form').hidden = true; $(root, '.okp').hidden = false
    })
    tap(root, '[data-reset]', () => { $(root, '.okp').hidden = true; $(root, '.form').hidden = false; $(root, '[data-label]').textContent = '请选择申请原因'; $(root, '[data-label]').classList.add('hold'); ta.value = ''; cnt.textContent = '0/200'; sync() })
  },
})

/* ---- 015 评价提交 ---- */
const RTAGS = { pos: ['质量很好', '物流很快', '包装精美', '性价比高', '与描述一致', '客服热情'], mid: ['一般般', '有小瑕疵', '物流较慢', '包装一般'], neg: ['质量差', '与描述不符', '物流太慢', '客服态度差', '包装破损'] }
const RLAB = ['', '非常差', '差', '一般', '满意', '非常满意']
const starBtns = (n, cls) => [1, 2, 3, 4, 5].map((i) => `<button type="button" data-n="${i}" class="${i <= n ? 'on' : ''}" aria-label="${i} 星">${sv('starf')}</button>`).join('')
defx({
  id: 'MP-ORD-015', name: '评价提交', style: '星级+标签+图片',
  fit: '订单完成后写评价：星级决定标签（好评给正向标签、差评给问题标签），可补文字与图片、给物流和服务单独打分、匿名',
  avoid: '默认 0 星（用户不点就无法提交）；差评不引导说明原因；把“匿名”藏得很深',
  kw: 'review submit 评价 提交 星级 标签 图片 匿名 物流评分 服务评分',
  css: `.mpord015{width:358px;max-width:100%;background:var(--card);border-radius:16px;box-shadow:0 4px 16px var(--sh06)}
${FORM_BASE('mpord015')}${TGB('mpord015')}
.mpord015 .form{padding:16px}
.mpord015 .rt1{display:flex;align-items:center;gap:8px;margin-top:16px;padding:12px;border-radius:12px;background:var(--pt)}.mpord015 .rt1>span{font-size:14px;font-weight:600;white-space:nowrap}.mpord015 .rt1 b{margin-left:auto;font-size:14px;font-weight:600;color:var(--p-text);white-space:nowrap}.mpord015 .rt1 .st5 button{width:26px;height:26px}
.mpord015 .st5{display:inline-flex;gap:2px}.mpord015 .st5 button{position:relative;width:28px;height:28px;color:var(--off);transition:color .15s,transform .15s}.mpord015 .st5 button::after{content:"";position:absolute;inset:-8px -2px}.mpord015 .st5 button svg{width:100%;height:100%}.mpord015 .st5 button.on{color:#C9A15A}.mpord015 .st5 button:active{transform:scale(.9)}
.mpord015 .tgs{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.mpord015 .tgs button{position:relative;height:32px;padding:0 12px;border-radius:8px;background:var(--n3);font-size:14px;color:var(--ink);transition:background .15s,color .15s,box-shadow .15s}.mpord015 .tgs button::after{content:"";position:absolute;inset:-6px -2px}.mpord015 .tgs button.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1px var(--p)}
.mpord015 .ta{margin-top:12px}
.mpord015 .ups{padding-top:12px}
.mpord015 .mini{display:flex;flex-direction:column;gap:10px;margin-top:16px;padding-top:14px;border-top:1px solid var(--line)}.mpord015 .mini div{display:flex;align-items:center;justify-content:space-between;font-size:14px}.mpord015 .mini .st5 button{width:22px;height:22px}.mpord015 .mini .st5 button::after{inset:-10px -3px}
.mpord015 .mini .an small{display:block;font-size:12px;color:var(--ink3)}
.mpord015 .sub{width:100%;margin-top:18px}`,
  html: () => `<div class="mpord015"><div class="form"><div class="pd"><div class="pimg"><img src="${P(0)}" alt=""></div><div class="tx"><div class="nm">${G.ear.n}</div><div class="sp2">${G.ear.sp}</div></div></div>
<div class="rt1"><span>商品评价</span><div class="st5" data-ix="rate" data-main>${starBtns(5)}</div><b data-lab>${RLAB[5]}</b></div>
<div class="tgs" data-ix="multi" data-tags>${RTAGS.pos.map((t) => `<button type="button" data-o>${t}</button>`).join('')}</div>
<div class="ta"><textarea maxlength="200" placeholder="说说使用感受，帮助更多人选择"></textarea><em>0/200</em></div>
<div class="ups" data-ix="upload" data-max="5"><button type="button" class="addp" data-add>${sv('camera')}添加图片</button></div>
<div class="mini"><div><span>物流服务</span><div class="st5" data-ix="rate">${starBtns(5)}</div></div><div><span>服务态度</span><div class="st5" data-ix="rate">${starBtns(5)}</div></div><div class="an"><span>匿名评价<small>开启后昵称显示为“匿**名”</small></span><button type="button" class="tgb" data-ix="toggle" role="switch" aria-checked="false" aria-label="匿名评价"></button></div></div>
<button type="button" class="btn btn-p sub" data-submit>提交评价</button></div>
<div class="okp" hidden><div class="okc">${sv('check')}</div><h3>评价成功</h3><p>感谢你的反馈，已获得 20 积分。</p><div class="acts"><button type="button" class="btn line" data-reset>再写一条</button><button type="button" class="btn btn-p" data-toast="查看我的评价">查看评价</button></div></div></div>`,
  js: (root) => {
    const ta = $(root, 'textarea'), cnt = $(root, '.ta em'), tags = $(root, '[data-tags]'), main = $(root, '[data-main]')
    const lvl = () => $$(main, '.on').length
    ta.addEventListener('input', () => { ta.classList.remove('err'); cnt.textContent = ta.value.length + '/200' })
    tapAfter(root, '[data-main] [data-n]', () => {
      const n = lvl(), set = n >= 4 ? 'pos' : n === 3 ? 'mid' : 'neg'
      $(root, '[data-lab]').textContent = RLAB[n]; tags.innerHTML = RTAGS[set].map((t) => `<button type="button" data-o>${t}</button>`).join('')
      ta.placeholder = n <= 2 ? '请说明遇到的问题，商家会尽快联系你' : '说说使用感受，帮助更多人选择'
    })
    tap(root, '[data-submit]', () => {
      if (lvl() <= 2 && ta.value.trim().length < 5) { ta.classList.add('err'); tt(root, '低分评价请至少写 5 个字说明原因'); return }
      $(root, '.form').hidden = true; $(root, '.okp').hidden = false
    })
    tap(root, '[data-reset]', () => { $(root, '.okp').hidden = true; $(root, '.form').hidden = false })
  },
})

/* ---- 016 发票信息 ---- */
defx({
  id: 'MP-ORD-016', name: '发票信息', style: '按需出现字段',
  fit: '确认订单页的“发票”入口进来：先选发票类型，再按个人 / 企业出现抬头与税号，保存前逐项校验并在字段下写原因',
  avoid: '一上来就展示全部字段（多数人不开票）；专用发票允许选个人抬头；校验失败只弹一个总提示',
  kw: 'invoice 发票 抬头 税号 个人 企业 增值税 电子发票 邮箱 开票',
  css: `.mpord016{width:358px;max-width:100%;background:var(--card);border-radius:16px;box-shadow:0 4px 16px var(--sh06)}
.mpord016 .form{padding:16px}.mpord016 h4{margin:16px 0 8px;font-size:14px;font-weight:600}.mpord016 .form>h4:first-child{margin-top:0}
.mpord016 .g2{display:flex;flex-wrap:wrap;gap:8px}.mpord016 .g2 button{position:relative;height:36px;padding:0 14px;border-radius:8px;background:var(--n3);font-size:14px;color:var(--ink);transition:background .15s,color .15s,box-shadow .15s}.mpord016 .g2 button::after{content:"";position:absolute;inset:-4px -2px}.mpord016 .g2 button.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1px var(--p)}.mpord016 .g2 button.off{color:var(--ink5);cursor:not-allowed}
.mpord016 .fld{margin-top:12px}.mpord016 .fld label{display:block;margin-bottom:6px;font-size:12px;color:var(--ink3)}.mpord016 .fld label i{color:var(--danger);margin-left:2px}
.mpord016 .fld input{display:block;width:100%;height:44px;padding:0 12px;border-radius:12px;border:1px solid transparent;background:var(--n3);font:inherit;font-size:14px;color:var(--ink);outline:none}.mpord016 .fld input::placeholder{color:var(--ink3)}.mpord016 .fld input:focus{border-color:var(--ink2)}.mpord016 .fld input.err{border-color:var(--danger)}
.mpord016 .er{display:block;margin-top:4px;font-size:12px;color:var(--danger)}
.mpord016 .nt{margin:12px 0 0;font-size:12px;line-height:20px;color:var(--ink3)}
.mpord016 .sub{width:100%;margin-top:18px}
.mpord016 .sum{display:flex;align-items:center;gap:12px;padding:16px}.mpord016 .sum .ic{flex:none;width:40px;height:40px;border-radius:12px;background:var(--ok-bg);color:var(--ok);display:flex;align-items:center;justify-content:center}.mpord016 .sum .ic svg{width:22px;height:22px}.mpord016 .sum .tx{flex:1;min-width:0;font-size:14px;line-height:22px}.mpord016 .sum .tx b{display:block;font-weight:600}.mpord016 .sum .tx span{display:block;font-size:12px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mpord016 .sum button{position:relative;font-size:14px;color:var(--p-text);font-weight:600}.mpord016 .sum button::after{content:"";position:absolute;inset:-12px -8px}`,
  html: () => `<div class="mpord016"><div class="form"><h4>发票类型</h4><div class="g2" data-ix="radio" data-g="type"><button type="button" data-o data-v="none">不开发票</button><button type="button" class="on" data-o data-v="e">电子普通发票</button><button type="button" data-o data-v="z">专用发票</button></div>
<div class="inv"><h4>抬头类型</h4><div class="g2" data-ix="radio" data-g="who"><button type="button" class="on" data-o data-v="p">个人 / 非企业</button><button type="button" data-o data-v="c">企业</button></div>
<div class="fld"><label for="mpord016a">发票抬头<i>*</i></label><input id="mpord016a" data-f="title" value="林小满" placeholder="请输入个人姓名"><span class="er" hidden></span></div>
<div class="fld" data-co hidden><label for="mpord016b">纳税人识别号<i>*</i></label><input id="mpord016b" data-f="tax" placeholder="15-20 位字母或数字" maxlength="20"><span class="er" hidden></span></div>
<div class="fld"><label for="mpord016c">接收邮箱<i>*</i></label><input id="mpord016c" data-f="mail" value="lin@example.com" placeholder="发票将发送到此邮箱"><span class="er" hidden></span></div>
<h4>发票内容</h4><div class="g2" data-ix="radio"><button type="button" class="on" data-o>商品明细</button><button type="button" data-o>商品类别</button></div><p class="nt">发票金额以实付金额为准，订单完成后 7 个工作日内开具。</p></div>
<button type="button" class="btn btn-p sub" data-save>保存</button></div>
<div class="sum" hidden><span class="ic">${sv('receipt')}</span><div class="tx"><b>发票信息已保存</b><span data-sd></span></div><button type="button" data-edit>修改</button></div></div>`,
  js: (root) => {
    const val = (k) => $(root, `[data-f=${k}]`), er = (k, m) => { const i = val(k), e = i.parentNode.querySelector('.er'); i.classList.toggle('err', !!m); e.hidden = !m; e.textContent = m || '' }
    const type = () => $(root, '[data-g=type] .on').dataset.v, who = () => $(root, '[data-g=who] .on').dataset.v
    const sync = () => {
      const t = type(), inv = $(root, '.inv')
      inv.hidden = t === 'none'
      const pb = $(root, '[data-g=who] [data-v=p]'), cb = $(root, '[data-g=who] [data-v=c]')
      pb.classList.toggle('off', t === 'z'); if (t === 'z' && who() === 'p') { pb.classList.remove('on'); cb.classList.add('on') }
      const co = who() === 'c'; $(root, '[data-co]').hidden = !co
      val('title').placeholder = co ? '请输入企业全称' : '请输入个人姓名'
      ;['title', 'tax', 'mail'].forEach((k) => er(k, ''))
    }
    let lastWho = 'p'
    tapAfter(root, '[data-g] [data-o]', (b) => {
      if (b.classList.contains('off')) return
      sync()
      if (who() !== lastWho) { lastWho = who(); val('title').value = who() === 'c' ? '' : '林小满' }
    })
    tap(root, '[data-g=who] [data-v=p]', (b, e) => { if (b.classList.contains('off')) { e.stopPropagation(); tt(root, '专用发票仅支持企业抬头') } })
    tap(root, '[data-save]', () => {
      const t = type(); if (t === 'none') { $(root, '.form').hidden = true; $(root, '.sum').hidden = false; $(root, '[data-sd]').textContent = '本单不开发票'; return }
      let ok = true; const c = who() === 'c'
      const title = val('title').value.trim(), tax = val('tax').value.trim(), mail = val('mail').value.trim()
      const e1 = !title ? '请填写发票抬头' : c && title.length < 4 ? '请填写企业全称（至少 4 个字）' : ''
      const e2 = c ? (!tax ? '请填写纳税人识别号' : /^[0-9A-Za-z]{15,20}$/.test(tax) ? '' : '纳税人识别号为 15-20 位字母或数字') : ''
      const e3 = !mail ? '请填写接收邮箱' : /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail) ? '' : '邮箱格式不正确'
      er('title', e1); er('tax', e2); er('mail', e3)
      if (e1 || e2 || e3) { tt(root, '请先修改标红的项目'); return }
      $(root, '.form').hidden = true; $(root, '.sum').hidden = false
      $(root, '[data-sd]').textContent = `${t === 'z' ? '增值税专用发票' : '电子普通发票'} · ${c ? '企业' : '个人'} · ${title}`
    })
    tap(root, '[data-edit]', () => { $(root, '.sum').hidden = true; $(root, '.form').hidden = false })
    sync()
  },
})

/* ---- 017 订单金额明细 ---- */
defx({
  id: 'MP-ORD-017', name: '订单金额明细', style: '逐项+积分开关',
  fit: '确认订单页与订单详情的金额拆解：商品总额、运费、各类优惠、积分抵扣（可开关），最后一行是实付款，并汇总“已优惠”',
  avoid: '优惠项不带负号与颜色区分；开关改了金额却不联动实付；把“已优惠”算进商品总额里',
  kw: 'price breakdown 金额明细 实付款 运费 优惠 满减 优惠券 积分抵扣 总额',
  css: `.mpord017{width:358px;max-width:100%;background:var(--card);border-radius:16px;padding:16px 16px 14px;box-shadow:0 4px 16px var(--sh06)}
${TGB('mpord017')}
.mpord017 h3{margin:0 0 6px;font-size:16px;font-weight:600}
.mpord017 .ln{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:44px;padding:4px 0;font-size:14px;color:var(--ink2)}.mpord017 .ln .v{color:var(--ink);font-variant-numeric:tabular-nums;white-space:nowrap}.mpord017 .ln .v .tg{margin-right:6px;vertical-align:1px}
.mpord017 .ln.neg .v{color:var(--price)}.mpord017 .ln small{display:block;font-size:12px;color:var(--ink3)}
.mpord017 .ln .rt{display:flex;align-items:center;gap:10px}.mpord017 .ln .rt b{font-weight:400;color:var(--ink3);font-variant-numeric:tabular-nums;white-space:nowrap}.mpord017 .ln .rt b.on{color:var(--price)}
.mpord017 .tot{display:flex;align-items:center;justify-content:space-between;margin-top:6px;padding-top:12px;border-top:1px dashed var(--n7);font-size:14px}.mpord017 .tot .sv{font-size:12px;color:var(--ink3)}.mpord017 .tot .sv b{font-size:12px;font-weight:600;color:var(--price)}
.mpord017 .tot .price{display:inline-flex;align-items:baseline;gap:1px}.mpord017 .tot .price b{font-size:22px;font-weight:700}`,
  html: () => `<div class="mpord017"><h3>金额明细</h3><div class="ln"><span>商品总额</span><span class="v">¥1,325.00</span></div><div class="ln"><span>运费</span><span class="v"><i class="tg tg-soft">满 ¥99 包邮</i>¥0.00</span></div><div class="ln neg"><span>店铺满减</span><span class="v">-¥30.00</span></div><div class="ln neg"><span>优惠券<small>店铺满减券</small></span><span class="v">-¥20.00</span></div><div class="ln"><span>积分抵扣<small>使用 2,000 积分，抵 ¥20</small></span><span class="rt"><b class="on" data-pv>-¥20.00</b><button type="button" class="tgb on" data-ix="toggle" role="switch" aria-checked="true" aria-label="积分抵扣"></button></span></div>
<div class="tot"><span class="sv">共优惠 <b data-sv>¥70.00</b></span><span>实付款 <span class="price"><small>¥</small><b data-pay>1,255.00</b></span></span></div></div>`,
  js: (root) => {
    const upd = () => {
      const on = $(root, '.tgb').classList.contains('on'), off = 30 + 20 + (on ? 20 : 0)
      $(root, '[data-pv]').textContent = on ? '-¥20.00' : '未使用'; $(root, '[data-pv]').classList.toggle('on', on)
      $(root, '[data-sv]').textContent = '¥' + yuan(off); $(root, '[data-pay]').textContent = yuan(1325 - off)
    }
    tapAfter(root, '.tgb', upd)
  },
})

/* ---- 018 提交订单栏 ---- */
defx({
  id: 'MP-ORD-018', name: '提交订单栏', style: '明细+提交态',
  fit: '确认订单页底部：件数与合计、点“已优惠”向上展开金额明细（带遮罩）、右侧“提交订单”，提交中禁用并保持宽度',
  avoid: '提交后不置灰按钮导致重复下单；明细弹层高度超过 80%；合计里不含运费却不说明',
  kw: 'submit order 提交订单 底栏 合计 已优惠 明细 弹层 遮罩 下单',
  css: `.mpord018{position:relative;width:358px;max-width:100%;height:420px;border-radius:16px;overflow:hidden;background:var(--bg);box-shadow:0 4px 16px var(--sh08)}
${LD('mpord018')}
.mpord018 .ctx{padding:12px;display:flex;flex-direction:column;gap:10px}.mpord018 .ctx div{background:var(--card);border-radius:12px;padding:14px}
.mpord018 .ctx i{display:block;height:10px;border-radius:5px;background:var(--n4)}.mpord018 .ctx i+i{margin-top:10px;width:60%}
.mpord018 .ctx .big{height:120px}
.mpord018 .ix-ov{z-index:30}.mpord018 .ix-mask{background:color-mix(in srgb,var(--scrim) 40%,transparent)}
.mpord018 .sheet{position:absolute;left:0;right:0;bottom:70px;max-height:80%;overflow:auto;padding:14px 16px 6px;border-radius:16px 16px 0 0;background:var(--card2);animation:mpord018u .25s cubic-bezier(.2,0,0,1)}@keyframes mpord018u{from{transform:translateY(24px);opacity:.5}}
.mpord018 .sheet h4{margin:0 0 4px;font-size:16px;font-weight:600}.mpord018 .sheet .ln{display:flex;justify-content:space-between;min-height:36px;align-items:center;font-size:14px;color:var(--ink2)}.mpord018 .sheet .ln b{font-weight:400;color:var(--ink);font-variant-numeric:tabular-nums}.mpord018 .sheet .ln.neg b{color:var(--price)}
.mpord018 .sbar{position:absolute;left:0;right:0;bottom:0;z-index:31;display:flex;align-items:center;gap:12px;height:70px;padding:0 12px 6px 16px;background:var(--card);box-shadow:0 -4px 16px var(--sh06)}
.mpord018 .sbar .tx{flex:1;min-width:0}.mpord018 .sbar .l1{display:flex;align-items:baseline;gap:4px;font-size:12px;color:var(--ink2)}.mpord018 .sbar .l1 .price{display:inline-flex;align-items:baseline;gap:1px}.mpord018 .sbar .l1 .price b{font-size:22px;font-weight:700}
.mpord018 .sbar .dtb{position:relative;display:inline-flex;align-items:center;gap:2px;margin-top:2px;font-size:12px;color:var(--ink3)}.mpord018 .sbar .dtb::after{content:"";position:absolute;inset:-12px -8px}.mpord018 .sbar .dtb svg{width:14px;height:14px;transition:transform .25s cubic-bezier(.2,0,0,1)}.mpord018 .sbar .dtb.open svg{transform:rotate(180deg)}.mpord018 .sbar .dtb b{color:var(--price);font-weight:600}
.mpord018 .sbar .btn{flex:none;min-width:128px;height:46px}.mpord018 .btn.busy{pointer-events:none}.mpord018 .btn .spin{margin-right:2px}`,
  html: () => `<div class="mpord018"><div class="ctx"><div><i></i><i></i></div><div class="big"><i></i><i></i></div><div><i></i></div></div>
<div class="ix-ov" data-ov="dt"><div class="ix-mask"></div><div class="sheet"><h4>金额明细</h4><div class="ln"><span>商品总额</span><b>¥1,325.00</b></div><div class="ln"><span>运费</span><b>¥0.00</b></div><div class="ln neg"><span>店铺满减</span><b>-¥30.00</b></div><div class="ln neg"><span>优惠券</span><b>-¥20.00</b></div><div class="ln neg"><span>积分抵扣</span><b>-¥20.00</b></div></div></div>
<div class="sbar"><div class="tx"><div class="l1">共 5 件，合计<span class="price"><small>¥</small><b>1,255.00</b></span></div><button type="button" class="dtb" data-dt>已优惠 <b>¥70.00</b>${sv('up')}</button></div><button type="button" class="btn btn-p" data-submit>提交订单</button></div></div>`,
  js: (root) => {
    const ov = $(root, '.ix-ov'), dt = $(root, '[data-dt]'), sub = $(root, '[data-submit]')
    const sync = () => dt.classList.toggle('open', ov.classList.contains('show'))
    tap(root, '[data-dt]', () => { ov.classList.toggle('show'); sync() })
    tapAfter(root, '.ix-mask', sync)
    tap(root, '[data-submit]', () => {
      if (sub.classList.contains('busy')) return
      ov.classList.remove('show'); sync()
      sub.classList.add('busy'); sub.innerHTML = '<span class="spin"></span>提交中'
      setTimeout(() => { sub.classList.remove('busy'); sub.textContent = '提交订单'; tt(root, '订单已提交，前往支付') }, 1000)
    })
  },
})

/* ---- 019 订单信息卡 ---- */
defx({
  id: 'MP-ORD-019', name: '订单信息卡', style: '可复制+展开',
  fit: '订单详情页底部的订单信息：编号可一键复制、下单与支付时间、支付与配送方式，次要字段（收货人、发票、留言）收进“更多”',
  avoid: '把订单编号做成图片或不可复制；全部字段平铺（详情页会过长）；时间不写到秒（售后对账要用）',
  kw: 'order info 订单信息 订单编号 复制 下单时间 支付方式 配送方式 订单详情 展开',
  css: `.mpord019{width:358px;max-width:100%;background:var(--card);border-radius:16px;padding:14px 16px 0;box-shadow:0 4px 16px var(--sh06)}
.mpord019 h3{margin:0 0 6px;font-size:16px;font-weight:600}
.mpord019 .kv{display:flex;gap:12px;align-items:flex-start;min-height:40px;padding:9px 0;font-size:14px;line-height:22px}.mpord019 .kv dt{flex:none;width:72px;color:var(--ink3)}.mpord019 .kv dd{margin:0;flex:1;min-width:0;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}
.mpord019 .kv .cp{position:relative;flex:none;height:24px;padding:0 8px;margin-left:8px;border-radius:5px;background:var(--pt);color:var(--p-text);font-size:12px;font-weight:600}.mpord019 .kv .cp::after{content:"";position:absolute;inset:-10px -4px}
.mpord019 .exp{display:flex;align-items:center;justify-content:center;gap:4px;width:100%;height:48px;border-top:1px solid var(--line);font-size:12px;color:var(--ink2)}.mpord019 .exp svg{width:14px;height:14px;transition:transform .25s cubic-bezier(.2,0,0,1)}.mpord019 .ix-ai.open .exp svg{transform:rotate(180deg)}`,
  html: () => `<div class="mpord019" data-ix="acc"><h3>订单信息</h3><dl style="margin:0"><div class="kv"><dt>订单编号</dt><dd>SO2026110400128<button type="button" class="cp" data-copy>复制</button></dd></div><div class="kv"><dt>下单时间</dt><dd>2026-11-04 09:12:36</dd></div><div class="kv"><dt>支付方式</dt><dd>微信支付（11-04 09:14:02）</dd></div><div class="kv"><dt>配送方式</dt><dd>快递配送 · 顺丰速运</dd></div></dl>
<div class="ix-ai"><div class="ix-ab"><div><dl style="margin:0"><div class="kv"><dt>收货信息</dt><dd>林小满 138****5206 北京市朝阳区望京街道阜通东大街 6 号院 3 号楼 1204 室（前台代收）</dd></div><div class="kv"><dt>发票</dt><dd>电子普通发票 · 林小满</dd></div><div class="kv"><dt>买家留言</dt><dd>送货前请先电话联系，谢谢</dd></div></dl></div></div><button type="button" class="exp" data-h><span data-lb>更多订单信息</span>${sv('down')}</button></div></div>`,
  js: (root) => {
    tap(root, '[data-copy]', () => { try { navigator.clipboard && navigator.clipboard.writeText('SO2026110400128').catch(() => {}) } catch (e) {} tt(root, '已复制订单编号') })
    tapAfter(root, '[data-h]', (h) => { $(h, '[data-lb]').textContent = h.closest('.ix-ai').classList.contains('open') ? '收起' : '更多订单信息' })
  },
})


})()
