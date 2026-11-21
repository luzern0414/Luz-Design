const {createApp,ref,reactive,computed,watch,nextTick}=Vue;
const storageKey='luz-web-workspace-v3';
const seed=[{id:1,title:'首页层级整理',category:'设计',owner:'林小满',status:'active'},{id:2,title:'移动流程设计',category:'设计',owner:'陈一',status:'active'},{id:3,title:'阅读笔记整理',category:'内容',owner:'林小满',status:'todo'},{id:4,title:'交付清单核对',category:'事务',owner:'周宁',status:'todo'},{id:5,title:'组件细节检查',category:'设计',owner:'陈一',status:'todo'},{id:6,title:'品牌文案整理',category:'内容',owner:'林小满',status:'todo'},{id:7,title:'图标对齐检查',category:'设计',owner:'陈一',status:'done'},{id:8,title:'需求范围确认',category:'事务',owner:'周宁',status:'done'}];
const validName=v=>typeof v==='string'&&/^[\u3400-\u9fff\d\s]{1,12}$/.test(v.trim());
function load(){try{const t=JSON.parse(localStorage.getItem(storageKey));if(Array.isArray(t)&&t.every(t=>validName(t.title)&&['todo','active','done'].includes(t.status)&&['设计','内容','事务'].includes(t.category)&&validName(t.owner)))return t}catch{}return structuredClone(seed)}
createApp({setup(){const detailOpen=ref(false);const media=matchMedia('(max-width:700px)'),narrow=ref(media.matches);media.addEventListener('change',event=>narrow.value=event.matches);const tasks=ref(load()),tab=ref('pending'),selectedId=ref(1),creating=ref(false),draft=ref(''),error=ref(''),newCategory=ref('设计'),announcement=ref(''),saveError=ref(false);
const filters = reactive({
  pending: { category: '全部', query: '' },
  done: { category: '全部', query: '' },
});
const category = computed({
  get: () => filters[tab.value].category,
  set: value => { filters[tab.value].category = value; },
});
const query = computed({
  get: () => filters[tab.value].query,
  set: value => { filters[tab.value].query = value; },
});
const navigation=[{value:'pending',label:'待办',icon:'list'},{value:'done',label:'完成',icon:'archive'}],categories=[{name:'全部',icon:'solid-tasks'},{name:'设计',icon:'solid-design'},{name:'内容',icon:'solid-content'},{name:'事务',icon:'solid-office'}];
const scoped=computed(()=>tasks.value.filter(t=>(t.status==='done')===(tab.value==='done'))),shown=computed(()=>scoped.value.filter(t=>(category.value==='全部'||t.category===category.value)&&[t.title,t.owner].some(v=>v.includes(query.value.trim())))),selected=computed(()=>tasks.value.find(t=>t.id===selectedId.value)||null);
watch(tasks,t=>{try{localStorage.setItem(storageKey,JSON.stringify(t));saveError.value=false}catch{saveError.value=true}},{deep:true});
const statusText=s=>({todo:'待开始',active:'进行中',done:'已完成'}[s]);
function changeTab(value){detailOpen.value=false;tab.value=value;creating.value=false;selectedId.value=null;announcement.value=''}
function select(t){detailOpen.value=true;selectedId.value=t.id;creating.value=false}
function openNew(){creating.value=true;draft.value='';error.value='';newCategory.value=category.value==='全部'?'设计':category.value}
function closeNew(){creating.value=false;nextTick(()=>document.querySelector('.new-task')?.focus())}
function startTask(){if(selected.value)selected.value.status='active'}
function toggleDone(task=selected.value){if(!task)return;task.status=task.status==='done'?'todo':'done';announcement.value=task.status==='done'?'已完成':'已恢复';detailOpen.value=false;nextTick(()=>document.querySelector('.task-title')?.focus())}
function create(){if(!validName(draft.value)){error.value='请输入简短中文名称';return}const t={id:Date.now(),title:draft.value.trim(),category:newCategory.value,owner:'林小满',status:'todo'};tasks.value.unshift(t);category.value='全部';query.value='';selectedId.value=t.id;closeNew();announcement.value='已保存'}
return{detailOpen,narrow,tasks,tab,category,query,selectedId,creating,draft,error,newCategory,announcement,saveError,navigation,categories,scoped,shown,selected,statusText,changeTab,select,openNew,closeNew,startTask,toggleDone,create};}}).use(ElementPlus).use(LuzInteractions).mount('#app');
