/* ===== 小程序 · 基础类别补充：表单 FORM / 弹层 FB / 导航 NAV / 按钮 BTN / 卡片 CARD / 头图 HDR / 入口 ENT =====
 * 编号：FORM 004–010 · FB 004–008 · NAV 006–010 · BTN 009–011 · CARD 010–012 · HDR 007–008 · ENT 008–010
 * 全部包在一个块作用域里，局部常量不会和其他文件冲突。 */
Object.assign(LINE, {
  mpb_headset: '<path d="M4.5 14v-2a7.5 7.5 0 0 1 15 0v2"/><rect x="3.5" y="13" width="4" height="6" rx="1.8"/><rect x="16.5" y="13" width="4" height="6" rx="1.8"/><path d="M18.5 19c0 1.4-1.6 2-4 2"/>',
  mpb_notice: '<path d="M4 10v4h3l7 4V6l-7 4z"/><path d="M17.5 9.5a3.5 3.5 0 0 1 0 5"/>',
  mpb_wifioff: '<path d="M3.5 3.5l17 17"/><path d="M2.5 9.5a15 15 0 0 1 4.500-2.700M21.500 9.500A15 15 0 0 0 12 5.500M6 13a9 9 0 0 1 2.500-1.800M18 13a9 9 0 0 0-3.300-2M9.500 16.500a4.500 4.500 0 0 1 5 0M12 20h.01"/>',
  mpb_chevs: '<path d="m6.500 6 6 6-6 6M12.500 6l6 6-6 6"/>',
  mpb_store: '<path d="M4 9.500 5.500 4.500h13L20 9.500"/><path d="M4 9.500a2.500 2.500 0 0 0 5 0 2.500 2.500 0 0 0 6 0 2.500 2.500 0 0 0 5 0"/><path d="M5.500 12.500V20h13v-7.500"/>',
  mpb_verified: '<path d="M12 3.500 19 6v5.500c0 4.500-3 7.500-7 9-4-1.500-7-4.500-7-9V6z"/><path d="m9 12 2.200 2.200L15.500 10"/>',
})
{
const q1 = (r, s) => r.querySelector(s)
const qa = (r, s) => [...r.querySelectorAll(s)]
const clamp = (v, a, b) => Math.max(a, Math.min(b, v))
/* 块被重渲染后旧节点会脱离页面：计时器和延时都先看一眼 root 还在不在 */
const later = (root, ms, fn) => setTimeout(() => { if (root.isConnected) fn() }, ms)
const every = (root, ms, fn) => { const id = setInterval(() => { if (!root.isConnected) clearInterval(id); else fn() }, ms); return id }
/* CSS 写法：& 代表块根选择器 .前缀，@@ 代表前缀本身（用在 @keyframes 名里） */
const CSS = (p, s) => s.replace(/@@/g, p).replace(/&/g, '.' + p)
const mi = (n, s = 20, x = '') => `<span style="display:inline-flex;flex:none;width:${s}px;height:${s}px;${x}">${sv(n)}</span>`
const SPIN = (p, sel, size = 18, col = '#fff', track = 'rgba(255,255,255,.4)') => `${sel}{width:${size}px;height:${size}px;flex:none;border-radius:50%;border:2.5px solid ${track};border-top-color:${col};animation:${p}s .8s linear infinite}@keyframes ${p}s{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){${sel}{animation:none}}`
const PRIMARY = 'background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;box-shadow:0 8px 18px rgba(var(--p-rgb),.19)'
const SHADOW = '0 10px 26px rgba(31,35,41,.08)'
const DANGER = 'var(--danger)', OKC = 'var(--ok)', OKT = 'var(--ok-ink)', WARN = 'var(--warn)'
/* 小控件的点击区补到 44：用伪元素外扩，不改外观 */
const HIT = (sel, x = 6, y = 6) => `${sel}{position:relative}${sel}::after{content:"";position:absolute;inset:-${y}px -${x}px}`
/* ───────── FORM 表单与输入 ───────── */
const FIELD = `& .fld{display:flex;align-items:center;gap:8px;height:48px;padding:0 6px 0 14px;border-radius:12px;border:1px solid var(--n7);background:var(--card)}& .fld:focus-within{border-color:var(--ink2)}& .fld.bad{border-color:${DANGER};background:#FDF8F7}& .fld input{flex:1;min-width:0;height:100%;border:0;outline:0;background:none;font:inherit;font-size:16px;color:var(--ink)}& .fld input::placeholder{color:color-mix(in srgb,var(--ink4) 52%,var(--ink3))}& .msg{min-height:16px;margin:4px 2px 8px;font-size:12px;line-height:16px;color:var(--ink3)}& .msg.er{color:${DANGER}}& .msg.ok{color:${OKT}}`

def({
  id: 'MP-FORM-004', name: '手机号验证码登录', style: '倒计时',
  fit: '登录注册、绑定手机、找回账号；一屏完成手机号、验证码、协议勾选',
  avoid: '已有微信一键登录时把它当主入口（只做备选）；验证码位数不固定的场景',
  kw: 'login 登录 手机号 验证码 倒计时 短信 绑定手机 协议',
  css: CSS('mpform004', `&{width:340px;background:var(--card);border-radius:22px;padding:26px 22px 22px;box-shadow:${SHADOW}}& h4{margin:0;font-size:22px;line-height:30px;font-weight:700}& .sub{margin:6px 0 22px;font-size:14px;line-height:20px;color:var(--ink2)}${FIELD}& .pre{display:flex;align-items:center;gap:2px;height:22px;padding-right:10px;border-right:1px solid var(--n6);font-size:16px;color:var(--ink)}& .pre span{display:inline-flex;width:14px;height:14px;color:var(--ink3)}& .clr{position:relative;width:32px;height:32px;display:flex;align-items:center;justify-content:center;color:color-mix(in srgb,var(--ink6) 31%,var(--ink5))}& .clr::after{content:"";position:absolute;inset:-6px -2px}& .clr span{display:inline-flex;width:16px;height:16px}& .get{position:relative;flex:none;height:36px;min-width:112px;padding:0 12px;border-radius:18px;background:var(--pt);color:var(--p-text);font-size:14px;font-weight:600;text-align:center}& .get::after{content:"";position:absolute;inset:-4px -2px}& .get:disabled{background:var(--soft);color:var(--ink3);cursor:default}& .agree{display:flex;align-items:flex-start;gap:8px;margin:2px 0 18px;font-size:12px;line-height:18px;color:var(--ink2);cursor:pointer}& .ck{position:relative;flex:none;width:18px;height:18px;border-radius:50%;border:1.5px solid var(--n10);display:flex;align-items:center;justify-content:center;color:transparent;transition:background-color .15s,border-color .15s}& .ck::after{content:"";position:absolute;inset:-13px}& .ck span{display:inline-flex;width:12px;height:12px}& .ck.on{background:var(--p);border-color:var(--p);color:#fff}& .agree a{color:var(--p-text);font-weight:600}& .agree.shake{animation:@@sh .32s cubic-bezier(.2,0,0,1)}@keyframes @@sh{25%{transform:translateX(-5px)}60%{transform:translateX(5px)}}& .msg.ag{margin:-12px 2px 12px}& .go{width:100%;height:48px;border-radius:24px;display:flex;align-items:center;justify-content:center;gap:8px;font-size:16px;font-weight:600;${PRIMARY};transition:opacity .2s}& .go.idle{opacity:.5;box-shadow:none}& .go.busy{cursor:progress}& .go.done{background:var(--ok-fill);box-shadow:none}& .go svg{width:20px;height:20px}${SPIN('mpform004', '& .sp', 18)}`),
  html: () => `<div class="mpform004"><h4>手机号登录</h4><p class="sub">未注册的手机号验证后将自动创建账号</p>
<div class="fld" data-f="phone"><span class="pre">+86<span>${sv('down')}</span></span><input type="tel" inputmode="numeric" maxlength="13" placeholder="请输入手机号" value="138 0013 8000" autocomplete="off" aria-label="手机号"><button class="clr" type="button" aria-label="清除手机号"><span>${sv('closec')}</span></button></div><div class="msg" data-e="phone" aria-live="polite"></div>
<div class="fld" data-f="code"><input type="text" inputmode="numeric" maxlength="6" placeholder="请输入 6 位验证码" autocomplete="off" aria-label="验证码"><button class="get" type="button">获取验证码</button></div><div class="msg" data-e="code" aria-live="polite"></div>
<div class="agree"><span class="ck" role="checkbox" aria-checked="false"><span>${sv('check')}</span></span><span>已阅读并同意<a>《用户协议》</a>和<a>《隐私政策》</a></span></div><div class="msg ag" data-e="agree" aria-live="polite"></div>
<button class="go idle" type="button">登录</button></div>`,
  js: (root) => {
    const ph = q1(root, '[data-f=phone] input'), cd = q1(root, '[data-f=code] input'), get = q1(root, '.get'), go = q1(root, '.go'), ag = q1(root, '.agree'), ck = q1(root, '.ck'), clr = q1(root, '.clr')
    const mp = q1(root, '[data-e=phone]'), mc = q1(root, '[data-e=code]'), ma = q1(root, '[data-e=agree]')
    const digits = (v) => v.replace(/\D/g, '')
    const okPhone = () => /^1[3-9]\d{9}$/.test(digits(ph.value))
    const say = (el, t, k) => { el.textContent = t; el.className = 'msg' + (el === ma ? ' ag' : '') + (k ? ' ' + k : ''); const f = el.previousElementSibling; if (f.classList.contains('fld')) f.classList.toggle('bad', k === 'er') }
    const fmt = () => { const d = digits(ph.value).slice(0, 11); ph.value = d.length > 7 ? `${d.slice(0, 3)} ${d.slice(3, 7)} ${d.slice(7)}` : d.length > 3 ? `${d.slice(0, 3)} ${d.slice(3)}` : d; clr.hidden = !d }
    const sync = () => go.classList.toggle('idle', !(okPhone() && digits(cd.value).length === 6 && ck.classList.contains('on')))
    ph.addEventListener('input', () => { fmt(); say(mp, ''); sync() })
    clr.addEventListener('click', () => { ph.value = ''; fmt(); say(mp, ''); sync(); ph.focus() })
    cd.addEventListener('input', () => { cd.value = digits(cd.value); say(mc, ''); sync() })
    let left = 0
    get.addEventListener('click', () => {
      if (left > 0) return
      if (!okPhone()) { say(mp, '请输入正确的 11 位手机号', 'er'); ph.focus(); return }
      const d = digits(ph.value); left = 60; get.disabled = true; get.textContent = `${left}s 后重新获取`
      say(mc, `验证码已发送至 ${d.slice(0, 3)}****${d.slice(7)}，5 分钟内有效`, 'ok'); cd.focus()
      const id = setInterval(() => {
        if (!root.isConnected) { clearInterval(id); return }
        left--; if (left <= 0) { clearInterval(id); get.disabled = false; get.textContent = '重新获取' } else get.textContent = `${left}s 后重新获取`
      }, 1000)
    })
    ag.addEventListener('click', (e) => {
      if (e.target.closest('a')) { IX.toast(root, '查看协议全文'); return }
      const on = ck.classList.toggle('on'); ck.setAttribute('aria-checked', on); say(ma, ''); sync()
    })
    go.addEventListener('click', () => {
      if (go.classList.contains('busy') || go.classList.contains('done')) return /* 加载中、已成功：忽略重复点击 */
      if (!okPhone()) { say(mp, '请输入正确的 11 位手机号', 'er'); ph.focus(); return }
      if (digits(cd.value).length !== 6) { say(mc, '请输入 6 位验证码', 'er'); cd.focus(); return }
      if (!ck.classList.contains('on')) { say(ma, '请先阅读并同意用户协议和隐私政策', 'er'); ag.classList.remove('shake'); void ag.offsetWidth; ag.classList.add('shake'); return }
      go.classList.add('busy'); go.innerHTML = '<span class="sp"></span>登录中'
      later(root, 1100, () => {
        go.classList.remove('busy')
        if (digits(cd.value) === '000000') { go.textContent = '登录'; say(mc, '验证码不正确，请重新获取', 'er'); return }
        go.classList.add('done'); go.innerHTML = sv('check') + '登录成功'; IX.toast(root, '欢迎回来')
        later(root, 2200, () => { go.classList.remove('done'); go.textContent = '登录' })
      })
    })
    fmt()
  },
})

/* ───── 地区数据：省 → 市 → 区，示例用 ───── */
const REGION = {
  浙江省: { 杭州市: ['西湖区', '滨江区', '余杭区', '拱墅区'], 宁波市: ['海曙区', '鄞州区', '北仑区'] },
  江苏省: { 南京市: ['玄武区', '鼓楼区', '江宁区'], 苏州市: ['姑苏区', '吴中区', '工业园区'] },
  广东省: { 广州市: ['天河区', '越秀区', '海珠区'], 深圳市: ['南山区', '福田区', '宝安区'] },
  四川省: { 成都市: ['武侯区', '锦江区', '高新区'] },
}
def({
  id: 'MP-FORM-005', name: '地址表单与地区选择', style: '三级联动',
  fit: '收货地址、服务地址新增编辑；地区用底部弹层三级选择，保存时原位提示缺项',
  avoid: '只需要城市级定位的场景（用定位 + 城市列表）；地址字段超过 7 项时改分步填写',
  kw: 'address 地址 收货地址 省市区 三级联动 级联 默认地址 联系人',
  css: CSS('mpform005', `&{position:relative;width:340px;background:var(--card);border-radius:22px;padding:4px 20px 20px;box-shadow:${SHADOW};overflow:hidden}& .fr{display:flex;align-items:flex-start;gap:12px;width:100%;padding:14px 0;border-bottom:1px solid var(--line);text-align:left}& .fr:focus-within{border-bottom-color:var(--ink2)}& .lb{flex:none;width:68px;font-size:16px;line-height:24px;color:var(--ink)}& .fr.bad .lb{color:${DANGER}}& .vl{flex:1;min-width:0}& .vl input,& .vl textarea{display:block;width:100%;border:0;outline:0;background:none;padding:0;font:inherit;font-size:16px;line-height:24px;color:var(--ink);resize:none}& .vl textarea{height:48px}& .vl input::placeholder,& .vl textarea::placeholder{color:color-mix(in srgb,var(--ink4) 52%,var(--ink3))}& .em{display:block;margin-top:4px;font-size:12px;line-height:16px;color:${DANGER}}& .em:empty{display:none}& .rg .vl{display:block}& .rg .v{display:block;font-size:16px;line-height:24px;color:color-mix(in srgb,var(--ink4) 52%,var(--ink3))}& .rg .v.has{color:var(--ink)}& .rg .ch{display:inline-flex;flex:none;width:16px;height:16px;margin-top:4px;color:var(--ink3)}& .tags{display:flex;gap:8px}& .tags button{height:36px;padding:0 18px;border-radius:18px;background:var(--soft);font-size:14px;color:var(--ink2);transition:background-color .15s}${HIT('& .tags button', 2, 4)}& .tags .on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1.5px var(--p)}& .fr.swr{align-items:center;border-bottom:0;padding-bottom:6px}& .fr.swr .lb{flex:1;width:auto}& .swt{position:relative;flex:none;width:48px;height:28px;border-radius:14px;background:var(--n8);transition:background-color .2s}& .swt::before{content:"";position:absolute;left:3px;top:3px;width:22px;height:22px;border-radius:50%;background:var(--card);box-shadow:0 2px 6px rgba(0,0,0,.2);transition:transform .2s cubic-bezier(.2,0,0,1)}& .swt::after{content:"";position:absolute;inset:-8px -2px}& .swt.on{background:var(--p)}& .swt.on::before{transform:translateX(20px)}& .go{width:100%;height:48px;margin-top:14px;border-radius:24px;display:flex;align-items:center;justify-content:center;gap:8px;font-size:16px;font-weight:600;${PRIMARY}}& .go.busy{cursor:progress}& .ix-mask{background:color-mix(in srgb,var(--scrim) 40%,transparent)}& .sheet{position:relative;align-self:flex-end;width:100%;background:var(--card2);border-radius:22px 22px 0 0;box-shadow:0 -10px 40px var(--sh16)}& .ix-ov.show .sheet{animation:@@up .26s cubic-bezier(.2,0,0,1)}@keyframes @@up{from{transform:translateY(40px);opacity:0}}& .sh{display:flex;align-items:center;justify-content:space-between;height:52px;padding:0 6px 0 20px}& .sh b{font-size:16px;font-weight:600}& .sh button{width:44px;height:44px;display:flex;align-items:center;justify-content:center;color:var(--ink2)}& .sh button span{display:inline-flex;width:18px;height:18px}& .rtabs{display:flex;gap:22px;padding:0 20px;border-bottom:1px solid var(--line)}& .rtabs button{position:relative;height:44px;max-width:96px;font-size:14px;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}& .rtabs button.on{color:var(--ink);font-weight:600}& .rtabs button.on::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:3px;border-radius:2px;background:var(--p)}& .rl{height:188px;overflow-y:auto;padding:4px 20px 12px}& .rl button{display:flex;align-items:center;justify-content:space-between;width:100%;height:44px;font-size:16px;color:var(--ink);text-align:left}& .rl button.on{color:var(--p-text);font-weight:600}& .rl button span{display:inline-flex;width:18px;height:18px;color:var(--p-fg)}`),
  html: () => `<div class="mpform005">
<div class="fr" data-k="name"><span class="lb">收货人</span><div class="vl"><input type="text" value="林小满" placeholder="请填写收货人姓名" aria-label="收货人"><span class="em"></span></div></div>
<div class="fr" data-k="tel"><span class="lb">手机号</span><div class="vl"><input type="tel" inputmode="numeric" maxlength="11" value="13800138000" placeholder="请填写 11 位手机号" aria-label="手机号"><span class="em"></span></div></div>
<button class="fr rg" type="button" data-open="rg" data-k="area"><span class="lb">所在地区</span><span class="vl"><span class="v">请选择省 / 市 / 区</span><span class="em"></span></span><span class="ch">${sv('right')}</span></button>
<div class="fr" data-k="addr"><span class="lb">详细地址</span><div class="vl"><textarea placeholder="街道、楼栋、门牌号" aria-label="详细地址"></textarea><span class="em"></span></div></div>
<div class="fr"><span class="lb">标签</span><div class="tags"><button class="on" type="button">家</button><button type="button">公司</button><button type="button">学校</button></div></div>
<div class="fr swr"><span class="lb">设为默认地址</span><span class="swt" data-ix="toggle" role="switch" aria-checked="false" aria-label="设为默认地址"></span></div>
<button class="go" type="button">保存地址</button>
<div class="ix-ov" data-ov="rg"><div class="ix-mask"></div><div class="sheet"><div class="sh"><b>选择所在地区</b><button type="button" data-close aria-label="关闭"><span>${sv('close')}</span></button></div><div class="rtabs"></div><div class="rl"></div></div></div></div>`,
  js: (root) => {
    let lv = 0, path = []
    const ov = q1(root, '[data-ov=rg]'), tabs = q1(root, '.rtabs'), list = q1(root, '.rl'), val = q1(root, '.rg .v'), go = q1(root, '.go')
    const items = () => (lv === 0 ? Object.keys(REGION) : lv === 1 ? Object.keys(REGION[path[0]]) : REGION[path[0]][path[1]])
    const draw = () => {
      tabs.innerHTML = [0, 1, 2].filter((i) => i <= path.length && i <= 2).map((i) => `<button type="button" data-lv="${i}" class="${i === lv ? 'on' : ''}">${path[i] || '请选择'}</button>`).join('')
      list.innerHTML = items().map((n) => `<button type="button" data-n="${n}" class="${n === path[lv] ? 'on' : ''}">${n}${n === path[lv] ? `<span>${sv('check')}</span>` : ''}</button>`).join('')
      list.scrollTop = 0
    }
    const mark = (k, msg) => { const r = q1(root, `[data-k=${k}]`); r.classList.toggle('bad', !!msg); const e = q1(r, '.em'); if (e) e.textContent = msg || '' }
    q1(root, '.rg').addEventListener('click', () => { lv = path.length ? 2 : 0; draw() })
    tabs.addEventListener('click', (e) => { const b = e.target.closest('[data-lv]'); if (!b) return; lv = +b.dataset.lv; path.length = lv; draw() })
    list.addEventListener('click', (e) => {
      const b = e.target.closest('[data-n]'); if (!b) return
      path[lv] = b.dataset.n; path.length = lv + 1
      if (lv < 2) { lv++; draw(); return }
      val.textContent = path.join(' '); val.classList.add('has'); mark('area', ''); ov.classList.remove('show')
    })
    qa(root, '.tags button').forEach((b) => b.addEventListener('click', () => qa(root, '.tags button').forEach((x) => x.classList.toggle('on', x === b))))
    qa(root, '.vl input, .vl textarea').forEach((i) => i.addEventListener('input', () => mark(i.closest('.fr').dataset.k, '')))
    go.addEventListener('click', () => {
      if (go.classList.contains('busy')) return
      const name = q1(root, '[data-k=name] input').value.trim(), tel = q1(root, '[data-k=tel] input').value.trim(), addr = q1(root, '[data-k=addr] textarea').value.trim()
      const bad = []
      if (!name) bad.push(['name', '请填写收货人姓名']); else mark('name', '')
      if (!/^1[3-9]\d{9}$/.test(tel)) bad.push(['tel', '请填写正确的 11 位手机号']); else mark('tel', '')
      if (!path.length || path.length < 3) bad.push(['area', '请选择所在地区']); else mark('area', '')
      if (addr.length < 5) bad.push(['addr', '地址太短，请补充楼栋和门牌号']); else mark('addr', '')
      bad.forEach(([k, m]) => mark(k, m))
      if (bad.length) { const f = q1(root, `[data-k=${bad[0][0]}] input, [data-k=${bad[0][0]}] textarea`); if (f) f.focus(); return }
      go.classList.add('busy'); go.textContent = '保存中…'
      later(root, 900, () => { go.classList.remove('busy'); go.textContent = '保存地址'; IX.toast(root, '地址已保存') })
    })
  },
})

def({
  id: 'MP-FORM-006', name: '滚轮日期时间选择', style: '三列滚轮',
  fit: '预约时间、配送时间、生日；可以上下滑动或点选，中间高亮条是当前选择',
  avoid: '选项超过 60 个的列（改搜索或分段）；需要一眼看到整月的场景（改日历）',
  kw: 'picker 滚轮 日期 时间选择器 预约时间 送达时间 datetime 滚动选择',
  css: CSS('mpform006', `&{width:340px;background:var(--card);border-radius:22px;box-shadow:${SHADOW};overflow:hidden}& .hd{display:flex;align-items:center;justify-content:space-between;height:52px;padding:0 6px;border-bottom:1px solid var(--line)}& .hd button{min-width:64px;height:44px;font-size:16px;color:var(--ink2)}& .hd button.ok{color:var(--p-text);font-weight:600}& .hd b{font-size:16px;font-weight:600}& .sum{display:flex;align-items:baseline;justify-content:center;gap:8px;padding:14px 0 2px}& .sum span{font-size:22px;line-height:30px;font-weight:700;font-variant-numeric:tabular-nums}& .cap,& .wheels{display:grid;grid-template-columns:1.8fr 1fr 1fr;padding:0 16px}& .cap{padding-top:6px;font-size:12px;line-height:16px;color:var(--ink3);text-align:center}& .wheels{position:relative;height:220px;margin-bottom:10px}& .band{position:absolute;left:16px;right:16px;top:88px;height:44px;border-radius:12px;background:var(--pt);pointer-events:none}& .wh{position:relative;height:220px;overflow-y:auto;padding:88px 0;scroll-snap-type:y mandatory;scrollbar-width:none;overscroll-behavior:contain;cursor:grab;outline:none;border-radius:12px}& .wh:focus-visible{box-shadow:inset 0 0 0 1px var(--ink2)}& .wh::-webkit-scrollbar{display:none}& .wh.drag{scroll-snap-type:none;cursor:grabbing;user-select:none}& .it{height:44px;display:flex;align-items:center;justify-content:center;scroll-snap-align:center;font-size:16px;color:var(--ink);font-variant-numeric:tabular-nums;white-space:nowrap}& .it.sel{font-weight:600;color:var(--p-text)}& .fade{position:absolute;left:16px;right:16px;height:84px;pointer-events:none}& .fade.t{top:0;background:linear-gradient(var(--card) 12%,transparent)}& .fade.b{bottom:0;background:linear-gradient(transparent,var(--card) 88%)}`),
  html: () => `<div class="mpform006"><div class="hd"><button type="button" data-a="cancel">取消</button><b>选择送达时间</b><button class="ok" type="button" data-a="ok">确定</button></div>
<div class="sum"><span data-sum>—</span></div><div class="cap"><span>日期</span><span>时</span><span>分</span></div>
<div class="wheels"><div class="band"></div><div class="wh" data-col="0" tabindex="0" aria-label="日期"></div><div class="wh" data-col="1" tabindex="0" aria-label="小时"></div><div class="wh" data-col="2" tabindex="0" aria-label="分钟"></div><i class="fade t"></i><i class="fade b"></i></div></div>`,
  js: (root) => {
    const H = 44, base = new Date(2026, 10, 4), wk = ['日', '一', '二', '三', '四', '五', '六']
    const dates = Array.from({ length: 7 }, (_, i) => { const d = new Date(base); d.setDate(base.getDate() + i); return { t: i === 0 ? '今天' : i === 1 ? '明天' : `${d.getMonth() + 1}月${d.getDate()}日 周${wk[d.getDay()]}`, s: `${d.getMonth() + 1}月${d.getDate()}日 周${wk[d.getDay()]}` } })
    const hours = Array.from({ length: 13 }, (_, i) => String(9 + i).padStart(2, '0'))
    const mins = ['00', '15', '30', '45']
    const data = [dates.map((d) => d.t), hours, mins], init = [2, 5, 2]
    const cols = qa(root, '.wh'), sum = q1(root, '[data-sum]')
    cols.forEach((wh, c) => { wh.innerHTML = data[c].map((t, i) => `<div class="it" data-i="${i}">${t}</div>`).join('') })
    const cur = (wh) => clamp(Math.round(wh.scrollTop / H), 0, data[+wh.dataset.col].length - 1)
    const paint = (wh) => { const f = wh.scrollTop / H; qa(wh, '.it').forEach((it, i) => { const d = Math.abs(i - f); it.style.opacity = Math.max(0.22, 1 - d * 0.36); it.classList.toggle('sel', d < 0.5) }) }
    const text = () => `${dates[cur(cols[0])].s} ${hours[cur(cols[1])]}:${mins[cur(cols[2])]}`
    const upd = () => { sum.textContent = text() }
    cols.forEach((wh, c) => {
      wh.scrollTop = init[c] * H; paint(wh)
      let raf = 0; wh.addEventListener('scroll', () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => { paint(wh); upd() }) })
      /* 鼠标拖动：触屏本来就能滑，鼠标要自己接管 */
      let d = null
      wh.addEventListener('pointerdown', (e) => { if (e.pointerType === 'mouse') d = { y: e.clientY, t: wh.scrollTop, m: false, id: e.pointerId } })
      wh.addEventListener('pointermove', (e) => { if (!d) return; const dy = e.clientY - d.y; if (!d.m && Math.abs(dy) > 3) { d.m = true; wh.classList.add('drag'); wh.setPointerCapture(d.id) } if (d.m) wh.scrollTop = d.t - dy })
      const end = () => { if (!d) return; const m = d.m; d = null; if (m) { wh.__m = true; setTimeout(() => (wh.__m = false), 0); wh.scrollTo({ top: cur(wh) * H, behavior: 'smooth' }); wh.classList.remove('drag') } }
      wh.addEventListener('pointerup', end); wh.addEventListener('pointercancel', end)
      wh.addEventListener('click', (e) => { if (wh.__m) return; const it = e.target.closest('.it'); if (it) wh.scrollTo({ top: +it.dataset.i * H, behavior: 'smooth' }) })
      wh.addEventListener('keydown', (e) => { const k = e.key === 'ArrowDown' ? 1 : e.key === 'ArrowUp' ? -1 : 0; if (k) { e.preventDefault(); wh.scrollTo({ top: clamp(cur(wh) + k, 0, data[c].length - 1) * H, behavior: 'smooth' }) } })
    })
    upd()
    q1(root, '[data-a=ok]').addEventListener('click', () => IX.toast(root, `已选择 ${text()}`))
    q1(root, '[data-a=cancel]').addEventListener('click', () => { cols.forEach((wh, c) => wh.scrollTo({ top: init[c] * H, behavior: 'smooth' })); IX.toast(root, '已恢复默认时间') })
  },
})
/* 开关：外壳 .swt + 里面一个旋钮 <i>；加载时旋钮里转圈 */
const SWT = (p) => `& .swt{position:relative;flex:none;width:48px;height:28px;border-radius:14px;background:var(--n8);cursor:pointer;transition:background-color .2s}& .swt::after{content:"";position:absolute;inset:-8px -2px}& .swt i{position:absolute;left:3px;top:3px;width:22px;height:22px;border-radius:50%;background:var(--card);box-shadow:0 2px 6px rgba(0,0,0,.2);transition:transform .2s cubic-bezier(.2,0,0,1)}& .swt.on{background:var(--p)}& .swt.on i{transform:translateX(20px)}& .swt.busy{cursor:progress}& .swt.busy i::before{content:"";position:absolute;inset:4px;border-radius:50%;border:2px solid rgba(var(--p-rgb),.25);border-top-color:var(--p);animation:${p}s .8s linear infinite}@keyframes ${p}s{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){& .swt.busy i::before{animation:none}}`

def({
  id: 'MP-FORM-007', name: '评价输入框', style: '星级计数',
  fit: '订单评价、服务评价、意见反馈；星级、印象标签、文字、匿名一次填完',
  avoid: '只收集星级的轻评价（直接用评分）；文字必填但没写明最少字数的场景',
  kw: '评价 评论 星级 字数计数 textarea 反馈 印象标签 匿名 review',
  css: CSS('mpform007', `&{width:340px;background:var(--card);border-radius:22px;padding:18px 18px 20px;box-shadow:${SHADOW}}& .pr{display:flex;align-items:center;gap:12px}& .pr img{width:52px;height:52px;border-radius:12px;object-fit:cover;flex:none}& .pr b{display:block;font-size:16px;line-height:22px;font-weight:600}& .pr span{font-size:12px;line-height:16px;color:var(--ink3)}& .rate{display:flex;align-items:center;gap:10px;margin:14px 0 4px}& .str{display:flex}& .str button{width:44px;height:44px;display:flex;align-items:center;justify-content:center;color:var(--ink7);transition:color .15s,transform .15s cubic-bezier(.2,0,0,1)}& .str button span{display:inline-flex;width:30px;height:30px}& .str button.on{color:#DDA43D}& .str button.on span svg{fill:currentColor}& .str button:active{transform:scale(.9)}& .rlab{font-size:14px;color:var(--ink3)}& .rlab.set{color:var(--p-text);font-weight:600}& .tags{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 12px}& .tags button{position:relative;height:32px;padding:0 12px;border-radius:16px;background:var(--soft);font-size:14px;color:var(--ink2)}& .tags button::after{content:"";position:absolute;inset:-6px -2px}& .tags .on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1.5px var(--p)}& .ta{position:relative;border:1px solid var(--n7);border-radius:12px;padding:12px 12px 30px;transition:border-color .15s}& .ta:focus-within{border-color:var(--ink2)}& .ta textarea{display:block;width:100%;height:92px;border:0;outline:0;background:none;padding:0;resize:none;font:inherit;font-size:14px;line-height:22px;color:var(--ink)}& .ta textarea::placeholder{color:color-mix(in srgb,var(--ink4) 52%,var(--ink3))}& .cnt{position:absolute;right:12px;bottom:8px;font-size:12px;line-height:16px;color:var(--ink3);font-variant-numeric:tabular-nums}& .cnt.warn{color:${WARN}}& .cnt.full{color:${DANGER};font-weight:600}& .tip{min-height:20px;margin:6px 2px 0;font-size:12px;line-height:16px;color:var(--ink3)}& .tip.er{color:${DANGER}}& .anon{display:flex;align-items:center;justify-content:space-between;margin:4px 0 14px;font-size:14px;color:var(--ink)}& .anon small{display:block;font-size:12px;color:var(--ink3)}${SWT('mpform007')}& .go{width:100%;height:48px;border-radius:24px;font-size:16px;font-weight:600;${PRIMARY};display:flex;align-items:center;justify-content:center;gap:8px;transition:opacity .2s}& .go.idle{opacity:.5;box-shadow:none}& .go.busy{cursor:progress}${SPIN('mpform007b', '& .sp', 18)}`),
  html: () => `<div class="mpform007"><div class="pr"><img src="${P(0)}" alt=""><div><b>无线降噪耳机</b><span>石墨灰 · 主动降噪</span></div></div>
<div class="rate"><div class="str" role="radiogroup" aria-label="评分">${[1, 2, 3, 4, 5].map((n) => `<button type="button" role="radio" aria-checked="false" aria-label="${n} 星" data-n="${n}"><span>${sv('star')}</span></button>`).join('')}</div><span class="rlab">点星星打分</span></div>
<div class="tags">${['质量好', '音质出色', '佩戴舒适', '续航长', '包装精美'].map((t) => `<button type="button">${t}</button>`).join('')}</div>
<div class="ta"><textarea maxlength="200" placeholder="分享你的使用感受，对其他买家很有帮助" aria-label="评价内容"></textarea><span class="cnt">0/200</span></div><div class="tip" aria-live="polite"></div>
<div class="anon"><div>匿名评价<small>其他人只能看到“匿名用户”</small></div><span class="swt" data-ix="toggle" role="switch" aria-checked="false" aria-label="匿名评价"><i></i></span></div>
<button class="go idle" type="button">发布评价</button></div>`,
  js: (root) => {
    const L = ['', '非常差', '较差', '一般', '满意', '非常满意']
    const stars = qa(root, '.str button'), ta = q1(root, 'textarea'), cnt = q1(root, '.cnt'), lab = q1(root, '.rlab'), go = q1(root, '.go'), tip = q1(root, '.tip')
    let score = 0
    const sync = () => go.classList.toggle('idle', !(score > 0 && ta.value.trim().length >= 5))
    const paint = () => { stars.forEach((b, i) => { b.classList.toggle('on', i < score); b.setAttribute('aria-checked', i + 1 === score) }); lab.textContent = score ? L[score] : '点星星打分'; lab.classList.toggle('set', !!score) }
    stars.forEach((b, i) => b.addEventListener('click', () => { score = i + 1; paint(); tip.textContent = ''; tip.className = 'tip'; sync() }))
    qa(root, '.tags button').forEach((b) => b.addEventListener('click', () => b.classList.toggle('on')))
    ta.addEventListener('input', () => {
      const n = ta.value.length; cnt.textContent = `${n}/200`
      cnt.className = 'cnt' + (n >= 200 ? ' full' : n >= 180 ? ' warn' : '')
      tip.textContent = n >= 200 ? '已达 200 字上限' : ''; tip.className = 'tip' + (n >= 200 ? ' er' : ''); sync()
    })
    go.addEventListener('click', () => {
      if (go.classList.contains('busy')) return
      if (!score) { tip.textContent = '先给商品打个分吧'; tip.className = 'tip er'; return }
      if (ta.value.trim().length < 5) { tip.textContent = '再多写几个字吧，至少 5 个字'; tip.className = 'tip er'; ta.focus(); return }
      go.classList.add('busy'); go.innerHTML = '<span class="sp"></span>发布中'
      later(root, 1000, () => { go.classList.remove('busy'); go.textContent = '发布评价'; IX.toast(root, '评价已发布，获得 10 积分') })
    })
  },
})

def({
  id: 'MP-FORM-008', name: '图片上传九宫格', style: '进度与重试',
  fit: '评价晒图、售后凭证、发布内容；三列九宫格，上传进度、失败重试、删除、首张当封面',
  avoid: '只要一张头像或证件照（用单图上传）；图片超过 9 张的场景（改相册选择页）',
  kw: 'upload 上传 图片 九宫格 晒图 售后凭证 删除 进度 重试',
  css: CSS('mpform008', `&{width:340px;background:var(--card);border-radius:22px;padding:18px 20px 16px;box-shadow:${SHADOW}}& .hd{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:12px}& .hd b{font-size:16px;font-weight:600}& .hd span{font-size:14px;color:var(--ink3);font-variant-numeric:tabular-nums}& .gd{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}& .t{position:relative;aspect-ratio:1;border-radius:12px;overflow:hidden;background:var(--soft)}& .t img{width:100%;height:100%;object-fit:cover}& .x{position:absolute;right:4px;top:4px;width:22px;height:22px;border-radius:50%;background:color-mix(in srgb,var(--scrim) 66%,transparent);color:#fff;display:flex;align-items:center;justify-content:center}& .x::after{content:"";position:absolute;inset:-11px}& .x span{display:inline-flex;width:12px;height:12px}& .cv{position:absolute;left:0;right:0;bottom:0;height:22px;background:var(--mask2);color:#fff;font-size:12px;line-height:22px;text-align:center}& .ov{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;background:color-mix(in srgb,var(--scrim) 55%,transparent);color:#fff;font-size:12px;line-height:16px}& .ov b{font-size:14px;font-weight:600;font-variant-numeric:tabular-nums}& .ov span{display:inline-flex;width:22px;height:22px}& .pgb{position:absolute;left:10px;right:10px;bottom:10px;height:4px;border-radius:2px;background:color-mix(in srgb,var(--card) 35%,transparent)}& .pgb i{display:block;height:100%;border-radius:2px;background:var(--card);transition:width .12s linear}& .t.bad{cursor:pointer}& .adt{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;aspect-ratio:1;border-radius:12px;border:1.5px dashed var(--n9);background:var(--n1);color:var(--ink2);font-size:12px;line-height:16px;transition:border-color .15s,background-color .15s}& .adt:hover{border-color:var(--p);background:var(--pt)}& .adt span{display:inline-flex;width:28px;height:28px;color:var(--ink2)}& .note{min-height:18px;margin:12px 0 0;font-size:12px;line-height:18px;color:var(--ink3)}& .note.er{color:${DANGER}}`),
  html: () => `<div class="mpform008"><div class="hd"><b>上传图片</b><span data-n>3/9</span></div><div class="gd"></div><p class="note" aria-live="polite"></p></div>`,
  js: (root) => {
    const MAX = 9, gd = q1(root, '.gd'), note = q1(root, '.note'), cntEl = q1(root, '[data-n]')
    let uid = 0, next = 2
    const tiles = [{ id: uid++, img: 0, st: 'ok', p: 100 }, { id: uid++, img: 1, st: 'ok', p: 100 }, { id: uid++, img: 5, st: 'ok', p: 100 }, { id: uid++, img: 3, st: 'err', p: 40 }]
    const tick = {}
    const draw = () => {
      const firstOk = tiles.findIndex((t) => t.st === 'ok')
      gd.innerHTML = tiles.map((t, i) => `<div class="t ${t.st === 'err' ? 'bad' : ''}" data-id="${t.id}"><img src="${P(t.img)}" alt="图片 ${i + 1}">${t.st === 'ok' && i === firstOk ? '<span class="cv">封面</span>' : ''}${t.st === 'up' ? `<div class="ov"><b data-p>${t.p}%</b>上传中<div class="pgb"><i style="width:${t.p}%"></i></div></div>` : ''}${t.st === 'err' ? `<div class="ov"><span>${sv('refresh')}</span>上传失败<br>点击重试</div>` : ''}<button class="x" type="button" data-x aria-label="删除图片 ${i + 1}"><span>${sv('close')}</span></button></div>`).join('') + (tiles.length < MAX ? `<button class="adt" type="button" data-add aria-label="添加图片"><span>${sv('plus')}</span>添加图片</button>` : '')
      const err = tiles.filter((t) => t.st === 'err').length, up = tiles.filter((t) => t.st === 'up').length
      cntEl.textContent = `${tiles.length}/${MAX}`
      note.className = 'note' + (err ? ' er' : '')
      note.textContent = err ? `${err} 张上传失败，点击图片重试` : up ? '正在上传，请稍候…' : tiles.length >= MAX ? '已达 9 张上限，删除后可继续添加' : '首张图片将作为封面，最多 9 张'
    }
    const start = (t) => {
      t.st = 'up'; t.p = t.p >= 100 || t.p < 0 ? 0 : t.p
      clearInterval(tick[t.id])
      tick[t.id] = setInterval(() => {
        if (!root.isConnected) { clearInterval(tick[t.id]); return }
        t.p = Math.min(100, t.p + 10 + Math.floor(Math.random() * 10))
        const el = q1(gd, `[data-id="${t.id}"]`)
        if (t.p >= 100) { clearInterval(tick[t.id]); t.st = 'ok'; draw() } else if (el) { q1(el, '[data-p]').textContent = t.p + '%'; q1(el, '.pgb i').style.width = t.p + '%' }
      }, 140)
      draw()
    }
    gd.addEventListener('click', (e) => {
      const x = e.target.closest('[data-x]'), add = e.target.closest('[data-add]'), bad = e.target.closest('.t.bad')
      if (x) { const id = +x.closest('.t').dataset.id; clearInterval(tick[id]); tiles.splice(tiles.findIndex((t) => t.id === id), 1); draw(); return }
      if (add) { if (tiles.length >= MAX) return; const t = { id: uid++, img: next++ % 9, st: 'up', p: 0 }; tiles.push(t); start(t); return }
      if (bad) { const t = tiles.find((q) => q.id === +bad.dataset.id); t.p = 0; start(t) }
    })
    draw()
  },
})

def({
  id: 'MP-FORM-009', name: '单选卡与复选卡', style: '描边选中',
  fit: '配送方式、增值服务、套餐规格；选项带说明和价格，选中后合计实时变化',
  avoid: '选项只有“是 / 否”（用开关）；选项文字很长或超过 6 个（改列表页）',
  kw: 'radio checkbox 单选 复选 多选 配送方式 增值服务 套餐 选项卡',
  css: CSS('mpform009', `&{width:340px;background:var(--card);border-radius:22px;padding:18px 18px 16px;box-shadow:${SHADOW}}& h5{margin:0 0 10px;font-size:14px;line-height:20px;font-weight:600;color:var(--ink2)}& h5 small{font-weight:400;color:var(--ink3);margin-left:6px}& .rcs{display:flex;flex-direction:column;gap:10px;margin-bottom:18px}& .rc{display:flex;align-items:center;gap:12px;width:100%;min-height:64px;padding:10px 14px;border-radius:14px;background:var(--card);box-shadow:inset 0 0 0 1px var(--n6);text-align:left;transition:box-shadow .15s,background-color .15s}& .rc.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p)}& .ib{display:flex;align-items:center;justify-content:center;flex:none;width:40px;height:40px;border-radius:12px;background:var(--pt);color:var(--p-text)}& .rc.on .ib{background:var(--lift)}& .ib span{display:inline-flex;width:22px;height:22px}& .tx{flex:1;min-width:0}& .tx b{display:block;font-size:16px;line-height:22px;font-weight:600}& .tx small{display:block;font-size:12px;line-height:16px;color:var(--ink3)}& .pc{flex:none;font-size:14px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}& .rd{position:relative;flex:none;width:20px;height:20px;border-radius:50%;border:1.5px solid var(--n10);display:flex;align-items:center;justify-content:center;color:transparent;transition:background-color .15s,border-color .15s}& .rd span{display:inline-flex;width:12px;height:12px}& .on>.rd{background:var(--p);border-color:var(--p);color:#fff}& .ccs{display:grid;grid-template-columns:1fr 1fr;gap:10px}& .ckc{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:2px;min-height:76px;padding:12px 14px;border-radius:14px;background:var(--card);box-shadow:inset 0 0 0 1px var(--n6);text-align:left;transition:box-shadow .15s,background-color .15s}& .ckc.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p)}& .ckc .ib{width:32px;height:32px;border-radius:10px;margin-bottom:4px}& .ckc .ib span{width:18px;height:18px}& .ckc b{font-size:14px;line-height:20px;font-weight:600}& .ckc small{font-size:12px;line-height:16px;color:var(--ink3)}& .bx{position:absolute;right:10px;top:10px;width:20px;height:20px;border-radius:6px;border:1.5px solid var(--n10);display:flex;align-items:center;justify-content:center;color:transparent;transition:background-color .15s,border-color .15s}& .bx span{display:inline-flex;width:12px;height:12px}& .ckc.on .bx{background:var(--p);border-color:var(--p);color:#fff}& .sum{display:flex;align-items:center;justify-content:space-between;margin-top:16px;padding-top:14px;border-top:1px solid var(--line);font-size:14px;color:var(--ink2)}& .sum b{margin-left:6px;font-size:22px;line-height:28px;font-weight:700;color:var(--price);font-variant-numeric:tabular-nums}`),
  html: () => {
    const rc = (on, ic, t, s, pv, p) => `<button class="rc ${on ? 'on' : ''}" type="button" role="radio" aria-checked="${!!on}" data-v="${pv}"><span class="ib">${sv(ic)}</span><span class="tx"><b>${t}</b><small>${s}</small></span><span class="pc">${p}</span><span class="rd"><span>${sv('check')}</span></span></button>`
    const ck = (on, ic, t, s, pv) => `<button class="ckc ${on ? 'on' : ''}" type="button" role="checkbox" aria-checked="${!!on}" data-v="${pv}"><span class="ib">${sv(ic)}</span><b>${t}</b><small>${s}</small><span class="bx"><span>${sv('check')}</span></span></button>`
    return `<div class="mpform009"><h5>配送方式</h5><div class="rcs" role="radiogroup">${rc(0, 'truck', '标准配送', '预计 11-06 送达', 0, '免运费')}${rc(1, 'clock', '次日达', '今天 18:00 前下单，明天送达', 6, '¥6')}${rc(0, 'pin', '到店自提', '2 小时后到店可取', 0, '免费')}</div>
<h5>增值服务<small>可多选</small></h5><div class="ccs">${ck(1, 'giftbox', '礼盒包装', '+ ¥8', 8)}${ck(0, 'edit', '手写贺卡', '免费', 0)}${ck(0, 'shield', '运输保价', '+ ¥2', 2)}${ck(0, 'receipt', '电子发票', '免费', 0)}</div>
<div class="sum"><span>配送 ¥<span data-ship>6</span> · 服务 ¥<span data-svc>8</span></span><span>应付附加<b>¥<span data-tot>14</span></b></span></div></div>`
  },
  js: (root) => {
    const rcs = qa(root, '.rc'), cks = qa(root, '.ckc')
    const upd = () => {
      const ship = +(rcs.find((r) => r.classList.contains('on')) || { dataset: { v: 0 } }).dataset.v, svc = cks.filter((c) => c.classList.contains('on')).reduce((a, c) => a + +c.dataset.v, 0)
      q1(root, '[data-ship]').textContent = ship; q1(root, '[data-svc]').textContent = svc; q1(root, '[data-tot]').textContent = ship + svc
    }
    rcs.forEach((r) => r.addEventListener('click', () => { rcs.forEach((x) => { x.classList.toggle('on', x === r); x.setAttribute('aria-checked', x === r) }); upd() }))
    cks.forEach((c) => c.addEventListener('click', () => { const on = c.classList.toggle('on'); c.setAttribute('aria-checked', on); upd() }))
    upd()
  },
})

def({
  id: 'MP-FORM-010', name: '带说明的开关列表', style: '失败回滚',
  fit: '消息通知、隐私与权限设置；每项有图标、标题和一句后果说明，开关点了立刻生效',
  avoid: '关闭会带来严重后果的项（改二次确认）；超过 8 项（按主题分组）',
  kw: 'switch 开关 设置 通知 隐私 权限 定位 免打扰 回滚',
  css: CSS('mpform010', `&{width:340px;background:var(--card);border-radius:22px;padding:4px 18px;box-shadow:${SHADOW}}& .row{display:flex;align-items:center;gap:12px;padding:14px 0;border-bottom:1px solid var(--line)}& .row:last-child{border-bottom:0}& .ic{display:flex;align-items:center;justify-content:center;flex:none;width:36px;height:36px;border-radius:10px;background:var(--pt);color:var(--p-text)}& .ic span{display:inline-flex;width:20px;height:20px}& .tx{flex:1;min-width:0}& .tx b{display:block;font-size:16px;line-height:22px;font-weight:600}& .tx small{display:block;font-size:12px;line-height:16px;color:var(--ink3)}& .why{display:none;margin-top:4px;font-size:12px;line-height:16px;color:${DANGER}}& .why.show{display:block}${SWT('mpform010')}`),
  html: () => {
    const r = (k, ic, t, s, on) => `<div class="row" data-k="${k}"><span class="ic"><span>${sv(ic)}</span></span><div class="tx"><b>${t}</b><small>${s}</small><span class="why" role="alert"></span></div><span class="swt ${on ? 'on' : ''}" role="switch" aria-checked="${!!on}" aria-label="${t}"><i></i></span></div>`
    return `<div class="mpform010">${r('order', 'receipt', '订单状态通知', '发货、签收、售后进度第一时间提醒', 1)}${r('promo', 'tag', '优惠活动提醒', '优惠券到期、会员日活动提前通知', 1)}${r('rec', 'heart', '个性化推荐', '根据浏览偏好推荐商品，关闭后展示通用推荐', 0)}${r('loc', 'pin', '附近门店定位', '用于推荐离你最近的门店和自提点', 0)}${r('dnd', 'moon', '夜间免打扰', '22:00 至次日 08:00 不推送消息', 1)}</div>`
  },
  js: (root) => {
    let granted = false
    root.addEventListener('click', (e) => {
      const sw = e.target.closest('.swt'); if (!sw || sw.classList.contains('busy')) return
      const row = sw.closest('.row'), k = row.dataset.k, why = q1(row, '.why'), name = q1(row, 'b').textContent
      const to = !sw.classList.contains('on'); why.classList.remove('show')
      sw.classList.toggle('on', to); sw.setAttribute('aria-checked', to); sw.classList.add('busy')
      later(root, 650, () => {
        sw.classList.remove('busy')
        if (k === 'loc' && to && !granted) { /* 失败：回滚并在原位写原因 */
          sw.classList.remove('on'); sw.setAttribute('aria-checked', false)
          why.textContent = '未获得定位权限，请在手机设置里允许小程序使用位置信息后重试'; why.classList.add('show'); granted = true
          later(root, 5000, () => why.classList.remove('show')); return
        }
        IX.toast(root, `${to ? '已开启' : '已关闭'}${name}`)
      })
    })
  },
})
/* ───────── FB 弹层与反馈 ───────── */
/* 迷你页面外框：弹层、提示都放在一个模拟的手机页面里，弹层只盖住这一页 */
const SCR = (h) => `&{position:relative;width:340px;height:${h}px;border-radius:22px;overflow:hidden;background:var(--bg);box-shadow:0 12px 30px var(--sh14)}& .nb{position:relative;z-index:1;display:flex;align-items:center;justify-content:center;height:48px;background:var(--card);font-size:16px;font-weight:600;box-shadow:0 1px 0 var(--line)}`

def({
  id: 'MP-FB-004', name: '底部操作菜单', style: '底部菜单',
  fit: '更多操作、分享、删除这类“选一个动作”的场景；危险项标红并二次确认，底部独立的取消键',
  avoid: '选项超过 6 个（改半屏弹层）；只有“确认 / 取消”两个选择（用对话框）',
  kw: 'action sheet 操作菜单 底部菜单 更多操作 分享 删除 取消 危险操作',
  stage: 'white',
  css: CSS('mpfb004', `${SCR(440)}& .pg{padding:12px}& .oc{background:var(--card);border-radius:16px;padding:14px;box-shadow:0 4px 14px var(--sh06)}& .oc .hd{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;font-size:12px;line-height:16px;color:var(--ink3)}& .oc .hd b{font-size:14px;font-weight:600;color:var(--p-text)}& .oc .it{display:flex;gap:12px}& .oc img{width:64px;height:64px;border-radius:12px;object-fit:cover;flex:none}& .oc h4{margin:0;font-size:16px;line-height:22px;font-weight:600}& .oc p{margin:2px 0 0;font-size:12px;line-height:16px;color:var(--ink3)}& .oc .ft{display:flex;align-items:center;justify-content:space-between;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}& .oc .ft span{font-size:14px;color:var(--ink2)}& .more{height:36px;padding:0 16px;border-radius:18px;background:var(--card);box-shadow:inset 0 0 0 1px var(--n8);font-size:14px;color:var(--ink);position:relative}& .more::after{content:"";position:absolute;inset:-4px -2px}& .oc.ad{margin-top:10px}& .oc.gone{opacity:.5}& .ix-mask{background:color-mix(in srgb,var(--scrim) 42%,transparent)}& .sheet{position:relative;align-self:flex-end;width:100%;padding:0 10px 10px}& .grp{background:var(--card);border-radius:16px;overflow:hidden}& .grp .t{display:flex;align-items:center;justify-content:center;min-height:48px;padding:6px 16px;font-size:14px;line-height:20px;color:var(--ink3);text-align:center}& .opt{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;height:52px;border-top:1px solid var(--line);font-size:16px;color:var(--ink);transition:background-color .12s}& .opt:active{background:var(--soft)}& .opt span{display:inline-flex;width:20px;height:20px;color:var(--ink2)}& .opt.dng,& .opt.dng span{color:${DANGER}}& .cancel{display:block;width:100%;height:52px;margin-top:8px;border-radius:16px;background:var(--card);font-size:16px;font-weight:600;color:var(--ink)}& .cancel:active{background:var(--soft)}& .cf .t{flex-direction:column;gap:2px;padding:14px 16px}& .cf .t b{font-size:16px;font-weight:600;color:var(--ink)}& .ix-ov.show .sheet{animation:@@up .26s cubic-bezier(.2,0,0,1)}& .ix-ov.show .ix-mask{animation:@@fd .2s linear}@keyframes @@up{from{transform:translateY(60%);opacity:0}}@keyframes @@fd{from{opacity:0}}`),
  html: () => `<div class="mpfb004"><div class="nb">订单详情</div><div class="pg"><div class="oc"><div class="hd"><span>订单号 SO2026110412</span><b>待收货</b></div><div class="it"><img src="${P(0)}" alt=""><div><h4>无线降噪耳机</h4><p>石墨灰 · 主动降噪 × 1</p><p>实付 ¥599.00</p></div></div><div class="ft"><span>预计明天送达</span><button class="more" type="button" data-open="as">更多操作</button></div></div><div class="oc ad"><div class="hd"><span>收货信息</span></div><h4>林小满 138 0013 8000</h4><p>浙江省杭州市西湖区文三路 99 号 5 栋 502</p></div></div>
<div class="ix-ov show" data-ov="as"><div class="ix-mask"></div><div class="sheet">
<div class="grp lst"><div class="t">订单 SO2026110412</div><button class="opt" type="button" data-a="share"><span>${sv('share')}</span>分享给好友</button><button class="opt" type="button" data-a="copy"><span>${sv('copy')}</span>复制订单号</button><button class="opt" type="button" data-a="cs"><span>${sv('chat')}</span>联系客服</button><button class="opt dng" type="button" data-a="del"><span>${sv('trash')}</span>删除订单</button></div>
<div class="grp cf" hidden><div class="t"><b>确认删除订单？</b>删除后订单将无法找回</div><button class="opt dng" type="button" data-a="delok">删除</button></div>
<button class="cancel" type="button" data-close>取消</button></div></div></div>`,
  js: (root) => {
    const ov = q1(root, '[data-ov=as]'), lst = q1(root, '.lst'), cf = q1(root, '.cf'), oc = q1(root, '.oc')
    const reset = () => { lst.hidden = false; cf.hidden = true }
    q1(root, '.more').addEventListener('click', reset)
    const MSG = { share: '已打开分享面板', copy: '已复制订单号', cs: '正在接入在线客服…' }
    root.addEventListener('click', (e) => {
      const o = e.target.closest('.opt'); if (!o) return
      const a = o.dataset.a
      if (a === 'del') { lst.hidden = true; cf.hidden = false; return }
      ov.classList.remove('show')
      if (a === 'delok') { oc.classList.add('gone'); q1(oc, '.hd b').textContent = '已删除'; IX.toast(root, '订单已删除') } else IX.toast(root, MSG[a])
    })
  },
})

def({
  id: 'MP-FB-005', name: '轻提示变体', style: '多种状态',
  fit: '操作结果的即时反馈：成功简短、失败写原因、加载遮住操作并在完成后转成功，纯文字用于复制等轻反馈',
  avoid: '需要用户做决定的信息（用对话框）；错误细节很多的表单（用原位提示）',
  kw: 'toast 轻提示 成功 失败 加载中 loading 反馈 已复制 snackbar',
  stage: 'white',
  css: CSS('mpfb005', `${SCR(380)}& .pg{padding:14px 14px 0}& .pg h5{margin:0 0 4px 4px;font-size:12px;line-height:16px;font-weight:600;color:var(--ink3)}& .li{display:flex;flex-direction:column;background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 4px 14px var(--sh06)}& .li button{display:flex;align-items:center;gap:12px;min-height:56px;padding:0 14px;border-top:1px solid var(--line);text-align:left;transition:background-color .12s}& .li button:first-child{border-top:0}& .li button:active{background:var(--n3)}& .li button:disabled{cursor:progress;opacity:.55}& .ib{display:flex;align-items:center;justify-content:center;flex:none;width:32px;height:32px;border-radius:10px}& .ib span{display:inline-flex;width:18px;height:18px}& .ib.ok{background:var(--ok-bg);color:${OKT}}& .ib.er{background:var(--danger-bg);color:${DANGER}}& .ib.ld{background:var(--pt);color:var(--p-text)}& .ib.tx{background:var(--soft);color:var(--ink2)}& .li b{display:block;font-size:16px;line-height:22px;font-weight:600}& .li small{display:block;font-size:12px;line-height:16px;color:var(--ink3)}& .li .ch{display:inline-flex;margin-left:auto;width:16px;height:16px;color:var(--ink3)}& .msk{position:absolute;inset:0;z-index:20}& .tt{position:absolute;z-index:21;left:50%;top:46%;display:flex;flex-direction:column;align-items:center;gap:10px;min-width:132px;max-width:236px;padding:20px 22px;border-radius:16px;background:color-mix(in srgb,var(--inv) 92%,transparent);color:#fff;font-size:14px;line-height:20px;text-align:center;transform:translate(-50%,-50%);box-shadow:0 14px 30px rgba(0,0,0,.22);animation:@@in .2s cubic-bezier(.2,0,0,1)}& .tt small{display:block;margin-top:-4px;font-size:12px;line-height:16px;color:rgba(255,255,255,.78)}& .tt .ci{display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:50%}& .tt .ci span{display:inline-flex;width:20px;height:20px}& .tt .ci.ok{background:var(--ok-fill)}& .tt .ci.er{background:var(--danger-fill)}& .tt.txt{top:auto;bottom:28px;min-width:0;flex-direction:row;padding:11px 18px;border-radius:22px;transform:translateX(-50%)}${SPIN('mpfb005', '& .tt .ld', 30, '#fff', 'rgba(255,255,255,.3)')}@keyframes @@in{from{opacity:0;transform:translate(-50%,-46%)}}& .tt.txt{animation-name:@@in2}@keyframes @@in2{from{opacity:0;transform:translate(-50%,8px)}}`),
  html: () => {
    const r = (k, c, ic, t, s) => `<button type="button" data-k="${k}"><span class="ib ${c}"><span>${sv(ic)}</span></span><span><b>${t}</b><small>${s}</small></span><span class="ch">${sv('right')}</span></button>`
    return `<div class="mpfb005"><div class="nb">轻提示</div><div class="pg"><h5>点一点，看看四种提示</h5><div class="li">${r('ok', 'ok', 'checkc', '成功', '操作完成，1.8 秒后自动消失')}${r('er', 'er', 'closec', '失败', '写清原因，停留 2.4 秒')}${r('ld', 'ld', 'refresh', '加载中', '遮住操作，完成后转成“已保存”')}${r('tx', 'tx', 'copy', '纯文字', '复制等轻反馈，贴近底部')}</div></div></div>`
  },
  js: (root) => {
    const box = root, btns = qa(root, '.li button'); let t1 = 0, t2 = 0
    const clear = () => { clearTimeout(t1); clearTimeout(t2); qa(box, '.tt, .msk').forEach((n) => n.remove()) }
    const mount = (cls, inner) => { clear(); const d = document.createElement('div'); d.className = 'tt ' + cls; d.setAttribute('role', 'status'); d.innerHTML = inner; q1(box, '.mpfb005').appendChild(d); return d }
    const ico = (c, n) => `<span class="ci ${c}"><span>${sv(n)}</span></span>`
    const show = (k) => {
      if (k === 'ok') { mount('ok', `${ico('ok', 'check')}已加入购物车`); t1 = later(root, 1800, clear) }
      if (k === 'er') { mount('er', `${ico('er', 'close')}提交失败<small>网络开小差了，请稍后重试</small>`); t1 = later(root, 2400, clear) }
      if (k === 'tx') { mount('txt', '已复制到剪贴板'); t1 = later(root, 1600, clear) }
      if (k === 'ld') {
        mount('ld', '<span class="ld"></span>正在保存…')
        const m = document.createElement('div'); m.className = 'msk'; q1(box, '.mpfb005').appendChild(m)
        btns.forEach((b) => (b.disabled = true))
        t1 = later(root, 1500, () => { mount('ok', `${ico('ok', 'check')}已保存`); btns.forEach((b) => (b.disabled = false)); t2 = later(root, 1400, clear) })
      }
    }
    btns.forEach((b) => b.addEventListener('click', () => show(b.dataset.k)))
  },
})

def({
  id: 'MP-FB-006', name: '下拉刷新', style: '拖出刷新态',
  fit: '消息、订单、动态等会更新的列表；手指下拉拉出提示，松手刷新，结果写明新增条数',
  avoid: '无限滚动的长内容页已有“加载更多”时再加会冲突；刷新耗时很长的页面（改骨架屏）',
  kw: 'pull refresh 下拉刷新 刷新 列表 松手 加载 pull-down 更新 消息列表',
  stage: 'white',
  css: CSS('mpfb006', `${SCR(400)}& .nb .rf{position:absolute;right:4px;top:2px;width:44px;height:44px;display:flex;align-items:center;justify-content:center;color:var(--ink2)}& .nb .rf span{display:inline-flex;width:20px;height:20px}& .vp{position:relative;height:352px;overflow:hidden;touch-action:none;cursor:grab;user-select:none}& .ind{position:absolute;left:0;right:0;top:0;height:56px;display:flex;align-items:center;justify-content:center;gap:8px;font-size:14px;color:var(--ink2)}& .ind span.a{display:inline-flex;width:18px;height:18px;transition:transform .2s cubic-bezier(.2,0,0,1)}& .ind.rdy span.a{transform:rotate(180deg)}& .ind.done{color:${OKT}}${SPIN('mpfb006', '& .ind i', 18, 'var(--p)', 'rgba(var(--p-rgb),.25)')}& .lst{position:relative;background:var(--card);will-change:transform;min-height:352px}& .r{display:flex;align-items:center;gap:12px;height:64px;padding:0 14px;border-bottom:1px solid var(--line);background:var(--card);transition:background-color 1.6s ease-out}& .r.new{background:var(--pt);transition:none}& .r .tx{flex:1;min-width:0}& .r b{display:block;font-size:16px;line-height:22px;font-weight:600}& .r p{margin:0;font-size:12px;line-height:16px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}& .r time{align-self:flex-start;margin-top:12px;font-size:12px;color:var(--ink3)}& .end{padding:16px;text-align:center;font-size:12px;color:var(--ink3)}`),
  html: () => `<div class="mpfb006"><div class="nb">消息<button class="rf" type="button" aria-label="刷新"><span>${sv('refresh')}</span></button></div>
<div class="vp"><div class="ind"><span class="a">${sv('arrowdown')}</span><em>下拉刷新</em></div><div class="lst"></div></div></div>`,
  js: (root) => {
    const vp = q1(root, '.vp'), lst = q1(root, '.lst'), ind = q1(root, '.ind'), TH = 64, HOLD = 56
    const row = (i, n, p, t, cls = '') => `<div class="r ${cls}">${critter(i, 40)}<div class="tx"><b>${n}</b><p>${p}</p></div><time>${t}</time></div>`
    const base = [[0, '系统通知', '你的订单已发货，预计明天送达', '10:24'], [1, '优惠中心', '满 99 减 20 券已到账，3 天后到期', '09:40'], [2, '林小满', '好的，那我先下单了，谢谢！', '昨天'], [3, '客服小助手', '您的售后申请已受理，请留意进度', '昨天'], [0, '会员中心', '本月积分将于月底清零，请尽快使用', '周一']]
    const batches = [[[1, '王子豪', '请问这款什么时候能补货？', '刚刚'], [2, '陈晓雨', '收到包裹啦，很满意，已好评', '刚刚'], [3, '物流通知', '包裹已到达杭州转运中心', '刚刚']], [[0, '李安然', '周末有门店活动吗？', '刚刚'], [1, '拼团提醒', '你参与的拼团还差 1 人成团', '刚刚']]]
    let list = base.slice(), y = 0, busy = false, d = null, n = 0
    const draw = (fresh = 0) => { lst.innerHTML = list.map((r, i) => row(...r, i < fresh ? 'new' : '')).join('') + '<div class="end">没有更多了</div>'; if (fresh) requestAnimationFrame(() => requestAnimationFrame(() => qa(lst, '.new').forEach((e) => e.classList.remove('new')))) }
    const mode = (k) => { ind.className = 'ind' + (k ? ' ' + k : '') }
    const set = (v, anim) => { y = v; lst.style.transition = anim ? 'transform .28s cubic-bezier(.2,0,0,1)' : 'none'; lst.style.transform = `translateY(${v}px)`; ind.style.opacity = v > 0 ? Math.min(1, 0.25 + v / 40) : anim ? 1 : 0; if (v === 0 && anim) later(root, 300, () => { if (y === 0) ind.style.opacity = 0 }) }
    const refresh = () => {
      if (busy) return; busy = true; set(HOLD, true); mode('ing'); ind.innerHTML = '<i></i><em>刷新中…</em>'
      later(root, 1100, () => {
        const add = batches[n++] || []
        list = add.concat(list); draw(add.length)
        mode('done'); ind.innerHTML = `<span class="a">${sv('check')}</span><em>${add.length ? `已更新 ${add.length} 条消息` : '已是最新，暂无新消息'}</em>`
        later(root, 800, () => { set(0, true); later(root, 300, () => { busy = false; mode(''); ind.innerHTML = `<span class="a">${sv('arrowdown')}</span><em>下拉刷新</em>`}) })
      })
    }
    vp.addEventListener('pointerdown', (e) => { if (busy) return; d = { y0: e.clientY, id: e.pointerId, m: false } })
    vp.addEventListener('pointermove', (e) => {
      if (!d) return; const dy = e.clientY - d.y0
      if (!d.m && Math.abs(dy) > 3) { d.m = true; try { vp.setPointerCapture(d.id) } catch (x) { /* 触屏已自动捕获 */ } }
      if (!d.m) return
      const v = Math.max(0, Math.min(110, dy * 0.5)); set(v, false)
      const rdy = v >= TH; ind.classList.toggle('rdy', rdy); q1(ind, 'em').textContent = rdy ? '松手刷新' : '下拉刷新'
    })
    const end = () => { if (!d) return; const m = d.m; d = null; if (!m) return; if (y >= TH) refresh(); else { set(0, true) } }
    vp.addEventListener('pointerup', end); vp.addEventListener('pointercancel', end)
    q1(root, '.rf').addEventListener('click', refresh)
    draw(); set(0, false); ind.style.opacity = 0
  },
})

def({
  id: 'MP-FB-007', name: '悬浮客服按钮', style: '可拖动展开',
  fit: '商城、服务类页面常驻的客服入口；点开向上展开三个入口，可以拖到左右边缘吸附，不挡主内容',
  avoid: '已有底部固定操作栏的详情页（会叠在一起，改放进操作栏）；一屏同时有第二个悬浮按钮',
  kw: 'fab 悬浮按钮 客服 在线客服 展开 吸附 拖动 联系我们 意见反馈',
  stage: 'white',
  css: CSS('mpfb007', `${SCR(400)}& .pg{padding:12px}& .bn{height:96px;border-radius:16px;background:linear-gradient(135deg,var(--pm),var(--pt));display:flex;align-items:center;padding:0 18px;font-size:18px;font-weight:600;color:var(--p-text)}& .gd{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}& .gd div{background:var(--card);border-radius:14px;overflow:hidden;box-shadow:0 4px 14px var(--sh06)}& .gd img{width:100%;aspect-ratio:1.5;object-fit:cover}& .gd p{margin:0;padding:8px 10px 10px;font-size:14px;line-height:20px;color:var(--ink)}& .msk{position:absolute;inset:0;z-index:10;background:color-mix(in srgb,var(--scrim) 30%,transparent);opacity:0;pointer-events:none;transition:opacity .2s}&.open .msk{opacity:1;pointer-events:auto}& .fab{position:absolute;z-index:11;width:52px;height:52px;touch-action:none}& .fab.snap{transition:left .24s cubic-bezier(.2,0,0,1),top .24s cubic-bezier(.2,0,0,1)}& .fb{position:relative;width:52px;height:52px;border-radius:50%;${PRIMARY};box-shadow:0 10px 22px rgba(var(--p-rgb),.28);display:flex;align-items:center;justify-content:center;cursor:grab}& .fb.drag{cursor:grabbing}& .fb span.i{position:absolute;display:inline-flex;width:24px;height:24px;transition:opacity .18s,transform .22s cubic-bezier(.2,0,0,1)}& .fb span.x{opacity:0;transform:rotate(-90deg)}&.open .fb span.i:not(.x){opacity:0;transform:rotate(90deg)}&.open .fb span.x{opacity:1;transform:none}& .bd{position:absolute;right:-2px;top:-2px;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--danger-fill);color:#fff;font-size:12px;line-height:18px;font-weight:600;text-align:center;box-shadow:0 0 0 2px var(--card)}& .mn{position:absolute;bottom:62px;right:0;display:flex;flex-direction:column;align-items:flex-end;gap:10px;pointer-events:none}& .fab.l .mn{right:auto;left:0;align-items:flex-start}& .fab.dn .mn{bottom:auto;top:62px;flex-direction:column-reverse}& .mi{display:flex;align-items:center;gap:8px;height:44px;padding:0 16px 0 12px;border-radius:22px;background:var(--card);box-shadow:0 8px 20px var(--sh16);font-size:14px;font-weight:600;white-space:nowrap;opacity:0;transform:translateY(var(--ty,10px)) scale(.96);transition:opacity .18s,transform .22s cubic-bezier(.2,0,0,1);transition-delay:calc(var(--i) * 40ms)}& .mi span{display:inline-flex;width:20px;height:20px;color:var(--p-text)}& .fab.dn .mn{--ty:-10px}&.open .mi{opacity:1;transform:none;pointer-events:auto}`),
  html: () => `<div class="mpfb007"><div class="nb">商城首页</div><div class="pg"><div class="bn">新品上市 · 次日达</div><div class="gd"><div><img src="${P(1)}" alt=""><p>轻量跑鞋</p></div><div><img src="${P(6)}" alt=""><p>保温水杯</p></div><div><img src="${P(2)}" alt=""><p>陶瓷马克杯</p></div><div><img src="${P(5)}" alt=""><p>护眼台灯</p></div></div></div>
<div class="msk"></div><div class="fab" style="left:274px;top:326px"><div class="mn"><button class="mi" type="button" style="--i:2" data-a="chat"><span>${sv('chat')}</span>在线客服</button><button class="mi" type="button" style="--i:1" data-a="tel"><span>${sv('phone')}</span>电话客服</button><button class="mi" type="button" style="--i:0" data-a="fb"><span>${sv('edit')}</span>意见反馈</button></div><button class="fb" type="button" aria-label="客服" aria-expanded="false"><span class="i">${sv('mpb_headset')}</span><span class="i x">${sv('close')}</span><b class="bd">1</b></button></div></div>`,
  js: (root) => {
    const W = 340, Hh = 400, S = 52, M = 14, frame = q1(root, '.mpfb007'), fab = q1(root, '.fab'), fb = q1(root, '.fb'), bd = q1(root, '.bd')
    let d = null, was = false
    const side = () => fab.classList.toggle('l', fab.offsetLeft + S / 2 < W / 2)
    const toggle = (on) => { const o = on === undefined ? !frame.classList.contains('open') : on; frame.classList.toggle('open', o); fb.setAttribute('aria-expanded', o); fab.classList.toggle('dn', o && fab.offsetTop < 190); side() }
    fb.addEventListener('pointerdown', (e) => { if (frame.classList.contains('open')) return; d = { x: e.clientX, y: e.clientY, l: fab.offsetLeft, t: fab.offsetTop, m: false, id: e.pointerId }; fab.classList.remove('snap') })
    fb.addEventListener('pointermove', (e) => {
      if (!d) return; const dx = e.clientX - d.x, dy = e.clientY - d.y
      if (!d.m && Math.hypot(dx, dy) > 5) { d.m = true; fb.classList.add('drag'); try { fb.setPointerCapture(d.id) } catch (x) { /* ok */ } }
      if (d.m) { fab.style.left = clamp(d.l + dx, M, W - S - M) + 'px'; fab.style.top = clamp(d.t + dy, 56, Hh - S - M) + 'px' }
    })
    const end = () => { if (!d) return; const m = d.m; d = null; fb.classList.remove('drag'); if (!m) return; was = true; setTimeout(() => (was = false), 0); fab.classList.add('snap'); fab.style.left = (fab.offsetLeft + S / 2 < W / 2 ? M : W - S - M) + 'px'; later(root, 260, side) }
    fb.addEventListener('pointerup', end); fb.addEventListener('pointercancel', end)
    fb.addEventListener('click', () => { if (was) return; toggle() })
    q1(root, '.msk').addEventListener('click', () => toggle(false))
    const MSG = { chat: '正在接入在线客服…', tel: '将拨打 400-820-1234', fb: '进入意见反馈页' }
    qa(root, '.mi').forEach((b) => b.addEventListener('click', () => { if (b.dataset.a === 'chat') bd.hidden = true; toggle(false); IX.toast(root, MSG[b.dataset.a]) }))
  },
})

def({
  id: 'MP-FB-008', name: '消息通知条', style: '可关闭重试',
  fit: '页面顶部的公告、网络异常、支付结果等轻通知；公告可滚动，异常带重试，结果带去处，一律不遮挡操作',
  avoid: '需要用户必须处理的信息（用对话框）；断网这类持续状态不要给关闭键，恢复后让它自己消失',
  kw: 'notice bar 通知条 公告 滚动公告 网络异常 重试 关闭 banner 消息气泡',
  stage: 'white',
  css: CSS('mpfb008', `&{width:340px;display:flex;flex-direction:column;gap:10px}& .nt{overflow:hidden;border-radius:14px;transition:height .22s cubic-bezier(.2,0,0,1),opacity .2s,margin .22s}& .nt .in{display:flex;align-items:center;gap:10px;min-height:48px;padding:6px 6px 6px 14px;border-radius:14px}& .nt.info .in{background:var(--pt);color:var(--p-text)}& .nt.warn .in{background:var(--warn-bg);color:${WARN}}& .nt.ok .in{background:var(--ok-bg);color:${OKT}}& .ic{display:inline-flex;flex:none;width:20px;height:20px}& .mq{flex:1;min-width:0;overflow:hidden;white-space:nowrap;font-size:14px;line-height:20px;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 10px,#000 calc(100% - 10px),transparent 100%);mask-image:linear-gradient(90deg,transparent 0,#000 10px,#000 calc(100% - 10px),transparent 100%)}& .mq>span{display:inline-flex;animation:@@m 18s linear infinite}& .mq:hover>span{animation-play-state:paused}& .mq i{flex:none;padding-right:56px}@keyframes @@m{to{transform:translateX(-50%)}}@media(prefers-reduced-motion:reduce){& .mq{text-overflow:ellipsis}& .mq>span{animation:none}& .mq i+i{display:none}}& .tx{flex:1;min-width:0;font-size:14px;line-height:20px}& .act{flex:none;display:inline-flex;align-items:center;gap:4px;height:32px;padding:0 12px;border-radius:16px;background:var(--glass0);font-size:14px;font-weight:600;color:inherit;position:relative}& .act::after{content:"";position:absolute;inset:-6px -2px}& .gol{position:relative;flex:none;display:inline-flex;align-items:center;font-size:14px;font-weight:600;color:inherit}& .gol::after{content:"";position:absolute;inset:-12px -6px}& .gol span{display:inline-flex;width:14px;height:14px}& .cl{position:relative;flex:none;width:32px;height:32px;display:flex;align-items:center;justify-content:center;opacity:.8}& .cl::after{content:"";position:absolute;inset:-6px}& .cl span{display:inline-flex;width:16px;height:16px}${SPIN('mpfb008', '& .act i', 14, 'currentColor', 'rgba(138,90,0,.25)')}& .none{display:none;align-items:center;justify-content:space-between;min-height:48px;padding:0 14px;border-radius:14px;background:var(--card);box-shadow:inset 0 0 0 1px var(--n6);font-size:14px;color:var(--ink2)}& .none.show{display:flex}& .none button{font-weight:600;color:var(--p-text);height:32px;position:relative}& .none button::after{content:"";position:absolute;inset:-6px}`),
  html: () => `<div class="mpfb008">
<div class="nt info" data-k="mq"><div class="in"><span class="ic">${sv('mpb_notice')}</span><div class="mq"><span><i>【公告】会员日福利：本周三全场满 199 减 30，叠加会员 9 折，活动至 11 月 6 日 24:00 截止，先到先得。</i><i aria-hidden="true">【公告】会员日福利：本周三全场满 199 减 30，叠加会员 9 折，活动至 11 月 6 日 24:00 截止，先到先得。</i></span></div><button class="cl" type="button" aria-label="关闭公告"><span>${sv('close')}</span></button></div></div>
<div class="nt warn" data-k="net"><div class="in"><span class="ic">${sv('mpb_wifioff')}</span><span class="tx">网络连接已断开，部分功能暂不可用</span><button class="act" type="button"><i hidden></i><b>重试</b></button></div></div>
<div class="nt ok" data-k="pay"><div class="in"><span class="ic">${sv('checkc')}</span><span class="tx">订单支付成功，预计明天送达</span><button class="gol" type="button" data-t="查看订单">查看<span>${sv('right')}</span></button><button class="cl" type="button" aria-label="关闭提示"><span>${sv('close')}</span></button></div></div>
<div class="none"><span>通知已全部关闭</span><button type="button">重新显示</button></div></div>`,
  js: (root) => {
    const none = q1(root, '.none'), nts = qa(root, '.nt')
    const left = () => nts.filter((n) => !n.hidden).length
    const fold = (n) => { n.style.height = n.offsetHeight + 'px'; requestAnimationFrame(() => { n.style.height = '0'; n.style.opacity = '0'; n.style.marginTop = '-10px' }); later(root, 230, () => { n.hidden = true; if (!left()) none.classList.add('show') }) }
    root.addEventListener('click', (e) => {
      const cl = e.target.closest('.cl'), act = e.target.closest('.act'), lk = e.target.closest('.gol')
      if (cl) { fold(cl.closest('.nt')); return }
      if (lk) { IX.toast(root, '进入订单详情'); return }
      if (act) {
        const n = act.closest('.nt'); if (act.dataset.busy) return; act.dataset.busy = 1
        q1(act, 'i').hidden = false; q1(act, 'b').textContent = '连接中'; q1(n, '.tx').textContent = '正在重新连接网络…'
        later(root, 1300, () => {
          n.className = 'nt ok'; q1(n, '.tx').textContent = '网络已恢复'; q1(n, '.ic').innerHTML = sv('checkc'); act.remove()
          later(root, 1500, () => fold(n))
        })
      }
    })
    q1(none, 'button').addEventListener('click', () => { const b = BLOCKS.find((x) => x.id === 'MP-FB-008'); root.innerHTML = b.html(); b.js(root); IX.init(root) })
  },
})
/* ───────── NAV 导航与顶栏 ───────── */
/* 微信自带的右上角胶囊（87×32）：自定义顶栏要给它留位置，这里画一个占位 */
const WXCAP = '<svg width="87" height="32" viewBox="0 0 87 32" fill="none" aria-hidden="true"><rect x=".5" y=".5" width="86" height="31" rx="15.5" fill="rgba(255,255,255,.7)" stroke="rgba(31,35,41,.2)"/><circle cx="24" cy="16" r="2" fill="var(--ink)"/><circle cx="31" cy="16" r="2" fill="var(--ink)"/><circle cx="38" cy="16" r="2" fill="var(--ink)"/><path d="M43.500 8v16" stroke="rgba(31,35,41,.2)"/><circle cx="62" cy="16" r="6.500" stroke="var(--ink)" stroke-width="1.800"/><circle cx="62" cy="16" r="2.500" fill="var(--ink)"/></svg>'

def({
  id: 'MP-NAV-006', name: '搜索导航栏', style: '定位加联想',
  fit: '首页、频道页顶部：左侧定位城市可切换，中间搜索框轮播热词、聚焦后给联想，右侧为微信胶囊留位',
  avoid: '没有定位业务的小程序（去掉定位，搜索框占满）；联想词没有真实数据来源时不要放',
  kw: 'search 搜索导航 定位 城市切换 热搜 联想 搜索框 首页顶栏 胶囊',
  stage: 'white',
  css: CSS('mpnav006', `&{position:relative;width:340px;background:var(--card);border-radius:22px;box-shadow:0 12px 30px var(--sh14)}& .top{display:flex;align-items:center;gap:8px;height:56px;padding:0 12px}& .loc{flex:none}& .lc{display:flex;align-items:center;gap:2px;height:44px;padding:0 2px;font-size:16px;font-weight:600;color:var(--ink)}& .lc span{display:inline-flex;width:18px;height:18px;color:var(--p-text)}& .lc b+span{width:14px;height:14px;color:var(--ink3)}& .loc .menu{min-width:132px;padding:6px;border-radius:14px;background:var(--card2);box-shadow:0 12px 30px var(--sh18)}& .loc .menu div{display:flex;align-items:center;height:40px;padding:0 10px;border-radius:10px;font-size:14px;color:var(--ink);cursor:pointer}& .loc .menu div:hover{background:var(--n3)}& .loc .menu div.on{color:var(--p-text);font-weight:600;background:var(--pt)}& .sr{flex:1;min-width:0;display:flex;align-items:center;gap:6px;height:36px;padding:0 4px 0 12px;border-radius:18px;background:var(--soft);box-shadow:inset 0 0 0 1px transparent;transition:box-shadow .15s,background-color .15s}& .sr:focus-within{background:var(--card);box-shadow:inset 0 0 0 1px var(--ink2)}& .sr>span{display:inline-flex;flex:none;width:18px;height:18px;color:var(--ink3)}& .inp{position:relative;flex:1;min-width:0;height:100%}& .inp input{width:100%;height:100%;border:0;outline:0;background:none;padding:0;font:inherit;font-size:14px;color:var(--ink)}& .inp input::-webkit-search-cancel-button{display:none}& .rl{position:absolute;inset:0;display:flex;align-items:center;font-size:14px;color:color-mix(in srgb,var(--ink4) 52%,var(--ink3));pointer-events:none;white-space:nowrap;overflow:hidden;animation:@@roll .3s cubic-bezier(.2,0,0,1)}@keyframes @@roll{from{opacity:0;transform:translateY(8px)}}& .inp input:not(:placeholder-shown)~.rl{display:none}& .cl{position:relative;flex:none;width:28px;height:28px;display:flex;align-items:center;justify-content:center;color:color-mix(in srgb,var(--ink6) 31%,var(--ink5))}& .cl::after{content:"";position:absolute;inset:-8px -4px}& .cl span{display:inline-flex;width:16px;height:16px}& .wx{flex:none;width:87px;height:32px}& .wx svg{display:block}& .hot{padding:2px 16px 16px}& .hot+.hot{padding-top:0}& .hot h5{display:flex;align-items:center;gap:6px;margin:0 0 10px;font-size:14px;line-height:20px;font-weight:600;color:var(--ink2)}& .hot h5>span{display:inline-flex;width:16px;height:16px;color:var(--p-text)}& .hot h5 .clr{position:relative;margin-left:auto;width:28px;height:28px;display:flex;align-items:center;justify-content:center;color:var(--ink3)}& .hot h5 .clr::after{content:"";position:absolute;inset:-8px}& .hot h5 .clr span{display:inline-flex;width:16px;height:16px}& .ws{display:flex;flex-wrap:wrap;gap:8px}& .ws button{position:relative;height:32px;padding:0 12px;border-radius:16px;background:var(--soft);font-size:14px;color:var(--ink2)}& .ws button::after{content:"";position:absolute;inset:-6px -2px}& .ws button.hl{background:var(--pt);color:var(--p-text);font-weight:600}& .sug{display:none;position:absolute;left:0;right:0;top:56px;z-index:20;padding:4px 16px 12px;border-radius:0 0 22px 22px;background:var(--card);box-shadow:0 18px 30px var(--sh14)}&.open .sug{display:block}& .sug .ls button{display:flex;align-items:center;gap:10px;width:100%;height:44px;font-size:16px;color:var(--ink);text-align:left;border-bottom:1px solid var(--line)}& .sug .ls button span{display:inline-flex;width:16px;height:16px;color:var(--ink3)}& .ne{display:none;padding:18px 0 8px;text-align:center;font-size:14px;color:var(--ink3)}& .ne.show{display:block}`),
  html: () => `<div class="mpnav006"><div class="top">
<div class="loc" data-ix="dd"><button class="lc" type="button" data-tg aria-label="切换城市"><span>${sv('pin')}</span><b data-label>杭州</b><span>${sv('down')}</span></button><div class="menu">${['杭州', '上海', '北京', '深圳'].map((c, i) => `<div data-o class="${i ? '' : 'on'}">${c}</div>`).join('')}</div></div>
<label class="sr"><span>${sv('search')}</span><div class="inp"><input type="search" placeholder=" " autocomplete="off" aria-label="搜索" data-ix="search" data-list=".sug .ls"><span class="rl">无线降噪耳机</span></div><button class="cl" type="button" aria-label="清除" hidden><span>${sv('closec')}</span></button></label>
<div class="wx" aria-hidden="true" title="微信胶囊占位">${WXCAP}</div></div>
<div class="hot"><h5><span>${sv('fire')}</span>大家都在搜</h5><div class="ws">${['无线降噪耳机', '护眼台灯', '保温水杯', '春季新品', '机械腕表', '会员日'].map((w, i) => `<button type="button" class="${i === 0 ? 'hl' : ''}">${w}</button>`).join('')}</div></div>
<div class="hot rc"><h5><span>${sv('clock')}</span>最近搜索<button class="clr" type="button" aria-label="清空搜索记录"><span>${sv('trash')}</span></button></h5><div class="ws">${['帆布托特包', '陶瓷马克杯', '保湿精华'].map((w) => `<button type="button">${w}</button>`).join('')}</div></div>
<div class="sug"><div class="ls">${['无线降噪耳机', '无线充电器', '护眼台灯', '保温水杯', '陶瓷马克杯', '机械腕表'].map((w) => `<button type="button"><span>${sv('search')}</span>${w}</button>`).join('')}</div><div class="ne">没有找到相关商品，换个词试试</div></div></div>`,
  js: (root) => {
    const input = q1(root, 'input'), rl = q1(root, '.rl'), cl = q1(root, '.cl'), sug = q1(root, '.sug'), ne = q1(root, '.ne'), frame = q1(root, '.mpnav006')
    const words = ['无线降噪耳机', '护眼台灯', '保温水杯', '春季新品']; let k = 0
    every(root, 3000, () => { if (input.value) return; k = (k + 1) % words.length; rl.textContent = words[k]; rl.style.animation = 'none'; void rl.offsetWidth; rl.style.animation = '' })
    const go = (w) => { input.value = w; cl.hidden = !w; frame.classList.remove('open'); input.blur(); IX.toast(root, `搜索：${w}`) }
    input.addEventListener('focus', () => frame.classList.add('open'))
    input.addEventListener('blur', () => frame.classList.remove('open'))
    input.addEventListener('input', () => {
      const v = input.value.trim().toLowerCase(); cl.hidden = !input.value
      ne.classList.toggle('show', !qa(sug, '.ls button').some((b) => !v || b.textContent.toLowerCase().includes(v)))
    })
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') go(input.value.trim() || rl.textContent) })
    sug.addEventListener('mousedown', (e) => e.preventDefault())
    sug.addEventListener('click', (e) => { const b = e.target.closest('.ls button'); if (b) go(b.textContent.trim()) })
    cl.addEventListener('click', () => { input.value = ''; cl.hidden = true; input.dispatchEvent(new Event('input', { bubbles: true })); input.focus() })
    qa(root, '.ws').forEach((w) => w.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) go(b.textContent.trim()) }))
    q1(root, '.clr').addEventListener('click', () => { q1(root, '.hot.rc').hidden = true; IX.toast(root, '已清空搜索记录') })
  },
})

def({
  id: 'MP-NAV-007', name: '吸顶标签栏', style: '横滑居中',
  fit: '分类较多（6–15 个）的频道页；标签可横向滑动，点谁谁滚到中间，滚过头图后吸在顶部，右侧可展开全部',
  avoid: '标签少于 5 个（直接平分宽度）；标签文字超过 5 个字（会撑得很宽）',
  kw: 'tabs 标签栏 吸顶 sticky 横滑 分类标签 选中居中 展开全部 频道',
  stage: 'white',
  css: CSS('mpnav007', `&{position:relative;width:340px;height:420px;border-radius:22px;overflow:hidden;background:var(--card);box-shadow:0 12px 30px var(--sh14)}& .scr{height:100%;overflow-y:auto;scrollbar-width:none}& .scr::-webkit-scrollbar{display:none}& .ban{display:flex;flex-direction:column;justify-content:center;gap:2px;height:100px;padding:0 20px;background:linear-gradient(135deg,var(--pm),var(--pt))}& .ban b{font-size:22px;line-height:30px;font-weight:700;color:var(--p-text)}& .ban span{font-size:14px;color:var(--ink2)}& .tbar{position:sticky;top:0;z-index:6;display:flex;align-items:center;height:48px;background:var(--card);box-shadow:0 1px 0 var(--line)}& .tbs{flex:1;min-width:0;height:100%;overflow-x:auto;scrollbar-width:none;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 12px,#000 calc(100% - 12px),transparent 100%);mask-image:linear-gradient(90deg,transparent 0,#000 12px,#000 calc(100% - 12px),transparent 100%);cursor:grab}& .tbs::-webkit-scrollbar{display:none}& .tbs .in{position:relative;display:flex;width:max-content;height:100%;padding:0 6px}& .t{height:100%;padding:0 14px;font-size:16px;color:var(--ink2);white-space:nowrap}& .t span::after{content:attr(data-x);display:block;height:0;overflow:hidden;visibility:hidden;font-weight:600}& .t.on{color:var(--ink);font-weight:600}& .ink{position:absolute;left:0;bottom:3px;height:3px;transition:left .24s cubic-bezier(.2,0,0,1),width .24s cubic-bezier(.2,0,0,1)}& .ink::after{content:"";display:block;width:20px;height:3px;margin:0 auto;border-radius:2px;background:var(--p)}& .all{position:relative;flex:none;width:44px;height:48px;display:flex;align-items:center;justify-content:center;color:var(--ink2)}& .all span{display:inline-flex;width:18px;height:18px;transition:transform .2s cubic-bezier(.2,0,0,1)}&.pnl .all span{transform:rotate(180deg)}& .pn{display:none;position:absolute;left:0;right:0;top:48px;padding:6px 14px 16px;background:var(--card2);border-radius:0 0 16px 16px;box-shadow:0 18px 30px var(--sh16)}&.pnl .pn{display:block}& .pn h6{margin:0 0 10px 2px;font-size:12px;line-height:16px;font-weight:600;color:var(--ink3)}& .pn .g{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}& .pn button{height:44px;border-radius:12px;background:var(--soft);font-size:14px;color:var(--ink2)}& .pn button.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1.5px var(--p)}& .ls{padding:4px 14px 16px;animation:@@fd .2s linear}@keyframes @@fd{from{opacity:0}}& .lh{padding:10px 0 4px;font-size:12px;line-height:16px;color:var(--ink3)}& .rw{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}& .rw img{width:72px;height:72px;border-radius:12px;object-fit:cover;flex:none}& .rw .tx{flex:1;min-width:0;display:flex;flex-direction:column}& .rw .tx>b{font-size:16px;line-height:22px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}& .rw small{font-size:12px;line-height:16px;color:var(--ink3)}& .rw .pr{margin-top:auto}& .end{padding:14px;text-align:center;font-size:12px;color:var(--ink3)}`),
  html: () => `<div class="mpnav007"><div class="scr"><div class="ban"><b>分类精选</b><span>满 199 减 30 · 次日达</span></div>
<div class="tbar"><div class="tbs" data-ix="drag"><div class="in" role="tablist"></div></div><button class="all" type="button" aria-label="展开全部分类" aria-expanded="false"><span>${sv('down')}</span></button>
<div class="pn"><h6>全部分类</h6><div class="g"></div></div></div><div class="ls"></div></div></div>`,
  js: (root) => {
    const CATS = ['推荐', '数码', '家居', '美妆', '服饰', '食品', '母婴', '运动', '图书', '宠物']
    const frame = q1(root, '.mpnav007'), scr = q1(root, '.scr'), tbs = q1(root, '.tbs'), inn = q1(root, '.tbs .in'), pn = q1(root, '.pn .g'), ls = q1(root, '.ls'), ban = q1(root, '.ban'), all = q1(root, '.all')
    inn.innerHTML = CATS.map((c, i) => `<button class="t ${i === 0 ? 'on' : ''}" type="button" data-t="${i}" role="tab" aria-selected="${i === 0}"><span data-x="${c}">${c}</span></button>`).join('') + '<i class="ink"></i>'
    pn.innerHTML = CATS.map((c, i) => `<button type="button" data-i="${i}" class="${i === 0 ? 'on' : ''}">${c}</button>`).join('')
    const list = (k) => { const rows = Array.from({ length: 5 }, (_, j) => (k * 2 + j * 3 + 1) % 9); return `<div class="lh">${CATS[k]} · 共 ${rows.length} 件</div>${rows.map((i) => { const p = PRODUCTS[i]; return `<div class="rw"><img src="${P(i)}" alt=""><div class="tx"><b>${p.n}</b><small>${p.d}</small><div class="pr">${priceHTML(p.p, p.o)}</div></div></div>` }).join('')}<div class="end">没有更多了</div>` }
    const ink = (t) => { const k = q1(inn, '.ink'); k.style.left = t.offsetLeft + 'px'; k.style.width = t.offsetWidth + 'px' }
    const pick = (k) => {
      qa(inn, '.t').forEach((b, i) => { b.classList.toggle('on', i === k); b.setAttribute('aria-selected', i === k) }); qa(pn, 'button').forEach((b, i) => b.classList.toggle('on', i === k))
      const t = q1(inn, `.t[data-t="${k}"]`); tbs.scrollTo({ left: t.offsetLeft - (tbs.clientWidth - t.offsetWidth) / 2, behavior: 'smooth' }); ink(t)
      ls.innerHTML = list(k); ls.style.animation = 'none'; void ls.offsetWidth; ls.style.animation = ''
      if (scr.scrollTop > ban.offsetHeight) scr.scrollTop = ban.offsetHeight
    }
    inn.addEventListener('click', (e) => { if (e.target.__drag) return; const b = e.target.closest('.t'); if (b) pick(+b.dataset.t) })
    pn.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) { pick(+b.dataset.i); frame.classList.remove('pnl'); all.setAttribute('aria-expanded', false) } })
    all.addEventListener('click', () => { const o = frame.classList.toggle('pnl'); all.setAttribute('aria-expanded', o) })
    ls.innerHTML = list(0); requestAnimationFrame(() => ink(q1(inn, '.t.on')))
  },
})

def({
  id: 'MP-NAV-008', name: '步骤导航', style: '带校验',
  fit: '预约、开票、认证这类 3–5 步的流程；顶部显示进度，已完成的步骤可点回去改，不满足条件时说明为什么不能下一步',
  avoid: '少于 3 步（一页做完）；步骤之间没有先后关系（改标签页）',
  kw: 'steps 步骤 步骤条 分步 向导 进度 预约流程 stepper 上一步',
  stage: 'white',
  css: CSS('mpnav008', `&{width:340px;background:var(--card);border-radius:22px;padding:20px 18px 18px;box-shadow:${SHADOW}}& .stp{display:grid;grid-template-columns:repeat(4,1fr)}& .s{position:relative;display:flex;flex-direction:column;align-items:center;gap:6px;font-size:12px;line-height:16px;color:var(--ink3)}& .s::before,& .s::after{content:"";position:absolute;top:13px;left:-50%;right:50%;height:2px}& .s:first-child::before,& .s:first-child::after{display:none}& .s::before{background:var(--n6)}& .s::after{background:var(--p);transform:scaleX(0);transform-origin:left;transition:transform .3s cubic-bezier(.2,0,0,1)}& .s.on::after,& .s.done::after{transform:scaleX(1)}& .c{position:relative;z-index:1;width:28px;height:28px;border-radius:50%;background:var(--card);box-shadow:inset 0 0 0 1.5px var(--n9);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;color:var(--ink3);transition:background-color .2s,box-shadow .2s,color .2s}& .c span{display:inline-flex;width:16px;height:16px}& .s.on .c{background:var(--p);box-shadow:none;color:#fff}& .s.on{color:var(--ink);font-weight:600}& .s.done .c{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p);color:var(--p-text)}& .s.done{color:var(--ink2);cursor:pointer}& .bd{margin-top:20px;min-height:176px}& .pn h4{margin:0 0 4px;font-size:18px;line-height:24px;font-weight:600}& .pn p{margin:0 0 12px;font-size:14px;line-height:20px;color:var(--ink2)}& .opts{display:flex;flex-direction:column;gap:8px}& .opts button{display:flex;align-items:center;justify-content:space-between;min-height:44px;padding:0 14px;border-radius:12px;background:var(--card);box-shadow:inset 0 0 0 1px var(--n6);font-size:14px;color:var(--ink);text-align:left;transition:box-shadow .15s,background-color .15s}& .opts button.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p);font-weight:600}& .opts button em{font-size:14px;color:var(--ink2);font-weight:600}& .grd{display:grid;grid-template-columns:1fr 1fr;gap:8px}& .grd button{height:44px;border-radius:12px;background:var(--card);box-shadow:inset 0 0 0 1px var(--n6);font-size:14px;color:var(--ink);transition:box-shadow .15s,background-color .15s}& .grd button.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p);color:var(--p-text);font-weight:600}& .fl{display:flex;flex-direction:column;gap:8px}& .fl input{height:44px;padding:0 14px;border-radius:12px;border:1px solid var(--n7);outline:0;background:var(--card);font:inherit;font-size:14px;color:var(--ink)}& .fl input:focus{border-color:var(--ink2)}& .sm{display:flex;flex-direction:column;gap:6px;padding:12px 14px;border-radius:12px;background:var(--n3)}& .sm div{display:flex;justify-content:space-between;gap:12px;font-size:14px;line-height:20px;color:var(--ink2)}& .sm b{font-weight:600;color:var(--ink);text-align:right}& .fin{display:flex;flex-direction:column;align-items:center;gap:8px;padding:14px 0 0;text-align:center}& .fin h4{margin:0}& .fin p{margin:0}& .fin .m{display:flex;align-items:center;justify-content:center;width:52px;height:52px;border-radius:50%;background:var(--ok-bg);color:${OKC}}& .fin .m span{display:inline-flex;width:28px;height:28px}& .why{min-height:20px;margin:8px 2px 0;font-size:12px;line-height:16px;color:${DANGER}}& .ft{display:flex;gap:10px;margin-top:6px}& .ft button{flex:1;height:44px;border-radius:22px;font-size:16px;font-weight:600;transition:opacity .2s}& .ft .bk{background:var(--pt);color:var(--p-text)}& .ft .bk:disabled{opacity:.45;cursor:default}& .ft .nx{flex:1.4;${PRIMARY}}& .ft .nx.dis{opacity:.5;box-shadow:none}`),
  html: () => `<div class="mpnav008"><div class="stp">${['选服务', '填信息', '选时间', '确认'].map((t, i) => `<div class="s" data-i="${i}"><span class="c">${i + 1}</span>${t}</div>`).join('')}</div><div class="bd"></div><div class="why" aria-live="polite"></div><div class="ft"><button class="bk" type="button">上一步</button><button class="nx" type="button">下一步</button></div></div>`,
  js: (root) => {
    const SV = [['标准清洁', '¥99'], ['深度保养', '¥199'], ['上门检测', '¥49']], TM = ['今天 18:00', '明天 09:00', '明天 14:00', '后天 10:00']
    const st = { i: 0, sv: -1, name: '', tel: '', tm: -1, done: false }
    const bd = q1(root, '.bd'), why = q1(root, '.why'), ft = q1(root, '.ft')
    const ok = () => [st.sv >= 0, st.name.trim().length > 0 && /^1[3-9]\d{9}$/.test(st.tel), st.tm >= 0, true][st.i]
    const REASON = ['请先选择一个服务项目', '请填写联系人和 11 位手机号', '请先选择上门时间', '']
    const draw = () => {
      qa(root, '.s').forEach((s, i) => { s.classList.toggle('on', i === st.i && !st.done); s.classList.toggle('done', i < st.i || st.done); q1(s, '.c').innerHTML = i < st.i || st.done ? `<span>${sv('check')}</span>` : i + 1 })
      if (st.done) { bd.innerHTML = `<div class="fin"><span class="m"><span>${sv('check')}</span></span><h4>预约已提交</h4><p>我们会在 30 分钟内与你电话确认</p></div>`; ft.innerHTML = '<button class="bk" type="button" data-r>重新预约</button>'; why.textContent = ''; return }
      bd.innerHTML = [
        `<div class="pn"><h4>选择服务项目</h4><p>不同项目的时长和价格不同</p><div class="opts">${SV.map((s, i) => `<button type="button" data-v="${i}" class="${i === st.sv ? 'on' : ''}">${s[0]}<em>${s[1]}</em></button>`).join('')}</div></div>`,
        `<div class="pn"><h4>填写联系信息</h4><p>用于上门前电话确认</p><div class="fl"><input data-f="name" placeholder="联系人姓名" value="${st.name}" aria-label="联系人"><input data-f="tel" inputmode="numeric" maxlength="11" placeholder="11 位手机号" value="${st.tel}" aria-label="手机号"></div></div>`,
        `<div class="pn"><h4>选择上门时间</h4><p>时间为预估到达，师傅出发前会电话告知</p><div class="grd">${TM.map((t, i) => `<button type="button" data-v="${i}" class="${i === st.tm ? 'on' : ''}">${t}</button>`).join('')}</div></div>`,
        `<div class="pn"><h4>确认预约信息</h4><p>提交后可在“我的预约”中查看</p><div class="sm"><div>服务项目<b>${(SV[st.sv] || ['—'])[0]}</b></div><div>联系人<b>${st.name || '—'} ${st.tel}</b></div><div>上门时间<b>${TM[st.tm] || '—'}</b></div><div>费用<b>${(SV[st.sv] || [0, '—'])[1]}</b></div></div></div>`,
      ][st.i]
      ft.innerHTML = '<button class="bk" type="button">上一步</button><button class="nx" type="button"></button>'
      const b2 = q1(ft, '.bk'), n2 = q1(ft, '.nx'); b2.disabled = st.i === 0; n2.textContent = st.i === 3 ? '提交预约' : '下一步'; n2.classList.toggle('dis', !ok()); why.textContent = ''
    }
    root.addEventListener('click', (e) => {
      const s = e.target.closest('.s.done'), v = e.target.closest('[data-v]'), n = e.target.closest('.nx'), b = e.target.closest('.bk'), r = e.target.closest('[data-r]')
      if (r) { Object.assign(st, { i: 0, sv: -1, name: '', tel: '', tm: -1, done: false }); draw(); return }
      if (s && !st.done) { st.i = +s.dataset.i; draw(); return }
      if (v) { st[st.i === 0 ? 'sv' : 'tm'] = +v.dataset.v; draw(); return }
      if (b && !b.disabled && !st.done) { st.i--; draw(); return }
      if (n) { if (!ok()) { why.textContent = REASON[st.i]; return } if (st.i === 3) { st.done = true; draw(); return } st.i++; draw() }
    })
    root.addEventListener('input', (e) => { const f = e.target.dataset.f; if (!f) return; st[f] = e.target.value; why.textContent = ''; q1(root, '.nx').classList.toggle('dis', !ok()) })
    draw()
  },
})

def({
  id: 'MP-NAV-009', name: '悬浮返回胶囊', style: '透明变实色',
  fit: '商品详情、文章详情这类头部是大图的页面；返回和回首页做成悬浮胶囊压在图上，往下滑后变成实色标题栏',
  avoid: '没有头图的普通二级页（用实色顶栏）；图片是纯白或很浅时（胶囊对比不够，加深胶囊底色）',
  kw: '返回 胶囊 悬浮 透明导航 沉浸式 顶栏 详情页 返回首页 滚动渐变',
  stage: 'white',
  css: CSS('mpnav009', `&{position:relative;width:340px;height:420px;border-radius:22px;overflow:hidden;background:var(--n3);box-shadow:0 12px 30px var(--sh14)}& .scr{height:100%;overflow-y:auto;scrollbar-width:none}& .scr::-webkit-scrollbar{display:none}& .hero{display:block;width:100%;height:300px;object-fit:cover}& .nv{position:absolute;left:0;right:0;top:0;z-index:5;display:flex;align-items:center;justify-content:space-between;height:52px;padding:0 12px;background:rgba(255,255,255,var(--a,0));box-shadow:0 1px 0 rgba(238,240,243,var(--a,0))}& .cp{position:relative;display:flex;align-items:center;width:88px;height:32px;border-radius:16px;background:color-mix(in srgb,var(--scrim) 42%,transparent);color:#fff;transition:background-color .2s,color .2s}& .cp button{position:relative;flex:1;height:100%;display:flex;align-items:center;justify-content:center;color:inherit}& .cp button::after{content:"";position:absolute;inset:-6px -2px}& .cp button span{display:inline-flex;width:18px;height:18px}& .cp i{width:1px;height:14px;background:currentColor;opacity:.35}&.solid .cp{background:var(--soft);color:var(--ink)}& .ti{position:absolute;left:112px;right:112px;top:0;height:52px;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:600;opacity:var(--a,0);pointer-events:none}& .wx{width:87px;height:32px}& .wx svg{display:block}& .inf{position:relative;margin-top:-18px;padding:18px 18px 16px;border-radius:22px 22px 0 0;background:var(--card)}& .inf .pr{display:flex;align-items:baseline;gap:8px}& .inf h4{margin:8px 0 4px;font-size:18px;line-height:26px;font-weight:600}& .inf p{margin:0;font-size:14px;line-height:20px;color:var(--ink2)}& .sp{display:flex;flex-direction:column;gap:2px;margin-top:10px;padding:0 18px;background:var(--card)}& .sp div{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--line);font-size:14px;color:var(--ink2)}& .sp b{font-weight:600;color:var(--ink)}& .dt{margin-top:10px;padding:16px 18px 24px;background:var(--card)}& .dt h5{margin:0 0 10px;font-size:16px;font-weight:600}& .dt img{width:100%;aspect-ratio:1.4;border-radius:12px;object-fit:cover;margin-bottom:10px}`),
  html: () => `<div class="mpnav009"><div class="nv"><div class="cp"><button type="button" data-a="back" aria-label="返回"><span>${sv('back')}</span></button><i></i><button type="button" data-a="home" aria-label="回到首页"><span>${sv('home')}</span></button></div><b class="ti">商品详情</b><div class="wx" aria-hidden="true" title="微信胶囊占位">${WXCAP}</div></div>
<div class="scr"><img class="hero" src="${P(0)}" alt=""><div class="inf"><div class="pr"><span class="price"><small>¥</small><b>599</b></span><span class="strike">¥799</span></div><h4>无线降噪耳机</h4><p>石墨灰 · 主动降噪 · 40 小时续航</p></div>
<div class="sp"><div>已选<b>石墨灰</b></div><div>配送<b>次日达 · 免运费</b></div><div>售后<b>7 天无理由退换</b></div></div>
<div class="dt"><h5>商品详情</h5><img src="${P(1)}" alt=""><img src="${P(5)}" alt=""></div></div></div>`,
  js: (root) => {
    const scr = q1(root, '.scr'), nv = q1(root, '.nv'), frame = q1(root, '.mpnav009')
    const upd = () => { const a = clamp((scr.scrollTop - 90) / 110, 0, 1); nv.style.setProperty('--a', a.toFixed(2)); frame.classList.toggle('solid', a > 0.55) }
    scr.addEventListener('scroll', upd, { passive: true }); upd()
    root.addEventListener('click', (e) => { const b = e.target.closest('[data-a]'); if (b) IX.toast(root, b.dataset.a === 'back' ? '返回上一页' : '回到首页') })
  },
})

def({
  id: 'MP-NAV-010', name: '角标标签栏', style: '红点与数字',
  fit: '底部一级导航需要提示未读和待处理：消息用数字，购物车用数量，“我的”用小红点；进入对应页面后角标按规则消失',
  avoid: '给每个标签都挂角标（失去提醒作用）；数字超过 99 仍写具体数字（统一显示 99+）',
  kw: 'tabbar 标签栏 角标 红点 未读 badge 底部导航 99+ 购物车数量',
  stage: 'white',
  css: CSS('mpnav010', `&{position:relative;display:flex;flex-direction:column;width:340px;height:400px;border-radius:22px;overflow:hidden;background:var(--bg);box-shadow:0 12px 30px var(--sh14)}& .pgs{position:relative;flex:1;min-height:0;overflow:hidden}& .pg{position:absolute;inset:0;padding:14px;overflow-y:auto;scrollbar-width:none}& .pg h4{margin:0 0 12px;font-size:18px;line-height:24px;font-weight:600}& .pd{display:flex;gap:12px;align-items:center;padding:12px;border-radius:16px;background:var(--card);box-shadow:0 4px 14px var(--sh06)}& .pd img{width:64px;height:64px;border-radius:12px;object-fit:cover;flex:none}& .pd .tx{flex:1;min-width:0}& .pd .tx>b{display:block;font-size:16px;line-height:22px;font-weight:600}& .pd small{font-size:12px;color:var(--ink3)}& .adc{position:relative;height:36px;padding:0 14px;border-radius:18px;${PRIMARY};font-size:14px;font-weight:600;white-space:nowrap;box-shadow:none}& .adc::after{content:"";position:absolute;inset:-4px -2px}& .tip{margin:12px 2px 0;font-size:12px;line-height:18px;color:var(--ink3)}& .ms{display:flex;gap:12px;align-items:center;padding:12px;margin-bottom:8px;border-radius:16px;background:var(--card)}& .ms .tx{flex:1;min-width:0}& .ms b{display:block;font-size:16px;line-height:22px;font-weight:600}& .ms p{margin:0;font-size:12px;line-height:16px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}& .cats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}& .cats div{display:flex;align-items:center;justify-content:center;height:56px;border-radius:14px;background:var(--card);font-size:14px;color:var(--ink2)}& .me{display:flex;align-items:center;gap:12px;padding:14px;border-radius:16px;background:var(--card)}& .me b{font-size:18px;font-weight:600}& .me p{margin:0;font-size:12px;color:var(--ink3)}& .cart{display:flex;flex-direction:column;align-items:center;gap:6px;padding:30px 0;text-align:center;color:var(--ink2);font-size:14px}& .cart b{font-size:28px;line-height:34px;font-weight:700;color:var(--ink)}& .tb{display:flex;height:56px;background:var(--card);box-shadow:0 -1px 0 var(--line)}& .tb button{position:relative;flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:12px;line-height:16px;color:var(--ink3);transition:color .15s}& .tb button.on{color:var(--p-fg);font-weight:600}& .tb .ic{position:relative;display:inline-flex;width:24px;height:24px}& .tb button.on .ic svg{fill:rgba(var(--p-rgb),.16)}& .bg{position:absolute;left:calc(100% - 8px);top:-6px;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--danger-fill);color:#fff;font-size:12px;line-height:18px;font-weight:600;text-align:center;box-shadow:0 0 0 2px var(--card);animation:@@pop .22s cubic-bezier(.2,0,0,1)}& .bg.dot{left:calc(100% - 6px);top:-2px;min-width:0;width:10px;height:10px;padding:0;border-radius:50%}@keyframes @@pop{from{transform:scale(.4)}}`),
  html: () => {
    const T = [['home', 'home', '首页', ''], ['grid', 'grid', '分类', ''], ['msg', 'chat', '消息', '3'], ['cart', 'cart', '购物车', '2'], ['me', 'user', '我的', 'dot']]
    return `<div class="mpnav010"><div class="pgs">
<div class="pg" data-p="home"><h4>今日推荐</h4><div class="pd"><img src="${P(1)}" alt=""><div class="tx"><b>轻量跑鞋</b><small>云白 · 男女同款</small><div style="margin-top:4px">${priceHTML(329, 429)}</div></div><button class="adc" type="button">加入购物车</button></div><p class="tip">点“加入购物车”，看购物车角标数量增加</p></div>
<div class="pg" data-p="grid" hidden><h4>全部分类</h4><div class="cats">${['数码', '家居', '美妆', '服饰', '食品', '运动'].map((c) => `<div>${c}</div>`).join('')}</div></div>
<div class="pg" data-p="msg" hidden><h4>消息</h4><div class="ms">${critter(0, 40)}<div class="tx"><b>系统通知</b><p>你的订单已发货，预计明天送达</p></div></div><div class="ms">${critter(1, 40)}<div class="tx"><b>优惠中心</b><p>满 99 减 20 券已到账</p></div></div><div class="ms">${critter(2, 40)}<div class="tx"><b>客服小助手</b><p>您的售后申请已受理</p></div></div><p class="tip">进入消息页后，消息角标自动清除</p></div>
<div class="pg" data-p="cart" hidden><h4>购物车</h4><div class="cart"><b data-n>2</b>件商品<span>角标和这里的数量保持一致</span></div></div>
<div class="pg" data-p="me" hidden><h4>我的</h4><div class="me">${critter(3, 48)}<div><b>林小满</b><p>金卡会员</p></div></div><p class="tip">进入“我的”后，小红点自动清除</p></div></div>
<div class="tb" role="tablist">${T.map(([k, ic, t, b], i) => `<button type="button" data-k="${k}" class="${i === 0 ? 'on' : ''}" role="tab" aria-selected="${i === 0}"><span class="ic">${sv(ic)}${b ? `<i class="bg ${b === 'dot' ? 'dot' : ''}" data-b="${k}">${b === 'dot' ? '' : b}</i>` : ''}</span>${t}</button>`).join('')}</div></div>`
  },
  js: (root) => {
    const cnt = { msg: 3, cart: 2 }
    const bg = (k) => q1(root, `[data-b=${k}]`)
    const sync = (k) => { const b = bg(k); if (!b) return; b.hidden = !cnt[k]; b.textContent = cnt[k] > 99 ? '99+' : cnt[k]; if (k === 'cart') q1(root, '[data-n]').textContent = cnt.cart }
    const go = (k) => {
      qa(root, '.tb button').forEach((b) => { b.classList.toggle('on', b.dataset.k === k); b.setAttribute('aria-selected', b.dataset.k === k) })
      qa(root, '.pg').forEach((p) => { p.hidden = p.dataset.p !== k })
      if (k === 'msg') later(root, 500, () => { cnt.msg = 0; sync('msg') })
      if (k === 'me') later(root, 500, () => { const d = bg('me'); if (d) d.hidden = true })
    }
    root.addEventListener('click', (e) => {
      const t = e.target.closest('.tb button'); if (t) { go(t.dataset.k); return }
      if (e.target.closest('.adc')) { cnt.cart++; sync('cart'); const b = bg('cart'); b.style.animation = 'none'; void b.offsetWidth; b.style.animation = ''; IX.toast(root, '已加入购物车') }
    })
  },
})
/* ───────── BTN 按钮 ───────── */
def({
  id: 'MP-BTN-009', name: '底部悬浮操作栏', style: '三种布局',
  fit: '订单确认、预约提交、待付款这类页面底部的固定操作区；三种布局按场景选，主按钮在右、次按钮在左',
  avoid: '页面里已经有底部标签栏时（叠在一起，改放在内容里）；一栏里放三个以上按钮',
  kw: '底部栏 操作栏 悬浮 固定 提交订单 去支付 价格栏 主次按钮 协议勾选',
  stage: 'white',
  css: CSS('mpbtn009', `${SCR(380)}& .pg{padding:12px}& .sgm{display:flex;padding:3px;border-radius:14px;background:var(--n5)}& .sgm button{flex:1;height:36px;border-radius:11px;font-size:14px;color:var(--ink2);position:relative}& .sgm button::after{content:"";position:absolute;inset:-4px -1px}& .sgm button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:0 2px 8px var(--sh14)}& .cd{margin-top:10px;padding:14px;border-radius:16px;background:var(--card);box-shadow:0 4px 14px var(--sh06)}& .cd .pr{display:flex;gap:12px}& .cd img{width:64px;height:64px;border-radius:12px;object-fit:cover;flex:none}& .cd .pr>div>b{display:block;font-size:16px;line-height:22px;font-weight:600}& .cd small{font-size:12px;line-height:16px;color:var(--ink3)}& .cd .ln{display:flex;justify-content:space-between;margin-top:10px;padding-top:10px;border-top:1px solid var(--line);font-size:14px;color:var(--ink2)}& .bar2{position:absolute;left:0;right:0;bottom:0;z-index:3;padding:10px 14px 14px;background:var(--card);box-shadow:0 -6px 20px var(--sh08)}& .row{display:flex;align-items:center;gap:10px}& .row button{height:44px;border-radius:22px;font-size:16px;font-weight:600;white-space:nowrap}& .bm{flex:1;background:var(--card);box-shadow:inset 0 0 0 1px var(--n8);color:var(--ink)}& .bp{flex:1.4;${PRIMARY}}& .bp:active,& .bm:active{transform:scale(.98)}& .sum{flex:1;min-width:0}& .sum span{display:block;font-size:12px;line-height:16px;color:var(--ink3)}& .sum .price b{font-size:22px}& .row .bp.fx{flex:none;width:128px}& .ag{display:flex;align-items:center;gap:8px;margin-bottom:10px;font-size:12px;line-height:18px;color:var(--ink2);cursor:pointer}& .ck{position:relative;flex:none;width:18px;height:18px;border-radius:50%;border:1.5px solid var(--n10);display:flex;align-items:center;justify-content:center;color:transparent;transition:background-color .15s,border-color .15s}& .ck::after{content:"";position:absolute;inset:-13px}& .ck span{display:inline-flex;width:12px;height:12px}& .ck.on{background:var(--p);border-color:var(--p);color:#fff}& .ag a{color:var(--p-text);font-weight:600}& .ag.er{color:${DANGER}}& .bp.dis{opacity:.5;box-shadow:none}& .row .bp.full{flex:1}`),
  html: () => `<div class="mpbtn009"><div class="nb">订单确认</div><div class="pg"><div class="sgm" data-ix="tabs" data-g="b9" role="tablist"><button class="on" type="button" data-t="a" role="tab">双按钮</button><button type="button" data-t="b" role="tab">价格栏</button><button type="button" data-t="c" role="tab">协议确认</button></div>
<div class="cd"><div class="pr"><img src="${P(5)}" alt=""><div><b>护眼台灯</b><small>无频闪 · 三档调光 × 1</small><div style="margin-top:4px">${priceHTML(219, 0)}</div></div></div><div class="ln"><span>商品合计</span><span>¥219.00</span></div></div></div>
<div class="bar2" data-p="a" data-g="b9"><div class="row"><button class="bm" type="button" data-t2="取消订单">取消订单</button><button class="bp" type="button" data-t2="去支付">去支付</button></div></div>
<div class="bar2" data-p="b" data-g="b9" hidden><div class="row"><div class="sum"><span class="price"><small>¥</small><b>219</b></span><span>已优惠 ¥31，含运费 ¥0</span></div><button class="bp fx" type="button" data-t2="提交订单">提交订单</button></div></div>
<div class="bar2" data-p="c" data-g="b9" hidden><div class="ag"><span class="ck" role="checkbox" aria-checked="false"><span>${sv('check')}</span></span><span>我已阅读并同意<a>《服务协议》</a></span></div><div class="row"><button class="bp full dis" type="button" data-t2="立即预约" aria-disabled="true">立即预约</button></div></div></div>`,
  js: (root) => {
    const ag = q1(root, '.ag'), ck = q1(root, '.ck'), cb = q1(root, '[data-p=c] .bp')
    ag.addEventListener('click', (e) => { if (e.target.closest('a')) return; const on = ck.classList.toggle('on'); ck.setAttribute('aria-checked', on); ag.classList.remove('er'); cb.classList.toggle('dis', !on); cb.setAttribute('aria-disabled', !on) })
    root.addEventListener('click', (e) => {
      const b = e.target.closest('.row button'); if (!b) return
      if (b.getAttribute('aria-disabled') === 'true') { ag.classList.add('er'); IX.toast(root, '请先勾选并同意服务协议'); return }
      IX.toast(root, { 取消订单: '订单已取消', 去支付: '正在拉起支付…', 提交订单: '订单已提交', 立即预约: '预约成功' }[b.dataset.t2])
    })
  },
})

def({
  id: 'MP-BTN-010', name: '按钮组防重复提交', style: '加载防重复',
  fit: '提交、保存、支付这类会请求接口的按钮组；点击即进入加载并禁用整组，成功后短暂显示结果，失败原位写原因并可重试',
  avoid: '不会请求接口的跳转按钮（不需要加载态）；加载时把文字换成更长的文案导致按钮变宽',
  kw: '防重复 加载 loading 提交 保存 按钮组 成功 失败 重试 禁用',
  css: CSS('mpbtn010', `&{width:340px;background:var(--card);border-radius:22px;padding:20px 18px 18px;box-shadow:${SHADOW}}& h4{margin:0;font-size:18px;line-height:26px;font-weight:600}& .sub{margin:2px 0 14px;font-size:14px;line-height:20px;color:var(--ink2)}& .fm{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-radius:12px;background:var(--n3);font-size:14px;color:var(--ink2)}& .fm b{font-weight:600;color:var(--ink)}& .grp{display:flex;gap:10px;margin-top:16px}& .grp button{height:44px;border-radius:22px;font-size:16px;font-weight:600;display:flex;align-items:center;justify-content:center;gap:8px;white-space:nowrap;transition:background-color .2s,opacity .2s,transform .15s cubic-bezier(.2,0,0,1)}& .cnl{flex:1;background:var(--pt);color:var(--p-text)}& .sv{flex:1.5;${PRIMARY}}& .sv:active:not(:disabled),& .cnl:active:not(:disabled){transform:scale(.98)}& .sv.busy{cursor:progress}& .sv.ok{background:var(--ok-fill);box-shadow:none}& .cnl:disabled{opacity:.45;cursor:default}& .sv svg{width:20px;height:20px}${SPIN('mpbtn010', '& .sp', 18)}& .er{display:none;align-items:center;gap:8px;margin-top:12px;padding:10px 12px;border-radius:12px;background:var(--danger-bg);color:${DANGER};font-size:14px;line-height:20px}& .er.show{display:flex}& .er span{display:inline-flex;flex:none;width:18px;height:18px}& .er em{flex:1}& .er button{position:relative;font-weight:600;color:${DANGER};text-decoration:underline;text-underline-offset:3px}& .er button::after{content:"";position:absolute;inset:-12px -6px}& .ft{display:flex;align-items:center;justify-content:space-between;margin-top:14px;padding-top:14px;border-top:1px solid var(--line);font-size:14px;color:var(--ink2)}& .ft small{display:block;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}${SWT('mpbtn010b')}`),
  html: () => `<div class="mpbtn010"><h4>修改绑定手机号</h4><p class="sub">保存后，下次登录请使用新手机号</p><div class="fm"><span>新手机号</span><b>138 0013 8000</b></div>
<div class="grp"><button class="cnl" type="button">取消</button><button class="sv" type="button">保存修改</button></div>
<div class="er" role="alert"><span>${sv('alert')}</span><em>保存失败：网络异常，请检查网络后重试</em><button type="button">重试</button></div>
<div class="ft"><div>模拟网络失败<small data-cnt>已拦截 0 次重复点击</small></div><span class="swt" data-ix="toggle" role="switch" aria-checked="false" aria-label="模拟网络失败"><i></i></span></div></div>`,
  js: (root) => {
    const sv_ = q1(root, '.sv'), cn = q1(root, '.cnl'), er = q1(root, '.er'), cnt = q1(root, '[data-cnt]'), sw = q1(root, '.swt')
    let busy = false, n = 0
    const go = () => {
      if (busy) { n++; cnt.textContent = `已拦截 ${n} 次重复点击`; return } /* 加载中：直接忽略，不重复发请求 */
      busy = true; er.classList.remove('show'); sv_.classList.add('busy'); cn.disabled = true; sv_.innerHTML = '<span class="sp"></span>保存中'
      later(root, 1400, () => {
        busy = false; sv_.classList.remove('busy'); cn.disabled = false
        if (sw.classList.contains('on')) { sv_.textContent = '保存修改'; er.classList.add('show'); return }
        sv_.classList.add('ok'); sv_.innerHTML = sv('check') + '已保存'; IX.toast(root, '手机号已更新')
        later(root, 1400, () => { sv_.classList.remove('ok'); sv_.textContent = '保存修改' })
      })
    }
    sv_.addEventListener('click', go); q1(er, 'button').addEventListener('click', go)
    cn.addEventListener('click', () => IX.toast(root, '已取消修改'))
  },
})

def({
  id: 'MP-BTN-011', name: '滑动确认按钮', style: '拖动确认',
  fit: '确认收货、确认转账、删除账号这类不可撤销的重要操作；比弹窗二次确认更不容易误触，也更有仪式感',
  avoid: '高频操作（每次都要拖很累）；需要无障碍或单手难操作的主流程（保留普通按钮）',
  kw: '滑动确认 滑块 slide confirm 确认收货 转账 拖动 右滑 防误触',
  css: CSS('mpbtn011', `&{width:340px;background:var(--card);border-radius:22px;padding:20px 20px 22px;box-shadow:${SHADOW}}& h4{margin:0;font-size:18px;line-height:26px;font-weight:600}& .sub{margin:4px 0 16px;font-size:14px;line-height:20px;color:var(--ink2)}& .od{display:flex;gap:12px;align-items:center;padding:10px;border-radius:14px;background:var(--n3)}& .od img{width:48px;height:48px;border-radius:10px;object-fit:cover;flex:none}& .od b{display:block;font-size:14px;line-height:20px;font-weight:600}& .od small{font-size:12px;color:var(--ink3)}& .trk{position:relative;height:52px;margin-top:18px;border-radius:26px;background:var(--soft);overflow:hidden;user-select:none;--x:0px}& .fil{position:absolute;left:0;top:0;bottom:0;width:calc(var(--x) + 48px);border-radius:26px;background:var(--pm);transition:background-color .25s}& .lbl{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding-left:34px;font-size:16px;font-weight:600;color:var(--ink2);opacity:calc(1 - var(--x-p,0) * 1.6);pointer-events:none}& .lbl::after{content:"";position:absolute;inset:0;background:linear-gradient(100deg,transparent 35%,color-mix(in srgb,var(--card) 80%,transparent) 50%,transparent 65%);transform:translateX(-100%);animation:@@sh 2.4s ease-in-out infinite}@keyframes @@sh{60%,100%{transform:translateX(100%)}}@media(prefers-reduced-motion:reduce){& .lbl::after{animation:none}}& .thb{position:absolute;left:4px;top:4px;width:44px;height:44px;border-radius:50%;${PRIMARY};display:flex;align-items:center;justify-content:center;cursor:grab;touch-action:none;transform:translateX(var(--x));transition:transform .24s cubic-bezier(.2,0,0,1)}& .trk.drag .thb,& .trk.drag .fil{transition:none;cursor:grabbing}& .thb span{display:inline-flex;width:22px;height:22px}& .trk.ok{background:var(--ok-bg)}& .trk.ok .fil{background:#CFE5D8}& .trk.ok .thb{background:var(--card);color:${OKC};box-shadow:0 4px 12px var(--sh14)}& .trk.ok .lbl{opacity:1;color:${OKT};padding-left:0;padding-right:34px}& .trk.ok .lbl::after{display:none}& .rs{display:block;margin:12px auto 0;height:32px;padding:0 12px;font-size:14px;color:var(--p-text);font-weight:600;position:relative}& .rs::after{content:"";position:absolute;inset:-6px}`),
  html: () => `<div class="mpbtn011"><h4>确认收货</h4><p class="sub">确认后货款将支付给商家，请确认商品无误</p><div class="od"><img src="${P(6)}" alt=""><div><b>保温水杯 · 鼠尾草绿</b><small>订单 SO2026110408 · 实付 ¥89.00</small></div></div>
<div class="trk"><div class="fil"></div><div class="lbl">向右滑动确认收货</div><button class="thb" type="button" role="slider" aria-label="向右滑动确认收货" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span>${sv('mpb_chevs')}</span></button></div><button class="rs" type="button" hidden>重新演示</button></div>`,
  js: (root) => {
    const trk = q1(root, '.trk'), thb = q1(root, '.thb'), lbl = q1(root, '.lbl'), rs = q1(root, '.rs')
    const max = () => trk.clientWidth - 52
    let d = null, x = 0
    const set = (v) => { x = v; trk.style.setProperty('--x', v + 'px'); trk.style.setProperty('--x-p', (v / max()).toFixed(3)); thb.setAttribute('aria-valuenow', Math.round(v / max() * 100)) }
    const confirm = () => { set(max()); trk.classList.add('ok'); lbl.textContent = '已确认收货'; thb.innerHTML = `<span>${sv('check')}</span>`; thb.setAttribute('aria-label', '已确认'); rs.hidden = false; IX.toast(root, '已确认收货') }
    thb.addEventListener('pointerdown', (e) => { if (trk.classList.contains('ok')) return; d = { x0: e.clientX, v0: x }; trk.classList.add('drag'); thb.setPointerCapture(e.pointerId) })
    thb.addEventListener('pointermove', (e) => { if (d) set(clamp(d.v0 + e.clientX - d.x0, 0, max())) })
    const end = () => { if (!d) return; d = null; trk.classList.remove('drag'); if (x >= max() * 0.9) confirm(); else set(0) }
    thb.addEventListener('pointerup', end); thb.addEventListener('pointercancel', end)
    thb.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowRight') { e.preventDefault(); if (!trk.classList.contains('ok')) confirm() } })
    rs.addEventListener('click', () => { trk.classList.remove('ok'); lbl.textContent = '向右滑动确认收货'; thb.innerHTML = `<span>${sv('mpb_chevs')}</span>`; thb.setAttribute('aria-label', '向右滑动确认收货'); rs.hidden = true; set(0) })
    set(0)
  },
})
/* ───────── CARD 卡片 ───────── */
def({
  id: 'MP-CARD-010', name: '品牌店铺卡', style: '封面与关注',
  fit: '品牌馆、店铺列表、关注页；一张卡讲清“这是谁、靠谱吗、卖什么”，关注可直接点',
  avoid: '没有真实粉丝和好评数据时（不要编造数字）；一屏连续排多张（每张都很高）',
  kw: 'brand 品牌卡 店铺卡 品牌馆 关注 粉丝 认证 好评率 shop',
  css: CSS('mpcard010', `&{width:340px;background:var(--card);border-radius:22px;overflow:hidden;box-shadow:${SHADOW}}& .cv{height:92px;background-size:cover;background-position:center}& .cv::after{content:"";display:block;height:100%;background:linear-gradient(180deg,rgba(var(--p-rgb),.38),rgba(var(--p-rgb),.06))}& .hd{display:flex;align-items:flex-end;justify-content:space-between;padding:0 18px;margin-top:-30px}& .lg{display:flex;align-items:center;justify-content:center;width:64px;height:64px;border-radius:50%;background:var(--pt);color:var(--p-text);box-shadow:0 0 0 4px var(--card),0 6px 14px var(--sh12)}& .lg span{display:inline-flex;width:30px;height:30px}& .fw{position:relative;height:36px;min-width:84px;padding:0 16px;border-radius:18px;${PRIMARY};box-shadow:none;font-size:14px;font-weight:600;transition:background-color .2s,color .2s}& .fw::after{content:"";position:absolute;inset:-4px -2px}& .fw.on{background:var(--pt);color:var(--p-text)}& .bd{padding:10px 18px 0}& .nm{display:flex;align-items:center;gap:8px}& .nm b{font-size:18px;line-height:26px;font-weight:600}& .vf{display:inline-flex;align-items:center;gap:2px;height:20px;padding:0 6px;border-radius:5px;background:var(--pt);color:var(--p-text);font-size:12px;font-weight:600}& .vf span{display:inline-flex;width:12px;height:12px}& .slg{margin:4px 0 0;font-size:14px;line-height:20px;color:var(--ink2)}& .st3{display:grid;grid-template-columns:repeat(3,1fr);margin:14px 0 0;padding:12px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);text-align:center}& .st3 div+div{border-left:1px solid var(--line)}& .st3 b{display:block;font-size:18px;line-height:24px;font-weight:600;font-variant-numeric:tabular-nums}& .st3 small{font-size:12px;color:var(--ink3)}& .pl{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:14px 18px 18px}& .pl button{text-align:left}& .pl img{width:100%;aspect-ratio:1;border-radius:12px;object-fit:cover}& .pl .nmx{display:block;margin-top:6px;font-size:14px;line-height:20px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}& .pl .price b{font-size:16px}`),
  html: () => `<div class="mpcard010"><div class="cv" style="background-image:url(${ASSETS.bg.silk})"></div>
<div class="hd"><span class="lg"><span>${sv('mpb_store')}</span></span><button class="fw" type="button" aria-pressed="false">关注</button></div>
<div class="bd"><div class="nm"><b>示例品牌旗舰店</b><span class="vf"><span>${sv('mpb_verified')}</span>官方认证</span></div><p class="slg">专注桌面与出行好物，2018 年创立</p>
<div class="st3"><div><b data-fans>12,386</b><small>粉丝</small></div><div><b>218</b><small>在售商品</small></div><div><b>99%</b><small>好评率</small></div></div></div>
<div class="pl">${[0, 1, 5].map((i) => `<button type="button" data-n="${PRODUCTS[i].n}"><img src="${P(i)}" alt=""><span class="nmx">${PRODUCTS[i].n}</span><span class="price"><small>¥</small><b>${PRODUCTS[i].p}</b></span></button>`).join('')}</div></div>`,
  js: (root) => {
    const fw = q1(root, '.fw'), fans = q1(root, '[data-fans]'); let n = 12386
    fw.addEventListener('click', () => { const on = fw.classList.toggle('on'); fw.setAttribute('aria-pressed', on); fw.textContent = on ? '已关注' : '关注'; n += on ? 1 : -1; fans.textContent = n.toLocaleString('en-US'); IX.toast(root, on ? '已关注，上新会通知你' : '已取消关注') })
    qa(root, '.pl button').forEach((b) => b.addEventListener('click', () => IX.toast(root, `查看：${b.dataset.n}`)))
  },
})

def({
  id: 'MP-CARD-011', name: '优惠套餐卡', style: '组合价',
  fit: '组合购买、套餐、礼盒；用缩略图 + 号讲清“包含什么”，规格切换后价格和省多少同步变化，明细默认收起',
  avoid: '组合里只有一件商品（用标准商品卡）；省下的金额不真实或原价是虚高的',
  kw: '套餐 组合 优惠 三件套 礼盒 combo bundle 立省 规格 展开明细',
  css: CSS('mpcard011', `&{width:340px;background:var(--card);border-radius:22px;padding:18px 18px 16px;box-shadow:${SHADOW}}& .hd{display:flex;align-items:center;gap:8px}& .hd b{font-size:18px;line-height:26px;font-weight:600}& .sub{margin:2px 0 14px;font-size:14px;line-height:20px;color:var(--ink2)}& .pics{display:flex;align-items:center;gap:6px;padding:12px;border-radius:16px;background:var(--n3)}& .pics img{width:74px;height:74px;border-radius:12px;object-fit:cover;flex:none}& .pics i{display:inline-flex;align-items:center;justify-content:center;flex:none;width:18px;height:18px;border-radius:50%;background:var(--card);color:var(--ink2);box-shadow:0 1px 4px var(--sh12)}& .pics i span{display:inline-flex;width:12px;height:12px}& .sp{display:flex;gap:8px;margin:14px 0 4px}& .sp button{position:relative;height:36px;padding:0 16px;border-radius:18px;background:var(--soft);font-size:14px;color:var(--ink2);transition:background-color .15s}& .sp button::after{content:"";position:absolute;inset:-4px -2px}& .sp .on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1.5px var(--p)}& .pr{display:flex;align-items:flex-end;justify-content:space-between;margin-top:12px}& .pr .l{display:flex;align-items:baseline;gap:6px}& .pr .price b{font-size:32px;line-height:36px;font-weight:700}& .pr .price small{font-size:16px}& .sv{display:inline-flex;align-items:center;height:22px;padding:0 8px;border-radius:5px;background:var(--danger-bg);color:var(--danger-ink);font-size:12px;font-weight:600}& .sd{font-size:12px;color:var(--ink3)}& .ix-ai>[data-h]{display:flex;align-items:center;justify-content:space-between;width:100%;height:44px;margin-top:6px;font-size:14px;color:var(--ink2);text-align:left}& .ix-ai>[data-h] span{display:inline-flex;width:16px;height:16px;transition:transform .22s cubic-bezier(.2,0,0,1)}& .ix-ai.open>[data-h] span{transform:rotate(180deg)}& .dl{display:flex;flex-direction:column;gap:8px;padding:2px 0 10px}& .dl div{display:flex;justify-content:space-between;font-size:14px;line-height:20px;color:var(--ink2)}& .dl b{font-weight:400;color:var(--ink);font-variant-numeric:tabular-nums}& .go{width:100%;height:48px;margin-top:4px;border-radius:24px;font-size:16px;font-weight:600;${PRIMARY}}& .go:active{transform:scale(.98)}`),
  html: () => `<div class="mpcard011"><div class="hd"><b>桌面好物三件套</b><span class="tg tg-hot">限时组合价</span></div><p class="sub">护眼台灯 + 保温水杯 + 陶瓷马克杯</p>
<div class="pics"><img src="${P(5)}" alt=""><i><span>${sv('plus')}</span></i><img src="${P(6)}" alt=""><i><span>${sv('plus')}</span></i><img src="${P(2)}" alt=""></div>
<div class="sp" role="radiogroup"><button class="on" type="button" role="radio" aria-checked="true" data-p="299" data-o="367">标准版</button><button type="button" role="radio" aria-checked="false" data-p="319" data-o="387">礼盒版 + ¥20</button></div>
<div class="pr"><div class="l"><span class="price"><small>¥</small><b data-p>299</b></span><span class="strike">¥<span data-o>367</span></span><span class="sv">立省 ¥<span data-s>68</span></span></div><span class="sd">已售 1,286 套</span></div>
<div data-ix="acc"><div class="ix-ai"><button type="button" data-h>查看套餐明细（3 件）<span>${sv('down')}</span></button><div class="ix-ab"><div><div class="dl"><div>护眼台灯 × 1<b>¥219</b></div><div>保温水杯 × 1<b>¥89</b></div><div>陶瓷马克杯 × 1<b>¥59</b></div><div class="gift" hidden>礼盒包装 × 1<b>¥20</b></div></div></div></div></div></div>
<button class="go" type="button">立即抢购</button></div>`,
  js: (root) => {
    const chips = qa(root, '.sp button'), gift = q1(root, '.gift')
    chips.forEach((c) => c.addEventListener('click', () => {
      chips.forEach((x) => { x.classList.toggle('on', x === c); x.setAttribute('aria-checked', x === c) })
      const p = +c.dataset.p, o = +c.dataset.o
      q1(root, '[data-p]:not(button)').textContent = p; q1(root, '[data-o]:not(button)').textContent = o; q1(root, '[data-s]').textContent = o - p; gift.hidden = c.dataset.p === '299'
    }))
    q1(root, '.go').addEventListener('click', () => IX.toast(root, '已进入下单页'))
  },
})

def({
  id: 'MP-CARD-012', name: '规格对比卡', style: '两列对比',
  fit: '同类商品或套餐二选一：同一行直接对比，更优的一项打勾，可以只看差异；点整列选择，底部一个主按钮确认',
  avoid: '超过三个对象（改成对比表页面）；两边差别很小时（对比没意义，直接选规格）',
  kw: '对比 比较 规格对比 参数对比 二选一 compare 只看差异 两款',
  css: CSS('mpcard012', `&{width:340px;background:var(--card);border-radius:22px;padding:16px 14px 16px;box-shadow:${SHADOW}}& .tp{display:flex;align-items:center;justify-content:space-between;padding:0 4px 12px;font-size:14px;color:var(--ink2)}& .tp b{font-size:16px;font-weight:600;color:var(--ink)}& .df{display:flex;align-items:center;gap:8px;font-size:14px;color:var(--ink2)}& .swt{position:relative;flex:none;width:44px;height:26px;border-radius:13px;background:var(--n8);cursor:pointer;transition:background-color .2s}& .swt::after{content:"";position:absolute;inset:-9px -3px}& .swt i{position:absolute;left:3px;top:3px;width:20px;height:20px;border-radius:50%;background:var(--card);box-shadow:0 2px 6px rgba(0,0,0,.2);transition:transform .2s cubic-bezier(.2,0,0,1)}& .swt.on{background:var(--p)}& .swt.on i{transform:translateX(18px)}& .cmp{display:grid;grid-template-columns:52px 1fr 1fr;gap:0 6px}& .cmp>*{min-width:0}& .col{display:flex;flex-direction:column;border-radius:16px;transition:background-color .2s,box-shadow .2s}& .col.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p)}& .ph2{position:relative;display:flex;flex-direction:column;align-items:center;gap:4px;height:116px;padding:12px 8px 8px;text-align:center}& .ph2 img{width:72px;height:72px;border-radius:12px;object-fit:cover}& .ph2 b{font-size:14px;line-height:20px;font-weight:600}& .rd{position:absolute;right:8px;top:8px;width:20px;height:20px;border-radius:50%;border:1.5px solid var(--n10);background:var(--card);display:flex;align-items:center;justify-content:center;color:transparent;transition:background-color .15s,border-color .15s}& .rd span{display:inline-flex;width:12px;height:12px}& .col.on .rd{background:var(--p);border-color:var(--p);color:#fff}& .lbs{display:flex;flex-direction:column}& .lbs .hd{height:116px}& .c{display:flex;align-items:center;justify-content:center;gap:4px;height:44px;padding:0 4px;font-size:14px;line-height:18px;color:var(--ink);text-align:center;border-top:1px solid var(--line)}& .lbs .c{justify-content:flex-start;color:var(--ink3);font-size:12px}& .col .c.best{font-weight:600;color:var(--p-text)}& .c span{display:inline-flex;flex:none;width:14px;height:14px;color:var(--p-fg)}& .c[hidden]{display:none}& .go{width:100%;height:48px;margin-top:14px;border-radius:24px;font-size:16px;font-weight:600;${PRIMARY}}& .go:active{transform:scale(.98)}`),
  html: () => {
    const R = [['容量', '500ml', '350ml', 'a'], ['材质', '304 不锈钢', '手作陶瓷', ''], ['保温', '12 小时', '不保温', 'a'], ['重量', '280g', '360g', 'a'], ['杯盖', '带密封盖', '带密封盖', 'same'], ['价格', '¥89', '¥69', 'b']]
    const cell = (v, w, me) => `<div class="c ${w === me ? 'best' : ''}" data-same="${w === 'same'}">${w === me ? `<span>${sv('check')}</span>` : ''}${v}</div>`
    return `<div class="mpcard012"><div class="tp"><b>保温杯 · 二选一</b><label class="df">只看差异<span class="swt" role="switch" aria-checked="false" aria-label="只看差异"><i></i></span></label></div>
<div class="cmp"><div class="lbs"><div class="hd"></div>${R.map((r) => `<div class="c" data-same="${r[3] === 'same'}">${r[0]}</div>`).join('')}</div>
<div class="col on" data-k="a" role="radio" aria-checked="true" tabindex="0"><div class="ph2"><span class="rd"><span>${sv('check')}</span></span><img src="${P(6)}" alt=""><b>保温水杯</b></div>${R.map((r) => cell(r[1], r[3], 'a')).join('')}</div>
<div class="col" data-k="b" role="radio" aria-checked="false" tabindex="0"><div class="ph2"><span class="rd"><span>${sv('check')}</span></span><img src="${P(2)}" alt=""><b>陶瓷马克杯</b></div>${R.map((r) => cell(r[2], r[3], 'b')).join('')}</div></div>
<button class="go" type="button">选择保温水杯</button></div>`
  },
  js: (root) => {
    const cols = qa(root, '.col'), go = q1(root, '.go'), sw = q1(root, '.swt'), NM = { a: '保温水杯', b: '陶瓷马克杯' }
    const pick = (c) => { cols.forEach((x) => { x.classList.toggle('on', x === c); x.setAttribute('aria-checked', x === c) }); go.textContent = `选择${NM[c.dataset.k]}` }
    cols.forEach((c) => { c.addEventListener('click', () => pick(c)); c.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(c) } }) })
    sw.addEventListener('click', () => { const only = sw.classList.toggle('on'); sw.setAttribute('aria-checked', only); qa(root, '.c[data-same=true]').forEach((c) => { c.hidden = only }) })
    go.addEventListener('click', () => IX.toast(root, `已选择${NM[(q1(root, '.col.on') || cols[0]).dataset.k]}`))
  },
})
/* ───────── HDR 头图横幅 ───────── */
def({
  id: 'MP-HDR-007', name: '搜索头与定位', style: '渐变轮播',
  fit: '首页顶部：左上定位可切换区域，下面是搜索框，再下面一块可滑动的活动轮播；主题色铺底，白色内容卡压在上面',
  avoid: '首屏还有别的营销模块时（轮播只留一块）；没有定位业务的小程序（去掉定位）',
  kw: 'header 头图 首页头部 搜索 定位 轮播 banner 渐变头图 区域切换',
  css: CSS('mphdr007', `&{position:relative;width:340px;padding:0 12px 14px;border-radius:24px;background:linear-gradient(165deg,var(--ga),var(--gb) 80%);box-shadow:0 14px 28px rgba(var(--p-rgb),.20)}& .top{display:flex;align-items:center;justify-content:space-between;height:52px}& .lc{display:flex;align-items:center;gap:4px;height:44px;font-size:16px;font-weight:600;color:#fff}& .lc span{display:inline-flex;width:18px;height:18px}& .lc b{font-weight:600}& .lc b+span{width:14px;height:14px}& .loc .menu{min-width:140px;padding:6px;border-radius:14px;background:var(--card2);box-shadow:0 12px 30px var(--sh22)}& .loc .menu div{display:flex;align-items:center;height:40px;padding:0 10px;border-radius:10px;font-size:14px;color:var(--ink);cursor:pointer}& .loc .menu div:hover{background:var(--n3)}& .loc .menu div.on{color:var(--p-text);font-weight:600;background:var(--pt)}& .wx{width:87px;height:32px}& .wx svg{display:block}& .sr{display:flex;align-items:center;gap:8px;height:44px;padding:0 5px 0 14px;border-radius:22px;background:var(--card);box-shadow:0 6px 16px var(--sh12)}& .sr:focus-within{box-shadow:0 6px 16px var(--sh12),inset 0 0 0 1px var(--ink2)}& .sr>span{display:inline-flex;flex:none;width:20px;height:20px;color:var(--ink3)}& .sr input{flex:1;min-width:0;height:100%;border:0;outline:0;background:none;font:inherit;font-size:14px;color:var(--ink)}& .sr input::placeholder{color:color-mix(in srgb,var(--ink4) 52%,var(--ink3))}& .sr button{flex:none;height:34px;padding:0 16px;border-radius:17px;${PRIMARY};box-shadow:none;font-size:14px;font-weight:600}& .car{margin-top:12px}& .car .ix-track{gap:10px;border-radius:16px}& .sl{display:flex;align-items:center;justify-content:space-between;width:100%;height:96px;padding:0 16px;border-radius:16px;background:var(--card);text-align:left}& .sl.alt{background:var(--pt)}& .sl .tx{display:block;min-width:0}& .sl b{display:block;font-size:18px;line-height:26px;font-weight:600;color:var(--ink)}& .sl small{display:block;margin-top:2px;font-size:12px;line-height:16px;color:var(--ink2)}& .sl .ico{width:64px;height:64px;filter:saturate(.8)}& .sl .ico-line{width:44px;height:44px;stroke:var(--p)}& .dots{display:flex;justify-content:center;gap:6px;margin-top:10px}& .dots i{position:relative;width:6px;height:6px;border-radius:3px;background:color-mix(in srgb,var(--card) 50%,transparent);transition:width .2s cubic-bezier(.2,0,0,1),background-color .2s}& .dots i::after{content:"";position:absolute;inset:-12px -4px}& .dots i.on{width:16px;background:var(--lift)}`),
  html: () => `<div class="mphdr007"><div class="top"><div class="loc" data-ix="dd"><button class="lc" type="button" data-tg aria-label="切换区域"><span>${sv('pin')}</span><b data-label>杭州·西湖区</b><span>${sv('down')}</span></button><div class="menu">${['西湖区', '滨江区', '余杭区', '拱墅区'].map((c, i) => `<div data-o data-v="杭州·${c}" class="${i ? '' : 'on'}">杭州·${c}</div>`).join('')}</div></div><div class="wx" aria-hidden="true" title="微信胶囊占位">${WXCAP}</div></div>
<label class="sr"><span>${sv('search')}</span><input type="search" placeholder="搜索商品、品牌、门店" autocomplete="off" aria-label="搜索"><button type="button">搜索</button></label>
<div class="car" data-ix="carousel" data-auto="3600"><div class="ix-track"><button class="sl" type="button" data-n="新人专享"><span class="tx"><b>新人专享礼</b><small>首单立减 ¥20 · 免运费</small></span>${IC('coupon')}</button><button class="sl alt" type="button" data-n="极速达"><span class="tx"><b>30 分钟极速达</b><small>附近门店直送 · 实时可查</small></span>${IC('scooter')}</button><button class="sl" type="button" data-n="会员日"><span class="tx"><b>会员日 9 折</b><small>每周三 · 叠加满减</small></span>${IC('star')}</button></div><div class="dots"><i></i><i></i><i></i></div></div></div>`,
  js: (root) => {
    const input = q1(root, 'input'), go = () => IX.toast(root, input.value.trim() ? `搜索：${input.value.trim()}` : '请输入搜索内容')
    q1(root, '.sr button').addEventListener('click', go); input.addEventListener('keydown', (e) => { if (e.key === 'Enter') go() })
    let x0 = 0; root.addEventListener('pointerdown', (e) => { x0 = e.clientX }); root.addEventListener('click', (e) => { const s = e.target.closest('.sl'); if (s && Math.abs(e.clientX - x0) < 6) IX.toast(root, `进入：${s.dataset.n}`) })
  },
})

def({
  id: 'MP-HDR-008', name: '个人信息卡头', style: '头像数据格',
  fit: '“我的”页顶部：头像、昵称、等级、签到，下面压一排积分 / 优惠券 / 收藏 / 足迹数据，点哪格进哪页',
  avoid: '没有账号体系的小程序；数据格超过 4 个（改成宫格入口）；头像用文字或首字母',
  kw: 'profile 个人中心 我的 头像 昵称 会员等级 签到 积分 收藏 足迹',
  css: CSS('mphdr008', `&{width:340px}& .hd{padding:0 16px 52px;border-radius:24px;background:linear-gradient(165deg,var(--ga),var(--gb) 80%);color:#fff;box-shadow:0 14px 28px rgba(var(--p-rgb),.20)}& .top{display:flex;align-items:center;justify-content:space-between;height:52px}& .top b{font-size:18px;font-weight:600}& .wx{width:87px;height:32px}& .wx svg{display:block}& .pf{display:flex;align-items:center;gap:14px}& .avw{display:flex;flex:none;border-radius:50%;box-shadow:0 0 0 3px rgba(255,255,255,.92)}& .who{flex:1;min-width:0}& .who b{display:block;font-size:22px;line-height:30px;font-weight:700}& .lv{display:inline-flex;align-items:center;gap:4px;height:22px;padding:0 8px;border-radius:11px;background:rgba(0,0,0,.16);font-size:12px;font-weight:600}& .lv span{display:inline-flex;width:12px;height:12px}& .who small{display:block;margin-top:4px;font-size:12px;opacity:.92}& .sg{position:relative;flex:none;display:flex;align-items:center;gap:4px;height:36px;padding:0 14px;border-radius:18px;background:var(--card);color:var(--p-text);font-size:14px;font-weight:600;transition:background-color .2s,color .2s}& .sg::after{content:"";position:absolute;inset:-4px -2px}& .sg span{display:inline-flex;width:16px;height:16px}& .sg.done{background:rgba(0,0,0,.16);color:#fff;cursor:default}& .stat{position:relative;display:grid;grid-template-columns:repeat(4,1fr);margin:-34px 12px 0;padding:14px 0 12px;border-radius:18px;background:var(--card);box-shadow:0 10px 24px var(--sh10)}& .stat button{position:relative;display:flex;flex-direction:column;align-items:center;gap:2px;min-height:44px}& .stat button+button::before{content:"";position:absolute;left:0;top:6px;bottom:6px;width:1px;background:var(--line)}& .stat b{font-size:22px;line-height:28px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums}& .stat small{font-size:12px;line-height:16px;color:var(--ink3)}`),
  html: () => `<div class="mphdr008"><div class="hd"><div class="top"><b>我的</b><div class="wx" aria-hidden="true" title="微信胶囊占位">${WXCAP}</div></div>
<div class="pf"><span class="avw">${critter(1, 64)}</span><div class="who"><b>林小满</b><span class="lv"><span>${sv('star')}</span>金卡会员</span><small>ID 20260408</small></div><button class="sg" type="button"><span>${sv('calendar')}</span>签到</button></div></div>
<div class="stat">${[['pt', '2,860', '积分'], ['cp', '6', '优惠券'], ['fv', '38', '收藏'], ['ft', '126', '足迹']].map(([k, n, t]) => `<button type="button" data-k="${t}"><b ${k === 'pt' ? 'data-pt' : ''}>${n}</b><small>${t}</small></button>`).join('')}</div></div>`,
  js: (root) => {
    const sg = q1(root, '.sg'), pt = q1(root, '[data-pt]'); let v = 2860
    sg.addEventListener('click', () => {
      if (sg.classList.contains('done')) return
      sg.classList.add('done'); sg.innerHTML = `<span>${sv('check')}</span>已签到`
      const to = v + 5, t0 = performance.now(); const step = (t) => { if (!root.isConnected) return; const k = Math.min(1, (t - t0) / 400); pt.textContent = Math.round(v + (to - v) * k).toLocaleString('en-US'); if (k < 1) requestAnimationFrame(step) }; requestAnimationFrame(step); v = to
      IX.toast(root, '签到成功，积分 +5')
    })
    qa(root, '.stat button').forEach((b) => b.addEventListener('click', () => IX.toast(root, `进入${b.dataset.k}`)))
  },
})

/* ───────── ENT 入口与宫格 ───────── */
def({
  id: 'MP-ENT-008', name: '两行宫格分页金刚区', style: '分页指示点',
  fit: '首页入口超过 10 个：每页最多 2 行、每行 5 个，超出横向分页滑动，底部指示点；最多 3 页，文案不超过 5 个汉字',
  avoid: '入口不到 8 个（直接用 3 × 2 金刚区）；超过 3 页（把低频入口收进“全部”页）；每个入口的文案超过 5 个字',
  kw: '金刚区 宫格 分页 横滑 两行 指示点 入口 swiper 首页入口 菜单',
  css: CSS('mpent008', `&{width:340px;padding:4px 0 14px;border-radius:22px;background:var(--card);box-shadow:${SHADOW}}& .ix-track{gap:0;border-radius:22px}& .pgx{width:100%;display:grid;grid-template-columns:repeat(5,1fr);grid-auto-rows:auto;gap:14px 0;align-content:start;padding:14px 6px 4px}& .cell{display:flex;flex-direction:column;align-items:center;gap:6px;min-height:76px;font-size:12px;line-height:16px;color:var(--ink);white-space:nowrap}& .cell .tile{width:48px;height:48px;transition:transform .15s cubic-bezier(.2,0,0,1)}& .cell:active .tile{transform:scale(.94)}& .dots{display:flex;justify-content:center;gap:6px;margin-top:10px}& .dots i{position:relative;width:6px;height:6px;border-radius:3px;background:var(--n8);transition:width .2s cubic-bezier(.2,0,0,1),background-color .2s}& .dots i::after{content:"";position:absolute;inset:-12px -4px}& .dots i.on{width:16px;background:var(--p)}`),
  html: () => {
    const P1 = [['bag', '新品首发'], ['star', '会员日'], ['giftbox', '礼品馆'], ['scooter', '极速达'], ['pin', '附近好店'], ['giftcard', '礼卡专区'], ['coupon', '领券中心'], ['wallet', '储值有礼'], ['heart', '心愿清单'], ['cart', '凑单专区']]
    const P2 = [['bag', '品牌馆'], ['giftbox', '生日礼'], ['scooter', '同城送'], ['pin', '门店自提'], ['star', '积分兑换'], ['heart', '好物推荐'], ['wallet', '企业采购'], ['coupon', '满减专区']]
    const pg = (l) => `<div class="pgx">${l.map(([n, t]) => `<button class="cell" type="button" data-n="${t}">${tileHTML(n, 'sq')}<span>${t}</span></button>`).join('')}</div>`
    return `<div class="mpent008" data-ix="carousel"><div class="ix-track">${pg(P1)}${pg(P2)}</div><div class="dots" aria-label="分页指示"><i></i><i></i></div></div>`
  },
  js: (root) => {
    let x0 = 0
    root.addEventListener('pointerdown', (e) => { x0 = e.clientX })
    root.addEventListener('click', (e) => { const c = e.target.closest('.cell'); if (c && Math.abs(e.clientX - x0) < 6) IX.toast(root, `进入：${c.dataset.n}`) })
  },
})

def({
  id: 'MP-ENT-009', name: '角标入口宫格', style: '三种角标',
  fit: '我的页、工作台的入口：有未处理事项的入口挂数字或红点，营销入口挂“新”“热”，点开后数字和红点消失；未上线的入口置灰',
  avoid: '给每个入口都挂角标（等于都没挂）；用角标做营销推销，红点只给“有事要处理”',
  kw: '角标 红点 数字角标 未读 badge 入口 宫格 待处理 置灰 入口提醒',
  css: CSS('mpent009', `&{width:340px;display:grid;grid-template-columns:repeat(4,1fr);gap:18px 0;padding:18px 4px 14px;border-radius:22px;background:var(--card);box-shadow:${SHADOW}}& .cell{display:flex;flex-direction:column;align-items:center;gap:6px;min-height:44px;font-size:12px;line-height:16px;color:var(--ink);white-space:nowrap}& .cell .tile{transition:transform .15s cubic-bezier(.2,0,0,1)}& .cell:active .tile{transform:scale(.94)}& .cell.off{color:var(--ink3)}& .cell.off .tile{filter:grayscale(1);opacity:.55}& .bd{position:absolute;right:-6px;top:-6px;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--danger-fill);color:#fff;font-size:12px;line-height:18px;font-weight:600;text-align:center;box-shadow:0 0 0 2px var(--card);animation:@@pop .22s cubic-bezier(.2,0,0,1)}& .bd.dot{right:-2px;top:-2px;min-width:0;width:10px;height:10px;padding:0;border-radius:50%}& .bd.tx{right:-10px;background:var(--p)}@keyframes @@pop{from{transform:scale(.4)}}`),
  html: () => {
    const E = [['coupon', '优惠券', '2'], ['cart', '购物车', '12'], ['giftbox', '礼品馆', '新'], ['scooter', '极速达', 'dot'], ['star', '会员日', '热'], ['pin', '附近好店', ''], ['giftcard', '礼卡专区', 'off'], ['wallet', '储值有礼', '']]
    return `<div class="mpent009">${E.map(([n, t, b]) => `<button class="cell ${b === 'off' ? 'off' : ''}" type="button" data-n="${t}" data-off="${b === 'off'}"><span class="tile tile-sq">${IC(n)}${b && b !== 'off' ? `<i class="bd ${b === 'dot' ? 'dot' : /^\d+$/.test(b) ? '' : 'tx'}">${b === 'dot' ? '' : b}</i>` : ''}</span><span>${t}</span></button>`).join('')}</div>`
  },
  js: (root) => {
    root.addEventListener('click', (e) => {
      const c = e.target.closest('.cell'); if (!c) return
      if (c.dataset.off === 'true') { IX.toast(root, '即将上线，敬请期待'); return }
      const b = q1(c, '.bd'); if (b && (b.classList.contains('dot') || /^\d+$/.test(b.textContent))) b.remove() /* 有事要处理的角标：进入后消失 */
      IX.toast(root, `进入：${c.dataset.n}`)
    })
  },
})

def({
  id: 'MP-ENT-010', name: '服务入口列表卡', style: '图标加状态',
  fit: '服务类小程序的几个主要服务：每行一个入口，写清做什么、现在能不能用；不可用的置灰并说明原因',
  avoid: '入口超过 5 个（改宫格）；状态文案是营销话术（只写“营业中 / 可预约 / 维护中”这类事实）',
  kw: '服务入口 入口卡 服务列表 门店自提 极速配送 状态 营业中 维护中 service',
  css: CSS('mpent010', `&{width:340px;padding:6px 18px 8px;border-radius:22px;background:var(--card);box-shadow:${SHADOW}}& .hd{display:flex;align-items:center;justify-content:space-between;height:48px}& .hd b{font-size:18px;font-weight:600}& .hd button{display:flex;align-items:center;gap:2px;height:44px;font-size:14px;color:var(--ink2)}& .hd button span{display:inline-flex;width:14px;height:14px}& .rw{display:flex;align-items:center;gap:12px;width:100%;min-height:72px;padding:12px 0;border-top:1px solid var(--line);text-align:left;transition:background-color .12s}& .rw:active{background:var(--n2)}& .rw .tile{width:48px;height:48px;border-radius:16px}& .tx{flex:1;min-width:0}& .tx b{display:block;font-size:16px;line-height:22px;font-weight:600}& .tx small{display:block;font-size:12px;line-height:16px;color:var(--ink3)}& .stt{flex:none;display:inline-flex;align-items:center;height:24px;padding:0 8px;border-radius:12px;font-size:12px;font-weight:600}& .stt.ok{background:var(--ok-bg);color:${OKT}}& .stt.in{background:var(--pt);color:var(--p-text)}& .stt.mu{background:var(--soft);color:var(--ink3)}& .ch{display:inline-flex;flex:none;width:16px;height:16px;color:color-mix(in srgb,var(--ink6) 31%,var(--ink5))}& .rw.off .tile{filter:grayscale(1);opacity:.55}& .rw.off b{color:var(--ink3)}`),
  html: () => {
    const R = [['pin', '门店自提', '附近 3 家门店可取', '营业中', 'ok'], ['scooter', '极速配送', '最快 30 分钟送达', '可下单', 'ok'], ['giftbox', '礼品定制', '刻字、贺卡、礼盒包装', '可预约', 'in'], ['giftcard', '礼卡兑换', '在线兑换，次日到账', '维护中', 'mu']]
    return `<div class="mpent010"><div class="hd"><b>常用服务</b><button type="button" data-n="全部服务">全部服务<span>${sv('right')}</span></button></div>${R.map(([n, t, d, s, k]) => `<button class="rw ${k === 'mu' ? 'off' : ''}" type="button" data-n="${t}" data-why="${k === 'mu' ? '系统维护中，预计 22:00 恢复' : ''}">${tileHTML(n, 'sq')}<span class="tx"><b>${t}</b><small>${d}</small></span><span class="stt ${k}">${s}</span><span class="ch">${sv('right')}</span></button>`).join('')}</div>`
  },
  js: (root) => {
    root.addEventListener('click', (e) => { const b = e.target.closest('[data-n]'); if (!b) return; IX.toast(root, b.dataset.why ? b.dataset.why : `进入：${b.dataset.n}`) })
  },
})
/* ───────── 怎么选：每个类别一份，旧行抄过来 + 新行，推荐项都是本类别里真实存在的组件名 ───────── */
guide('mp', 'FORM', [
  ['常规搜索', '搜索栏三种', '圆角胶囊最亲和，内嵌主按钮提高点击率'],
  ['选规格、数量', '步进器与规格选择', '选中态用主色描边加浅底，不要只靠颜色'],
  ['登录、地址、备注这类输入', '输入框与开关', '聚焦只加深边框；出错用红框加一句话原因，别只变色'],
  ['登录、绑定手机', '手机号验证码登录', '验证码按钮写明剩余秒数；缺项在原位提示，不要让登录键无故变灰'],
  ['新增 / 编辑地址', '地址表单与地区选择', '地区用底部弹层逐级选，保存时把缺的项标红并写原因'],
  ['选预约时间、配送时间', '滚轮日期时间选择', '可滑可点，中间高亮条就是当前选择；一列别超过 60 项'],
  ['写评价、晒图、售后凭证', '评价输入框 / 图片上传九宫格', '评价给星级、标签和字数提示；图片要有上传进度、失败重试和封面'],
  ['配送方式、套餐、增值服务', '单选卡与复选卡', '选项带说明和价格，选中态用描边加浅底，合计实时变化'],
  ['通知、隐私、权限设置', '带说明的开关列表', '每项写一句后果说明；失败要回滚并在原位写原因'],
])
guide('mp', 'FB', [
  ['结果反馈', '轻提示 / 轻提示变体', '成功简短、失败写原因多停一会儿；加载中遮住操作；错误细节别只靠轻提示，用原位提示'],
  ['需要二次确认（删除、退款）', '对话框', '写清后果；主按钮放右边'],
  ['选规格、选地址等较长内容', '底部弹层（选规格）', '高度不超过 80%，底部按钮固定'],
  ['从几个动作里选一个', '底部操作菜单', '危险项标红并二次确认，取消键独立放在底部'],
  ['消息、订单这类会更新的列表', '下拉刷新', '拉到阈值前后文案要变，刷新完说明更新了几条'],
  ['商城、服务页的常驻客服入口', '悬浮客服按钮', '可拖到左右边缘吸附；已有底部操作栏的页面别再叠一个'],
  ['公告、网络异常、支付结果', '消息通知条', '公告可滚动可关闭；异常带重试；持续状态不给关闭键，恢复后自己消失'],
])
guide('mp', 'NAV', [
  ['常规页面', '顶栏四种形态 / 标签栏三种形态', '实色顶栏最稳；突出核心动作用凸起中间按钮，想要轻盈用悬浮胶囊'],
  ['图片头部的页面（商品详情）', '悬浮返回胶囊', '返回和回首页做成胶囊压在图上，往下滑变实色；右上角给微信胶囊留位'],
  ['首页顶部要定位和搜索', '搜索导航栏', '定位在左、搜索居中、右侧留出微信胶囊的 87 × 32；聚焦后出联想'],
  ['底部导航要提示未读和待处理', '角标标签栏', '消息用数字、购物车用数量、“我的”用红点；进入后按规则清除，超过 99 显示 99+'],
  ['分类页、频道页的分类较多', '吸顶标签栏 / 侧边分类栏', '6–15 个分类用横滑标签，点谁谁居中；分类特别多时用侧边栏'],
  ['订单状态、内容分类、视图切换', '分段控件与标签页', '超过 6 个选项改用横滑标签'],
  ['预约、认证等分步流程', '步骤导航', '已完成的步骤可点回去改；不能下一步时写明为什么'],
  ['商品筛选', '吸顶排序条', '综合 / 销量 / 价格 / 筛选，选中态要一眼看清'],
])
guide('mp', 'BTN', [
  ['页面里最重要的一个动作', '渐变主按钮', '一屏只放一个，用主色最强的形态'],
  ['次要动作、取消', '浅底与线框按钮', '与主按钮拉开层级，不抢视线'],
  ['商品详情底部购买栏', '分裂按钮', '“加入购物车 | 立即购买”两色并排，一个动作两个意图'],
  ['订单确认、待付款、预约提交的底部栏', '底部悬浮操作栏', '次按钮在左、主按钮在右；要同意协议的把勾选放在按钮上方并写明原因'],
  ['促销、抢购', '立体厚底按钮 / 金色营销按钮', '按下有手感，营销感强；不要和主按钮同屏同强度'],
  ['叠在图片上', '玻璃按钮', '要有稳定的底图；不稳定时改用白底主色字'],
  ['提交、保存、支付等异步动作', '按钮组防重复提交 / 状态按钮', '加载中保持宽度并禁用整组，失败原位写原因可重试，避免重复提交'],
  ['确认收货、转账等不可撤销的操作', '滑动确认按钮', '比弹窗更不容易误触；高频操作不要用，保留普通按钮的替代入口'],
])
guide('mp', 'CARD', [
  ['日常商品列表、电商首页', '标准商品卡 / 横向列表卡', '信息密度高、风格中性，换主题色最容易，是最稳妥的选择'],
  ['内容种草、社区、笔记', '瀑布流内容卡', '图片为主，高度错落形成节奏，适合浏览型场景'],
  ['节日活动、品牌头图', '大图沉浸卡', '情绪强、字少，一屏只放一张，别连续堆叠'],
  ['高客单价、珠宝、品牌店', '暗金奢品卡 / 极简线框卡', '靠留白和克制显出档次，不要放促销标签'],
  ['大促、拼团、拉新', '立体促销卡', '强对比与厚底引导点击，用在首屏一两处，不要整屏都是'],
  ['旅游、生活方式这类要通透感的品牌', '玻璃信息卡', '需要一张好看的底图，文字对比要实测'],
  ['会员权益、积分', '会员卡', '把等级和进度放在一张卡里，一眼看懂离下一级还差多少'],
  ['品牌馆、店铺列表、关注页', '品牌店铺卡', '粉丝、好评率必须是真实数据；关注可以直接点，其余整张卡进入店铺'],
  ['套餐、组合、礼盒', '优惠套餐卡', '用缩略图加号讲清包含什么，省下的钱要真实；明细默认收起'],
  ['同类商品或套餐二选一', '规格对比卡', '最多两列；更优项打勾，可以只看差异；底部只留一个主按钮'],
])
guide('mp', 'HDR', [
  ['首页顶部、需要和主题色统一', '渐变头图 + 商品图', '最常见，改主题色即换整页气质'],
  ['信息偏少、想要干净', '浅色头图 + 大图标', '最稳，几乎不会出错'],
  ['节日、品牌、氛围', '图片背景 + 主题遮罩', '情绪最强；遮罩用主题色保证文字可读'],
  ['高端、通透', '玻璃面板叠图', '底图要好看；文字对比度逐张测'],
  ['多个活动轮流展示', '轮播横幅（露出两侧）', '露出两侧暗示可滑动，第三张以后几乎没人看'],
  ['一屏要放多个活动', '拼贴双栏（一大两小）', '一大两小，主次分明'],
  ['首页顶部要定位和搜索', '搜索头与定位', '定位、搜索、一块活动轮播放进同一块头部；首屏营销模块仍不超过 2 个'],
  ['“我的”页顶部', '个人信息卡头', '头像、等级、签到加四个数据格；头像用卡通动物，不用文字'],
])
guide('mp', 'ENT', [
  ['首页有 6 个业务要分发', '3 × 2 金刚区', '入口数、文案长度和屏宽推导出列数；少于 4 个别凑宫格'],
  ['首页入口超过 10 个', '两行宫格分页金刚区', '每页最多 2 行，超出横向分页并配指示点，最多 3 页，文案不超过 5 个字'],
  ['7–8 个业务入口、偏柔和', '4 + 3 圆形底', '文案很长时圆形装不下'],
  ['入口只有 2–4 个、每个都是重点', '大卡片入口 / 服务入口列表卡', '服务类用列表卡写清做什么、现在能不能用'],
  ['入口上要提示待处理事项', '角标入口宫格', '数字和红点只给“有事要处理”，点开后消失；营销用“新”“热”文字角标'],
  ['二级分类、快捷筛选', '横滑胶囊条', '图标含义不直观时要配文字'],
  ['想要更强品牌感', '无底大图标', '3D 图标本身有体积，不需要底板；线性和扁平图标不适用'],
  ['决定图标和底板风格', '四种图标风格对照 / 图标底的三种背景', '电商食品用真实或 3D，工具金融用扁平，控件位置只用线性；底板渐变最有质感、浅色最稳'],
])
/*__END__*/
/*__END__*/
}
