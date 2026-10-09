import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def create_visualizations():
    print("Loading training data...")
    df = pd.read_csv('train_data.csv')

    # To make an interesting animation, we'll use 'business_age_months' as the time frame.
    # Grouping it into years so the animation frames aren't too numerous.
    df['business_age_years'] = np.ceil(df['business_age_months'] / 12).astype(int)
    
    # Sort by age so the animation goes sequentially
    df = df.sort_values('business_age_years')

    print("Creating Animated Scatter Plot...")
    # 1. Animated Scatter Plot
    # Shows the evolution of borrower profiles over their business age
    fig1 = px.scatter(
        df,
        x="upi_transaction_velocity",
        y="seasonal_inventory_turnover",
        animation_frame="business_age_years",
        animation_group=df.index,
        color="default_risk",
        size="utility_bill_consistency",
        hover_name="business_age_months",
        range_x=[0, 550],
        range_y=[0, 13],
        color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
        title="Animated Analysis: Transaction Velocity vs Inventory Turnover over Business Age (Years)",
        labels={
            "upi_transaction_velocity": "UPI Transaction Velocity",
            "seasonal_inventory_turnover": "Seasonal Inventory Turnover",
            "default_risk": "Default Risk (1=Yes)",
            "business_age_years": "Business Age (Years)",
            "utility_bill_consistency": "Utility Bill Consistency"
        }
    )
    # Update layout for a sleek "FinTech dark mode" look
    fig1.update_layout(template="plotly_dark", title_x=0.5)
    
    # Adjust animation speed
    fig1.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 800
    fig1.write_html("animated_scatter.html")
    print("-> Saved 'animated_scatter.html'")

    print("Creating Interactive 3D Risk Landscape...")
    # 2. Interactive 3D Scatter Plot
    # Sample data to keep browser rendering smooth
    df_sample = df.sample(n=1500, random_state=42)
    fig2 = px.scatter_3d(
        df_sample,
        x='upi_transaction_velocity',
        y='seasonal_inventory_turnover',
        z='utility_bill_consistency',
        color='default_risk',
        color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
        opacity=0.7,
        title="3D Risk Landscape of Unbanked Borrowers",
        labels={
            "upi_transaction_velocity": "UPI Velocity",
            "seasonal_inventory_turnover": "Inventory Turnover",
            "utility_bill_consistency": "Utility Consistency",
            "default_risk": "Risk (1=Default)"
        }
    )
    fig2.update_layout(template="plotly_dark", title_x=0.5)
    # Tweak camera angle for better initial view
    fig2.update_layout(scene_camera=dict(eye=dict(x=1.5, y=1.5, z=0.5)))
    fig2.write_html("3d_risk_landscape.html")
    print("-> Saved '3d_risk_landscape.html'")

    print("Creating Feature Distribution Violin Plot...")
    # 3. Violin Plot (Distribution)
    # Useful for seeing the density of safe vs risky borrowers across different metrics
    fig3 = px.violin(
        df,
        y="utility_bill_consistency",
        x="default_risk",
        color="default_risk",
        box=True, 
        points="all", 
        hover_data=df.columns,
        title="Distribution of Utility Bill Consistency by Default Risk",
        color_discrete_sequence=['#00CC96', '#EF553B'] # Green for 0, Red for 1
    )
    fig3.update_layout(template="plotly_dark", title_x=0.5)
    fig3.write_html("violin_distribution.html")
    print("-> Saved 'violin_distribution.html'")
    
    print("\nAll visualizations created successfully! You can open the .html files in your web browser.")

if __name__ == "__main__":
    create_visualizations()
