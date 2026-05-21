import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(
    page_title="Rebel Foods - Kitchen PNL",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    :root {
        --rebel-yellow: #F5C518;
        --rebel-dark:   #1A1A2E;
        --rebel-mid:    #16213E;
        --rebel-accent: #E94560;
        --rebel-green:  #00B074;
        --rebel-gray:   #F0F2F6;
    }
    .stApp { background: var(--rebel-gray); }
    .hero {
        background: linear-gradient(135deg, var(--rebel-dark) 0%, var(--rebel-mid) 100%);
        padding: 1.4rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .hero h1 { color: var(--rebel-yellow); margin: 0; font-size: 1.8rem; }
    .hero p  { color: #ccc; margin: 0; font-size: 0.9rem; }
    .kpi-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
    .kpi-card {
        flex: 1; min-width: 160px;
        background: white;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,.08);
        border-left: 4px solid var(--rebel-yellow);
    }
    .kpi-card.red   { border-left-color: var(--rebel-accent); }
    .kpi-card.green { border-left-color: var(--rebel-green); }
    .kpi-label { font-size: 0.72rem; color: #888; text-transform: uppercase; letter-spacing: .05em; }
    .kpi-value { font-size: 1.55rem; font-weight: 700; color: var(--rebel-dark); }
    .kpi-sub   { font-size: 0.78rem; color: #aaa; }
    .section-hdr {
        background: var(--rebel-dark);
        color: var(--rebel-yellow);
        padding: .55rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1rem;
        margin: 1rem 0 .6rem;
        letter-spacing: .03em;
    }
    section[data-testid="stSidebar"] { background: var(--rebel-dark) !important; }
    section[data-testid="stSidebar"] * { color: #eee !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label { color: var(--rebel-yellow) !important; }
    .stTabs [data-baseweb="tab"] { background: var(--rebel-dark); color: #eee; border-radius: 8px 8px 0 0; }
    .stTabs [aria-selected="true"] { background: var(--rebel-yellow) !important; color: var(--rebel-dark) !important; font-weight: 700; }
    .dataframe th { background: var(--rebel-dark) !important; color: var(--rebel-yellow) !important; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner="Loading data...")
def load_data(path):
    df = pd.read_excel(path, sheet_name="Sheet 1 - stores", header=1)

    df["GM%"]       = (df["GROSS MARGIN"] / df["NET REVENUE"] * 100).round(2)
    df["CM"]        = df["GROSS MARGIN"]
    df["CM%"]       = df["GM%"]
    df["EBITDA"]    = df["KITCHEN EBITDA"]
    df["EBITDA%"]   = (df["EBITDA"] / df["NET REVENUE"] * 100).round(2)
    df["VARIANCE%"] = (df["VARIANCE"] / df["NET REVENUE"] * 100).round(4)

    rev_bins   = [0, 1_500_000, 2_500_000, 3_500_000, 4_500_000, float("inf")]
    rev_labels = [
        "(a) Below INR 15 lacs",
        "(b) INR 15 to 25 lacs",
        "(c) INR 25 to 35 lacs",
        "(d) INR 35 to 45 lacs",
        "(e) Above INR 45 lacs",
    ]
    df["REV_BUCKET"] = pd.cut(df["NET REVENUE"], bins=rev_bins, labels=rev_labels)

    var_bins   = [0, 0.5, 0.75, 1.0, float("inf")]
    var_labels = ["(a) Var < 0.5%", "(b) Var 0.5% to 0.75%", "(c) Var 0.75% to 1%", "(d) Var > 1%"]
    df["VAR_BUCKET"] = pd.cut(df["VARIANCE%"], bins=var_bins, labels=var_labels)

    month_order = ["Oct-2023", "Nov-2023", "Dec-2023", "Jan-2024", "Feb-2024", "Mar-2024"]
    df["MONTH"] = pd.Categorical(df["MONTH"], categories=month_order, ordered=True)

    return df


st.sidebar.markdown("## Data Source")
uploaded = st.sidebar.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded:
    raw = BytesIO(uploaded.read())
    df_raw = load_data(raw)
else:
    try:
        df_raw = load_data("Kittchen_PNL_Data.xlsx")
    except FileNotFoundError:
        st.error("Please upload the Excel file using the sidebar.")
        st.stop()

st.markdown("""
<div class="hero">
  <div>
    <h1>Rebel Foods - Cloud Kitchen PNL</h1>
    <p>Kitchen-level Profit and Loss | Variance Analysis | 344 stores | 5 cities | 6 months</p>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Dashboard 1 - Kitchen Level PNL", "Dashboard 2 - Variance Level PNL"])


with tab1:

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Kitchen PNL Filters")

    all_months = list(df_raw["MONTH"].cat.categories)
    all_stores = sorted(df_raw["STORE"].unique())
    all_zones  = sorted(df_raw["ZONE MAPPING"].unique())
    all_cities = sorted(df_raw["CITY"].unique())
    all_rc     = sorted(df_raw["REVENUE COHORT"].unique())
    all_cm     = sorted(df_raw["CM COHORT"].unique())
    all_ecat   = sorted(df_raw["EBITDA CATEGORY"].unique())
    all_ecoh   = sorted(df_raw["EBITDA COHORT"].unique())

    sel_months = st.sidebar.multiselect("Month",           all_months, default=all_months)
    sel_zones  = st.sidebar.multiselect("Zone",            all_zones,  default=all_zones)
    sel_cities = st.sidebar.multiselect("City",            all_cities, default=all_cities)
    sel_stores = st.sidebar.multiselect("Store",           all_stores, default=all_stores)
    sel_rc     = st.sidebar.multiselect("Revenue Cohort",  all_rc,     default=all_rc)
    sel_cm     = st.sidebar.multiselect("CM Cohort",       all_cm,     default=all_cm)
    sel_ecat   = st.sidebar.multiselect("EBITDA Category", all_ecat,   default=all_ecat)
    sel_ecoh   = st.sidebar.multiselect("EBITDA Cohort",   all_ecoh,   default=all_ecoh)

    ebitda_min = float(df_raw["EBITDA"].min())
    ebitda_max = float(df_raw["EBITDA"].max())
    ebitda_rng = st.sidebar.slider(
        "EBITDA Range (Rs.)",
        ebitda_min, ebitda_max, (ebitda_min, ebitda_max),
        step=1000.0
    )

    cm_min = float(df_raw["CM"].min())
    cm_max = float(df_raw["CM"].max())
    cm_rng = st.sidebar.slider(
        "CM Range (Rs.)",
        cm_min, cm_max, (cm_min, cm_max),
        step=1000.0
    )

    rev_min = float(df_raw["NET REVENUE"].min())
    rev_max = float(df_raw["NET REVENUE"].max())
    rev_rng = st.sidebar.slider(
        "Net Revenue Range (Rs.)",
        rev_min, rev_max, (rev_min, rev_max),
        step=10000.0
    )

    @st.cache_data(ttl=300)
    def filter_d1(df, months, zones, cities, stores, rc, cm_coh, ecat, ecoh, ebitda_rng, cm_rng, rev_rng):
        mask = (
            df["MONTH"].isin(months) &
            df["ZONE MAPPING"].isin(zones) &
            df["CITY"].isin(cities) &
            df["STORE"].isin(stores) &
            df["REVENUE COHORT"].isin(rc) &
            df["CM COHORT"].isin(cm_coh) &
            df["EBITDA CATEGORY"].isin(ecat) &
            df["EBITDA COHORT"].isin(ecoh) &
            df["EBITDA"].between(*ebitda_rng) &
            df["CM"].between(*cm_rng) &
            df["NET REVENUE"].between(*rev_rng)
        )
        return df[mask]

    df1 = filter_d1(
        df_raw, tuple(sel_months), tuple(sel_zones), tuple(sel_cities),
        tuple(sel_stores), tuple(sel_rc), tuple(sel_cm),
        tuple(sel_ecat), tuple(sel_ecoh),
        ebitda_rng, cm_rng, rev_rng
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    total_rev    = df1["NET REVENUE"].sum()
    total_ebitda = df1["EBITDA"].sum()
    avg_gm       = df1["GM%"].mean()
    avg_ebitda   = df1["EBITDA%"].mean()
    n_stores     = df1["STORE"].nunique()

    def fmt_cr(v):
        return f"Rs. {v/1e7:.2f} Cr"

    k1.metric("Net Revenue",   fmt_cr(total_rev))
    k2.metric("Total EBITDA",  fmt_cr(total_ebitda))
    k3.metric("Avg GM%",       f"{avg_gm:.1f}%")
    k4.metric("Avg EBITDA%",   f"{avg_ebitda:.1f}%")
    k5.metric("Active Stores", n_stores)

    st.markdown('<div class="section-hdr">KITCHEN SNAPSHOT - Monthly PNL Table</div>', unsafe_allow_html=True)

    pivot_cols = ["STORE", "CITY", "ZONE MAPPING", "MONTH",
                  "NET REVENUE", "GM%", "CM%", "EBITDA", "EBITDA%", "REVENUE COHORT", "EBITDA CATEGORY"]
    pivot_df = df1[pivot_cols].sort_values(["STORE", "MONTH"]).reset_index(drop=True)

    pivot_df["NET REVENUE"] = pivot_df["NET REVENUE"].map(lambda x: f"Rs. {x:,.0f}")
    pivot_df["EBITDA"]      = pivot_df["EBITDA"].map(lambda x: f"Rs. {x:,.0f}")
    pivot_df["GM%"]         = pivot_df["GM%"].map(lambda x: f"{x:.1f}%")
    pivot_df["CM%"]         = pivot_df["CM%"].map(lambda x: f"{x:.1f}%")
    pivot_df["EBITDA%"]     = pivot_df["EBITDA%"].map(lambda x: f"{x:.1f}%")

    st.dataframe(pivot_df, use_container_width=True, height=380)

    st.markdown('<div class="section-hdr">Revenue and EBITDA Trends</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        trend = df1.groupby("MONTH", observed=True)["NET REVENUE"].sum().reset_index()
        fig = px.bar(
            trend, x="MONTH", y="NET REVENUE",
            title="Net Revenue by Month",
            color_discrete_sequence=["#F5C518"],
            labels={"NET REVENUE": "Net Revenue (Rs.)"}
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color="#1A1A2E", title_font_size=14)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        city_rev = df1.groupby("CITY")["NET REVENUE"].sum().reset_index().sort_values("NET REVENUE", ascending=False)
        fig2 = px.pie(
            city_rev, values="NET REVENUE", names="CITY",
            title="Revenue Share by City",
            color_discrete_sequence=px.colors.qualitative.Bold,
            hole=0.45
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color="#1A1A2E", title_font_size=14)
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        ebitda_trend = df1.groupby("MONTH", observed=True)["EBITDA%"].mean().reset_index()
        fig3 = px.line(
            ebitda_trend, x="MONTH", y="EBITDA%",
            title="Avg EBITDA% Trend",
            markers=True,
            color_discrete_sequence=["#E94560"],
            labels={"EBITDA%": "Avg EBITDA%"}
        )
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color="#1A1A2E", title_font_size=14)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        cat_cnt = df1["EBITDA CATEGORY"].value_counts().reset_index()
        cat_cnt.columns = ["Category", "Count"]
        fig4 = px.bar(
            cat_cnt, x="Category", y="Count",
            color="Category",
            title="EBITDA Positive vs Negative Store Count",
            color_discrete_map={"EBITDA +ve": "#00B074", "EBITDA -ve": "#E94560"}
        )
        fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color="#1A1A2E",
                           title_font_size=14, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-hdr">Store-Level Revenue vs EBITDA%</div>', unsafe_allow_html=True)

    scatter_df = (
        df1.groupby("STORE", observed=True)
        .agg(
            NET_REVENUE=("NET REVENUE", "sum"),
            EBITDA_PCT=("EBITDA%", "mean"),
            CITY=("CITY", "first"),
            ZONE=("ZONE MAPPING", "first")
        )
        .reset_index()
    )
    fig5 = px.scatter(
        scatter_df, x="NET_REVENUE", y="EBITDA_PCT",
        color="CITY", hover_name="STORE",
        size="NET_REVENUE", size_max=18,
        title="Store Revenue vs Avg EBITDA%",
        labels={"NET_REVENUE": "Total Net Revenue (Rs.)", "EBITDA_PCT": "Avg EBITDA%"},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig5.add_hline(y=0, line_dash="dash", line_color="#E94560", annotation_text="Break-even")
    fig5.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color="#1A1A2E", height=420)
    st.plotly_chart(fig5, use_container_width=True)


with tab2:

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Variance Filters")

    all_var_buckets = ["(a) Var < 0.5%", "(b) Var 0.5% to 0.75%", "(c) Var 0.75% to 1%", "(d) Var > 1%"]
    sel_var = st.sidebar.multiselect(
        "Variance Category",
        all_var_buckets,
        default=all_var_buckets,
        key="var_filter"
    )

    df2 = df_raw[df_raw["VAR_BUCKET"].isin(sel_var)].copy()
    month_order = list(df_raw["MONTH"].cat.categories)

    vk1, vk2, vk3 = st.columns(3)
    vk1.metric("Stores in Selection", df2["STORE"].nunique())
    vk2.metric("Avg Variance%", f"{df2['VARIANCE%'].mean():.2f}%")
    vk3.metric("Total Variance (Rs.)", f"Rs. {df2['VARIANCE'].sum():,.0f}")

    st.markdown('<div class="section-hdr">Sub-Dashboard A - Avg Variance % by Revenue Category and Month</div>',
                unsafe_allow_html=True)
    st.caption("Average variance % of kitchens grouped by revenue category for each month.")

    pivot_a = (
        df2.groupby(["REV_BUCKET", "MONTH"], observed=True)["VARIANCE%"]
        .mean()
        .round(2)
        .reset_index()
        .pivot(index="REV_BUCKET", columns="MONTH", values="VARIANCE%")
        .reindex(columns=[m for m in month_order if m in df2["MONTH"].cat.categories])
    )
    pivot_a.loc["Grand total"] = pivot_a.mean()
    pivot_a = pivot_a.applymap(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
    pivot_a.index.name = "Revenue Category"
    pivot_a.columns.name = ""

    st.dataframe(
        pivot_a.style
            .set_properties(**{"text-align": "center"})
            .set_table_styles([
                {"selector": "th", "props": [("background-color", "#1A1A2E"), ("color", "#F5C518"), ("font-weight", "bold")]},
                {"selector": "tr:last-child", "props": [("font-weight", "bold"), ("background-color", "#FFF9E5")]},
            ]),
        use_container_width=True
    )

    pivot_a_num = (
        df2.groupby(["REV_BUCKET", "MONTH"], observed=True)["VARIANCE%"]
        .mean()
        .round(2)
        .reset_index()
        .pivot(index="REV_BUCKET", columns="MONTH", values="VARIANCE%")
        .reindex(columns=[m for m in month_order if m in df2["MONTH"].cat.categories])
    )
    pivot_a_num = pivot_a_num.reindex([r for r in [
        "(a) Below INR 15 lacs", "(b) INR 15 to 25 lacs",
        "(c) INR 25 to 35 lacs", "(d) INR 35 to 45 lacs",
        "(e) Above INR 45 lacs"
    ] if r in pivot_a_num.index])

    fig_heat = go.Figure(go.Heatmap(
        z=pivot_a_num.values,
        x=list(pivot_a_num.columns),
        y=list(pivot_a_num.index),
        colorscale="YlOrRd",
        text=[[f"{v:.2f}%" for v in row] for row in pivot_a_num.values],
        texttemplate="%{text}",
        colorbar_title="Var %"
    ))
    fig_heat.update_layout(
        title="Avg Variance% Heatmap - Revenue Category by Month",
        plot_bgcolor="white", paper_bgcolor="white",
        font_color="#1A1A2E", height=320,
        xaxis_title="Month", yaxis_title="Revenue Category"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown('<div class="section-hdr">Sub-Dashboard B - Store Count by Revenue Bucket and Month</div>',
                unsafe_allow_html=True)
    st.caption("Count of distinct kitchen stores in each revenue range per month.")

    pivot_b = (
        df2.groupby(["REV_BUCKET", "MONTH"], observed=True)["STORE"]
        .nunique()
        .reset_index()
        .pivot(index="REV_BUCKET", columns="MONTH", values="STORE")
        .reindex(columns=[m for m in month_order if m in df2["MONTH"].cat.categories])
    )
    pivot_b.loc["Grand total"] = pivot_b.sum()
    pivot_b = pivot_b.fillna(0).astype(int)
    pivot_b.index.name = "Revenue Category"
    pivot_b.columns.name = ""

    st.dataframe(
        pivot_b.style
            .set_properties(**{"text-align": "center"})
            .set_table_styles([
                {"selector": "th", "props": [("background-color", "#1A1A2E"), ("color", "#F5C518"), ("font-weight", "bold")]},
                {"selector": "tr:last-child", "props": [("font-weight", "bold"), ("background-color", "#FFF9E5")]},
            ])
            .background_gradient(cmap="YlGn", subset=pd.IndexSlice[pivot_b.index[:-1], :]),
        use_container_width=True
    )

    c_b1, c_b2 = st.columns(2)

    with c_b1:
        rev_cnt = df2.groupby("REV_BUCKET", observed=True)["STORE"].nunique().reset_index()
        rev_cnt.columns = ["Revenue Bucket", "Store Count"]
        fig_bar = px.bar(
            rev_cnt, x="Revenue Bucket", y="Store Count",
            title="Store Count by Revenue Bucket",
            color="Revenue Bucket",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_bar.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                              font_color="#1A1A2E", showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_b2:
        var_trend = df2.groupby("MONTH", observed=True)["VARIANCE%"].mean().reset_index()
        fig_vt = px.area(
            var_trend, x="MONTH", y="VARIANCE%",
            title="Avg Variance% Trend",
            color_discrete_sequence=["#E94560"],
            labels={"VARIANCE%": "Avg Variance%"}
        )
        fig_vt.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color="#1A1A2E")
        st.plotly_chart(fig_vt, use_container_width=True)

    st.markdown('<div class="section-hdr">Variance% Distribution by Zone</div>', unsafe_allow_html=True)

    fig_box = px.box(
        df2, x="ZONE MAPPING", y="VARIANCE%",
        color="ZONE MAPPING",
        title="Variance% Distribution by Zone",
        points="outliers",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_box.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          font_color="#1A1A2E", showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)


st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#aaa; font-size:.8rem;'>"
    "Rebel Foods - Cloud Kitchen Analytics | "
    "Python 3.10 | Streamlit 1.35 | Plotly 5.22 | Pandas 2.2"
    "</p>",
    unsafe_allow_html=True
)