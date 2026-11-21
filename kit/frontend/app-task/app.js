const {createApp,ref,reactive,computed,watch,nextTick}=Vue;
const storageKey='luz-app-task-v3';
const seed=[{id:1,title:'首页层级整理',category:'设计',done:false},{id:2,title:'移动流程设计',category:'设计',done:false},{id:3,title:'阅读笔记整理',category:'内容',done:false},{id:4,title:'交付清单核对',category:'事务',done:false},{id:5,title:'图标细节检查',category:'设计',done:true},{id:6,title:'需求范围确认',category:'事务',done:true}];
const validName=v=>typeof v==='string'&&/^[\u3400-\u9fff\d\s]{1,12}$/.test(v.trim());
function load(){try{const a=JSON.parse(localStorage.getItem(storageKey));if(Array.isArray(a)&&a.every(t=>validName(t.title)&&typeof t.done==='boolean'&&['设计','内容','事务'].includes(t.category)))return a}catch{}return structuredClone(seed)}
createApp({setup(){const tasks=ref(load()),tab=ref('pending'),creating=ref(false),draft=ref(''),newCategory=ref('设计'),expandedId=ref(null),announcement=ref(''),saveError=ref(false);
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
const categories=[{name:'全部',icon:'solid-tasks'},{name:'设计',icon:'solid-design'},{name:'内容',icon:'solid-content'},{name:'事务',icon:'solid-office'}];
const scoped=computed(()=>tasks.value.filter(t=>t.done===(tab.value==='done'))),shown=computed(()=>scoped.value.filter(t=>(category.value==='全部'||t.category===category.value)&&t.title.includes(query.value.trim())));
watch(tasks,t=>{try{localStorage.setItem(storageKey,JSON.stringify(t));saveError.value=false}catch{saveError.value=true}},{deep:true});
function changeTab(){expandedId.value=null;creating.value=false;announcement.value=''}
function openNew(){creating.value=true;draft.value='';newCategory.value=category.value==='全部'?'设计':category.value}
function closeNew(){creating.value=false;nextTick(()=>document.querySelector('.create-button')?.focus())}
function create(){if(!validName(draft.value))return;tasks.value.unshift({id:Date.now(),title:draft.value.trim(),category:newCategory.value,done:false});query.value='';category.value='全部';closeNew();announcement.value='已保存'}
function toggle(task){task.done=!task.done;expandedId.value=null;announcement.value=task.done?'已完成':'已恢复';nextTick(()=>document.querySelector('.task-content')?.focus())}
return{tasks,tab,category,query,creating,draft,newCategory,expandedId,announcement,saveError,categories,scoped,shown,validName,changeTab,openNew,closeNew,create,toggle};}}).use(vant).use(ElementPlus).use(LuzInteractions).mount('#app');
