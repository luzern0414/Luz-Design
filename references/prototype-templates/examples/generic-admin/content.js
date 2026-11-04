/* 通用示例的内容模块：只做两件事——按固定随机数生成演示数据（虚构），以及一个自定义页面（个人中心）。
 * 机制（外壳、列表、表单、设置、工作台）都在 admin 模板里；这里没有机制，只有某一个“商品与订单运营后台”的数据与专属页面。 */
const seeded = (seed) => () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296 }
const BASE = [['无线降噪耳机', '石墨灰 · 主动降噪', 599, '数码'], ['轻量跑鞋', '云白 · 男女同款', 329, '鞋包'], ['陶瓷马克杯', '手作釉面 · 350ml', 69, '家居'], ['帆布托特包', '原色 · 可放 14 寸', 159, '鞋包'], ['机械腕表', '钢壳皮带 · 40mm', 899, '数码'], ['护眼台灯', '无频闪 · 三档调光', 219, '家居'], ['保温水杯', '鼠尾草绿 · 500ml', 89, '家居'], ['保湿精华', '玻尿酸 · 30ml', 258, '美妆'], ['通勤双肩包', '米色 · 防泼水', 369, '鞋包']]
const VARIANT = ['', '（升级款）', '（礼盒装）']
const pad2 = (n) => String(n).padStart(2, '0')
const ymd = (d) => `${d.getUTCFullYear()}-${pad2(d.getUTCMonth() + 1)}-${pad2(d.getUTCDate())}`
const shift = (base, n) => { const d = new Date(base + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return ymd(d) }

function seed(data) {
  const today = data.shell.today, R = seeded(20261104), pick = (a) => a[Math.floor(R() * a.length)], names = LIB.NAMES
  /* 商品 */
  data.products = Array.from({ length: 27 }, (_, i) => {
    const b = BASE[i % 9], v = VARIANT[Math.floor(i / 9)], price = Math.round(b[2] * (1 + Math.floor(i / 9) * 0.12))
    const stock = i % 11 === 4 ? 0 : 6 + Math.floor(R() * 180)
    return { id: 'P' + (1001 + i), name: b[0] + v, spec: b[1], cat: b[3], price, stock, on: stock > 0 && i % 7 !== 3, images: [i % 9], tags: i % 4 === 0 ? ['热卖'] : [], desc: '', sales: 20 + Math.floor(R() * 900), updatedAt: shift(today, -Math.floor(R() * 20)) + ' 1' + (i % 10) + ':20' }
  })
  /* 订单：越早越可能已完成，最近的才有待发货与待付款 */
  const chans = ['app', 'web', 'mini'], pays = ['wechat', 'alipay', 'card']
  data.orders = Array.from({ length: 128 }, (_, i) => {
    const age = Math.floor((i / 128) * 35 + R() * 1.5), day = shift(today, -Math.min(34, age)), n = 1 + Math.floor(R() * 3)
    const items = Array.from({ length: n }, () => { const p = pick(data.products); return { name: p.name, qty: 1 + Math.floor(R() * 2), price: p.price } })
    const amount = items.reduce((a, x) => a + x.qty * x.price, 0)
    let st; const r = R()
    if (age <= 1) st = r < 0.45 ? 'pending' : r < 0.7 ? 'unpaid' : r < 0.9 ? 'shipped' : 'done'
    else if (age <= 4) st = r < 0.3 ? 'pending' : r < 0.55 ? 'shipped' : r < 0.9 ? 'done' : 'closed'
    else st = r < 0.82 ? 'done' : r < 0.92 ? 'closed' : 'refund'
    const time = `${day} ${pad2(8 + Math.floor(R() * 13))}:${pad2(Math.floor(R() * 60))}`
    const log = [{ time, text: '买家提交订单' }]
    if (st !== 'unpaid' && st !== 'closed') log.push({ time, text: '支付成功，系统审核通过' })
    if (st === 'shipped' || st === 'done' || st === 'refund') log.push({ time: time.slice(0, 11) + '15:05', text: '商家发货' })
    if (st === 'done') log.push({ time: shift(day, 2) + ' 11:30', text: '买家确认收货' })
    if (st === 'closed') log.push({ time: time.slice(0, 11) + '23:59', text: '超时未支付，订单自动关闭' })
    if (st === 'refund') log.push({ time: shift(day, 3) + ' 09:40', text: '退款完成，金额原路退回' })
    return { id: 'SO' + (20261104900 - i * 3), no: 'SO' + (20261104900 - i * 3), customer: names[(i * 5 + 3) % 12], av: (i * 5 + 3) % 12, amount, goods: items.map((x) => `${x.name} × ${x.qty}`).join('；'), status: st, channel: pick(chans), pay: pick(pays), createdAt: time, items, addr: pick(['上海市静安区南京西路 1266 号 12 楼', '上海市浦东新区世纪大道 88 号 3 单元 502', '杭州市西湖区文三路 478 号 8 层', '成都市锦江区红星路 19 号 2 栋 1601']), log }
  })
  data.orders.sort((a, b) => b.createdAt.localeCompare(a.createdAt))
  /* 会员 */
  data.members = Array.from({ length: 44 }, (_, i) => {
    const st = i % 9 === 8 ? 'closed' : i % 7 === 6 ? 'expired' : i % 6 === 5 ? 'expiring' : 'active'
    return { id: 'M' + (3001 + i), name: names[i % 12] + (i >= 12 ? ['', '', '', '二'][Math.floor(i / 12)] : ''), av: i % 12, phone: `138 **** ${1000 + i * 7}`, level: ['normal', 'silver', 'gold'][i % 3 === 2 ? 2 : i % 2], points: Math.floor(R() * 8000), spent: Math.round(R() * 12000 * 100) / 100, lastVisit: shift(today, -Math.floor(R() * 40)), status: st, enabled: st !== 'closed' }
  })
  /* 营销活动 */
  data.promos = [['新客立减', 'discount', '2026-10-01', '2026-12-31', 20, 0, 1203], ['满 300 减 40', 'full', '2026-11-01', '2026-11-30', 40, 300, 482], ['双十一预热券', 'coupon', '2026-11-01', '2026-11-11', 30, 199, 960], ['会员日 9 折', 'discount', '2026-11-08', '2026-11-08', 10, 0, 0], ['老客回归礼', 'coupon', '2026-10-15', '2026-11-15', 15, 99, 211], ['周三晚间秒杀', 'discount', '2026-09-01', '2026-10-31', 25, 0, 1720], ['满 500 减 80', 'full', '2026-11-12', '2026-12-12', 80, 500, 0], ['拉新有礼', 'coupon', '2026-10-20', '2026-12-20', 10, 0, 365]].map((p, i) => ({ id: 'A' + (501 + i), name: p[0], type: p[1], start: p[2], end: p[3], range: `${p[2]} 至 ${p[3]}`, off: p[4], threshold: p[5], used: p[6], on: p[3] >= today && p[2] <= today, state: p[3] < today ? 'ended' : p[2] > today ? 'scheduled' : 'running' }))
  /* 评价 */
  const texts = ['做工扎实，降噪效果比预期好，通勤路上很安静。', '尺码偏小半码，建议拍大一码。', '收到的杯子有一处釉面瑕疵，已联系客服，处理得还算及时，希望包装再加强一点，运输途中杯口有轻微磕碰，不过不影响使用。', '包很轻，容量够用，肩带稍窄。', '物流很快，第二天就到了。', '表带有点硬，戴了几天才适应。', '台灯三档亮度很实用，没有频闪。', '香味太浓，不太适合敏感肌。']
  data.reviews = Array.from({ length: 36 }, (_, i) => {
    const score = [5, 4, 2, 5, 1, 4, 5, 3][i % 8], st = i % 5 === 4 ? 'hidden' : i % 3 === 0 ? 'done' : 'todo'
    return { id: 'R' + (7001 + i), product: pick(data.products).name, customer: names[(i * 7 + 1) % 12], av: (i * 7 + 1) % 12, score, text: texts[i % 8], createdAt: shift(today, -Math.floor(R() * 25)) + ' ' + pad2(9 + (i % 12)) + ':' + pad2((i * 13) % 60), status: st, reply: st === 'done' ? '感谢反馈，已为您安排处理。' : '' }
  })
  /* 财务对账 */
  data.ledger = Array.from({ length: 30 }, (_, i) => {
    const gross = Math.round((8000 + R() * 9000) * 100) / 100, fee = Math.round(gross * 0.006 * 100) / 100, st = i % 9 === 4 ? 'diff' : i < 2 ? 'pending' : 'matched'
    return { id: 'F' + (9001 + i), date: shift(today, -i - 1), channel: ['wechat', 'alipay', 'card'][i % 3], count: 18 + Math.floor(R() * 40), gross, fee, net: Math.round((gross - fee) * 100) / 100, status: st }
  })
  /* 日统计：由订单计算（销售额、订单数、退款），新增会员取固定随机 */
  const days = {}
  for (let i = 34; i >= 0; i--) days[shift(today, -i)] = { date: shift(today, -i), sales: 0, orders: 0, refund: 0, members: 3 + Math.floor(R() * 12) }
  data.orders.forEach((o) => { const d = days[o.createdAt.slice(0, 10)]; if (!d) return; if (o.status === 'refund') d.refund += o.amount; else if (o.status !== 'closed' && o.status !== 'unpaid') { d.sales += o.amount; d.orders += 1 } })
  data.stats = { daily: Object.values(days) }
  const chName = { app: '应用', web: '网页', mini: '小程序' }, by = { app: 0, web: 0, mini: 0 }, top = {}
  data.orders.filter((o) => o.status !== 'closed' && o.status !== 'unpaid').forEach((o) => { by[o.channel] += o.amount; o.items.forEach((x) => { top[x.name] = (top[x.name] || 0) + x.qty * x.price }) })
  data.breakdown = { channel: Object.entries(by).map(([k, v]) => ({ name: chName[k], value: Math.round(v) })), top: Object.entries(top).map(([name, value]) => ({ name, value: Math.round(value) })) }
  /* 动态与日志 */
  data.feed = data.orders.filter((o) => o.status === 'pending').slice(0, 6).map((o) => ({ time: o.createdAt.slice(11), text: `${o.customer} 下单 ¥${o.amount.toFixed(2)}，等待发货`, sheet: 'order-detail', id: o.id }))
  const roleOf = ['管理员', '运营', '运营', '管理员']
  data.audit = Array.from({ length: 24 }, (_, i) => ({ id: 'L' + (6001 + i), time: shift(today, -Math.floor(i / 4)) + ' ' + pad2(9 + (i * 3) % 10) + ':' + pad2((i * 17) % 60), who: ['管理员', '林运营', '周运营', '管理员'][i % 4], role: roleOf[i % 4], level: i % 8 === 3 ? 'warn' : i % 11 === 5 ? 'error' : 'info', what: ['登录后台', '修改商品「陶瓷马克杯」库存为 80', '发货订单 SO20261104888', '停用营销活动「周三晚间秒杀」', '导出订单 128 条', '回复评价 R7003', '调整会员等级', '登录失败：密码错误（已锁定 5 分钟）'][i % 8], result: i % 11 === 5 ? '失败' : '成功' }))
}

K.content({
  init: seed,
  pages: {
    /* 个人中心：库的“个人资料”组件 + 自己的最近登录卡（custom 页面也用库的积木，并保留 data-cid） */
    profile(frame, ctx) {
      const sessions = [['本机 · 浏览器', '2026-11-04 09:12', '上海'], ['办公电脑 · 浏览器', '2026-11-03 18:40', '上海'], ['手机 · 浏览器', '2026-11-02 08:05', '杭州']]
      return `${K.block('AD-MGMT-006').replace('class="pt-blk"', 'class="pt-blk ad-blk"')}<section class="ad-card" style="padding:16px 20px" data-cid="AD-MGMT-008"><h3 style="margin:0 0 8px;font-size:16px;font-weight:600">最近登录</h3><table class="ad-mini"><thead><tr><th class="l">设备</th><th>时间</th><th>地点</th></tr></thead><tbody>${sessions.map((s) => `<tr><td class="l">${s[0]}</td><td>${s[1]}</td><td>${s[2]}</td></tr>`).join('')}</tbody></table></section>`
    },
  },
})
