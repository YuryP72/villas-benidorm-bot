(function(){
  const API = document.currentScript.getAttribute('data-api') || 'https://YOUR-APP.onrender.com';
  const VILLA = {
    main: 'https://villas-benidorm.com/renders/residence.jpg',
    gallery: [
      'https://villas-benidorm.com/renders/residence.jpg',
      'https://villas-benidorm.com/renders/modern_villa_sunset.jpg',
      'https://villas-benidorm.com/renders/modern_villa_forest_reflection.jpg',
      'https://villas-benidorm.com/renders/modern_villa_pool_after_dark.jpg',
      'https://villas-benidorm.com/renders/golden_evening_living_room.jpg'
    ],
    plans: {
      basement: 'https://villas-benidorm.com/renders/plans/floor-1.png',
      ground: 'https://villas-benidorm.com/renders/plans/floor0.png',
      first: 'https://villas-benidorm.com/renders/plans/floor1.png'
    }
  };
  const i18n = {
    ru: {btn:'Виллы Benidorm', title:'Резиденция Benidorm', loc:'📍 Локация', plans:'🗺️ Планировки', price:'💶 Цены', book:'📅 Просмотр', ask:'💬 Вопрос', send:'Отправить', name:'Имя', phone:'Телефон', msg:'Сообщение'},
    en: {btn:'Villas Benidorm', title:'Benidorm Residence', loc:'📍 Location', plans:'🗺️ Floor Plans', price:'💶 Prices', book:'📅 Viewing', ask:'💬 Ask', send:'Send', name:'Name', phone:'Phone', msg:'Message'},
    es: {btn:'Villas Benidorm', title:'Residencia Benidorm', loc:'📍 Ubicación', plans:'🗺️ Planos', price:'💶 Precios', book:'📅 Visita', ask:'💬 Pregunta', send:'Enviar', name:'Nombre', phone:'Teléfono', msg:'Mensaje'}
  };
  const lang = (navigator.language||'ru').slice(0,2);
  const t = i18n[lang] || i18n.ru;

  const css = `
  .vb-fab{position:fixed;right:20px;bottom:20px;z-index:99999;background:#0f172a;color:#fff;border:1px solid #d4af37;border-radius:999px;padding:14px 22px;font-family:Inter,sans-serif;cursor:pointer;box-shadow:0 10px 30px rgba(0,0,0,.4);font-weight:700;display:flex;gap:8px;align-items:center}
  .vb-modal{position:fixed;inset:0;z-index:100000;display:none;background:rgba(0,0,0,.55);backdrop-filter:blur(6px)}
  .vb-modal.open{display:flex;align-items:center;justify-content:center;padding:16px}
  .vb-card{width:100%;max-width:440px;background:#fff;border-radius:24px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.5);font-family:Inter,sans-serif;max-height:92vh;display:flex;flex-direction:column}
  .vb-hero{position:relative;height:260px;background:#000}
  .vb-hero img{width:100%;height:100%;object-fit:cover}
  .vb-hero-overlay{position:absolute;inset:0;background:linear-gradient(to top, rgba(0,0,0,.7), transparent 60%);display:flex;align-items:flex-end;padding:16px;color:#fff}
  .vb-tabs{display:flex;gap:6px;padding:10px 12px;overflow:auto;background:#f8fafc;border-bottom:1px solid #e2e8f0}
  .vb-tab{white-space:nowrap;padding:8px 12px;border-radius:999px;border:1px solid #e2e8f0;background:#fff;font-size:12px;font-weight:600;cursor:pointer}
  .vb-tab.active{background:#0f172a;color:#fff;border-color:#0f172a}
  .vb-content{padding:14px;overflow:auto}
  .vb-gallery{display:flex;gap:8px;overflow:auto;padding-bottom:6px}
  .vb-gallery img{width:72px;height:72px;border-radius:12px;object-fit:cover;cursor:pointer;border:2px solid transparent}
  .vb-gallery img.active{border-color:#d4af37}
  .vb-plan-img{width:100%;border-radius:16px;border:1px solid #e2e8f0}
  .vb-input{width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:10px;margin:6px 0;font-size:14px;box-sizing:border-box}
  .vb-send{width:100%;background:#0f172a;color:#fff;padding:12px;border-radius:12px;border:0;font-weight:700;cursor:pointer;margin-top:8px}
  `;
  const style=document.createElement('style'); style.textContent=css; document.head.appendChild(style);

  const fab=document.createElement('div'); fab.className='vb-fab'; fab.innerHTML=`<span>💎</span> ${t.btn}`; document.body.appendChild(fab);
  const modal=document.createElement('div'); modal.className='vb-modal';
  modal.innerHTML=`
    <div class="vb-card">
      <div class="vb-hero">
        <img id="vb-hero-img" src="${VILLA.main}" alt="residence">
        <div class="vb-hero-overlay"><div><div style="font-size:18px;font-weight:800">${t.title}</div><div style="font-size:12px;opacity:.9">villas-benidorm.com • 3 уровня • 5 рендеров</div></div></div>
        <span id="vb-close" style="position:absolute;top:12px;right:12px;background:rgba(0,0,0,.6);color:#fff;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</span>
      </div>
      <div class="vb-tabs">
        <div class="vb-tab active" data-tab="gallery">🖼️ Фото</div>
        <div class="vb-tab" data-tab="plans">${t.plans}</div>
        <div class="vb-tab" data-tab="location">${t.loc}</div>
        <div class="vb-tab" data-tab="price">${t.price}</div>
        <div class="vb-tab" data-tab="book">${t.book}</div>
      </div>
      <div class="vb-content" id="vb-content"></div>
    </div>
  `;
  document.body.appendChild(modal);

  const $ = s=>modal.querySelector(s);
  const contentEl = $('#vb-content');
  let activeTab='gallery';
  let activeGalleryIdx=0;

  function render(){
    if(activeTab==='gallery'){
      contentEl.innerHTML=`
        <div class="vb-gallery" id="vb-thumbs">
          ${VILLA.gallery.map((u,i)=>`<img src="${u}" data-i="${i}" class="${i===activeGalleryIdx?'active':''}" loading="lazy">`).join('')}
        </div>
        <div style="font-size:11px;color:#64748b;margin:8px 0">Источник: villas-benidorm.com/renders/* • ${activeGalleryIdx+1}/5</div>
        <input class="vb-input" id="vb-name" placeholder="${t.name}">
        <input class="vb-input" id="vb-phone" placeholder="${t.phone}">
        <textarea class="vb-input" id="vb-msg" rows="2" placeholder="${t.msg}"></textarea>
        <button class="vb-send" id="vb-send-btn">${t.send} в Telegram</button>
        <div id="vb-status" style="font-size:12px;color:#16a34a;margin-top:8px;display:none"></div>
      `;
      contentEl.querySelectorAll('#vb-thumbs img').forEach(img=>{
        img.onclick=()=>{activeGalleryIdx=parseInt(img.dataset.i); $('#vb-hero-img').src=VILLA.gallery[activeGalleryIdx]; render();};
      });
      bindSend();
    } else if(activeTab==='plans'){
      contentEl.innerHTML=`
        <div style="display:flex;gap:6px;margin-bottom:10px">
          <button class="vb-tab active" data-plan="basement">Basement -1</button>
          <button class="vb-tab" data-plan="ground">Ground</button>
          <button class="vb-tab" data-plan="first">First</button>
        </div>
        <img class="vb-plan-img" id="vb-plan-img" src="${VILLA.plans.basement}" alt="plan">
        <div style="font-size:11px;color:#64748b;margin-top:8px">Прямо с сайта: villas-benidorm.com/renders/plans/*.png — клик для увеличения</div>
      `;
      let current='basement';
      contentEl.querySelectorAll('[data-plan]').forEach(b=>{
        b.onclick=()=>{
          contentEl.querySelectorAll('[data-plan]').forEach(x=>x.classList.remove('active'));
          b.classList.add('active');
          current=b.dataset.plan;
          $('#vb-plan-img').src=VILLA.plans[current];
        };
      });
      $('#vb-plan-img').onclick=()=>window.open($('#vb-plan-img').src, '_blank');
    } else if(activeTab==='location'){
      contentEl.innerHTML=`<div style="font-size:14px;line-height:1.5">📍 Finestrat / Benidorm, Costa Blanca<br>Вид на море и skyline Benidorm<br><br><iframe width="100%" height="220" style="border:0;border-radius:12px" src="https://www.openstreetmap.org/export/embed.html?bbox=-0.16%2C38.54%2C-0.10%2C38.58&layer=mapnik&marker=38.56%2C-0.13"></iframe><div style="font-size:11px;color:#64748b;margin-top:6px">Карта — данные с сайта, уточняется</div></div>`;
    } else if(activeTab==='price'){
      contentEl.innerHTML=`<div style="font-size:14px"><b>Цена: по запросу</b><br>Данные подтягиваются с villas-benidorm.com<br><br><button class="vb-send" onclick="document.querySelector('[data-tab=book]').click()">Запросить цену</button></div>`;
    } else if(activeTab==='book'){
      contentEl.innerHTML=`
        <input class="vb-input" id="vb-name" placeholder="${t.name}">
        <input class="vb-input" id="vb-phone" placeholder="${t.phone}">
        <input class="vb-input" type="date" id="vb-date">
        <textarea class="vb-input" id="vb-msg" rows="3" placeholder="Когда удобно посмотреть?"></textarea>
        <button class="vb-send" id="vb-send-btn">${t.book}</button>
        <div id="vb-status" style="font-size:12px;color:#16a34a;margin-top:8px;display:none"></div>
      `;
      bindSend();
    }
  }

  function bindSend(){
    const btn = document.getElementById('vb-send-btn');
    if(!btn) return;
    btn.onclick = async ()=>{
      const payload = {
        name: document.getElementById('vb-name')?.value || 'Guest',
        phone: document.getElementById('vb-phone')?.value || '',
        message: document.getElementById('vb-msg')?.value || `Интерес: ${activeTab} ${VILLA.main}`,
        lang: lang,
        villa_id: 'residence',
        page_url: location.href,
        session_id: localStorage.getItem('villas_session') || Math.random().toString(36).slice(2,8)
      };
      localStorage.setItem('villas_session', payload.session_id);
      try{
        await fetch(`${API}/api/contact`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
        const st=document.getElementById('vb-status'); st.style.display='block'; st.textContent='✅ Отправлено! Ответ придет сюда и в Telegram.';
      }catch(e){alert('Ошибка, попробуйте еще раз');}
    };
  }

  modal.querySelectorAll('.vb-tabs .vb-tab').forEach(tab=>{
    tab.onclick=()=>{
      modal.querySelectorAll('.vb-tabs .vb-tab').forEach(x=>x.classList.remove('active'));
      tab.classList.add('active');
      activeTab=tab.dataset.tab;
      render();
    };
  });

  fab.onclick=()=>{modal.classList.add('open'); render();};
  $('#vb-close').onclick=()=>modal.classList.remove('open');
  modal.onclick=(e)=>{if(e.target===modal) modal.classList.remove('open');};
})();
