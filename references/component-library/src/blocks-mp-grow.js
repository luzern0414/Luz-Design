/* ===== 小程序域：营销活动 MKT（006 起）· 会员与个人中心 MEM（001 起）· 服务与预约 SVC（001 起）=====
 * 全部包在一个函数里，不往全局放任何名字；图标名以 mg 开头。
 * CSS 里 & = 块根选择器，§ = 块根类名（用于 keyframes 名）。 */
;(() => {
  Object.assign(LINE, {
    mgcrown: '<path d="M5 20h14M4.5 17 3.5 8l5 4 3.5-6 3.5 6 5-4-1 9z"/>',
    mgcoin: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5v9M9.5 9.8h4a1.6 1.6 0 0 1 0 3.2h-3a1.6 1.6 0 0 0 0 3.2h4.2"/>',
    mgnav: '<path d="m4 11.5 16-7.5-7.5 16-2-6.5z"/>',
    mgsmile: '<circle cx="12" cy="12" r="8.5"/><path d="M9 14.8c1 1.2 2 1.7 3 1.7s2-.5 3-1.7M9 10h.01M15 10h.01"/>',
    mgstore: '<path d="M4 9.5 5.5 4h13L20 9.5M4 9.5a2.7 2.7 0 0 0 5.3 0 2.7 2.7 0 0 0 5.4 0 2.7 2.7 0 0 0 5.3 0M5.5 12.5V20h13v-7.5M10 20v-4.5h4V20"/>',
    mgcheckin: '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4M9 15l2 2 4-4"/>',
    mgmedal: '<circle cx="12" cy="9" r="5"/><path d="m9 13.5-1.5 7 4.5-2.5 4.5 2.5-1.5-7"/>',
    mgtimer: '<circle cx="12" cy="13.5" r="7"/><path d="M12 10v3.8l2.5 1.5M9.5 3.5h5"/>',
    mgbarcode: '<path d="M4 6v12M7 6v12M11 6v12M14 6v12M17 6v8M20 6v12"/>',
    mgbag: '<path d="M5 8h14l-1 12H6z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/><path d="M9.5 12.5a2.5 2.5 0 0 0 5 0"/>',
  })

  /* ---------- 共用小工具 ---------- */
  const cls = (id) => id.replace(/-/g, '').toLowerCase()
  const CSS = (id, s) => s.replace(/&/g, '.' + cls(id)).replace(/§/g, cls(id))
  const reduce = () => window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches
  const nf = (v) => Math.round(v).toLocaleString('en-US')
  const n2 = (v) => v.toFixed(2)
  const tween = (from, to, ms, fn, done) => {
    if (reduce() || ms <= 0) { fn(to); done && done(); return }
    const t0 = performance.now()
    const step = (t) => {
      const k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - k, 3)
      fn(from + (to - from) * e)
      if (k < 1) requestAnimationFrame(step); else { fn(to); done && done() }
    }
    requestAnimationFrame(step)
  }
  const later = (root, ms, fn) => setTimeout(() => { if (root.isConnected) fn() }, ms)

  /* 共用 CSS 片段（& 与 § 在 CSS() 里替换）*/
  const PB = `& .pb{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;height:44px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:16px;font-weight:600;box-shadow:0 5px 12px rgba(var(--p-rgb),.2);transition:transform .15s cubic-bezier(.2,0,0,1),background-color .2s}& .pb:active{transform:scale(.98)}& .pb:disabled{background:var(--n5);color:var(--ink3);box-shadow:none;cursor:default;transform:none}& .pb.ok{background:var(--pt);color:var(--p-text);box-shadow:none}& .pb.cx{background:var(--soft);color:var(--ink2);box-shadow:none}`
  const SB = `& .sb{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:4px;min-width:68px;height:32px;padding:0 14px;border-radius:16px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:14px;font-weight:600;white-space:nowrap;transition:transform .15s cubic-bezier(.2,0,0,1)}& .sb::after{content:"";position:absolute;inset:-6px -4px}& .sb:active{transform:scale(.96)}& .sb.gh{background:var(--pt);color:var(--p-text)}& .sb:disabled,& .sb.off{background:var(--soft);color:var(--ink3);cursor:default;transform:none}`
  const SPIN = `& .sp{display:inline-block;width:14px;height:14px;border-radius:50%;border:2px solid currentColor;border-right-color:transparent;animation:§spin .8s linear infinite}@keyframes §spin{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){& .sp{animation-duration:3s}}`
  const DLG = `& .dlg{position:relative;margin:auto;width:280px;background:var(--card2);border-radius:22px;padding:22px 18px 16px;text-align:center;box-shadow:0 24px 50px var(--sh25);animation:§pop .22s cubic-bezier(.2,0,0,1)}@keyframes §pop{from{opacity:0;transform:scale(.94)}}& .dlg h4{margin:0;font-size:18px;font-weight:600}& .dlg p{margin:10px 0 18px;font-size:14px;line-height:1.6;color:var(--ink2)}& .dlg .row{display:flex;gap:10px}`
  const HEAD = `& .hd{display:flex;align-items:center;justify-content:space-between;gap:8px}& .hd b{font-size:18px;font-weight:600}& .hd span{font-size:12px;color:var(--ink3)}`
  const CARD = (w = 340, r = 22) => `&{width:${w}px;background:var(--card);border-radius:${r}px;box-shadow:0 10px 26px var(--sh08)}`
  const CLAMP2 = `display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden`
  const ELL = `white-space:nowrap;overflow:hidden;text-overflow:ellipsis`
  const GOLD = { bg: '#F6EEDA', fg: '#7A5A1E', ac: '#B8913F' } // 低饱和暖金，只在小面积使用

  /* ================================================================
   * 营销活动 MKT
   * ================================================================ */
  guide('mp', 'MKT', [
    ['拉新、首单转化', '新人礼包弹层 / 票券缺口优惠券', '首次进入一次性亮出全部权益，一键领取；缺口券形状用户天然理解为“券”'],
    ['日常领券、凑单省钱', '优惠券领取中心', '分类筛选 + 领取状态（领取、已领取、已抢光、失败重试）一次到位，别让用户猜有没有领成功'],
    ['限时折扣、整点抢购', '秒杀模块 / 限时抢购场次条', '倒计时制造紧迫，场次条让用户知道“下一场什么时候”，进度条必须是真实库存'],
    ['社交裂变', '拼团卡 / 拼团进度卡 / 好友砍价卡', '“还差 1 人”“再砍 ¥50”是最强的转化文案；邀请后要有等待与成功的反馈'],
    ['提升客单价', '满减进度条 / 满减凑单面板', '购物车里提示“再买 ¥31”，凑单面板直接给可加购的商品，比任何弹窗都有效'],
    ['留存、复购', '签到与会员权益 / 积分兑换商品卡 / 会员日专区', '连续奖励让用户明天再来；积分要能兑换、会员日要有明确的价格差'],
    ['轻量互动、提升活跃', '幸运抽奖转盘', '每日次数有限、奖品真实可兑现；谢谢参与也要有温和的文案'],
  ])

  /* ---------- MP-MKT-006 幸运抽奖转盘 ---------- */
  const WHEEL = [['¥5 券', 'coupon', 3], ['20 积分', 'mgcoin', 3], ['谢谢参与', 'mgsmile', 4], ['免邮券', 'truck', 2], ['¥10 券', 'coupon', 1], ['50 积分', 'mgcoin', 3], ['再抽一次', 'refresh', 1], ['8 折券', 'tag', 2]]
  const wheelBg = `repeating-conic-gradient(from -23deg,var(--pm) 0 1deg,transparent 1deg 45deg),conic-gradient(from -22.5deg,${Array.from({ length: 8 }, (_, i) => `${i % 2 ? 'var(--pt)' : '#fff'} ${i * 45}deg ${(i + 1) * 45}deg`).join(',')})`
  def({
    id: 'MP-MKT-006', name: '幸运抽奖转盘', style: '转盘抽奖',
    fit: '每日签到后的互动奖励、会员日、拉新活动；点“开始”转动并停在奖项上，奖品直接入账',
    avoid: '奖品不能真实兑现；没有次数限制（会被刷）；把“谢谢参与”概率放得过高让人觉得被骗',
    kw: '抽奖 转盘 大转盘 lottery wheel spin 随机 积分 活动 互动',
    css: CSS('MP-MKT-006', `&{width:340px;padding:18px 16px 16px;border-radius:22px;background:linear-gradient(180deg,var(--pm) 0,var(--pt) 34%,var(--card) 100%);box-shadow:0 10px 26px var(--sh08);text-align:center}
${HEAD}& .hd{margin-bottom:28px;text-align:left}& .hd span{color:var(--ink2)}& .hd em{padding:0 2px;font-size:14px;font-weight:600;color:var(--p-text)}
& .wv{position:relative;width:264px;height:264px;margin:0 auto}
& .ptr{position:absolute;left:50%;top:-22px;width:24px;height:32px;margin-left:-12px;background:var(--pd);clip-path:polygon(0 0,100% 0,100% 42%,50% 100%,0 42%);z-index:3}
& .wheel{position:relative;width:264px;height:264px;border-radius:50%;background:var(--card);box-shadow:0 0 0 8px var(--card),0 0 0 9px var(--pm),0 14px 30px var(--sh14)}
& .disk{position:absolute;inset:0;border-radius:50%;background:${wheelBg}}
& .lb{position:absolute;z-index:1;width:64px;margin:-26px 0 0 -32px;padding:4px 0;border-radius:12px;display:flex;flex-direction:column;align-items:center;gap:2px;font-size:12px;line-height:16px;font-weight:600;color:var(--ink);transition:background-color .2s,color .2s}
& .lb .li{width:20px;height:20px;color:var(--p-text)}& .lb.on{background:var(--p);color:#fff}& .lb.on .li{color:#fff}
& .go{position:absolute;left:50%;top:50%;z-index:2;width:68px;height:68px;margin:-34px 0 0 -34px;border-radius:50%;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:16px;font-weight:600;box-shadow:0 0 0 5px var(--card),0 6px 14px rgba(var(--p-rgb),.28);transition:transform .15s cubic-bezier(.2,0,0,1)}
& .go:active{transform:scale(.96)}& .go:disabled{background:var(--n5);color:var(--ink3);box-shadow:0 0 0 5px var(--card);cursor:default;transform:none}
& .res{margin:26px 0 0;min-height:44px;display:flex;align-items:center;justify-content:center;padding:0 14px;border-radius:12px;background:var(--card);box-shadow:inset 0 0 0 1px var(--line);font-size:14px;color:var(--ink2);transition:background-color .2s}
& .res.win{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:none}
& .rule{margin:10px 0 0;font-size:12px;color:var(--ink3)}`),
    html: () => `<div class="mpmkt006"><div class="hd"><b>幸运大转盘</b><span>今日还有 <em data-left>3</em> 次机会</span></div><div class="wv"><i class="ptr"></i><div class="wheel"><div class="disk"></div>${WHEEL.map(([t, ic], i) => `<div class="lb" data-i="${i}"><span class="li">${sv(ic)}</span>${t}</div>`).join('')}<button class="go" type="button" data-go>开始</button></div></div><p class="res" data-res aria-live="polite">转动转盘，试试手气</p><p class="rule">奖品自动放入卡券包，积分当天到账</p></div>`,
    js: (root) => {
      const W = 264, R = 90, SEG = 45
      const disk = root.querySelector('.disk'), lbs = [...root.querySelectorAll('.lb')], go = root.querySelector('[data-go]'), res = root.querySelector('[data-res]'), leftEl = root.querySelector('[data-left]')
      let theta = 0, left = 3, busy = false
      const place = () => { disk.style.transform = `rotate(${theta}deg)`; lbs.forEach((l, i) => { const a = (i * SEG + theta) * Math.PI / 180; l.style.left = (W / 2 + R * Math.sin(a)) + 'px'; l.style.top = (W / 2 - R * Math.cos(a)) + 'px' }) }
      place()
      const pick = () => { const tot = WHEEL.reduce((s, w) => s + w[2], 0); let r = Math.random() * tot; for (let i = 0; i < WHEEL.length; i++) { r -= WHEEL[i][2]; if (r <= 0) return i } return 0 }
      go.addEventListener('click', () => {
        if (busy || left <= 0) return
        busy = true; go.disabled = true; go.textContent = '转动中'; res.className = 'res'; res.textContent = '好运转动中……'; lbs.forEach((l) => l.classList.remove('on'))
        const k = pick(), start = theta
        const base = ((-k * SEG - start) % 360 + 360) % 360
        const target = start + 360 * 5 + base + (Math.random() * 20 - 10)
        tween(start, target, 3600, (v) => { theta = v; place() }, () => {
          busy = false; lbs[k].classList.add('on'); res.dataset.k = k
          const [name] = WHEEL[k]
          if (name === '再抽一次') res.textContent = '运气不错，这次不扣次数，再来一次'
          else { left--; leftEl.textContent = left; if (name === '谢谢参与') res.textContent = '差一点点，明天再来试试'; else { res.classList.add('win'); res.textContent = `恭喜获得「${name}」，已放入账户`; IX.toast(root, `获得 ${name}`) } }
          go.disabled = left <= 0; go.textContent = left <= 0 ? '已抽完' : '开始'
        })
      })
    },
  })

  /* ---------- MP-MKT-007 拼团进度卡 ---------- */
  def({
    id: 'MP-MKT-007', name: '拼团进度卡', style: '头像堆叠',
    fit: '拼团详情页、分享落地页、订单里的“拼团中”；让人一眼看到还差几人、还剩多久',
    avoid: '没有真实成团规则时伪造头像和人数；倒计时结束后不说明结果（成团失败要自动退款并写出来）',
    kw: '拼团 成团 还差几人 邀请好友 倒计时 group buy 裂变 分享',
    css: CSS('MP-MKT-007', `${CARD()}&{padding:16px}
& .gd{display:flex;gap:12px}& .gd img{width:72px;height:72px;border-radius:12px;object-fit:cover;flex:none}
& .tx{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:space-between}& h4{margin:0;font-size:14px;line-height:20px;font-weight:600;${CLAMP2}}
& .pr{display:flex;align-items:center;gap:6px}& .pr .price b{font-size:22px}
& .mem{margin:22px 0 4px;display:flex;justify-content:center;gap:14px}
& .m{position:relative;width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center}
& .m .av{width:48px;height:48px;box-shadow:0 0 0 2px var(--card),0 0 0 3px var(--pm)}
& .m.e{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--pm);color:var(--p-fg)}& .m.e svg{width:20px;height:20px}
& .m.pop .av{animation:§in .32s cubic-bezier(.2,0,0,1)}@keyframes §in{from{opacity:0;transform:scale(.6)}}
& .lead{position:absolute;left:50%;bottom:-9px;transform:translateX(-50%);height:20px;padding:0 6px;border-radius:4px;background:var(--pd);color:#fff;font-size:12px;font-weight:600;line-height:20px;white-space:nowrap}
& .sr{display:flex;align-items:center;justify-content:space-between;margin:20px 0 14px;font-size:14px}& .sr b{font-size:16px;font-weight:600;color:var(--p-text)}& .sr .cd{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
& .done .sr b{color:var(--ok)}
${PB}${SPIN}`),
    html: () => `<div class="mpmkt007" data-total="4"><div class="gd"><img src="${P(2)}" alt=""><div class="tx"><h4>手作釉面陶瓷马克杯 350ml 两只装礼盒款</h4><div class="pr"><span class="price"><small>¥</small><b>49</b></span><span class="strike">¥69</span><span class="tg tg-soft">4 人团</span></div></div></div><div class="mem"><span class="m">${critter(0, 48)}<i class="lead">团长</i></span><span class="m">${critter(1, 48)}</span><span class="m e" data-slot>${sv('plus')}</span><span class="m e" data-slot>${sv('plus')}</span></div><div class="sr"><b data-need>还差 2 人成团</b><span class="cd" data-cd>剩余 <span data-ix="count" data-sec="86321"><i data-h>23</i>:<i data-m>58</i>:<i data-s>41</i></span></span></div><button class="pb" type="button" data-inv>邀请好友拼团</button></div>`,
    js: (root) => {
      const need = root.querySelector('[data-need]'), btn = root.querySelector('[data-inv]'), box = root.querySelector('.mpmkt007'), cd = root.querySelector('[data-cd]')
      let filled = 2
      btn.addEventListener('click', () => {
        if (btn.disabled) return
        if (box.classList.contains('done')) { IX.toast(root, '前往拼团订单详情'); return }
        btn.disabled = true; btn.innerHTML = '<span class="sp"></span>等待好友加入…'
        later(root, 1100, () => {
          const slot = root.querySelector('[data-slot]')
          slot.className = 'm pop'; slot.innerHTML = critter(filled, 48); slot.removeAttribute('data-slot')
          IX.toast(root, `${NAMES[filled + 1]} 已加入拼团`); filled++
          const left = 4 - filled; btn.disabled = false
          if (left > 0) { need.textContent = `还差 ${left} 人成团`; btn.textContent = '继续邀请好友' }
          else { box.classList.add('done'); need.textContent = '拼团成功，商家将尽快发货'; const c = cd.querySelector('[data-ix=count]'); if (c) { clearInterval(c.__t); c.removeAttribute('data-ix') } cd.textContent = '已成团'; btn.className = 'pb ok'; btn.textContent = '查看拼团订单' }
        })
      })
    },
  })

  /* ---------- MP-MKT-008 好友砍价卡 ---------- */
  const BARG = { orig: 599, floor: 329, cur: 471 }
  const frRow = (i, amt) => `<div class="fr"><span class="a">${critter(i, 28)}</span><span class="n">${NAMES[i]}</span><b>−¥${n2(amt)}</b></div>`
  def({
    id: 'MP-MKT-008', name: '好友砍价卡', style: '进度砍价',
    fit: '低价引流、爆款拉新；展示当前价、离底价还差多少、谁帮砍了多少，点按钮邀请好友帮砍',
    avoid: '底价低于成本又不限量；每个好友可无限帮砍；砍价成功后没有明确的“立即购买”和有效期',
    kw: '砍价 帮砍 底价 助力 邀请 bargain cut price 好友 进度',
    css: CSS('MP-MKT-008', `${CARD()}&{padding:16px}${HEAD}& .hd .cd{display:flex;align-items:center;gap:4px;font-variant-numeric:tabular-nums}& .hd .cd svg{width:14px;height:14px}& .hd .cd i{font-style:normal}
& .gd{display:flex;gap:12px;margin-top:14px}& .gd img{width:72px;height:72px;border-radius:12px;object-fit:cover;flex:none}& .tx{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:space-between}& h4{margin:0;font-size:14px;line-height:20px;font-weight:600;${CLAMP2}}
& .pc{position:relative;display:flex;align-items:baseline;gap:8px;margin:14px 0 10px}& .pc .lab{font-size:12px;color:var(--ink3)}& .pc .price small{font-size:14px}& .pc .price b{font-size:32px;font-weight:700}
& .fl{position:absolute;left:96px;top:-6px;font-size:16px;font-weight:600;color:var(--price);opacity:0;pointer-events:none}& .fl.go{animation:§up .9s cubic-bezier(.2,0,0,1)}@keyframes §up{0%{opacity:0;transform:translateY(8px)}20%{opacity:1}100%{opacity:0;transform:translateY(-26px)}}
& .bx{height:8px;border-radius:4px;background:var(--n4);overflow:hidden}& .bx i{display:block;height:100%;border-radius:4px;background:linear-gradient(90deg,var(--ga),var(--gb));transition:width .5s cubic-bezier(.2,0,0,1)}
& .meta{display:flex;justify-content:space-between;margin:8px 0 14px;font-size:12px;color:var(--ink3)}& .meta b{font-weight:600;color:var(--p-text)}
& .frs{display:flex;flex-direction:column;gap:2px;padding:6px 12px;border-radius:12px;background:var(--n2);margin-bottom:14px}& .frs h5{margin:6px 0 2px;font-size:12px;font-weight:600;color:var(--ink3)}
& .fr{display:flex;align-items:center;gap:8px;height:36px;font-size:14px}& .fr .a{display:flex}& .fr .n{flex:1;min-width:0;${ELL}}& .fr b{font-weight:600;color:var(--price);font-variant-numeric:tabular-nums}& .fr.new{animation:§in .35s cubic-bezier(.2,0,0,1)}@keyframes §in{from{opacity:0;transform:translateY(-8px)}}
& .win .bx i{background:var(--ok-fill)}
${PB}${SPIN}`),
    html: () => `<div class="mpmkt008"><div class="hd"><b>我的砍价</b><span class="cd">${sv('clock')}<span data-ix="count" data-sec="82800"><i data-h>23</i>:<i data-m>00</i>:<i data-s>00</i></span> 后结束</span></div><div class="gd"><img src="${P(0)}" alt=""><div class="tx"><h4>无线降噪耳机 石墨灰 主动降噪</h4><span class="strike" style="margin:0">原价 ¥${n2(BARG.orig)}</span></div></div><div class="pc"><span class="lab">当前价</span><span class="price"><small>¥</small><b data-now>${n2(BARG.cur)}</b></span><span class="fl" data-fl></span></div><div class="bx"><i data-bar style="width:${(BARG.orig - BARG.cur) / (BARG.orig - BARG.floor) * 100}%"></i></div><div class="meta"><span>已砍 <b data-cut>¥${n2(BARG.orig - BARG.cur)}</b></span><span>底价 ¥${n2(BARG.floor)}</span></div><div class="frs"><h5 data-fc>好友助力 · 2 人</h5><div data-fl2>${frRow(1, 52.4)}${frRow(2, 75.6)}</div></div><button class="pb" type="button" data-inv>邀请好友帮砍</button></div>`,
    js: (root) => {
      const now = root.querySelector('[data-now]'), bar = root.querySelector('[data-bar]'), cut = root.querySelector('[data-cut]'), fl = root.querySelector('[data-fl]'), list = root.querySelector('[data-fl2]'), fc = root.querySelector('[data-fc]'), btn = root.querySelector('[data-inv]'), box = root.querySelector('.mpmkt008')
      let cur = BARG.cur, helpers = 2
      btn.addEventListener('click', () => {
        if (btn.disabled) return
        if (cur <= BARG.floor) { IX.toast(root, '前往确认订单'); return }
        btn.disabled = true; btn.innerHTML = '<span class="sp"></span>好友赶来中…'
        later(root, 900, () => {
          const rem = cur - BARG.floor
          const amt = Math.min(rem, Math.round((8 + Math.random() * 28) * 100) / 100)
          const next = Math.round((cur - amt) * 100) / 100
          fl.textContent = `−¥${n2(amt)}`; fl.classList.remove('go'); void fl.offsetWidth; fl.classList.add('go')
          tween(cur, next, 500, (v) => { now.textContent = n2(v) })
          cur = next; helpers++
          bar.style.width = ((BARG.orig - cur) / (BARG.orig - BARG.floor) * 100) + '%'; cut.textContent = `¥${n2(BARG.orig - cur)}`
          list.insertAdjacentHTML('afterbegin', frRow((helpers + 1) % 12, amt)); list.firstElementChild.classList.add('new')
          while (list.children.length > 3) list.lastElementChild.remove()
          fc.textContent = `好友助力 · ${helpers} 人`
          btn.disabled = false
          if (cur <= BARG.floor) { box.classList.add('win'); btn.textContent = `砍价成功，¥${n2(BARG.floor)} 立即购买`; IX.toast(root, '已砍到底价') } else btn.textContent = '继续邀请好友帮砍'
        })
      })
    },
  })

  /* ---------- MP-MKT-009 限时抢购场次条 ---------- */
  const SESS = [['08:00', '已结束', 'end'], ['10:00', '已开抢', 'on'], ['12:00', '即将开始', 'soon'], ['14:00', '即将开始', 'soon'], ['10:00', '明日预告', 'tmr']]
  const FS = [[6, '保温水杯 500ml 鼠尾草绿', 59, 89, 72], [2, '手作釉面陶瓷马克杯 两只装', 39, 69, 45], [7, '玻尿酸保湿精华 30ml', 129, 258, 88]]
  const fsRow = (g, kind) => {
    const [i, nm, p, o, pct] = g
    const mid = kind === 'on' ? `<div class="pg"><i style="width:${pct}%"></i></div><small class="pt">已抢 ${pct}%</small>` : kind === 'end' ? `<small class="pt">本场已抢完</small>` : `<small class="pt">${(pct * 17).toLocaleString('en-US')} 人想要</small>`
    const btn = kind === 'on' ? `<button class="sb" type="button" data-grab>马上抢</button>` : kind === 'end' ? `<button class="sb" type="button" disabled>已抢光</button>` : `<button class="sb gh" type="button" data-remind>${sv('bell')}提醒我</button>`
    return `<div class="it"><img src="${P(i)}" alt=""><div class="tx"><h4>${nm}</h4><div class="pr"><span class="price"><small>¥</small><b>${p}</b></span><span class="strike">¥${o}</span></div>${mid}</div>${btn}</div>`
  }
  def({
    id: 'MP-MKT-009', name: '限时抢购场次条', style: '横滑场次',
    fit: '整点秒杀专区、频道页顶部；横滑切场次，一眼分清已开抢、即将开始、明日预告',
    avoid: '场次超过 6 个且没有横滑提示；“即将开始”场次直接放购买按钮（应是“提醒我”）；假库存进度',
    kw: '抢购 秒杀 场次 整点 横滑 已开抢 即将开始 提醒 flash sale session 倒计时',
    css: CSS('MP-MKT-009', `${CARD()}&{padding:14px 0 6px;overflow:hidden}
& .ses{gap:8px;padding:2px 16px;scroll-snap-type:none}& .ses>*{scroll-snap-align:none}
& .sn{flex:none;width:84px;height:56px;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:var(--ink2);background:var(--n3);transition:background-color .2s,color .2s}
& .sn b{font-size:18px;line-height:22px;font-weight:600;font-variant-numeric:tabular-nums}& .sn span{font-size:12px;line-height:16px}
& .sn.on{background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff}& .sn.end:not(.on){color:var(--ink3)}
& .sts{display:flex;align-items:center;gap:6px;padding:12px 16px 2px;font-size:14px;color:var(--ink2);font-variant-numeric:tabular-nums}& .sts svg{width:16px;height:16px;color:var(--p-text);flex:none}& .sts b{font-weight:600;color:var(--p-text)}& .sts i{font-style:normal}
& .ls{padding:4px 16px 8px}& .it{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}& .it:last-child{border-bottom:0}
& .it img{width:76px;height:76px;border-radius:12px;object-fit:cover;flex:none}& .it .tx{flex:1;min-width:0;display:flex;flex-direction:column;gap:5px}& .it h4{margin:0;font-size:14px;line-height:20px;font-weight:600;${ELL}}
& .pr{display:flex;align-items:baseline}& .pr .price b{font-size:18px}& .pg{height:6px;border-radius:3px;background:var(--n4)}& .pg i{display:block;height:100%;border-radius:3px;background:linear-gradient(90deg,var(--ga),var(--gb));transition:width .4s}& .pt{font-size:12px;color:var(--ink3)}
& .sb svg{width:14px;height:14px}
${SB}${SPIN}`),
    html: () => `<div class="mpmkt009"><div data-ix="tabs" data-g="s9"><div class="ix-track ses">${SESS.map(([t, s, k], i) => `<button class="sn ${k === 'on' ? 'on' : ''} ${k}" type="button" data-t="s${i}"><b>${t}</b><span>${s}</span></button>`).join('')}</div></div>${SESS.map(([t, s, k], i) => `<div data-p="s${i}" data-g="s9" ${k === 'on' ? '' : 'hidden'}><div class="sts">${k === 'on' ? `${sv('mgtimer')}距本场结束 <span data-ix="count" data-sec="4328"><b data-h>01</b>:<b data-m>12</b>:<b data-s>08</b></span>` : k === 'end' ? `${sv('info')}本场已结束，下一场 12:00` : k === 'soon' ? `${sv('mgtimer')}距开抢还有 <span data-ix="count" data-sec="${i === 2 ? 5400 : 12600}"><b data-h>01</b>:<b data-m>30</b>:<b data-s>00</b></span>` : `${sv('calendar')}明天 10:00 开抢，可提前设置提醒`}</div><div class="ls">${FS.map((g) => fsRow(g, k)).join('')}</div></div>`).join('')}</div>`,
    js: (root) => {
      const tr = root.querySelector('.ses'), on = tr.querySelector('.on')
      if (on) tr.scrollLeft = Math.max(0, on.offsetLeft - 16)
      tr.addEventListener('click', (e) => { const b = e.target.closest('[data-t]'); if (b) setTimeout(() => tr.scrollTo({ left: b.offsetLeft - (tr.clientWidth - b.offsetWidth) / 2, behavior: reduce() ? 'auto' : 'smooth' }), 0) })
      root.addEventListener('click', (e) => {
        const r = e.target.closest('[data-remind]')
        if (r) { const set = r.classList.toggle('set'); r.innerHTML = set ? `${sv('check')}已提醒` : `${sv('bell')}提醒我`; r.classList.toggle('gh', !set); IX.toast(root, set ? '开抢前 5 分钟提醒你' : '已取消提醒'); return }
        const g = e.target.closest('[data-grab]')
        if (!g || g.disabled) return
        if (g.dataset.pay) { IX.toast(root, '前往收银台'); return }
        g.disabled = true; g.innerHTML = '<span class="sp"></span>'
        later(root, 700, () => {
          const row = g.closest('.it'), pg = row.querySelector('.pg i'), pt = row.querySelector('.pt'), v = Math.min(100, parseInt(pg.style.width) + 3)
          pg.style.width = v + '%'; pt.textContent = `已抢 ${v}%`
          g.disabled = false; g.className = 'sb gh'; g.textContent = '去付款'; g.dataset.pay = '1'; IX.toast(root, '抢到了，请在 15 分钟内付款')
        })
      })
    },
  })

  /* ---------- MP-MKT-010 优惠券领取中心 ---------- */
  const CPS = [
    ['cut', '<small>¥</small>20', '满 99 可用', '新人满减券', '领取后 7 天内有效', 'idle'],
    ['off', '9<small>折</small>', '无门槛', '全场通用折扣券', '最高减 ¥30', 'idle'],
    ['ship', '<small>¥</small>6', '免运费', '运费抵扣券', '12-15 到期', 'idle'],
    ['cut', '<small>¥</small>10', '满 69 可用', '家居日用品类满减券（限指定品类商品使用）', '12-31 到期', 'fail'],
    ['cut', '<small>¥</small>50', '满 299 可用', '会员专享大额满减券', '今日份已被抢光', 'out'],
  ]
  const notch = (x) => `radial-gradient(circle 8px at ${x}px 0,transparent 7.5px,#000 8px) top/100% 51% no-repeat,radial-gradient(circle 8px at ${x}px 100%,transparent 7.5px,#000 8px) bottom/100% 51% no-repeat`
  def({
    id: 'MP-MKT-010', name: '优惠券领取中心', style: '分类+状态',
    fit: '领券中心、结算页“领券”面板；按类型筛选，领取后原地变“已领取”，失败可重试，抢光置灰',
    avoid: '券面塞太多字（只放金额、门槛、名称、有效期）；领取后没有任何反馈；缺口直接用背景色遮盖（换底色会露馅）',
    kw: '优惠券 领券 领券中心 缺口 满减 折扣券 免邮 coupon claim 已领取 重试',
    css: CSS('MP-MKT-010', `${CARD()}&{padding:16px 16px 12px;background:var(--pt)}${HEAD}
& .tb{display:flex;gap:8px;margin:12px 0 14px}& .tb button{position:relative;height:32px;padding:0 14px;border-radius:16px;background:var(--card);font-size:14px;color:var(--ink2);transition:background-color .2s,color .2s}& .tb button::after{content:"";position:absolute;inset:-6px -2px}& .tb .on{background:var(--p);color:#fff;font-weight:600}
& .list{display:flex;flex-direction:column;gap:12px}
& .cp{filter:drop-shadow(0 3px 8px var(--sh08))}
& .cb{display:flex;height:88px;background:var(--card);border-radius:16px;overflow:hidden;-webkit-mask:${notch(104)};mask:${notch(104)}}
& .l{flex:none;width:104px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:linear-gradient(145deg,var(--ga),var(--gb));color:#fff;transition:background .25s,color .25s}
& .l b{font-size:28px;line-height:1;font-weight:700}& .l b small{font-size:14px;font-weight:600}& .l span{font-size:12px}
& .r{position:relative;flex:1;min-width:0;display:flex;align-items:center;gap:8px;padding:0 12px 0 14px}& .r::before{content:"";position:absolute;left:0;top:12px;bottom:12px;border-left:1px dashed var(--n7)}
& .r .tx{flex:1;min-width:0}& .r h4{margin:0;font-size:14px;line-height:20px;font-weight:600;${CLAMP2}}& .r p{margin:2px 0 0;font-size:12px;color:var(--ink3);${ELL}}
& .got .l{background:var(--pm);color:var(--p-text)}& .out .l{background:var(--n5);color:var(--ink2)}& .out .r{opacity:.85}
& .end{margin:14px 0 4px;text-align:center;font-size:12px;color:var(--ink3)}
${SB}${SPIN}`),
    html: () => `<div class="mpmkt010"><div class="hd"><b>领券中心</b><span>已领 <b style="font-size:12px;font-weight:600;color:var(--p-text)" data-got>0</b> / 4 张</span></div><div class="tb" data-ix="tabs" data-list=".list"><button class="on" type="button" data-t="all">全部</button><button type="button" data-t="cut">满减</button><button type="button" data-t="off">折扣</button><button type="button" data-t="ship">免邮</button></div><div class="list">${CPS.map(([k, a, c, t, s, st]) => `<div class="cp ${st === 'out' ? 'out' : ''}" data-k="${k}" data-st="${st}"><div class="cb"><div class="l"><b>${a}</b><span>${c}</span></div><div class="r"><div class="tx"><h4>${t}</h4><p>${s}</p></div>${st === 'out' ? '<button class="sb" type="button" disabled>已抢光</button>' : '<button class="sb" type="button" data-claim>领取</button>'}</div></div></div>`).join('')}</div><p class="end">没有更多了</p></div>`,
    js: (root) => {
      const got = root.querySelector('[data-got]')
      root.addEventListener('click', (e) => {
        const b = e.target.closest('[data-claim]'); if (!b || b.disabled) return
        const cp = b.closest('.cp'); b.disabled = true; b.innerHTML = '<span class="sp"></span>'
        later(root, 700, () => {
          if (cp.dataset.st === 'fail') { cp.dataset.st = 'idle'; b.disabled = false; b.textContent = '重试'; IX.toast(root, '网络开小差，请重试'); return }
          cp.classList.add('got'); b.className = 'sb gh'; b.textContent = '已领取'; b.removeAttribute('data-claim'); b.disabled = true; b.style.opacity = '1'
          got.textContent = root.querySelectorAll('.cp.got').length; IX.toast(root, '领取成功，已放入卡券包')
        })
      })
    },
  })

  /* ---------- MP-MKT-011 新人礼包弹层 ---------- */
  const GIFTS = [['<small>¥</small>20', '满 99 可用', '新人满减券'], ['<small>¥</small>10', '满 59 可用', '品类通用券'], ['<small>¥</small>6', '免运费', '运费抵扣券']]
  def({
    id: 'MP-MKT-011', name: '新人礼包弹层', style: '居中弹层',
    fit: '新用户首次进入首页、注册成功后；一次性亮出 3 张以内的券，一键领取，关闭后留一个小入口',
    avoid: '每次打开小程序都弹（同一用户只弹一次）；礼包里放超过 3 样；关闭按钮太小或藏起来',
    kw: '新人礼包 弹层 弹窗 一键领取 新用户 注册 首单 popup welcome gift',
    css: CSS('MP-MKT-011', `&{position:relative;width:340px;height:500px;border-radius:22px;overflow:hidden;background:var(--n3);box-shadow:0 10px 26px var(--sh08)}
& .bg{padding:14px 14px 0}& .bg .sk{height:36px;border-radius:18px;background:var(--n5)}& .bg .ban{height:96px;margin:12px 0;border-radius:16px;background:linear-gradient(135deg,var(--pm),var(--pt))}
& .bg .gr{display:grid;grid-template-columns:1fr 1fr;gap:10px}& .bg .gr div{background:var(--card);border-radius:12px;padding:8px}& .bg .gr img{width:100%;aspect-ratio:1/1;border-radius:8px;object-fit:cover}& .bg .gr i{display:block;height:8px;border-radius:4px;background:var(--n5);margin-top:8px;width:70%}
& .fab{position:absolute;right:12px;bottom:14px;display:flex;align-items:center;gap:6px;height:44px;padding:0 16px 0 12px;border-radius:22px;background:var(--card);box-shadow:0 6px 18px var(--sh16);font-size:14px;font-weight:600;color:var(--p-text)}& .fab svg{width:20px;height:20px}
& .ix-ov{flex-direction:column;align-items:center;justify-content:center;gap:18px}
${DLG}& .dlg{display:flow-root;margin:0;padding:0 18px 18px}
& .hero{width:96px;height:96px;margin:-48px auto 6px;border-radius:50%;background:var(--card);box-shadow:0 8px 20px var(--sh14);display:flex;align-items:center;justify-content:center}& .hero .ico{width:66px;height:66px}& .hero .ico-line{width:44px;height:44px;stroke:var(--p)}
& .dlg h4{font-size:22px}& .dlg p{margin:6px 0 14px}
& .cps{list-style:none;margin:0 0 16px;padding:0;display:flex;flex-direction:column;gap:8px}& .cps li{display:flex;align-items:center;gap:12px;height:52px;padding:0 12px;border-radius:12px;background:var(--pt);text-align:left}
& .cps b{flex:none;min-width:52px;font-size:22px;line-height:1;font-weight:700;color:var(--p-text)}& .cps b small{font-size:14px;font-weight:600}& .cps .t{flex:1;min-width:0}& .cps .t strong{display:block;font-size:14px;font-weight:600;${ELL}}& .cps .t span{font-size:12px;color:var(--ink3)}
& .cps .k{flex:none;width:22px;height:22px;border-radius:50%;box-shadow:inset 0 0 0 1.5px var(--pm);color:#fff;display:flex;align-items:center;justify-content:center;transition:background-color .2s}& .cps .k svg{width:14px;height:14px;opacity:0}& .cps li.got .k{background:var(--ok-fill);box-shadow:none}& .cps li.got .k svg{opacity:1}
& .x{position:relative;width:36px;height:36px;border-radius:50%;background:var(--glass2);color:var(--ink);display:flex;align-items:center;justify-content:center}& .x::after{content:"";position:absolute;inset:-4px}& .x svg{width:16px;height:16px}
${PB}${SPIN}`),
    html: () => `<div class="mpmkt011"><div class="bg"><div class="sk"></div><div class="ban"></div><div class="gr">${[1, 3, 5, 8].map((i) => `<div><img src="${P(i)}" alt=""><i></i></div>`).join('')}</div></div><button class="fab" type="button" data-open="gift">${sv('giftbox')}<span data-fl>新人礼包</span></button><div class="ix-ov show" data-ov="gift"><div class="ix-mask"></div><div class="dlg"><div class="hero">${IC('giftbox')}</div><h4>新人专享礼包</h4><p>注册成功，3 张券已备好，7 天内有效</p><ul class="cps">${GIFTS.map(([a, c, t]) => `<li><b>${a}</b><span class="t"><strong>${t}</strong><span>${c}</span></span><span class="k">${sv('check')}</span></li>`).join('')}</ul><button class="pb" type="button" data-take>一键领取 3 张券</button></div><button class="x" type="button" data-close aria-label="关闭">${sv('close')}</button></div></div>`,
    js: (root) => {
      const btn = root.querySelector('[data-take]'), ov = root.querySelector('[data-ov]'), fl = root.querySelector('[data-fl]')
      btn.addEventListener('click', () => {
        if (btn.dataset.done) { ov.classList.remove('show'); IX.toast(root, '已为你筛出可用商品'); return }
        btn.disabled = true; btn.innerHTML = '<span class="sp"></span>领取中…'
        later(root, 700, () => {
          root.querySelectorAll('.cps li').forEach((li, i) => setTimeout(() => li.classList.add('got'), i * 120))
          btn.disabled = false; btn.dataset.done = '1'; btn.textContent = '去使用'; fl.textContent = '礼包已领取'; IX.toast(root, '3 张券已放入卡券包')
        })
      })
    },
  })

  /* ---------- MP-MKT-012 积分兑换商品卡 ---------- */
  const EXC = [{ i: 2, n: '手作釉面马克杯 两只装', c: 800, s: 12 }, { i: 4, n: '机械腕表 钢壳皮带 40mm 限量联名款', c: 3000, s: 3 }]
  def({
    id: 'MP-MKT-012', name: '积分兑换商品卡', style: '余额联动',
    fit: '积分商城首页、会员中心“积分兑换”；顶部显示可用积分，卡片按够不够自动切换“立即兑换/还差多少”，兑换前二次确认',
    avoid: '积分不够时隐藏商品（让用户知道还差多少才有动力）；兑换后不扣减显示；兑换不二次确认',
    kw: '积分 兑换 积分商城 积分换购 points redeem exchange 余额 库存 确认',
    css: CSS('MP-MKT-012', `&{position:relative;width:340px;padding:16px;border-radius:22px;background:var(--pt);box-shadow:0 10px 26px var(--sh08);overflow:hidden}
& .bal{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-radius:16px;background:var(--card);margin-bottom:12px}& .bal .l{display:flex;align-items:center;gap:10px}& .bal .l .cz{width:36px;height:36px;border-radius:50%;background:var(--pt);color:var(--p-text);padding:7px;flex:none}& .bal small{display:block;font-size:12px;color:var(--ink3)}& .bal b{font-size:28px;line-height:34px;font-weight:700;font-variant-numeric:tabular-nums}& .bal .more{display:flex;align-items:center;gap:2px;font-size:14px;color:var(--p-text);font-weight:600}& .bal .more svg{width:14px;height:14px}
& .gr{display:grid;grid-template-columns:1fr 1fr;gap:12px}& .cd{background:var(--card);border-radius:16px;padding:8px 8px 12px;display:flex;flex-direction:column}
& .cd img{width:100%;aspect-ratio:1/1;border-radius:12px;object-fit:cover}& .cd h4{margin:10px 4px 0;font-size:14px;line-height:20px;font-weight:600;${CLAMP2};min-height:40px}
& .cd .cs{display:flex;align-items:center;gap:4px;margin:6px 4px 2px;font-size:16px;font-weight:600;color:var(--p-text);font-variant-numeric:tabular-nums}& .cd .cs svg{width:16px;height:16px}& .cd .sk{margin:0 4px 10px;font-size:12px;color:var(--ink3)}
& .cd .sb{margin:auto 4px 0}
${SB}${SPIN}& .ix-ov{align-items:center}${DLG}& .dlg{margin:auto}& .dlg b{color:var(--p-text)}`),
    html: () => `<div class="mpmkt012"><div class="bal"><div class="l"><span class="cz">${sv('mgcoin')}</span><div><small>我的积分</small><b data-bal>2,360</b></div></div><button class="more" type="button" data-toast="进入积分明细">积分明细${sv('chev')}</button></div><div class="gr">${EXC.map((x, k) => `<div class="cd" data-c="${x.c}" data-k="${k}" data-n="${x.n}"><img src="${P(x.i)}" alt=""><h4>${x.n}</h4><div class="cs">${sv('mgcoin')}${nf(x.c)} 积分</div><div class="sk">仅剩 <span data-stk>${x.s}</span> 件</div><button class="sb" type="button" data-ex data-open="cf">立即兑换</button></div>`).join('')}</div><div class="ix-ov" data-ov="cf"><div class="ix-mask"></div><div class="dlg"><h4>确认兑换</h4><p>将使用 <b data-dc>800</b> 积分兑换「<span data-dn>马克杯</span>」，兑换后积分不可退回。</p><div class="row"><button class="pb cx" type="button" data-close>取消</button><button class="pb" type="button" data-do>确认兑换</button></div></div></div></div>`,
    js: (root) => {
      const bal = root.querySelector('[data-bal]'), cards = [...root.querySelectorAll('.cd')], dc = root.querySelector('[data-dc]'), dn = root.querySelector('[data-dn]'), ov = root.querySelector('[data-ov]'), ok = root.querySelector('[data-do]')
      let points = 2360, cur = null
      const sync = () => cards.forEach((c) => {
        const b = c.querySelector('[data-ex]'), need = +c.dataset.c; if (c.dataset.done) return
        const short = need - points; b.disabled = short > 0; b.removeAttribute('data-open'); if (short <= 0) b.setAttribute('data-open', 'cf')
        b.textContent = short > 0 ? `还差 ${nf(short)} 积分` : '立即兑换'
      })
      sync()
      root.addEventListener('click', (e) => { const b = e.target.closest('[data-ex]'); if (b && !b.disabled) { cur = b.closest('.cd'); dc.textContent = nf(+cur.dataset.c); dn.textContent = cur.dataset.n.length > 10 ? cur.dataset.n.slice(0, 10) + '…' : cur.dataset.n } })
      ok.addEventListener('click', () => {
        if (!cur || ok.disabled) return
        ok.disabled = true; ok.innerHTML = '<span class="sp"></span>'
        later(root, 600, () => {
          ok.disabled = false; ok.textContent = '确认兑换'; ov.classList.remove('show')
          const from = points; points -= +cur.dataset.c; tween(from, points, 500, (v) => { bal.textContent = nf(v) })
          const stk = cur.querySelector('[data-stk]'); stk.textContent = Math.max(0, +stk.textContent - 1)
          const b = cur.querySelector('[data-ex]'); cur.dataset.done = '1'; b.removeAttribute('data-open'); b.disabled = true; b.textContent = '已兑换'
          sync(); IX.toast(root, '兑换成功，可在订单中查看')
        })
      })
    },
  })

  /* ---------- MP-MKT-013 会员日专区 ---------- */
  const LV = [['普通', 0.95], ['银卡', 0.9], ['金卡', 0.85], ['铂金', 0.8]]
  const MD = [[6, '保温水杯 500ml', 89], [1, '轻量跑鞋 云白', 329], [7, '玻尿酸保湿精华', 258]]
  def({
    id: 'MP-MKT-013', name: '会员日专区', style: '等级折扣',
    fit: '每月固定会员日、会员专享频道；按等级展示折扣，切换等级价格实时变化，激励升级',
    avoid: '折扣差异太小（用户感知不到）；会员价与日常价对不上；没有标出“我的等级”',
    kw: '会员日 会员价 折扣 等级 专区 铂金 金卡 member day 折上折 升级',
    css: CSS('MP-MKT-013', `${CARD()}&{overflow:hidden}
& .top{padding:16px 16px 14px;background:linear-gradient(160deg,var(--pm),var(--pt));display:flex;align-items:flex-start;justify-content:space-between;gap:8px}& .top h3{margin:0;font-size:22px;line-height:28px;font-weight:600}& .top p{margin:2px 0 0;font-size:12px;color:var(--ink2)}
& .top .cd{flex:none;display:flex;flex-direction:column;align-items:flex-end;gap:2px;font-size:12px;color:var(--ink2)}& .top .cd b{display:inline-flex;gap:3px;font-size:14px;font-weight:600;color:var(--p-text);font-variant-numeric:tabular-nums}& .top .cd i{font-style:normal}
& .lvs{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:14px 16px 4px}& .lv{position:relative;height:56px;border-radius:12px;background:var(--n3);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:12px;color:var(--ink2);transition:background-color .2s,color .2s}
& .lv b{font-size:16px;line-height:20px;font-weight:600;color:var(--ink)}& .lv.on{background:var(--p);color:#fff}& .lv.on b{color:#fff}& .lv.me::after{content:"我的";position:absolute;right:-2px;top:-8px;height:18px;padding:0 5px;border-radius:4px;background:${GOLD.bg};color:${GOLD.fg};font-size:12px;line-height:18px;font-weight:600}
& .gs{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:12px 16px 0}& .g img{width:100%;aspect-ratio:1/1;border-radius:12px;object-fit:cover}& .g h4{margin:6px 0 2px;font-size:12px;line-height:16px;font-weight:600;${ELL}}& .g .price b{font-size:16px}& .g .price small{font-size:12px}& .g .strike{display:block;margin:3px 0 0}
& .sv{margin:12px 16px 12px;padding:10px 12px;border-radius:12px;background:var(--pt);font-size:12px;line-height:18px;color:var(--p-text)}
& .ft{padding:0 16px 16px}${PB}`),
    html: () => `<div class="mpmkt013"><div class="top"><div><h3>会员日</h3><p>每月 8 号 · 会员专享折上折</p></div><div class="cd"><span>距本场结束</span><b data-ix="count" data-sec="187448"><i data-h>52</i>:<i data-m>04</i>:<i data-s>08</i></b></div></div><div class="lvs" data-ix="tabs">${LV.map(([n, d], i) => `<button class="lv ${i === 2 ? 'on me' : ''}" type="button" data-t="l${i}" data-d="${d}" data-i="${i}">${n}<b>${(d * 10).toFixed(1).replace('.0', '')} 折</b></button>`).join('')}</div><div class="gs">${MD.map(([i, n, p]) => `<div class="g"><img src="${P(i)}" alt=""><h4>${n}</h4><span class="price"><small>¥</small><b data-p="${p}">${Math.round(p * 0.85)}</b></span><span class="strike">¥${p}</span></div>`).join('')}</div><div class="sv" data-sv></div><div class="ft"><button class="pb" type="button" data-toast="进入会员日专区">进入会员日专区</button></div></div>`,
    js: (root) => {
      const save = root.querySelector('[data-sv]'), mine = 2
      const total = (d) => MD.reduce((s, m) => s + m[2] - Math.round(m[2] * d), 0)
      const upd = (i) => {
        const d = LV[i][1]
        root.querySelectorAll('[data-p]').forEach((b) => { b.textContent = Math.round(+b.dataset.p * d) })
        const t = total(d), mt = total(LV[mine][1])
        save.textContent = i === mine ? `你是${LV[mine][0]}会员，这三件合计已省 ¥${t}` : i > mine ? `升级到${LV[i][0]}，这三件合计可省 ¥${t}，比现在多省 ¥${t - mt}` : `${LV[i][0]}会员这三件合计可省 ¥${t}，比你少省 ¥${mt - t}`
      }
      upd(mine)
      root.querySelector('.lvs').addEventListener('click', (e) => { const b = e.target.closest('[data-i]'); if (b) upd(+b.dataset.i) })
    },
  })

  /* ---------- MP-MKT-014 满减凑单面板 ---------- */
  const TIERS = [[99, 10], [150, 25], [200, 45]]
  const ADDS = [[2, '手作釉面马克杯', 59], [3, '帆布托特包 原色', 129], [5, '护眼台灯 三档调光', 219]]
  def({
    id: 'MP-MKT-014', name: '满减凑单面板', style: '阶梯进度',
    fit: '购物车“去凑单”落地页、结算前提示；多档满减用阶梯进度条，下面直接给可加购的商品',
    avoid: '档位超过 3 档；推荐商品价格远超缺口（用户会放弃）；加购后进度不实时变化',
    kw: '凑单 满减 阶梯 满额减 加购 客单价 进度条 threshold bundle add on 免运费',
    css: CSS('MP-MKT-014', `${CARD()}&{padding:16px}${HEAD}& .hd span b{font-size:14px;font-weight:600;color:var(--ink)}
& .tip{margin:12px 0 22px;font-size:14px;color:var(--ink2)}& .tip b{font-weight:600;color:var(--p-text)}
& .trk{position:relative;height:8px;border-radius:4px;background:var(--n4);margin:0 4px 46px}& .trk .f{position:absolute;left:0;top:0;bottom:0;border-radius:4px;background:linear-gradient(90deg,var(--ga),var(--gb));transition:width .35s cubic-bezier(.2,0,0,1)}
& .mk{position:absolute;top:50%;width:20px;height:20px;margin:-10px 0 0 -10px;border-radius:50%;background:var(--card);box-shadow:inset 0 0 0 2px var(--n8);display:flex;align-items:center;justify-content:center;color:#fff;transition:background-color .2s,box-shadow .2s}& .mk svg{width:12px;height:12px;opacity:0}
& .mk.hit{background:var(--p);box-shadow:none}& .mk.hit svg{opacity:1}
& .mk em{position:absolute;top:26px;left:50%;transform:translateX(-50%);font-style:normal;font-size:12px;line-height:16px;white-space:nowrap;text-align:center;color:var(--ink3)}& .mk.hit em{color:var(--p-text);font-weight:600}& .mk:last-child em{transform:translateX(-70%)}
& .it{display:flex;align-items:center;gap:12px;padding:10px 0;border-top:1px solid var(--line)}& .it img{width:56px;height:56px;border-radius:12px;object-fit:cover;flex:none}& .it .tx{flex:1;min-width:0}& .it h4{margin:0 0 6px;font-size:14px;line-height:20px;font-weight:600;${ELL}}& .it .price b{font-size:18px}
& .sum{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:6px;padding-top:14px;border-top:1px solid var(--line)}& .sum p{margin:0;font-size:12px;color:var(--ink3)}& .sum p b{display:block;margin-top:2px;font-size:22px;line-height:26px;font-weight:600;color:var(--price);font-variant-numeric:tabular-nums}& .sum .pb{width:132px;flex:none}
${SB}${PB}`),
    html: () => `<div class="mpmkt014"><div class="hd"><b>满减凑单</b><span>购物车 <b data-cart>¥68</b></span></div><p class="tip" data-tip></p><div class="trk"><i class="f" data-f></i>${TIERS.map(([t, d], i) => `<span class="mk" data-t="${t}" style="left:${t / 2}%">${sv('check')}<em>满 ${t}<br>减 ${d}</em></span>`).join('')}</div>${ADDS.map(([i, n, p]) => `<div class="it" data-p="${p}"><img src="${P(i)}" alt=""><div class="tx"><h4>${n}</h4><span class="price"><small>¥</small><b>${p}</b></span></div><button class="sb gh" type="button" data-add>加购</button></div>`).join('')}<div class="sum"><p>合计（已减 ¥<span data-cut>0</span>）<b data-pay>¥68</b></p><button class="pb" type="button" data-toast="去结算">去结算</button></div></div>`,
    js: (root) => {
      const BASE = 68, MAX = 200, tip = root.querySelector('[data-tip]'), f = root.querySelector('[data-f]'), mks = [...root.querySelectorAll('.mk')]
      const upd = () => {
        const add = [...root.querySelectorAll('.it.in')].reduce((s, it) => s + +it.dataset.p, 0), total = BASE + add
        f.style.width = Math.min(100, total / MAX * 100) + '%'
        let cut = 0; mks.forEach((m, i) => { const hit = total >= TIERS[i][0]; m.classList.toggle('hit', hit); if (hit) cut = TIERS[i][1] })
        const nx = TIERS.find(([t]) => total < t)
        tip.innerHTML = !nx ? `已享最高优惠，立减 <b>¥${cut}</b>` : cut ? `已减 <b>¥${cut}</b>，再买 <b>¥${nx[0] - total}</b> 可减 ¥${nx[1]}` : `再买 <b>¥${nx[0] - total}</b> 立减 ¥${nx[1]}`
        root.querySelector('[data-cart]').textContent = '¥' + total; root.querySelector('[data-cut]').textContent = cut; root.querySelector('[data-pay]').textContent = '¥' + (total - cut)
      }
      upd()
      root.addEventListener('click', (e) => {
        const b = e.target.closest('[data-add]'); if (!b) return
        const it = b.closest('.it'), on = it.classList.toggle('in'); b.className = on ? 'sb off' : 'sb gh'; b.textContent = on ? '已加购' : '加购'; b.disabled = false
        upd()
      })
    },
  })

  /* ================================================================
   * 会员与个人中心 MEM
   * ================================================================ */
  guide('mp', 'MEM', [
    ['个人中心顶部', '个人中心头部', '未登录引导一键登录，已登录展示头像、等级和核心数据；两态高度一致，切换不跳动'],
    ['展示等级与升级进度', '会员等级进度卡', '成长值和可花的积分分开显示，“距下一级还差多少”一句话说清，节点可点开看权益'],
    ['积分流水、对账', '积分明细列表', '获得与消耗分开筛选，即将过期的积分提示放最上面；滚动加载，到底写“没有更多了”'],
    ['每日留存、拉活跃', '月度签到日历 / 成长任务列表', '连续天数 + 里程碑奖励，签到后立刻看见变化；任务用“去完成、领取、已领取”三态'],
    ['介绍会员权益', '会员权益宫格', '没解锁的权益也展示并写明解锁条件，是升级的动力；点开看一句话说明'],
    ['订单与售后入口', '我的订单入口行', '五个固定入口 + 角标；有在途包裹时把物流提示放在下面，点开看轨迹'],
    ['账号与通用设置', '设置列表', '开关直接生效并轻提示；清缓存、检查更新要有进行中与结果；退出登录必须二次确认'],
  ])

  /* ---------- MP-MEM-001 个人中心头部 ---------- */
  def({
    id: 'MP-MEM-001', name: '个人中心头部', style: '登录两态',
    fit: '“我的”页顶部；未登录引导一键登录，已登录显示头像、昵称、等级和积分/券/收藏等核心数字',
    avoid: '未登录也展示一堆 0；头像用文字或首字母（默认用卡通动物）；两态高度不同导致页面跳动',
    kw: '个人中心 我的 头部 登录 未登录 已登录 头像 昵称 等级 profile header login',
    css: CSS('MP-MEM-001', `&{width:340px}
& .dm{display:flex;align-items:center;justify-content:space-between;margin:0 4px 10px;font-size:12px;color:var(--ink3)}& .dm div{display:flex;padding:2px;border-radius:12px;background:var(--n6)}& .dm button{position:relative;height:28px;padding:0 12px;border-radius:8px;font-size:12px;color:var(--ink2);font-weight:600}& .dm button::after{content:"";position:absolute;inset:-8px -2px}& .dm .on{background:var(--lift);color:var(--ink);box-shadow:0 1px 4px var(--sh14)}
& .cd{position:relative;padding:18px 16px 14px;border-radius:22px;background:linear-gradient(180deg,var(--pm) 0,var(--pt) 58%,var(--card) 100%);box-shadow:0 10px 26px var(--sh08)}
& .tp{display:flex;align-items:center;gap:12px}
& .ava{width:64px;height:64px;flex:none;border-radius:50%;background:var(--card);box-shadow:0 0 0 3px var(--card),0 4px 10px var(--sh10);display:flex;align-items:center;justify-content:center;color:var(--ink3);overflow:hidden}& .ava .ui{width:32px;height:32px}
& .id{flex:1;min-width:0}& .id h3{margin:0;display:flex;align-items:center;gap:8px;font-size:18px;line-height:24px;font-weight:600}& .id h3 span{${ELL}}& .id p{margin:4px 0 0;font-size:12px;line-height:16px;color:var(--ink3);${ELL}}
& .lv{flex:none;display:inline-flex;align-items:center;gap:3px;height:24px;padding:0 8px;border-radius:12px;background:${GOLD.bg};color:${GOLD.fg};font-size:12px;font-weight:600}& .lv svg{width:14px;height:14px}
& .acts{display:flex;flex:none;gap:0;align-self:flex-start;margin:-6px -8px 0 0}& .acts button{position:relative;width:44px;height:44px;display:flex;align-items:center;justify-content:center;color:var(--ink)}& .acts svg{width:22px;height:22px}& .acts i{position:absolute;right:11px;top:10px;width:8px;height:8px;border-radius:50%;background:var(--hot);box-shadow:0 0 0 2px var(--card)}
& .bx1{min-height:76px;margin-top:14px;display:flex;flex-direction:column;justify-content:center}
& .stats{display:grid;grid-template-columns:repeat(4,1fr);padding:12px 0;border-radius:16px;background:var(--card)}& .stats button{display:flex;flex-direction:column;align-items:center;gap:2px;font-size:12px;color:var(--ink3);border-left:1px solid var(--line)}& .stats button:first-child{border-left:0}& .stats b{font-size:18px;line-height:24px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
& .tip{margin:8px 0 0;text-align:center;font-size:12px;color:var(--ink3)}
&:not(.in) [data-in],&.in [data-out]{display:none}
${PB}${SPIN}`),
    html: () => `<div class="mpmem001"><div class="dm"><span>预览状态</span><div data-ix="radio"><button type="button" class="on" data-o="out">未登录</button><button type="button" data-o="in">已登录</button></div></div><div class="cd"><div class="tp"><span class="ava" data-out><i class="ui">${sv('user')}</i></span><span class="ava" data-in>${critter(1, 64)}</span><div class="id"><div data-out><h3>登录 / 注册</h3><p>登录后查看积分、优惠券与订单</p></div><div data-in><h3><span>林小满</span><i class="lv">${sv('mgcrown')}金卡会员</i></h3><p>ID 8820 3417 · 已加入 326 天</p></div></div><div class="acts" data-in><button type="button" data-toast="3 条新消息" aria-label="消息">${sv('bell')}<i></i></button><button type="button" data-toast="进入设置" aria-label="设置">${sv('gear')}</button></div></div><div class="bx1"><div data-out><button class="pb" type="button" data-login>微信一键登录</button><p class="tip">登录即表示同意《用户协议》《隐私政策》</p></div><div class="stats" data-in><button type="button" data-toast="进入积分明细"><b>2,360</b>积分</button><button type="button" data-toast="进入卡券包"><b>4</b>优惠券</button><button type="button" data-toast="进入我的收藏"><b>18</b>收藏</button><button type="button" data-toast="进入浏览足迹"><b>56</b>足迹</button></div></div></div></div>`,
    js: (root) => {
      const box = root.querySelector('.mpmem001'), set = (on) => { box.classList.toggle('in', on); root.querySelectorAll('.dm [data-o]').forEach((b) => b.classList.toggle('on', (b.dataset.o === 'in') === on)) }
      root.querySelector('.dm').addEventListener('click', (e) => { const b = e.target.closest('[data-o]'); if (b) set(b.dataset.o === 'in') })
      root.querySelector('[data-login]').addEventListener('click', (e) => {
        const b = e.currentTarget; b.disabled = true; b.innerHTML = '<span class="sp"></span>登录中…'
        later(root, 700, () => { b.disabled = false; b.textContent = '微信一键登录'; set(true); IX.toast(root, '登录成功') })
      })
    },
  })

  /* ---------- MP-MEM-002 会员等级进度卡 ---------- */
  const LVD = [['普通', 0, ['新人专享券', '生日祝福']], ['银卡', 500, ['9 折会员价', '每月 1 张免邮券', '积分 1.2 倍']], ['金卡', 1500, ['8.5 折会员价', '每月 2 张免邮券', '积分 1.5 倍', '生日礼券']], ['铂金', 3000, ['8 折会员价', '全年免邮', '积分 2 倍', '专属客服']]]
  const LVX = [0, 500 / 3000 * 100, 50, 100]
  def({
    id: 'MP-MEM-002', name: '会员等级进度卡', style: '节点进度',
    fit: '会员中心首屏、个人中心下方；展示当前等级、成长值、距下一级还差多少，点节点看各级权益',
    avoid: '把成长值和可花的积分混在一起显示；等级超过 5 档；不说明成长值怎么来',
    kw: '会员 等级 成长值 进度 升级 铂金 金卡 level progress membership 权益 节点',
    css: CSS('MP-MEM-002', `${CARD()}&{padding:16px}
& .top{display:flex;align-items:center;gap:12px}& .top .bd{width:44px;height:44px;flex:none;border-radius:50%;background:${GOLD.bg};color:${GOLD.fg};padding:11px}& .top .t{flex:1;min-width:0}& .top .t b{display:block;font-size:18px;line-height:24px;font-weight:600}& .top .t span{font-size:12px;color:var(--ink3)}& .top .t em{color:var(--ink);font-weight:600}
& .top .pt{flex:none;display:flex;align-items:center;gap:4px;height:28px;padding:0 10px;border-radius:12px;background:var(--pt);color:var(--p-text);font-size:12px;font-weight:600}& .top .pt svg{width:14px;height:14px}
& .nx{margin:14px 0 0;font-size:14px;color:var(--ink2)}& .nx b{font-weight:600;color:var(--p-text)}
& .rw{position:relative;height:8px;margin:44px 6px 0;border-radius:4px;background:var(--n4)}& .rw .f{position:absolute;left:0;top:0;bottom:0;border-radius:4px;background:linear-gradient(90deg,var(--ga),var(--gb))}
& .you{position:absolute;top:-34px;transform:translateX(-50%);height:24px;padding:0 8px;border-radius:12px;background:var(--pd);color:#fff;font-size:12px;line-height:24px;font-weight:600;white-space:nowrap}& .you::after{content:"";position:absolute;left:50%;bottom:-4px;width:8px;height:8px;margin-left:-4px;background:var(--pd);transform:rotate(45deg)}
& .nd{position:absolute;top:-8px;left:var(--x);transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:8px;font-size:12px;line-height:16px;color:var(--ink3);white-space:nowrap}& .nd::after{content:"";position:absolute;inset:-6px -10px -4px}
& .nd i{width:16px;height:16px;border-radius:50%;background:var(--card);box-shadow:inset 0 0 0 2px var(--n8);display:flex;align-items:center;justify-content:center;color:#fff}& .nd i svg{width:10px;height:10px;opacity:0}
& .nd.ps i{background:var(--p);box-shadow:none}& .nd.ps i svg{opacity:1}& .nd.cu{color:var(--ink);font-weight:600}& .nd.on{color:var(--p-text);font-weight:600}& .nd.on i{box-shadow:0 0 0 3px var(--pm)}
& .nd.a{transform:translateX(-8px);align-items:flex-start}& .nd.z{transform:translateX(calc(-100% + 8px));align-items:flex-end}
& .pn{margin:44px 0 14px;padding:12px;border-radius:12px;background:var(--pt)}& .pn .pk{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;font-size:14px}& .pn .pk b{font-weight:600;color:var(--p-text)}& .pn .pk span{display:flex;align-items:center;gap:4px;font-size:12px;color:var(--ink2)}& .pn .pk svg{width:14px;height:14px}
& .pn ul{margin:0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:8px}& .pn li{height:24px;padding:0 8px;border-radius:8px;background:var(--card2);font-size:12px;line-height:24px;color:var(--ink2)}
${PB}`),
    html: () => `<div class="mpmem002"><div class="top"><span class="bd">${sv('mgcrown')}</span><div class="t"><b>金卡会员</b><span>成长值 <em>1,860</em></span></div><span class="pt">${sv('mgcoin')}积分 2,360</span></div><p class="nx">距铂金还差 <b>1,140</b> 成长值</p><div data-ix="tabs"><div class="rw"><i class="f" style="width:62%"></i><span class="you" style="left:62%">1,860</span>${LVD.map(([n, v], i) => `<button type="button" class="nd ${i < 3 ? 'ps' : ''} ${i === 2 ? 'cu on' : ''} ${i === 0 ? 'a' : i === 3 ? 'z' : ''}" style="--x:${LVX[i]}%" data-t="n${i}"><i>${sv('check')}</i>${n}</button>`).join('')}</div></div>${LVD.map(([n, v, bs], i) => `<div class="pn" data-p="n${i}" ${i === 2 ? '' : 'hidden'}><div class="pk"><b>${n} · 成长值满 ${nf(v)}</b><span>${i <= 2 ? `${sv('checkc')}${i === 2 ? '当前等级' : '已达成'}` : `${sv('lock')}还差 1,140`}</span></div><ul>${bs.map((x) => `<li>${x}</li>`).join('')}</ul></div>`).join('')}<button class="pb" type="button" data-toast="去做任务赚成长值">去做任务赚成长值</button></div>`,
  })

  /* ---------- MP-MEM-003 积分明细列表 ---------- */
  const PTS0 = [['11 月'], ['每日签到', 'mgcheckin', '11-04 08:12', 10], ['订单完成奖励（含双 11 活动加赠）', 'bag', '11-03 19:40', 128], ['积分兑换 · 手作釉面马克杯', 'giftbox', '11-02 15:26', -800], ['晒单评价', 'chat', '11-01 21:05', 20], ['10 月'], ['邀请好友注册奖励', 'users', '10-28 10:03', 50], ['积分抵现 · 订单 SO2026102851', 'wallet2', '10-27 20:11', -300]]
  const PTS1 = [[['每日签到', 'mgcheckin', '10-27 08:20', 10], ['过期积分清理', 'hourglass', '10-01 00:00', -120], ['9 月'], ['订单完成奖励', 'bag', '09-26 18:32', 86]], [['生日礼积分', 'giftbox', '09-12 00:00', 100], ['每日签到', 'mgcheckin', '09-11 09:41', 10], ['每日签到', 'mgcheckin', '09-10 08:57', 10]]]
  const ptRow = (r) => r.length === 1 ? `<div class="mo" data-k="in out">${r[0]}</div>` : `<div class="ro" data-k="${r[3] > 0 ? 'in' : 'out'}"><span class="ic">${sv(r[1])}</span><div class="tx"><b>${r[0]}</b><span>${r[2]}</span></div><em class="${r[3] > 0 ? 'up' : ''}">${r[3] > 0 ? '+' : '−'}${Math.abs(r[3])}</em></div>`
  def({
    id: 'MP-MEM-003', name: '积分明细列表', style: '滚动加载',
    fit: '积分流水页；顶部可用积分与即将过期提示，获得/消耗分开筛选，滚动到底自动加载更多',
    avoid: '用页码翻页（列表一律滚动加载）；消耗和获得用不同的大色块（用 +/− 与文字色区分即可）；不写过期时间',
    kw: '积分 明细 流水 记录 获得 消耗 过期 滚动加载 points ledger history 账单',
    css: CSS('MP-MEM-003', `${CARD()}&{padding:16px 0 0;overflow:hidden}
& .sum{display:flex;align-items:flex-end;justify-content:space-between;padding:0 16px}& .sum small{display:block;font-size:12px;color:var(--ink3)}& .sum b{font-size:32px;line-height:38px;font-weight:700;font-variant-numeric:tabular-nums}
& .wn{margin:10px 16px 0;display:flex;align-items:center;gap:6px;padding:8px 12px;border-radius:12px;background:var(--warn-bg);color:var(--warn);font-size:12px;line-height:16px}& .wn svg{width:16px;height:16px;flex:none}
& .tb{display:flex;gap:8px;padding:12px 16px 4px}& .tb button{position:relative;height:32px;padding:0 14px;border-radius:16px;background:var(--n3);font-size:14px;color:var(--ink2);transition:background-color .2s,color .2s}& .tb button::after{content:"";position:absolute;inset:-6px -2px}& .tb .on{background:var(--p);color:#fff;font-weight:600}
& .sc{max-height:330px;overflow-y:auto;padding:0 16px;scrollbar-width:thin;scrollbar-color:var(--n8) transparent}
& .mo{padding:12px 0 4px;font-size:12px;font-weight:600;color:var(--ink3)}
& .ro{display:flex;align-items:center;gap:12px;min-height:60px;border-bottom:1px solid var(--line)}& .ro:last-child{border-bottom:0}
& .ic{width:40px;height:40px;flex:none;border-radius:12px;background:var(--pt);color:var(--p-text);padding:10px}& .tx{flex:1;min-width:0}& .tx b{display:block;font-size:14px;line-height:20px;font-weight:600;${ELL}}& .tx span{font-size:12px;color:var(--ink3)}
& .ro em{flex:none;min-width:48px;text-align:right;font-size:16px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}& .ro em.up{color:var(--ok)}
& .ft{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;height:44px;font-size:12px;color:var(--ink3)}
${SPIN}`),
    html: () => `<div class="mpmem003"><div class="sum"><div><small>可用积分</small><b>2,360</b></div></div><div class="wn">${sv('hourglass')}<span>120 积分将于 12-31 过期，尽快使用</span></div><div class="tb" data-ix="tabs" data-list=".lst"><button class="on" type="button" data-t="all">全部</button><button type="button" data-t="in">获得</button><button type="button" data-t="out">消耗</button></div><div class="sc" data-sc><div class="lst">${PTS0.map(ptRow).join('')}</div><button class="ft" type="button" data-more>上滑或点击加载更多</button></div></div>`,
    js: (root) => {
      const sc = root.querySelector('[data-sc]'), list = root.querySelector('.lst'), ft = root.querySelector('[data-more]')
      let n = 0, busy = false
      const load = () => {
        if (busy || n >= PTS1.length) return
        busy = true; ft.innerHTML = '<span class="sp"></span>加载中…'
        later(root, 600, () => {
          list.insertAdjacentHTML('beforeend', PTS1[n++].map(ptRow).join(''))
          const on = root.querySelector('.tb .on'), key = on ? on.dataset.t : 'all'
          if (key !== 'all') [...list.children].forEach((it) => { it.hidden = !(it.dataset.k || '').split(' ').includes(key) })
          busy = false; ft.textContent = n >= PTS1.length ? '没有更多了' : '上滑或点击加载更多'; if (n >= PTS1.length) ft.disabled = true
        })
      }
      sc.addEventListener('scroll', () => { if (sc.scrollTop + sc.clientHeight >= sc.scrollHeight - 24) load() })
      ft.addEventListener('click', load)
    },
  })

  /* ---------- MP-MEM-004 月度签到日历 ---------- */
  const SIGNED0 = [1, 2, 3], TODAY = 4, MILE = { 7: 50, 14: 80, 21: 100, 30: 200 }
  def({
    id: 'MP-MEM-004', name: '月度签到日历', style: '连续签到',
    fit: '签到页、个人中心签到入口；整月日历看已签与漏签，点“签到”立刻变已签并累加连续天数和积分',
    avoid: '连续中断后清零过重（可保留“补签卡”）；奖励无法兑现；把今天之前未签的日子标成红色指责用户',
    kw: '签到 日历 连续签到 打卡 里程碑 积分 check-in calendar streak 月历',
    css: CSS('MP-MEM-004', `${CARD()}&{padding:16px}
${HEAD}& .hd b{display:block;font-size:18px;line-height:24px}& .hd b em{padding:0 2px;font-size:22px;font-weight:600;color:var(--p-text)}& .hd b small{display:block;margin-top:2px;font-size:12px;color:var(--ink3);font-weight:400}
& .pt{display:flex;align-items:center;gap:4px;height:28px;padding:0 10px;border-radius:12px;background:var(--pt);color:var(--p-text);font-size:12px;font-weight:600;font-variant-numeric:tabular-nums}& .pt svg{width:14px;height:14px}
& .gp{height:6px;margin:14px 0 4px;border-radius:3px;background:var(--n4)}& .gp i{display:block;height:100%;border-radius:3px;background:linear-gradient(90deg,var(--ga),var(--gb));transition:width .4s cubic-bezier(.2,0,0,1)}& .gt{display:flex;justify-content:space-between;font-size:12px;color:var(--ink3)}
& .mh{margin:14px 0 4px;display:flex;justify-content:space-between;align-items:center;font-size:14px;font-weight:600}& .mh span{font-size:12px;font-weight:400;color:var(--ink3)}
& .cal{display:grid;grid-template-columns:repeat(7,1fr);justify-items:center}& .wk{height:28px;display:flex;align-items:center;font-size:12px;color:var(--ink3)}
& .dy{position:relative;width:44px;height:44px;display:flex;align-items:center;justify-content:center;font-size:14px;color:var(--ink)}& .dy .n{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;transition:background-color .2s,color .2s}& .dy .n svg{width:16px;height:16px}
& .dy.f{color:var(--ink3)}& .dy.g .n{background:${GOLD.bg};color:${GOLD.fg}}& .dy.g .n svg{width:18px;height:18px}
& .dy.s .n{background:var(--pt);color:var(--p-text)}& .dy.t .n{box-shadow:inset 0 0 0 1.5px var(--p);color:var(--p-text);font-weight:600}
& .dy.pop .n{animation:§pop .35s cubic-bezier(.2,0,0,1)}@keyframes §pop{0%{transform:scale(.6)}60%{transform:scale(1.12)}100%{transform:scale(1)}}
& .ft{margin-top:10px}${PB}${SPIN}`),
    html: () => {
      const cells = Array.from({ length: 30 }, (_, i) => i + 1).map((d) => {
        const s = SIGNED0.includes(d), t = d === TODAY, g = MILE[d]
        return `<button class="dy ${s ? 's' : t ? 't' : 'f'} ${g ? 'g' : ''}" type="button" data-d="${d}" ${t ? 'data-today' : ''} ${g ? `title="连续到这天额外 +${g} 积分"` : ''}><span class="n">${s ? sv('check') : g ? sv('giftbox') : d}</span></button>`
      }).join('')
      return `<div class="mpmem004"><div class="hd"><b>已连续签到 <em data-streak>3</em> 天<small>今日签到 +10 积分，满 7 天额外 +50</small></b><span class="pt">${sv('mgcoin')}<i data-pts>2,360</i></span></div><div class="gp"><i data-gp style="width:${3 / 7 * 100}%"></i></div><div class="gt"><span data-gtx>再签 4 天领 7 日礼包</span><span data-gt>3 / 7</span></div><div class="mh">2026 年 11 月<span>金色格子为里程碑奖励</span></div><div class="cal">${['日', '一', '二', '三', '四', '五', '六'].map((w) => `<span class="wk">${w}</span>`).join('')}${cells}</div><div class="ft"><button class="pb" type="button" data-sign>今日签到 +10 积分</button></div></div>`
    },
    js: (root) => {
      const btn = root.querySelector('[data-sign]'), today = root.querySelector('[data-today]'), st = root.querySelector('[data-streak]'), gp = root.querySelector('[data-gp]'), gtx = root.querySelector('[data-gtx]'), gt = root.querySelector('[data-gt]'), pts = root.querySelector('[data-pts]')
      let signed = false
      const sign = () => {
        if (signed || btn.disabled) return
        btn.disabled = true; btn.innerHTML = '<span class="sp"></span>签到中…'
        later(root, 500, () => {
          signed = true; today.className = 'dy s pop'; today.querySelector('.n').innerHTML = sv('check'); today.removeAttribute('data-today')
          st.textContent = 4; gp.style.width = (4 / 7 * 100) + '%'; gtx.textContent = '再签 3 天领 7 日礼包'; gt.textContent = '4 / 7'
          tween(2360, 2370, 500, (v) => { pts.textContent = nf(v) })
          btn.className = 'pb ok'; btn.textContent = '今日已签到，明天继续 +10'; IX.toast(root, '签到成功 +10 积分')
        })
      }
      btn.addEventListener('click', sign)
      today.addEventListener('click', sign)
    },
  })

  /* ---------- MP-MEM-005 成长任务列表 ---------- */
  const TASKS = [['每日签到', 'mgcheckin', '每日 1 次', 10, 'done'], ['浏览商品满 30 秒', 'eye', '今日已完成', 5, 'ready'], ['分享商品给好友', 'share', '每日 1 次', 10, 'todo'], ['完成一笔订单', 'bag', '本月 0/1', 30, 'todo'], ['邀请好友注册并完成首单（每邀请 1 位可领一次）', 'users', '已邀请 0 位', 50, 'todo']]
  const tkBtn = (st) => st === 'done' ? '<button class="sb off" type="button" disabled data-act="done">已领取</button>' : st === 'ready' ? '<button class="sb" type="button" data-act="ready">领取</button>' : '<button class="sb gh" type="button" data-act="todo">去完成</button>'
  def({
    id: 'MP-MEM-005', name: '成长任务列表', style: '三态按钮',
    fit: '成长值、积分任务页；每行一个任务，奖励写在旁边，按钮三态：去完成、领取、已领取，顶部实时汇总',
    avoid: '任务描述超过两行；完成后不给反馈直接消失；“去完成”跳转后回来状态没更新',
    kw: '任务 成长任务 去完成 领取 奖励 积分任务 task list reward 成长值 日常任务',
    css: CSS('MP-MEM-005', `${CARD()}&{padding:16px 16px 6px}${HEAD}& .hd span b{font-size:14px;font-weight:600;color:var(--p-text)}
& .ls{margin-top:6px}& .tk{display:flex;align-items:center;gap:12px;min-height:64px;border-bottom:1px solid var(--line)}& .tk:last-child{border-bottom:0}
& .ic{width:40px;height:40px;flex:none;border-radius:12px;background:var(--pt);color:var(--p-text);padding:10px;transition:background-color .2s}& .tk.done .ic{background:var(--soft);color:var(--ink3)}
& .tx{flex:1;min-width:0}& .tx b{display:block;font-size:14px;line-height:20px;font-weight:600;${ELL}}& .tx span{font-size:12px;color:var(--ink3)}& .tx em{font-weight:600;color:var(--p-text)}
${SB}${SPIN}`),
    html: () => `<div class="mpmem005"><div class="hd"><b>今日任务</b><span>已领 <b data-got>10</b> · 待领 <b data-wait>5</b> 成长值</span></div><div class="ls">${TASKS.map(([t, ic, d, v, st]) => `<div class="tk ${st === 'done' ? 'done' : ''}" data-v="${v}" data-st="${st}"><span class="ic">${sv(ic)}</span><div class="tx"><b>${t}</b><span><em>+${v} 成长值</em> · ${d}</span></div>${tkBtn(st)}</div>`).join('')}</div></div>`,
    js: (root) => {
      const got = root.querySelector('[data-got]'), wait = root.querySelector('[data-wait]')
      const sum = () => { let g = 0, w = 0; root.querySelectorAll('.tk').forEach((r) => { if (r.dataset.st === 'done') g += +r.dataset.v; if (r.dataset.st === 'ready') w += +r.dataset.v }); got.textContent = g; wait.textContent = w }
      sum()
      root.addEventListener('click', (e) => {
        const b = e.target.closest('[data-act]'); if (!b || b.disabled) return
        const row = b.closest('.tk'), st = row.dataset.st
        if (st === 'todo') {
          b.disabled = true; b.innerHTML = '<span class="sp"></span>'
          later(root, 800, () => { row.dataset.st = 'ready'; b.disabled = false; b.className = 'sb'; b.dataset.act = 'ready'; b.textContent = '领取'; sum(); IX.toast(root, '任务完成，快去领取奖励') })
        } else if (st === 'ready') {
          b.disabled = true; b.innerHTML = '<span class="sp"></span>'
          later(root, 450, () => { row.dataset.st = 'done'; row.classList.add('done'); b.className = 'sb off'; b.dataset.act = 'done'; b.textContent = '已领取'; b.disabled = true; sum(); IX.toast(root, `+${row.dataset.v} 成长值`) })
        }
      })
    },
  })

  /* ---------- MP-MEM-006 会员权益宫格 ---------- */
  const BNF = [['scooter', '包邮特权', 0, '每月免邮券，铂金全年免邮'], ['coupon', '专属优惠券', 0, '每月 1 次领取会员专享券'], ['giftbox', '生日礼', 1, '生日当月赠送礼券与双倍积分'], ['star', '积分加速', 1, '消费积分 1.5 倍，铂金 2 倍'], ['giftcard', '礼卡兑换', 2, '积分可按 1:1 兑换礼卡'], ['wallet', '储值赠送', 2, '储值满额加赠 10%']]
  const BLV = ['银卡', '金卡', '铂金']
  def({
    id: 'MP-MEM-006', name: '会员权益宫格', style: '解锁态',
    fit: '会员中心、开通会员页；3 × 2 展示权益，切换等级看解锁情况，点权益看一句话说明',
    avoid: '只展示已解锁的（没有升级动力）；权益名超过 5 个字；没解锁的不写条件',
    kw: '会员权益 权益 宫格 解锁 等级 免邮 生日礼 积分加速 benefit privilege grid 特权',
    css: CSS('MP-MEM-006', `${CARD()}&{padding:16px}${HEAD}
& .lvs{display:flex;padding:2px;border-radius:12px;background:var(--soft)}& .lvs button{position:relative;height:28px;padding:0 12px;border-radius:8px;font-size:12px;color:var(--ink2);font-weight:600}& .lvs button::after{content:"";position:absolute;inset:-8px -2px}& .lvs .on{background:var(--lift);color:var(--ink);box-shadow:0 1px 4px var(--sh14)}
& .gr{display:grid;grid-template-columns:repeat(3,1fr);gap:14px 8px;margin:16px 0 14px}
& .bn{position:relative;display:flex;flex-direction:column;align-items:center;gap:4px;padding:8px 0;border-radius:12px;font-size:14px;font-weight:600;color:var(--ink);transition:background-color .2s}& .bn .tile{width:56px;height:56px}& .bn small{font-size:12px;font-weight:400;color:var(--p-text)}
& .bn.on{background:var(--pt)}& .bn.lkd .tile{opacity:.42;filter:grayscale(.6)}& .bn.lkd{color:var(--ink3)}& .bn.lkd small{color:var(--ink3)}
& .bn .lc{position:absolute;left:50%;top:44px;margin-left:12px;width:22px;height:22px;border-radius:50%;background:var(--card);box-shadow:0 1px 4px var(--sh20);color:var(--ink2);padding:4px;display:none}& .bn.lkd .lc{display:block}
& .dt{padding:12px 14px;border-radius:12px;background:var(--n2)}& .dt b{font-size:14px;font-weight:600;color:var(--p-text)}& .dt p{margin:4px 0 0;font-size:14px;line-height:1.6;color:var(--ink2)}`),
    html: () => `<div class="mpmem006"><div class="hd"><b>会员权益</b><div class="lvs" data-ix="radio">${BLV.map((n, i) => `<button type="button" data-o="${i}" class="${i === 1 ? 'on' : ''}">${n}</button>`).join('')}</div></div><div class="gr">${BNF.map(([ic, n, mn, d], i) => `<button class="bn" type="button" data-i="${i}" data-min="${mn}"><span class="tile tile-sq">${IC(ic)}</span>${n}<small></small><span class="lc">${sv('lock')}</span></button>`).join('')}</div><div class="dt"><b data-dt></b><p data-dd></p></div></div>`,
    js: (root) => {
      let lv = 1, sel = 0
      const bns = [...root.querySelectorAll('.bn')], dt = root.querySelector('[data-dt]'), dd = root.querySelector('[data-dd]')
      const paint = () => {
        bns.forEach((b, i) => { const lk = +b.dataset.min > lv; b.classList.toggle('lkd', lk); b.querySelector('small').textContent = lk ? `${BLV[+b.dataset.min]}解锁` : '已解锁'; b.classList.toggle('on', i === sel && !lk) })
        const [, n, mn, d] = BNF[sel], lk = mn > lv
        dt.textContent = lk ? `${n} · ${BLV[mn]}及以上可享` : n; dd.textContent = d
      }
      paint()
      root.querySelector('.lvs').addEventListener('click', (e) => { const b = e.target.closest('[data-o]'); if (!b) return; lv = +b.dataset.o; paint() })
      root.querySelector('.gr').addEventListener('click', (e) => { const b = e.target.closest('.bn'); if (!b) return; sel = +b.dataset.i; if (+b.dataset.min > lv) IX.toast(root, `${BLV[+b.dataset.min]}及以上解锁`); paint() })
    },
  })

  /* ---------- MP-MEM-007 我的订单入口行 ---------- */
  const ODR = [['wallet2', '待付款', 2], ['box', '待发货', 0], ['truck', '待收货', 1], ['star', '待评价', 120], ['refresh', '退款/售后', -1]]
  def({
    id: 'MP-MEM-007', name: '我的订单入口行', style: '角标+物流',
    fit: '个人中心的订单区；五个固定状态入口带数字/圆点角标，下方一行在途物流提示，点开看轨迹',
    avoid: '入口超过 5 个；角标数字超过 99 不收敛（显示 99+）；订单状态入口又在别处重复放一份',
    kw: '订单 入口 待付款 待发货 待收货 待评价 售后 角标 物流 order entry badge 个人中心',
    css: CSS('MP-MEM-007', `${CARD()}&{padding:16px 16px 4px}${HEAD}& .all{position:relative;display:flex;align-items:center;gap:2px;font-size:12px;color:var(--ink3)}& .all::after{content:"";position:absolute;inset:-14px -8px}& .all svg{width:12px;height:12px}
& .en{display:grid;grid-template-columns:repeat(5,1fr);margin:6px 0 8px}& .e{display:flex;flex-direction:column;align-items:center;gap:6px;min-height:64px;padding-top:10px;border-radius:12px;font-size:12px;color:var(--ink2);transition:background-color .15s}& .e:active{background:var(--soft)}
& .e .ic{position:relative;width:28px;height:28px;color:var(--ink)}
& .bd{position:absolute;left:16px;top:-8px;min-width:18px;height:18px;padding:0 5px;border-radius:12px;background:var(--hot);color:#fff;font-size:12px;line-height:18px;font-weight:600;text-align:center;box-shadow:0 0 0 2px var(--card)}& .bd.dot{left:22px;top:-3px;min-width:0;width:10px;height:10px;padding:0}
& .tkr{border-top:1px solid var(--line)}& .th{display:flex;align-items:center;gap:12px;width:100%;min-height:60px;text-align:left}& .th .ti{width:36px;height:36px;flex:none;border-radius:12px;background:var(--pt);color:var(--p-text);padding:8px}& .th .tx{flex:1;min-width:0}& .th b{display:block;font-size:14px;line-height:20px;font-weight:600}& .th .tx span{display:block;font-size:12px;color:var(--ink3);${ELL}}
& .th .ch{width:16px;height:16px;flex:none;color:var(--ink3);transition:transform .25s cubic-bezier(.2,0,0,1)}& .ix-ai.open .th .ch{transform:rotate(90deg)}
& .tm{margin:0 0 12px 18px;padding:2px 0 0 18px;border-left:2px solid var(--pm);display:flex;flex-direction:column;gap:12px}& .tm li{position:relative;list-style:none;font-size:12px;line-height:18px;color:var(--ink3)}& .tm li b{display:block;font-size:14px;line-height:20px;font-weight:400;color:var(--ink2)}& .tm li::before{content:"";position:absolute;left:-23px;top:6px;width:8px;height:8px;border-radius:50%;background:var(--pm)}& .tm li:first-child::before{background:var(--p)}& .tm li:first-child b{color:var(--ink);font-weight:600}`),
    html: () => `<div class="mpmem007"><div class="hd"><b>我的订单</b><button class="all" type="button" data-toast="进入全部订单">全部订单${sv('chev')}</button></div><div class="en">${ODR.map(([ic, n, c]) => `<button class="e" type="button" data-toast="进入${n}订单${c > 0 ? `（${c > 99 ? '99+' : c}）` : ''}"><span class="ic">${sv(ic)}${c > 0 ? `<i class="bd">${c > 99 ? '99+' : c}</i>` : c < 0 ? '<i class="bd dot"></i>' : ''}</span>${n}</button>`).join('')}</div><div class="tkr" data-ix="acc"><div class="ix-ai"><button class="th" type="button" data-h><span class="ti">${sv('truck')}</span><div class="tx"><b>包裹正在派送中</b><span>快递员已出发，预计今天 18:00 前送达</span></div><span class="ch">${sv('chev')}</span></button><div class="ix-ab"><div><ul class="tm"><li><b>快递员已出发，请保持电话畅通</b>今天 14:30</li><li><b>包裹已到达上海浦东转运中心</b>今天 08:46</li><li><b>商家已发货，等待快递揽收</b>11-03 22:10</li></ul></div></div></div></div></div>`,
  })

  /* ---------- MP-MEM-008 设置列表 ---------- */
  def({
    id: 'MP-MEM-008', name: '设置列表', style: '开关直接生效',
    fit: '“我的”里的设置页；分组列表：账号、通知开关、通用（清缓存、检查更新）、退出登录',
    avoid: '开关要点“保存”才生效；清缓存/检查更新没有进行中与结果；退出登录一点就退（要二次确认）',
    kw: '设置 开关 通知 清除缓存 检查更新 退出登录 账号 settings switch list 偏好',
    css: CSS('MP-MEM-008', `&{position:relative;width:340px;padding:12px;border-radius:22px;background:var(--n3);box-shadow:0 10px 26px var(--sh08);overflow:hidden}
& .gp{margin-bottom:12px;padding:0 14px;border-radius:16px;background:var(--card)}& .gp h5{margin:0;padding:12px 0 0;font-size:12px;font-weight:600;color:var(--ink3)}
& .rw{position:relative;display:flex;align-items:center;gap:10px;width:100%;min-height:52px;text-align:left;border-bottom:1px solid var(--line);font-size:14px}& .gp .rw:last-child{border-bottom:0}
& .rw .tx{flex:1;min-width:0}& .rw .tx b{display:block;font-weight:400;${ELL}}& .rw .tx small{display:block;font-size:12px;line-height:16px;color:var(--ink3)}
& .rw .v{flex:none;display:flex;align-items:center;gap:4px;font-size:14px;color:var(--ink3)}& .rw .v svg{width:16px;height:16px}
& .sw2{flex:none;position:relative;width:44px;height:24px;border-radius:12px;background:var(--n8);transition:background-color .2s cubic-bezier(.2,0,0,1)}& .sw2::before{content:"";position:absolute;left:2px;top:2px;width:20px;height:20px;border-radius:50%;background:var(--card);box-shadow:0 1px 3px rgba(31,35,41,.3);transition:transform .2s cubic-bezier(.2,0,0,1)}& .rw.on .sw2{background:var(--p)}& .rw.on .sw2::before{transform:translateX(20px)}
& .out{display:block;width:100%;height:48px;border-radius:16px;background:var(--card);color:var(--danger);font-size:16px;font-weight:600}
${PB}${SPIN}${DLG}& .ix-ov{align-items:center}& .dlg .pb{width:auto;flex:1}`),
    html: () => `<div class="mpmem008"><div class="gp"><h5>账号</h5><button class="rw" type="button" data-toast="修改手机号"><span class="tx"><b>手机号</b></span><span class="v">138****0000${sv('chev')}</span></button><button class="rw" type="button" data-toast="管理收货地址"><span class="tx"><b>收货地址</b></span><span class="v">${sv('chev')}</span></button><button class="rw" type="button" data-toast="账号与安全"><span class="tx"><b>账号与安全</b></span><span class="v">${sv('chev')}</span></button></div><div class="gp"><h5>通知</h5><button class="rw on" type="button" data-sw="订单与物流通知" role="switch" aria-checked="true"><span class="tx"><b>订单与物流通知</b><small>发货、派送、签收提醒</small></span><i class="sw2"></i></button><button class="rw" type="button" data-sw="优惠活动推送" role="switch" aria-checked="false"><span class="tx"><b>优惠活动推送</b><small>领券、会员日、限时活动</small></span><i class="sw2"></i></button><button class="rw on" type="button" data-sw="夜间免打扰" role="switch" aria-checked="true"><span class="tx"><b>夜间免打扰</b><small>22:00 – 08:00 不推送</small></span><i class="sw2"></i></button></div><div class="gp"><h5>通用</h5><button class="rw" type="button" data-cache><span class="tx"><b>清除缓存</b></span><span class="v" data-cv>23.4 MB</span></button><button class="rw" type="button" data-upd><span class="tx"><b>检查更新</b></span><span class="v" data-uv>当前 v2.4.1</span></button></div><button class="out" type="button" data-open="out" data-lo>退出登录</button><div class="ix-ov" data-ov="out"><div class="ix-mask"></div><div class="dlg"><h4>退出登录</h4><p>退出后将无法查看订单与积分，确定要退出吗？</p><div class="row"><button class="pb cx" type="button" data-close>取消</button><button class="pb" type="button" data-do>退出</button></div></div></div></div>`,
    js: (root) => {
      root.addEventListener('click', (e) => {
        const sw = e.target.closest('[data-sw]')
        if (sw) { const on = sw.classList.toggle('on'); sw.setAttribute('aria-checked', on); IX.toast(root, `${on ? '已开启' : '已关闭'}${sw.dataset.sw}`); return }
        const c = e.target.closest('[data-cache]')
        if (c && !c.dataset.busy) { const v = c.querySelector('[data-cv]'); if (v.textContent === '0 KB') { IX.toast(root, '没有可清理的缓存'); return } c.dataset.busy = '1'; v.innerHTML = '<span class="sp"></span>'; later(root, 800, () => { v.textContent = '0 KB'; delete c.dataset.busy; IX.toast(root, '已清除 23.4 MB 缓存') }); return }
        const u = e.target.closest('[data-upd]')
        if (u && !u.dataset.busy) { const v = u.querySelector('[data-uv]'); u.dataset.busy = '1'; v.innerHTML = '<span class="sp"></span>'; later(root, 900, () => { v.textContent = '已是最新版本'; delete u.dataset.busy }) }
      })
      root.querySelector('[data-do]').addEventListener('click', () => {
        root.querySelector('[data-ov]').classList.remove('show')
        const lo = root.querySelector('[data-lo]'); lo.removeAttribute('data-open'); lo.className = 'pb'; lo.textContent = '登录 / 注册'; lo.dataset.toast = '前往登录'
        IX.toast(root, '已退出登录')
      })
    },
  })

  /* ================================================================
   * 服务与预约 SVC
   * ================================================================ */
  guide('mp', 'SVC', [
    ['展示门店、选门店', '门店信息卡', '距离、营业状态、导航与电话放在一张卡里；休息中也要能看地址、打电话'],
    ['预约到店服务', '预约日期时段选择', '日期横滑 + 时段分组网格，约满、已过置灰并写明原因；选中后确认按钮才可点'],
    ['多个套餐 / 时长', '服务套餐选择', '选中态用主色描边加浅底，加购项可勾选，价格和时长随选择实时联动'],
    ['指定服务人员', '服务人员选择', '头像、职称、评分、最早可约时间一次给全，并保留“不指定”选项'],
    ['到店核销', '核销券码卡', '二维码与条形码可切换且自动刷新；待使用、已使用、已过期分开展示'],
    ['排队叫号', '取号排队进度卡', '前面还有几桌、预计等待、当前叫号三件事放首屏；轮到时变成醒目提示并给倒计时'],
    ['点单、外卖、到店自取', '点单菜品行与购物袋', '“加入”变步进器，购物袋数量和金额实时联动；没到起送价写清还差多少'],
  ])

  /* ---------- MP-SVC-001 门店信息卡 ---------- */
  const STORES = [
    ['静安寺旗舰店（地铁 2 号线 3 号口直达）', 'open', '营业中', '09:00 – 22:00', '静安区南京西路 1618 号 2 层 208 室', '1.2 km', ['可预约', '有停车位', '免费 WiFi'], '20% 50%'],
    ['世纪汇店', 'closed', '休息中', '明天 09:00 营业', '浦东新区世纪大道 1192 号 B1 层', '6.8 km', ['可预约', '有停车位'], '85% 40%'],
  ]
  def({
    id: 'MP-SVC-001', name: '门店信息卡', style: '距离+营业态',
    fit: '选门店页、附近门店列表、预约前选店；一张卡说清名称、营业状态、距离、地址，并直接导航或打电话',
    avoid: '休息中的门店直接隐藏（用户还想看地址和电话）；营业时间不写具体几点；整卡可点时卡内再放同目的地按钮',
    kw: '门店 店铺 附近门店 营业中 休息中 距离 导航 电话 地址 store card shop 营业状态',
    css: CSS('MP-SVC-001', `&{width:340px;display:flex;flex-direction:column;gap:12px}
& .cd{padding:12px;border-radius:16px;background:var(--card);box-shadow:0 8px 22px var(--sh08)}
& .tp{display:flex;gap:12px}& .im{flex:none;width:96px;height:96px;border-radius:12px;background-size:cover}& .closed .im{filter:grayscale(.55);opacity:.9}
& .in{flex:1;min-width:0;display:flex;flex-direction:column;gap:6px}
& .r1{display:flex;align-items:flex-start;gap:4px}& .r1 h4{flex:1;min-width:0;margin:0;font-size:16px;line-height:22px;font-weight:600;${CLAMP2}}
& .hrt{position:relative;flex:none;width:28px;height:28px;margin:-3px -4px 0 0;display:flex;align-items:center;justify-content:center;color:var(--ink3);transition:color .2s,transform .15s cubic-bezier(.2,0,0,1)}& .hrt::after{content:"";position:absolute;inset:-8px}& .hrt svg{width:20px;height:20px}& .hrt.on{color:var(--p-fg)}& .hrt.on svg{fill:currentColor}& .hrt:active{transform:scale(.9)}
& .r2{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--ink2)}
& .st2{flex:none;height:20px;padding:0 6px;border-radius:4px;font-size:12px;line-height:20px;font-weight:600;background:var(--ok-bg);color:var(--ok)}& .closed .st2{background:var(--soft);color:var(--ink3)}
& .ad{margin:0;display:flex;gap:4px;font-size:12px;line-height:18px;color:var(--ink3)}& .ad svg{width:14px;height:14px;flex:none;margin-top:2px}& .ad span{${CLAMP2}}
& .tgs{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 12px}& .tgs span{height:20px;padding:0 6px;border-radius:4px;background:var(--pt);color:var(--p-text);font-size:12px;line-height:20px;font-weight:600}
& .ac{display:grid;grid-template-columns:1fr 1fr;gap:8px}& .gb{display:flex;align-items:center;justify-content:center;gap:6px;height:44px;border-radius:12px;background:var(--pt);color:var(--p-text);font-size:14px;font-weight:600;transition:transform .15s cubic-bezier(.2,0,0,1)}& .gb:active{transform:scale(.97)}& .gb svg{width:18px;height:18px}& .gb em{font-weight:400;color:var(--ink2)}`),
    html: () => `<div class="mpsvc001">${STORES.map(([n, st, tg, hr, ad, di, tags, bp]) => `<div class="cd ${st}"><div class="tp"><div class="im" style="background-image:url(${ASSETS.bg.interior});background-position:${bp}"></div><div class="in"><div class="r1"><h4>${n}</h4><button class="hrt" type="button" data-ix="like" aria-label="收藏门店">${sv('heart')}</button></div><div class="r2"><span class="st2">${tg}</span><span>${hr}</span></div><p class="ad">${sv('pin')}<span>${ad}</span></p></div></div><div class="tgs">${tags.map((t) => `<span>${t}</span>`).join('')}</div><div class="ac"><button class="gb" type="button" data-toast="正在打开地图导航">${sv('mgnav')}导航 <em>${di}</em></button><button class="gb" type="button" data-toast="拨打门店电话 021-6288 0000">${sv('phone')}电话</button></div></div>`).join('')}</div>`,
  })

  /* ---------- MP-SVC-002 预约日期时段选择 ---------- */
  const WKN = ['日', '一', '二', '三', '四', '五', '六']
  const dayInfo = (i) => { const d = new Date(2026, 10, 4 + i); return { mm: String(d.getMonth() + 1).padStart(2, '0'), dd: String(d.getDate()).padStart(2, '0'), wn: '周' + WKN[d.getDay()], lb: i === 0 ? '今天' : i === 1 ? '明天' : '周' + WKN[d.getDay()] } }
  const GROUPS = [['上午', ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30']], ['下午', ['13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']], ['晚上', ['18:00', '18:30', '19:00', '19:30']]]
  const NOW = '11:20', FULLDAY = 3
  const slotState = (d, t, gi) => d === FULLDAY ? 'full' : (d === 0 && t < NOW) ? 'past' : ((d * 7 + gi * 3) % 5 === 0 ? 'full' : 'ok')
  const slotsHTML = (d) => {
    if (d === FULLDAY) return `<div class="em">${sv('calendar')}<b>这天已约满</b><span>换个日期试试，或预约其他门店</span></div>`
    let gi = 0
    return GROUPS.map(([g, ts]) => `<div class="gp2"><h5>${g}</h5><div class="gd">${ts.map((t) => { const st = slotState(d, t, gi++); return `<button class="sx ${st}" type="button" data-t="${t}" ${st === 'ok' ? '' : 'disabled'}>${t}${st === 'full' ? '<i>约满</i>' : st === 'past' ? '<i>已过</i>' : ''}</button>` }).join('')}</div></div>`).join('')
  }
  def({
    id: 'MP-SVC-002', name: '预约日期时段选择', style: '日期+时段',
    fit: '美业、健身、医疗、家政等预约流程；先横滑选日期，再选时段，约满与已过置灰，选定后才能确认',
    avoid: '一次展示超过 14 天（改用月历）；约满的时段直接隐藏；确认按钮在没选时段时可点',
    kw: '预约 日期 时段 时间选择 约满 横滑 booking appointment time slot 排期 预订',
    css: CSS('MP-SVC-002', `${CARD()}&{padding:16px 0}${HEAD}& .hd{padding:0 16px}& .hd span{display:flex;align-items:center;height:24px;padding:0 8px;border-radius:12px;background:var(--pt);color:var(--p-text);font-weight:600}
& .ds{gap:8px;padding:14px 16px 4px;scroll-snap-type:none}& .ds>*{scroll-snap-align:none}
& .dt{flex:none;width:56px;height:76px;border-radius:12px;background:var(--n3);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:12px;color:var(--ink2);transition:background-color .2s,color .2s}& .dt b{font-size:18px;line-height:24px;font-weight:600;color:var(--ink)}& .dt i{min-height:16px;font-size:12px;line-height:16px;color:var(--ink3)}
& .dt.on{background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff}& .dt.on b,& .dt.on i{color:#fff}& .dt.full:not(.on) b{color:var(--ink3)}
& .gp2{padding:0 16px;margin-top:12px}& .gp2 h5{margin:0 0 8px;font-size:12px;font-weight:600;color:var(--ink3)}& .gd{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
& .sx{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;height:40px;border-radius:12px;background:var(--card);box-shadow:inset 0 0 0 1px var(--n7);font-size:14px;line-height:16px;color:var(--ink);font-variant-numeric:tabular-nums;transition:background-color .15s,box-shadow .15s,color .15s}& .sx::after{content:"";position:absolute;inset:-2px}
& .sx i{font-size:12px;line-height:14px;color:var(--ink3)}& .sx.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p);color:var(--p-text);font-weight:600}& .sx:disabled{background:var(--n3);box-shadow:none;color:var(--ink3);cursor:default}
& .em{display:flex;flex-direction:column;align-items:center;gap:4px;padding:34px 16px 30px;text-align:center;color:var(--ink3);font-size:12px}& .em svg{width:32px;height:32px;margin-bottom:4px}& .em b{font-size:14px;font-weight:600;color:var(--ink2)}
& .ft{margin:16px 16px 0;padding-top:12px;border-top:1px solid var(--line)}& .sm{margin-bottom:10px;font-size:14px;color:var(--ink2)}& .sm b{font-weight:600;color:var(--p-text)}
${PB}${SPIN}`),
    html: () => `<div class="mpsvc002"><div class="hd"><b>选择预约时间</b><span>深层清洁护理 · 60 分钟</span></div><div class="ix-track ds" data-ds>${Array.from({ length: 14 }, (_, i) => { const x = dayInfo(i); return `<button class="dt ${i === 0 ? 'on' : ''} ${i === FULLDAY ? 'full' : ''}" type="button" data-d="${i}"><span>${x.lb}</span><b>${x.dd}</b><i>${i === FULLDAY ? '约满' : ''}</i></button>` }).join('')}</div><div data-slots>${slotsHTML(0)}</div><div class="ft"><div class="sm" data-sum>请选择日期与时段</div><button class="pb" type="button" data-ok disabled>确认预约</button></div></div>`,
    js: (root) => {
      const ds = root.querySelector('[data-ds]'), box = root.querySelector('[data-slots]'), sum = root.querySelector('[data-sum]'), btn = root.querySelector('[data-ok]')
      let d = 0, t = null, done = false
      const lab = () => { const x = dayInfo(d); return `${x.mm}-${x.dd} ${x.wn} ${t}` }
      const reset = () => { done = false; btn.className = 'pb'; btn.textContent = '确认预约'; btn.disabled = !t; sum.innerHTML = t ? `已选 <b>${lab()}</b>` : '请选择日期与时段' }
      ds.addEventListener('click', (e) => {
        const b = e.target.closest('[data-d]'); if (!b) return
        d = +b.dataset.d; t = null; ds.querySelectorAll('.dt').forEach((x) => x.classList.toggle('on', x === b)); box.innerHTML = slotsHTML(d); reset()
      })
      box.addEventListener('click', (e) => {
        const b = e.target.closest('.sx'); if (!b || b.disabled) return
        t = b.dataset.t; box.querySelectorAll('.sx').forEach((x) => x.classList.toggle('on', x === b)); reset()
      })
      btn.addEventListener('click', () => {
        if (done) { IX.toast(root, '进入预约详情'); return }
        if (!t || btn.disabled) return
        btn.disabled = true; btn.innerHTML = '<span class="sp"></span>提交中…'
        later(root, 700, () => { done = true; btn.disabled = false; btn.className = 'pb ok'; btn.textContent = '查看预约详情'; sum.innerHTML = `预约成功 · <b>${lab()}</b>`; IX.toast(root, '预约成功，到店出示预约码') })
      })
    },
  })

  /* ---------- MP-SVC-003 取号排队进度卡 ---------- */
  const notchC = notch(104).replace(/104px/g, '50%')
  def({
    id: 'MP-SVC-003', name: '取号排队进度卡', style: '叫号四态',
    fit: '餐饮、门诊、网点排队；首屏给出我的号码、前面还有几桌、预计等待、当前叫号，轮到时变成醒目提示',
    avoid: '只写“排队中”不给数字；预计等待时间不更新；取消排队不二次确认；叫号后不给到店倒计时',
    kw: '排队 取号 叫号 等位 排号 进度 queue ticket waiting 前面还有 预计等待',
    css: CSS('MP-SVC-003', `${CARD()}&{position:relative;padding:16px;overflow:hidden}
& .hd{display:flex;align-items:center;justify-content:space-between;gap:8px}& .nm{display:flex;align-items:center;gap:6px;min-width:0;font-size:14px;font-weight:600;${ELL}}& .nm svg{width:18px;height:18px;color:var(--p-text);flex:none}
& .tag{flex:none;height:24px;padding:0 10px;border-radius:12px;font-size:12px;line-height:24px;font-weight:600;background:var(--pt);color:var(--p-text)}
&[data-st=soon] .tag{background:var(--warn-bg);color:var(--warn)}&[data-st=call] .tag{background:var(--ok-bg);color:var(--ok)}&[data-st=cancel] .tag{background:var(--soft);color:var(--ink3)}
& .tw{margin-top:14px;filter:drop-shadow(0 3px 8px var(--sh08))}& .tk{position:relative;display:grid;grid-template-columns:1fr 1fr;padding:16px 0;border-radius:16px;background:var(--pt);-webkit-mask:${notchC};mask:${notchC}}
& .tk::before{content:"";position:absolute;left:50%;top:14px;bottom:14px;border-left:1.5px dashed var(--pm)}
& .no,& .ah{display:flex;flex-direction:column;align-items:center;gap:2px;padding:0 10px;text-align:center}& .no small,& .ah small{font-size:12px;color:var(--ink3)}& .no span,& .ah .eta{font-size:12px;color:var(--ink2)}
& .no b{font-size:32px;line-height:40px;font-weight:700;color:var(--p-text);font-variant-numeric:tabular-nums}& .ab{display:flex;align-items:baseline;gap:4px}& .ab b{font-size:32px;line-height:40px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums}& .ab span{font-size:14px;color:var(--ink2)}& .eta em{font-weight:600;color:var(--ink)}
&[data-st=cancel] .tk{background:var(--soft)}&[data-st=cancel] .no b,&[data-st=cancel] .ab b{color:var(--ink3)}
& .rl{position:relative;height:8px;margin:24px 12px 6px;border-radius:4px;background:var(--n4)}& .rl .f{position:absolute;left:0;top:0;bottom:0;border-radius:4px;background:linear-gradient(90deg,var(--ga),var(--gb));transition:width .5s cubic-bezier(.2,0,0,1)}
& .kn{position:absolute;top:50%;width:24px;height:24px;margin:-12px 0 0 -12px;border-radius:50%;background:var(--card);box-shadow:0 0 0 2px var(--p),0 2px 6px var(--sh18);color:var(--p-text);padding:5px;transition:left .5s cubic-bezier(.2,0,0,1)}
& .rb{display:flex;justify-content:space-between;margin:0 6px;font-size:12px;color:var(--ink3)}
& .cur{display:flex;align-items:center;justify-content:space-between;margin-top:14px;padding:10px 12px;border-radius:12px;background:var(--n2);font-size:14px;color:var(--ink2)}& .cur b{font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}& .cur small{font-size:12px;color:var(--ink3)}
& .bn{margin-top:12px;padding:10px 12px;border-radius:12px;font-size:14px;line-height:1.5}& .bn.warn{background:var(--warn-bg);color:var(--warn)}& .bn.ok{background:var(--ok-bg);color:var(--ok-ink)}& .bn.mu{background:var(--soft);color:var(--ink2)}& .bn b{font-variant-numeric:tabular-nums}
& .pb{margin-top:14px}& .ln{display:block;margin:6px auto -6px;height:44px;padding:0 16px;font-size:14px;color:var(--ink3)}
${PB}${SPIN}${DLG}& .ix-ov{align-items:center}& .dlg .pb{width:auto;flex:1;margin-top:0}`),
    html: () => `<div class="mpsvc003" data-st="wait"><div class="hd"><span class="nm">${sv('mgstore')}海岸线餐厅 · 静安店</span><span class="tag" data-tag>排队中</span></div><div class="tw"><div class="tk"><div class="no"><small>我的号码</small><b data-no>A037</b><span>小桌 · 1–2 人</span></div><div class="ah"><small>前面还有</small><div class="ab"><b data-ahead>5</b><span>桌</span></div><span class="eta">预计等待 <em data-eta>25</em> 分钟</span></div></div></div><div class="rl"><i class="f" data-fill style="width:37.5%"></i><i class="kn" data-kn style="left:37.5%">${sv('user')}</i></div><div class="rb"><span>已取号</span><span>入座</span></div><p class="cur"><span>当前叫号 <b data-cur>A032</b></span><small>更新于 <span data-at>刚刚</span></small></p><div class="bn" data-bn hidden></div><button class="pb" type="button" data-main>刷新进度</button><button class="ln" type="button" data-open="cf" data-cancel>取消排队</button><div class="ix-ov" data-ov="cf"><div class="ix-mask"></div><div class="dlg"><h4>取消排队</h4><p>取消后当前号码 A037 将作废，重新取号需要重新排队。</p><div class="row"><button class="pb cx" type="button" data-close>再等等</button><button class="pb" type="button" data-do>确认取消</button></div></div></div></div>`,
    js: (root) => {
      const box = root.querySelector('.mpsvc003')
      const q = (s) => root.querySelector(s)
      const no = q('[data-no]'), ah = q('[data-ahead]'), eta = q('[data-eta]'), cur = q('[data-cur]'), at = q('[data-at]'), fill = q('[data-fill]'), kn = q('[data-kn]'), tag = q('[data-tag]'), bn = q('[data-bn]'), main = q('[data-main]'), cancel = q('[data-cancel]'), ov = q('[data-ov]')
      let my = 37, ahead = 5, tot = 8, state = 'wait', busy = false, tmr = null, left = 600
      const fmt = (n) => 'A' + String(n).padStart(3, '0')
      const stop = () => { if (tmr) { clearInterval(tmr); tmr = null } }
      const paint = () => {
        state = state === 'cancel' ? 'cancel' : ahead === 0 ? 'call' : ahead === 1 ? 'soon' : 'wait'
        box.dataset.st = state; stop()
        no.textContent = fmt(my); at.textContent = '刚刚'
        const dead = state === 'cancel'
        ah.textContent = dead ? '–' : ahead; eta.textContent = dead ? '–' : ahead * 5; cur.textContent = dead ? fmt(my - ahead) : fmt(my - ahead)
        const p = (tot - ahead) / tot * 100; fill.style.width = p + '%'; kn.style.left = p + '%'
        tag.textContent = { wait: '排队中', soon: '即将到号', call: '已叫号', cancel: '已取消' }[state]
        cancel.hidden = dead; bn.hidden = state === 'wait'
        main.className = 'pb'; main.disabled = false
        if (state === 'soon') { bn.className = 'bn warn'; bn.textContent = '下一桌就是您，请回到店内附近，错过叫号将顺延一位。'; main.textContent = '刷新进度' }
        else if (state === 'call') {
          bn.className = 'bn ok'; bn.innerHTML = '轮到您了！请在 <b data-cd>10:00</b> 内到前台出示号码，超时将自动过号。'; main.textContent = '我已到店'
          left = 600; const cd = bn.querySelector('[data-cd]'); tmr = setInterval(() => { if (!root.isConnected) { stop(); return } left = Math.max(0, left - 1); cd.textContent = `${String(Math.floor(left / 60)).padStart(2, '0')}:${String(left % 60).padStart(2, '0')}` }, 1000)
        } else if (dead) { bn.className = 'bn mu'; bn.textContent = `已取消排队，号码 ${fmt(my)} 已作废。`; main.textContent = '重新取号' }
        else main.textContent = '刷新进度'
      }
      paint()
      main.addEventListener('click', () => {
        if (busy) return
        if (state === 'cancel') { my += 4; ahead = 7; tot = 10; state = 'wait'; paint(); IX.toast(root, `已取号 ${fmt(my)}，前面还有 7 桌`); return }
        if (state === 'call') { main.disabled = true; main.className = 'pb ok'; main.textContent = '已通知店员'; IX.toast(root, `请向前台出示 ${fmt(my)}`); return }
        busy = true; main.disabled = true; main.innerHTML = '<span class="sp"></span>刷新中…'
        later(root, 600, () => { busy = false; ahead = Math.max(0, ahead - 1); paint(); IX.toast(root, ahead === 0 ? '轮到您了' : `前面还有 ${ahead} 桌`) })
      })
      q('[data-do]').addEventListener('click', () => { ov.classList.remove('show'); state = 'cancel'; paint(); IX.toast(root, '已取消排队') })
    },
  })

  /* ---------- MP-SVC-004 核销券码卡 ---------- */
  const rng = (seed) => { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296 } }
  const qrSVG = (seed, size) => {
    const N = 25, r = rng(seed), g = Array.from({ length: N }, () => Array.from({ length: N }, () => (r() > 0.52 ? 1 : 0)))
    const finder = (ox, oy) => { for (let y = -1; y < 8; y++) for (let x = -1; x < 8; x++) { const X = ox + x, Y = oy + y; if (X >= 0 && Y >= 0 && X < N && Y < N) g[Y][X] = 0 } for (let y = 0; y < 7; y++) for (let x = 0; x < 7; x++) g[oy + y][ox + x] = (x === 0 || x === 6 || y === 0 || y === 6 || (x >= 2 && x <= 4 && y >= 2 && y <= 4)) ? 1 : 0 }
    finder(0, 0); finder(N - 7, 0); finder(0, N - 7)
    let d = ''; for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) if (g[y][x]) d += `M${x} ${y}h1v1h-1z`
    return `<svg viewBox="0 0 ${N} ${N}" width="${size}" height="${size}" shape-rendering="crispEdges" role="img" aria-label="核销二维码"><path d="${d}" fill="var(--ink)"/></svg>`
  }
  const barSVG = (seed) => { const r = rng(seed); let x = 0, d = ''; while (x < 190) { const w = 1 + Math.floor(r() * 3), gap = 1 + Math.floor(r() * 2); d += `M${x} 0h${w}v64h-${w}z`; x += w + gap } return `<svg viewBox="0 0 ${x} 64" width="236" height="64" preserveAspectRatio="none" shape-rendering="crispEdges" role="img" aria-label="核销条形码"><path d="${d}" fill="var(--ink)"/></svg>` }
  const notchV = `radial-gradient(circle 8px at 0 var(--y),transparent 7.5px,#000 8px) left/51% 100% no-repeat,radial-gradient(circle 8px at 100% var(--y),transparent 7.5px,#000 8px) right/51% 100% no-repeat`
  def({
    id: 'MP-SVC-004', name: '核销券码卡', style: '码+三态',
    fit: '到店核销的券、预约码、取餐码；二维码/条形码可切换并自动刷新，已使用、已过期各有独立状态',
    avoid: '码是静态图片可被截图复用（要自动刷新）；已使用的券还显示可扫的码；券码不能复制',
    kw: '核销 券码 二维码 条形码 到店 使用 已使用 已过期 voucher qr code redeem 核销码',
    css: CSS('MP-SVC-004', `&{width:340px}
& .tb{display:flex;gap:8px;margin-bottom:12px}& .tb button{position:relative;height:32px;padding:0 14px;border-radius:16px;background:var(--card);font-size:14px;color:var(--ink2);transition:background-color .2s,color .2s}& .tb button::after{content:"";position:absolute;inset:-6px -2px}& .tb .on{background:var(--p);color:#fff;font-weight:600}
& .tw{filter:drop-shadow(0 6px 16px var(--sh10))}& .tkt{--y:104px;position:relative;background:var(--card);border-radius:16px;-webkit-mask:${notchV};mask:${notchV}}
& .tp{padding:16px 16px 0;height:104px}& .tp h4{margin:0;font-size:18px;line-height:24px;font-weight:600;${ELL}}& .tp p{margin:4px 0 0;font-size:12px;line-height:18px;color:var(--ink3);${ELL}}
& .vd{display:flex;align-items:center;gap:8px;margin-top:10px;font-size:12px;color:var(--ink2)}& .vd em{height:20px;padding:0 6px;border-radius:4px;font-size:12px;line-height:20px;font-weight:600;background:var(--ok-bg);color:var(--ok)}& .vd em.mu{background:var(--soft);color:var(--ink3)}
& .dv{position:absolute;left:14px;right:14px;top:var(--y);border-top:1.5px dashed var(--n6)}
& .bx4{display:flex;flex-direction:column;align-items:center;padding:18px 16px 14px}
& .cs{display:flex;padding:2px;border-radius:12px;background:var(--soft)}& .cs button{position:relative;display:flex;align-items:center;gap:4px;height:28px;padding:0 12px;border-radius:8px;font-size:12px;color:var(--ink2);font-weight:600}& .cs button::after{content:"";position:absolute;inset:-8px -2px}& .cs svg{width:14px;height:14px}& .cs .on{background:var(--lift);color:var(--ink);box-shadow:0 1px 4px var(--sh14)}
& .cbox{display:flex;align-items:center;justify-content:center;width:184px;height:184px;margin-top:14px;border-radius:16px;box-shadow:inset 0 0 0 1px var(--line)}& .cbar{width:268px;height:104px}& .cbox.fl svg{animation:§fl .35s cubic-bezier(.2,0,0,1)}@keyframes §fl{from{opacity:.2}}
& .no{display:flex;align-items:center;gap:6px;margin-top:12px;font-size:22px;line-height:28px;font-weight:600;font-variant-numeric:tabular-nums}
& .cp{position:relative;width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:16px;background:var(--pt);color:var(--p-text)}& .cp::after{content:"";position:absolute;inset:-6px}& .cp svg{width:16px;height:16px}
& .rf{display:flex;align-items:center;gap:2px;margin-top:6px;font-size:12px;color:var(--ink3)}& .rf button{position:relative;display:flex;align-items:center;gap:2px;height:24px;padding:0 6px;color:var(--p-text);font-weight:600}& .rf button::after{content:"";position:absolute;inset:-10px -4px}& .rf svg{width:14px;height:14px}
& .nt{margin:0 16px;border-top:1px solid var(--line)}& .nt .h{display:flex;align-items:center;justify-content:space-between;width:100%;height:44px;font-size:14px;color:var(--ink2)}& .nt .h svg{width:16px;height:16px;transition:transform .25s cubic-bezier(.2,0,0,1)}& .ix-ai.open .h svg{transform:rotate(90deg)}
& .nt ul{margin:0 0 12px;padding-left:18px;font-size:12px;line-height:20px;color:var(--ink3)}
& .stp{display:flex;flex-direction:column;align-items:center;gap:6px;padding:26px 16px 24px;text-align:center;font-size:12px;line-height:18px;color:var(--ink3)}& .stp b{display:inline-flex;align-items:center;gap:4px;height:32px;padding:0 16px;border-radius:16px;box-shadow:inset 0 0 0 1.5px currentColor;font-size:16px;font-weight:600;color:var(--ink2)}& .stp svg{width:18px;height:18px}
& .gray .tp h4,& .gray .tp p{color:var(--ink3)}
${SB}`),
    html: () => {
      const head = (st) => `<div class="tp"><h4>双人下午茶套餐券</h4><p>静安店 · 全场通用 · 节假日可用</p><div class="vd">${st === 'ok' ? '<em>待使用</em>' : st === 'used' ? '<em class="mu">已使用</em>' : '<em class="mu">已过期</em>'}<span>${st === 'expired' ? '有效期至 2026-10-31' : '有效期至 2026-12-31'}</span></div></div><i class="dv"></i>`
      return `<div class="mpsvc004"><div class="tb" data-ix="tabs" data-g="v4"><button class="on" type="button" data-t="ok">待使用</button><button type="button" data-t="used">已使用</button><button type="button" data-t="expired">已过期</button></div>
<div data-p="ok" data-g="v4"><div class="tw"><div class="tkt">${head('ok')}<div class="bx4"><div class="cs" data-ix="tabs" data-g="c4"><button class="on" type="button" data-t="qr">${sv('qr')}二维码</button><button type="button" data-t="bar">${sv('mgbarcode')}条形码</button></div><div data-p="qr" data-g="c4"><div class="cbox" data-qr></div></div><div data-p="bar" data-g="c4" hidden><div class="cbox cbar" data-bar>${barSVG(8820)}</div></div><div class="no"><span>8820 3417 5521</span><button class="cp" type="button" data-copy aria-label="复制券码">${sv('copy')}</button></div><div class="rf"><span data-hint>二维码 <i data-sec>60</i> 秒后自动刷新</span><button type="button" data-refresh>${sv('refresh')}刷新</button></div></div><div class="nt" data-ix="acc"><div class="ix-ai"><button class="h" type="button" data-h>使用须知${sv('chev')}</button><div class="ix-ab"><div><ul><li>到店出示二维码或券码，由店员扫码核销</li><li>每张券限用一次，核销后不可退回</li><li>不与其他优惠同享，节假日通用</li></ul></div></div></div></div></div></div></div>
<div data-p="used" data-g="v4" hidden><div class="tw"><div class="tkt gray">${head('used')}<div class="stp"><b>${sv('check')}已核销</b>核销时间 2026-11-02 14:20<br>核销门店 静安店 · 店员 周越</div></div></div></div>
<div data-p="expired" data-g="v4" hidden><div class="tw"><div class="tkt gray">${head('expired')}<div class="stp"><b>${sv('hourglass')}已过期</b>券已于 2026-10-31 过期，不可再使用<br>过期券保留 90 天后自动清理</div></div></div></div></div>`
    },
    js: (root) => {
      const qr = root.querySelector('[data-qr]'), sec = root.querySelector('[data-sec]')
      let seed = 20261104, left = 60
      const draw = () => { qr.innerHTML = qrSVG(seed, 160) }
      const refresh = () => { seed = (seed * 1103515245 + 12345) >>> 0; left = 60; sec.textContent = 60; qr.classList.remove('fl'); void qr.offsetWidth; qr.classList.add('fl'); draw() }
      draw()
      const tick = setInterval(() => { if (!root.isConnected) { clearInterval(tick); return } left--; if (left <= 0) refresh(); else sec.textContent = left }, 1000)
      root.querySelector('[data-refresh]').addEventListener('click', () => { refresh(); IX.toast(root, '二维码已刷新') })
      root.querySelector('[data-copy]').addEventListener('click', () => { try { navigator.clipboard && navigator.clipboard.writeText('882034175521').catch(() => {}) } catch (e) {} IX.toast(root, '已复制券码') })
    },
  })

  /* ---------- MP-SVC-005 服务套餐选择 ---------- */
  const PKG = [['基础洁面', 60, 168, 198, '深层清洁 · 补水面膜 · 肩颈放松', ''], ['标准焕肤', 90, 298, 368, '基础洁面全部内容，加焕肤精华导入与面部淋巴排毒', '热门'], ['尊享修护', 120, 498, 628, '标准焕肤全部内容，加屏障修护安瓿、专属顾问全程服务，并赠居家护理小样一份', '']]
  const ADD = [['眼部护理', 38], ['热石按摩', 58], ['精油升级', 28]]
  def({
    id: 'MP-SVC-005', name: '服务套餐选择', style: '单选+加购',
    fit: '美业、家政、洗护、摄影等多档服务；套餐单选，加购项多选，价格与时长实时联动，底部固定合计与预约按钮',
    avoid: '套餐超过 4 档（先分类）；选中只靠颜色不靠边框；套餐说明一大段（用一句话 + “含”清单）',
    kw: '服务套餐 套餐 选择 加购 加项 价格联动 时长 package plan select 美业 家政 预约',
    css: CSS('MP-SVC-005', `${CARD()}&{padding:16px}${HEAD}
& .ls{display:flex;flex-direction:column;gap:10px;margin:12px 0}
& .pk{position:relative;display:flex;gap:12px;padding:12px;border-radius:16px;background:var(--card);box-shadow:inset 0 0 0 1px var(--n6);text-align:left;transition:background-color .2s,box-shadow .2s}& .pk.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p)}
& .rd{flex:none;width:20px;height:20px;margin-top:2px;border-radius:50%;box-shadow:inset 0 0 0 1.5px var(--n9);display:flex;align-items:center;justify-content:center;color:#fff;transition:background-color .2s,box-shadow .2s}& .rd svg{width:12px;height:12px;opacity:0}& .pk.on .rd{background:var(--p);box-shadow:none}& .pk.on .rd svg{opacity:1}
& .bd{flex:1;min-width:0}& .bd h4{margin:0;display:flex;align-items:center;gap:6px;font-size:16px;line-height:22px;font-weight:600}& .bd p{margin:4px 0 0;font-size:12px;line-height:18px;color:var(--ink3);${CLAMP2}}& .bd .du{margin-top:4px;font-size:12px;color:var(--ink2)}& .pk .tg{background:var(--p);color:#fff}
& .pr{flex:none;text-align:right}& .pr .price b{font-size:22px}& .pr .strike{display:block;margin:4px 0 0}
& .adh{margin:14px 0 8px;font-size:12px;font-weight:600;color:var(--ink3)}& .ads{display:flex;flex-wrap:wrap;gap:8px}& .ad{position:relative;display:flex;align-items:center;gap:4px;height:32px;padding:0 12px;border-radius:16px;background:var(--n3);font-size:14px;color:var(--ink2);transition:background-color .2s,color .2s}& .ad::after{content:"";position:absolute;inset:-6px -2px}& .ad svg{width:14px;height:14px;display:none}& .ad.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1.5px var(--p)}& .ad.on svg{display:block}
& .bar2{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:16px;padding-top:14px;border-top:1px solid var(--line)}& .bar2 small{display:block;font-size:12px;line-height:18px;color:var(--ink3)}& .bar2 b{display:flex;align-items:baseline;gap:2px;font-size:22px;line-height:28px;font-weight:600;color:var(--price);font-variant-numeric:tabular-nums}& .bar2 b i{font-size:14px}& .bar2 .pb{width:132px;flex:none}
${PB}${SPIN}`),
    html: () => `<div class="mpsvc005"><div class="hd"><b>选择服务套餐</b><span>深层清洁护理</span></div><div class="ls">${PKG.map(([n, m, p, o, d, t], i) => `<button class="pk ${i === 1 ? 'on' : ''}" type="button" data-k="${i}"><span class="rd">${sv('check')}</span><div class="bd"><h4>${n}${t ? `<i class="tg tg-soft">${t}</i>` : ''}</h4><p>${d}</p><div class="du">约 ${m} 分钟</div></div><div class="pr"><span class="price"><small>¥</small><b>${p}</b></span><span class="strike">¥${o}</span></div></button>`).join('')}</div><div class="adh">加购项（可多选）</div><div class="ads">${ADD.map(([n, p], i) => `<button class="ad" type="button" data-a="${i}">${sv('check')}${n} +¥${p}</button>`).join('')}</div><div class="bar2"><div><small data-bd>约 90 分钟 · 加购 ¥0</small><b><i>¥</i><span data-tot>298</span></b></div><button class="pb" type="button" data-ok>立即预约</button></div></div>`,
    js: (root) => {
      let pk = 1, shown = PKG[1][2]; const ad = new Set()
      const tot = root.querySelector('[data-tot]'), bd = root.querySelector('[data-bd]')
      const upd = () => {
        const extra = [...ad].reduce((s, i) => s + ADD[i][1], 0), v = PKG[pk][2] + extra, from = shown; shown = v
        tween(from, v, 300, (x) => { tot.textContent = nf(x) })
        bd.textContent = `约 ${PKG[pk][1] + ad.size * 15} 分钟 · 加购 ¥${extra}`
      }
      root.addEventListener('click', (e) => {
        const k = e.target.closest('.pk'); if (k) { pk = +k.dataset.k; root.querySelectorAll('.pk').forEach((x) => x.classList.toggle('on', x === k)); upd(); return }
        const a = e.target.closest('.ad'); if (a) { const i = +a.dataset.a; if (ad.has(i)) ad.delete(i); else ad.add(i); a.classList.toggle('on', ad.has(i)); upd(); return }
        const ok = e.target.closest('[data-ok]'); if (ok && !ok.disabled) {
          ok.disabled = true; ok.innerHTML = '<span class="sp"></span>提交中…'
          later(root, 700, () => { ok.disabled = false; ok.textContent = '立即预约'; IX.toast(root, `已选「${PKG[pk][0]}」，下一步选择时间`) })
        }
      })
    },
  })

  /* ---------- MP-SVC-006 服务人员选择 ---------- */
  const STAFF = [['不指定', '系统为你匹配最快可约', null, '', '今天 11:30 起可约', 'ok'], ['周越', '高级技师 · 8 年', 0, '敏感肌 · 焕肤', '今天 14:30 起可约', 'ok'], ['陈嘉禾', '资深顾问 · 6 年', 1, '深层清洁', '今天 15:00 起可约', 'ok'], ['林夕', '首席技师 · 12 年 · 擅长抗衰与面部轮廓提升护理', 2, '抗衰 · 轮廓', '今日已约满，明天 10:00 可约', 'full'], ['何晓雯', '技师 · 3 年', 3, '舒缓 · 补水', '今天 16:30 起可约', 'ok']]
  const STR = ['4.9', '4.8', '5.0', '4.7'], STN = ['1,280', '960', '2,046', '412']
  def({
    id: 'MP-SVC-006', name: '服务人员选择', style: '横滑卡片',
    fit: '美业、健身、咨询、家政；横滑选技师/顾问，头像、职称、评分、擅长、最早可约一次给全，含“不指定”',
    avoid: '只放头像和名字（没有决策信息）；约满的人直接消失；没有“不指定”让用户被迫挑',
    kw: '技师 顾问 服务人员 选择 横滑 评分 擅长 最早可约 不指定 staff stylist coach 美业',
    css: CSS('MP-SVC-006', `${CARD()}&{padding:16px 0}${HEAD}& .hd{padding:0 16px}
& .ts{gap:10px;padding:14px 16px 6px;scroll-snap-type:none}& .ts>*{scroll-snap-align:none}
& .sf{position:relative;flex:none;width:156px;padding:14px 12px 12px;border-radius:16px;background:var(--card);box-shadow:inset 0 0 0 1px var(--n6);text-align:left;display:flex;flex-direction:column;gap:4px;transition:background-color .2s,box-shadow .2s}& .sf.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p)}
& .av0{width:56px;height:56px;border-radius:50%;margin-bottom:4px;background:var(--pt);color:var(--p-text);padding:14px;flex:none}& .sf .av{width:56px;height:56px;margin-bottom:4px}
& .sf h4{margin:0;font-size:16px;line-height:22px;font-weight:600}& .sf .t{font-size:12px;line-height:18px;color:var(--ink3);min-height:36px;${CLAMP2}}
& .sf .rt{display:flex;align-items:center;gap:4px;font-size:12px;color:var(--ink2)}& .sf .rt svg{width:14px;height:14px;color:${GOLD.ac}}& .sf .rt b{font-weight:600;color:var(--ink)}
& .sf .sk{font-size:12px;color:var(--p-text);${ELL}}& .sf .av2{margin-top:4px;padding-top:8px;border-top:1px solid var(--line);font-size:12px;line-height:18px;color:var(--ok);min-height:46px}& .sf.full .av2{color:var(--warn)}
& .ck{position:absolute;right:10px;top:10px;width:22px;height:22px;border-radius:50%;background:var(--p);color:#fff;padding:5px;opacity:0;transform:scale(.6);transition:opacity .15s,transform .2s cubic-bezier(.2,0,0,1)}& .sf.on .ck{opacity:1;transform:none}
& .ft{display:flex;align-items:center;gap:12px;margin:12px 16px 0;padding-top:14px;border-top:1px solid var(--line)}& .sm{flex:1;min-width:0;font-size:12px;line-height:18px;color:var(--ink3)}& .sm b{display:block;font-size:14px;line-height:20px;font-weight:600;color:var(--ink)}& .ft .pb{width:132px;flex:none}
${PB}`),
    html: () => `<div class="mpsvc006"><div class="hd"><b>选择服务人员</b><span>共 ${STAFF.length - 1} 位</span></div><div class="ix-track ts" data-ts>${STAFF.map(([n, t, a, sk, av, st], i) => `<button class="sf ${st} ${i === 0 ? 'on' : ''}" type="button" data-i="${i}">${a === null ? `<span class="av0">${sv('users')}</span>` : critter(a, 56)}<h4>${n}</h4><span class="t">${t}</span>${a === null ? '<span class="rt">智能匹配</span>' : `<span class="rt">${sv('starf')}<b>${STR[a]}</b> · 服务 ${STN[a]} 单</span>`}<span class="sk">${sk || '全部项目'}</span><span class="av2">${av}</span><span class="ck">${sv('check')}</span></button>`).join('')}</div><div class="ft"><div class="sm" data-sum></div><button class="pb" type="button" data-next>下一步</button></div></div>`,
    js: (root) => {
      const sum = root.querySelector('[data-sum]'), cards = [...root.querySelectorAll('.sf')]
      let sel = 0
      const paint = () => { cards.forEach((c, i) => c.classList.toggle('on', i === sel)); const [n, , , , av] = STAFF[sel]; sum.innerHTML = `已选 <b>${n}</b>${av}` }
      paint()
      root.querySelector('[data-ts]').addEventListener('click', (e) => { const c = e.target.closest('.sf'); if (c) { sel = +c.dataset.i; paint() } })
      root.querySelector('[data-next]').addEventListener('click', () => IX.toast(root, `已选${STAFF[sel][0]}，下一步选择时间`))
    },
  })

  /* ---------- MP-SVC-007 点单菜品行与购物袋 ---------- */
  const DISH = [{ i: 2, n: '手作釉面马克杯', d: '手作釉面，容量 350ml，赠杯垫一枚', p: 39, t: '招牌', lim: 5 }, { i: 6, n: '保温随行杯 500ml 鼠尾草绿限定款', d: '316 不锈钢内胆，保冷保温 24 小时', p: 59, t: '新品', lim: 9 }, { i: 3, n: '帆布托特包', d: '原色加厚帆布，可放 14 寸电脑', p: 49, t: '', lim: 9 }, { i: 5, n: '护眼小台灯', d: '三档调光，无频闪', p: 79, t: '', lim: 9, sold: true }]
  def({
    id: 'MP-SVC-007', name: '点单菜品行与购物袋', style: '步进+联动',
    fit: '外卖、到店自取、堂食扫码点单；“加入”变步进器，购物袋数量金额实时联动，没到起送价写清还差多少',
    avoid: '售罄商品直接隐藏（置灰并写“已售罄”）；步进器没有上限提示；起送门槛不显示还差多少',
    kw: '点单 外卖 菜品 步进器 购物袋 购物车 起送 起送价 加购 自取 order menu dish stepper bag',
    css: CSS('MP-SVC-007', `&{position:relative;width:340px;padding:16px 16px 64px;border-radius:22px;background:var(--card);box-shadow:0 10px 26px var(--sh08);overflow:hidden}${HEAD}
& .ls{margin-top:4px}& .dh{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid var(--line)}& .dh:last-child{border-bottom:0}& .dh img{width:76px;height:76px;border-radius:12px;object-fit:cover;flex:none}& .sold img{filter:grayscale(1);opacity:.55}
& .tx{flex:1;min-width:0;display:flex;flex-direction:column}& .tx h4{margin:0;display:flex;align-items:center;gap:6px;font-size:14px;line-height:20px;font-weight:600}& .tx h4 span{${ELL}}& .tx h4 .tg{flex:none}& .tx p{margin:2px 0 0;font-size:12px;line-height:18px;color:var(--ink3);${ELL}}
& .rw{margin-top:auto;display:flex;align-items:center;justify-content:space-between;padding-top:4px}& .rw .price b{font-size:18px}& .sold h4,& .sold .price{color:var(--ink3)}& .so{height:24px;padding:0 8px;border-radius:12px;background:var(--soft);color:var(--ink3);font-size:12px;line-height:24px}
& .ctl{display:flex;align-items:center}& .ctl .mi,& .ctl .vl{display:none}& .ctl.has .mi{display:flex;animation:§in .2s cubic-bezier(.2,0,0,1)}& .ctl.has .vl{display:block;min-width:28px;text-align:center;font-size:14px;font-weight:600;font-variant-numeric:tabular-nums}@keyframes §in{from{opacity:0;transform:translateX(8px)}}
& .rb{position:relative;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center}& .rb::after{content:"";position:absolute;inset:-8px}& .rb svg{width:16px;height:16px}& .pl{background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;transition:transform .15s cubic-bezier(.2,0,0,1)}& .pl:active{transform:scale(.9)}& .mi{box-shadow:inset 0 0 0 1.5px var(--p);color:var(--p-text);background:var(--card)}
& .bg{position:absolute;left:0;right:0;bottom:0;z-index:31;display:flex;align-items:center;gap:12px;height:64px;padding:0 16px 0 12px;background:var(--card);box-shadow:0 -4px 16px var(--sh08)}
& .bag{position:relative;flex:none;width:44px;height:44px;border-radius:50%;background:var(--pd);color:#fff;padding:10px;margin-top:-18px;box-shadow:0 0 0 4px var(--card),0 6px 14px var(--sh18);transition:transform .2s cubic-bezier(.2,0,0,1)}& .bag.bump{animation:§bump .3s cubic-bezier(.2,0,0,1)}@keyframes §bump{40%{transform:scale(1.14)}}
& .cnt{position:absolute;right:-6px;top:-6px;min-width:20px;height:20px;padding:0 5px;border-radius:12px;background:var(--hot);color:#fff;font-size:12px;line-height:20px;font-weight:600;text-align:center;box-shadow:0 0 0 2px var(--card)}
& .am{flex:1;min-width:0}& .am b{display:block;font-size:18px;line-height:24px;font-weight:600;font-variant-numeric:tabular-nums}& .am small{display:block;font-size:12px;line-height:16px;color:var(--ink3);${ELL}}
& .go{flex:none;min-width:112px;height:44px;padding:0 14px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:14px;font-weight:600;white-space:nowrap}& .go:disabled{background:var(--n5);color:var(--ink3);cursor:default}
& .ix-ov{align-items:flex-end}& .sh{position:relative;width:100%;margin-bottom:64px;padding:14px 16px 6px;border-radius:22px 22px 0 0;background:var(--card);box-shadow:0 -10px 30px var(--sh16);max-height:230px;overflow-y:auto;animation:§up .22s cubic-bezier(.2,0,0,1)}@keyframes §up{from{transform:translateY(16px);opacity:0}}
& .shh{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}& .shh b{font-size:16px;font-weight:600}& .shh button{position:relative;display:flex;align-items:center;gap:4px;font-size:12px;color:var(--ink3)}& .shh button::after{content:"";position:absolute;inset:-12px -8px}& .shh svg{width:14px;height:14px}
& .sr{display:flex;align-items:center;gap:10px;min-height:52px;font-size:14px}& .sr .n{flex:1;min-width:0;${ELL}}& .sr .p{flex:none;min-width:48px;text-align:right;font-weight:600;color:var(--price);font-variant-numeric:tabular-nums}
${SPIN}`),
    html: () => `<div class="mpsvc007"><div class="hd"><b>到店自取 · 静安店</b><span>预计 15 分钟可取</span></div><div class="ls">${DISH.map((x, k) => `<div class="dh ${x.sold ? 'sold' : ''}" data-i="${k}"><img src="${P(x.i)}" alt=""><div class="tx"><h4><span>${x.n}</span>${x.t ? `<i class="tg tg-soft">${x.t}</i>` : ''}</h4><p>${x.d}</p><div class="rw"><span class="price"><small>¥</small><b>${x.p}</b></span>${x.sold ? '<span class="so">已售罄</span>' : `<div class="ctl"><button class="rb mi" type="button" data-q="-1" data-i="${k}" aria-label="减少">${sv('minus')}</button><b class="vl" data-val>0</b><button class="rb pl" type="button" data-q="1" data-i="${k}" aria-label="加入">${sv('plus')}</button></div>`}</div></div></div>`).join('')}</div><div class="bg"><button class="bag" type="button" data-bag aria-label="购物袋">${sv('mgbag')}<i class="cnt" data-cnt hidden>0</i></button><div class="am"><b data-tot>未选购商品</b><small>配送费 ¥3 · ¥20 起送</small></div><button class="go" type="button" data-go disabled>¥20 起送</button></div><div class="ix-ov" data-ov="bag"><div class="ix-mask"></div><div class="sh"><div class="shh"><b>已选商品</b><button type="button" data-clr>${sv('trash')}清空</button></div><div data-shl></div></div></div></div>`,
    js: (root) => {
      const MIN = 20, qty = DISH.map(() => 0)
      const q = (s) => root.querySelector(s), ov = q('[data-ov]'), cnt = q('[data-cnt]'), tot = q('[data-tot]'), go = q('[data-go]'), bag = q('[data-bag]'), shl = q('[data-shl]')
      const render = (bump) => {
        const n = qty.reduce((s, v) => s + v, 0), money = qty.reduce((s, v, i) => s + v * DISH[i].p, 0)
        root.querySelectorAll('.dh').forEach((row) => { const i = +row.dataset.i, c = row.querySelector('.ctl'); if (!c) return; c.classList.toggle('has', qty[i] > 0); c.querySelector('[data-val]').textContent = qty[i] })
        cnt.hidden = n === 0; cnt.textContent = n; tot.textContent = n ? '¥' + money : '未选购商品'
        go.disabled = n === 0 || money < MIN; go.textContent = n === 0 ? `¥${MIN} 起送` : money < MIN ? `差 ¥${MIN - money} 起送` : '去结算'
        shl.innerHTML = qty.map((v, i) => v ? `<div class="sr"><span class="n">${DISH[i].n}</span><span class="p">¥${v * DISH[i].p}</span><div class="ctl has"><button class="rb mi" type="button" data-q="-1" data-i="${i}" aria-label="减少">${sv('minus')}</button><b class="vl">${v}</b><button class="rb pl" type="button" data-q="1" data-i="${i}" aria-label="增加">${sv('plus')}</button></div></div>` : '').join('')
        if (n === 0) ov.classList.remove('show')
        if (bump) { bag.classList.remove('bump'); void bag.offsetWidth; bag.classList.add('bump') }
      }
      render()
      root.addEventListener('click', (e) => {
        const b = e.target.closest('[data-q]')
        if (b) { const i = +b.dataset.i, d = +b.dataset.q; if (d > 0 && qty[i] >= DISH[i].lim) { IX.toast(root, `每人限购 ${DISH[i].lim} 份`); return } qty[i] = Math.max(0, qty[i] + d); render(d > 0); return }
        if (e.target.closest('[data-bag]')) { if (!qty.some((v) => v)) { IX.toast(root, '购物袋是空的，先选点什么吧'); return } ov.classList.toggle('show'); return }
        if (e.target.closest('[data-clr]')) { qty.fill(0); render(); return }
        const g = e.target.closest('[data-go]'); if (g && !g.disabled) { g.disabled = true; g.innerHTML = '<span class="sp"></span>'; later(root, 600, () => { g.disabled = false; render(); IX.toast(root, '前往确认订单') }) }
      })
    },
  })

/*__END__*/
})()
