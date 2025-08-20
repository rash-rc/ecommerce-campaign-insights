import pandas as pd

def campaign_windows(df: pd.DataFrame):
    df = df.copy()
    df['month'] = df['order_date'].dt.month
    monthly = df.groupby('month')['gross_sales'].sum().sort_values(ascending=False)
    top_months = monthly.head(4).index.tolist()
    acquisition = sorted([m for m in top_months if m in [11,12,1,3]]) or [11,12,1,3]
    retention = [2,3]
    return {'acquisition_months': acquisition, 'retention_months': retention}