(root) => {
  const visible = el => {
    const s=getComputedStyle(el),r=el.getBoundingClientRect();
    return r.width>1&&r.height>1&&s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0'&&!el.closest('.sr-only,[hidden],[inert],[aria-hidden="true"]');
  };
  const all=selector=>Array.from(root.querySelectorAll(selector)).filter(visible);
  const violations=[];
  const suggestions=[];
  const text=all('*').flatMap(el=>Array.from(el.childNodes).filter(n=>n.nodeType===3&&n.textContent.trim()).map(n=>n.textContent.trim())).join('\n');
  const placeholders=all('input,textarea').map(el=>el.getAttribute('placeholder')||'').join('\n');
  const content=text+'\n'+placeholders;
  if(/[A-Za-z]/.test(content))suggestions.push({rule:'visible-english',matches:content.match(/[A-Za-z]+/g)});
  if(/今天|本地演示|演示数据|仅供参考|下一步建议/.test(content))suggestions.push({rule:'forbidden-copy'});
  const datePattern=/(?:19|20)\d{2}[年./-]\d{1,2}|\d{1,2}月\d{1,2}日|周[一二三四五六日天]/;
  const approvedPeriods=new Set();
  for(const el of all('[data-business-period][data-week]')){
    if(el.closest('[data-form-page]'))violations.push({rule:'period-in-entry-form'});
    const match=/^(\d{4})-(\d{2})$/.exec(el.dataset.week||'');
    if(!match){violations.push({rule:'invalid-business-period'});continue}
    const jan4=new Date(Date.UTC(+match[1],0,4)),start=new Date(jan4);start.setUTCDate(4-((jan4.getUTCDay()+6)%7)+(+match[2]-1)*7);
    const end=new Date(start);end.setUTCDate(start.getUTCDate()+6);
    const expected=(start.getUTCMonth()+1)+'月'+start.getUTCDate()+'日至'+(end.getUTCMonth()+1)+'月'+end.getUTCDate()+'日';
    if(!el.innerText.includes(expected)){violations.push({rule:'period-label-mismatch',week:el.dataset.week,expected});continue}
    approvedPeriods.add(el);
  }
  const validDate=value=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return false;const [y,m,d]=value.split('-').map(Number);return new Date(Date.UTC(y,m-1,d)).toISOString().slice(0,10)===value};
  const approvedDates=all('[data-business-date]').filter(el=>{
    const value=el.dataset.businessDate;
    if(!validDate(value)){if(value)violations.push({rule:'invalid-business-date',value});return false}
    const supported=el.closest('[data-form-page]')||el.matches('time[datetime],.history-top [data-business-date]');
    if(!supported)violations.push({rule:'unrelated-business-date'});
    return !!supported;
  });
  for(const el of all('*').filter(el=>!el.children.length&&datePattern.test(el.innerText||''))){
    if(![...approvedPeriods,...approvedDates].some(parent=>parent===el||parent.contains(el)))suggestions.push({rule:'visible-unrelated-date',text:el.innerText.slice(0,80)});
  }
  const headings=all('h1,h2,h3,[role=heading],.task-title span').map(el=>{
    const s=getComputedStyle(el),r=el.getBoundingClientRect(),name=el.innerText;
    if(/[\p{P}\p{S}]/u.test(name))suggestions.push({rule:'title-punctuation',name});
    if(r.height>+(s.lineHeight.replace('px',''))*1.2)suggestions.push({rule:'multiline-title',name});
    return {text:name,height:r.height,lineHeight:s.lineHeight,fontSize:s.fontSize,whiteSpace:s.whiteSpace};
  });
  const overlays=all('dialog,[aria-modal=true],[role=dialog],[role=alertdialog],.van-popup,.el-popper').filter(el=>!el.matches('.luz-tooltip[role=tooltip]'));
  for(const el of overlays){
    const r=el.getBoundingClientRect();
    const warning=el.getAttribute('role')==='alertdialog'&&!el.querySelector('input,textarea,select,form,[contenteditable=true],[role=spinbutton]');
    const centered=Math.abs(r.left+r.width/2-root.clientWidth/2)<=Math.max(24,root.clientWidth*.08)&&Math.abs(r.top+r.height/2-root.clientHeight/2)<=Math.max(24,root.clientHeight*.15);
    const options=el.getAttribute('role')==='listbox'&&!el.querySelector('form,textarea,button');
    if(!(warning&&centered)&&!options)violations.push({rule:'business-or-edge-overlay',role:el.getAttribute('role')});
  }
  if(all('[title]').length)violations.push({rule:'native-title-tooltip'});
  const hints=all('.luz-tooltip');
  if(hints.some(el=>el.querySelector('a,button,input,textarea,select,[tabindex]')))violations.push({rule:'interactive-tooltip'});
  const surface=root.dataset.uiSurface||'web';
  const minimum=surface==='app'||(surface==='app-web'&&root.clientWidth<=760)?10:12;
  const textNodes=all('*').filter(el=>Array.from(el.childNodes).some(n=>n.nodeType===3&&n.textContent.trim())||el.matches('input,textarea'));
  const typography=textNodes.map(el=>({text:(el.innerText||el.value||el.placeholder||'').slice(0,40),size:+getComputedStyle(el).fontSize.replace('px',''),family:getComputedStyle(el).fontFamily}));
  const tooSmall=typography.filter(t=>t.size<minimum);
  if(tooSmall.length)suggestions.push({rule:'font-below-surface-minimum',minimum,items:tooSmall});
  const families=[...new Set(typography.map(t=>t.family))];
  if(families.length>1)suggestions.push({rule:'multiple-font-families',families});
  if(all('.avatar,[data-avatar]').some(el=>!el.querySelector('img')&&el.tagName!=='IMG'))suggestions.push({rule:'text-avatar'});
  const iconGroups='.heading-with-icon,.rail__item,.main-nav button,.tabbar__item,.van-tabbar-item,.entry,.categories button,.business-entries button';
  const icons=all(iconGroups).map(el=>{
    const icon=el.querySelector('img');
    const label=el.querySelector('.van-tabbar-item__text')||el.querySelector('span');
    if(!icon||!label||!visible(label))return null;
    const imageBox=icon.getBoundingClientRect(),labelBox=label.getBoundingClientRect();
    const fontSize=parseFloat(getComputedStyle(label).fontSize);
    const nav=el.closest('.main-nav');
    const inline=el.matches('.heading-with-icon,.rail__item')||(nav&&getComputedStyle(nav).position!=='fixed');
    const layout=inline?'inline':'stacked';
    const iconSize=Math.max(imageBox.width,imageBox.height);
    const matches=inline
      ? imageBox.right<=labelBox.left+2&&Math.abs(imageBox.height-Math.min(fontSize,24))<=1
      : imageBox.bottom<=labelBox.top+2&&imageBox.height>fontSize;
    if(!matches)suggestions.push({rule:'icon-label-layout',text:label.innerText,layout});
    if(iconSize>24.5&&!el.closest('[data-preserve-icons],.business-entries'))suggestions.push({rule:'icon-visual-size',text:label.innerText,size:iconSize,referenceLimit:24});
    return {text:label.innerText,layout,iconHeight:imageBox.height,fontSize,iconBottom:imageBox.bottom,labelTop:labelBox.top};
  }).filter(Boolean);
  const images=all('img').map(el=>({path:el.getAttribute('src'),loaded:el.complete&&el.naturalWidth>0,width:el.naturalWidth}));
  if(images.some(i=>!i.loaded))violations.push({rule:'broken-image'});
  const top=root.querySelector('[data-top-row]');
  const topBox=top?.getBoundingClientRect();
  const topControls=top?Array.from(top.querySelectorAll('input,button,h1,h2,[data-header-content]')).filter(visible):[];
  const intervals=topControls.map(el=>el.getBoundingClientRect()).map(r=>({left:r.left,right:r.right})).sort((a,b)=>a.left-b.left);
  let occupied=0,cursor=topBox?.left||0,largestGap=0;
  for(const r of intervals){largestGap=Math.max(largestGap,r.left-cursor);occupied+=Math.max(0,r.right-Math.max(cursor,r.left));cursor=Math.max(cursor,r.right)}
  if(topBox)largestGap=Math.max(largestGap,topBox.right-cursor);
  const topRow=top?{width:topBox.width,height:topBox.height,icons:Array.from(top.querySelectorAll('img')).filter(visible).length,controls:topControls.length,occupiedRatio:occupied/topBox.width,largestGapRatio:largestGap/topBox.width}:null;
  if(topRow&&topRow.height>64&&topRow.controls===0)suggestions.push({rule:'empty-top-row'});
  const headerReview=topRow&&topRow.occupiedRatio<.45&&topRow.largestGapRatio>.4?['顶部控件集中在局部，需要人工检查空白']:[];
  const topCaptions=topControls.filter(el=>el.matches('button.icon-button,button.icon-action')&&el.innerText.trim());
  if(topCaptions.length)suggestions.push({rule:'top-icon-caption',text:topCaptions.map(e=>e.innerText)});
  const actionGroups=all('[data-action-group]').map(el=>{const buttons=Array.from(el.querySelectorAll('button')).filter(visible);const rects=buttons.map(b=>b.getBoundingClientRect());const sameRow=rects.length<2||rects.every(r=>Math.abs(r.top-rects[0].top)<3);if(!sameRow)suggestions.push({rule:'separated-action-group'});return {labels:buttons.map(b=>b.getAttribute('aria-label')||b.innerText),sameRow,gaps:rects.slice(1).map((r,i)=>r.left-rects[i].right)}});
  const textButtons=all('button.el-button,button.van-button').filter(el=>el.innerText.trim()&&!el.querySelector('img')).map(el=>({text:el.innerText,width:el.getBoundingClientRect().width}));
  const favicon=root.querySelector('link[rel=icon]')?.getAttribute('href');
  if(!favicon)suggestions.push({rule:'missing-favicon'});
  if(root.scrollWidth>root.clientWidth+1)violations.push({rule:'page-overflow'});
  const navigationNames=new Set(all('nav[aria-label="主导航"] button,[role=tablist][aria-label="主导航"] [role=tab]').map(el=>el.innerText.trim()));
  for(const top of all('[data-page-top]')){
    for(const heading of top.querySelectorAll('h1'))if(navigationNames.has(heading.innerText.trim()))suggestions.push({rule:'duplicated-navigation-heading',text:heading.innerText});
    const style=getComputedStyle(top);
    if(parseFloat(style.borderRadius)>0&&(parseFloat(style.borderWidth)>0||style.boxShadow!=='none'))suggestions.push({rule:'card-wrapped-overview'});
  }
  for(const heading of all('[data-module-heading]')){
    for(let ancestor=heading.parentElement;ancestor&&ancestor!==root&&!ancestor.matches('body');ancestor=ancestor.parentElement){
      const style=getComputedStyle(ancestor),background=style.backgroundColor;
      const filled=background!=='transparent'&&!/rgba\([^)]*,\s*0\)/.test(background);
      const rounded=parseFloat(style.borderRadius)>=4;
      const surface=filled||parseFloat(style.borderWidth)>0||style.boxShadow!=='none';
      if(ancestor.matches('[data-ui-card]')||(rounded&&surface)){
        suggestions.push({rule:'module-heading-inside-card',text:heading.innerText,ancestor:ancestor.tagName.toLowerCase()+'.'+String(ancestor.className).trim().replace(/\s+/g,'.')});break;
      }
    }
    for(const button of heading.querySelectorAll('button'))if(/^(新建|新增|添加|补充)/.test(button.getAttribute('aria-label')||'')&&button.innerText.trim())suggestions.push({rule:'create-action-visible-text'});
  }
  for(const button of all('button[aria-label]')){
    if(/^(新建|新增|添加|补充)/.test(button.getAttribute('aria-label'))&&!button.closest('[data-module-heading],[data-form-page]'))suggestions.push({rule:'create-action-outside-heading',name:button.getAttribute('aria-label')});
  }
  for(const row of all('[data-filter-row],.demo-collections,.line-switch,.project-range,.filter-row,.task-filters')){
    const controls=[...row.querySelectorAll('button,select,.el-radio-button')].filter(visible),rects=controls.map(el=>el.getBoundingClientRect());
    if(rects.length>1&&rects.some(r=>Math.abs((r.top+r.bottom)/2-(rects[0].top+rects[0].bottom)/2)>Math.max(8,rects[0].height/2)))suggestions.push({rule:'multiline-filters'});
  }
  for(const field of all('textarea,input:not([type=hidden]):not([type=radio]):not([type=checkbox])')){
    const label=(field.getAttribute('aria-label')||'')+' '+(field.placeholder||'');
    if(field.type==='range')violations.push({rule:'horizontal-number-input'});
    if(!/搜索/.test(label)&&!field.closest('[data-form-page],[data-inline-field]'))violations.push({rule:'input-outside-explicit-edit',name:label});
  }
  for(const bar of all('.van-tabbar,.bottom-tabs,.mobile-tabs,nav[aria-label="主导航"]')){
    const r=bar.getBoundingClientRect(),style=getComputedStyle(bar);
    if(bar.matches('nav')&&(style.position!=='fixed'||style.bottom==='auto'))continue;
    if(Math.abs(r.left)>1||Math.abs(r.right-root.clientWidth)>1||Math.abs(r.bottom-root.clientHeight)>1)suggestions.push({rule:'bottom-navigation-edge-gap',rect:{left:r.left,right:r.right,bottom:r.bottom}});
    if(style.backgroundColor==='transparent'||/rgba\([^)]*,\s*0\)/.test(style.backgroundColor))suggestions.push({rule:'transparent-bottom-navigation'});
  }
  const actionResults=[];
  for(const trigger of all('[aria-expanded=true][aria-controls]')){
    const target=root.querySelector('#'+CSS.escape(trigger.getAttribute('aria-controls')));if(!target||!visible(target))continue;
    const item=trigger.closest('[data-ui-object],article,.task'),r=target.getBoundingClientRect();
    if(item&&!item.contains(target)&&item.nextElementSibling!==target)violations.push({rule:'detached-expansion-result'});
    actionResults.push({name:trigger.getAttribute('aria-label')||trigger.innerText,resultTop:r.top,resultVisible:r.top<root.clientHeight&&r.bottom>0});
  }
  return {schema:'luz-ui-browser-scan/4',surface,typography:{minimum,families,sizes:[...new Set(typography.map(t=>t.size))],tooSmall},viewport:{width:root.clientWidth,height:root.clientHeight,scrollWidth:root.scrollWidth},visibleText:content,headings,icons,images,topRow,headerReview,actionGroups,actionResults,textButtons,favicon,background:getComputedStyle(root.querySelector('body')).backgroundColor,overlays:overlays.length,violations,suggestions,limits:['Static attributes do not prove click outcomes or role permissions','First middle last and long-list transitions require observed evidence','Period labels are checked here; current-period bounds require runtime and server tests']};
}
