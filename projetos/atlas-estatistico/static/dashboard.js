let RECORDS = [];
let KPIS = {};
let RANKINGS = [];

document.getElementById('today-tag').textContent =
  new Date().toLocaleDateString('pt-BR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

document.getElementById('genTag').textContent =
  'Gerado em ' + new Date().toLocaleDateString('pt-BR');


/* ---------- Country flag helper ---------- */

function flagImg(iso2, country = '') {

  if (!iso2 || typeof iso2 !== 'string') {
    return '';
  }

  const code = iso2.trim().toLowerCase();

  if (!/^[a-z]{2}$/.test(code)) {
    return '';
  }

  return `
    <img
      class="country-flag"
      src="https://flagcdn.com/w40/${code}.png"
      alt="Bandeira de ${country}"
      loading="lazy"
      onerror="this.style.display='none'"
    >
  `;
}


/* ---------- Theme toggle ---------- */

const root = document.documentElement;
const themeBtn = document.getElementById('themeToggle');
let currentTheme = null;

if (themeBtn) {

  themeBtn.addEventListener('click', () => {

    const prefersDark =
      window.matchMedia(
        '(prefers-color-scheme: dark)'
      ).matches;

    if (currentTheme === null) {

      currentTheme =
        prefersDark
          ? 'light'
          : 'dark';

    } else {

      currentTheme =
        currentTheme === 'dark'
          ? 'light'
          : 'dark';

    }

    root.setAttribute(
      'data-theme',
      currentTheme
    );

    themeBtn.textContent =
      currentTheme === 'dark'
        ? 'Modo claro'
        : 'Modo escuro';

    renderAll();

  });

}


/* ---------- Formatting helpers ---------- */

function fmtInt(n) {

  if (
    n === null ||
    n === undefined ||
    !Number.isFinite(Number(n))
  ) {
    return '—';
  }

  return Math
    .round(Number(n))
    .toLocaleString('pt-BR');

}


function fmtCompact(n) {

  if (
    n === null ||
    n === undefined ||
    !Number.isFinite(Number(n))
  ) {
    return '—';
  }

  n = Number(n);

  if (n >= 1e9) {

    return (
      (n / 1e9)
        .toFixed(2)
        .replace('.', ',') +
      ' bi'
    );

  }

  if (n >= 1e6) {

    return (
      (n / 1e6)
        .toFixed(1)
        .replace('.', ',') +
      ' mi'
    );

  }

  if (n >= 1e3) {

    return (
      (n / 1e3)
        .toFixed(0) +
      ' mil'
    );

  }

  return fmtInt(n);

}


function fmtPct(n, d) {

  if (
    n === null ||
    n === undefined ||
    !Number.isFinite(Number(n))
  ) {
    return '—';
  }

  return (
    Number(n)
      .toFixed(d ?? 2)
      .replace('.', ',') +
    '%'
  );

}


/* ---------- KPI strip ---------- */

function renderKPIs() {

  const items = [

    {
      label: 'População mundial (soma)',
      value: fmtCompact(
        KPIS.total_population
      ),
      flag: null,
      sub:
        KPIS.n_countries +
        ' países e territórios cobertos'
    },

    {
      label: 'Maior território',
      value: KPIS.largest_country,
      flag: KPIS.largest_country_iso2,
      sub:
        fmtCompact(
          KPIS.largest_country_value
        ) +
        ' km²'
    },

    {
      label: 'IDH mediano',
      value:
        Number(KPIS.median_hdi)
          .toFixed(3)
          .replace('.', ','),
      flag: KPIS.max_hdi_iso2,
      sub:
        KPIS.max_hdi_country +
        ' lidera (' +
        Number(KPIS.max_hdi_value)
          .toFixed(3)
          .replace('.', ',') +
        ')'
    },

    {
      label: 'Maior fatia de água do mundo',
      value: KPIS.most_world_water,
      flag: KPIS.most_world_water_iso2,
      sub:
        fmtPct(
          KPIS.most_world_water_value,
          1
        ) +
        ' de toda a água interior do planeta'
    },

    {
      label: 'Área terrestre total',
      value:
        fmtCompact(
          KPIS.total_land_km2
        ) +
        ' km²',
      flag: null,
      sub:
        'Soma da área de terra de todos os países'
    },

    {
      label: 'Fecundidade média',
      value:
        Number(KPIS.avg_fertility)
          .toFixed(2)
          .replace('.', ',') +
        ' filhos/mulher',
      flag: null,
      sub:
        'Correlação de ' +
        Number(KPIS.corr_hdi_fertility)
          .toFixed(2)
          .replace('.', ',') +
        ' com o IDH'
    },

    {
      label: 'Densidade média',
      value:
        fmtInt(KPIS.avg_density) +
        ' hab/km²',
      flag: KPIS.most_dense_iso2,
      sub:
        KPIS.most_dense +
        ' é o mais denso (' +
        fmtInt(KPIS.most_dense_value) +
        ')'
    },

    {
      label: 'Menor IDH',
      value: KPIS.min_hdi_country,
      flag: KPIS.min_hdi_iso2,
      sub:
        'IDH de ' +
        Number(KPIS.min_hdi_value)
          .toFixed(3)
          .replace('.', ',')
    }

  ];


  document.getElementById(
    'kpiStrip'
  ).innerHTML =

    items.map(it => `

      <div class="kpi">

        <div class="kpi-label">
          ${it.label}
        </div>

        <div class="kpi-value">

          ${
            it.flag
              ? flagImg(
                  it.flag,
                  it.value
                )
              : ''
          }

          ${it.value}

        </div>

        <div class="kpi-sub">
          ${it.sub}
        </div>

      </div>

    `).join('');


  const corrTag =
    document.getElementById(
      'corrTag'
    );

  if (corrTag) {

    corrTag.textContent =
      Number(
        KPIS.corr_hdi_fertility
      )
        .toFixed(3)
        .replace('.', ',');

  }

}


/* ---------- Ranking cards ---------- */

function renderRankGrid() {

  const cfg = [

    {
      key: 'top_area',
      title: 'Extensão territorial',
      unit: 'km²',
      fmt: v => fmtCompact(v)
    },

    {
      key: 'top_population',
      title: 'População',
      unit: 'habitantes',
      fmt: v => fmtCompact(v)
    },

    {
      key: 'top_hdi',
      title: 'IDH',
      unit: 'índice (0–1)',
      fmt: v =>
        Number(v)
          .toFixed(3)
          .replace('.', ',')
    },

    {
      key: 'top_world_water',
      title: '% da água interior do mundo',
      unit: 'participação global',
      fmt: v =>
        fmtPct(v, 2)
    }

  ];


  document.getElementById(
    'rankGrid'
  ).innerHTML =

    cfg.map(c => {

      const items =
        RANKINGS[c.key] || [];


      const list =
        items.map((it, i) => `

          <li>

            <span class="rank-n">
              ${i + 1}
            </span>

            <span class="rank-flag">
              ${flagImg(
                it.iso2,
                it.country
              )}
            </span>

            <span class="rank-name">
              ${it.country}
            </span>

            <span class="rank-val">
              ${c.fmt(it.value)}
            </span>

          </li>

        `).join('');


      return `

        <div class="rank-cell">

          <h3>
            ${c.title}
          </h3>

          <p class="rank-unit">
            ${c.unit}
          </p>

          <ul class="rank-list">
            ${list}
          </ul>

        </div>

      `;

    }).join('');

}


/* ---------- Plotly theme helper ---------- */

function plotlyColors() {

  const cs =
    getComputedStyle(
      document.documentElement
    );

  return {

    fg:
      cs.getPropertyValue(
        '--fg'
      ).trim(),

    fgDim:
      cs.getPropertyValue(
        '--fg-dim'
      ).trim(),

    bg:
      cs.getPropertyValue(
        '--bg'
      ).trim(),

    bgPanel:
      cs.getPropertyValue(
        '--bg-panel'
      ).trim(),

    bgFeature:
      cs.getPropertyValue(
        '--bg-feature'
      ).trim(),

    brass:
      cs.getPropertyValue(
        '--brass'
      ).trim(),

    teal:
      cs.getPropertyValue(
        '--teal'
      ).trim(),

    coral:
      cs.getPropertyValue(
        '--coral'
      ).trim(),

    sage:
      cs.getPropertyValue(
        '--sage'
      ).trim(),

    line:
      cs.getPropertyValue(
        '--line'
      ).trim()

  };

}

function baseLayout(extra) {

  const c =
    plotlyColors();


  return Object.assign({

    paper_bgcolor:
      'rgba(0,0,0,0)',

    plot_bgcolor:
      'rgba(0,0,0,0)',

    font: {

      family:
        'Inter, sans-serif',

      color:
        c.fgDim,

      size: 12

    },

    margin: {

      t: 10,
      r: 10,
      b: 36,
      l: 44

    }

  }, extra || {});

}


const commonConfig = {

  displayModeBar: false,

  responsive: true

};


/* ---------- Featured map ---------- */

let currentMetric =
  'population';


/*
 * Escala principal do mapa:
 *
 * Azul profundo -> Violeta -> Laranja
 *
 * A ideia é criar uma diferença visual
 * muito maior entre países com valores baixos,
 * médios e altos.
 */


const MAP_COLORSCALE = [

  [0.00, '#163A70'],

  [0.35, '#1677B8'],

  [0.65, '#20A6A0'],

  [1.00, '#F4B942']

];


const metricMeta = {

  population: {

    label: 'População',

    colorscale:
      MAP_COLORSCALE,

    transform:
      v => Math.log10(v + 1),

    fmt:
      v => fmtCompact(v)

  },


  hdi: {

    label: 'IDH',

    colorscale:
      MAP_COLORSCALE,

    transform:
      v => v,

    fmt:
      v =>
        v != null
          ? Number(v)
              .toFixed(3)
              .replace('.', ',')
          : '—'

  },


  total_km2: {

    label: 'Território (km²)',

    colorscale:
      MAP_COLORSCALE,

    transform:
      v => Math.log10(v + 1),

    fmt:
      v =>
        fmtCompact(v) +
        ' km²'

  },


  density: {

    label: 'Densidade (hab/km²)',

    colorscale:
      MAP_COLORSCALE,

    transform:
      v => Math.log10(v + 1),

    fmt:
      v =>
        fmtInt(v) +
        '/km²'

  },


  fertility: {

    label: 'Fecundidade',

    colorscale:
      MAP_COLORSCALE,

    transform:
      v => v,

    fmt:
      v =>
        v != null
          ? Number(v)
              .toFixed(2)
              .replace('.', ',')
          : '—'

  },


  pct_world_water: {

    label:
      '% da água interior do mundo',

    colorscale:
      MAP_COLORSCALE,

    transform:
      v => Math.log10(v + 0.05),

    fmt:
      v => fmtPct(v, 2)

  }

};

function renderMap() {

  const meta =
    metricMeta[currentMetric];


  const rows =
    RECORDS.filter(r =>

      r[currentMetric] !== null &&
      r[currentMetric] !== undefined &&
      r.iso3

    );


  if (!rows.length) {
    return;
  }


  const c =
    plotlyColors();


  const zVals =
    rows.map(r =>
      meta.transform(
        Number(
          r[currentMetric]
        )
      )
    );


  const trace = [{

    type:
      'choropleth',

    locations:
      rows.map(r =>
        r.iso3
      ),

    z:
      zVals,

    text:
      rows.map(r =>
        r.country +
        '<br>' +
        meta.label +
        ': ' +
        meta.fmt(
          r[currentMetric]
        )
      ),

    hoverinfo:
      'text',

    colorscale:
      meta.colorscale,

    showscale:
      false,

    marker: {

      line: {

        color:
          c.bg,

        width:
          0.5

      }

    }

  }];


  const layout =
    baseLayout({

      geo: {

        showframe:
          false,

        showcoastlines:
          false,

        projection: {

          type:
            'natural earth'

        },

        bgcolor:
          'rgba(0,0,0,0)',

        landcolor:
          c.bgPanel,

        showland:
          true,

        lakecolor:
          c.bgFeature

      },

      margin: {

        t: 6,
        r: 6,
        b: 6,
        l: 6

      },

      height:
        640

    });


  Plotly.newPlot(

    'map',

    trace,

    layout,

    commonConfig

  );


  /*
   * A legenda externa continua sendo atualizada
   * somente se existir no HTML.
   */

  const legendMin =
    document.getElementById(
      'legendMin'
    );

  const legendMax =
    document.getElementById(
      'legendMax'
    );

  const legendBar =
    document.getElementById(
      'legendBar'
    );


  if (
    legendMin &&
    legendMax &&
    legendBar
  ) {

    const minRow =
      rows.reduce((a, b) =>

        Number(
          a[currentMetric]
        ) <
        Number(
          b[currentMetric]
        )
          ? a
          : b

      );


    const maxRow =
      rows.reduce((a, b) =>

        Number(
          a[currentMetric]
        ) >
        Number(
          b[currentMetric]
        )
          ? a
          : b

      );


    legendMin.textContent =
      minRow.country +
      ' · ' +
      meta.fmt(
        minRow[currentMetric]
      );


    legendMax.textContent =
      maxRow.country +
      ' · ' +
      meta.fmt(
        maxRow[currentMetric]
      );


    legendBar.style.background =
      'linear-gradient(90deg, ' +
      meta.colorscale
        .map(p => p[1])
        .join(',') +
      ')';

  }

}


/* ---------- Map metric buttons ---------- */

document
  .querySelectorAll(
    '#metricTabs button'
  )
  .forEach(btn => {

    btn.addEventListener(
      'click',
      () => {

        document
          .querySelectorAll(
            '#metricTabs button'
          )
          .forEach(b =>
            b.classList.remove(
              'active'
            )
          );


        btn.classList.add(
          'active'
        );


        currentMetric =
          btn.dataset.metric;


        renderMap();

      }
    );

  });


/* ---------- Scatter: HDI x Fertility ---------- */

function renderScatter() {

  const c =
    plotlyColors();


  const rows =
    RECORDS.filter(r =>

      r.hdi !== null &&
      r.fertility !== null &&
      r.population

    );


  const trace = [{

    type:
      'scatter',

    mode:
      'markers',

    x:
      rows.map(r =>
        r.hdi
      ),

    y:
      rows.map(r =>
        r.fertility
      ),

    text:
      rows.map(r =>
        r.country
      ),

    customdata:
      rows.map(r =>
        r.iso2
      ),

    hovertemplate:

      '%{text}<br>' +

      'IDH: %{x:.3f}<br>' +

      'Fecundidade: %{y:.2f}' +

      '<extra></extra>',

    marker: {

      size:
        rows.map(r =>
          Math.sqrt(
            r.population
          ) / 900 + 4
        ),

      color:
        c.brass,

      opacity:
        0.75,

      line: {

        width:
          0.5,

        color:
          c.bg

      }

    }

  }];


  const layout =
    baseLayout({

      xaxis: {

        title:
          'IDH',

        gridcolor:
          c.line,

        zeroline:
          false

      },

      yaxis: {

        title:
          'Fecundidade (filhos/mulher)',

        gridcolor:
          c.line,

        zeroline:
          false

      },

      height:
        380

    });


  Plotly.newPlot(

    'scatter',

    trace,

    layout,

    commonConfig

  );

}


/* ---------- HDI tier distribution ---------- */

function renderHdiDist() {

  const c =
    plotlyColors();


  const order = [

    'Baixo',
    'Medio',
    'Alto',
    'Muito Alto'

  ];


  const labels = [

    'Baixo',
    'Médio',
    'Alto',
    'Muito Alto'

  ];


  const counts =
    order.map(t =>

      RECORDS.filter(r =>
        r.hdi_tier === t
      ).length

    );


  const trace = [{

    type:
      'bar',

    x:
      labels,

    y:
      counts,

    marker: {

      color: [

        c.coral,
        c.teal,
        c.sage,
        c.brass

      ]

    },

    text:
      counts.map(String),

    textposition:
      'outside',

    hovertemplate:

      '%{x}: %{y} países' +

      '<extra></extra>'

  }];


  const layout =
    baseLayout({

      xaxis: {

        gridcolor:
          c.line

      },

      yaxis: {

        gridcolor:
          c.line,

        title:
          'Nº de países'

      },

      height:
        380

    });


  Plotly.newPlot(

    'hdiDist',

    trace,

    layout,

    commonConfig

  );

}


/* ---------- Territory x Population ---------- */

function renderScatterArea() {

  const c =
    plotlyColors();


  const rows =
    RECORDS.filter(r =>

      r.total_km2 &&
      r.population &&
      r.density

    );


  const trace = [{

    type:
      'scatter',

    mode:
      'markers',

    x:
      rows.map(r =>
        r.total_km2
      ),

    y:
      rows.map(r =>
        r.population
      ),

    text:
      rows.map(r =>
        r.country
      ),

    hovertemplate:

      '%{text}<br>' +

      'Território: %{x:,.0f} km²<br>' +

      'População: %{y:,.0f}' +

      '<extra></extra>',

    marker: {

      size:
        9,

      opacity:
        0.75,

      color:
        rows.map(r =>
          Math.log10(
            r.density + 1
          )
        ),

      colorscale: [

        [0, c.teal],
        [0.5, c.brass],
        [1, c.coral]

      ],

      showscale:
        false,

      line: {

        width:
          0.5,

        color:
          c.bg

      }

    }

  }];


  const layout =
    baseLayout({

      xaxis: {

        title:
          'Território (km², escala log)',

        type:
          'log',

        gridcolor:
          c.line

      },

      yaxis: {

        title:
          'População (escala log)',

        type:
          'log',

        gridcolor:
          c.line

      },

      height:
        360

    });


  Plotly.newPlot(

    'scatterArea',

    trace,

    layout,

    commonConfig

  );

}


/* ---------- Top density bar ---------- */

function renderTopBar(
  elId,
  key,
  n,
  colorKey,
  fmt
) {

  const c =
    plotlyColors();


  const rows =
    [...RECORDS]

      .filter(r =>

        r[key] !== null &&
        r[key] !== undefined

      )

      .sort((a, b) =>

        Number(b[key]) -
        Number(a[key])

      )

      .slice(0, n)

      .reverse();


  const trace = [{

    type:
      'bar',

    orientation:
      'h',

    y:
      rows.map(r =>
        r.country
      ),

    customdata:
      rows.map(r =>
        r.iso2
      ),

    x:
      rows.map(r =>
        r[key]
      ),

    marker: {

      color:
        c[colorKey] ||
        c.brass

    },

    text:
      rows.map(r =>
        fmt(r[key])
      ),

    textposition:
      'outside',

    hovertemplate:

      '%{y}: %{text}' +

      '<extra></extra>'

  }];


  const layout =
    baseLayout({

      xaxis: {

        gridcolor:
          c.line,

        showticklabels:
          false

      },

      yaxis: {

        automargin:
          true

      },

      height:
        360,

      margin: {

        t: 10,
        r: 60,
        b: 30,
        l: 130

      }

    });


  Plotly.newPlot(

    elId,

    trace,

    layout,

    commonConfig

  );

}


/* ---------- Table ---------- */

let sortKey =
  'population';

let sortDir =
  -1;


function renderTable(
  filterText
) {

  const tbody =
    document.getElementById(
      'tableBody'
    );


  let rows =
    RECORDS.filter(r =>

      !filterText ||

      (r.country || '')
        .toLowerCase()
        .includes(
          filterText.toLowerCase()
        )

    );


  rows =
    rows
      .slice()
      .sort((a, b) => {

        let av =
          a[sortKey];

        let bv =
          b[sortKey];


        if (
          typeof av ===
          'string'
        ) {

          av =
            av || '';

          bv =
            bv || '';


          return sortDir *
            av.localeCompare(
              bv
            );

        }


        av =
          av ?? -Infinity;

        bv =
          bv ?? -Infinity;


        return sortDir *
          (av - bv);

      });


  const tierColorVar = {

    'Muito Alto':
      'var(--brass)',

    'Alto':
      'var(--sage)',

    'Medio':
      'var(--teal)',

    'Baixo':
      'var(--coral)'

  };


  const tierLabel = {

    'Muito Alto':
      'Muito Alto',

    'Alto':
      'Alto',

    'Medio':
      'Médio',

    'Baixo':
      'Baixo'

  };


  tbody.innerHTML =

    rows.map(r => `

      <tr>

        <td>

          <div class="country-cell">

            ${
              flagImg(
                r.iso2,
                r.country
              )
            }

            <span>
              ${r.country}
            </span>

          </div>

        </td>


        <td class="num">

          ${
            r.total_km2 != null
              ? fmtInt(
                  r.total_km2
                )
              : '—'
          }

        </td>


        <td class="num">

          ${
            r.population != null
              ? fmtInt(
                  r.population
                )
              : '—'
          }

        </td>


        <td class="num">

          ${
            r.density != null
              ? Number(
                  r.density
                ).toLocaleString(
                  'pt-BR',
                  {
                    maximumFractionDigits:
                      1
                  }
                )
              : '—'
          }

        </td>


        <td class="num">

          ${
            r.hdi != null
              ? Number(
                  r.hdi
                )
                  .toFixed(3)
                  .replace(
                    '.',
                    ','
                  )
              : '—'
          }

        </td>


        <td class="num">

          ${
            r.fertility != null
              ? Number(
                  r.fertility
                )
                  .toFixed(2)
                  .replace(
                    '.',
                    ','
                  )
              : '—'
          }

        </td>


        <td class="num">

          ${
            r.pct_world_water != null
              ? fmtPct(
                  r.pct_world_water,
                  2
                )
              : '—'
          }

        </td>


        <td>

          ${
            r.hdi_tier

              ? `

                <span
                  class="tier-pill"
                  style="
                    color:
                      ${tierColorVar[
                        r.hdi_tier
                      ]};

                    border-color:
                      ${tierColorVar[
                        r.hdi_tier
                      ]}
                  "
                >
                  ${
                    tierLabel[
                      r.hdi_tier
                    ]
                  }
                </span>

              `

              : '—'
          }

        </td>

      </tr>

    `).join('');

}


/* ---------- Table sorting ---------- */

document
  .querySelectorAll(
    '#dataTable thead th'
  )
  .forEach(th => {

    th.addEventListener(
      'click',
      () => {

        const key =
          th.dataset.key;


        if (
          sortKey === key
        ) {

          sortDir *= -1;

        } else {

          sortKey =
            key;

          sortDir =
            -1;

        }


        document
          .querySelectorAll(
            '#dataTable thead th .arrow'
          )
          .forEach(a => {

            a.textContent =
              '';

          });


        const arrow =
          th.querySelector(
            '.arrow'
          );


        if (arrow) {

          arrow.textContent =
            sortDir === 1
              ? '↑'
              : '↓';

        }


        renderTable(
          document.getElementById(
            'searchBox'
          ).value
        );

      }

    );

  });


/* ---------- Table search ---------- */

document
  .getElementById(
    'searchBox'
  )
  .addEventListener(
    'input',
    e => {

      renderTable(
        e.target.value
      );

    }
  );


/* ---------- Render all ---------- */

function renderAll() {

  renderKPIs();

  renderRankGrid();

  renderMap();

  renderScatter();

  renderHdiDist();

  renderScatterArea();

  renderTopBar(
    'topDensity',
    'density',
    12,
    'teal',
    v =>
      fmtInt(v) +
      '/km²'
  );

  renderTable(
    document.getElementById(
      'searchBox'
    ).value || ''
  );

}


/* ---------- Carrega os dados da API Flask ---------- */

async function init() {

  try {

    const res =
      await fetch(
        '/api/data'
      );


    if (!res.ok) {

      throw new Error(

        'Erro ao carregar /api/data (' +
        res.status +
        ')'

      );

    }


    const data =
      await res.json();


    RECORDS =
      data.records;

    KPIS =
      data.kpis;

    RANKINGS =
      data.rankings;


    document.getElementById(
      'n-countries-tag'
    ).textContent =

      KPIS.n_countries +
      ' países';


    renderAll();


  } catch (error) {

    console.error(
      'Erro ao inicializar o dashboard:',
      error
    );


    document.body.innerHTML = `

      <div style="
        padding:40px;
        font-family:sans-serif;
        color:#C1554A;
      ">

        <h2>
          Erro ao carregar o dashboard
        </h2>

        <p>
          Não foi possível carregar os dados.
        </p>

        <pre style="
          white-space:pre-wrap;
          color:#888;
        ">${error.message}</pre>

      </div>

    `;

  }

}


init();


/* ---------- Responsive Plotly ---------- */

window.addEventListener(
  'resize',
  () => {

    const charts = [

      'map',
      'scatter',
      'hdiDist',
      'scatterArea',
      'topDensity'

    ];


    charts.forEach(id => {

      const element =
        document.getElementById(
          id
        );


      if (element) {

        Plotly.Plots.resize(
          element
        );

      }

    });

  }
);