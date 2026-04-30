# 📊 Dashboard DRE Executivo 2024

Dashboard interativo da **Demonstração do Resultado do Exercício (DRE)** desenvolvido para apresentações executivas (Diretoria e CEO). Construído com **Streamlit + Plotly** em tema dark-blue profissional.

🔗 **Acesse o dashboard:** [dre-insightsjobsia.streamlit.app](https://dre-insightsjobsia.streamlit.app)

---

## Visão Geral

O dashboard transforma 5.000 lançamentos contábeis em análises estratégicas e visuais executivos, permitindo navegação interativa por trimestre, região, filial e categoria de produto — tudo em tempo real.

## Funcionalidades

### Filtros Interativos
- **Trimestre** — Q1, Q2, Q3, Q4 ou visão anual consolidada
- **Região** — Centro-Oeste, Nordeste, Norte, Sudeste, Sul
- **Filial** — 9 unidades (Matriz São Paulo + 8 filiais)
- **Categoria de Produto** — SaaS, Serviços, Produtos

### KPIs Executivos
| Indicador | Descrição |
|---|---|
| Receita Bruta | Total faturado no período |
| Deduções | Impostos sobre venda e descontos |
| Receita Líquida | Receita após deduções |
| Lucro Bruto | Após CMV e CSP |
| EBIT | Resultado operacional |
| Lucro Líquido | Resultado final com margem % |

### Visualizações
- **Cascata DRE** — Waterfall completo do resultado (impacto visual para CEO)
- **Evolução Mensal** — Receita × Custos × Lucro Líquido (barras + linha)
- **Evolução de Margens** — Margem Bruta, EBIT e Líquida mês a mês
- **Resultado por Região** — Performance comparativa das 5 regiões
- **Receita por Categoria** — Participação de SaaS, Serviços e Produtos
- **Performance por Filial** — Ranking das 9 unidades
- **Top Contas de Despesa** — Maiores centros de custo operacional
- **DRE Estruturada** — Demonstração completa com formatação contábil

### Insights Estratégicos Automáticos
Painel de 6 insights gerados dinamicamente conforme os filtros, cobrindo:
- Saúde financeira e classificação de margens
- Carga tributária sobre vendas
- Eficiência operacional
- Destaque regional e de filial
- Resultado financeiro (juros e receitas)
- Recomendação executiva

---

## Estrutura do Projeto

```
dashboard-dre-2024/
├── DADOS/
│   └── dre_dataset.csv       # 5.000 lançamentos contábeis 2024
├── dashboard_dre.py          # Aplicação principal Streamlit
├── requirements.txt          # Dependências para deploy
├── pyproject.toml            # Configuração do projeto (uv)
└── uv.lock                   # Versões travadas das dependências
```

---

## Estrutura dos Dados

O arquivo `dre_dataset.csv` contém os seguintes campos:

| Campo | Descrição |
|---|---|
| `id_lancamento` | Identificador único do lançamento |
| `data` | Data do lançamento |
| `ano` / `mes` / `trimestre` | Dimensões temporais |
| `grupo_dre` | Grupo da DRE (Receita Bruta, CMV, CSP, etc.) |
| `conta_contabil` | Conta contábil detalhada |
| `natureza` | Receita ou Despesa |
| `valor` | Valor em R$ |
| `filial_id` / `filial_nome` | Unidade de negócio |
| `regiao` | Região geográfica |
| `centro_custo` | Centro de custo |
| `produto_nome` / `categoria_produto` | Produto e categoria |

### Grupos da DRE
```
Receita Bruta
└── Deduções (ISS, PIS/COFINS, Descontos)
    = Receita Líquida
    └── CMV — Custo de Mercadorias Vendidas
    └── CSP — Custo de Serviços Prestados
        = Lucro Bruto
        └── Despesas Comerciais
        └── Despesas Administrativas
            = EBIT (Resultado Operacional)
            └── Receitas Financeiras
            └── Despesas Financeiras
            └── Outras Receitas / Despesas
                = LAIR (Antes do IR/CSLL)
                └── Impostos sobre Lucro (IRPJ + CSLL)
                    = Lucro Líquido
```

---

## Como Rodar Localmente

### Pré-requisitos
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) instalado

### Instalação e execução

```bash
# Clone o repositório
git clone git@github.com:Breno-Teodomiro/dashboard-dre-2024.git
cd dashboard-dre-2024

# Instala as dependências
uv sync

# Roda o dashboard
uv run streamlit run dashboard_dre.py
```

Acesse em: **http://localhost:8501**

### Sem uv (pip tradicional)

```bash
pip install -r requirements.txt
streamlit run dashboard_dre.py
```

---

## Stack Tecnológica

| Tecnologia | Versão | Uso |
|---|---|---|
| [Streamlit](https://streamlit.io) | 1.57 | Framework do dashboard |
| [Plotly](https://plotly.com/python/) | 6.7 | Gráficos interativos |
| [Pandas](https://pandas.pydata.org) | 3.0 | Manipulação dos dados |
| [NumPy](https://numpy.org) | 2.4 | Cálculos numéricos |
| [uv](https://docs.astral.sh/uv/) | — | Gerenciamento de dependências |

---

## Deploy

O dashboard está publicado no **Streamlit Community Cloud** com deploy automático a cada push na branch `master`.

Para atualizar o dashboard em produção:

```bash
git add .
git commit -m "descrição da mudança"
git push origin master
```

O Streamlit detecta o push e atualiza automaticamente em ~1 minuto.

---

## Autor

**Breno Teodomiro**
- GitHub: [@Breno-Teodomiro](https://github.com/Breno-Teodomiro)
- LinkedIn: [breno-teodomiro-power-bi](https://www.linkedin.com/in/breno-teodomiro-power-bi/)
- Email: insights.jobs.ia@gmail.com
