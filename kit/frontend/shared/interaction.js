/* Element Plus supplies tooltip, input and button behavior; this module composes
   them into anchored hints and explicit, local edits. No remote save is implied. */
(function () {
  const {h,cloneVNode,ref,computed,nextTick,onMounted,onBeforeUnmount,watch}=Vue;
  let serial=0;
  const drafts=new Map(),fieldCommits=new Map(),pageStack=[];
  let pendingHistoryBack=0;
  const historyWaiters=[];
  window.addEventListener('popstate',()=>{if(pendingHistoryBack>0){pendingHistoryBack--;nextTick(()=>{if(!pendingHistoryBack)historyWaiters.splice(0).forEach(open=>open())})}});
  let navigationTrigger=null;
  // Capture the origin before Vue removes a v-if list and the browser loses focus.
  document.addEventListener('click',event=>{
    const target=event.target.closest?.('[data-ui-open],button,a[href],[role="button"]');
    if(target)navigationTrigger={time:Date.now(),scroll:window.scrollY,focus:target,key:target.closest('[data-ui-open]')?.getAttribute('data-ui-open'),label:target.getAttribute('aria-label')};
  },true);
  // Commit pending wheel inertia before the form's business submit handler runs.
  function flushFields(root){for(const [element,commit] of fieldCommits)if(root.contains(element))commit()}
  const Section={props:['heading','bodyClass'],setup(){return {headingId:'section-'+(++serial)}},template:`<section class="ui-section" :aria-labelledby="headingId"><div class="ui-section-heading" data-module-heading><h2 :id="headingId">{{heading}}</h2><slot name="actions"></slot></div><div :class="['ui-section-body',bodyClass]" data-ui-card><slot></slot></div></section>`};
  const FormPage={props:{heading:String,detail:Boolean},emits:['close'],setup(props,{emit}){
    const page=ref(null),id='form-'+(++serial),trigger=document.activeElement;
    const previous=navigationTrigger&&Date.now()-navigationTrigger.time<1000?navigationTrigger:{scroll:window.scrollY,focus:trigger,key:trigger?.closest('[data-ui-open]')?.getAttribute('data-ui-open'),label:trigger?.getAttribute('aria-label')};navigationTrigger=null;let popped=false,alive=true,registered=false;
    const pop=()=>{const target=pageStack.indexOf(history.state?.luzForm),own=pageStack.indexOf(id);if(own<0||own<=target)return;popped=true;emit('close')};
    onMounted(()=>{const open=()=>{if(!alive)return;registered=true;pageStack.push(id);history.pushState({...history.state,luzForm:id},'',location.pathname+location.search+'#'+id);window.addEventListener('popstate',pop)};if(pendingHistoryBack)historyWaiters.push(open);else open();window.scrollTo(0,0);nextTick(()=>page.value?.querySelector('h1')?.focus({preventScroll:true}))});
    onBeforeUnmount(()=>{alive=false;window.removeEventListener('popstate',pop);const own=pageStack.indexOf(id);if(own>=0)pageStack.splice(own,1);if(registered&&!popped&&history.state?.luzForm===id){pendingHistoryBack++;history.back()}nextTick(()=>{
      let attempts=0;
      const visible=e=>e?.isConnected&&e.tagName!=='BODY'&&e.getClientRects().length;
      const restore=()=>{
        const restored=visible(previous.focus)?previous.focus:previous.key?Array.from(document.querySelectorAll('[data-ui-open="'+CSS.escape(previous.key)+'"]')).find(visible):previous.label?Array.from(document.querySelectorAll('button[aria-label]')).find(e=>e.getAttribute('aria-label')===previous.label&&visible(e)):null;
        window.scrollTo(0,previous.scroll);
        if(restored)restored.focus({preventScroll:true});else if(++attempts<8)requestAnimationFrame(restore);
      };
      // Data tables may render their rows after the parent's next Vue tick.
      requestAnimationFrame(restore);
    })});
    return {page,flushFields,close:()=>emit('close')};
  },template:`<section ref="page" class="ui-form-page" :data-form-page="detail?undefined:''" :data-detail-page="detail?'':undefined" @submit.capture="flushFields($event.target)"><header class="form-page-heading page-hero" data-page-top><ui-action icon="back" label="返回上一页" @click="close"></ui-action><h1 tabindex="-1">{{heading}}</h1></header><div class="form-page-body"><slot></slot></div></section>`};
  const WheelField={props:{modelValue:[String,Number],label:String,numeric:Boolean,precision:{type:Number,default:0},options:Array},emits:['update:modelValue'],setup(props,{emit}){
    const root=ref(null),picker=ref(null),editing=ref(false),input=ref(null),draft=ref(props.modelValue),custom=ref([]),selected=computed(()=>[props.modelValue??'']);
    const choices=computed(()=>{
      if(!props.numeric)return [...new Set([...(props.options||[]),...custom.value,props.modelValue].filter(v=>v!==undefined&&v!==null&&v!==''))].map(v=>({text:String(v),value:v}));
      const step=props.precision?100:1,values=Array.from({length:101},(_,i)=>i*step);
      return [...(props.modelValue==null?[{text:'未填写',value:''}]:[]),...[...new Set([...values,...custom.value,props.modelValue].filter(v=>typeof v==='number'&&v>=0))].sort((a,b)=>a-b).map(v=>({text:String(v),value:v}))];
    });
    function change(values){if(!editing.value&&values[0]!==undefined)emit('update:modelValue',values[0])}
    function begin(){draft.value=props.modelValue;editing.value=true;nextTick(()=>input.value?.focus())}
    function finish(){if(!editing.value)return;const v=props.numeric?draft.value:String(draft.value||'').trim();if(v!==null&&v!==undefined&&v!=='')custom.value=[...custom.value,v];emit('update:modelValue',v);editing.value=false}
    function flush(){if(editing.value){input.value?.blur?.();finish()}else{picker.value?.confirm();const option=picker.value?.getSelectedOptions()?.[0];if(option)change([option.value])}}
    onMounted(()=>{fieldCommits.set(root.value,flush);nextTick(()=>root.value?.querySelectorAll('.van-picker [tabindex]').forEach(el=>el.setAttribute('tabindex','-1')))});onBeforeUnmount(()=>fieldCommits.delete(root.value));
    function activate(option,event){if(option.value===props.modelValue){event.stopPropagation();begin()}}
    function step(direction){if(editing.value)return;const i=choices.value.findIndex(o=>o.value===props.modelValue),next=choices.value[Math.max(0,Math.min(choices.value.length-1,i+direction))];if(next)emit('update:modelValue',next.value)}
    function key(event){if(event.isComposing)return;if(['ArrowUp','ArrowDown'].includes(event.key)){event.preventDefault();step(event.key==='ArrowUp'?1:-1)}else if(event.key==='Home'&&props.numeric){event.preventDefault();emit('update:modelValue',0)}else if(event.key==='Enter'){event.preventDefault();begin()}}
    let lastWheel=0;
    function wheel(event){if(editing.value)return;event.preventDefault();if(Date.now()-lastWheel>80){step(event.deltaY>0?1:-1);lastWheel=Date.now()}}
    return {root,picker,editing,input,draft,selected,choices,change,begin,finish,activate,key,wheel};
  },template:`<div ref="root" class="ui-wheel-field" :data-wheel-field="label" @wheel="wheel"><div v-show="!editing" tabindex="0" role="spinbutton" :aria-label="label" :aria-valuenow="numeric?modelValue:choices.findIndex(o=>o.value===modelValue)" :aria-valuemin="0" :aria-valuemax="numeric?undefined:choices.length-1" :aria-valuetext="String(modelValue??'未填写')" @keydown="key"><div aria-hidden="true"><van-picker ref="picker" :columns="choices" :model-value="selected" @update:model-value="change" :show-toolbar="false" :visible-option-num="3" :option-height="34" :swipe-duration="200"><template #option="option"><span :class="['wheel-option',{'wheel-chosen':option.value===modelValue}]" @click="activate(option,$event)">{{option.text}}</span></template></van-picker></div></div><div v-if="editing" class="wheel-manual"><el-input-number v-if="numeric" ref="input" v-model="draft" :precision="precision" :min="0" :controls="false" :aria-label="label" @blur="finish" @keydown.enter.prevent="finish"></el-input-number><el-input v-else ref="input" v-model="draft" :aria-label="label" maxlength="12" @blur="finish" @keydown.enter.prevent="finish"></el-input></div><ui-action v-if="!editing" class="wheel-edit" icon="edit" :label="'输入'+label" @click="begin"></ui-action></div>`};
  const DateField={props:{modelValue:String,label:{type:String,default:'记录日期'},max:String,initial:String},emits:['update:modelValue'],setup(props,{emit}){
    const root=ref(null),picker=ref(null),input=ref(null),opened=ref(false),manual=ref(false),draft=ref(''),id='date-'+(++serial);
    const parse=value=>{const [y,m,d]=String(value).split('-').map(Number);return new Date(y,m-1,d)};
    const minDate=new Date(1900,0,1),maxDate=computed(()=>parse(props.max||'2099-12-31'));
    const selected=computed(()=>String(props.modelValue||props.initial||props.max).split('-'));
    const display=computed(()=>{if(!props.modelValue)return '选择日期';const [y,m,d]=props.modelValue.split('-').map(Number);return y+'年'+m+'月'+d+'日'});
    const formatter=(type,option)=>({...option,text:Number(option.value)+({year:'年',month:'月',day:'日'}[type])});
    function change(values){if(values?.length===3)emit('update:modelValue',values.join('-'))}
    function begin(){opened.value=false;draft.value=props.modelValue||'';manual.value=true;nextTick(()=>input.value?.focus())}
    function finish(){if(!manual.value)return;emit('update:modelValue',draft.value||'');manual.value=false}
    function flush(){if(manual.value)finish();else if(opened.value){picker.value?.confirm();change(picker.value?.getSelectedDate())}}
    onMounted(()=>fieldCommits.set(root.value,flush));onBeforeUnmount(()=>fieldCommits.delete(root.value));
    return {root,picker,input,opened,manual,draft,id,minDate,maxDate,selected,display,formatter,change,begin,finish};
  },template:`<div ref="root" class="ui-date-field" :data-business-date="modelValue"><label :for="id">{{label}}</label><div class="date-input-row"><el-input v-if="manual" ref="input" :id="id" v-model="draft" type="date" data-business-date :max="max" :aria-label="label" @blur="finish" @keydown.enter.prevent="finish"></el-input><button v-else :id="id" type="button" class="date-selection" :aria-label="'选择'+label" :aria-expanded="opened" :aria-controls="id+'-picker'" @click="opened=!opened">{{display}}</button><ui-action v-if="!manual" icon="edit" :label="'输入'+label" @click="begin"></ui-action></div><div v-if="opened" :id="id+'-picker'" class="date-inline-picker" :aria-label="label+'选择'"><van-date-picker data-business-date ref="picker" :model-value="selected" @update:model-value="change" :min-date="minDate" :max-date="maxDate" :formatter="formatter" :show-toolbar="false" :visible-option-num="3" :option-height="36" :swipe-duration="200"></van-date-picker></div></div>`};
  const Hint={
    props:{content:String,disabled:Boolean},
    setup(props,{slots}) {
      const open=ref(false);let hovered=false,focused=false,dismissed=false,closing;
      const enter=()=>{clearTimeout(closing);hovered=true;if(!dismissed&&!props.disabled)open.value=true};
      const scheduleClose=()=>{clearTimeout(closing);closing=setTimeout(()=>{if(!hovered&&!focused){open.value=false;dismissed=false}},120)};
      const leave=()=>{hovered=false;scheduleClose()};
      const focus=()=>{focused=true;if(!dismissed&&!props.disabled)open.value=true};
      const blur=()=>{focused=false;scheduleClose()};
      const dismiss=e=>{if(e.key==='Escape'&&open.value){dismissed=true;open.value=false}};
      watch(()=>props.disabled,v=>{if(v)open.value=false});
      onMounted(()=>document.addEventListener('keydown',dismiss));
      onBeforeUnmount(()=>{document.removeEventListener('keydown',dismiss);clearTimeout(closing)});
      return ()=>h(ElementPlus.ElTooltip,{
        visible:open.value,disabled:props.disabled,
        trigger:'hover',triggerKeys:[],effect:'light',placement:'bottom',
        showAfter:0,hideAfter:0,autoClose:0,enterable:true,persistent:false,
        popperClass:'luz-tooltip',offset:8,
      },{default:()=>slots.default?.().map(v=>cloneVNode(v,{onMouseenter:enter,onMouseleave:leave,onFocusin:focus,onFocusout:blur})),
          content:()=>h('span',{class:'hint-content',onMouseenter:enter,onMouseleave:leave},props.content)});
    },
  };
  const actionText=(icon,label)=>{
    if(icon==='action-add')return label.startsWith('生成')?'生成':'新建';
    if(icon==='action-close')return label.startsWith('撤销')?'撤销':'取消';
    if(icon==='action-check')return label==='结束录音'?'结束':label.startsWith('保存')?'保存':'完成';
    if(icon==='action-restore')return '恢复';
    if(icon==='archive')return '归档';
    return '';
  };
  const Action={
    inheritAttrs:false,props:{label:String,icon:String,iconOnly:Boolean},
    setup(props,{attrs}) {
      return ()=>{
        const text=props.iconOnly?'':actionText(props.icon,props.label);
        const button=()=>h(ElementPlus.ElButton,{...attrs,class:[attrs.class,text?'text-action':'icon-button'],'aria-label':props.label},()=>text||h('img',{src:'artwork/'+(props.icon==='action-add'?'add':props.icon)+'.webp',alt:''}));
        return text?button():h(Hint,{content:props.label,disabled:!!attrs.disabled},{default:button});
      };
    },
  };
  const InlineField={
    props:{fieldKey:{type:String,required:true},value:[String,Number],label:String,as:{type:String,default:'span'},multiline:Boolean,maxlength:{type:Number,default:16},options:Array,onSave:{type:Function,required:true}},
    setup(props) {
      const editing=ref(false),draft=ref(props.value),error=ref(''),saving=ref(false),input=ref(null),trigger=ref(null),uid='inline-field-'+(++serial);
      const begin=(value)=>{draft.value=value===undefined?(drafts.get(props.fieldKey)?.value??props.value):value;error.value='';editing.value=true;drafts.set(props.fieldKey,{value:draft.value});nextTick(()=>input.value?.focus())};
      const finish=()=>{drafts.delete(props.fieldKey);editing.value=false;error.value='';nextTick(()=>trigger.value?.$el?.focus())};
      const cancel=()=>{if(!saving.value){draft.value=props.value;finish()}};
      watch(draft,v=>{if(editing.value)drafts.set(props.fieldKey,{value:v})});
      const save=async()=>{
        if(saving.value)return;
        const value=typeof draft.value==='string'?draft.value.trim():draft.value;
        if(!String(value??'').trim()){error.value='内容不能为空';input.value?.focus();return}
        if(!props.options&&((!props.multiline&&!/^[\u3400-\u9fff\d\s]+$/.test(String(value)))||(props.multiline&&/[A-Za-z]/.test(value)))){error.value=props.multiline?'请使用中文':'请输入简短中文名称';return}
        saving.value=true;error.value='';
        try{const result=await props.onSave(value);if(result!==true){error.value=typeof result==='string'?result:'保存失败';return}finish()}
        catch{error.value='保存失败'}finally{saving.value=false}
      };
      const key=e=>{if(e.isComposing)return;if(e.key==='Escape'){e.preventDefault();e.stopPropagation();cancel()}else if(e.key==='Enter'&&!props.multiline){e.preventDefault();save()}};
      return {editing,draft,error,saving,input,trigger,uid,begin,cancel,save,key};
    },
    template:`<div class="inline-field" :class="{'inline-field-editing':editing,'inline-field-multiline':multiline}" :data-inline-field="fieldKey">
      <template v-if="!editing"><component :is="as" class="inline-field-value">{{options?.find(o=>o.value===value)?.label||value||'未填写'}}</component><ui-hint :content="'修改'+label"><el-button ref="trigger" class="inline-edit-trigger icon-button" :aria-label="'修改'+label" @click="begin()"><img src="artwork/edit.webp" alt=""></el-button></ui-hint></template>
      <template v-else><div class="inline-field-editor" @keydown="key"><div v-if="options" class="choice-list inline-field-choices"><button v-for="option in options" :key="option.value" :class="{chosen:draft===option.value}" :aria-pressed="draft===option.value" @click="draft=option.value">{{option.label}}</button></div><el-input v-else ref="input" v-model="draft" :type="multiline?'textarea':'text'" :rows="3" :maxlength="maxlength" :aria-label="label" :aria-invalid="!!error" :aria-describedby="error?uid:undefined" :disabled="saving"></el-input><div class="inline-field-actions" data-action-group><el-button class="text-action confirm-action" :aria-label="'保存'+label" :disabled="saving" @click="save">{{saving?'保存中':'保存'}}</el-button><el-button class="text-action" :aria-label="'取消修改'+label" :disabled="saving" @click="cancel">取消</el-button></div></div><p v-if="error" :id="uid" class="inline-field-error" role="alert">{{error}}</p></template>
    </div>`,
  };
  window.LuzInteractions={install(app){app.directive('file-label',{mounted(el,binding){el.querySelectorAll('input[type=file]').forEach(input=>input.setAttribute('aria-label',binding.value))},updated(el,binding){el.querySelectorAll('input[type=file]').forEach(input=>input.setAttribute('aria-label',binding.value))}});app.component('UiFormPage',FormPage);app.component('UiDetailPage',{props:['heading'],emits:['close'],setup:(props,{slots,emit})=>()=>h(FormPage,{heading:props.heading,detail:true,onClose:()=>emit('close')},slots)});app.component('UiWheelField',WheelField);app.component('UiDateField',DateField);app.component('UiSection',Section);app.component('UiHint',Hint);app.component('UiAction',Action);app.component('UiInlineField',InlineField)}};
})();
