/* 六种页面布局的 React 写法：同一套类名与令牌（ui.css），组件只负责把区域放对位置。
   用法：import './ui.css'; <HeroLayout hero={…} aside={[…]} below={[…]} />。这份代码是参照写法，随 ui.css 的类名保持一致，本仓库没有运行 React 的环境，未在其中执行过。 */
import { useEffect, useRef, useState } from 'react';

/** 1 主次布局：hero 一个主角（占 8 列、跨两行），aside 放右侧小块，below 放下方小块 */
export function HeroLayout({ hero, aside = [], below = [] }) {
  return (
    <section className="l-hero">
      <article className="card hero">{hero}</article>
      {aside.map((n, i) => <article key={i} className="card card--tight aside">{n}</article>)}
      {below.map((n, i) => <article key={i} className="card card--tight below">{n}</article>)}
    </section>
  );
}

/** 2 横带分层：bands 是 [{ title, content, kind }]，第一条放概览数字（stats），第二条趋势，第三条明细 */
export function BandsLayout({ bands }) {
  return (
    <div className="l-bands">
      {bands.map((b, i) => (
        <section key={i} className="band" aria-label={b.title}>
          {b.kind === 'stats' ? <div className="band-stats">{b.content}</div> : (<><div className="band-title"><h2>{b.title}</h2>{b.actions}</div>{b.content}</>)}
        </section>
      ))}
    </div>
  );
}

/** 3 主区加右侧窄栏：rail 用 position: sticky 固定，容器宽 860 以下落到主区下方 */
export function RailLayout({ main, rail }) {
  return (
    <div className="l-rail">
      <div className="main">{main}</div>
      <aside className="rail" aria-label="提醒与动态">{rail}</aside>
    </div>
  );
}

/** 4 全幅画布加浮动面板：floats 是 [{ at: 'tl' | 'tr' | 'bl' | 'br' | 'bottom', node }] */
export function CanvasLayout({ canvas, floats = [] }) {
  return (
    <section className="l-canvas">
      <div className="canvas">{canvas}</div>
      {floats.map((f, i) => <div key={i} className={`float ${f.at}`}>{f.node}</div>)}
    </section>
  );
}

/** 5 看板分列：columns 是 [{ id, title, cards: [{ id, node }] }]；拖动落下时调用 onMove(cardId, fromId, toId)；每张卡另有“移到…”按钮 */
export function KanbanLayout({ columns, onMove }) {
  const [drag, setDrag] = useState(null), [over, setOver] = useState(null);
  return (
    <div className="l-kanban">
      {columns.map((c) => (
        <section key={c.id} className={`kcol${over === c.id ? ' drop' : ''}`} aria-label={c.title}
          onDragOver={(e) => { e.preventDefault(); setOver(c.id); }} onDragLeave={() => setOver(null)}
          onDrop={(e) => { e.preventDefault(); setOver(null); if (drag && drag.from !== c.id) onMove(drag.id, drag.from, c.id); setDrag(null); }}>
          <div className="kcol-head"><strong>{c.title}</strong><span className="count">{c.cards.length}</span></div>
          <div className="stack">
            {c.cards.map((cd) => (
              <article key={cd.id} className={`kcard${drag && drag.id === cd.id ? ' dragging' : ''}`} draggable tabIndex={0}
                onDragStart={() => setDrag({ id: cd.id, from: c.id })} onDragEnd={() => { setDrag(null); setOver(null); }}>
                {cd.node}
                <select className="select" aria-label="移到其他列" value="" onChange={(e) => e.target.value && onMove(cd.id, c.id, e.target.value)}>
                  <option value="">移到…</option>
                  {columns.filter((x) => x.id !== c.id).map((x) => <option key={x.id} value={x.id}>{x.title}</option>)}
                </select>
              </article>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

/** 6 时间轴泳道：lanes 是 [{ id, label, events: [{ id, from, to, title, kind }] }]，from 与 to 用小时数（10.5 即 10:30）；now 画现在的竖线 */
export function LanesLayout({ from, to, now, lanes, onEvent }) {
  const slots = to - from, ref = useRef(null), [x, setX] = useState(null);
  const fmt = (t) => `${String(Math.floor(t)).padStart(2, '0')}:${t % 1 ? '30' : '00'}`;
  useEffect(() => { const el = ref.current; if (!el || now == null) return; const t = el.querySelector('.ticks').getBoundingClientRect(), r = el.getBoundingClientRect(); setX(t.left - r.left + el.scrollLeft + ((now - from) / slots) * t.width); }, [now, from, slots]);
  return (
    <div className="l-lanes" ref={ref} style={{ '--slots': slots }}>
      <div className="lanes-ruler"><div className="corner" /><div className="ticks">{Array.from({ length: slots }, (_, i) => <span key={i}>{fmt(from + i)}</span>)}</div></div>
      {lanes.map((ln) => {
        const evs = [...ln.events].sort((a, b) => a.from - b.from), rows = [];
        evs.forEach((e) => { let r = rows.findIndex((end) => end <= e.from); if (r < 0) { r = rows.length; rows.push(0); } rows[r] = e.to; e.row = r + 1; e.conflict = evs.some((o) => o !== e && o.from < e.to && o.to > e.from); });
        return [
          <div key={ln.id + 'l'} className="lane-label"><strong>{ln.label}</strong></div>,
          <div key={ln.id + 't'} className="lane-track">
            {evs.map((e) => <div key={e.id} className={`lane-event${e.conflict ? ' conflict' : e.kind === 'warn' ? ' warn' : ''}`} style={{ '--from': e.from - from + 1, '--to': e.to - from + 1, '--row': e.row }} role="button" tabIndex={0} onClick={() => onEvent?.(e, ln)}>{e.title}</div>)}
          </div>,
        ];
      })}
      {x != null && <div className="lanes-now" data-label={`现在 ${fmt(now)}`} style={{ left: x }} aria-hidden="true" />}
    </div>
  );
}
