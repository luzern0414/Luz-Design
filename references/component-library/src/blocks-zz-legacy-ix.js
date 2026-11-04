/* ===== 旧 52 个模板的交互：只挂 js 钩子，不动它们的 HTML（少数已在源文件里改成真控件）===== */
const L = (id, fn) => {
  const b = BLOCKS.find((x) => x.id === id); if (!b) { console.warn('旧模板未找到', id); return }
  const prev = b.js; b.js = (r) => { if (prev) prev(r); fn(r) }
}
const q1 = (r, s) => r.querySelector(s)
const qa1 = (r, s) => [...r.querySelectorAll(s)]
const T1 = (r, m) => IX.toast(r, m)
const style1 = (r, t) => { const s = document.createElement('style'); s.textContent = t; r.appendChild(s) }
const onClick = (r, sel, fn) => qa1(r, sel).forEach((e, i) => e.addEventListener('click', (ev) => fn(e, ev, i)))
const radioGroup = (r, groupSel, itemSel, fn) => qa1(r, groupSel).forEach((g) => qa1(g, itemSel).forEach((it) => it.addEventListener('click', () => { qa1(g, itemSel).forEach((x) => x.classList.toggle('on', x === it)); if (fn) fn(it, g) })))
const tick1 = (r, secs, draw) => { let s = secs; draw(s); const t = setInterval(() => { if (!r.isConnected) { clearInterval(t); return } s = s > 0 ? s - 1 : secs; draw(s) }, 1000) }
const hms = (s) => [Math.floor(s / 3600), Math.floor(s % 3600 / 60), s % 60].map((x) => String(x).padStart(2, '0'))

/* 卡片 */
L('MP-CARD-001', (r) => onClick(r, '.add', () => T1(r, '已加入购物车')))
L('MP-CARD-002', (r) => onClick(r, '.add', () => T1(r, '已加入购物车')))
L('MP-CARD-003', (r) => { const b = q1(r, '.pc'); const o = b.textContent; let on = false; b.style.cursor = 'pointer'; b.addEventListener('click', () => { on = !on; b.textContent = on ? '已收藏 ✓' : o; T1(r, on ? '已收藏' : '已取消收藏') }) })
L('MP-CARD-004', (r) => onClick(r, '.au span:last-child', (e) => { const on = e.dataset.on !== '1'; const n = parseInt(e.textContent.replace(/\D/g, ''), 10) + (on ? 1 : -1); e.dataset.on = on ? '1' : '0'; e.textContent = (on ? '♥ ' : '♡ ') + n; e.style.color = on ? 'var(--p)' : ''; e.style.cursor = 'pointer' }))
L('MP-CARD-005', (r) => { const b = q1(r, 'button'); let on = false; b.addEventListener('click', () => { on = !on; b.textContent = on ? '已预订 ✓' : '立即预订'; T1(r, on ? '预订成功' : '已取消预订') }) })
L('MP-CARD-006', (r) => { const b = q1(r, '.go'); b.addEventListener('click', () => { b.textContent = '已抢到 ✓'; T1(r, '抢购成功') }) })
L('MP-CARD-007', (r) => { const b = q1(r, '.lk'); let on = false; b.style.cursor = 'pointer'; b.addEventListener('click', () => { on = !on; b.textContent = on ? '已加入购物车 ✓' : '加入购物车 →' }) })
L('MP-CARD-008', (r) => { const b = q1(r, 'button'); let on = false; b.addEventListener('click', () => { on = !on; b.textContent = on ? '已预约' : '预约'; T1(r, on ? '预约成功，门店将联系你' : '已取消预约') }) })
L('MP-CARD-009', (r) => {
  const c = q1(r, '.k9'); let pts = 2860; c.style.cursor = 'pointer'
  c.addEventListener('click', () => {
    pts += 100; q1(r, '.pt').firstChild.textContent = pts.toLocaleString('en-US'); const need = Math.max(0, 3500 - pts)
    q1(r, '.pgb i').style.width = Math.min(100, pts / 3500 * 100) + '%'; q1(r, '.nx').textContent = need ? `距钻石会员还差 ${need} 积分` : '已达钻石会员'; T1(r, '积分 +100')
  })
})
/* 按钮 */
;['MP-BTN-001', 'MP-BTN-002', 'MP-BTN-003', 'MP-BTN-004', 'MP-BTN-005'].forEach((id) => L(id, (r) => onClick(r, '.bt:not(.ds)', (b) => T1(r, '点击：' + b.textContent.trim()))))
L('MP-BTN-006', (r) => {
  style1(r, '.b8 .m{cursor:pointer}.b8 .m.on{color:var(--p-fg)}.b8 .m.on svg{fill:var(--p)}')
  onClick(r, '.m', (m) => m.classList.toggle('on'))
  onClick(r, '.a', () => T1(r, '已加入购物车')); onClick(r, '.b', () => T1(r, '去结算'))
})
L('MP-BTN-007', (r) => {
  const ibs = qa1(r, '.ib'); const cart = ibs[0], heart = ibs[1]; style1(r, '.b9 .ib{cursor:pointer}')
  cart.addEventListener('click', () => { const b = q1(cart, 'b'); b.textContent = +b.textContent + 1 })
  heart.addEventListener('click', () => heart.classList.toggle('on'))
  ibs[2].addEventListener('click', () => T1(r, '已复制分享链接')); ibs[3].addEventListener('click', () => T1(r, '快速操作'))
})
L('MP-BTN-008', (r) => onClick(r, '.bt.x:not(.ds)', (b) => {
  const orig = b.innerHTML, cls = b.className
  b.addEventListener('click', () => {
    if (b.dataset.busy) return; b.dataset.busy = '1'; b.className = 'bt x ld'; b.innerHTML = '<span class="sp"></span>处理中'
    setTimeout(() => { b.className = 'bt x ok'; b.innerHTML = sv('check') + '完成'; setTimeout(() => { b.className = cls; b.innerHTML = orig; delete b.dataset.busy }, 1400) }, 1200)
  })
}))
/* 入口 */
L('MP-ENT-001', (r) => { style1(r, '.i1>div{cursor:pointer}.i1>div:active{transform:scale(.95)}'); onClick(r, '.i1>div', (d) => T1(r, '进入「' + d.textContent.trim() + '」')) })
L('MP-ENT-002', (r) => { style1(r, '.i2>div{cursor:pointer}.i2>div:active{transform:scale(.95)}'); onClick(r, '.i2>div', (d) => T1(r, '进入「' + d.textContent.trim() + '」')) })
L('MP-ENT-003', (r) => { style1(r, '.i3 .c{cursor:pointer;transition:transform .15s}.i3 .c:active{transform:scale(.97)}'); onClick(r, '.i3 .c', (d) => T1(r, '进入「' + q1(d, 'b').textContent + '」')) })
L('MP-ENT-004', (r) => radioGroup(r, '.i4', '.p'))
L('MP-ENT-005', (r) => { style1(r, '.i5>div{cursor:pointer}.i5>div:active{transform:scale(.95)}'); onClick(r, '.i5>div', (d) => T1(r, '进入「' + d.textContent.trim() + '」')) })
L('MP-ENT-006', (r) => { style1(r, '.i6 .r{cursor:pointer;transition:box-shadow .15s}.i6 .r.sel{box-shadow:0 0 0 2px var(--p),0 4px 14px var(--sh06)}'); onClick(r, '.i6 .r', (d) => { qa1(r, '.i6 .r').forEach((x) => x.classList.toggle('sel', x === d)); T1(r, '选用 ' + q1(d, 'b').firstChild.textContent + ' 风格') }) })
L('MP-ENT-007', (r) => { style1(r, '.i7 .t{cursor:pointer;transition:transform .15s}.i7 .t:active{transform:scale(.94)}'); onClick(r, '.i7 .t', (d) => T1(r, d.parentNode.textContent.trim())) })
/* 头图 */
;['MP-HDR-001', 'MP-HDR-002', 'MP-HDR-003', 'MP-HDR-004'].forEach((id) => L(id, (r) => onClick(r, 'button', (b) => T1(r, '点击：' + b.textContent.trim()))))
L('MP-HDR-006', (r) => { style1(r, '.h6 .a,.h6 .b,.h6 .c{cursor:pointer;transition:transform .15s}.h6 .a:active,.h6 .b:active,.h6 .c:active{transform:scale(.97)}'); onClick(r, '.h6 .a,.h6 .b,.h6 .c', (d) => T1(r, '进入「' + q1(d, 'h4').textContent + '」')) })
/* 价格与标签 */
L('MP-PRC-002', (r) => { style1(r, '.t2 .tg{cursor:pointer}.t2 .tg.sel{box-shadow:0 0 0 2px var(--p)}'); onClick(r, '.t2 .tg', (t) => t.classList.toggle('sel')) })
L('MP-PRC-004', (r) => {
  const s = q1(r, '.st5'); s.style.cursor = 'pointer'
  s.addEventListener('click', (e) => { const b = s.getBoundingClientRect(); const p = Math.max(0.2, Math.min(1, (e.clientX - b.left) / b.width)); const v = Math.ceil(p * 10) / 2; s.style.setProperty('--w', (v / 5 * 100) + '%'); q1(r, '.r b').textContent = v.toFixed(1) })
})
L('MP-PRC-005', (r) => { style1(r, '.t5 .d{cursor:pointer}.t5 .d.sel{box-shadow:0 0 0 2px var(--p)}'); onClick(r, '.t5 .d', (t) => t.classList.toggle('sel')) })
L('MP-PRC-006', (r) => tick1(r, 2 * 3600 + 15 * 60 + 8, (s) => { const [h, m, x] = hms(s); qa1(r, '.a i, .c i').forEach((e, i) => { e.textContent = [h, m, x][i % 3] }); q1(r, '.b').textContent = `距结束 ${h}:${m}:${x}` }))
/* 营销 */
L('MP-MKT-001', (r) => onClick(r, '.r button', (b) => {
  const c = b.closest('.c'); if (c.classList.contains('used')) { c.classList.remove('used'); b.textContent = '领取'; return }
  c.classList.add('used'); b.textContent = '已领取'; T1(r, '领取成功，已放入我的优惠券')
}))
L('MP-MKT-002', (r) => {
  tick1(r, 2 * 3600 + 15 * 60 + 8, (s) => { const p = hms(s); qa1(r, '.ct i').forEach((e, i) => { e.textContent = p[i] }) })
  style1(r, '.m3 .c{cursor:pointer;transition:transform .15s}.m3 .c:active{transform:scale(.97)}')
  onClick(r, '.m3 .c', (c) => { const bar = q1(c, '.pg i'), t = q1(c, 'small'); const n = Math.min(100, parseInt(bar.style.width, 10) + 3); bar.style.width = n + '%'; t.textContent = n >= 100 ? '已抢光' : `已抢 ${n}%` })
})
L('MP-MKT-003', (r) => {
  const b = q1(r, '.m4 button'), gp = q1(r, '.gp'), em = q1(r, '.gp em'); let joined = false
  b.addEventListener('click', () => {
    joined = !joined; b.textContent = joined ? '已成团 ✓' : '去拼团'; em.textContent = joined ? '拼团成功' : '还差 1 人'
    if (joined) { const i = document.createElement('i'); i.style.background = 'linear-gradient(145deg,#E3C9D2,#C08FA0)'; gp.insertBefore(i, em); T1(r, '拼团成功') } else { gp.removeChild(gp.querySelectorAll('i')[3]) }
  })
})
L('MP-MKT-004', (r) => {
  let rest = 31; const a = q1(r, '.t a'), span = q1(r, '.t span'), bar = q1(r, '.pg i'); a.style.cursor = 'pointer'
  a.addEventListener('click', () => { rest = Math.max(0, rest - 10); bar.style.width = ((199 - rest) / 199 * 100) + '%'; span.innerHTML = rest ? `再买 <b>¥${rest}</b> 免运费` : '<b>已享受免运费</b>'; if (!rest) a.textContent = '去结算 ›' })
})
L('MP-MKT-005', (r) => {
  style1(r, '.m6 .d>div{cursor:pointer}'); const days = qa1(r, '.m6 .d>div'), h = q1(r, '.m6 .h b')
  days.forEach((d) => d.addEventListener('click', () => {
    const next = days.find((x) => !x.classList.contains('on')); if (d !== next) { T1(r, '请按顺序签到'); return }
    d.classList.add('on'); q1(d, 'i').textContent = '✓'; const n = days.filter((x) => x.classList.contains('on')).length; h.textContent = `已连续签到 ${n} 天`; T1(r, n === 7 ? '签到成功，大礼已发放' : '签到成功 +5 积分')
  }))
})
/* 导航 */
L('MP-NAV-001', (r) => { onClick(r, '.bk', () => T1(r, '返回上一页')); onClick(r, '.sr', () => T1(r, '打开搜索')) })
L('MP-NAV-002', (r) => qa1(r, '.n2 .t').forEach((t) => qa1(t, 'button').forEach((b) => b.addEventListener('click', () => { if (b.classList.contains('ctr')) { T1(r, '发布'); return } qa1(t, 'button:not(.ctr)').forEach((x) => x.classList.toggle('on', x === b)) }))))
L('MP-NAV-003', (r) => { radioGroup(r, '.n3 .u', 'button'); radioGroup(r, '.n3 .p', 'button'); radioGroup(r, '.n3 .s', 'button') })
L('MP-NAV-004', (r) => {
  const sets = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 0, 5, 2], [3, 6, 1, 8]], names = ['新品', '热销', '礼品', '极速达']
  radioGroup(r, '.rl', ':scope > div', (it) => { const k = qa1(r, '.rl > div').indexOf(it); q1(r, '.ct h5').textContent = names[k]; qa1(r, '.gr img').forEach((im, i) => { im.src = P(sets[k][i]) }) })
})
L('MP-NAV-005', (r) => {
  style1(r, '.n5 .ar.up i:first-child{border-bottom-color:var(--p)}.n5 .ar.up i:last-child{border-top-color:var(--n9)}')
  const btns = qa1(r, '.n5 button:not(.ft)')
  btns.forEach((b) => b.addEventListener('click', () => {
    const price = b.querySelector('.ar')
    if (price) { const was = b.classList.contains('on'); if (was) price.classList.toggle('up') ; else price.classList.remove('up') }
    btns.forEach((x) => x.classList.toggle('on', x === b))
  }))
  onClick(r, '.ft', () => T1(r, '打开筛选面板'))
})
/* 表单 */
L('MP-FORM-001', (r) => onClick(r, '.s button', () => T1(r, '搜索：' + (q1(r, '.s.a input').value || '全部商品'))))
L('MP-FORM-003', (r) => {
  const a = q1(r, '[data-addr]'), em = q1(r, '.em'); const chk = () => { const bad = a.value.trim() === ''; a.classList.toggle('er', bad); em.style.display = bad ? '' : 'none' }
  a.addEventListener('input', chk); a.addEventListener('blur', chk)
})
/* 弹层与反馈 */
L('MP-FB-001', (r) => {
  const root = q1(r, '.o1'); root.insertAdjacentHTML('beforeend', '<div class="o1b"><button type="button" data-toast="已加入购物车">加入购物车</button><button type="button" data-toast="已复制">复制链接</button><button type="button" data-toast="保存成功">保存</button></div>')
  style1(r, '.o1b{flex-basis:100%;display:flex;gap:8px;justify-content:center;margin-top:6px}.o1b button{height:36px;padding:0 14px;border-radius:18px;background:var(--card);font-size:14px;color:var(--ink2);box-shadow:0 2px 8px var(--sh10)}')
})
L('MP-FB-002', (r) => {
  const d = q1(r, '.o2'); const wrap = d.parentNode; const re = document.createElement('button'); re.type = 'button'; re.textContent = '重新打开对话框'; re.hidden = true; re.style.cssText = 'height:40px;padding:0 20px;border-radius:20px;background:var(--pt);color:var(--p-text);font-weight:600;font-size:14px'; wrap.appendChild(re)
  const close = (msg) => { d.hidden = true; re.hidden = false; if (msg) T1(r, msg) }
  q1(d, '.a').addEventListener('click', () => close()); q1(d, '.b').addEventListener('click', () => close('已移出购物车')); re.addEventListener('click', () => { d.hidden = false; re.hidden = true })
})
L('MP-FB-003', (r) => {
  const sh = q1(r, '.o3'); const wrap = sh.parentNode; const re = document.createElement('button'); re.type = 'button'; re.textContent = '选择规格'; re.hidden = true; re.style.cssText = 'height:40px;padding:0 20px;border-radius:20px;background:var(--pt);color:var(--p-text);font-weight:600;font-size:14px'; wrap.appendChild(re)
  q1(sh, '.x').style.cursor = 'pointer'; q1(sh, '.x').addEventListener('click', () => { sh.hidden = true; re.hidden = false })
  re.addEventListener('click', () => { sh.hidden = false; re.hidden = true })
  radioGroup(sh, '.sp', 'button', (it) => { q1(sh, '.h .t > small').textContent = '已选：' + it.textContent })
  q1(sh, '.go').addEventListener('click', () => { T1(r, '已加入购物车'); sh.hidden = true; re.hidden = false })
})
