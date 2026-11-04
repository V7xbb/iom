'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  Activity, ArrowDown, ArrowLeft, ArrowUpLeft, BadgeCheck, Bot, BrainCircuit,
  CalendarDays, Check, CheckCircle2, Code2, Crown, ExternalLink, Globe2,
  Instagram, Menu, MessageCircle, Moon, Newspaper, Radio, Send, Settings,
  ShieldCheck, Sun, Terminal, Users, Zap, Youtube, X, Music2, Copy, QrCode,
  Laptop, Cpu, ChevronLeft, UserRound, Gamepad2
} from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';

type Project = { id:number; title:string; description:string; category:string; tech_stack:string; image_url:string; demo_url:string; source_url:string; status:string; featured:boolean };
type News = { id:number; title:string; body:string; image_url:string; created_at?:string };
type ActivityItem = { id:number; message:string; created_at:string };
type Socials = { telegram:string; whatsapp:string; instagram:string; tiktok:string; youtube:string; discord:string };
const API = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const fallbackSocials:Socials = {telegram:'https://t.me/hkrroe',whatsapp:'https://wa.me/201201165541',instagram:'https://instagram.com/hkrroe',tiktok:'https://www.tiktok.com/@hkrroe',youtube:'https://www.youtube.com/@hkrroe',discord:'https://discord.com/app'};
const services = [
  { icon:Bot, title:'تطوير بوتات Telegram', sub:'بوتات ذكية وأنظمة خدمات متكاملة' },
  { icon:BrainCircuit, title:'حلول الذكاء الاصطناعي', sub:'دمج نماذج AI وأدوات ذكية' },
  { icon:Zap, title:'أتمتة المهام والأنظمة', sub:'ربط الخدمات وتوفير الوقت' },
  { icon:Code2, title:'برمجة Python', sub:'واجهات API وبرامج مخصصة' },
  { icon:Globe2, title:'تطوير مواقع الويب', sub:'تجارب رقمية سريعة ومتجاوبة' },
  { icon:ShieldCheck, title:'أمان وحماية', sub:'بناء تطبيقات بممارسات آمنة' },
];
const navItems = [['الرئيسية','#home'],['من أنا','#about'],['مشاريعي','#projects'],['خدماتي','#services'],['الأخبار','#news'],['توثيق HKRROE','#verified'],['تواصل معنا','#contact']] as const;

function fmtDate(value?:string) { if(!value) return 'تاريخ النشر'; const d=new Date(value); return Number.isNaN(d.getTime())?'تاريخ النشر':new Intl.DateTimeFormat('ar-EG',{dateStyle:'medium'}).format(d); }
function uptimeLabel(seconds:number|null) { if(seconds===null) return 'غير متاح'; const d=Math.floor(seconds/86400), h=Math.floor((seconds%86400)/3600), m=Math.floor((seconds%3600)/60); return d?`${d} يوم ${h} ساعة`:h?`${h} ساعة ${m} دقيقة`:`${m} دقيقة`; }

export default function Home() {
  const [dark,setDark]=useState(true), [mobileOpen,setMobileOpen]=useState(false);
  const [projects,setProjects]=useState<Project[]>([]), [news,setNews]=useState<News[]>([]), [activity,setActivity]=useState<ActivityItem[]>([]);
  const [socials,setSocials]=useState<Socials>(fallbackSocials);
  const [stats,setStats]=useState<{projects:number;visits:number;uptime_seconds:number}|null>(null);
  const [health,setHealth]=useState<{status:string;database:string;uptime_seconds:number}|null>(null);
  const [verifyId,setVerifyId]=useState(''), [verifyMsg,setVerifyMsg]=useState('');
  const [copied,setCopied]=useState(false);
  const [discordCopied,setDiscordCopied]=useState(false);
  const [identityUrl,setIdentityUrl]=useState('https://example.com/identity/HKR-USER-0001');

  useEffect(()=>{
    setIdentityUrl(`${window.location.origin}/identity/HKR-USER-0001`);
    let alive=true;
    const load=async()=>{
      const requests = await Promise.allSettled([
        fetch(`${API}/api/projects`).then(r=>r.ok?r.json():[]),
        fetch(`${API}/api/news`).then(r=>r.ok?r.json():[]),
        fetch(`${API}/api/activity`).then(r=>r.ok?r.json():[]),
        fetch(`${API}/api/stats`).then(r=>r.ok?r.json():null),
        fetch(`${API}/api/health`).then(r=>r.ok?r.json():null),
        fetch(`${API}/api/settings`).then(r=>r.ok?r.json():null),
      ]);
      if(!alive) return;
      const get=(i:number)=>requests[i].status==='fulfilled'?requests[i].value:null;
      setProjects(Array.isArray(get(0))?get(0):[]); setNews(Array.isArray(get(1))?get(1):[]); setActivity(Array.isArray(get(2))?get(2):[]);
      setStats(get(3)); setHealth(get(4)); if(get(5)?.socials) setSocials({...fallbackSocials,...get(5).socials});
    };
    load();
    const timer=window.setInterval(async()=>{
      try { const [h,a,s]=await Promise.all([fetch(`${API}/api/health`),fetch(`${API}/api/activity`),fetch(`${API}/api/stats`)]); if(!alive)return; if(h.ok)setHealth(await h.json());if(a.ok)setActivity(await a.json());if(s.ok)setStats(await s.json()); } catch { if(alive)setHealth(null); }
    },30000);
    try { if(!sessionStorage.getItem('hkrroe-visit-recorded')) { fetch(`${API}/api/visits`,{method:'POST'}).then(()=>sessionStorage.setItem('hkrroe-visit-recorded','1')).catch(()=>{}); } } catch {}
    return ()=>{alive=false;window.clearInterval(timer);};
  },[]);

  const uptime=health?.uptime_seconds ?? stats?.uptime_seconds ?? null;
  const socialItems=useMemo(()=>[
    {key:'telegram',name:'Telegram',handle:'@hkrroe',Icon:Send,url:socials.telegram,cls:'telegram'},
    {key:'whatsapp',name:'WhatsApp',handle:'01201165541',Icon:MessageCircle,url:socials.whatsapp,cls:'whatsapp'},
    {key:'instagram',name:'Instagram',handle:'@hkrroe',Icon:Instagram,url:socials.instagram,cls:'instagram'},
    {key:'tiktok',name:'TikTok',handle:'@hkrroe',Icon:Music2,url:socials.tiktok,cls:'tiktok'},
    {key:'youtube',name:'YouTube',handle:'@hkrroe',Icon:Youtube,url:socials.youtube,cls:'youtube'},
    {key:'discord',name:'Discord',handle:'rtx_vipq',Icon:Gamepad2,url:socials.discord,cls:'discord'},
  ],[socials]);

  async function verify(e:React.FormEvent<HTMLFormElement>) {
    e.preventDefault(); if(!verifyId.trim()){setVerifyMsg('اكتب رقم الشهادة الأول.');return;} setVerifyMsg('جاري التحقق...');
    try {const r=await fetch(`${API}/api/verified/${encodeURIComponent(verifyId.trim())}`);const d=await r.json();setVerifyMsg(r.ok?`الاسم: ${d.subject} — الحالة: ${d.status==='approved'?'معتمدة':d.status==='revoked'?'ملغاة':'قيد المراجعة'}`:'رقم الشهادة مش موجود.');}catch{setVerifyMsg('خدمة التحقق غير متاحة حاليًا.');}
  }
  async function copyDiscord(){try{await navigator.clipboard.writeText('rtx_vipq');setDiscordCopied(true);setTimeout(()=>setDiscordCopied(false),2200);}catch{setDiscordCopied(false);}}
  async function copyIdentity(){try{await navigator.clipboard.writeText(identityUrl);setCopied(true);setTimeout(()=>setCopied(false),2200);}catch{setCopied(false);}}

  return <main className={dark?'site':'site light'} dir="rtl">
    <header className="topbar">
      <a className="brand" href="#home" aria-label="HKRROE الرئيسية"><span className="brand-mark">H</span><span className="brand-copy"><b>HKRROE</b><small>Building Smart Digital Experiences.</small></span></a>
      <nav className="desktop-nav" aria-label="التنقل الرئيسي">{navItems.map(([label,href],i)=><a className={i===0?'active':''} href={href} key={href}>{label}</a>)}</nav>
      <div className="top-actions"><a className="dashboard-link" href="/dashboard"><Crown size={16}/> لوحة التحكم</a><button className="theme-btn" onClick={()=>setDark(!dark)} aria-label="تغيير المظهر">{dark?<Sun size={19}/>:<Moon size={19}/>}</button><button className="mobile-menu" onClick={()=>setMobileOpen(!mobileOpen)} aria-label="القائمة">{mobileOpen?<X/>:<Menu/>}</button></div>
    </header>
    {mobileOpen&&<nav className="mobile-nav">{navItems.map(([label,href])=><a href={href} key={href} onClick={()=>setMobileOpen(false)}>{label}</a>)}<a href="/dashboard">لوحة التحكم</a></nav>}

    <section className="hero" id="home">
      <div className="hero-grid"/><div className="hero-glow glow-one"/><div className="hero-glow glow-two"/>
      <div className="hero-copy"><span className="welcome-script">Welcome to <b>HKRROE</b></span><h1>بوابتك لعالم التكنولوجيا والخدمات الرقمية</h1><p>أكتر من مجرد موقع... إحنا مجتمع متكامل.</p><div className="hero-buttons"><a className="btn-primary" href="#projects">ابدأ الآن <ArrowUpLeft size={18}/></a><a className="btn-outline" href="#about">شاهد العرض <ArrowDown size={17}/></a></div></div>
      <div className="hero-mascot" aria-label="شخصية HKRROE"><div className="mascot-ring ring-a"/><div className="mascot-ring ring-b"/><img src="/images/hkrroe-mascot-hero.webp" alt="شخصية HKRROE المقنّعة بإضاءة خضراء"/><div className="mascot-caption">HKRROE · CYBER NEO</div></div>
      <aside className="live-console"><div className="console-head"><span className="live-dot"/> LIVE COMMAND CENTER <Activity size={15}/></div><div className="console-status"><div className="signal-bars"><i/><i/><i/><i/><i/></div><div><span>حالة الموقع</span><b>{health?.status==='ok'?'يعمل بشكل طبيعي':'غير متصل / غير مفحوص'}</b></div></div><div className="console-line"><span className={`health-led ${health?.database==='connected'?'on':'off'}`}/><span>قاعدة البيانات</span><b>{health?.database==='connected'?'متصلة':health?.database==='disconnected'?'غير متصلة':'غير معروف'}</b></div><div className="console-line"><span className={`health-led ${health?.status==='ok'?'on':'off'}`}/><span>حالة API</span><b>{health?.status==='ok'?'نشط':'غير متاح'}</b></div><div className="console-divider"/><div className="console-title">آخر الأنشطة <span>●</span></div>{activity.slice(0,3).map(a=><div className="console-activity" key={a.id}><Activity size={15}/><span>{a.message}</span></div>)}{activity.length===0&&<div className="console-empty">مفيش أنشطة مسجلة لسه</div>}<div className="console-foot">مدة تشغيل الخدمة: {uptimeLabel(uptime)}</div></aside>
      <div className="hero-stats"><div><Code2/><b>{stats?`+${stats.projects}`:'—'}</b><small>مشاريع منشورة</small></div><div><Users/><b>{stats?`+${stats.visits.toLocaleString('en-US')}`:'—'}</b><small>زوار فريدون اليوم</small></div></div>
    </section>

    <section className="social-stage" aria-label="منصات التواصل"><div className="stage-orbit"/><div className="social-3d-grid">{socialItems.map(({key,name,handle,Icon,url,cls})=>key==='discord'?<button className={`social-cube ${cls}`} key={key} onClick={copyDiscord}><span className="cube-face"><Icon/><b>{name}</b><small>{discordCopied?'تم نسخ الاسم':handle}</small></span></button>:<a className={`social-cube ${cls}`} key={key} href={url} target="_blank" rel="noopener noreferrer"><span className="cube-face"><Icon/><b>{name}</b><small>{handle}</small></span></a>)}</div></section>

    <section className="services-strip" id="services">{services.map(({icon:Icon,title,sub})=><article className="service-tile" key={title}><Icon size={31}/><b>{title}</b><small>{sub}</small></article>)}</section>

    <section className="dashboard-panels">
      <article className="panel projects-panel" id="projects"><div className="panel-heading"><h3>مشاريعنا المميزة</h3><a href="/projects">عرض الكل <ArrowLeft size={15}/></a></div>{projects.filter(p=>p.featured).slice(0,2).map(p=><div className="featured-project" key={p.id}><div className="project-thumb"><Code2 size={45}/><span>HKRROE</span></div><div className="project-info"><span className="status-tag">{p.status==='completed'?'مكتمل':p.status==='in-progress'?'قيد التطوير':p.status}</span><h4>{p.title}</h4><p>{p.description}</p><div className="project-actions">{p.demo_url&&<a href={p.demo_url} target="_blank" rel="noreferrer">عرض المشروع <ExternalLink size={13}/></a>}{p.source_url&&<a href={p.source_url} target="_blank" rel="noreferrer">المصدر <ExternalLink size={13}/></a>}</div></div></div>)}{projects.filter(p=>p.featured).length===0&&<div className="empty-state"><Laptop size={32}/><b>مفيش مشاريع مميزة منشورة لسه</b><small>أضف مشاريعك من لوحة التحكم وهتظهر هنا تلقائيًا.</small></div>}</article>
      <article className="panel services-panel"><div className="panel-heading"><h3>خدماتنا</h3><span className="panel-icon">✦</span></div><ul>{services.slice(0,4).map(s=><li key={s.title}><CheckCircle2 size={17}/>{s.title}</li>)}</ul><p className="service-note">خدمات ومشاريع حسب الطلب — تواصل لمعرفة التفاصيل.</p></article>
      <article className="panel certificate-panel" id="verified"><div className="panel-heading"><h3>بطاقة الهوية الرقمية</h3><BadgeCheck/></div><div className="mini-id"><div className="mini-shield"><ShieldCheck size={48}/></div><div><b>HKRROE</b><strong>Digital Identity</strong><small>ID: HKR-USER-0001</small></div><div className="mini-qr"><QRCodeSVG value={identityUrl} size={78} bgColor="#ffffff" fgColor="#05100a" level="M"/></div></div><p className="certificate-note">بطاقة تعريف رقمية خاصة بمنصة HKRROE، وليست توثيقًا رسميًا من أي منصة خارجية.</p><div className="id-actions"><a href="/identity/HKR-USER-0001">عرض البطاقة</a><button onClick={copyIdentity}><Copy size={14}/>{copied?'تم النسخ':'نسخ رابط البطاقة'}</button></div></article>
    </section>

    <section className="lower-sections" id="about"><div className="lower-card about-card"><span className="section-eyebrow">01 / من أنا</span><h2>بنبني أفكار<br/><em>تتحول لواقع.</em></h2><p>HKRROE هوية تطوير رقمية مستقلة بتركّز على البرمجة، الأتمتة، وحلول الذكاء الاصطناعي، بهدف تقديم أدوات وتجارب رقمية مفيدة.</p><a href="#contact">تواصل معايا <ArrowLeft size={15}/></a></div><div className="lower-card news-card" id="news"><div className="panel-heading"><h3>آخر الأخبار والتحديثات</h3><a href="/news">عرض الكل <ArrowLeft size={15}/></a></div>{news.slice(0,2).map(n=><div className="news-item" key={n.id}><div className="news-visual"><Newspaper size={36}/><span>HKRROE</span></div><div><span className="status-tag">تحديث</span><h4>{n.title}</h4><p>{n.body}</p><small><CalendarDays size={13}/> {fmtDate(n.created_at)}</small></div></div>)}{news.length===0&&<div className="empty-state compact"><Newspaper/><b>مفيش أخبار منشورة حاليًا</b><small>الأخبار اللي هتنشرها من لوحة التحكم هتظهر هنا.</small></div>}</div></section>

    <section className="verify-section"><div className="section-title"><span>HKRROE / VERIFICATION</span><h2>تحقق من <em>الهوية</em></h2><p>افحص رقم شهادة صادر من نظام HKRROE الداخلي.</p></div><form className="verify-form" onSubmit={verify}><input value={verifyId} onChange={e=>setVerifyId(e.target.value)} placeholder="مثال: HKR-XXXXXXXXXX" aria-label="رقم شهادة التحقق"/><button type="submit"><ShieldCheck size={16}/> تحقق الآن</button></form>{verifyMsg&&<p className="verify-message" role="status">{verifyMsg}</p>}</section>

    <footer id="contact"><div className="footer-brand"><span className="brand-mark">H</span><div><b>HKRROE</b><small>Building Smart Digital Experiences.</small></div></div><p>HKRROE <i/> Assiut, Egypt <i/> Building Smart Digital Experiences.</p><div className="footer-socials">{socialItems.map(({key,name,Icon,url})=>key==='discord'?<button key={key} onClick={copyDiscord} aria-label="نسخ اسم Discord"><Icon/></button>:<a key={key} href={url} target="_blank" rel="noopener noreferrer" aria-label={name}><Icon/></a>)}</div><a className="footer-contact" href={socials.whatsapp}>تواصل معايا <Send size={15}/></a></footer>
    <div className="copyright">© {new Date().getFullYear()} HKRROE. All rights reserved. <span>MORE THAN A WEBSITE.</span></div>
  </main>;
}
