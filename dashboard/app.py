import pandas as pd
import streamlit as st

st.set_page_config(page_title="PromoPilot: E-commerce Campaign Insights", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('data/synthetic_orders_2023-11_to_2024-10.csv', parse_dates=['order_date'])

df = load_data()

st.title("🚀 PromoPilot: E-commerce Campaign Insights")
st.markdown("Data-driven playbook: **When** to acquire/retain, **who** to target, **what** to promote, **where** to spend.")

col1, col2, col3 = st.columns(3)
with col1:
    country = st.multiselect("Country", options=sorted(df['country'].unique()), default=sorted(df['country'].unique()))
with col2:
    age = st.multiselect("Age Group", options=df['age_group'].unique(), default=df['age_group'].unique())
with col3:
    cat = st.multiselect("Category", options=df['category'].unique(), default=df['category'].unique())

f = df[df['country'].isin(country) & df['age_group'].isin(age) & df['category'].isin(cat)]

st.subheader("Campaign KPIs")
recent_cutoff = f['order_date'].max() - pd.Timedelta(days=90) if len(f) else None
recent = f[f['order_date'] >= recent_cutoff] if recent_cutoff is not None else f.iloc[:0]

new_share = (f['customer_type'].eq('New').mean()) if len(f) else 0.0
repeat_share = 1 - new_share if len(f) else 0.0
female_share = (f.loc[f['gender'].eq('Female'), 'net_sales'].sum() / f['net_sales'].sum()) if len(f) and f['net_sales'].sum() > 0 else 0.0
return_rate_90 = (recent['returned'].mean()) if len(recent) else 0.0
top3 = f.groupby('category')['net_sales'].sum().sort_values(ascending=False).head(3)

k1, k2, k3, k4 = st.columns(4)
k1.metric("New vs Repeat", f"{new_share:.0%} / {repeat_share:.0%}")
k2.metric("Female Net Sales Share", f"{female_share:.0%}")
k3.metric("Return Rate (Last 90d)", f"{return_rate_90:.1%}")
k4.metric("Top Categories", ", ".join(top3.index.tolist()))

with st.expander("📅 Acquisition & Retention Planner", expanded=True):
    st.markdown("""
- **Acquisition:** **Nov/Dec → Mar** (holiday lift + **Mar** peak).
- **Retention:** **Feb → Mar** (reorder window after holidays).
- **Summer:** Run promotional pushes to counter seasonal dip.
""")

st.subheader("Monthly Gross Sales")
monthly = f.groupby(pd.Grouper(key='order_date', freq='M'))['gross_sales'].sum()
st.line_chart(monthly)

st.subheader("Net Sales by Category")
cat_sales = f.groupby('category')['net_sales'].sum().sort_values(ascending=False)
st.bar_chart(cat_sales)

st.subheader("Top Regions by Net Sales")
reg = f.groupby(['country','region'])['net_sales'].sum().sort_values(ascending=False).head(10)
st.bar_chart(reg)

st.subheader("Bottom Categories – Recommended Actions")
bottom = f.groupby('category')['net_sales'].sum().sort_values(ascending=True).head(5).reset_index()
bottom['action'] = bottom['net_sales'].apply(lambda x: "Review pricing / consider promo" if x > 0 else "Consider discontinue or re-price")
st.dataframe(bottom, use_container_width=True)