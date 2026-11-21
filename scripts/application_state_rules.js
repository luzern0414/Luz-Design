/* Evaluate in the browser after each application state has settled. Returns serializable findings. */
() => {
  const issues = [], seen = new Set(), styles = new Map(), pixels = new Map();
  const root = document.documentElement;
  const view = {w:root.clientWidth, h:window.innerHeight};
  const icon = '.icon,.ic,.el-icon,.van-icon,.iconfont,.fa,.fas,.far,.mdi,.icon-button,.icon-only,[data-icon],[data-ic],[class*="material-icons"],[class*="material-symbols"]';
  const avatar = '.avatar,.el-avatar,.van-image--round[data-avatar],.msg__avatar,[data-avatar],[class*="user-avatar"],[class*="profile-avatar"]';
  const surface = 'html,body,main,[role=main],[role=banner],[role=navigation],#app,#root,#__next,.app-shell,.page-shell,[data-ui-surface]';
  const control = 'form,input:not([type=hidden]),textarea,select,[contenteditable=true],[role=spinbutton],[role=textbox]';
  const styleOf = el => {if (!styles.has(el)) styles.set(el,getComputedStyle(el)); return styles.get(el)};
  const tag = el => el.id ? '#'+el.id : el.localName+(el.classList.length?'.'+el.classList[0]:'');
  function add(rule, el, detail, suffix='') {
    const element=tag(el)+suffix, key=rule+'|'+element+'|'+detail;
    if(!seen.has(key)){seen.add(key);issues.push({rule,element,detail})}
  }
  const cv=document.createElement('canvas');cv.width=cv.height=1;
  const ctx=cv.getContext('2d',{willReadFrequently:true});
  function rgba(color) {
    if(!pixels.has(color)){
      if(!color || !CSS.supports('color',color))return [0,0,0,0];
      ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);
      pixels.set(color,Array.from(ctx.getImageData(0,0,1,1).data));
    }
    return pixels.get(color);
  }
  function green([r,g,b,a]){
    const difference=Math.max(r,g,b)-Math.min(r,g,b);
    if(!a||difference<3)return false;
    const hue=g>=b&&g>=r ? 120+60*(b-r)/difference : b>=r&&b>=g ? 240+60*(r-g)/difference : 60*(g-b)/difference;
    return hue>=65&&hue<=185;
  }
  const white = c => {const [r,g,b,a]=rgba(c);return !a||(r===255&&g===255&&b===255)};
  const tokens = /\b(?:rgba?|hsla?|oklch|oklab|lch|lab|color|hwb)\([^()]+\)|#[a-f\d]{3,8}\b/gi;
  function colorCheck(property,value,el,suffix) {
    if(!value||value==='none')return;
    const colors=CSS.supports('color',value)?[value]:value.match(tokens)||[];
    for(const c of colors)if(green(rgba(c)))add('green-interface-color',el,property+' '+c,suffix);
  }
  const all=[root,...root.querySelectorAll('*')];
  function shown(el) {
    if(el.closest('script,style,template,defs,symbol,clipPath,mask,.sr-only,.visually-hidden'))return false;
    const r=el.getBoundingClientRect();
    return (r.width>0||r.height>0||el===root||el===document.body)&&el.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});
  }
  function glyph(el){
    const walk=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
    for(let n=walk.nextNode();n;n=walk.nextNode())if(n.textContent.trim()&&!n.parentElement.closest('title,desc,.sr-only,.visually-hidden')&&shown(n.parentElement))return n.textContent.trim();
    for(const p of ['::before','::after']){
      const s=getComputedStyle(el,p);
      if(s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0'&&/^["'].+["']$/.test(s.content))return s.content.slice(1,-1);
    }
    return '';
  }
  function raster(el){
    const image=document.createElement('canvas');image.width=image.height=40;
    const c=image.getContext('2d',{willReadFrequently:true});
    try{const filters=[];for(let n=el;n;n=n.parentElement){const filter=styleOf(n).filter;if(filter!=='none')filters.push(filter)}if(filters.length)c.filter=filters.join(' ');c.drawImage(el,0,0,40,40);return c.getImageData(0,0,40,40).data}catch{return null}
  }
  const isAnchoredList = el => {
    if(!el.matches('[role=listbox], [role=menu], .el-select__popper,.van-dropdown-item__content') && !el.querySelector('[role=listbox]'))return false;
    if(el.querySelector('form,textarea,[contenteditable=true],input:not([type=search]):not([role=combobox])'))return false;
    const list=el.id?el:el.querySelector('[role=listbox][id]'),r=el.getBoundingClientRect();
    const anchors=[...document.querySelectorAll('[aria-expanded=true],[role=combobox],select')].filter(shown);
    return anchors.some(a=>{
      const b=a.getBoundingClientRect(),controls=a.getAttribute('aria-controls');
      if(controls&&list?.id&&!controls.split(/\s+/).includes(list.id))return false;
      return b.right>=r.left-4&&b.left<=r.right+4&&Math.min(Math.abs(r.top-b.bottom),Math.abs(b.top-r.bottom))<=24;
    });
  };
  const paintRoot = (el,r,s) => {
    if(el.matches(surface))return true;
    if(el.matches('header,footer,nav,aside')&&!el.closest('article,.card,[data-card],main > section,dialog,[role=dialog]'))return true;
    return r.left<=1&&r.top<=1&&r.right>=view.w-1&&r.bottom>=view.h-1&&!['img','video','canvas','svg'].includes(el.localName);
  };
  for(const el of all){
    if(!shown(el))continue;
    const s=styleOf(el), r=el.getBoundingClientRect(), visibleText=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
    const graphic=el.matches(avatar)||el.matches(icon)||el.matches('img')&&(el.closest(avatar+','+icon)||el.matches('[data-ic],.nav-icon,.action-icon')||el.closest('button,nav,[role=tab]')&&!el.matches('[data-product-image]')&&!el.closest('picture,figure')&&r.width<=64&&r.height<=64);
    if(el.matches(avatar)){
      const img=el.matches('img')?el:el.querySelector('img');
      const picture=img&&img.complete&&img.naturalWidth>0;
      const svg=(el.matches('svg')?el:el.querySelector('svg'));
      const vector=svg?.querySelector('path,use,circle,ellipse,line,polygon,polyline,rect');
      const label=glyph(el);
      if(label||!picture&&!vector&&!s.maskImage.includes('url('))add('graphical-avatar-required',el,label||'头像缺少已加载的图形');
      if(picture){
        const src=(img.currentSrc||img.src).split('?')[0];
        const photo=/(?:portrait|headshot|photograph|头像照片|人物照片|[/-]photo[-./])/.test(src+' '+img.alt);
        const data=raster(img), palette=new Set();let opaque=0;
        if(data)for(let i=0;i<data.length;i+=4){if(data[i+3]>245){opaque++;palette.add(((data[i]>>4)<<8)|((data[i+1]>>4)<<4)|(data[i+2]>>4))}}
        if(photo||data&&opaque>1530&&palette.size>200)add('graphical-avatar-required',el,'头像图像呈现照片特征');
      }
    }
    if(el.matches(icon+',button,[role=button]')){
      const value=glyph(el);
      if(value&&((el.matches(icon)&&!el.matches('button,[role=button],a'))||/^[\p{S}\p{P}\p{Co}\u200d\ufe0f\u20e3]+$/u.test(value)))add('text-icon',el,value);
    }
    const positioned=['fixed','absolute'].includes(s.position);
    const edge=r.left<=3||r.right>=view.w-3||r.bottom>=view.h-3;
    const panel=/(?:^|[-_\s])(drawer|sheet|modal|popup|overlay|offcanvas|off-canvas|slideout|sidepanel)(?:$|[-_\s])/i.test(typeof el.className==='string'?el.className:'');
    const modal=el.matches('dialog,[role=dialog],[role=alertdialog],[aria-modal=true],:popover-open');
    const floating=positioned&&(Number(s.zIndex)>0||s.position==='fixed')&&!el.matches(surface)&&((edge&&(r.width>view.w*.38&&r.height>view.h*.32||r.height>view.h*.65))||el.querySelector(control));
    if(modal||panel&&positioned||floating){
      const navLandmark=el.matches('nav,header,footer,[role=navigation],[role=tablist],.van-tabbar,.bottom-tabs,.mobile-tabs')||el.matches('aside')&&!!el.querySelector('nav,[role=navigation]');
      const linked=el.id&&[...document.querySelectorAll('[aria-controls][aria-expanded=true]')].some(a=>!el.contains(a)&&a.getAttribute('aria-controls').split(/\s+/).includes(el.id));
      const scrim=[...document.querySelectorAll('[class*="backdrop"],[class*="scrim"],[class*="overlay-mask"],[data-backdrop]')].some(a=>a!==el&&shown(a)&&['fixed','absolute'].includes(styleOf(a).position));
      const permanentNav=navLandmark&&!modal&&!panel&&!el.querySelector('form,textarea')&&!(r.height>view.h*.5&&(linked||scrim));
      const center=Math.abs(r.left+r.width/2-view.w/2)<=Math.max(24,view.w*.08)&&Math.abs(r.top+r.height/2-view.h/2)<=Math.max(24,view.h*.12);
      const warning=(el.matches('[role=alertdialog]')||!!el.querySelector('[role=alertdialog]'))&&center&&!el.querySelector(control);
      const tip=el.matches('[role=tooltip],[role=status],[role=alert]')&&!el.querySelector(control+',button,a');
      const backdropOnly=!modal&&!el.querySelector(control+',button,a,[role=dialog],[role=alertdialog]')&&!el.textContent.trim();
      const fullRoute=!panel&&!modal&&r.width>=view.w-2&&r.height>=view.h-2&&el.matches('main,[role=main],[data-form-page]')&&s.backgroundColor==='rgb(255, 255, 255)';
      if(!permanentNav&&!warning&&!tip&&!backdropOnly&&!fullRoute&&!isAnchoredList(el))add('business-or-edge-overlay',el,'浮层承载业务或从页面边缘覆盖内容');
    }
    for(const pseudo of ['', '::before','::after']){
      const st=pseudo?getComputedStyle(el,pseudo):s;
      if(pseudo&&(['none','normal'].includes(st.content)||st.display==='none'||st.visibility==='hidden'||st.opacity==='0'))continue;
      const topSurface=pseudo ? (paintRoot(el,r,s)&&parseFloat(st.width)>=r.width*.96&&parseFloat(st.height)>=r.height*.94||parseFloat(st.width)>=view.w-2&&parseFloat(st.height)>=view.h-2) : paintRoot(el,r,s);
      if(topSurface&&(!white(st.backgroundColor)||st.backgroundImage!=='none'))add('nonwhite-background',el,st.backgroundColor+' '+st.backgroundImage,pseudo);
      if(!topSurface&&st.backgroundImage.includes('url(')&&!el.matches(avatar+','+icon+',img,figure,[role=img]')&&!el.closest('figure,picture')&&!/photo|image|media|artwork/i.test(String(el.className)))add('component-background-image',el,'核对组件的图像用途',pseudo);
      colorCheck('background-color',st.backgroundColor,el,pseudo);
      if(st.backgroundImage.includes('gradient'))colorCheck('gradient',st.backgroundImage.replace(/url\([^)]*\)/g,''),el,pseudo);
      colorCheck('box-shadow',st.boxShadow,el,pseudo);
      if(visibleText||pseudo&&st.content.length>2||el.matches('input,select,textarea'))colorCheck('color',st.color,el,pseudo);
      if(st.outlineStyle!=='none'&&parseFloat(st.outlineWidth)>0)colorCheck('outline',st.outlineColor,el,pseudo);
      for(const side of ['Top','Right','Bottom','Left'])if(st['border'+side+'Style']!=='none'&&parseFloat(st['border'+side+'Width'])>0)colorCheck('border',st['border'+side+'Color'],el,pseudo);
      if(!pseudo&&el.matches('svg path,svg circle,svg ellipse,svg line,svg rect,svg polygon,svg polyline,svg text,svg use')){
        if(el.localName!=='line'&&st.fill!=='none'&&Number(st.fillOpacity)>0)colorCheck('fill',st.fill,el,'');
        if(st.stroke!=='none'&&Number(st.strokeOpacity)>0)colorCheck('stroke',st.stroke,el,'');
        for(const paint of [st.fill,st.stroke]){const id=paint?.match(/url\(["']?[^#)]*#([^)'"]+)/)?.[1];
          if(id)for(const stop of document.getElementById(id)?.querySelectorAll('stop')||[])colorCheck('SVG gradient',styleOf(stop).stopColor,el,'');}
      }
      if(!pseudo&&el.matches('input[type=checkbox],input[type=radio],progress'))colorCheck('accent',st.accentColor,el,'');
    }
    if(el.matches('canvas')||el.matches('img')&&graphic){
      const data=raster(el);if(data){let count=0;for(let i=0;i<data.length;i+=4)if(data[i+3]>20&&green(data.subarray(i,i+4)))count++;
      if(count>=5)add('green-interface-color',el,el.localName+' 图形含绿色像素')}
    }
  }
  if(!matchMedia('(forced-colors: active)').matches&&[root,document.body].every(el=>!rgba(styleOf(el).backgroundColor)[3])){
    const probe=document.createElement('span');probe.style.cssText='display:none;color:Canvas!important';root.append(probe);
    const color=getComputedStyle(probe).color;probe.remove();if(!white(color))add('nonwhite-background',root,color);
  }
  return issues;
}

