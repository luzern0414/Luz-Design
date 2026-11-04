/* ===== 小程序 · 内容与社区 CONT / 列表与筛选 LIST / 状态与空态 STATE / 价格补充 PRC（007 起）=====
 * 整个文件包在一个函数里，局部名字不会和别的 blocks 文件冲突；
 * js(root) 钩子自成一体（不引用函数外的辅助），方便按编号单独取用。 */
;(() => {
  /* S：& 换成块的根类名，@@ 换成块名前缀（用于动画名，保证每个块自带自己的 @keyframes） */
  const S = (p, c) => c.replace(/&/g, '.' + p).replace(/@@/g, p)
  Object.assign(LINE, {
    mc_thumb: '<path d="M7.5 10.5V20h-3a1 1 0 0 1-1-1v-7.5a1 1 0 0 1 1-1zM7.5 10.5 11 4.5a1.8 1.8 0 0 1 3.3 1.2l-.5 3.8h4.700a2 2 0 0 1 2 2.300l-1.200 6.500a2.500 2.500 0 0 1-2.500 1.700H7.500"/>',
    mc_wifioff: '<path d="M3 3l18 18M2.500 9.500a14 14 0 0 1 4-2.500M21.500 9.500a14 14 0 0 0-9.500-4M5.500 13a9 9 0 0 1 3-1.900M18.500 13a9 9 0 0 0-3.200-2M9 16.500a4.500 4.500 0 0 1 6 0M12 20h.01"/>',
    mc_nosearch: '<circle cx="11" cy="11" r="6.500"/><path d="m20.500 20.500-4.700-4.700M8.800 8.800l4.400 4.400M13.200 8.800l-4.400 4.400"/>',
    mc_hash: '<path d="M9.500 4 7.500 20M16.500 4l-2 16M4.500 9h16M3.500 15h16"/>',
    mc_live: '<circle cx="12" cy="12" r="2"/><path d="M7.700 7.700a6 6 0 0 0 0 8.600M16.300 7.700a6 6 0 0 1 0 8.600M4.900 4.900a10 10 0 0 0 0 14.200M19.100 4.900a10 10 0 0 1 0 14.200"/>',
    mc_volume: '<path d="M4 9.500v5h3.500l4.500 4v-13l-4.500 4zM15.500 9a4 4 0 0 1 0 6M18 6.500a8 8 0 0 1 0 11"/>',
    mc_bookmark: '<path d="M6.500 4h11v16.500L12 16.500l-5.500 4z"/>',
    mc_signal: '<path d="M5 19v-3M10 19v-6M15 19v-9M20 19V5"/>',
    mc_cards: '<rect x="3.500" y="3.500" width="7" height="9" rx="1.500"/><rect x="13.500" y="3.500" width="7" height="5" rx="1.500"/><rect x="3.500" y="15.500" width="7" height="5" rx="1.500"/><rect x="13.500" y="11.500" width="7" height="9" rx="1.500"/>',
  })
  const I = (n, c = '') => `<i class="i${c ? ' ' + c : ''}">${sv(n)}</i>`
  const ICO = '& .i{display:inline-flex;flex:none;width:16px;height:16px}& .i svg{display:block}'
  const SPIN = '& .spin{display:inline-block;flex:none;width:16px;height:16px;border-radius:50%;border:2px solid rgba(var(--p-rgb),.25);border-top-color:var(--p);animation:@@spin .8s linear infinite}@keyframes @@spin{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){& .spin{animation-duration:2.4s}}'
  const POP = '@keyframes @@pop{0%{transform:scale(1)}40%{transform:scale(1.28)}100%{transform:scale(1)}}'
  const CLAMP = (n) => `display:-webkit-box;-webkit-line-clamp:${n};-webkit-box-orient:vertical;overflow:hidden`
  const CARD = 'background:var(--card);border-radius:22px;box-shadow:0 10px 26px var(--sh08)'
  /* 点赞/收藏按钮：data-ix="like"，点击切换 .on 并 ±1 */
  const LIKE_CSS = `& .lkb{display:inline-flex;align-items:center;justify-content:center;gap:4px;min-width:44px;height:44px;padding:0 8px;color:var(--ink3);font-size:12px;transition:color .15s}& .lkb .i{width:20px;height:20px}& .lkb .i svg{transition:fill .15s}& .lkb b{font-weight:400;font-variant-numeric:tabular-nums}& .lkb.on{color:var(--p-fg)}& .lkb.on .i svg{fill:currentColor}& .lkb.on .i{animation:@@pop .3s cubic-bezier(.2,0,0,1)}${POP}`
  const like = (icon, n, extra = '') => `<button class="lkb${extra ? ' ' + extra : ''}" type="button" data-ix="like" aria-label="${icon === 'heart' ? '喜欢' : icon === 'mc_bookmark' ? '收藏' : '点赞'}">${I(icon)}<b data-n>${n}</b></button>`
  const TAB_INK = '& .tb{position:relative;display:flex;gap:24px;height:48px;border-bottom:1px solid var(--line)}& .tb button{position:relative;height:48px;font-size:16px;color:var(--ink2);transition:color .15s}& .tb button.on{color:var(--ink);font-weight:600}& .tb .ink{position:absolute;bottom:-1px;height:3px;display:flex;justify-content:center;transition:left .25s cubic-bezier(.2,0,0,1),width .25s cubic-bezier(.2,0,0,1)}& .tb .ink::after{content:"";width:20px;height:3px;border-radius:2px;background:linear-gradient(90deg,var(--ga),var(--gb))}'

  /* ================= CONT 内容与社区 ================= */
  guide('mp', 'CONT', [
    ['首页推荐位、专栏头条', '文章卡·大图式', '一张大图加两行标题，信息够用；一屏只放一张，连续排会审美疲劳'],
    ['资讯流、种草笔记流', '文章列表·左图右文 / 信息流瀑布', '资讯要扫读选左图右文（读过变灰）；种草要看图选双列瀑布（点“加载更多”追加）'],
    ['教程短片、直播预热', '视频卡·可播放 / 直播卡·双列', '视频点一下就在卡片里播、进度条可拖；直播中看观看人数、预告点预约，卡内不放两个按钮'],
    ['文章、商品下方的讨论区', '评论列表', '点赞即时变色计数，回复折叠进“展开 N 条”，输入框固定底部'],
    ['兴趣选择、话题订阅', '话题标签云', '热度分三档字号，限选数量并提示，选完才能点“完成”'],
    ['热门榜、销量榜、搜索榜', '内容排行榜', '前三名用淡色徽标强调，其余用数字；日榜周榜月榜切换'],
    ['首页通知、活动提醒', '公告滚动条', '多条短公告纵向轮播，长公告横向滚动，都能关闭；一屏只放一条'],
  ])

  /* MP-CONT-001 */
  def({
    id: 'MP-CONT-001', name: '文章卡·大图式', style: '大图互动',
    fit: '首页推荐位、专栏头条、品牌故事；一张大图加两行标题，信息够用不拥挤',
    avoid: '一屏连续排多张（改用左图右文列表）；封面图质量差或比例不统一时',
    kw: 'article 文章卡 资讯 专栏 大图 封面 点赞 收藏 阅读 推荐',
    css: S('mpcont001', `&{width:340px;${CARD};overflow:hidden}
& .cv{position:relative;aspect-ratio:16/10;overflow:hidden;cursor:pointer;background:var(--ph)}
& .cv img{width:100%;height:100%;object-fit:cover;transition:transform .3s cubic-bezier(.2,0,0,1)}
& .cv:hover img{transform:scale(1.03)}
& .tg1{position:absolute;left:12px;top:12px;height:24px;padding:0 10px;border-radius:12px;background:var(--glass2);color:var(--p-text);font-size:12px;font-weight:600;display:inline-flex;align-items:center}
& .rd{position:absolute;right:12px;bottom:12px;height:24px;padding:0 10px 0 8px;border-radius:12px;background:var(--mask2);color:#fff;font-size:12px;display:inline-flex;align-items:center;gap:4px}
& .bd{padding:14px 16px 0}
& h4{margin:0;font-size:18px;line-height:26px;font-weight:600;cursor:pointer;${CLAMP(2)}}
& p{margin:6px 0 0;font-size:14px;line-height:22px;color:var(--ink2);${CLAMP(2)}}
& .au{display:flex;align-items:center;gap:8px;padding:6px 8px 6px 16px;margin-top:4px}
& .who{flex:1;min-width:0;display:flex;flex-direction:column}
& .who b{font-size:14px;font-weight:600;line-height:20px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .who span{font-size:12px;line-height:18px;color:var(--ink3)}
& .act{display:flex;flex:none}
${LIKE_CSS}${ICO}`),
    html: () => `<div class="mpcont001"><div class="cv" data-toast="进入文章详情"><img src="${P(5)}" alt=""><span class="tg1">选购指南</span><span class="rd">${I('eye')}2.1 万</span></div><div class="bd"><h4 data-toast="进入文章详情">办公桌灯怎么选：看懂色温、显色指数和频闪三个参数</h4><p>从三个参数入手，避开三类常见的坑，再附一份按预算整理的选购清单。</p></div><div class="au">${critter(0, 32)}<div class="who"><b>桌面研究所</b><span>11-02 · 5 分钟读完</span></div><div class="act">${like('mc_thumb', 326)}${like('mc_bookmark', 148)}</div></div></div>`,
  })

  /* MP-CONT-002 */
  const ART = [
    ['通勤耳机怎么选：降噪与续航的取舍', 0, '小满', '评测', '2 小时前', 'new'],
    ['一只好杯子：陶瓷、玻璃还是不锈钢，这篇一次讲清楚材质、容量与清洗的区别', 2, '阿杯', '种草', '昨天', 'fol'],
    ['提升效率的 5 件桌面小物', 5, '桌面控', '清单', '昨天', 'new'],
    ['入门机械腕表，从哪一块开始', 4, '表迷', '指南', '3 天前', 'fol'],
    ['双肩包通勤半年的真实使用记录', 8, '老周', '体验', '4 天前', 'new fol'],
    ['春季跑鞋选购：缓震、支撑与脚型', 1, '跑者笔记', '指南', '5 天前', 'fol'],
  ]
  def({
    id: 'MP-CONT-002', name: '文章列表·左图右文', style: '标签筛选',
    fit: '资讯流、专栏列表、搜索结果；密度高，顶部标签可切换，读过的标题自动变灰',
    avoid: '需要强视觉冲击的专题页（改用大图式）；标题超过两行时只会被截断，写短一点',
    kw: 'article list 文章列表 资讯 左图右文 标签切换 已读 信息流 内容流',
    css: S('mpcont002', `&{width:340px;${CARD};padding:0 16px 4px}
${TAB_INK}
& .list{margin-top:-1px}
& .it{display:flex;gap:12px;padding:14px 0;border-top:1px solid var(--line);cursor:pointer}
& .th{flex:none;width:96px;height:96px;border-radius:12px;overflow:hidden;background:var(--ph)}
& .th img{width:100%;height:100%;object-fit:cover}
& .tx{flex:1;min-width:0;display:flex;flex-direction:column;gap:8px}
& h5{margin:0;font-size:16px;line-height:22px;font-weight:600;color:var(--ink);${CLAMP(2)}}
& .it.rd h5{color:var(--ink3);font-weight:400}
& .meta{margin-top:auto;display:flex;align-items:center;gap:8px;font-size:12px;line-height:20px;color:var(--ink3);min-width:0}
& .meta .tg{height:20px;border-radius:4px;flex:none}
& .meta span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}`),
    html: () => `<div class="mpcont002"><div class="tb" data-ix="tabs" data-list=".list"><button type="button" class="on" data-t="all">推荐</button><button type="button" data-t="new">最新</button><button type="button" data-t="fol">关注</button><i class="ink"></i></div><div class="list">${ART.map(([t, im, au, tag, tm, k]) => `<div class="it" data-k="${k}" data-toast="进入文章详情"><div class="th"><img src="${P(im)}" alt=""></div><div class="tx"><h5>${t}</h5><div class="meta"><span class="tg tg-soft">${tag}</span><span>${au}</span><span>${tm}</span></div></div></div>`).join('')}</div></div>`,
    js: (root) => { root.querySelectorAll('.it').forEach((it) => it.addEventListener('click', () => it.classList.add('rd'))) },
  })

  /* MP-CONT-003 */
  def({
    id: 'MP-CONT-003', name: '视频卡·可播放', style: '进度条',
    fit: '教程、种草、品牌短片；点一下就在卡片里播放，进度条可点可拖，播完能重播',
    avoid: '时长超过 3 分钟的长视频（改跳转详情页）；不要自动带声音播放',
    kw: 'video 视频卡 播放 暂停 进度条 重播 短视频 封面 时长 播放量',
    css: S('mpcont003', `&{width:340px;${CARD};overflow:hidden}
& .vd{position:relative;aspect-ratio:16/9;overflow:hidden;background:#2A2F36;cursor:pointer;user-select:none}
& .vd img{width:100%;height:100%;object-fit:cover;animation:@@kb 12s ease-in-out infinite alternate;animation-play-state:paused}
& .vd[data-st=play] img{animation-play-state:running}
@keyframes @@kb{from{transform:scale(1)}to{transform:scale(1.08)}}
& .shade{position:absolute;inset:0;background:linear-gradient(180deg,color-mix(in srgb,var(--scrim) 18%,transparent),transparent 30%,transparent 55%,color-mix(in srgb,var(--scrim) 55%,transparent))}
& .pc,& .du{position:absolute;height:24px;padding:0 8px;border-radius:12px;background:var(--mask2);color:#fff;font-size:12px;display:inline-flex;align-items:center;gap:4px}
& .pc{left:12px;top:12px}& .du{right:12px;bottom:12px}
& .big{position:absolute;left:50%;top:50%;width:56px;height:56px;margin:-28px 0 0 -28px;border-radius:50%;background:var(--glass2);color:var(--p-text);display:flex;align-items:center;justify-content:center;box-shadow:0 6px 18px var(--sh24);transition:opacity .2s,transform .2s cubic-bezier(.2,0,0,1)}
& .big:active{transform:scale(.94)}
& .big span{display:none;width:24px;height:24px}& .big svg{display:block;fill:currentColor}
& .big .b-play{display:block;margin-left:3px}
& .vd[data-st=pause] .big .b-play{display:block}
& .vd[data-st=play] .big{opacity:0;pointer-events:none}
& .vd[data-st=end] .big .b-play{display:none}& .vd[data-st=end] .big .b-re{display:block}
& .vd[data-st=end] .big .b-re svg{fill:none}
& .ctl{position:absolute;left:0;right:0;bottom:0;display:flex;align-items:center;gap:10px;padding:0 14px 4px;opacity:0;pointer-events:none;transition:opacity .2s;background:linear-gradient(180deg,transparent,color-mix(in srgb,var(--scrim) 60%,transparent))}
& .vd:not([data-st=idle]) .ctl{opacity:1;pointer-events:auto}
& .vd:not([data-st=idle]) .du{opacity:0}
& .tm{flex:none;font-size:12px;color:#fff;font-variant-numeric:tabular-nums;line-height:44px}
& .pg{position:relative;flex:1;height:44px;cursor:pointer;touch-action:none}
& .pg::before{content:"";position:absolute;left:0;right:0;top:50%;height:4px;margin-top:-2px;border-radius:2px;background:color-mix(in srgb,var(--card) 35%,transparent)}
& .pg i{position:absolute;left:0;top:50%;height:4px;margin-top:-2px;width:0;border-radius:2px;background:var(--card)}
& .pg u{position:absolute;top:50%;left:0;width:12px;height:12px;margin:-6px 0 0 -6px;border-radius:50%;background:var(--card);box-shadow:0 1px 4px rgba(0,0,0,.35);text-decoration:none;transition:transform .15s}
& .pg:hover u,& .pg.dr u{transform:scale(1.25)}
& .bd{padding:12px 16px 4px}
& h4{margin:0;font-size:16px;line-height:24px;font-weight:600;${CLAMP(2)}}
& .row{display:flex;align-items:center;gap:8px;margin-top:6px}
& .row .nm{font-size:14px;font-weight:600;line-height:20px}& .row .dt{flex:1;font-size:12px;color:var(--ink3)}
${LIKE_CSS}${ICO}`),
    html: () => `<div class="mpcont003"><div class="vd" data-st="idle"><img src="${P(0)}" alt=""><i class="shade"></i><span class="pc">${I('play')}8.6 万次播放</span><span class="du">00:32</span><button class="big" type="button" aria-label="播放或暂停"><span class="b-play">${sv('play')}</span><span class="b-re">${sv('refresh')}</span></button><div class="ctl"><span class="tm">00:00 / 00:32</span><div class="pg" role="slider" tabindex="0" aria-label="播放进度" aria-valuemin="0" aria-valuemax="32" aria-valuenow="0"><i></i><u></u></div></div></div><div class="bd"><h4>30 秒学会正确佩戴降噪耳机，通勤路上不再漏音</h4><div class="row">${critter(2, 28)}<span class="nm">阿杯</span><span class="dt">3 天前</span>${like('mc_thumb', '2,386')}</div></div></div>`,
    js: (root) => {
      const vd = root.querySelector('.vd'), pg = root.querySelector('.pg'), fill = pg.querySelector('i'), knob = pg.querySelector('u'), tm = root.querySelector('.tm'), total = 32
      let t = 0, st = 'idle', timer = null
      const f = (s) => String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(Math.floor(s % 60)).padStart(2, '0')
      const draw = () => { const p = t / total * 100; fill.style.width = p + '%'; knob.style.left = p + '%'; tm.textContent = f(t) + ' / ' + f(total); pg.setAttribute('aria-valuenow', Math.round(t)); vd.dataset.st = st }
      const tick = () => { if (!root.isConnected) { clearInterval(timer); return } t = Math.min(total, t + 0.1); if (t >= total) { st = 'end'; clearInterval(timer) } draw() }
      const play = () => { if (st === 'end' || t >= total) t = 0; st = 'play'; clearInterval(timer); timer = setInterval(tick, 100); draw() }
      const pause = () => { st = 'pause'; clearInterval(timer); draw() }
      vd.addEventListener('click', (e) => { if (e.target.closest('.ctl')) return; st === 'play' ? pause() : play() })
      const seek = (x) => { const r = pg.getBoundingClientRect(); t = Math.max(0, Math.min(total, (x - r.left) / r.width * total)); if (t >= total) { st = 'end'; clearInterval(timer) } draw() }
      pg.addEventListener('pointerdown', (e) => { e.stopPropagation(); pg.setPointerCapture(e.pointerId); pg.classList.add('dr'); const wasPlay = st === 'play'; if (wasPlay) clearInterval(timer); seek(e.clientX); pg.__w = wasPlay })
      pg.addEventListener('pointermove', (e) => { if (pg.classList.contains('dr')) seek(e.clientX) })
      const up = () => { if (!pg.classList.contains('dr')) return; pg.classList.remove('dr'); if (pg.__w && t < total) play() }
      pg.addEventListener('pointerup', up); pg.addEventListener('pointercancel', up)
      pg.addEventListener('keydown', (e) => { const d = e.key === 'ArrowRight' ? 2 : e.key === 'ArrowLeft' ? -2 : 0; if (!d) return; e.preventDefault(); t = Math.max(0, Math.min(total, t + d)); if (st === 'end' && t < total) st = 'pause'; draw() })
      draw()
    },
  })

  /* MP-CONT-004 */
  def({
    id: 'MP-CONT-004', name: '直播卡·双列', style: '直播预约',
    fit: '直播频道、首页直播位；直播中卡片展示实时观看人数，预告卡提供预约提醒',
    avoid: '没有真实直播数据时不要伪造观看人数；同一张卡不要既能进入又放“进入直播间”按钮',
    kw: 'live 直播卡 直播中 预告 预约 观看人数 主播 双列 讲解商品',
    css: S('mpcont004', `&{width:340px;display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:stretch}
& .cd{display:flex;flex-direction:column;background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 6px 18px var(--sh08)}
& .cv{position:relative;aspect-ratio:3/4;overflow:hidden;background:var(--ph);cursor:pointer}
& .cv img{width:100%;height:100%;object-fit:cover}
& .cv::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,color-mix(in srgb,var(--scrim) 22%,transparent),transparent 28%,transparent 62%,color-mix(in srgb,var(--scrim) 50%,transparent))}
& .soon .cv::after{background:color-mix(in srgb,var(--scrim) 42%,transparent)}
& .bg1{position:absolute;left:8px;top:8px;z-index:1;height:24px;padding:0 8px;border-radius:12px;background:var(--danger-fill);color:#fff;font-size:12px;font-weight:600;display:inline-flex;align-items:center;gap:6px}
& .bg1 u{display:inline-flex;align-items:flex-end;gap:2px;height:10px;text-decoration:none}
& .bg1 u i{width:2px;border-radius:1px;background:var(--card);animation:@@bar 1s ease-in-out infinite}
& .bg1 u i:nth-child(1){height:6px}& .bg1 u i:nth-child(2){height:10px;animation-delay:.2s}& .bg1 u i:nth-child(3){height:7px;animation-delay:.4s}
@keyframes @@bar{0%,100%{transform:scaleY(.5)}50%{transform:scaleY(1)}}
@media(prefers-reduced-motion:reduce){& .bg1 u i{animation:none}}
& .bg1.pre{background:color-mix(in srgb,var(--scrim) 62%,transparent)}
& .vw{position:absolute;right:8px;top:8px;z-index:1;height:24px;padding:0 8px;border-radius:12px;background:var(--mask2);color:#fff;font-size:12px;display:inline-flex;align-items:center;gap:4px;font-variant-numeric:tabular-nums}
& .tm1{position:absolute;z-index:1;left:0;right:0;top:50%;transform:translateY(-50%);text-align:center;color:#fff}
& .tm1 b{display:block;font-size:22px;line-height:30px;font-weight:700;font-variant-numeric:tabular-nums}
& .tm1 span{font-size:12px;opacity:.92}
& .tx{flex:1;display:flex;flex-direction:column;padding:10px 10px 10px}
& h5{margin:0;font-size:14px;line-height:20px;font-weight:600;${CLAMP(2)};min-height:40px}
& .hs{display:flex;align-items:center;gap:6px;margin-top:6px;font-size:12px;color:var(--ink3);min-width:0}
& .hs span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .gd{margin-top:auto;padding-top:8px}
& .gd .ing{display:block;margin-bottom:4px;font-size:12px;line-height:18px;font-weight:600;color:var(--p-text)}
& .gd .pd{display:flex;align-items:center;gap:8px;padding:6px;border-radius:12px;background:var(--n3);min-width:0}
& .gd img{width:36px;height:36px;border-radius:8px;object-fit:cover;flex:none}
& .gd .pt{min-width:0;display:flex;flex-direction:column;gap:3px;font-size:12px;line-height:16px;color:var(--ink2)}
& .gd .pt span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .gd .price b{font-size:14px}
& .sd{margin-top:auto;display:flex;flex-direction:column;gap:8px;padding-top:8px}
& .sd .cnt{font-size:12px;line-height:18px;color:var(--ink3);font-variant-numeric:tabular-nums}
& .rs{position:relative;display:flex;align-items:center;justify-content:center;gap:4px;width:100%;height:44px;border-radius:22px;background:var(--pt);color:var(--p-text);font-size:14px;font-weight:600;transition:background .15s,color .15s}
& .rs:active{transform:scale(.97)}
& .rs .lb1{display:none}& .rs.on{background:var(--lift);color:var(--ink2);box-shadow:inset 0 0 0 1px var(--n7)}& .rs.on .lb0{display:none}& .rs.on .lb1{display:inline-flex;align-items:center;gap:4px}& .rs .lb0{display:inline-flex;align-items:center;gap:4px}
${ICO}`),
    html: () => `<div class="mpcont004"><div class="cd live"><div class="cv" data-toast="进入直播间"><img src="${P(6)}" alt=""><span class="bg1"><u><i></i><i></i><i></i></u>直播中</span><span class="vw">${I('eye')}<b data-v>8,642</b></span></div><div class="tx"><h5>春季焕新夜：补水好物限量专场</h5><div class="hs">${critter(1, 20)}<span>小鹿严选</span></div><div class="gd"><span class="ing">正在讲解</span><div class="pd"><img src="${P(6)}" alt=""><div class="pt"><span>保温水杯 500ml</span><span class="price"><small>¥</small><b>89</b></span></div></div></div></div></div><div class="cd soon"><div class="cv" data-toast="预告详情"><img src="${P(3)}" alt=""><span class="bg1 pre">${I('clock')}预告</span><div class="tm1"><b>19:30</b><span>今晚开播</span></div></div><div class="tx"><h5>通勤包新品首发，老板亲自讲搭配</h5><div class="hs">${critter(3, 20)}<span>包包研究所</span></div><div class="sd"><span class="cnt"><b data-n>1,286</b> 人已预约</span><button class="rs" type="button" aria-pressed="false"><span class="lb0">${I('bell')}预约提醒</span><span class="lb1">${I('check')}已预约</span></button></div></div></div></div>`,
    js: (root) => {
      const v = root.querySelector('[data-v]'); let n = 8642
      const timer = setInterval(() => { if (!root.isConnected) { clearInterval(timer); return } n += 7 + Math.floor(Math.random() * 32); v.textContent = n >= 10000 ? (n / 10000).toFixed(1) + ' 万' : n.toLocaleString('en-US') }, 1800)
      const rs = root.querySelector('.rs'), c = root.querySelector('.cnt [data-n]'); let m = 1286
      rs.addEventListener('click', () => { const on = rs.classList.toggle('on'); rs.setAttribute('aria-pressed', on); m += on ? 1 : -1; c.textContent = m.toLocaleString('en-US'); IX.toast(root, on ? '开播前 10 分钟提醒你' : '已取消预约') })
    },
  })

  /* MP-CONT-005 */
  const CMT = [
    ['林小满', 0, '作者', '用了两个月，通勤地铁上降噪效果很明显，续航也比预想的好。唯一的小问题是耳翼偏硬，戴超过两小时会有点压耳朵，建议换一对耳塞套试试。', '2 小时前', 120, 86, [['陈晓雨', 1, '耳塞套是单独买的吗？尺寸怎么选？', '1 小时前', 12], ['林小满', 0, '官方有 S/M/L 三个尺寸，盒里默认是 M，可以免费换。', '45 分钟前', 5]]],
    ['王子豪', 2, '', '音质对得起价格，低频不糊。', '昨天', 1500, 42, [['周一帆', 3, '同感，通勤够用了。', '昨天', 3]]],
    ['赵可心', 3, '', '包装很用心，送人也体面，快递第二天就到了。', '10 分钟前', 10, 15, []],
  ]
  const cmtHTML = ([nm, av, au, tx, tm, age, lk, rp], i) => `<li data-age="${age}"><div class="av1">${critter(av, 36)}</div><div class="m"><div class="nm"><b>${nm}</b>${au ? `<em>${au}</em>` : ''}</div><p>${tx}</p><div class="meta"><span>${tm}</span><button class="rp" type="button" data-reply="${nm}">回复</button>${like('mc_thumb', lk)}</div>${rp.length ? `<div class="rps" data-ix="acc"><div class="ix-ai"><button class="more" type="button" data-h><span class="c0">展开 ${rp.length} 条回复</span><span class="c1">收起回复</span>${I('down')}</button><div class="ix-ab"><div><div class="rbx">${rp.map(([n2, a2, t2, m2, l2]) => `<div class="sub"><div class="nm"><b>${n2}</b></div><p>${t2}</p><div class="meta"><span>${m2}</span>${like('mc_thumb', l2)}</div></div>`).join('')}</div></div></div></div></div>` : ''}</div></li>`
  def({
    id: 'MP-CONT-005', name: '评论列表', style: '点赞回复',
    fit: '文章、商品、视频下方的讨论区；点赞即时计数，回复折叠展开，输入框固定在底部',
    avoid: '评论超过 20 条一次全展示（分页加载）；用户头像不要用文字首字母',
    kw: 'comment 评论 回复 点赞 展开 楼层 热门 最新 输入框 发送',
    css: S('mpcont005', `&{width:340px;${CARD};overflow:hidden}
& .hd{display:flex;align-items:center;justify-content:space-between;padding:6px 16px 0 20px;height:56px}
& .hd b{font-size:16px;font-weight:600}& .hd em{font-size:14px;font-weight:400;color:var(--ink3);margin-left:4px;font-variant-numeric:tabular-nums}
& .sg{display:flex;background:var(--soft);border-radius:12px;padding:2px}
& .sg button{height:32px;padding:0 12px;border-radius:8px;font-size:12px;color:var(--ink2);transition:background .15s,color .15s}
& .sg button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:0 1px 4px var(--sh12)}
& .ls{list-style:none;margin:0;padding:0 16px;max-height:360px;overflow-y:auto}
& .ls>li{display:flex;gap:10px;padding:12px 0;border-top:1px solid var(--line)}
& .ls>li:first-child{border-top:0}
& .av1{flex:none}
& .m{flex:1;min-width:0}
& .nm{display:flex;align-items:center;gap:6px}& .nm b{font-size:14px;font-weight:600;line-height:20px}
& .nm em{height:18px;padding:0 6px;border-radius:4px;background:var(--pt);color:var(--p-text);font-size:12px;font-weight:600;display:inline-flex;align-items:center}
& .m p{margin:2px 0 0;font-size:14px;line-height:22px;color:var(--ink);word-break:break-all}
& .meta{display:flex;align-items:center;font-size:12px;color:var(--ink3);margin-top:0}
& .meta .rp{min-width:44px;height:44px;margin-left:4px;color:var(--ink2)}
& .meta .lkb{margin-left:auto;margin-right:-8px}
& .rps .more{display:inline-flex;align-items:center;gap:4px;height:32px;padding:0 10px;border-radius:16px;background:var(--n3);font-size:12px;color:var(--ink2)}
& .rps .more .i{width:14px;height:14px;transition:transform .25s cubic-bezier(.2,0,0,1)}
& .rps .ix-ai.open .more .i{transform:rotate(180deg)}
& .rps .c1{display:none}& .rps .ix-ai.open .c0{display:none}& .rps .ix-ai.open .c1{display:inline}
& .rbx{background:var(--n3);border-radius:12px;margin-top:8px;padding:0 12px 4px}
& .sub{padding-top:8px}
& .sub p{font-size:14px;margin:0}
& .cp{display:flex;align-items:center;gap:8px;padding:10px 12px 12px 16px;border-top:1px solid var(--line);background:var(--card)}
& .cp input{flex:1;min-width:0;height:44px;border:1px solid transparent;border-radius:22px;background:var(--soft);padding:0 16px;font:inherit;font-size:14px;color:var(--ink);outline:none}
& .cp input:focus{border-color:var(--ink2);background:var(--card)}
& .cp input::placeholder{color:var(--ink3)}
& .send{flex:none;min-width:64px;height:44px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:14px;font-weight:600;transition:opacity .15s}
& .send:disabled{background:var(--n6);color:var(--ink4);cursor:not-allowed}
& .ls>li.nw{animation:@@in .35s cubic-bezier(.2,0,0,1)}
@keyframes @@in{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
${LIKE_CSS}${ICO}`),
    html: () => `<div class="mpcont005"><div class="hd"><b>评论<em data-cnt>128</em></b><div class="sg"><button type="button" class="on" data-s="hot">热门</button><button type="button" data-s="new">最新</button></div></div><ul class="ls">${CMT.map(cmtHTML).join('')}</ul><div class="cp"><input type="text" placeholder="说点什么…" aria-label="写评论" maxlength="100"><button class="send" type="button" disabled>发送</button></div></div>`,
    js: (root) => {
      const ls = root.querySelector('.ls'), inp = root.querySelector('.cp input'), send = root.querySelector('.send'), cnt = root.querySelector('[data-cnt]')
      const likes = (li) => parseInt(li.querySelector('.meta .lkb [data-n]').textContent.replace(/,/g, ''), 10) || 0
            const sortBy = (k) => {
        root.querySelectorAll('.sg button').forEach((b) => b.classList.toggle('on', b.dataset.s === k))
        const items = [...ls.children]
        items.sort((a, b) => k === 'hot' ? likes(b) - likes(a) : (+a.dataset.age) - (+b.dataset.age))
        items.forEach((li) => ls.appendChild(li))
      }
      root.querySelector('.sg').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) sortBy(b.dataset.s) })
      inp.addEventListener('input', () => { send.disabled = !inp.value.trim() })
      let to = ''
      ls.addEventListener('click', (e) => { const r = e.target.closest('.rp'); if (!r) return; to = r.dataset.reply; inp.placeholder = '回复 @' + to; inp.focus() })
      const post = () => {
        const v = inp.value.trim(); if (!v) return
        const li = document.createElement('li'); li.className = 'nw'; li.dataset.age = 0
        li.innerHTML = '<div class="av1"></div><div class="m"><div class="nm"><b>我</b></div><p></p><div class="meta"><span>刚刚</span><button class="lkb" type="button" data-ix="like" aria-label="点赞"><i class="i">' + sv('mc_thumb') + '</i><b data-n>0</b></button></div></div>'
        li.querySelector('p').textContent = (to ? '回复 @' + to + '：' : '') + v
        li.querySelector('.av1').innerHTML = '<svg width="36" height="36" viewBox="0 0 48 48" style="border-radius:50%;flex:none"><circle cx="24" cy="24" r="24" fill="#F2E1EA"/><circle cx="13" cy="15" r="5" fill="#D9AFC1"/><circle cx="35" cy="15" r="5" fill="#D9AFC1"/><circle cx="24" cy="28" r="13.5" fill="#D9AFC1"/><circle cx="24" cy="31" r="5.5" fill="var(--card)" opacity=".7"/><circle cx="19.5" cy="25.5" r="1.7" fill="#4A3A33"/><circle cx="28.5" cy="25.5" r="1.7" fill="#4A3A33"/><ellipse cx="24" cy="29.5" rx="2.2" ry="1.6" fill="#4A3A33"/></svg>'
        ls.prepend(li); ls.scrollTop = 0
        cnt.textContent = (parseInt(cnt.textContent, 10) || 0) + 1
        inp.value = ''; inp.placeholder = '说点什么…'; to = ''; send.disabled = true
        root.querySelectorAll('.sg button').forEach((b) => b.classList.toggle('on', b.dataset.s === 'new'))
        IX.toast(root, '评论已发布')
      }
      send.addEventListener('click', post)
      inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') post() })
    },
  })

  /* MP-CONT-006 */
  const TOPICS = [
    [['通勤好物', 0], ['桌面改造', 0], ['居家咖啡', 1], ['周末露营', 1], ['一人食', 1], ['读书打卡', 2], ['早起挑战', 2], ['数码开箱', 1], ['平价护肤', 0], ['运动穿搭', 1], ['收纳整理', 2], ['城市漫步', 2]],
    [['春日出游', 0], ['手冲入门', 1], ['家居小改造', 1], ['好物分享', 0], ['轻量跑步', 1], ['断舍离', 2], ['通勤穿搭', 1], ['宠物日常', 0], ['植物养护', 2], ['极简生活', 1], ['周末市集', 2], ['夜读时光', 2]],
  ]
  const tpHTML = (set) => set.map(([n, t]) => `<button class="tp ${['hot', 'mid', 'low'][t]}" type="button" data-n="${n}">${t === 0 ? I('fire') : '#'}${n}</button>`).join('')
  def({
    id: 'MP-CONT-006', name: '话题标签云', style: '热度多选',
    fit: '兴趣选择、话题订阅、发布页选话题；热度分三档字号，限选数量，选完才能点“完成”',
    avoid: '一屏标签超过 15 个（改用“换一批”）；不要给每个标签配不同鲜艳颜色',
    kw: 'topic tag cloud 话题 标签云 兴趣 热门 订阅 多选 换一批',
    css: S('mpcont006', `&{width:340px;${CARD};padding:16px 16px 14px}
& .hd{display:flex;align-items:center;justify-content:space-between}
& .hd b{font-size:16px;font-weight:600}
& .rf{display:inline-flex;align-items:center;gap:4px;min-width:44px;height:44px;margin:-10px -8px -10px 0;padding:0 8px;font-size:14px;color:var(--ink2)}
& .rf .i{transition:transform .4s cubic-bezier(.2,0,0,1)}& .rf.sp .i{transform:rotate(360deg)}
& .cloud{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:12px 10px;padding:14px 0 12px;min-height:178px;align-content:center}
& .cloud.sw1{animation:@@fd .3s cubic-bezier(.2,0,0,1)}
@keyframes @@fd{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
& .tp{position:relative;display:inline-flex;align-items:center;gap:4px;border-radius:16px;white-space:nowrap;transition:background .15s,color .15s,box-shadow .15s}
& .tp::before{content:"";position:absolute;inset:-6px -2px}
& .tp:active{transform:scale(.96)}
& .tp.hot{height:40px;padding:0 14px;font-size:16px;font-weight:600;background:var(--pt);color:var(--p-text);box-shadow:inset 0 0 0 1px var(--pm)}
& .tp.mid{height:36px;padding:0 12px;font-size:14px;background:var(--soft);color:var(--ink)}
& .tp.low{height:32px;padding:0 10px;font-size:12px;background:var(--card);color:var(--ink2);box-shadow:inset 0 0 0 1px var(--n6)}
& .tp.on{background:var(--p);color:#fff;box-shadow:none}
& .tp .i{width:16px;height:16px}
& .ft{display:flex;align-items:center;justify-content:space-between;padding-top:12px;border-top:1px solid var(--line)}
& .sel{font-size:14px;color:var(--ink2)}& .sel b{font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
& .ok{min-width:96px;height:44px;padding:0 20px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:16px;font-weight:600;box-shadow:0 5px 12px rgba(var(--p-rgb),.2);transition:transform .15s}
& .ok:active{transform:scale(.97)}
& .ok:disabled{background:var(--n6);color:var(--ink4);box-shadow:none;cursor:not-allowed}
${ICO}`),
    html: () => `<div class="mpcont006" data-max="5"><div class="hd"><b>选择感兴趣的话题</b><button class="rf" type="button">${I('refresh')}换一批</button></div><div class="cloud">${tpHTML(TOPICS[0])}</div><template class="set">${tpHTML(TOPICS[1])}</template><div class="ft"><span class="sel">已选 <b data-c>0</b>/5</span><button class="ok" type="button" disabled>完成</button></div></div>`,
    js: (root) => {
      const el = root.querySelector('.mpcont006'), cloud = el.querySelector('.cloud'), cnt = el.querySelector('[data-c]'), ok = el.querySelector('.ok'), rf = el.querySelector('.rf')
      const max = +el.dataset.max, sets = [cloud.innerHTML, el.querySelector('template.set').innerHTML], picked = new Set(); let k = 0
      const paint = () => { cloud.querySelectorAll('.tp').forEach((b) => b.classList.toggle('on', picked.has(b.dataset.n))); cnt.textContent = picked.size; ok.disabled = picked.size === 0 }
      cloud.addEventListener('click', (e) => {
        const b = e.target.closest('.tp'); if (!b) return
        const n = b.dataset.n
        if (picked.has(n)) picked.delete(n); else { if (picked.size >= max) { IX.toast(root, '最多选择 ' + max + ' 个话题'); return } picked.add(n) }
        paint()
      })
      rf.addEventListener('click', () => { k = (k + 1) % sets.length; cloud.innerHTML = sets[k]; cloud.classList.remove('sw1'); void cloud.offsetWidth; cloud.classList.add('sw1'); rf.classList.toggle('sp'); paint() })
      ok.addEventListener('click', () => { if (picked.size) IX.toast(root, '已关注 ' + picked.size + ' 个话题') })
    },
  })

  /* MP-CONT-007 */
  const RANK = [
    ['通勤耳机怎么选：降噪与续航的取舍', '小满', 0], ['提升效率的 5 件桌面小物', '桌面控', 5], ['每天一杯，给自己一点仪式感', '阿杯', 2], ['入门机械腕表，从哪一块开始', '表迷', 4], ['春季跑鞋选购：缓震、支撑与脚型', '跑者笔记', 1], ['双肩包通勤半年的真实使用记录', '老周', 8],
  ]
  const RK_TABS = [
    ['d', '日榜', [0, 1, 2, 3, 4], ['8.6 万', '7.9 万', '6.4 万', '5.2 万', '4.8 万'], ['up', 'same', 'up', 'down', 'up']],
    ['w', '周榜', [1, 0, 3, 2, 5], ['52.4 万', '49.8 万', '38.1 万', '35.7 万', '30.2 万'], ['same', 'down', 'up', 'down', 'up']],
    ['m', '月榜', [2, 0, 1, 4, 3], ['186.3 万', '171.0 万', '160.5 万', '122.8 万', '118.6 万'], ['up', 'up', 'down', 'same', 'down']],
  ]
  const TREND = { up: `<span class="tr up">${I('arrowup')}</span>`, down: `<span class="tr dn">${I('arrowdown')}</span>`, same: '<span class="tr">—</span>' }
  def({
    id: 'MP-CONT-007', name: '内容排行榜', style: '前三强调',
    fit: '热门榜、销量榜、搜索榜；前三名用淡色徽标强调，日榜周榜月榜一键切换',
    avoid: '榜单只有三五条数据时别做；排名靠买量的榜不要放，用户一眼就能看出',
    kw: 'rank 排行榜 热榜 日榜 周榜 月榜 前三 热度 趋势 榜单',
    css: S('mpcont007', `&{width:340px;${CARD};padding:4px 12px 10px}
& .hd{display:flex;align-items:center;gap:8px;height:56px;padding:0 4px}
& .hd b{display:inline-flex;align-items:center;gap:6px;font-size:16px;font-weight:600}
& .hd b .i{width:20px;height:20px;color:var(--p-fg)}
& .sg{margin-left:auto;display:flex;background:var(--soft);border-radius:12px;padding:2px}
& .sg button{height:32px;padding:0 12px;border-radius:8px;font-size:12px;color:var(--ink2);transition:background .15s,color .15s}
& .sg button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:0 1px 4px var(--sh12)}
& .row{display:flex;align-items:center;gap:12px;min-height:68px;padding:8px;border-radius:12px;cursor:pointer;transition:background .15s}
& .row:hover{background:var(--n3)}
& .no{flex:none;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;color:var(--ink3);font-variant-numeric:tabular-nums}
& .r1 .no{background:var(--warn-bg);color:var(--warn)}& .r2 .no{background:var(--n4);color:var(--ink2)}& .r3 .no{background:var(--tint-f4e8e1);color:var(--bronze)}
& .cvr{flex:none;width:52px;height:52px;border-radius:12px;overflow:hidden;background:var(--ph)}
& .cvr img{width:100%;height:100%;object-fit:cover}
& .tt{flex:1;min-width:0}
& .tt h5{margin:0;font-size:14px;line-height:20px;font-weight:600;${CLAMP(2)}}
& .tt span{display:block;margin-top:2px;font-size:12px;line-height:18px;color:var(--ink3)}
& .hv{flex:none;display:flex;flex-direction:column;align-items:flex-end;gap:2px;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
& .hv b{display:inline-flex;align-items:center;gap:3px;font-weight:400;color:var(--ink2)}
& .hv b .i{width:14px;height:14px;color:var(--p-fg)}
& .tr{display:inline-flex;align-items:center;color:var(--ink3);height:16px}
& .tr .i{width:12px;height:12px}& .tr.up{color:var(--ok)}& .tr.dn{color:var(--danger)}
& .r1{background:linear-gradient(135deg,var(--pt),var(--card) 85%);box-shadow:inset 0 0 0 1px var(--pm);min-height:84px}
& .r1 .cvr{width:64px;height:64px}
& .r1 .no{width:32px;height:32px;font-size:16px}
& .r1 h5{line-height:22px}
${ICO}`),
    html: () => `<div class="mpcont007"><div class="hd"><b>${I('fire')}内容热榜</b><div class="sg" data-ix="tabs" data-g="rk">${RK_TABS.map(([k, n], i) => `<button type="button" data-t="${k}" class="${i ? '' : 'on'}">${n}</button>`).join('')}</div></div>${RK_TABS.map(([k, , ord, heat, tr], pi) => `<div data-p="${k}" data-g="rk"${pi ? ' hidden' : ''}>${ord.map((ix, r) => { const [t, au, im] = RANK[ix]; return `<div class="row r${r + 1}" data-toast="查看内容详情"><span class="no">${r + 1}</span><div class="cvr"><img src="${P(im)}" alt=""></div><div class="tt"><h5>${t}</h5><span>${au}</span></div><div class="hv"><b>${I('fire')}${heat[r]}</b>${TREND[tr[r]]}</div></div>` }).join('')}</div>`).join('')}</div>`,
  })

  /* MP-CONT-008 */
  const FEED = [
    ['通勤耳机怎么选：降噪与续航的取舍', 0, '3/4', '小满', 0, 326], ['提升效率的 5 件桌面小物', 5, '1/1', '桌面控', 1, 148], ['每天一杯，给自己一点仪式感', 2, '4/5', '阿杯', 2, 212], ['入门机械腕表，从哪一块开始', 4, '3/4', '表迷', 3, 97],
    ['春季跑鞋选购：缓震、支撑与脚型', 1, '1/1', '跑者笔记', 0, 184], ['双肩包通勤半年的真实使用记录', 8, '4/5', '老周', 1, 76], ['把杯子换成保温款之后，我每天多喝了一升水', 6, '3/4', '喝水打卡', 2, 258], ['便宜好用的精华，到底差在哪', 7, '1/1', '护肤课代表', 3, 131],
    ['帆布包还能这样搭', 3, '4/5', '小满', 0, 64], ['一盏灯带来的书桌改造', 5, '3/4', '桌面控', 1, 203], ['手作釉面杯：慢慢变旧的好看', 2, '1/1', '阿杯', 2, 88], ['周末市集淘到的小物清单', 4, '4/5', '老周', 3, 57],
  ]
  const feedCard = ([t, im, ar, au, av, n]) => `<div class="cd"><div class="pic" data-toast="打开笔记"><img src="${P(im)}" style="aspect-ratio:${ar}" alt=""></div><h5>${t}</h5><div class="ft">${critter(av, 20)}<span class="au">${au}</span>${like('heart', n)}</div></div>`
  def({
    id: 'MP-CONT-008', name: '信息流瀑布', style: '加载更多',
    fit: '种草、笔记、社区首页；两列错落排布，点“加载更多”追加，加载完给出“没有更多了”',
    avoid: '需要对比价格规格的交易列表（改横向列表卡）；封面比例差别过大时用统一裁切',
    kw: 'feed waterfall 信息流 瀑布流 双列 笔记 种草 加载更多 追加 点赞',
    css: S('mpcont008', `&{width:340px}
& .cols{display:flex;gap:10px;align-items:flex-start}
& .col{flex:1;min-width:0;display:flex;flex-direction:column;gap:10px}
& .cd{background:var(--card);border-radius:12px;overflow:hidden;box-shadow:0 4px 14px var(--sh08)}
& .cd.nw{animation:@@in .4s cubic-bezier(.2,0,0,1)}
@keyframes @@in{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
& .pic{overflow:hidden;cursor:pointer;background:var(--ph)}
& .pic img{width:100%;object-fit:cover;transition:transform .3s cubic-bezier(.2,0,0,1)}
& .pic:hover img{transform:scale(1.04)}
& h5{margin:0;padding:8px 10px 0;font-size:14px;line-height:20px;font-weight:600;${CLAMP(2)}}
& .ft{display:flex;align-items:center;gap:6px;padding:6px 10px 6px;font-size:12px;color:var(--ink3)}
& .ft .au{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .ft .lkb{height:44px;min-width:44px;margin:-10px -8px -10px 0;padding:0 8px}
& .more{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;height:44px;margin-top:12px;border-radius:22px;background:var(--card);color:var(--ink2);font-size:14px;box-shadow:0 2px 8px var(--sh08);transition:transform .15s}
& .more:active{transform:scale(.98)}
& .more.ld{color:var(--ink3);cursor:progress}
& .end{display:flex;align-items:center;justify-content:center;gap:12px;height:44px;margin-top:12px;font-size:12px;color:var(--ink3)}
& .end::before,& .end::after{content:"";width:40px;height:1px;background:var(--n7)}
${LIKE_CSS}${ICO}${SPIN}`),
    html: () => {
      const cols = [[], []]; FEED.slice(0, 4).forEach((f, i) => cols[i % 2].push(feedCard(f)))
      return `<div class="mpcont008"><div class="cols"><div class="col">${cols[0].join('')}</div><div class="col">${cols[1].join('')}</div></div><template class="b1">${FEED.slice(4, 8).map(feedCard).join('')}</template><template class="b2">${FEED.slice(8, 12).map(feedCard).join('')}</template><button class="more" type="button"><span class="lbl">加载更多</span></button></div>`
    },
    js: (root) => {
      const el = root.querySelector('.mpcont008'), cols = [...el.querySelectorAll('.col')], more = el.querySelector('.more'); let n = 0
      const tpls = [...el.querySelectorAll('template')]
      more.addEventListener('click', () => {
        if (more.classList.contains('ld')) return
        more.classList.add('ld'); more.innerHTML = '<i class="spin"></i><span class="lbl">加载中…</span>'
        setTimeout(() => {
          if (!root.isConnected) return
          const t = tpls[n++]; if (!t) return
          const wrap = document.createElement('div'); wrap.innerHTML = t.innerHTML
          ;[...wrap.children].forEach((c) => { c.classList.add('nw'); const col = cols[0].offsetHeight <= cols[1].offsetHeight ? cols[0] : cols[1]; col.appendChild(c) })
          more.classList.remove('ld'); more.innerHTML = '<span class="lbl">加载更多</span>'
          if (n >= tpls.length) { const end = document.createElement('div'); end.className = 'end'; end.textContent = '没有更多了'; more.replaceWith(end) }
        }, 900)
      })
    },
  })

  /* MP-CONT-009 */
  const NOTICE = [['活动', '首单立减 20 元，今晚截止'], ['物流', '部分地区配送延后 1 天'], ['会员', '会员日：每周三全场 9 折']]
  def({
    id: 'MP-CONT-009', name: '公告滚动条', style: '纵向轮播',
    fit: '首页顶部、订单页的通知条；多条短公告纵向轮播，长公告横向滚动，可关闭',
    avoid: '重要且必须阅读的通知（改弹窗或固定条）；一屏同时出现两条以上通知条',
    kw: 'notice 公告 通知条 滚动 轮播 跑马灯 marquee 横幅 消息 维护通知',
    css: S('mpcont009', `&{width:340px;display:flex;flex-direction:column;gap:12px}
& .tk{position:relative;display:flex;align-items:center;gap:10px;height:44px;padding:0 12px;border-radius:12px;background:var(--card);box-shadow:0 4px 14px var(--sh08);cursor:pointer}
& .tk>.i{width:20px;height:20px;color:var(--p-fg)}
& .win{position:relative;flex:1;min-width:0;height:44px;overflow:hidden}
& .rail{will-change:transform}
& .rail>div{display:flex;align-items:center;gap:8px;height:44px;font-size:14px;color:var(--ink)}
& .rail>div span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .rail .tg{height:20px;border-radius:4px;flex:none}
& .cur{flex:none;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
& .tk .go{width:16px;height:16px;flex:none;color:var(--ink3)}
& .wn{display:flex;align-items:center;gap:10px;height:44px;padding:0 4px 0 12px;border-radius:12px;background:var(--warn-bg);color:var(--warn);overflow:hidden;transition:height .25s cubic-bezier(.2,0,0,1),opacity .2s,margin .25s}
& .wn>.i{width:20px;height:20px}
& .mq{position:relative;flex:1;min-width:0;height:44px;overflow:hidden;font-size:14px;line-height:44px;white-space:nowrap}
& .mq span{display:inline-block;padding-left:100%;animation:@@mq 14s linear infinite}
& .mq:hover span{animation-play-state:paused}
@keyframes @@mq{to{transform:translateX(-100%)}}
@media(prefers-reduced-motion:reduce){& .mq span{animation:none;padding-left:0}}
& .wn .x{flex:none;width:44px;height:44px;display:flex;align-items:center;justify-content:center;color:var(--warn)}
& .wn .x .i{width:16px;height:16px}
& .wn.gone{height:0;opacity:0;margin-bottom:-12px}
& .back{align-self:center;height:44px;padding:0 12px;font-size:12px;color:var(--ink3);text-decoration:underline;text-underline-offset:3px}
${ICO}`),
    html: () => `<div class="mpcont009"><div class="tk" data-toast="查看公告详情"><i class="i">${sv('mc_volume')}</i><div class="win"><div class="rail">${NOTICE.concat([NOTICE[0]]).map(([t, x]) => `<div><span class="tg tg-soft">${t}</span><span>${x}</span></div>`).join('')}</div></div><span class="cur"><b data-cur>1</b>/${NOTICE.length}</span>${I('right', 'go')}</div><div class="wn" role="status">${I('alert')}<div class="mq"><span>系统将于 11 月 6 日 02:00–04:00 升级维护，期间下单与支付暂不可用，请提前安排。</span></div><button class="x" type="button" aria-label="关闭通知">${I('close')}</button></div><button class="back" type="button" hidden>重新显示通知</button></div>`,
    js: (root) => {
      const tk = root.querySelector('.tk'), rail = tk.querySelector('.rail'), cur = tk.querySelector('[data-cur]'), n = rail.children.length - 1
      let i = 0, paused = false
      const go = () => {
        i++; rail.style.transition = 'transform .4s cubic-bezier(.2,0,0,1)'; rail.style.transform = 'translateY(' + (-i * tk.clientHeight) + 'px)'
        cur.textContent = (i % n) + 1
        if (i === n) setTimeout(() => { rail.style.transition = 'none'; i = 0; rail.style.transform = 'translateY(0)' }, 420)
      }
      const timer = setInterval(() => { if (!root.isConnected) { clearInterval(timer); return } if (!paused) go() }, 2600)
      tk.addEventListener('mouseenter', () => (paused = true)); tk.addEventListener('mouseleave', () => (paused = false))
      tk.addEventListener('touchstart', () => (paused = true), { passive: true }); tk.addEventListener('touchend', () => (paused = false))
      const wn = root.querySelector('.wn'), back = root.querySelector('.back')
      wn.querySelector('.x').addEventListener('click', () => { wn.classList.add('gone'); back.hidden = false })
      back.addEventListener('click', () => { wn.classList.remove('gone'); back.hidden = true })
    },
  })

  /* ================= LIST 列表与筛选 ================= */
  guide('mp', 'LIST', [
    ['分类页、商品类目（一级 6–15 个）', '左右联动分类', '点左侧右边滚到对应分段，滚动时左侧高亮跟随——小程序分类页的硬要求'],
    ['商品列表要按品类、价格、服务筛选', '筛选条与筛选弹层', '常用条件放条上直接点，复杂条件收进弹层；确定按钮显示结果数，重置一键清空'],
    ['商品列表顶部要排序', '排序条与结果列表', '综合 / 销量 / 价格升降 / 新品；选中态一眼可辨，列表与网格可切换'],
    ['搜索结果页', '搜索结果页头', '关键词在结果里高亮、顶部写明结果数；空输入给最近搜索，无结果给换词建议'],
    ['订单、消息、记录这类长列表', '滚动加载列表', '不用页码；到底自动加载，失败可点重试，加载完写“没有更多了”'],
    ['城市、品牌、联系人', '字母索引条', '右侧字母条点按或拖动跳转，拖动时放大提示当前字母；条目少于 20 个别做'],
  ])

  /* MP-LIST-001 */
  const CATL = [
    ['新品推荐', 0, [['降噪耳机', 0], ['轻量跑鞋', 1], ['手作马克杯', 2], ['帆布托特包', 3], ['机械腕表', 4], ['护眼台灯', 5]]],
    ['数码', 0, [['无线耳机', 0], ['智能腕表', 4], ['桌面台灯', 5]]],
    ['鞋包', 0, [['轻量跑鞋', 1], ['帆布托特', 3], ['双肩背包', 8], ['通勤腰包', 3]]],
    ['居家', 1, [['手作马克杯', 2], ['保温水杯', 6], ['护眼台灯', 5], ['咖啡杯垫', 2], ['便携餐盒', 6], ['香薰蜡烛', 7]]],
    ['美妆', 0, [['保湿精华', 7], ['修护面霜', 7], ['防晒乳', 7]]],
    ['食品', 0, [['手冲咖啡豆', 2], ['燕麦脆', 3], ['坚果礼盒', 8]]],
    ['运动', 0, [['轻量跑鞋', 1], ['运动水壶', 6], ['瑜伽垫', 8], ['运动腰包', 3]]],
  ]
  def({
    id: 'MP-LIST-001', name: '左右联动分类', style: '滚动跟随',
    fit: '分类页、商品类目；点左侧分类右边滚到对应分段，右边滚动时左侧高亮自动跟随',
    avoid: '一级分类少于 5 个（改顶部标签）；分段内容太少导致最后几类点不到顶',
    kw: 'category 分类 左右联动 侧边栏 类目 滚动联动 scrollspy 二级分类 商品分类',
    css: S('mplist001', `&{width:340px;height:456px;${CARD};overflow:hidden;display:flex;flex-direction:column}
& .sr{flex:none;display:flex;align-items:center;gap:8px;height:44px;margin:10px 12px 8px;padding:0 14px;border-radius:22px;background:var(--soft);color:var(--ink3);font-size:14px;cursor:pointer}
& .sr .i{width:18px;height:18px}
& .bd{flex:1;min-height:0;display:grid;grid-template-columns:88px 1fr}
& .lf{overflow-y:auto;background:var(--n2);scrollbar-width:none;position:relative}
& .lf::-webkit-scrollbar{display:none}
& .lf button{position:relative;display:flex;align-items:center;justify-content:center;width:100%;min-height:52px;padding:0 6px;font-size:14px;line-height:20px;color:var(--ink2);transition:background .15s,color .15s}
& .lf button.on{background:var(--lift);color:var(--ink);font-weight:600}
& .lf button.on::before{content:"";position:absolute;left:0;top:14px;bottom:14px;width:4px;border-radius:0 2px 2px 0;background:var(--p)}
& .lf .dot{position:absolute;right:12px;top:12px;width:8px;height:8px;border-radius:50%;background:var(--danger-fill)}
& .rt{position:relative;overflow-y:auto;padding:0 12px;scrollbar-width:thin}
& .sec h5{position:sticky;top:0;z-index:1;margin:0;padding:14px 0 10px;background:var(--card);font-size:14px;line-height:20px;font-weight:600}
& .gr{display:grid;grid-template-columns:repeat(3,1fr);gap:14px 8px;padding-bottom:12px}
& .gi{display:flex;flex-direction:column;align-items:center;gap:6px;cursor:pointer}
& .gi img{width:64px;height:64px;border-radius:12px;object-fit:cover;background:var(--n3);transition:transform .2s cubic-bezier(.2,0,0,1)}
& .gi:hover img{transform:scale(1.05)}
& .gi span{max-width:100%;font-size:12px;line-height:18px;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
${ICO}`),
    html: () => `<div class="mplist001"><div class="sr" data-toast="进入搜索页">${I('search')}<span>搜索商品、品牌、品类</span></div><div class="bd"><div class="lf" role="tablist" aria-label="商品分类">${CATL.map(([n, d], i) => `<button type="button" role="tab" class="${i ? '' : 'on'}">${n}${d ? '<i class="dot"></i>' : ''}</button>`).join('')}</div><div class="rt">${CATL.map(([n, , its]) => `<section class="sec"><h5>${n}</h5><div class="gr">${its.map(([t, im]) => `<div class="gi" data-toast="进入${t}"><img src="${P(im)}" alt=""><span>${t}</span></div>`).join('')}</div></section>`).join('')}<div class="pad"></div></div></div></div>`,
    js: (root) => {
      const lf = root.querySelector('.lf'), rt = root.querySelector('.rt'), btns = [...lf.querySelectorAll('button')], secs = [...rt.querySelectorAll('.sec')], pad = rt.querySelector('.pad')
      let lock = false, lockT = 0, cur = -1
      pad.style.height = Math.max(0, rt.clientHeight - secs[secs.length - 1].offsetHeight) + 'px'
      const mark = (i) => {
        if (i === cur) return; cur = i
        btns.forEach((b, k) => { b.classList.toggle('on', k === i); b.setAttribute('aria-selected', k === i) })
        const b = btns[i]
        if (b.offsetTop < lf.scrollTop) lf.scrollTop = b.offsetTop - 8
        else if (b.offsetTop + b.offsetHeight > lf.scrollTop + lf.clientHeight) lf.scrollTop = b.offsetTop + b.offsetHeight - lf.clientHeight + 8
      }
      rt.addEventListener('scroll', () => {
        if (lock) return
        const y = rt.scrollTop + 8; let i = 0
        secs.forEach((s, k) => { if (s.offsetTop <= y) i = k })
        mark(i)
      })
      btns.forEach((b, i) => b.addEventListener('click', () => {
        lock = true; clearTimeout(lockT); mark(i)
        rt.scrollTo({ top: secs[i].offsetTop, behavior: 'smooth' })
        lockT = setTimeout(() => { lock = false }, 700)
      }))
      mark(0)
    },
  })

  /* MP-LIST-002 */
  const FP = [
    ['无线降噪耳机', 599, '数码', '包邮 现货 有券', 0], ['轻量跑鞋', 329, '鞋包', '包邮 新品', 1], ['陶瓷马克杯', 69, '居家', '包邮 现货', 2], ['帆布托特包', 159, '鞋包', '现货', 3],
    ['机械腕表', 899, '数码', '有券', 4], ['护眼台灯', 219, '居家', '包邮 新品', 5], ['保温水杯', 89, '居家', '包邮 现货 新品', 6], ['保湿精华', 258, '美妆', '有券 现货', 7],
  ]
  def({
    id: 'MP-LIST-002', name: '筛选条与筛选弹层', style: '多选重置',
    fit: '商品列表、搜索结果；常用条件放条上直接点，复杂条件收进弹层，确定按钮实时显示结果数',
    avoid: '筛选项只有两三个（直接放条上）；弹层高度超过 80%，条件多时改分组折叠',
    kw: 'filter 筛选 筛选条 筛选弹层 多选 价格区间 重置 确定 品类 底部弹层',
    css: S('mplist002', `&{position:relative;width:340px;height:480px;${CARD};overflow:hidden;display:flex;flex-direction:column}
& .fb{flex:none;display:flex;align-items:center;height:52px;border-bottom:1px solid var(--line)}
& .qc{flex:1;min-width:0;display:flex;gap:8px;overflow-x:auto;padding:0 8px 0 12px;scrollbar-width:none}
& .qc::-webkit-scrollbar{display:none}
& .qc button{position:relative;flex:none;height:32px;padding:0 14px;border-radius:16px;background:var(--soft);color:var(--ink2);font-size:14px;transition:background .15s,color .15s,box-shadow .15s}
& .qc button::before{content:"";position:absolute;inset:-6px -2px}
& .qc button.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1px var(--pm)}
& .fbtn{flex:none;display:flex;align-items:center;gap:4px;height:52px;padding:0 14px;border-left:1px solid var(--line);font-size:14px;color:var(--ink2)}
& .fbtn .i{width:16px;height:16px}
& .fbtn.has{color:var(--p-text);font-weight:600}
& .bdg{display:none;min-width:16px;height:16px;padding:0 4px;border-radius:8px;background:var(--p);color:#fff;font-size:12px;font-weight:600;line-height:16px;text-align:center}
& .fbtn.has .bdg{display:inline-block}
& .ap{flex:none;display:flex;flex-wrap:wrap;gap:8px;padding:10px 12px 0}
& .ap:empty{display:none}
& .ap span{display:inline-flex;align-items:center;gap:2px;height:28px;padding:0 2px 0 10px;border-radius:8px;background:var(--pt);color:var(--p-text);font-size:12px;font-weight:600}
& .ap button{position:relative;width:24px;height:24px;display:flex;align-items:center;justify-content:center;color:var(--p-text)}
& .ap button::before{content:"";position:absolute;inset:-10px -6px}
& .ap button .i{width:12px;height:12px}
& .sm{flex:none;padding:10px 16px 4px;font-size:12px;color:var(--ink3)}& .sm b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}
& .ls{flex:1;min-height:0;overflow-y:auto;padding:0 12px 8px}
& .pr{display:flex;gap:12px;padding:8px 0}
& .pr img{width:64px;height:64px;border-radius:12px;object-fit:cover;flex:none;background:var(--ph)}
& .pr .tx{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:space-between}
& .pr h5{margin:0;font-size:14px;line-height:20px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .pr .tgs{display:flex;gap:6px}
& .pr .price b{font-size:18px}
& .pr .tg{height:20px;border-radius:4px}
& .emp{display:flex;flex-direction:column;align-items:center;gap:10px;padding:40px 20px;text-align:center;color:var(--ink2);font-size:14px}
& .emp .i{width:40px;height:40px;color:var(--ink3)}
& .emp button{height:44px;padding:0 20px;border-radius:22px;background:var(--pt);color:var(--p-text);font-size:14px;font-weight:600}
& .ix-ov{align-items:flex-end}
& .sheet{position:relative;width:100%;max-height:80%;display:flex;flex-direction:column;background:var(--card2);border-radius:22px 22px 0 0;box-shadow:0 -10px 30px var(--sh16);animation:@@up .28s cubic-bezier(.2,0,0,1)}
@keyframes @@up{from{transform:translateY(40px);opacity:0}to{transform:none;opacity:1}}
& .sh-h{flex:none;display:flex;align-items:center;justify-content:space-between;height:52px;padding:0 4px 0 20px}
& .sh-h b{font-size:16px;font-weight:600}
& .sh-h .x{width:44px;height:44px;display:flex;align-items:center;justify-content:center;color:var(--ink2)}
& .sh-h .x .i{width:20px;height:20px}
& .sh-b{flex:1;min-height:0;overflow-y:auto;padding:0 20px 8px}
& .sh-b h6{margin:12px 0 10px;font-size:14px;line-height:20px;font-weight:600;color:var(--ink)}
& .chs{display:flex;flex-wrap:wrap;gap:10px}
& .ch{height:36px;padding:0 16px;border-radius:8px;background:var(--soft);color:var(--ink2);font-size:14px;transition:background .15s,color .15s,box-shadow .15s}
& .ch.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1.5px var(--p)}
& .pin{display:flex;align-items:center;gap:10px;margin-bottom:10px}
& .pin label{flex:1;min-width:0;display:flex;align-items:center;gap:4px;height:44px;padding:0 12px;border-radius:8px;background:var(--soft);border:1px solid transparent;font-size:14px;color:var(--ink3)}
& .pin label:focus-within{border-color:var(--ink2);background:var(--card)}
& .pin input{flex:1;width:100%;min-width:0;border:0;outline:0;background:none;font:inherit;font-size:14px;color:var(--ink)}
& .pin i{width:12px;height:1px;background:var(--n9)}
& .sh-f{flex:none;display:flex;gap:10px;padding:12px 20px 16px;border-top:1px solid var(--line)}
& .sh-f button{height:44px;border-radius:22px;font-size:16px;font-weight:600}
& .sh-f .rs{flex:none;width:96px;background:var(--soft);color:var(--ink2)}
& .sh-f .go{flex:1;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;box-shadow:0 5px 12px rgba(var(--p-rgb),.2)}
& .sh-f button:active{transform:scale(.98)}
${ICO}`),
    html: () => `<div class="mplist002"><div class="fb"><div class="qc" data-ix="drag">${['包邮', '现货', '新品', '有券'].map((t) => `<button type="button" data-tag="${t}">${t}</button>`).join('')}</div><button class="fbtn" type="button" data-open="flt">筛选${I('filter')}<b class="bdg">0</b></button></div><div class="ap"></div><div class="sm">共 <b data-n>${FP.length}</b> 件商品</div><div class="ls">${FP.map(([n, p, c, tg, im]) => `<div class="pr" data-ct="${c}" data-price="${p}" data-tags="${tg}"><img src="${P(im)}" alt=""><div class="tx"><h5>${n}</h5><div class="tgs">${tg.split(' ').map((t) => `<span class="tg tg-soft">${t}</span>`).join('')}</div><span class="price"><small>¥</small><b>${p}</b></span></div></div>`).join('')}<div class="emp" hidden>${I('mc_nosearch')}<span>没有符合条件的商品</span><button type="button" data-clear>清除筛选</button></div></div><div class="ix-ov" data-ov="flt"><div class="ix-mask"></div><div class="sheet" role="dialog" aria-label="筛选"><div class="sh-h"><b>筛选</b><button class="x" type="button" data-close aria-label="关闭">${I('close')}</button></div><div class="sh-b"><h6>品类</h6><div class="chs">${['数码', '鞋包', '居家', '美妆'].map((c) => `<button class="ch" type="button" data-ct="${c}">${c}</button>`).join('')}</div><h6>价格区间（元）</h6><div class="pin"><label>¥<input type="text" inputmode="numeric" placeholder="最低价" data-k="min" maxlength="5"></label><i></i><label>¥<input type="text" inputmode="numeric" placeholder="最高价" data-k="max" maxlength="5"></label></div><div class="chs">${[['100 以下', '', 100], ['100–300', 100, 300], ['300–600', 300, 600], ['600 以上', 600, '']].map(([t, a, b]) => `<button class="ch" type="button" data-rg="${a}|${b}">${t}</button>`).join('')}</div></div><div class="sh-f"><button class="rs" type="button" data-reset>重置</button><button class="go" type="button" data-close data-ok>确定 · 共 <span data-pn>${FP.length}</span> 件</button></div></div></div></div>`,
    js: (root) => {
      const el = root.querySelector('.mplist002'), rows = [...el.querySelectorAll('.pr')], emp = el.querySelector('.emp'), ap = el.querySelector('.ap')
      const A = { cats: new Set(), min: '', max: '' }, Pn = { cats: new Set(), min: '', max: '' }, tags = new Set()
      const ok = (r, st) => { const p = +r.dataset.price, t = r.dataset.tags.split(' '); return (!st.cats.size || st.cats.has(r.dataset.ct)) && (st.min === '' || p >= +st.min) && (st.max === '' || p <= +st.max) && [...tags].every((x) => t.includes(x)) }
      const paint = () => {
        let n = 0; rows.forEach((r) => { const m = ok(r, A); r.hidden = !m; if (m) n++ })
        el.querySelector('.sm [data-n]').textContent = n; emp.hidden = n > 0
        const chips = [...A.cats].map((c) => ['cat', c, c]); if (A.min !== '' || A.max !== '') chips.push(['price', '', '¥' + (A.min === '' ? '0' : A.min) + (A.max === '' ? ' 以上' : '–' + A.max)])
        ap.innerHTML = chips.map(([k, v, t]) => `<span>${t}<button type="button" data-rm="${k}" data-v="${v}" aria-label="移除${t}"><i class="i">${sv('close')}</i></button></span>`).join('')
        const fb = el.querySelector('.fbtn'), cnt = A.cats.size + (A.min !== '' || A.max !== '' ? 1 : 0)
        fb.classList.toggle('has', cnt > 0); fb.querySelector('.bdg').textContent = cnt
        el.querySelectorAll('.qc button').forEach((b) => b.classList.toggle('on', tags.has(b.dataset.tag)))
      }
      const paintSheet = () => {
        el.querySelectorAll('.sheet [data-ct]').forEach((b) => b.classList.toggle('on', Pn.cats.has(b.dataset.ct)))
        el.querySelectorAll('.sheet [data-rg]').forEach((b) => b.classList.toggle('on', b.dataset.rg === Pn.min + '|' + Pn.max))
        el.querySelector('[data-k=min]').value = Pn.min; el.querySelector('[data-k=max]').value = Pn.max
        el.querySelector('[data-pn]').textContent = rows.filter((r) => ok(r, Pn)).length
      }
      el.querySelector('.qc').addEventListener('click', (e) => { const b = e.target.closest('[data-tag]'); if (!b) return; tags.has(b.dataset.tag) ? tags.delete(b.dataset.tag) : tags.add(b.dataset.tag); paint() })
      el.querySelector('.fbtn').addEventListener('click', () => { Pn.cats = new Set(A.cats); Pn.min = A.min; Pn.max = A.max; paintSheet() })
      const sheet = el.querySelector('.sheet')
      sheet.addEventListener('click', (e) => {
        const c = e.target.closest('[data-ct]'), g = e.target.closest('[data-rg]')
        if (c) { Pn.cats.has(c.dataset.ct) ? Pn.cats.delete(c.dataset.ct) : Pn.cats.add(c.dataset.ct); paintSheet() }
        if (g) { const [a, b] = g.dataset.rg.split('|'); if (Pn.min === a && Pn.max === b) { Pn.min = ''; Pn.max = '' } else { Pn.min = a; Pn.max = b } paintSheet() }
        if (e.target.closest('[data-reset]')) { Pn.cats.clear(); Pn.min = ''; Pn.max = ''; paintSheet() }
        if (e.target.closest('[data-ok]')) { A.cats = new Set(Pn.cats); A.min = Pn.min; A.max = Pn.max; paint() }
      })
      sheet.addEventListener('input', (e) => { const k = e.target.dataset.k; if (!k) return; e.target.value = e.target.value.replace(/\D/g, ''); Pn[k] = e.target.value; el.querySelectorAll('.sheet [data-rg]').forEach((b) => b.classList.toggle('on', b.dataset.rg === Pn.min + '|' + Pn.max)); el.querySelector('[data-pn]').textContent = rows.filter((r) => ok(r, Pn)).length })
      ap.addEventListener('click', (e) => { const b = e.target.closest('[data-rm]'); if (!b) return; if (b.dataset.rm === 'cat') A.cats.delete(b.dataset.v); else { A.min = ''; A.max = '' } paint() })
      el.querySelector('[data-clear]').addEventListener('click', () => { A.cats.clear(); A.min = ''; A.max = ''; tags.clear(); paint() })
      paint()
    },
  })

  /* MP-LIST-003 */
  const SORTP = [['无线降噪耳机', '石墨灰 · 主动降噪', 599, 799, 2386, 0, 0], ['轻量跑鞋', '云白 · 男女同款', 329, 429, 1204, 1, 1], ['陶瓷马克杯', '手作釉面 · 350ml', 69, 89, 3112, 0, 2], ['帆布托特包', '原色 · 可放 14 寸', 159, 0, 987, 0, 3], ['护眼台灯', '无频闪 · 三档调光', 219, 0, 1533, 1, 5], ['保温水杯', '鼠尾草绿 · 500ml', 89, 119, 4208, 1, 6]]
  def({
    id: 'MP-LIST-003', name: '排序条与结果列表', style: '真排序',
    fit: '商品列表、搜索结果顶部；综合 / 销量 / 价格 / 新品真实排序，右侧可切换列表与网格',
    avoid: '排序项超过 5 个（收进筛选）；价格第一次点就反向会让人困惑，先升序再降序',
    kw: 'sort 排序 排序条 综合 销量 价格 升序 降序 新品 列表',
    css: S('mplist003', `&{width:340px;${CARD};overflow:hidden}
& .sb{display:flex;align-items:center;height:48px;padding:0 4px 0 8px;border-bottom:1px solid var(--line)}
& .sb button{display:flex;align-items:center;justify-content:center;gap:4px;height:48px;padding:0 12px;font-size:14px;color:var(--ink2);transition:color .15s}
& .sb .so{flex:1;padding:0}
& .sb .so.on{color:var(--p-fg);font-weight:600}
& .ar{display:flex;flex-direction:column;gap:2px}
& .ar i{width:0;height:0;border:4px solid transparent}
& .ar i:first-child{border-bottom:5px solid var(--n9);border-top:0}& .ar i:last-child{border-top:5px solid var(--n9);border-bottom:0}
& .so.asc .ar i:first-child{border-bottom-color:var(--p)}& .so.desc .ar i:last-child{border-top-color:var(--p)}
& .vw{flex:none;width:44px;padding:0!important;color:var(--ink2)!important}
& .vw .i{width:20px;height:20px}
& .sm{padding:10px 16px 0;font-size:12px;color:var(--ink3)}& .sm b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}
& .ls{padding:4px 12px 12px}
& .it{display:flex;gap:12px;padding:10px 0}
& .it img{width:84px;height:84px;border-radius:12px;object-fit:cover;flex:none;background:var(--ph)}
& .it .tx{flex:1;min-width:0;display:flex;flex-direction:column}
& .it h5{margin:0;font-size:14px;line-height:20px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .it .sp{margin-top:2px;font-size:12px;line-height:18px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .it .pr{margin-top:auto;display:flex;align-items:baseline;gap:4px}
& .it .price b{font-size:18px}
& .it .sl{margin-left:auto;font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
& .it .tg{margin-left:4px;height:18px;border-radius:4px}
& .ls.g2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
& .g2 .it{flex-direction:column;gap:8px;padding:0}
& .g2 .it img{width:100%;height:auto;aspect-ratio:1/1}
& .g2 .it .pr{margin-top:6px;flex-wrap:wrap;row-gap:2px}
& .g2 .it .sl{flex-basis:100%;margin-left:0}
${ICO}`),
    html: () => `<div class="mplist003"><div class="sb"><button class="so on" type="button" data-s="def">综合</button><button class="so" type="button" data-s="sales">销量</button><button class="so" type="button" data-s="price">价格<span class="ar"><i></i><i></i></span></button><button class="so" type="button" data-s="new">新品</button><button class="vw" type="button" aria-label="切换列表与网格">${I('list', 'v1')}${I('mc_cards', 'v2')}</button></div><div class="sm">共 <b>${SORTP.length}</b> 件 · <span data-sl>综合排序</span></div><div class="ls">${SORTP.map(([n, sp, p, o, sl, nw, im], i) => `<div class="it" data-i="${i}" data-sales="${sl}" data-price="${p}" data-new="${nw}"><img src="${P(im)}" alt=""><div class="tx"><h5>${n}${nw ? '<span class="tg tg-soft">新品</span>' : ''}</h5><span class="sp">${sp}</span><div class="pr">${priceHTML(p, o)}<span class="sl">月售 ${sl.toLocaleString('en-US')}</span></div></div></div>`).join('')}</div></div>`,
    js: (root) => {
      const el = root.querySelector('.mplist003'), ls = el.querySelector('.ls'), btns = [...el.querySelectorAll('.so')], vw = el.querySelector('.vw'), lab = el.querySelector('[data-sl]')
      const v1 = vw.querySelector('.v1'), v2 = vw.querySelector('.v2'); v2.style.display = 'none'
      let mode = 'def', dir = 'asc'
      const flip = (fn) => {
        const old = new Map([...ls.children].map((c) => [c, c.getBoundingClientRect()])); fn()
        ;[...ls.children].forEach((c) => { const a = old.get(c), b = c.getBoundingClientRect(), dx = a.left - b.left, dy = a.top - b.top; if (dx || dy) { c.style.transition = 'none'; c.style.transform = 'translate(' + dx + 'px,' + dy + 'px)'; requestAnimationFrame(() => requestAnimationFrame(() => { c.style.transition = 'transform .3s cubic-bezier(.2,0,0,1)'; c.style.transform = '' })) } })
      }
      const sortNow = () => {
        const items = [...ls.children], n = (c, k) => +c.dataset[k]
        items.sort((a, b) => mode === 'sales' ? n(b, 'sales') - n(a, 'sales') : mode === 'price' ? (dir === 'asc' ? n(a, 'price') - n(b, 'price') : n(b, 'price') - n(a, 'price')) : mode === 'new' ? n(b, 'new') - n(a, 'new') || n(a, 'i') - n(b, 'i') : n(a, 'i') - n(b, 'i'))
        flip(() => items.forEach((c) => ls.appendChild(c)))
        lab.textContent = { def: '综合排序', sales: '销量从高到低', price: dir === 'asc' ? '价格从低到高' : '价格从高到低', new: '新品优先' }[mode]
      }
      btns.forEach((b) => b.addEventListener('click', () => {
        const k = b.dataset.s
        if (k === 'price') dir = mode === 'price' && dir === 'asc' ? 'desc' : 'asc'
        mode = k
        btns.forEach((x) => { x.classList.toggle('on', x === b); x.classList.toggle('asc', x === b && k === 'price' && dir === 'asc'); x.classList.toggle('desc', x === b && k === 'price' && dir === 'desc') })
        sortNow()
      }))
      vw.addEventListener('click', () => { flip(() => { const g = ls.classList.toggle('g2'); v1.style.display = g ? 'none' : ''; v2.style.display = g ? '' : 'none' }) })
    },
  })

  /* MP-LIST-004 */
  const SRCH = [
    ['保温水杯', '500ml · 鼠尾草绿', 89, 6], ['陶瓷马克杯', '手作釉面 · 350ml', 69, 2], ['玻璃咖啡杯套装', '双层隔热 · 2 只装', 129, 2], ['316 不锈钢随行杯', '防漏 · 400ml', 99, 6],
    ['无线降噪耳机', '石墨灰 · 主动降噪', 599, 0], ['护眼台灯', '无频闪 · 三档调光', 219, 5], ['轻量跑鞋', '云白 · 男女同款', 329, 1], ['帆布托特包', '原色 · 可放 14 寸', 159, 3],
  ]
  const hotQ = ['降噪耳机', '水杯', '护眼台灯', '轻量跑鞋', '托特包']
  def({
    id: 'MP-LIST-004', name: '搜索结果页头', style: '关键词高亮',
    fit: '搜索结果页；顶部搜索框可改词，结果里关键词高亮并写明结果数，空输入给最近搜索与热搜',
    avoid: '结果数很少时仍写“共 N 页”；无结果只写“没有结果”而不给换词建议',
    kw: 'search result 搜索结果 关键词 高亮 搜索框 最近搜索 热搜 无结果 联想',
    css: S('mplist004', `&{width:340px;min-height:500px;${CARD};overflow:hidden}
& .sh{display:flex;align-items:center;gap:4px;padding:8px 4px 8px 4px}
& .bk{flex:none;width:44px;height:44px;display:flex;align-items:center;justify-content:center;color:var(--ink)}
& .bk .i{width:20px;height:20px}
& .fld{flex:1;min-width:0;display:flex;align-items:center;gap:8px;height:44px;padding:0 4px 0 14px;border-radius:22px;background:var(--soft);border:1px solid transparent;color:var(--ink3)}
& .fld:focus-within{border-color:var(--ink2);background:var(--card)}
& .fld .i{width:18px;height:18px}
& .fld input{flex:1;min-width:0;border:0;outline:0;background:none;font:inherit;font-size:14px;color:var(--ink)}
& .fld input::placeholder{color:var(--ink3)}
& .clr{flex:none;width:36px;height:36px;display:flex;align-items:center;justify-content:center;color:var(--ink5)}
& .clr .i{width:18px;height:18px}
& .go{flex:none;min-width:56px;height:44px;padding:0 8px;font-size:14px;font-weight:600;color:var(--p-text)}
& .sum{padding:6px 16px 4px;font-size:14px;color:var(--ink2)}& .sum b{font-weight:600;color:var(--ink)}& .sum em{color:var(--p-text);font-weight:600}
& .rel{display:flex;align-items:center;gap:8px;padding:6px 16px 8px;overflow-x:auto;scrollbar-width:none;font-size:12px;color:var(--ink3);white-space:nowrap}
& .rel::-webkit-scrollbar{display:none}
& .chip{position:relative;flex:none;height:28px;padding:0 12px;border-radius:8px;background:var(--soft);color:var(--ink2);font-size:12px}
& .chip::before{content:"";position:absolute;inset:-8px -2px}
& .ls{list-style:none;margin:0;padding:0 16px 12px}
& .ls li{display:flex;gap:12px;padding:10px 0;border-top:1px solid var(--line)}
& .ls li:first-child{border-top:0}
& .ls img{width:64px;height:64px;border-radius:12px;object-fit:cover;flex:none;background:var(--ph)}
& .ls .tx{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:space-between}
& .ls h5{margin:0;font-size:14px;line-height:20px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .ls .sp{font-size:12px;line-height:18px;color:var(--ink3)}
& .ls .price b{font-size:18px}
& mark{background:var(--pm);color:var(--p-text);border-radius:4px;padding:0 1px}
& .pn-sug{padding:4px 16px 16px}
& .pn-sug h6{display:flex;align-items:center;justify-content:space-between;margin:12px 0 10px;font-size:14px;font-weight:600}
& .pn-sug h6 button{width:44px;height:44px;margin:-12px -12px -12px 0;display:flex;align-items:center;justify-content:center;color:var(--ink3)}
& .pn-sug h6 .i{width:18px;height:18px}
& .chips{display:flex;flex-wrap:wrap;gap:10px}
& .chips .chip{height:32px;padding:0 14px;font-size:14px}
& .tp3{list-style:none;margin:0;padding:0}
& .tp3 li{display:flex;align-items:center;gap:12px;height:44px;font-size:14px;cursor:pointer}
& .tp3 li i{flex:none;width:20px;font-style:normal;text-align:center;font-weight:600;color:var(--ink3);font-variant-numeric:tabular-nums}
& .tp3 li:nth-child(-n+3) i{color:var(--p-fg)}
& .pn-none{display:flex;flex-direction:column;align-items:center;gap:8px;padding:36px 20px 20px;text-align:center}
& .pn-none .big{display:flex;width:64px;height:64px;border-radius:50%;background:var(--pt);color:var(--p-fg);align-items:center;justify-content:center}
& .pn-none .big .i{width:32px;height:32px}
& .pn-none b{font-size:16px;font-weight:600;line-height:24px;word-break:break-all}
& .pn-none p{margin:0;font-size:14px;color:var(--ink2)}
& .pn-none .chips{justify-content:center;margin-top:8px}
${ICO}`),
    html: () => `<div class="mplist004"><div class="sh"><button class="bk" type="button" aria-label="返回" data-toast="返回上一页">${I('back')}</button><label class="fld">${I('search')}<input type="text" value="杯" placeholder="搜索商品、品牌" aria-label="搜索关键词" enterkeyhint="search"><button class="clr" type="button" aria-label="清空">${I('closec')}</button></label><button class="go" type="button">搜索</button></div><div class="pn-res"><div class="sum">找到 <b data-n>4</b> 件“<em data-kw>杯</em>”相关商品</div><div class="rel"><span>相关搜索</span>${['保温水杯', '马克杯', '咖啡杯'].map((q) => `<button class="chip" type="button" data-q="${q}">${q}</button>`).join('')}</div><ul class="ls">${SRCH.map(([n, sp, p, im]) => `<li data-name="${n}" data-sp="${sp}"><img src="${P(im)}" alt=""><div class="tx"><h5>${n}</h5><span class="sp">${sp}</span><span class="price"><small>¥</small><b>${p}</b></span></div></li>`).join('')}</ul></div><div class="pn-none" hidden><span class="big">${I('mc_nosearch')}</span><b>没有找到“<span data-kw>杯</span>”</b><p>换个词试试，或看看大家都在搜</p><div class="chips">${hotQ.slice(0, 4).map((q) => `<button class="chip" type="button" data-q="${q}">${q}</button>`).join('')}</div></div><div class="pn-sug" hidden><div class="rc"><h6>最近搜索<button type="button" data-clr aria-label="清空最近搜索">${I('trash')}</button></h6><div class="chips">${['马克杯', '跑鞋', '台灯', '双肩包'].map((q) => `<button class="chip" type="button" data-q="${q}">${q}</button>`).join('')}</div></div><h6>大家都在搜</h6><ul class="tp3">${hotQ.map((q, i) => `<li data-q="${q}"><i>${i + 1}</i>${q}</li>`).join('')}</ul></div></div>`,
    js: (root) => {
      const el = root.querySelector('.mplist004'), inp = el.querySelector('input'), clr = el.querySelector('.clr'), rows = [...el.querySelectorAll('.ls li')]
      const res = el.querySelector('.pn-res'), none = el.querySelector('.pn-none'), sug = el.querySelector('.pn-sug')
      const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]))
      const hi = (t, q) => { let out = '', lo = t.toLowerCase(), ql = q.toLowerCase(), p = 0, k; while ((k = lo.indexOf(ql, p)) > -1) { out += esc(t.slice(p, k)) + '<mark>' + esc(t.slice(k, k + q.length)) + '</mark>'; p = k + q.length } return out + esc(t.slice(p)) }
      const update = () => {
        const q = inp.value.trim(); clr.hidden = !inp.value
        if (!q) { res.hidden = true; none.hidden = true; sug.hidden = false; return }
        sug.hidden = true
        let n = 0
        rows.forEach((r) => { const m = (r.dataset.name + ' ' + r.dataset.sp).toLowerCase().includes(q.toLowerCase()); r.hidden = !m; if (m) { n++; r.querySelector('h5').innerHTML = hi(r.dataset.name, q) } })
        res.hidden = n === 0; none.hidden = n > 0
        el.querySelector('[data-n]').textContent = n
        el.querySelectorAll('[data-kw]').forEach((k) => (k.textContent = q))
      }
      inp.addEventListener('input', update)
      clr.addEventListener('click', () => { inp.value = ''; inp.focus(); update() })
      el.addEventListener('click', (e) => { const c = e.target.closest('[data-q]'); if (c) { inp.value = c.dataset.q; update() } })
      el.querySelector('.go').addEventListener('click', () => { if (!inp.value.trim()) IX.toast(root, '请输入搜索关键词'); else update() })
      inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') { if (!inp.value.trim()) IX.toast(root, '请输入搜索关键词'); else update() } })
      const dc = el.querySelector('[data-clr]'); if (dc) dc.addEventListener('click', () => { el.querySelector('.rc').hidden = true })
      update()
    },
  })

  /* MP-LIST-005 */
  const ODR = (r) => `<div class="od"><img src="${P(r.img)}" alt=""><div class="tx"><h5>${r.sku}</h5><span class="sp">× ${r.q} · ${r.at}</span></div><div class="rg"><b><small>¥</small>${r.amt.toLocaleString('en-US')}</b><span class="sx ${r.tone}">${r.st}</span></div></div>`
  def({
    id: 'MP-LIST-005', name: '滚动加载列表', style: '失败重试',
    fit: '订单、消息、浏览记录等长列表；滑到底自动加载，失败可点重试，加载完写“没有更多了”',
    avoid: '用页码翻页（小程序用滚动加载）；加载失败只弹一下轻提示就让列表停在那里',
    kw: 'infinite scroll 滚动加载 上拉加载 分页 加载中 没有更多 加载失败 重试 订单列表',
    css: S('mplist005', `&{width:340px;${CARD};overflow:hidden}
& .hd{display:flex;align-items:baseline;justify-content:space-between;height:52px;padding:0 16px;align-items:center;border-bottom:1px solid var(--line)}
& .hd b{font-size:16px;font-weight:600}& .hd span{font-size:12px;color:var(--ink3);font-variant-numeric:tabular-nums}
& .sc{height:384px;overflow-y:auto;padding:0 16px;scrollbar-width:thin}
& .od{display:flex;align-items:center;gap:12px;min-height:72px;padding:10px 0;border-bottom:1px solid var(--line)}
& .od.nw{animation:@@in .35s cubic-bezier(.2,0,0,1)}
@keyframes @@in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
& .od img{width:52px;height:52px;border-radius:12px;object-fit:cover;flex:none;background:var(--ph)}
& .od .tx{flex:1;min-width:0}
& .od h5{margin:0;font-size:14px;line-height:20px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .od .sp{display:block;margin-top:2px;font-size:12px;line-height:18px;color:var(--ink3)}
& .rg{flex:none;display:flex;flex-direction:column;align-items:flex-end;gap:4px}
& .rg b{font-size:16px;font-weight:600;font-variant-numeric:tabular-nums}& .rg b small{font-size:12px;font-weight:600;margin-right:1px}
& .sx{height:20px;padding:0 8px;border-radius:4px;font-size:12px;font-weight:600;display:inline-flex;align-items:center}
& .sx.ok{background:var(--ok-bg);color:var(--ok)}& .sx.warn{background:var(--warn-bg);color:var(--warn)}& .sx.danger{background:var(--danger-bg);color:var(--danger)}& .sx.info{background:var(--pt);color:var(--p-text)}& .sx.mute{background:var(--soft);color:var(--ink3)}
& .ftr{display:flex;align-items:center;justify-content:center;gap:8px;min-height:56px;font-size:12px;color:var(--ink3)}
& .ftr .again{display:inline-flex;align-items:center;gap:6px;height:44px;padding:0 16px;border-radius:22px;background:var(--danger-bg);color:var(--danger);font-size:14px;font-weight:600}
& .ftr .again .i{width:16px;height:16px}
& .ftr .endl{display:flex;align-items:center;gap:12px}
& .ftr .endl::before,& .ftr .endl::after{content:"";width:40px;height:1px;background:var(--n7)}
${ICO}${SPIN}`),
    html: () => `<div class="mplist005"><div class="hd"><b>全部订单</b><span>已加载 <b data-c style="font-size:12px;font-weight:600;color:var(--ink2)">8</b> / ${ORDER_ROWS.length}</span></div><div class="sc">${ORDER_ROWS.slice(0, 8).map(ODR).join('')}<template class="pg">${ORDER_ROWS.slice(8, 16).map(ODR).join('')}</template><template class="pg">${ORDER_ROWS.slice(16, 24).map(ODR).join('')}</template><div class="ftr" data-st="idle"><span>上拉加载更多</span></div></div></div>`,
    js: (root) => {
      const sc = root.querySelector('.sc'), ftr = root.querySelector('.ftr'), cnt = root.querySelector('[data-c]'), tpls = [...root.querySelectorAll('template')]
      let st = 'idle', page = 0, failed = false
      const view = { idle: () => '<span>上拉加载更多</span>', load: () => '<i class="spin"></i><span>加载中…</span>', fail: () => '<button class="again" type="button"><i class="i">' + sv('refresh') + '</i>加载失败，点击重试</button>', end: () => '<span class="endl">没有更多了</span>' }
      const set = (s) => { st = s; ftr.dataset.st = s; ftr.innerHTML = view[s]() }
      const run = () => {
        if (st === 'load' || st === 'end') return
        set('load')
        setTimeout(() => {
          if (!root.isConnected) return
          if (page === 1 && !failed) { failed = true; set('fail'); return }
          const t = tpls[page++]; const w = document.createElement('div'); w.innerHTML = t.innerHTML
          ;[...w.children].forEach((c) => { c.classList.add('nw'); sc.insertBefore(c, ftr) })
          cnt.textContent = sc.querySelectorAll('.od').length
          set(page >= tpls.length ? 'end' : 'idle')
        }, 900)
      }
      sc.addEventListener('scroll', () => { if (st === 'idle' && sc.scrollTop + sc.clientHeight >= sc.scrollHeight - 48) run() })
      ftr.addEventListener('click', (e) => { if (e.target.closest('.again')) run() })
    },
  })

  /* MP-LIST-006 */
  const CITY = [['A', '安庆 鞍山'], ['B', '北京 保定 包头'], ['C', '成都 重庆 长沙 常州'], ['D', '大连 东莞'], ['F', '福州 佛山'], ['G', '广州 贵阳 桂林'], ['H', '杭州 合肥 哈尔滨'], ['J', '济南 嘉兴'], ['N', '南京 宁波 南昌'], ['S', '上海 深圳 苏州 沈阳'], ['T', '天津 太原'], ['W', '武汉 无锡'], ['X', '西安 厦门'], ['Z', '郑州 珠海 中山']]
  def({
    id: 'MP-LIST-006', name: '字母索引条', style: '点击跳转',
    fit: '城市选择、品牌列表、通讯录；右侧字母条可点可拖，拖动时放大提示当前字母，滚动时同步高亮',
    avoid: '条目少于 20 个（直接平铺）；索引字母小于 12px 或点击区小于 44px 高的整条',
    kw: 'index bar 字母索引 城市选择 通讯录 品牌 A-Z 拼音 跳转 吸顶标题',
    css: S('mplist006', `&{width:340px;height:456px;${CARD};overflow:hidden;display:flex;flex-direction:column}
& .hd{flex:none;display:flex;align-items:center;height:48px;padding:0 4px;border-bottom:1px solid var(--line)}
& .hd b{flex:1;text-align:center;font-size:16px;font-weight:600;margin-right:44px}
& .hd button{width:44px;height:44px;display:flex;align-items:center;justify-content:center}
& .hd .i{width:20px;height:20px}
& .loc{flex:none;display:flex;align-items:center;gap:8px;height:44px;padding:0 16px;font-size:14px;color:var(--ink2);background:var(--pt)}
& .loc .i{width:16px;height:16px;color:var(--p-fg)}& .loc b{color:var(--p-text);font-weight:600}
& .lw{position:relative;flex:1;min-height:0}
& .ls{position:absolute;inset:0;overflow-y:auto;scrollbar-width:none}
& .ls::-webkit-scrollbar{display:none}
& .ls h6{position:sticky;top:0;z-index:1;margin:0;height:32px;padding:0 16px;background:var(--n3);font-size:12px;line-height:32px;font-weight:600;color:var(--ink2)}
& .hot{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:12px 40px 14px 16px}
& .hot button{height:44px;border-radius:8px;background:var(--soft);font-size:14px;color:var(--ink);transition:background .15s}
& .hot button.on{background:var(--pt);color:var(--p-text);font-weight:600;box-shadow:inset 0 0 0 1.5px var(--p)}
& .ct{list-style:none;margin:0;padding:0}
& .ct li{display:flex;align-items:center;justify-content:space-between;height:48px;margin-left:16px;padding-right:44px;border-bottom:1px solid var(--line);font-size:16px;cursor:pointer}
& .ct li:last-child{border-bottom:0}
& .ct li.on{color:var(--p-text);font-weight:600}
& .ct li .i{display:none;width:18px;height:18px;color:var(--p-fg)}& .ct li.on .i{display:inline-flex}
& .ib{position:absolute;right:4px;top:50%;transform:translateY(-50%);z-index:2;display:flex;flex-direction:column;align-items:center;width:28px;padding:6px 0;border-radius:16px;touch-action:none;user-select:none;cursor:pointer}
& .ib button{width:22px;height:18px;border-radius:16px;font-size:12px;line-height:18px;color:var(--ink3);cursor:pointer}
& .ib button.on{background:var(--p);color:#fff;font-weight:600}
& .bub{position:absolute;left:50%;top:50%;z-index:3;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:16px;background:color-mix(in srgb,var(--scrim) 78%,transparent);color:#fff;font-size:22px;font-weight:700;display:flex;align-items:center;justify-content:center;pointer-events:none}
${ICO}`),
    html: () => `<div class="mplist006"><div class="hd"><button type="button" aria-label="返回" data-toast="返回上一页">${I('back')}</button><b>选择城市</b></div><div class="loc">${I('pin')}当前城市<b data-cur>杭州</b></div><div class="lw"><div class="ls"><section class="sec" data-l="热"><h6>热门城市</h6><div class="hot">${['北京', '上海', '广州', '深圳', '杭州', '成都'].map((c) => `<button type="button" data-c="${c}" class="${c === '杭州' ? 'on' : ''}">${c}</button>`).join('')}</div></section>${CITY.map(([l, cs]) => `<section class="sec" data-l="${l}"><h6>${l}</h6><ul class="ct">${cs.split(' ').map((c) => `<li data-c="${c}" class="${c === '杭州' ? 'on' : ''}">${c}${I('check')}</li>`).join('')}</ul></section>`).join('')}<div class="pad"></div></div><div class="ib" aria-label="字母索引">${['热'].concat(CITY.map((c) => c[0])).map((l, i) => `<button type="button" class="${i ? '' : 'on'}">${l}</button>`).join('')}</div><div class="bub" hidden>热</div></div></div>`,
    js: (root) => {
      const ls = root.querySelector('.ls'), secs = [...ls.querySelectorAll('.sec')], ib = root.querySelector('.ib'), bub = root.querySelector('.bub'), btns = [...ib.querySelectorAll('button')], pad = ls.querySelector('.pad')
      pad.style.height = Math.max(0, ls.clientHeight - secs[secs.length - 1].offsetHeight) + 'px'
      let drag = false, bt = 0
      const mark = (i) => btns.forEach((b, k) => b.classList.toggle('on', k === i))
      const jump = (i, show) => {
        ls.scrollTop = secs[i].offsetTop; mark(i)
        if (show) { bub.textContent = secs[i].dataset.l; bub.hidden = false; clearTimeout(bt); bt = setTimeout(() => { bub.hidden = true }, 700) }
      }
      ls.addEventListener('scroll', () => { let i = 0; secs.forEach((s, k) => { if (s.offsetTop <= ls.scrollTop + 1) i = k }); mark(i) })
      const pick = (y) => { const r = btns[0].getBoundingClientRect(); const i = Math.max(0, Math.min(btns.length - 1, Math.floor((y - r.top) / r.height))); jump(i, true) }
      ib.addEventListener('pointerdown', (e) => { drag = true; ib.setPointerCapture(e.pointerId); pick(e.clientY) })
      ib.addEventListener('pointermove', (e) => { if (drag) pick(e.clientY) })
      const up = () => { drag = false }
      ib.addEventListener('pointerup', up); ib.addEventListener('pointercancel', up)
      ib.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b && e.detail === 0) jump(btns.indexOf(b), true) })
      ls.addEventListener('click', (e) => {
        const c = e.target.closest('[data-c]'); if (!c) return
        const n = c.dataset.c
        ls.querySelectorAll('[data-c]').forEach((x) => x.classList.toggle('on', x.dataset.c === n))
        root.querySelector('[data-cur]').textContent = n
      })
    },
  })

  /* ================= STATE 状态与空态 ================= */
  guide('mp', 'STATE', [
    ['无订单、无收藏、无搜索结果、无网络', '空状态四场景', '插画 + 一句原因 + 一个下一步按钮；原因写具体，按钮写动作，别只说“暂无数据”'],
    ['页面首次进入、列表首屏', '骨架屏', '形状和真实内容一致，闪动提示在加载；内容出来后不要跳位'],
    ['接口失败、请求超时', '加载失败重试', '写清原因与错误码；点重试按钮变“加载中”但宽度不变，成功后原地出内容'],
    ['网络断开、弱网', '断网提示条', '挂在顶栏下，不挡内容；点重试显示连接中，恢复后变绿并自动收起'],
    ['支付、提交、审核结束', '结果页', '大图标 + 结论 + 原因 + 一个主按钮；失败页要有重试与另一条出路'],
    ['新功能上线、首次进入', '新手引导蒙层', '一次只高亮一个目标，给跳过与步数；最后一步写“知道了”，只出现一次'],
  ])

  const ILL = (icon) => `<div class="ill"><i class="bgc"></i><i class="d1"></i><i class="d2"></i><i class="d3"></i><span class="cd">${sv(icon)}</span></div>`
  const ILL_CSS = `& .ill{position:relative;width:140px;height:112px;margin:0 auto 16px}
& .ill .bgc{position:absolute;left:18px;top:4px;width:104px;height:104px;border-radius:50%;background:var(--pt)}
& .ill .d1{position:absolute;right:10px;top:14px;width:10px;height:10px;border-radius:50%;background:var(--pm)}
& .ill .d2{position:absolute;left:8px;bottom:22px;width:8px;height:8px;border-radius:50%;background:var(--p);opacity:.35}
& .ill .d3{position:absolute;right:20px;bottom:10px;width:14px;height:14px;border-radius:4px;background:var(--pm);transform:rotate(18deg)}
& .ill .cd{position:absolute;left:38px;top:24px;width:64px;height:64px;padding:16px;border-radius:16px;background:var(--card);color:var(--p-fg);box-shadow:0 8px 20px rgba(var(--p-rgb),.16);animation:@@fl 3.2s ease-in-out infinite}
& .ill .cd svg{display:block}
@keyframes @@fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
@media(prefers-reduced-motion:reduce){& .ill .cd{animation:none}}`
  const EMP = [
    ['od', '无订单', 'receipt', '还没有订单', '挑几件喜欢的，下单后可在这里查看', '去逛逛', '去首页逛逛'],
    ['sr', '无结果', 'mc_nosearch', '没有找到相关商品', '换个关键词，或者少选几个筛选条件试试', '清除筛选', '已清除筛选条件'],
    ['nw', '无网络', 'mc_wifioff', '网络好像断了', '请检查 Wi-Fi 或移动网络后重试', '重新加载', '网络仍未连接，请稍后再试'],
    ['fv', '无收藏', 'heart', '收藏夹是空的', '看到喜欢的商品点一下心形，就会收在这里', '去看看', '去看看热门商品'],
  ]
  def({
    id: 'MP-STATE-001', name: '空状态四场景', style: '带下一步',
    fit: '无订单、无搜索结果、无网络、无收藏；插画加一句具体原因，只留一个下一步按钮',
    avoid: '只写“暂无数据”；同一页放两个同等强度的按钮；插画比内容还抢眼',
    kw: 'empty 空状态 空页面 无数据 无订单 无结果 无网络 无收藏 插画 缺省页',
    css: S('mpstate001', `&{width:340px;${CARD};padding:12px 12px 28px}
& .sg{display:flex;background:var(--soft);border-radius:12px;padding:2px}
& .sg button{flex:1;height:36px;border-radius:8px;font-size:14px;color:var(--ink2);transition:background .15s,color .15s}
& .sg button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:0 1px 4px var(--sh12)}
& .pn{display:flex;flex-direction:column;align-items:center;padding:28px 12px 0;text-align:center;min-height:268px}
& .pn:not([hidden]){animation:@@in .3s cubic-bezier(.2,0,0,1)}
@keyframes @@in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
& h4{margin:0;font-size:16px;line-height:24px;font-weight:600}
& .pn p{margin:6px 0 20px;max-width:240px;font-size:14px;line-height:22px;color:var(--ink2)}
& .act{min-width:140px;height:44px;padding:0 24px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:16px;font-weight:600;box-shadow:0 5px 12px rgba(var(--p-rgb),.2);transition:transform .15s}
& .act:active{transform:scale(.97)}
${ILL_CSS}`),
    html: () => `<div class="mpstate001"><div class="sg" data-ix="tabs" data-g="em">${EMP.map(([k, n], i) => `<button type="button" data-t="${k}" class="${i ? '' : 'on'}">${n}</button>`).join('')}</div>${EMP.map(([k, , ic, t, d, b, toast], i) => `<div class="pn" data-p="${k}" data-g="em"${i ? ' hidden' : ''}>${ILL(ic)}<h4>${t}</h4><p>${d}</p><button class="act" type="button" data-toast="${toast}">${b}</button></div>`).join('')}</div>`,
  })

  /* MP-STATE-002 */
  def({
    id: 'MP-STATE-002', name: '骨架屏', style: '闪动',
    fit: '页面首次进入、列表首屏、详情页；用和真实内容一致的灰块占位，闪动提示正在加载',
    avoid: '加载很快（<300ms）时别闪一下骨架；骨架形状与真实内容差别大，出内容时会跳位',
    kw: 'skeleton 骨架屏 占位 加载中 shimmer loading 闪动 首屏 placeholder',
    css: S('mpstate002', `&{width:340px}
& .box{${CARD};padding:16px}
& .sk i{display:block;border-radius:8px;background:linear-gradient(90deg,var(--n4) 25%,var(--n2) 37%,var(--n4) 63%);background-size:400% 100%;animation:@@sh 1.4s ease infinite}
@keyframes @@sh{0%{background-position:100% 50%}100%{background-position:0 50%}}
@media(prefers-reduced-motion:reduce){& .sk i{animation:none}}
& .hd{display:flex;align-items:center;gap:10px;height:40px}
& .hd .ln{flex:1;display:flex;flex-direction:column;gap:6px}
& .sk .av{width:40px;height:40px;border-radius:50%}
& .sk .l1{width:96px;height:14px}& .sk .l2{width:64px;height:12px}
& .sk .img{width:100%;aspect-ratio:16/9;margin-top:12px;border-radius:12px}
& .sk .tt{margin-top:12px;display:flex;flex-direction:column;gap:12px;height:48px}
& .sk .tt .l3{width:92%;height:16px}& .sk .tt .l4{width:60%;height:16px}
& .sk .fr{display:flex;gap:10px;margin-top:12px;height:28px}
& .sk .fr i{width:72px;height:28px}
& .ct .nm{display:flex;flex-direction:column}
& .ct .nm b{font-size:14px;line-height:20px;font-weight:600}& .ct .nm span{font-size:12px;line-height:18px;color:var(--ink3)}
& .ct .cv{width:100%;aspect-ratio:16/9;margin-top:12px;border-radius:12px;object-fit:cover;background:var(--ph)}
& .ct h4{margin:12px 0 0;height:48px;font-size:16px;line-height:24px;font-weight:600;${CLAMP(2)}}
& .ct .fr{display:flex;align-items:center;gap:10px;margin-top:12px;height:28px;font-size:12px;color:var(--ink3)}
& .ct .fr .tg{height:24px;border-radius:4px}
& .ct.in{animation:@@in .35s cubic-bezier(.2,0,0,1)}
@keyframes @@in{from{opacity:0}to{opacity:1}}
& .re{display:flex;align-items:center;justify-content:center;gap:6px;height:44px;margin:8px auto 0;padding:0 16px;font-size:14px;color:var(--ink2)}
& .re .i{width:16px;height:16px}
${ICO}`),
    html: () => `<div class="mpstate002"><div class="box"><div class="sk" aria-busy="true" aria-label="加载中"><div class="hd"><i class="av"></i><div class="ln"><i class="l1"></i><i class="l2"></i></div></div><i class="img"></i><div class="tt"><i class="l3"></i><i class="l4"></i></div><div class="fr"><i></i><i></i></div></div><div class="ct" hidden><div class="hd">${critter(0, 40)}<div class="nm"><b>桌面研究所</b><span>11-02 · 5 分钟读完</span></div></div><img class="cv" src="${P(5)}" alt=""><h4>办公桌灯怎么选：看懂色温、显色指数和频闪三个参数</h4><div class="fr"><span class="tg tg-soft">选购指南</span><span>2.1 万阅读</span><span>326 赞</span></div></div></div><button class="re" type="button" hidden>${I('refresh')}重新加载</button></div>`,
    js: (root) => {
      const sk = root.querySelector('.sk'), ct = root.querySelector('.ct'), re = root.querySelector('.re'); let t = 0
      const show = (loading) => { sk.hidden = !loading; ct.hidden = loading; re.hidden = loading; if (!loading) { ct.classList.remove('in'); void ct.offsetWidth; ct.classList.add('in') } }
      const start = () => { clearTimeout(t); show(true); t = setTimeout(() => { if (root.isConnected) show(false) }, 2400) }
      re.addEventListener('click', start); start()
    },
  })

  /* MP-STATE-003 */
  const REV = [['陈晓雨', 1, 5, '降噪很稳，地铁里基本听不到报站声，续航也够用一整周。', '11-02'], ['王子豪', 2, 4, '音质不错，就是耳翼偏硬，戴久了有点压。', '10-30'], ['赵可心', 3, 5, '包装很用心，快递第二天就到了，送人体面。', '10-27']]
  def({
    id: 'MP-STATE-003', name: '加载失败重试', style: '重试加载',
    fit: '接口失败、请求超时；写清原因与错误码，点重试按钮变加载中（宽度不变），成功后原地出内容',
    avoid: '只弹一下轻提示就让页面留白；失败页没有任何下一步；重试时按钮变宽导致跳动',
    kw: 'error 加载失败 重试 retry 超时 错误页 网络异常 请求失败 刷新 异常状态',
    css: S('mpstate003', `&{width:340px;${CARD};overflow:hidden}
& .hdr{display:flex;align-items:center;justify-content:space-between;height:52px;padding:0 16px;border-bottom:1px solid var(--line)}
& .hdr b{font-size:16px;font-weight:600}& .hdr span{font-size:12px;color:var(--ink3)}
& .pn-err{display:flex;flex-direction:column;align-items:center;padding:32px 24px 32px;text-align:center;min-height:300px;justify-content:center}
& .ic{display:flex;width:64px;height:64px;border-radius:50%;background:var(--danger-bg);color:var(--danger);align-items:center;justify-content:center;margin-bottom:14px}
& .ic svg{width:30px;height:30px}
& h4{margin:0;font-size:16px;line-height:24px;font-weight:600}
& .pn-err p{margin:6px 0 20px;font-size:14px;line-height:22px;color:var(--ink2)}
& .pn-err p small{display:block;margin-top:2px;font-size:12px;color:var(--ink3)}
& .rt{display:inline-flex;align-items:center;justify-content:center;gap:8px;width:148px;height:44px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:16px;font-weight:600;box-shadow:0 5px 12px rgba(var(--p-rgb),.2);transition:transform .15s}
& .rt:active{transform:scale(.97)}
& .rt:disabled{cursor:progress;transform:none}
& .rt .spin{display:none;border-color:rgba(255,255,255,.4);border-top-color:var(--card)}
&[data-st=load] .rt .spin{display:inline-block}
& .pn-ok{padding:4px 16px 0}
& .pn-ok.in{animation:@@in .35s cubic-bezier(.2,0,0,1)}
@keyframes @@in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
& .rv{display:flex;gap:10px;padding:14px 0;border-top:1px solid var(--line)}& .rv:first-child{border-top:0}
& .rv .m{flex:1;min-width:0}
& .rv .nm{display:flex;align-items:center;justify-content:space-between;font-size:14px;font-weight:600;line-height:20px}
& .rv .nm span{font-size:12px;font-weight:400;color:var(--ink3)}
& .rv .st5{display:flex;gap:2px;margin:2px 0 4px;color:#C99A3A}& .rv .st5 .i{width:14px;height:14px}& .rv .st5 .i svg{fill:currentColor}& .rv .st5 .off{color:var(--n7)}
& .rv p{margin:0;font-size:14px;line-height:22px;color:var(--ink)}
& .again{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;height:44px;border-top:1px solid var(--line);font-size:12px;color:var(--ink3)}
& .again .i{width:14px;height:14px}
${ICO}${SPIN}`),
    html: () => `<div class="mpstate003" data-st="err"><div class="hdr"><b>商品评价</b><span>共 1,286 条</span></div><div class="pn-err"><span class="ic">${sv('alert')}</span><h4>加载失败</h4><p>网络开小差了，请稍后重试<small>错误码 504 · 请求超时</small></p><button class="rt" type="button"><i class="spin"></i><span class="lbl">重试</span></button></div><div class="pn-ok" hidden>${REV.map(([n, av, st, t, d]) => `<div class="rv">${critter(av, 36)}<div class="m"><div class="nm">${n}<span>${d}</span></div><div class="st5">${[1, 2, 3, 4, 5].map((k) => I('starf', k > st ? 'off' : '')).join('')}</div><p>${t}</p></div></div>`).join('')}</div><button class="again" type="button" hidden>${I('refresh')}重新演示</button></div>`,
    js: (root) => {
      const el = root.querySelector('.mpstate003'), btn = el.querySelector('.rt'), err = el.querySelector('.pn-err'), ok = el.querySelector('.pn-ok'), again = el.querySelector('.again'); let t = 0
      btn.addEventListener('click', () => {
        if (btn.disabled) return
        btn.disabled = true; el.dataset.st = 'load'; btn.querySelector('.lbl').textContent = '加载中'
        t = setTimeout(() => {
          if (!root.isConnected) return
          el.dataset.st = 'ok'; err.hidden = true; ok.hidden = false; ok.classList.remove('in'); void ok.offsetWidth; ok.classList.add('in'); again.hidden = false
        }, 1300)
      })
      again.addEventListener('click', () => { clearTimeout(t); el.dataset.st = 'err'; err.hidden = false; ok.hidden = true; again.hidden = true; btn.disabled = false; btn.querySelector('.lbl').textContent = '重试' })
    },
  })

  /* MP-STATE-004 */
  def({
    id: 'MP-STATE-004', name: '断网提示条', style: '自动恢复',
    fit: '网络断开、弱网；挂在顶栏下方不挡内容，点重试显示连接中，恢复后变绿并自动收起',
    avoid: '断网时弹全屏遮罩；提示条一直不消失，网络恢复了还留在页面上',
    kw: 'offline 断网 无网络 弱网 提示条 网络异常 重试 恢复 banner network',
    css: S('mpstate004', `&{width:340px;${CARD};overflow:hidden}
& .nv{height:48px;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:600;border-bottom:1px solid var(--line)}
& .bn{display:grid;grid-template-columns:minmax(0,1fr);grid-template-rows:1fr;transition:grid-template-rows .3s cubic-bezier(.2,0,0,1)}
& .bi{min-height:0;overflow:hidden}
& .nbar{display:flex;align-items:center;gap:8px;height:44px;padding:0 4px 0 16px;font-size:14px;transition:background .25s,color .25s}
&[data-st=off] .nbar{background:var(--warn-bg);color:var(--warn)}
&[data-st=try] .nbar{background:var(--pt);color:var(--p-text)}
&[data-st=ok] .nbar{background:var(--ok-bg);color:var(--ok)}
&[data-st=hide] .bn{grid-template-rows:0fr}
& .nbar .msg{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
& .nbar .i{width:18px;height:18px}
& .nbar .e1,& .nbar .e2,& .nbar .e3{display:none}
&[data-st=off] .nbar .e1{display:inline-flex}&[data-st=try] .nbar .e2{display:inline-block}&[data-st=ok] .nbar .e3{display:inline-flex}
& .nbar .spin{width:16px;height:16px;border-color:rgba(var(--p-rgb),.25);border-top-color:var(--p)}
& .nbar .ac{min-width:56px;height:44px;padding:0 12px;font-size:14px;font-weight:600;color:inherit}
&:not([data-st=off]) .nbar .ac{visibility:hidden}
& .pgc{padding:4px 16px 4px;transition:opacity .3s}
&[data-st=off] .pgc,&[data-st=try] .pgc{opacity:.5}
& .pr{display:flex;gap:12px;align-items:center;padding:10px 0;border-top:1px solid var(--line)}& .pr:first-child{border-top:0}
& .pr img{width:56px;height:56px;border-radius:12px;object-fit:cover;flex:none}
& .pr b{display:block;font-size:14px;font-weight:600;line-height:20px}& .pr span{display:block;font-size:12px;line-height:18px;color:var(--ink3)}
& .pr .price{margin-left:auto}& .pr .price b{display:inline;font-size:16px}
& .dm{display:flex;align-items:center;justify-content:space-between;height:52px;padding:0 8px 0 16px;border-top:1px solid var(--line);font-size:14px;color:var(--ink2)}
& .tgl{position:relative;width:60px;height:44px;display:flex;align-items:center;justify-content:center}
& .tgl i{position:relative;width:46px;height:28px;border-radius:16px;background:var(--n7);transition:background .2s}
& .tgl i::after{content:"";position:absolute;left:3px;top:3px;width:22px;height:22px;border-radius:50%;background:var(--card);box-shadow:0 1px 4px var(--sh25);transition:transform .2s cubic-bezier(.2,0,0,1)}
& .tgl.on i{background:var(--p)}& .tgl.on i::after{transform:translateX(18px)}
${ICO}${SPIN}`),
    html: () => `<div class="mpstate004" data-st="off"><div class="nv">首页</div><div class="bn"><div class="bi"><div class="nbar" role="status"><i class="i e1">${sv('mc_wifioff')}</i><i class="spin e2"></i><i class="i e3">${sv('check')}</i><span class="msg">网络不可用，请检查网络设置</span><button class="ac" type="button">重试</button></div></div></div><div class="pgc">${[0, 1, 2].map((i) => `<div class="pr"><img src="${P(i)}" alt=""><div><b>${PRODUCTS[i].n}</b><span>${PRODUCTS[i].d}</span></div><span class="price"><small>¥</small><b>${PRODUCTS[i].p}</b></span></div>`).join('')}</div><div class="dm"><span>模拟断网</span><button class="tgl on" type="button" role="switch" aria-checked="true" aria-label="模拟断网"><i></i></button></div></div>`,
    js: (root) => {
      const el = root.querySelector('.mpstate004'), msg = el.querySelector('.msg'), ac = el.querySelector('.ac'), tg = el.querySelector('.tgl'); let t1 = 0, t2 = 0
      const MSG = { off: '网络不可用，请检查网络设置', try: '正在重新连接…', ok: '网络已恢复' }
      const set = (s) => { el.dataset.st = s; if (MSG[s]) msg.textContent = MSG[s] }
      const recover = () => {
        clearTimeout(t1); clearTimeout(t2); set('try')
        t1 = setTimeout(() => { if (!root.isConnected) return; set('ok'); tg.classList.remove('on'); tg.setAttribute('aria-checked', 'false'); t2 = setTimeout(() => { if (root.isConnected) set('hide') }, 1600) }, 1300)
      }
      ac.addEventListener('click', recover)
      tg.addEventListener('click', () => {
        const on = tg.classList.toggle('on'); tg.setAttribute('aria-checked', on)
        if (on) { clearTimeout(t1); clearTimeout(t2); set('off') } else recover()
      })
    },
  })

  /* MP-STATE-005 */
  const RS_TABS = [['ok', '支付成功'], ['no', '支付失败'], ['wt', '审核中']]
  def({
    id: 'MP-STATE-005', name: '结果页', style: '成功失败',
    fit: '支付、提交、审核结束；大图标加结论加原因，只留一个主按钮；失败页提供重试与另一条出路',
    avoid: '失败只写“操作失败”不写原因；成功页放三个以上同等按钮；结果页没有后续出口',
    kw: 'result 结果页 支付成功 支付失败 审核中 提交成功 状态页 反馈 重新支付 订单完成',
    css: S('mpstate005', `&{width:340px;${CARD};padding:12px 12px 20px}
& .sg{display:flex;background:var(--soft);border-radius:12px;padding:2px}
& .sg button{flex:1;height:36px;border-radius:8px;font-size:14px;color:var(--ink2);transition:background .15s,color .15s}
& .sg button.on{background:var(--lift);color:var(--ink);font-weight:600;box-shadow:0 1px 4px var(--sh12)}
& .pn{display:flex;flex-direction:column;align-items:center;padding:28px 8px 0;text-align:center}
& .pn:not([hidden]){animation:@@in .3s cubic-bezier(.2,0,0,1)}
@keyframes @@in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
& .ic{position:relative;display:flex;width:72px;height:72px;border-radius:50%;align-items:center;justify-content:center;margin-bottom:16px}
& .ic::before{content:"";position:absolute;inset:-8px;border-radius:50%;background:currentColor;opacity:.08}
& .ic svg{display:block;width:34px;height:34px}
& .ic.ok{background:var(--ok-bg);color:var(--ok)}& .ic.no{background:var(--danger-bg);color:var(--danger)}& .ic.wt{background:var(--warn-bg);color:var(--warn)}
& .pn:not([hidden]) .ic{animation:@@pop .4s cubic-bezier(.2,0,0,1)}
@keyframes @@pop{0%{transform:scale(.6);opacity:0}70%{transform:scale(1.06)}100%{transform:scale(1);opacity:1}}
& .pn:not([hidden]) .ic.ok path{stroke-dasharray:30;stroke-dashoffset:30;animation:@@dr .45s .15s cubic-bezier(.2,0,0,1) forwards}
@keyframes @@dr{to{stroke-dashoffset:0}}
@media(prefers-reduced-motion:reduce){& .pn:not([hidden]) .ic,& .pn:not([hidden]) .ic.ok path{animation:none;stroke-dashoffset:0}}
& h4{margin:0;font-size:18px;line-height:26px;font-weight:600}
& .pn>p{margin:6px 0 0;max-width:260px;font-size:14px;line-height:22px;color:var(--ink2)}
& .why{margin-top:12px;width:100%;padding:10px 12px;border-radius:12px;background:var(--danger-bg);color:var(--danger);font-size:14px;line-height:22px;text-align:left}
& .why b{font-weight:600}
& .smy{width:100%;margin-top:16px;padding:4px 14px;border-radius:12px;background:var(--n3)}
& .smy div{display:flex;align-items:center;justify-content:space-between;min-height:40px;font-size:14px}
& .smy div+div{border-top:1px solid var(--line)}
& .smy span{color:var(--ink3)}& .smy b{font-weight:600;font-variant-numeric:tabular-nums}
& .smy .price{color:var(--price)}& .smy .price b{font-size:16px}
& .stp{display:flex;align-items:center;width:100%;margin-top:16px;padding:0 8px}
& .stp div{display:flex;flex-direction:column;align-items:center;gap:6px;flex:none;width:64px;font-size:12px;color:var(--ink3)}
& .stp div i{width:20px;height:20px;border-radius:50%;background:var(--n6);display:flex;align-items:center;justify-content:center;color:#fff}
& .stp div i svg{width:12px;height:12px}
& .stp .dn i{background:var(--ok-fill)}& .stp .dn{color:var(--ink2)}
& .stp .cur i{background:var(--warn-fill);animation:@@bl 1.6s ease-in-out infinite}& .stp .cur{color:var(--warn);font-weight:600}
@keyframes @@bl{0%,100%{opacity:1}50%{opacity:.45}}
@media(prefers-reduced-motion:reduce){& .stp .cur i{animation:none}}
& .stp hr{flex:1;height:2px;margin:0 0 24px;border:0;background:var(--n6)}& .stp hr.dn{background:var(--ok-fill)}
& .acts{display:flex;flex-direction:column;align-items:center;gap:2px;width:100%;margin-top:20px}
& .pb{display:inline-flex;align-items:center;justify-content:center;gap:8px;width:100%;height:44px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:16px;font-weight:600;box-shadow:0 5px 12px rgba(var(--p-rgb),.2);transition:transform .15s}
& .pb:active{transform:scale(.98)}& .pb:disabled{cursor:progress;transform:none}
& .pb .spin{border-color:rgba(255,255,255,.4);border-top-color:var(--card)}
& .ln2{min-width:44px;height:44px;padding:0 16px;font-size:14px;color:var(--ink2)}
${ICO}${SPIN}`),
    html: () => `<div class="mpstate005"><div class="sg" data-ix="tabs" data-g="rs">${RS_TABS.map(([k, n], i) => `<button type="button" data-t="${k}" class="${i ? '' : 'on'}">${n}</button>`).join('')}</div>
<div class="pn" data-p="ok" data-g="rs"><span class="ic ok">${sv('check')}</span><h4>支付成功</h4><p>订单已提交，预计明天 18:00 前送达</p><div class="smy"><div><span>订单编号</span><b>SO2611040128</b></div><div><span>支付方式</span><b>微信支付</b></div><div><span>实付金额</span><span class="price"><small>¥</small><b>489.00</b></span></div></div><div class="acts"><button class="pb" type="button" data-toast="进入订单详情">查看订单</button><button class="ln2" type="button" data-toast="返回首页">继续逛逛</button></div></div>
<div class="pn" data-p="no" data-g="rs" hidden><span class="ic no">${sv('close')}</span><h4>支付失败</h4><p>订单已为你保留 29 分钟，请尽快支付</p><div class="why"><b>失败原因：</b>银行卡余额不足</div><div class="acts"><button class="pb rp" type="button"><i class="spin" hidden></i><span class="lbl">重新支付</span></button><button class="ln2" type="button" data-toast="选择其他支付方式">更换支付方式</button></div></div>
<div class="pn" data-p="wt" data-g="rs" hidden><span class="ic wt">${sv('hourglass')}</span><h4>资料审核中</h4><p>预计 1 个工作日内完成，结果会通过服务通知提醒你</p><div class="stp"><div class="dn"><i>${sv('check')}</i>已提交</div><hr class="dn"><div class="cur"><i></i>审核中</div><hr><div><i></i>已通过</div></div><div class="acts"><button class="pb" type="button" data-toast="返回首页">返回首页</button></div></div></div>`,
    js: (root) => {
      const rp = root.querySelector('.rp'); let t = 0
      rp.addEventListener('click', () => {
        if (rp.disabled) return
        rp.disabled = true; rp.querySelector('.spin').hidden = false; rp.querySelector('.lbl').textContent = '支付中'
        t = setTimeout(() => {
          if (!root.isConnected) return
          rp.disabled = false; rp.querySelector('.spin').hidden = true; rp.querySelector('.lbl').textContent = '重新支付'
          root.querySelector('[data-t="ok"]').click()
        }, 1200)
      })
    },
  })

  /* MP-STATE-006 */
  const ENL = { bag: '新品', star: '热销', giftbox: '礼品', scooter: '极速达' }
  def({
    id: 'MP-STATE-006', name: '新手引导蒙层', style: '高亮目标',
    fit: '新功能上线、首次进入；一次只高亮一个目标，给步数与跳过，最后一步写“知道了”',
    avoid: '一次引导超过 4 步；每次打开都弹（只在首次出现）；遮罩上的文字小于 14px',
    kw: 'coach guide onboarding 新手引导 蒙层 高亮 聚光灯 步骤 跳过 下一步',
    css: S('mpstate006', `&{width:340px;display:flex;flex-direction:column;align-items:center}
& .frm{position:relative;width:340px;height:480px;${CARD};overflow:hidden}
& .pgx{display:flex;flex-direction:column;height:100%}
& .top{flex:none;height:44px;display:flex;align-items:center;padding:0 16px;font-size:16px;font-weight:600}
& .sch{flex:none;display:flex;align-items:center;gap:8px;height:44px;margin:0 12px;padding:0 14px;border-radius:22px;background:var(--soft);color:var(--ink3);font-size:14px}
& .sch .i{width:18px;height:18px}
& .ban{flex:none;display:flex;align-items:center;justify-content:space-between;height:76px;margin:12px 12px 0;padding:0 16px;border-radius:16px;background:linear-gradient(135deg,var(--ga),var(--gb));color:#fff}
& .ban h5{margin:0;font-size:18px;line-height:26px;font-weight:600}& .ban p{margin:0;font-size:12px;opacity:.92}
& .ban .ico{width:56px;height:56px;object-fit:contain}& .ban .ico-line{width:44px;height:44px;stroke:var(--card)}
& .ent{flex:none;display:grid;grid-template-columns:repeat(4,1fr);margin:12px 12px 0;padding:12px 0 8px;border-radius:16px}
& .ent div{display:flex;flex-direction:column;align-items:center;gap:6px;font-size:12px;color:var(--ink2)}
& .rec{flex:1;min-height:0;padding:8px 12px 0;overflow:hidden}
& .rec h5{margin:0 0 6px;font-size:14px;line-height:20px;font-weight:600}
& .rec .pl{display:flex;gap:10px;align-items:center;padding:8px 0}
& .rec .pl img{width:56px;height:56px;border-radius:12px;object-fit:cover}
& .rec .pl b{display:block;font-size:14px;line-height:20px;font-weight:600}& .rec .pl span{font-size:12px;color:var(--ink3)}
& .tbr{flex:none;display:flex;height:56px;border-top:1px solid var(--line);padding:0 8px}
& .tbr div{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:12px;color:var(--ink3)}
& .tbr div.on{color:var(--p-fg);font-weight:600}
& .tbr .i{width:22px;height:22px}
& .cm{position:absolute;inset:0;z-index:5}
& .spot{position:absolute;left:0;top:0;width:0;height:0;box-shadow:0 0 0 2px rgba(255,255,255,.9),0 0 0 9999px rgba(31,35,41,.66);transition:left .28s cubic-bezier(.2,0,0,1),top .28s cubic-bezier(.2,0,0,1),width .28s cubic-bezier(.2,0,0,1),height .28s cubic-bezier(.2,0,0,1),border-radius .28s}
& .tip{position:absolute;width:260px;padding:14px 16px 6px;border-radius:16px;background:var(--card2);box-shadow:0 12px 30px rgba(31,35,41,.3)}
& .tip .ar{position:absolute;top:-6px;width:12px;height:12px;background:var(--card2);transform:rotate(45deg);border-radius:2px}
& .tip.up .ar{top:auto;bottom:-6px}
& .tip h5{margin:0;font-size:16px;line-height:24px;font-weight:600}
& .tip p{margin:4px 0 0;font-size:14px;line-height:22px;color:var(--ink2)}
& .tip .ft{display:flex;align-items:center;gap:4px;margin-top:6px}
& .tip .dots{display:flex;gap:6px;flex:1}
& .tip .dots i{width:6px;height:6px;border-radius:3px;background:var(--n7);transition:width .25s cubic-bezier(.2,0,0,1),background .25s}
& .tip .dots i.on{width:16px;background:var(--p)}
& .tip .skip{min-width:44px;height:44px;padding:0 8px;font-size:14px;color:var(--ink3)}
& .tip .nx{min-width:88px;height:44px;padding:0 18px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:14px;font-weight:600}
& .again{margin-top:6px;display:inline-flex;align-items:center;gap:6px;height:44px;padding:0 16px;font-size:12px;color:var(--ink3)}
& .again .i{width:14px;height:14px}
${ICO}`),
    html: () => `<div class="mpstate006"><div class="frm"><div class="pgx"><div class="top">示例商城</div><div class="sch" data-g="1" data-t="先搜一搜" data-d="想买什么直接搜，支持商品名、品牌和品类。" data-r="22">${I('search')}搜索商品、品牌、品类</div><div class="ban"><div><h5>新人专享</h5><p>首单立减 ¥20</p></div>${IC('coupon')}</div><div class="ent" data-g="2" data-t="常用入口" data-d="新品、热销、礼品和极速达都在这里，点一下直达。" data-r="16">${['bag', 'star', 'giftbox', 'scooter'].map((n) => `<div><span class="tile tile-sq">${IC(n)}</span><span>${ENL[n]}</span></div>`).join('')}</div><div class="rec"><h5>为你推荐</h5>${[3, 6].map((i) => `<div class="pl"><img src="${P(i)}" alt=""><div><b>${PRODUCTS[i].n}</b><span>${PRODUCTS[i].d}</span></div></div>`).join('')}</div><div class="tbr"><div class="on">${I('home')}首页</div><div>${I('grid')}分类</div><div>${I('cart')}购物车</div><div data-g="3" data-t="订单与权益" data-d="订单、优惠券和会员权益都在“我的”里。" data-r="12">${I('user')}我的</div></div></div><div class="cm"><i class="spot"></i><div class="tip" role="dialog" aria-label="新手引导"><i class="ar"></i><h5></h5><p></p><div class="ft"><span class="dots"></span><button class="skip" type="button">跳过</button><button class="nx" type="button">下一步</button></div></div></div></div><button class="again" type="button">${I('refresh')}重新查看引导</button></div>`,
    js: (root) => {
      const frm = root.querySelector('.frm'), cm = frm.querySelector('.cm'), spot = cm.querySelector('.spot'), tip = cm.querySelector('.tip'), again = root.querySelector('.again')
      const tg = [...frm.querySelectorAll('[data-g]')].sort((a, b) => a.dataset.g - b.dataset.g)
      let i = 0
      const place = () => {
        const t = tg[i], f = frm.getBoundingClientRect(), r = t.getBoundingClientRect(), pad = 6
        const x = r.left - f.left - pad, y = r.top - f.top - pad, w = r.width + pad * 2, h = r.height + pad * 2
        Object.assign(spot.style, { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', borderRadius: (+t.dataset.r + pad) + 'px' })
        tip.querySelector('h5').textContent = t.dataset.t + '（' + (i + 1) + '/' + tg.length + '）'; tip.querySelector('p').textContent = t.dataset.d
        tip.querySelector('.dots').innerHTML = tg.map((_, k) => '<i' + (k === i ? ' class="on"' : '') + '></i>').join('')
        tip.querySelector('.nx').textContent = i === tg.length - 1 ? '知道了' : '下一步'
        const tw = tip.offsetWidth, th = tip.offsetHeight, below = y + h + 14 + th <= f.height - 8
        const left = Math.max(12, Math.min(f.width - tw - 12, x + w / 2 - tw / 2))
        tip.style.left = left + 'px'; tip.style.top = (below ? y + h + 14 : y - th - 14) + 'px'; tip.classList.toggle('up', !below)
        tip.querySelector('.ar').style.left = Math.max(16, Math.min(tw - 28, x + w / 2 - left - 6)) + 'px'
      }
      const open = () => { i = 0; cm.hidden = false; spot.style.transition = 'none'; place(); requestAnimationFrame(() => requestAnimationFrame(() => { spot.style.transition = '' })) }
      tip.querySelector('.nx').addEventListener('click', () => { if (i >= tg.length - 1) { cm.hidden = true; return } i++; place() })
      tip.querySelector('.skip').addEventListener('click', () => { cm.hidden = true })
      again.addEventListener('click', open)
      open()
    },
  })

  /* ================= PRC 价格与标签（007 起）================= */
  guide('mp', 'PRC', [
    ['普通商品、会员价、秒杀价', '价格样式集', '价格是页面里最该被看见的数字，货币符号和小数缩小一档；会员金价与秒杀价别同屏'],
    ['划线价 + 会员价 + 优惠券叠加', '会员价与到手价', '大字只放到手价，明细收进折叠；开关实时重算，营销信息不超过三层'],
    ['同一商品规格不同价', '价格区间与规格', '没选规格显示区间，选了变成单价；售罄规格划线禁用；按钮随之从“请选择”变可点'],
    ['高客单价商品想降低一次付清压力', '分期价选择', '每期金额放大、手续费写清楚；免息和含费分开标注，总计始终可见'],
    ['商品图角落', '角标与丝带', '最多一个，别把图遮住'],
    ['满减、包邮、新人、状态提示', '优惠标签组', '虚线像“券”，用户天然理解是优惠；标签样式集用于状态提示，一张卡不超过三个'],
    ['限时活动', '倒计时样式', '数字等宽避免跳动；超过 24 小时改写“剩 2 天”'],
  ])

  /* MP-PRC-007 */
  def({
    id: 'MP-PRC-007', name: '会员价与到手价', style: '开关联动',
    fit: '商品详情、确认订单；划线价、会员价、优惠券叠加，大字只放到手价，明细可折叠，开关实时重算',
    avoid: '营销信息超过三层；把每一项优惠都用大字强调，反而看不清最终价',
    kw: 'price 会员价 到手价 划线价 优惠券 叠加 明细 折扣 已省 价格组合',
    css: S('mpprc007', `&{width:340px;${CARD};padding:16px}
& .top{display:flex;align-items:center;gap:12px}
& .top img{width:56px;height:56px;border-radius:12px;object-fit:cover;flex:none}
& .top b{display:block;font-size:14px;line-height:20px;font-weight:600}& .top span{font-size:12px;line-height:18px;color:var(--ink3)}
& .pc{margin-top:14px;padding:14px;border-radius:16px;background:linear-gradient(135deg,var(--pt),var(--card) 90%);box-shadow:inset 0 0 0 1px var(--pm)}
& .main{display:flex;align-items:baseline;gap:8px}
& .lb{font-size:12px;color:var(--ink2)}
& .amt{display:inline-flex;align-items:baseline;color:var(--price);font-variant-numeric:tabular-nums}
& .amt small{font-size:16px;font-weight:600;margin-right:2px}
& .amt b{font-size:32px;line-height:1;font-weight:700}
& .amt b.pop{animation:@@pop .3s cubic-bezier(.2,0,0,1)}
@keyframes @@pop{0%{transform:scale(1)}40%{transform:scale(1.08)}100%{transform:scale(1)}}
& .strike{margin-left:0}
& .tags{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-top:10px}
& .tags .tg{height:20px;border-radius:4px}
& .tg.gold{background:var(--warn-bg);color:var(--gold-ink2)}
& .tg.cp{background:var(--pt);color:var(--p-text);box-shadow:inset 0 0 0 1px var(--p);border-radius:4px;font-weight:400}
& .tags .sv{margin-left:auto;font-size:12px;font-weight:600;color:var(--ok)}
& .op{display:flex;align-items:center;justify-content:space-between;min-height:56px;border-bottom:1px solid var(--line)}
& .pc+.op{margin-top:8px}
& .op b{display:block;font-size:14px;line-height:20px;font-weight:600}& .op span{font-size:12px;line-height:18px;color:var(--ink3)}
& .tgl{position:relative;flex:none;width:60px;height:44px;display:flex;align-items:center;justify-content:flex-end}
& .tgl i{position:relative;width:46px;height:28px;border-radius:16px;background:var(--n7);transition:background .2s}
& .tgl i::after{content:"";position:absolute;left:3px;top:3px;width:22px;height:22px;border-radius:50%;background:var(--card);box-shadow:0 1px 4px var(--sh25);transition:transform .2s cubic-bezier(.2,0,0,1)}
& .tgl.on i{background:var(--p)}& .tgl.on i::after{transform:translateX(18px)}
& .dt [data-h]{display:flex;align-items:center;justify-content:space-between;width:100%;height:44px;font-size:14px;color:var(--ink2)}
& .dt [data-h] .i{width:16px;height:16px;transition:transform .25s cubic-bezier(.2,0,0,1)}
& .dt .ix-ai.open [data-h] .i{transform:rotate(180deg)}
& .rows{padding:0 0 2px}
& .rows div{display:flex;align-items:center;justify-content:space-between;min-height:30px;font-size:14px;color:var(--ink2);font-variant-numeric:tabular-nums}
& .rows div em{color:var(--ink)}& .rows .cut em{color:var(--ok)}
& .rows .tot{margin-top:4px;padding-top:8px;border-top:1px dashed var(--n7);color:var(--ink);font-weight:600}
& .rows .tot em{color:var(--price);font-size:16px}
${ICO}`),
    html: () => `<div class="mpprc007"><div class="top"><img src="${P(0)}" alt=""><div><b>无线降噪耳机</b><span>石墨灰 · 主动降噪</span></div></div><div class="pc"><div class="main"><span class="lb">到手价</span><span class="amt"><small>¥</small><b data-t>489</b></span><span class="strike">¥799</span></div><div class="tags"><span class="tg gold" data-g="m">会员价 -¥60</span><span class="tg cp" data-g="c">券 -¥50</span><span class="sv">已省 ¥<span data-s>310</span></span></div></div><div class="op"><div><b>会员价</b><span>金卡会员再减 ¥60</span></div><button class="tgl on" type="button" role="switch" aria-checked="true" data-k="m" aria-label="使用会员价"><i></i></button></div><div class="op"><div><b>优惠券</b><span>满 500 减 50</span></div><button class="tgl on" type="button" role="switch" aria-checked="true" data-k="c" aria-label="使用优惠券"><i></i></button></div><div class="dt" data-ix="acc"><div class="ix-ai open"><button type="button" data-h>价格明细${I('down')}</button><div class="ix-ab"><div><div class="rows"><div>商品价<em>¥799.00</em></div><div class="cut">活动立减<em>-¥200.00</em></div><div class="cut" data-g="m">会员价<em>-¥60.00</em></div><div class="cut" data-g="c">优惠券<em>-¥50.00</em></div><div class="tot">到手价<em>¥<span data-t2>489.00</span></em></div></div></div></div></div></div></div>`,
    js: (root) => {
      const el = root.querySelector('.mpprc007'), st = { m: true, c: true }
      const paint = () => {
        const sub = 799 - 200 - (st.m ? 60 : 0), total = sub - (st.c ? 50 : 0)
        const b = el.querySelector('[data-t]'); b.textContent = total; b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop')
        el.querySelector('[data-t2]').textContent = total.toFixed(2); el.querySelector('[data-s]').textContent = 799 - total
        el.querySelectorAll('[data-g]').forEach((n) => { n.hidden = !st[n.dataset.g] })
      }
      el.querySelectorAll('.tgl').forEach((t) => t.addEventListener('click', () => { const k = t.dataset.k; st[k] = !st[k]; t.classList.toggle('on', st[k]); t.setAttribute('aria-checked', st[k]); paint() }))
    },
  })

  /* MP-PRC-008 */
  const SPEC = [['350ml 经典款', 59, 128], ['500ml 加大款', 79, 12], ['双杯礼盒', 109, 36], ['三件套装', 129, 0]]
  def({
    id: 'MP-PRC-008', name: '价格区间与规格', style: '选规格变价',
    fit: '同一商品多规格不同价；没选规格显示区间，选了变单价，售罄规格禁用，按钮随之变可点',
    avoid: '区间跨度大到失去参考意义（超过 3 倍时改按规格分开卖）；售罄规格不置灰',
    kw: 'price range 价格区间 规格 sku 起 单价 库存 售罄 选规格',
    css: S('mpprc008', `&{width:340px;${CARD};padding:16px}
& .hd{display:flex;gap:12px;align-items:flex-end}
& .hd img{width:72px;height:72px;border-radius:12px;object-fit:cover;flex:none;background:var(--ph)}
& .amt{display:inline-flex;align-items:baseline;color:var(--price);font-variant-numeric:tabular-nums;flex-wrap:wrap}
& .amt small{font-size:16px;font-weight:600;margin-right:2px}
& .amt b{font-size:28px;line-height:1.1;font-weight:700}
& .amt .to{display:inline-flex;align-items:baseline;margin-left:6px}
& .amt .to::before{content:"–";margin-right:6px;font-size:22px;color:var(--ink3)}
& .amt.one .to{display:none}
& .amt b.pop{animation:@@pop .3s cubic-bezier(.2,0,0,1)}
@keyframes @@pop{0%{transform:scale(1)}40%{transform:scale(1.08)}100%{transform:scale(1)}}
& .sub{display:block;margin-top:4px;font-size:12px;line-height:18px;color:var(--ink3)}
& h6{margin:16px 0 10px;font-size:14px;line-height:20px;font-weight:600}
& .chs{display:flex;flex-wrap:wrap;gap:10px}
& .sp{display:flex;flex-direction:column;align-items:flex-start;gap:2px;min-width:140px;padding:8px 14px;border-radius:12px;background:var(--n3);box-shadow:inset 0 0 0 1.5px transparent;font-size:14px;color:var(--ink);text-align:left;transition:background .15s,box-shadow .15s}
& .sp small{font-size:12px;color:var(--ink3)}
& .sp.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p);color:var(--p-text);font-weight:600}
& .sp.on small{color:var(--p-text);font-weight:400}
& .sp:disabled{color:color-mix(in srgb,var(--ink6) 42%,var(--ink5));cursor:not-allowed}& .sp:disabled span{text-decoration:line-through}
& .buy{display:flex;align-items:center;justify-content:center;width:100%;height:44px;margin-top:18px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:16px;font-weight:600;box-shadow:0 5px 12px rgba(var(--p-rgb),.2);transition:transform .15s}
& .buy:active{transform:scale(.98)}
& .buy:disabled{background:var(--n6);color:var(--ink4);box-shadow:none;cursor:not-allowed;transform:none}
${ICO}`),
    html: () => `<div class="mpprc008"><div class="hd"><img src="${P(6)}" alt=""><div><span class="amt"><small>¥</small><b data-a>59</b><span class="to"><small>¥</small><b data-b>109</b></span></span><span class="sub" data-sub>共 4 种规格，请选择规格</span></div></div><h6>规格</h6><div class="chs">${SPEC.map(([n, p, k]) => `<button class="sp" type="button" data-p="${p}" data-n="${n}" data-k="${k}"${k ? '' : ' disabled'}><span>${n}</span><small>${k ? '¥' + p : '已售罄'}</small></button>`).join('')}</div><button class="buy" type="button" disabled>请选择规格</button></div>`,
    js: (root) => {
      const el = root.querySelector('.mpprc008'), chips = [...el.querySelectorAll('.sp:not(:disabled)')], amt = el.querySelector('.amt'), a = el.querySelector('[data-a]'), sub = el.querySelector('[data-sub]'), buy = el.querySelector('.buy')
      const lo = Math.min(...chips.map((c) => +c.dataset.p)), hi = Math.max(...chips.map((c) => +c.dataset.p)); let cur = null
      const paint = () => {
        chips.forEach((c) => { c.classList.toggle('on', c === cur); c.setAttribute('aria-pressed', c === cur) })
        a.classList.remove('pop'); void a.offsetWidth; a.classList.add('pop')
        if (cur) {
          a.textContent = cur.dataset.p; amt.classList.add('one')
          sub.textContent = '已选：' + cur.dataset.n + (+cur.dataset.k <= 20 ? ' · 仅剩 ' + cur.dataset.k + ' 件' : ' · 库存充足')
          buy.disabled = false; buy.textContent = '加入购物车 · ¥' + cur.dataset.p
        } else {
          a.textContent = lo; el.querySelector('[data-b]').textContent = hi; amt.classList.remove('one')
          sub.textContent = '共 4 种规格，请选择规格'; buy.disabled = true; buy.textContent = '请选择规格'
        }
      }
      chips.forEach((c) => c.addEventListener('click', () => { cur = cur === c ? null : c; paint() }))
      buy.addEventListener('click', () => { if (!buy.disabled) IX.toast(root, '已加入购物车') })
    },
  })

  /* MP-PRC-009 */
  const fm = (n) => n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  const TOTAL = 3999
  const TERMS = [[1, 0, '一次付清', ''], [3, 0, '免息', 'free'], [6, 0.0045, '含手续费', 'fee'], [12, 0.005, '含手续费', 'fee']].map(([n, r, tx, kind]) => { const fee = Math.round(TOTAL * r * n * 100) / 100, all = TOTAL + fee; return { n, r, tx, kind, fee, all, per: Math.round(all / n * 100) / 100 } })
  def({
    id: 'MP-PRC-009', name: '分期价选择', style: '逐期试算',
    fit: '高客单价商品（建议 ¥1,000 以上）；每期金额放大、手续费写清楚，免息与含费分开标注，总计始终可见',
    avoid: '只放“每期低至 ¥x”的诱导文案；把手续费藏在小字里；同屏出现多种分期方案',
    kw: 'installment 分期 分期价 每期 手续费 免息 花呗 信用卡 高客单价 试算',
    css: S('mpprc009', `&{width:340px;${CARD};padding:16px}
& .top{display:flex;align-items:center;gap:12px}
& .top img{width:56px;height:56px;border-radius:12px;object-fit:cover;flex:none}
& .top b{display:block;font-size:14px;line-height:20px;font-weight:600}
& .top .price{margin-top:4px;display:block}& .top .price b{display:inline;font-size:22px;line-height:1;font-weight:700}
& h6{margin:16px 0 10px;font-size:14px;line-height:20px;font-weight:600}
& .terms{display:grid;grid-template-columns:1fr 1fr;gap:10px}
& .tm{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:4px;min-height:68px;padding:10px 12px;border-radius:12px;background:var(--n3);box-shadow:inset 0 0 0 1.5px transparent;text-align:left;transition:background .15s,box-shadow .15s}
& .tm .ln{display:flex;align-items:baseline;gap:4px;font-variant-numeric:tabular-nums}
& .tm .ln b{font-size:16px;line-height:22px;font-weight:600}& .tm .ln small{font-size:12px;color:var(--ink2)}
& .tm .nt{display:inline-flex;align-items:center;height:20px;padding:0 6px;border-radius:4px;font-size:12px;background:var(--n4);color:var(--ink2)}
& .tm .nt.free{background:var(--ok-bg);color:var(--ok);font-weight:600}
& .tm.on{background:var(--pt);box-shadow:inset 0 0 0 1.5px var(--p)}
& .tm.on .ln b{color:var(--p-text)}
& .tm .ck{position:absolute;right:8px;top:8px;display:none;width:18px;height:18px;border-radius:50%;background:var(--p);color:#fff;align-items:center;justify-content:center}
& .tm.on .ck{display:flex}& .tm .ck svg{width:12px;height:12px;stroke-width:3}
& .smy{margin-top:14px;padding:4px 14px;border-radius:12px;background:var(--n3)}
& .smy div{display:flex;align-items:center;justify-content:space-between;min-height:36px;font-size:14px;color:var(--ink2);font-variant-numeric:tabular-nums}
& .smy div+div{border-top:1px solid var(--line)}
& .smy em{color:var(--ink);font-weight:600}
& .smy .all{color:var(--ink);font-weight:600}& .smy .all em{color:var(--price);font-size:16px}
& .go{display:flex;align-items:center;justify-content:center;width:100%;height:44px;margin-top:16px;border-radius:22px;background:linear-gradient(180deg,var(--ga),var(--gb));color:#fff;font-size:16px;font-weight:600;box-shadow:0 5px 12px rgba(var(--p-rgb),.2);transition:transform .15s}
& .go:active{transform:scale(.98)}
${ICO}`),
    html: () => `<div class="mpprc009"><div class="top"><img src="${P(4)}" alt=""><div><b>机械腕表 · 钢壳皮带</b><span class="price"><small>¥</small><b>${TOTAL.toLocaleString('en-US')}</b></span></div></div><h6>选择分期</h6><div class="terms">${TERMS.map((t, i) => `<button class="tm${i === 2 ? ' on' : ''}" type="button" data-n="${t.n}" data-per="${fm(t.per)}" data-fee="${fm(t.fee)}" data-all="${fm(t.all)}" data-r="${(t.r * 100).toFixed(2)}"><span class="ln">${t.n === 1 ? '<b>¥' + TOTAL.toLocaleString('en-US') + '</b>' : '<b>¥' + fm(t.per) + '</b><small>× ' + t.n + ' 期</small>'}</span><span class="nt ${t.kind}">${t.tx}</span><i class="ck">${sv('check')}</i></button>`).join('')}</div><div class="smy"><div>每期应还<em data-v-per></em></div><div>分期手续费<em data-v-fee></em></div><div class="all">应付总额<em data-v-all></em></div></div><button class="go" type="button" data-toast="已选择分期方案">确认分期</button></div>`,
    js: (root) => {
      const el = root.querySelector('.mpprc009'), tms = [...el.querySelectorAll('.tm')]
      const paint = (b) => {
        tms.forEach((t) => { t.classList.toggle('on', t === b); t.setAttribute('aria-pressed', t === b) })
        const one = b.dataset.n === '1'
        el.querySelector('[data-v-per]').textContent = '¥' + b.dataset.per + (one ? '' : ' × ' + b.dataset.n + ' 期')
        el.querySelector('[data-v-fee]').textContent = +b.dataset.fee ? '¥' + b.dataset.fee + '（每期 ' + b.dataset.r + '%）' : '¥0.00（免息）'
        el.querySelector('[data-v-all]').textContent = '¥' + b.dataset.all
      }
      tms.forEach((t) => t.addEventListener('click', () => paint(t)))
      paint(el.querySelector('.tm.on'))
    },
  })

})()
