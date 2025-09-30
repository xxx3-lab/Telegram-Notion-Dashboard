import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta

API_URL = "http://backend:8000"

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Finance Tracker Dashboard"

# Стили для мобильных и десктопа
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                color: #667eea;
                font-size: 2.5em;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
                margin: 10px 0;
            }
            .stat-label {
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .charts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 25px;
            }
            .chart-container {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .chart-title {
                font-size: 1.3em;
                font-weight: bold;
                color: #333;
                margin-bottom: 15px;
            }
            @media (max-width: 768px) {
                .charts-grid {
                    grid-template-columns: 1fr;
                }
                .header h1 {
                    font-size: 1.8em;
                }
                .container {
                    padding: 10px;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0),
    html.Div(id='page-content', className='container')
])

@callback(Output('page-content', 'children'), [Input('url', 'search'), Input('interval-component', 'n_intervals')])
def display_page(search, n):
    user_id = 123456  # Default
    if search:
        params = dict(item.split('=') for item in search[1:].split('&') if '=' in item)
        user_id = int(params.get('user_id', user_id))
    
    try:
        # Получаем данные
        summary = requests.get(f"{API_URL}/stats/summary/?user_id={user_id}").json()
        balance = requests.get(f"{API_URL}/balance/?user_id={user_id}").json()
        by_category = requests.get(f"{API_URL}/stats/by-category/?user_id={user_id}&days=30").json()
        daily_stats = requests.get(f"{API_URL}/stats/daily/?user_id={user_id}&days=30").json()
        monthly_stats = requests.get(f"{API_URL}/stats/monthly/?user_id={user_id}").json()
        expenses = requests.get(f"{API_URL}/expenses/?user_id={user_id}").json()
        
        # Header
        header = html.Div([
            html.H1("💰 Финансовый Dashboard"),
            html.P(f"Пользователь ID: {user_id}", style={'color': '#666'})
        ], className='header')
        
        # Stats cards
        stats_cards = html.Div([
            html.Div([
                html.Div("📅 Сегодня", className='stat-label'),
                html.Div(f"{summary['today']:.0f} ₽", className='stat-value')
            ], className='stat-card'),
            html.Div([
                html.Div("📅 За неделю", className='stat-label'),
                html.Div(f"{summary['week']:.0f} ₽", className='stat-value')
            ], className='stat-card'),
            html.Div([
                html.Div("📅 За месяц", className='stat-label'),
                html.Div(f"{summary['month']:.0f} ₽", className='stat-value')
            ], className='stat-card'),
            html.Div([
                html.Div("💼 Баланс", className='stat-label'),
                html.Div(
                    f"{balance['balance']:.0f} ₽",
                    className='stat-value',
                    style={'color': '#28a745' if balance['balance'] >= 0 else '#dc3545'}
                )
            ], className='stat-card'),
        ], className='stats-grid')
        
        # Pie chart - По категориям
        if by_category:
            df_cat = pd.DataFrame(by_category)
            fig_pie = px.pie(
                df_cat,
                values='total',
                names='category',
                title='Распределение расходов по категориям',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(height=450, showlegend=True)
        else:
            fig_pie = go.Figure()
        
        # Bar chart - По категориям
        if by_category:
            df_cat_sorted = df_cat.sort_values('total', ascending=True)
            fig_bar = px.bar(
                df_cat_sorted,
                y='category',
                x='total',
                orientation='h',
                title='Расходы по категориям (₽)',
                color='total',
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(height=450, showlegend=False)
        else:
            fig_bar = go.Figure()
        
        # Line chart - Дневная динамика
        if daily_stats:
            df_daily = pd.DataFrame(daily_stats)
            df_daily['date'] = pd.to_datetime(df_daily['date'])
            fig_line = px.line(
                df_daily,
                x='date',
                y='total',
                title='Динамика расходов по дням',
                markers=True
            )
            fig_line.update_traces(line_color='#667eea', line_width=3)
            fig_line.update_layout(height=450)
        else:
            fig_line = go.Figure()
        
        # Area chart - Накопительная сумма
        if daily_stats:
            df_daily['cumulative'] = df_daily['total'].cumsum()
            fig_area = px.area(
                df_daily,
                x='date',
                y='cumulative',
                title='Накопительные расходы',
                color_discrete_sequence=['#764ba2']
            )
            fig_area.update_layout(height=450)
        else:
            fig_area = go.Figure()
        
        # Bubble chart
        if by_category:
            df_cat['size'] = df_cat['total'] / df_cat['total'].max() * 100
            fig_bubble = px.scatter(
                df_cat,
                x='count',
                y='total',
                size='size',
                color='category',
                title='Bubble Chart: Частота vs Сумма',
                labels={'count': 'Количество транзакций', 'total': 'Сумма (₽)'},
                size_max=60
            )
            fig_bubble.update_layout(height=450)
        else:
            fig_bubble = go.Figure()
        
        # Sunburst chart
        if expenses:
            df_expenses = pd.DataFrame(expenses)
            if not df_expenses.empty:
                df_expenses['month'] = pd.to_datetime(df_expenses['date']).dt.strftime('%Y-%m')
                fig_sunburst = px.sunburst(
                    df_expenses,
                    path=['month', 'category'],
                    values='amount',
                    title='Иерархия расходов: Месяц → Категория'
                )
                fig_sunburst.update_layout(height=450)
            else:
                fig_sunburst = go.Figure()
        else:
            fig_sunburst = go.Figure()
        
        # Treemap
        if by_category:
            fig_treemap = px.treemap(
                df_cat,
                path=['category'],
                values='total',
                title='Treemap расходов по категориям',
                color='total',
                color_continuous_scale='RdYlGn_r'
            )
            fig_treemap.update_layout(height=450)
        else:
            fig_treemap = go.Figure()
        
        # Monthly trend
        if monthly_stats:
            df_monthly = pd.DataFrame(monthly_stats)
            df_monthly['period'] = df_monthly['year'].astype(str) + '-' + df_monthly['month'].astype(str).str.zfill(2)
            fig_monthly = px.bar(
                df_monthly,
                x='period',
                y='total',
                title='Расходы по месяцам',
                color='total',
                color_continuous_scale='Blues'
            )
            fig_monthly.update_layout(height=450)
        else:
            fig_monthly = go.Figure()
        
        # Heatmap (если есть данные за несколько месяцев)
        if expenses and len(expenses) > 10:
            df_exp = pd.DataFrame(expenses)
            df_exp['date'] = pd.to_datetime(df_exp['date'])
            df_exp['weekday'] = df_exp['date'].dt.dayofweek
            df_exp['week'] = df_exp['date'].dt.isocalendar().week
            
            heatmap_data = df_exp.groupby(['week', 'weekday'])['amount'].sum().reset_index()
            pivot_table = heatmap_data.pivot(index='weekday', columns='week', values='amount').fillna(0)
            
            fig_heatmap = px.imshow(
                pivot_table,
                title='Heatmap расходов по дням недели',
                labels={'x': 'Неделя', 'y': 'День недели', 'color': 'Сумма (₽)'},
                color_continuous_scale='Reds',
                aspect='auto'
            )
            fig_heatmap.update_layout(height=450)
        else:
            fig_heatmap = go.Figure()
        
        # Box plot
        if expenses:
            df_exp = pd.DataFrame(expenses)
            fig_box = px.box(
                df_exp,
                x='category',
                y='amount',
                title='Распределение сумм по категориям (Box Plot)',
                color='category'
            )
            fig_box.update_layout(height=450, showlegend=False)
        else:
            fig_box = go.Figure()
        
        # Violin plot
        if expenses:
            fig_violin = px.violin(
                df_exp,
                x='category',
                y='amount',
                title='Violin Plot распределения расходов',
                color='category',
                box=True
            )
            fig_violin.update_layout(height=450, showlegend=False)
        else:
            fig_violin = go.Figure()
        
        # Funnel chart - топ категории
        if by_category:
            df_cat_top = df_cat.nlargest(7, 'total')
            fig_funnel = px.funnel(
                df_cat_top,
                x='total',
                y='category',
                title='Funnel Chart топовых категорий'
            )
            fig_funnel.update_layout(height=450)
        else:
            fig_funnel = go.Figure()
        
        # Charts grid
        charts = html.Div([
            html.Div([
                html.Div("🥧 Распределение по категориям", className='chart-title'),
                dcc.Graph(figure=fig_pie, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("📊 Расходы по категориям", className='chart-title'),
                dcc.Graph(figure=fig_bar, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("📈 Дневная динамика", className='chart-title'),
                dcc.Graph(figure=fig_line, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("📉 Накопительные расходы", className='chart-title'),
                dcc.Graph(figure=fig_area, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("🫧 Частота vs Сумма", className='chart-title'),
                dcc.Graph(figure=fig_bubble, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("☀️ Иерархия расходов", className='chart-title'),
                dcc.Graph(figure=fig_sunburst, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("🗺️ Treemap категорий", className='chart-title'),
                dcc.Graph(figure=fig_treemap, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("📅 Месячный тренд", className='chart-title'),
                dcc.Graph(figure=fig_monthly, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("🔥 Heatmap активности", className='chart-title'),
                dcc.Graph(figure=fig_heatmap, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("📦 Box Plot распределения", className='chart-title'),
                dcc.Graph(figure=fig_box, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("🎻 Violin Plot", className='chart-title'),
                dcc.Graph(figure=fig_violin, config={'displayModeBar': False})
            ], className='chart-container'),
            
            html.Div([
                html.Div("🎯 Funnel топовых категорий", className='chart-title'),
                dcc.Graph(figure=fig_funnel, config={'displayModeBar': False})
            ], className='chart-container'),
        ], className='charts-grid')
        
        return [header, stats_cards, charts]
    
    except Exception as e:
        return html.Div([
            html.H1("❌ Ошибка загрузки данных"),
            html.P(f"Детали: {str(e)}")
        ])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
