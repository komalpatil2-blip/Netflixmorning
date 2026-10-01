from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Netflix Insights", page_icon="N", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
	--ink: #202124;
	--muted: #70747b;
	--paper: #f5f5f2;
	--surface: #ffffff;
	--line: #e5e5e0;
	--red: #d91e32;
	--gold: #e7a33e;
	--teal: #238b83;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: var(--paper); color: var(--ink); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #22272b; }
[data-testid="stSidebar"] * { color: #f3f3ef; }
[data-testid="stSidebar"] [data-baseweb="select"] div { color: #202124; }
[data-testid="stSidebar"] [data-testid="stDateInput"] input { color: #202124; }
main .block-container { max-width: 1500px; padding: 2rem 3rem 4rem; }
.hero {
	position: relative;
	overflow: hidden;
	background: #22272b;
	color: #fff;
	padding: 2.2rem 2.5rem;
	border-radius: 8px;
	margin-bottom: 1.5rem;
	border-left: 6px solid var(--red);
}
.hero:after {
	content: 'N'; position: absolute; right: 2.5rem; top: -3.6rem;
	font: 800 14rem 'Manrope', sans-serif; color: rgba(255,255,255,.045);
}
.eyebrow { color: #ef747d; text-transform: uppercase; font-size: .72rem; font-weight: 700; letter-spacing: 2px; }
.hero h1 { font: 800 2.25rem 'Manrope', sans-serif; margin: .35rem 0 .25rem; color: #fff; }
.hero p { color: #c5c9cb; margin: 0; font-size: .98rem; }
h2, h3 { font-family: 'Manrope', sans-serif !important; color: var(--ink); }
h2 { font-size: 1.25rem !important; }
[data-testid="stMetric"] {
	background: var(--surface); padding: 1rem 1.15rem; border: 1px solid var(--line);
	border-radius: 6px; border-top: 3px solid var(--red);
}
[data-testid="stMetricLabel"] { color: var(--muted); font-size: .8rem; }
[data-testid="stMetricValue"] { color: var(--ink); font: 700 1.7rem 'Manrope', sans-serif; }
[data-testid="stMetricDelta"] { font-size: .75rem; }
[data-testid="stTabs"] button { font-weight: 600; }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 6px; }
div[data-testid="stTextInput"] input { background: white; }
.section-note { color: var(--muted); font-size: .84rem; margin-top: -.65rem; margin-bottom: 1rem; }
@media (max-width: 800px) {
	main .block-container { padding: 1rem 1rem 3rem; }
	.hero { padding: 1.5rem; }
	.hero h1 { font-size: 1.8rem; }
	.hero:after { right: .5rem; }
}
</style>
""", unsafe_allow_html=True)

DATA_PATH = Path(__file__).with_name("Netflix_100_Customers_Dataset (1).csv")
if not DATA_PATH.exists():
	DATA_PATH = Path(__file__).with_name("netflix.csv")

st.markdown("""
<div class="hero">
	<div class="eyebrow">Audience intelligence | 2026</div>
	<h1>Netflix Insights</h1>
	<p>A clear view of viewing habits, customer reach, and subscription revenue.</p>
</div>
""", unsafe_allow_html=True)

if not DATA_PATH.exists():
	st.error("Dataset not found. Place the Netflix CSV beside this app.")
	st.stop()

netflix = pd.read_csv(DATA_PATH)
required_columns = {
	"Customer_ID",
	"Region",
	"Subscription_Plan",
	"Category",
	"Rating",
	"Watch_Date",
	"Watch_Time_Minutes",
	"Monthly_Revenue",
}
missing_columns = required_columns.difference(netflix.columns)
if missing_columns:
	st.error(f"Dataset is missing required columns: {', '.join(sorted(missing_columns))}")
	st.stop()

netflix["Watch_Date"] = pd.to_datetime(netflix["Watch_Date"], errors="coerce")
for column in ("Rating", "Watch_Time_Minutes", "Monthly_Revenue"):
	netflix[column] = pd.to_numeric(netflix[column], errors="coerce")
netflix = netflix.dropna(subset=["Watch_Date"])

with st.sidebar:
	st.header("Filters")
	selected_regions = st.multiselect(
		"Region", sorted(netflix["Region"].dropna().unique()),
		default=sorted(netflix["Region"].dropna().unique()),
	)
	selected_plans = st.multiselect(
		"Subscription plan", sorted(netflix["Subscription_Plan"].dropna().unique()),
		default=sorted(netflix["Subscription_Plan"].dropna().unique()),
	)
	selected_categories = st.multiselect(
		"Category", sorted(netflix["Category"].dropna().unique()),
		default=sorted(netflix["Category"].dropna().unique()),
	)
	date_range = st.date_input(
		"Watch date range",
		value=(netflix["Watch_Date"].min().date(), netflix["Watch_Date"].max().date()),
		min_value=netflix["Watch_Date"].min().date(),
		max_value=netflix["Watch_Date"].max().date(),
	)

filtered = netflix[
	netflix["Region"].isin(selected_regions)
	& netflix["Subscription_Plan"].isin(selected_plans)
	& netflix["Category"].isin(selected_categories)
]
if isinstance(date_range, tuple) and len(date_range) == 2:
	start_date, end_date = date_range
	filtered = filtered[
		filtered["Watch_Date"].dt.date.between(start_date, end_date)
	]

st.caption(f"Showing {len(filtered):,} of {len(netflix):,} viewing records")

if filtered.empty:
	st.info("No records match these filters. Adjust the selections in the sidebar.")
	st.stop()

total_revenue = filtered["Monthly_Revenue"].sum()
customer_count = filtered["Customer_ID"].nunique()
average_rating = filtered["Rating"].mean()
total_watch_hours = filtered["Watch_Time_Minutes"].sum() / 60

metric_columns = st.columns(4)
metric_columns[0].metric("Monthly revenue", f"${total_revenue:,.0f}")
metric_columns[1].metric("Customers", f"{customer_count:,}")
metric_columns[2].metric(
	"Average rating", f"{average_rating:.1f}" if pd.notna(average_rating) else "N/A"
)
metric_columns[3].metric("Watch time", f"{total_watch_hours:,.0f} hrs")

overview_tab, records_tab = st.tabs(["Overview", "Viewing records"])
with overview_tab:
	left_chart, right_chart = st.columns([1, 1])
	with left_chart:
		st.subheader("Revenue by region")
		revenue_by_region = filtered.groupby("Region")["Monthly_Revenue"].sum().sort_values()
		st.bar_chart(revenue_by_region, color="#d91e32", horizontal=True)

	with right_chart:
		st.subheader("Viewing by category")
		category_views = filtered.groupby("Category").size().sort_values(ascending=False)
		st.bar_chart(category_views, color="#e7a33e")

	left_detail, right_detail = st.columns([1, 1])
	with left_detail:
		st.subheader("Customers by subscription plan")
		plan_mix = (
			filtered.groupby("Subscription_Plan")["Customer_ID"].nunique()
			.rename("Customers")
			.reset_index()
		)
		st.vega_lite_chart(
			plan_mix,
			{
				"mark": {"type": "arc", "outerRadius": 110},
				"encoding": {
					"theta": {"field": "Customers", "type": "quantitative"},
					"color": {
						"field": "Subscription_Plan",
						"type": "nominal",
						"scale": {"range": ["#d91e32", "#e7a33e", "#238b83"]},
						"legend": {"title": None},
					},
					"tooltip": [
						{"field": "Subscription_Plan", "type": "nominal", "title": "Plan"},
						{"field": "Customers", "type": "quantitative"},
					],
				},
			},
			use_container_width=True,
		)

	with right_detail:
		st.subheader("Rating distribution")
		rating_distribution = (
			filtered["Rating"].dropna().round().value_counts().sort_index()
			.rename_axis("Rating")
			.rename("Records")
		)
		st.bar_chart(rating_distribution, color="#238b83")

	st.subheader("Viewing activity")
	daily_views = filtered.set_index("Watch_Date").resample("D").size().rename("Views")
	st.area_chart(daily_views, color="#238b83")

	st.subheader("Summary tables")
	plan_summary, title_summary = st.columns([1, 1])
	with plan_summary:
		st.markdown("**Plan performance**")
		plan_table = (
			filtered.groupby("Subscription_Plan")
			.agg(
				Customers=("Customer_ID", "nunique"),
				Views=("Customer_ID", "size"),
				Monthly_Revenue=("Monthly_Revenue", "sum"),
				Average_Rating=("Rating", "mean"),
			)
			.reset_index()
			.rename(
				columns={
					"Subscription_Plan": "Plan",
					"Monthly_Revenue": "Monthly revenue",
					"Average_Rating": "Average rating",
				}
			)
			.sort_values("Monthly revenue", ascending=False)
		)
		st.dataframe(
			plan_table.style.format(
				{"Monthly revenue": "${:,.0f}", "Average rating": "{:.1f}"}
			),
			use_container_width=True,
			hide_index=True,
		)

	with title_summary:
		st.markdown("**Top titles by watch time**")
		title_table = (
			filtered.dropna(subset=["Title"])
			.groupby("Title")
			.agg(
				Views=("Title", "size"),
				Watch_Minutes=("Watch_Time_Minutes", "sum"),
				Average_Rating=("Rating", "mean"),
			)
			.reset_index()
			.rename(
				columns={
					"Watch_Minutes": "Watch minutes",
					"Average_Rating": "Average rating",
				}
			)
			.sort_values("Watch minutes", ascending=False)
			.head(10)
		)
		st.dataframe(
			title_table.style.format(
				{"Watch minutes": "{:,.0f}", "Average rating": "{:.1f}"}
			),
			use_container_width=True,
			hide_index=True,
		)

with records_tab:
	st.subheader("Viewing records")
	st.markdown('<p class="section-note">Search across titles, customers, and the visible record fields.</p>', unsafe_allow_html=True)
	search = st.text_input("Search records", placeholder="Try a title, customer, region, or category")
	table = filtered.copy()
	if search:
		searchable = table.astype(str).apply(lambda column: column.str.contains(search, case=False, na=False))
		table = table[searchable.any(axis=1)]
	st.dataframe(
		table.sort_values("Watch_Date", ascending=False),
		use_container_width=True,
		hide_index=True,
	)





# In[ ]:





# In[ ]:




