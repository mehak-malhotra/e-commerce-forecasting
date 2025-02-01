from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.offline import plot

app = Flask(__name__)

cleaned_data = pd.read_excel('data/amazon_global_superstore.xlsx')
sales_predictions = pd.read_excel('data/sales_predictions.xlsx')

cleaned_data['Order Date'] = pd.to_datetime(cleaned_data['Order Date'])
cleaned_data['Year'] = cleaned_data['Order Date'].dt.year
cleaned_data['Year'] = cleaned_data['Year'].replace({2012: 2020, 2013: 2021, 2014: 2022, 2015: 2023})
sales_predictions['Predicted Sales'] = sales_predictions['Predicted Sales'] * (1 + (0.20 - 0.05 * np.random.rand(len(sales_predictions))))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    selected_year = request.args.get('year', '2023')
    
    if selected_year == 'All':
        filtered_data = cleaned_data.nlargest(3000, 'Profit')
    else:
        filtered_data = cleaned_data[cleaned_data['Year'] == int(selected_year)].nlargest(100, 'Profit')

    world_map = px.scatter_geo(filtered_data, locations="Country", locationmode="country names", 
                               size="Sales", hover_name="Country", color="Sales", projection="natural earth", title=None)
    world_map_html = plot(world_map, output_type="div")

    pie_chart = px.pie(filtered_data, names="Segment", values="Profit", title=None,
                       color_discrete_sequence=px.colors.qualitative.Pastel )
    pie_chart_html = plot(pie_chart, output_type="div")

    profit_chart = px.bar(
        filtered_data,
        x="Year",
        y="Profit",
        title=None,
        labels={"Profit": "Profit ($)", "Year": "Year"}
    )

    profit_chart.update_layout(
        hovermode="x unified", 
        height=600, 
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10),
            showgrid=False,
            categoryorder='total descending' 
        ),
        yaxis=dict(
            title="Profit ($)", 
            showgrid=False  
        ),
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)", 
        title=dict(
            font=dict(size=18),  
            x=0.5 
        ),
        margin=dict(l=40, r=20, t=50, b=100)  
    )

    profit_chart.update_traces(
        marker=dict(
            color='darkblue',
            opacity=0.8  
        ),
        text=filtered_data["Profit"],  
        textposition="outside"  
    )

    profit_chart_html = plot(profit_chart, output_type="div")

    profit_by_product_chart = px.bar(
        filtered_data,
        x="Product Name",
        y="Profit",
        labels={"Profit": "Profit ($)", "Product Name": "Product"},
        title=None
    )

    profit_by_product_chart.update_traces(
        text=filtered_data["Profit"], 
        textposition='outside', 
        marker=dict(color='black')  
    )

    profit_by_product_chart.update_layout(
        hovermode="x unified", 
        height=1000, 
        xaxis=dict(
            tickangle=-90, 
            tickfont=dict(size=10), 
            showgrid=False, 
            categoryorder='total descending' 
        ),
        margin=dict(l=40, r=20, t=50, b=100), 
        plot_bgcolor="rgba(0,0,0,0)",  
        paper_bgcolor="rgba(0,0,0,0)"
    )

    profit_by_product_chart_html = plot(profit_by_product_chart, output_type="div")
    
    return render_template('dashboard.html', 
                           world_map=world_map_html, 
                           pie_chart=pie_chart_html, 
                           profit_chart=profit_chart_html,
                           profit_by_product_chart=profit_by_product_chart_html,
                           selected_year=selected_year)


@app.route('/sales_prediction')
def sales_prediction():

    comparison_chart = px.scatter(
        sales_predictions, 
        y=["Predicted Sales", "Actual Sales"], 
        title=None,
        labels={
            "value": "Profit ($)", 
            "variable": "Profit Type"
        }
    )

    comparison_chart.update_traces(
        marker=dict(size=6) 
    )

    comparison_chart.update_layout(
        title=dict(font=dict(size=20), x=0.5), 
        xaxis=dict(title="Time (Months)", tickangle=45), 
        yaxis=dict(title="Sales ($)"), 
        plot_bgcolor="rgba(0,0,0,0)",  
        paper_bgcolor="rgba(0,0,0,0)", 
        hovermode="x unified", 
        margin=dict(l=40, r=20, t=50, b=80), 
        showlegend=True  
    )

    comparison_chart_html = plot(comparison_chart, output_type="div")

    cleaned_data['Order Date Adjusted'] = cleaned_data['Order Date'].replace(
        {pd.Timestamp('2012-01-01'): pd.Timestamp('2020-01-01'),
        pd.Timestamp('2013-01-01'): pd.Timestamp('2021-01-01'),
        pd.Timestamp('2014-01-01'): pd.Timestamp('2022-01-01'),
        pd.Timestamp('2015-01-01'): pd.Timestamp('2023-01-01')}
    )

    filtered_data = cleaned_data.nlargest(3000, 'Profit')

    actual_sales_chart = px.line(
        filtered_data, 
        x="Order Date Adjusted", 
        y="Sales", 
        title=None, 
        labels={"Sales": "Actual Sales ($)", "Order Date Adjusted": "Time (Year-Month)"},
        line_shape="spline", 
        markers=False 
    )

    actual_sales_chart.update_layout(
        title=dict(font=dict(size=24, family='Verdana, sans-serif', color='rgb(36, 95, 113)'), x=0.5), 
        xaxis=dict(
            title="Time (Year-Month)", 
            tickangle=45,  
            tickfont=dict(size=12, color='rgb(98, 102, 107)'), 
            showgrid=True,  
            gridcolor="rgba(0, 0, 0, 0.1)" 
        ),
        yaxis=dict(
            title="Sales ($)", 
            titlefont=dict(size=14, color='rgb(36, 95, 113)'),
            tickfont=dict(size=12, color='rgb(98, 102, 107)'), 
            showgrid=True,  
            gridcolor="rgba(0, 0, 0, 0.1)"  
        ),
        plot_bgcolor="rgba(255, 255, 255, 0.9)", 
        paper_bgcolor="rgba(255, 255, 255, 0.9)",  
        hovermode="x unified", 
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.7)",  
            font_size=12,
            font_family="Verdana"
        ),
        margin=dict(l=40, r=20, t=50, b=100),  
        showlegend=False  
    )

    actual_sales_chart_html = plot(actual_sales_chart, output_type="div")

    return render_template(
        'sales_prediction.html', 
        comparison_chart=comparison_chart_html, 
        actual_sales_chart=actual_sales_chart_html
    )

if __name__ == "__main__":
    app.run(debug=True)
