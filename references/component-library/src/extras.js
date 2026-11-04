/* ===== 共用补充：线性图标、默认头像、示例数据（所有组件共用，保证内容一致）===== */
Object.assign(LINE, {
  truck: LINE.scooter, edit: '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>', trash: '<path d="M5 7h14M10 7V4.5h4V7M7 7l1 13h8l1-13"/>',
  phone: '<path d="M6.5 3.5h3l1.5 4-2 1.5a11 11 0 0 0 5 5l1.5-2 4 1.5v3a2 2 0 0 1-2 2A15 15 0 0 1 4.5 5.5a2 2 0 0 1 2-2z"/>',
  file: '<path d="M6 3.5h8l4 4v13H6z"/><path d="M14 3.5v4h4M9 12h6M9 16h6"/>', shield: '<path d="M12 3.5 19 6v5.5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M12 3.5v2.5M12 18v2.5M3.5 12H6M18 12h2.5M6 6l1.8 1.8M16.2 16.2 18 18M18 6l-1.8 1.8M7.8 16.2 6 18"/>',
  receipt: '<path d="M6 3.5h12v17l-3-2-3 2-3-2-3 2z"/><path d="M9 8.5h6M9 12.5h6"/>', camera: '<path d="M4 8h3.5L9 5.5h6L16.5 8H20v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
  refresh: '<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3M19.5 4.5v4h-4"/>', wallet2: '<rect x="3.5" y="6.5" width="17" height="12" rx="2"/><path d="M3.5 10h17"/>',
  filter: '<path d="M4 6h16l-6 7v5l-4 2v-7z"/>', sort: '<path d="M8 5v14M8 19l-3-3M8 19l3-3M16 19V5M16 5l-3 3M16 5l3 3"/>', tag: '<path d="M4 12.5V4h8.5l8 8-8.5 8.5z"/><circle cx="8.5" cy="8.5" r="1.2"/>',
  info: '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5M12 8v.5"/>', more: '<circle cx="5" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="19" cy="12" r="1.2"/>',
  qr: '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h3v3M20 14v6h-3"/>',
  down: '<path d="m6 9 6 6 6-6"/>', up: '<path d="m6 15 6-6 6 6"/>', right: '<path d="m9 5 7 7-7 7"/>', left: '<path d="m15 5-7 7 7 7"/>',
  arrowup: '<path d="M12 19V5M6 11l6-6 6 6"/>', arrowdown: '<path d="M12 5v14M6 13l6 6 6-6"/>', arrowright: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  starf: '<path d="m12 3.5 2.6 5.3 5.9.9-4.2 4.1 1 5.8L12 16.9 6.7 19.6l1-5.8L3.5 9.7l5.9-.9z" fill="currentColor"/>', sun: '<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6 7 7M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4"/>',
  moon: '<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/>', users: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.500-6s6.500 2.400 6.500 6"/><path d="M15.500 4.800a3.500 3.500 0 0 1 0 6.400M17.500 14.300c2.300.7 4 2.600 4 5.700"/>',
  lock: '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>', unlock: '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 7.500-1.800"/>',
  eye: '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.500 12 2.500 12z"/><circle cx="12" cy="12" r="2.800"/>', eyeoff: '<path d="M3 3l18 18M10 5.800A9 9 0 0 1 12 5.500c6 0 9.500 6.500 9.500 6.500a15 15 0 0 1-3 3.700M6.300 7.200A15 15 0 0 0 2.500 12S6 18.500 12 18.500a9 9 0 0 0 3.500-.7"/>',
  calendar: '<rect x="3.500" y="5" width="17" height="15.500" rx="2.500"/><path d="M3.500 10h17M8 3v4M16 3v4"/>', download: '<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>', upload: '<path d="M12 16V5M7 9l5-5 5 5M5 20h14"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.700 0l3-3a4 4 0 0 0-5.700-5.700l-1 1M14 10a4 4 0 0 0-5.700 0l-3 3a4 4 0 0 0 5.700 5.700l1-1"/>', mail: '<rect x="3.500" y="5.500" width="17" height="13" rx="2.500"/><path d="m4 7 8 6 8-6"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>', logout: '<path d="M9 4.500H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h3M14 8l4 4-4 4M18 12H9"/>', copy: '<rect x="8" y="8" width="12" height="12" rx="2.500"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
  save: '<path d="M5 4.500h11l3 3v12H5z"/><path d="M8 4.500v5h7v-5M8 19.500v-6h8v6"/>', key: '<circle cx="8" cy="14" r="3.500"/><path d="m10.500 11.500 8-8M15.500 6.500l2.500 2.500M13 9l2 2"/>',
  layers: '<path d="m12 3.500 9 5-9 5-9-5z"/><path d="m3 12.500 9 5 9-5M3 16.500l9 5 9-5"/>', list: '<path d="M8 6h12M8 12h12M8 18h12"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/>',
  barchart: '<path d="M5 20V10M12 20V4M19 20v-7"/>', piechart: '<path d="M12 3.500V12h8.500A8.500 8.500 0 0 0 12 3.500z"/><path d="M12 12 6 18A8.500 8.500 0 1 1 12 3.500"/>', linechart: '<path d="M3.500 19.500h17M5 15l4.500-5 3.500 3 6-7"/>',
  database: '<ellipse cx="12" cy="6" rx="7" ry="2.800"/><path d="M5 6v6c0 1.500 3.100 2.800 7 2.800s7-1.300 7-2.800V6M5 12v6c0 1.500 3.100 2.800 7 2.800s7-1.300 7-2.800v-6"/>',
  server: '<rect x="4" y="4" width="16" height="6.500" rx="2"/><rect x="4" y="13.500" width="16" height="6.500" rx="2"/><path d="M8 7.200h.01M8 16.800h.01"/>', cloud: '<path d="M7 18.500h10a4 4 0 0 0 .5-8 5.500 5.500 0 0 0-10.700 1.500A3.300 3.300 0 0 0 7 18.500z"/>',
  clipboard: '<rect x="5.500" y="4.500" width="13" height="16" rx="2.500"/><path d="M9 4.500V3.500h6v1M9 11h6M9 15h4"/>', flag: '<path d="M5.500 21V4M5.500 5h12l-2.500 4 2.500 4h-12"/>', play: '<path d="M8 5.500v13l11-6.500z"/>', pause: '<path d="M8 5.500v13M16 5.500v13"/>',
  image: '<rect x="3.500" y="4.500" width="17" height="15" rx="2.500"/><circle cx="9" cy="10" r="1.800"/><path d="m4 17 5-4.500 3.500 3 3-2.500 4.500 4"/>', video: '<rect x="3.500" y="6" width="12.500" height="12" rx="2.500"/><path d="m16 10.500 4.500-2.500v8L16 13.500"/>',
  folder: '<path d="M3.500 6.500a2 2 0 0 1 2-2h4l2 2.500h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>', bolt: '<path d="M13 3 5.500 13.500H11L10 21l7.500-10.500H12z"/>', pin2: '<path d="M12 21s6.500-5.600 6.500-11a6.500 6.500 0 0 0-13 0c0 5.400 6.500 11 6.500 11z"/><circle cx="12" cy="10" r="2.300"/>',
  alert: '<path d="M12 4 3 19.500h18z"/><path d="M12 10v4.500M12 17v.5"/>', checkc: '<circle cx="12" cy="12" r="8.500"/><path d="m8.500 12.500 2.500 2.500 4.500-5"/>', closec: '<circle cx="12" cy="12" r="8.500"/><path d="m9 9 6 6M15 9l-6 6"/>',
  grid2: '<rect x="3.500" y="3.500" width="7" height="7" rx="1.500"/><rect x="13.500" y="3.500" width="7" height="7" rx="1.500"/><rect x="3.500" y="13.500" width="7" height="7" rx="1.500"/><rect x="13.500" y="13.500" width="7" height="7" rx="1.500"/>',
  dashboard: '<rect x="3.500" y="3.500" width="7" height="9" rx="1.500"/><rect x="13.500" y="3.500" width="7" height="5" rx="1.500"/><rect x="3.500" y="15.500" width="7" height="5" rx="1.500"/><rect x="13.500" y="11.500" width="7" height="9" rx="1.500"/>',
  box: '<path d="m12 3.500 8 4v9l-8 4-8-4v-9z"/><path d="m4 7.500 8 4 8-4M12 11.500v9"/>', cube: '<path d="m12 3.500 8 4v9l-8 4-8-4v-9z"/>', hourglass: '<path d="M7 3.500h10M7 20.500h10M8 3.500c0 4 4 5 4 8.500S8 16.500 8 20.500M16 3.500c0 4-4 5-4 8.500s4 4.500 4 8.500"/>',
  drag: '<circle cx="9" cy="6" r="1.100"/><circle cx="15" cy="6" r="1.100"/><circle cx="9" cy="12" r="1.100"/><circle cx="15" cy="12" r="1.100"/><circle cx="9" cy="18" r="1.100"/><circle cx="15" cy="18" r="1.100"/>',
})
const sv2 = sv /* 同 sv(name)：线性图标，宽高 100%，描边 2 */
/* 默认头像：卡通动物，按序号固定，不用文字头像 */
const AV_BG = ['#F6E3D4', '#E3EEDC', '#E2E9F4', '#F2E1EA']
const AV_FUR = ['#C9A27E', '#B9C4AE', '#A8B8D0', '#D9AFC1']
const AV_FACE = [
  (c) => `<circle cx="14" cy="14" r="6" fill="${c}"/><circle cx="34" cy="14" r="6" fill="${c}"/><circle cx="24" cy="27" r="13" fill="${c}"/><circle cx="19.5" cy="25" r="1.7" fill="#4A3A33"/><circle cx="28.5" cy="25" r="1.7" fill="#4A3A33"/><ellipse cx="24" cy="30" rx="3" ry="2.2" fill="#4A3A33"/>`,
  (c) => `<ellipse cx="17" cy="11" rx="3.5" ry="9" fill="${c}"/><ellipse cx="31" cy="11" rx="3.5" ry="9" fill="${c}"/><circle cx="24" cy="29" r="12.5" fill="${c}"/><circle cx="19.5" cy="27" r="1.7" fill="#4A3A33"/><circle cx="28.5" cy="27" r="1.7" fill="#4A3A33"/><path d="M22 31.5q2 2 4 0" stroke="#4A3A33" stroke-width="1.6" fill="none" stroke-linecap="round"/>`,
  (c) => `<path d="M12 22 14 8l8 6zM36 22 34 8l-8 6z" fill="${c}"/><circle cx="24" cy="28" r="13" fill="${c}"/><circle cx="19.5" cy="26.5" r="1.7" fill="#4A3A33"/><circle cx="28.5" cy="26.5" r="1.7" fill="#4A3A33"/><path d="M22.5 30.5h3l-1.5 2z" fill="#4A3A33"/>`,
  (c) => `<circle cx="13" cy="15" r="5" fill="${c}"/><circle cx="35" cy="15" r="5" fill="${c}"/><circle cx="24" cy="28" r="13.5" fill="${c}"/><circle cx="24" cy="31" r="5.5" fill="#fff" opacity=".7"/><circle cx="19.5" cy="25.5" r="1.7" fill="#4A3A33"/><circle cx="28.5" cy="25.5" r="1.7" fill="#4A3A33"/><ellipse cx="24" cy="29.5" rx="2.2" ry="1.6" fill="#4A3A33"/>`,
]
const critter = (i, s = 40) => `<svg class="av" width="${s}" height="${s}" viewBox="0 0 48 48" aria-hidden="true" style="border-radius:50%;flex:none"><circle cx="24" cy="24" r="24" fill="${AV_BG[i % 4]}"/>${AV_FACE[i % 4](AV_FUR[i % 4])}</svg>`
/* 示例数据：姓名、订单、商品，所有组件共用，保证内容一致 */
const NAMES = ['林小满', '陈晓雨', '王子豪', '李安然', '周一帆', '赵可心', '吴梓轩', '郑佳怡', '孙明哲', '钱思远', '何婉清', '许知行']
const DEPTS = ['运营部', '市场部', '客服部', '财务部', '技术部', '仓储部']
const ORDER_STATUS = [['待付款', 'warn'], ['待发货', 'info'], ['配送中', 'info'], ['已完成', 'ok'], ['已取消', 'mute'], ['退款中', 'danger']]
const SKUS = [['无线降噪耳机', 599, 0], ['轻量跑鞋', 329, 1], ['陶瓷马克杯', 59, 2], ['帆布托特包', 129, 3], ['机械腕表', 899, 4], ['护眼台灯', 219, 5], ['保温水杯', 89, 6], ['保湿精华', 259, 7], ['双肩背包', 399, 8]]
const ORDER_ROWS = Array.from({ length: 24 }, (_, i) => {
  const s = SKUS[i % 9], st = ORDER_STATUS[(i * 5 + 1) % 6], q = (i % 3) + 1
  return { no: 'SO' + String(2026110400 + 128 - i * 7).padStart(10, '0'), who: NAMES[i % 12], sku: s[0], q, amt: s[1] * q, st: st[0], tone: st[1], at: `11-04 ${String(9 + (i % 12)).padStart(2, '0')}:${String((i * 17) % 60).padStart(2, '0')}`, img: s[2] }
})
const STATUS_TAG_CSS = '' /* 状态色统一用：ok #3F7D58 / warn #8A5A00 / danger #A8433B / info 主题色 / mute #6A727D；底色取各自的 10% 混白 */
