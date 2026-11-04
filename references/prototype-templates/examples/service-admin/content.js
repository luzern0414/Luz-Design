/* 到店服务示例的内容模块：只放这一个行业的演示数据（虚构）。没有商品、没有订单；工作台是“今天的预约与核销”。 */
const seeded = (seed) => () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296 }
const pad2 = (n) => String(n).padStart(2, '0')
const shift = (base, n) => { const d = new Date(base + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10) }

function seed(data) {
  const today = data.shell.today, R = seeded(7711), names = LIB.NAMES, pick = (a) => a[Math.floor(R() * a.length)]
  data.services = [['体验课', 60, 99, '体验'], ['标准服务', 45, 168, '标准'], ['深度服务', 90, 328, '深度'], ['双人套餐', 120, 598, '套餐'], ['专项调理', 60, 258, '标准'], ['亲子课程', 75, 218, '体验'], ['月度次卡（8 次）', 45, 1080, '次卡'], ['到店咨询', 30, 0, '体验']].map((s, i) => ({ id: 'S' + (101 + i), name: s[0], mins: s[1], price: s[2], cat: s[3], on: i !== 5, sales: 40 + Math.floor(R() * 300), intro: '' }))
  data.staff = names.slice(0, 6).map((n, i) => ({ id: 'T' + (i + 1), name: n, av: i }))
  const times = ['09:00', '09:30', '10:30', '11:00', '13:30', '14:00', '15:30', '16:00', '17:30', '19:00']
  data.bookings = Array.from({ length: 70 }, (_, i) => {
    const day = shift(today, -3 + Math.floor(i / 10)), isToday = day === today, past = day < today
    const st = past ? pick(['done', 'done', 'done', 'noshow', 'cancelled']) : isToday ? pick(['booked', 'arrived', 'arrived', 'done', 'noshow']) : 'booked'
    return { id: 'B' + (4001 + i), date: day, time: times[i % 10], customer: names[(i * 5 + 2) % 12], av: (i * 5 + 2) % 12, service: pick(data.services).name, staff: pick(data.staff).name, status: st }
  })
  data.clients = Array.from({ length: 36 }, (_, i) => ({ id: 'C' + (2001 + i), name: names[i % 12] + (i >= 12 ? ['', '', '二', '三'][Math.floor(i / 12)] : ''), av: i % 12, phone: `139 **** ${2000 + i * 11}`, card: ['次卡', '月卡', '体验卡'][i % 3], left: i % 3 === 2 ? 1 : Math.floor(R() * 12), lastVisit: shift(today, -Math.floor(R() * 60)), status: i % 7 === 6 ? 'sleep' : i % 9 === 8 ? 'new' : 'active', spent: Math.round(R() * 5000), note: i % 5 === 0 ? '偏好上午时段，对香味敏感，预约时提前提醒' : '' }))
  data.clients.forEach((c) => { if (c.lastVisit < shift(today, -45) && c.status === 'active') c.status = 'sleep' })
  data.redeems = Array.from({ length: 52 }, (_, i) => ({ id: 'V' + (8001 + i), time: shift(today, -Math.floor(i / 6)) + ' ' + pad2(9 + (i * 3) % 11) + ':' + pad2((i * 13) % 60), customer: names[(i * 7 + 4) % 12], av: (i * 7 + 4) % 12, service: pick(data.services).name, by: pick(data.staff).name, way: i % 3 === 0 ? 'code' : 'scan', status: i % 13 === 5 ? 'revoked' : 'done', amount: pick([99, 168, 328, 258, 0]) }))
  const days = {}
  for (let i = 34; i >= 0; i--) days[shift(today, -i)] = { date: shift(today, -i), bookings: 0, arrived: 0, verified: 0, revenue: 0 }
  Object.values(days).forEach((d, i) => { d.bookings = 14 + Math.floor(R() * 12) + (i % 7 === 5 ? 6 : 0); d.arrived = Math.round(d.bookings * (0.82 + R() * 0.12)); d.verified = Math.round(d.arrived * (0.9 + R() * 0.08)); d.revenue = d.verified * (120 + Math.floor(R() * 60)) })
  data.stats = { daily: Object.values(days) }
  const heat = {}; data.redeems.filter((r) => r.status === 'done').forEach((r) => { heat[r.service] = (heat[r.service] || 0) + 1 })
  data.breakdown = { service: Object.entries(heat).map(([name, value]) => ({ name, value })), source: [{ name: '小程序', value: 312 }, { name: '电话', value: 96 }, { name: '到店', value: 141 }] }
  data.audit = []
}

K.content({ init: seed, pages: {} })
