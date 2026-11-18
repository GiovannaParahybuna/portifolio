const t=document.getElementById("tema"),r=document.documentElement;
const ico=()=>t.textContent=r.dataset.theme==="dark"?"☀️":"🌙";ico();
t.onclick=()=>{r.dataset.theme=r.dataset.theme==="dark"?"light":"dark";try{localStorage.setItem("t",r.dataset.theme)}catch(e){}ico()};
const g=document.getElementById("projetos");
if(g)g.innerHTML=PROJETOS.map(p=>`<a class="card" href="projeto.html?id=${p.id}"><div class="ic">${p.icone}</div><h3>${p.titulo}</h3><div><span class="tag">${p.tag}</span>${p.status?` <span class="tag dev">🚧 ${p.status}</span>`:""}</div><p>${p.resumo}</p><span class="go">Ver projeto →</span></a>`).join("");
const pg=document.getElementById("projeto");
if(pg){const p=PROJETOS.find(x=>x.id===new URLSearchParams(location.search).get("id"))||PROJETOS[0];document.title=p.titulo;
 pg.innerHTML=`<a class="back" href="index.html#projetos">← Voltar</a><div class="pill">${p.tag}</div>${p.status?` <span class="pill dev">🚧 ${p.status}</span>`:""}<h1>${p.icone} <span>${p.titulo}</span></h1><p class="sub" style="margin-top:14px;max-width:680px">${p.detalhes}</p><div class="links">${p.links.map(l=>`<a class="btn o" href="${l[1]}" target="_blank" rel="noopener">${l[0]}</a>`).join("")}</div><div class="chips" style="margin-bottom:26px">${p.stack.map(s=>`<span class="chip">${s}</span>`).join("")}</div><ul class="dest">${p.destaques.map(d=>`<li>${d}</li>`).join("")}</ul><div id="extra"></div>`;
 if(p.id==="futebol")futebol(document.getElementById("extra"))}
async function futebol(el){
 const cores={W:"#22c55e",D:"#94a3b8",L:"#ef4444"},$=i=>document.getElementById(i);let j,liga;
 const get=async u=>{const r=await fetch(u);if(!r.ok)throw new Error(r.status);return r.json()};
 el.innerHTML=`<div class=tabs id=tabs></div><div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:22px"><button class=btn id=upd>🔄 Atualizar via API</button><span id=msg style="color:var(--mut);font-size:.85rem"></span></div><div id=tab></div>`;
 const msg=t=>$("msg").textContent=t;
 const desenhar=()=>{const rows=j.dados.filter(d=>d.competicao===liga).sort((a,b)=>b.pontos-a.pontos||b.saldo_de_gols-a.saldo_de_gols||b.gols_marcados-a.gols_marcados);
  const atk=[...rows].sort((a,b)=>b.gols_marcados-a.gols_marcados)[0],def=[...rows].sort((a,b)=>a.gols_sofridos-b.gols_sofridos)[0];
  $("tab").innerHTML=`<div class=kpis><div class=kpi><small>Líder</small><b>${rows[0].time}</b></div><div class=kpi><small>Melhor ataque</small><b>${atk.time} (${atk.gols_marcados})</b></div><div class=kpi><small>Melhor defesa</small><b>${def.time} (${def.gols_sofridos})</b></div></div>
  <div class=tw><table><tr><th>#</th><th style="text-align:left">Time</th><th>Pts</th><th>PJ</th><th>V</th><th>E</th><th>D</th><th>GP</th><th>GC</th><th>SG</th><th>Forma</th></tr>${rows.map((d,i)=>`<tr><td>${i+1}</td><td class=t><img src="${d.logo}" alt="">${d.time}</td><td class=p>${d.pontos}</td><td>${d.partidas}</td><td>${d.vitorias}</td><td>${d.empates}</td><td>${d.derrotas}</td><td>${d.gols_marcados}</td><td>${d.gols_sofridos}</td><td>${d.saldo_de_gols}</td><td>${String(d.forma||"").split(",").filter(Boolean).map(c=>`<span class=dot style="background:${cores[c]}"></span>`).join("")}</td></tr>`).join("")}</table></div>`};
 const abas=()=>{const ligas=[...new Set(j.dados.map(d=>d.competicao))];if(!ligas.includes(liga))liga=ligas[0];
  $("tabs").innerHTML=ligas.map(l=>`<button class="${l===liga?"on":""}">${l}</button>`).join("");
  $("tabs").querySelectorAll("button").forEach(b=>b.onclick=()=>{liga=b.textContent;abas();desenhar()})};
 const mostrar=(d,o)=>{j=d;abas();desenhar();msg(`${o} · ${new Date(j.atualizado_em).toLocaleString("pt-BR")}`)};
 try{mostrar(await get("data/classificacao.json?"+Date.now()),"Última atualização diária")}catch(e){el.innerHTML="<p class=sub>Não foi possível carregar os dados (use servidor local ou GitHub Pages).</p>";return}
 $("upd").onclick=async()=>{if(!CONFIG.API_URL){msg("API ao vivo ainda não configurada (veja o README).");return}
  $("upd").disabled=true;msg("Consultando a API…");
  try{mostrar(await get(CONFIG.API_URL),"Atualizado agora pela API")}catch(e){msg("Falha ao consultar a API. Mantendo os últimos dados salvos.")}$("upd").disabled=false}}
