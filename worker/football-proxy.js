// Cloudflare Worker: consulta a football-data.org com o token guardado como segredo e devolve o mesmo JSON do site.
const LIGAS={Brasil:["Brasileirão","BSA"],Inglaterra:["Premier League","PL"],Espanha:["La Liga","PD"],Alemanha:["Bundesliga","BL1"],Itália:["Serie A","SA"],França:["Ligue 1","FL1"],Portugal:["Primeira Liga","PPL"]};
export default{async fetch(req,env,ctx){
 const cors={"Access-Control-Allow-Origin":env.ALLOWED_ORIGIN||"*","Content-Type":"application/json; charset=utf-8"};
 if(req.method==="OPTIONS")return new Response(null,{headers:{...cors,"Access-Control-Allow-Headers":"*"}});
 const cache=caches.default,key=new Request(new URL(req.url).origin+"/cache-classificacao");
 const hit=await cache.match(key);if(hit)return new Response(hit.body,{headers:cors});   // cache de 10 min protege o limite da API
 const dados=[];
 for(const [pais,[nome,cod]] of Object.entries(LIGAS)){
  const r=await fetch(`https://api.football-data.org/v4/competitions/${cod}/standings`,{headers:{"X-Auth-Token":env.FOOTBALL_TOKEN}});
  if(!r.ok)return new Response(JSON.stringify({erro:r.status,liga:cod,token_configurado:!!env.FOOTBALL_TOKEN,detalhe:(await r.text()).slice(0,300)}),{status:502,headers:cors});
  for(const s of (await r.json()).standings){if(s.type&&s.type!=="TOTAL")continue;
   for(const t of s.table)dados.push({pais,competicao:nome,time:t.team.name,logo:t.team.crest,pontos:t.points,partidas:t.playedGames,forma:t.form||"",vitorias:t.won,empates:t.draw,derrotas:t.lost,gols_marcados:t.goalsFor,gols_sofridos:t.goalsAgainst,saldo_de_gols:t.goalDifference})}}
 const out=new Response(JSON.stringify({atualizado_em:new Date().toISOString(),dados}),{headers:{...cors,"Cache-Control":"public, max-age=600"}});
 ctx.waitUntil(cache.put(key,out.clone()));return out}}
