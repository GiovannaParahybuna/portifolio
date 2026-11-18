# Portfólio – Giovanna
Site estático. Teste local: `python -m http.server` → http://localhost:8000
- Projetos: edite `js/projetos.js`. Configure `REPO` em `js/config.js`.
- Futebol, atualização diária: workflow `.github/workflows/atualizar.yml` (segredo `FOOTBALL_TOKEN` no GitHub).
- Futebol, botão "Atualizar via API" (tempo real): publique `worker/football-proxy.js` como Cloudflare Worker,
  crie o segredo `FOOTBALL_TOKEN`, (opcional) a variável `ALLOWED_ORIGIN` com a URL do seu site e cole a URL do Worker em `API_URL` (`js/config.js`).
