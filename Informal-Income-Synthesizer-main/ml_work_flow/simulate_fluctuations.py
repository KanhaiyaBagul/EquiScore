import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_fluctuation_dashboard():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # We will simulate 12-month historical logs for two specific users to show their fluctuations.
    np.random.seed(42)
    
    # ---------------------------------------------------------
    # Borrower A: Good Profile (Approved)
    # Has stable fluctuations, indicating a healthy business
    # ---------------------------------------------------------
    borrower_a_upi = np.random.normal(300, 25, 12)  # Stable, high transaction volume
    borrower_a_inventory = np.random.normal(8.5, 0.8, 12) # Consistent inventory turnover
    borrower_a_bills = [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1] # Missed only 1 utility bill in August
    
    # ---------------------------------------------------------
    # Borrower B: Risky Profile (Denied)
    # Has wild fluctuations and a downward trend, high risk
    # ---------------------------------------------------------
    borrower_b_upi = np.linspace(280, 60, 12) + np.random.normal(0, 40, 12) # Declining volume with wild swings
    borrower_b_inventory = np.linspace(6.5, 1.5, 12) + np.random.normal(0, 1.2, 12) # Inventory sits longer
    borrower_b_bills = [1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0] # Extremely inconsistent bill payments
    
    # Ensure no negative values
    borrower_b_upi = np.maximum(0, borrower_b_upi)
    borrower_b_inventory = np.maximum(0, borrower_b_inventory)
    
    # Create interactive subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "1. UPI Transaction Velocity Fluctuations (Count per Month)", 
            "2. Seasonal Inventory Turnover Ratio", 
            "3. Utility Bill Payment Status (1 = Paid, 0 = Missed)"
        )
    )
    
    # --- Row 1: UPI Velocity ---
    fig.add_trace(
        go.Scatter(x=months, y=borrower_a_upi, name="Borrower A (Approved)", 
                   line=dict(color="#00CC96", width=4, shape='spline'), mode='lines+markers', marker=dict(size=8)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=months, y=borrower_b_upi, name="Borrower B (Denied)", 
                   line=dict(color="#EF553B", width=4, shape='spline'), mode='lines+markers', marker=dict(size=8)),
        row=1, col=1
    )
    
    # --- Row 2: Inventory Turnover ---
    fig.add_trace(
        go.Scatter(x=months, y=borrower_a_inventory, name="Borrower A", showlegend=False, 
                   line=dict(color="#00CC96", width=3, dash='dot', shape='spline'), mode='lines+markers', marker=dict(symbol='diamond', size=8)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=months, y=borrower_b_inventory, name="Borrower B", showlegend=False, 
                   line=dict(color="#EF553B", width=3, dash='dot', shape='spline'), mode='lines+markers', marker=dict(symbol='diamond', size=8)),
        row=2, col=1
    )
    
    # --- Row 3: Utility Bills ---
    fig.add_trace(
        go.Bar(x=months, y=borrower_a_bills, name="Borrower A Bills", marker_color="#00CC96", opacity=0.8),
        row=3, col=1
    )
    fig.add_trace(
        go.Bar(x=months, y=borrower_b_bills, name="Borrower B Bills", marker_color="#EF553B", opacity=0.8),
        row=3, col=1
    )
    
    # Update layout for a highly interactive, animated-feel time-series
    fig.update_layout(
        title="12-Month Financial Fluctuations: Approved vs. Denied Profile",
        template="plotly_dark",
        height=900,
        hovermode="x unified", # Shows all values simultaneously on hover
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1)
    )
    
    # Add interactive range slider to the bottom for zooming in on specific months
    fig.update_xaxes(rangeslider_visible=True, row=3, col=1)
    
    fig.write_html("fluctuation_trends.html")
    print("Created interactive fluctuation trends dashboard at 'fluctuation_trends.html'")

if __name__ == "__main__":
    create_fluctuation_dashboard()
