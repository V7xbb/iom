'use client';
import {useEffect,useState} from 'react';
const API=(process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000').replace(/\/$/,'');
type News={id:number;title:string;body:string;image_url:string;created_at:string};
export default function NewsPage(){const [items,setItems]=useState<News[]>([]);useEffect(()=>{fetch(`${API}/api/news`).then(r=>r.ok?r.json():[]).then(setItems).catch(()=>setItems([]))},[]);return <main className="listing-page" dir="rtl"><a href="/" className="listing-brand">HKRROE ← الرئيسية</a><h1>الأخبار <em>والتحديثات</em></h1><p>كل جديد عن المنصة ومشاريعها.</p><div className="listing-grid">{items.map(n=><article key={n.id} className="listing-card">{n.image_url&&<img src={n.image_url} alt=""/>}<span>{n.created_at?new Date(n.created_at).toLocaleDateString('ar-EG'):'تحديث'}</span><h2>{n.title}</h2><p>{n.body}</p></article>)}</div>{!items.length&&<p>مفيش أخبار منشورة لسه.</p>}</main>}
