import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests



# URL da API do Google Sheets
url = "https://sheets.googleapis.com/v4/spreadsheets/1jPCW6USCP4y4CdG5bgzo6ytv2AmtnsI-jR44_LVoAyY/values/A1:G100?key=AIzaSyAdVWlABQ8jmXjyghfAOcWoweelNOgR_BY"

# Fazer a requisição GET
response = requests.get(url)
data = response.json()

st.set_page_config(page_title="Dashboard Imobiliária Sandbox", layout="wide")

# Extrair os cabeçalhos e os valores dos dados JSON
headers = data['values'][0]
values = data['values'][1:]

# Criar um DataFrame com os dados
df = pd.DataFrame(values, columns=headers)

# Converter a coluna de datas para o formato datetime
df['data_venda'] = pd.to_datetime(df['data_venda'], format='%d/%m/%Y')

# Converter as colunas numéricas para o tipo adequado
df['valor'] = pd.to_numeric(df['valor'].str.replace('.', '').str.replace(',', '.'), errors='coerce')
df['fluxo_caixa'] = pd.to_numeric(df['fluxo_caixa'].str.replace('.', '').str.replace(',', '.'), errors='coerce')

# Adicionar colunas para comissão e lucro real
df['comissao_imobiliaria'] = df['valor'] * 0.10
df['comissao_vendedores'] = df['valor'] * 0.05
df['lucro_real'] = df['valor'] - df['comissao_imobiliaria'] - df['comissao_vendedores']

# Verificar se a coluna 'cidade' existe
if 'cidade' not in df.columns:
    st.error("A coluna 'cidade' não foi encontrada no DataFrame.")
else:
    # Funções para criar gráficos
    def create_line_chart(data, x, y, title):
        fig = px.line(data, x=x, y=y, title=title, labels={x: 'Data', y: 'Valor'}, line_shape='linear')
        fig.update_layout(
            autosize=True,
            height=300,  # Aumentar a altura do gráfico
            width=1200,  # Aumentar a largura do gráfico
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(240,240,240,0.1)'
        )
        fig.update_traces(line=dict(color='royalblue'))
        return fig
    
    

    def create_bar_chart(data, x, y, title):
        fig = px.bar(data, x=x, y=y, title=title, labels={x: x, y: y}, color_discrete_sequence=['mediumseagreen'])
        fig.update_layout(
            autosize=True,
            height=400,  # Aumentar a altura do gráfico
            width=600,   # Aumentar a largura do gráfico
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(240,240,240,0.1)'
        )
        fig.update_traces(marker=dict(color='darkgreen'))
        return fig

    def create_pie_chart(data, values, names):
        fig = px.pie(data, values=values, names=names, title='Distribuição de Vendas', color_discrete_sequence=px.colors.sequential.Plasma)
        fig.update_layout(
            autosize=True,
            height=400,  # Aumentar a altura do gráfico
            width=600,   # Aumentar a largura do gráfico
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(240,240,240,0.1)'
        )
        return fig

    def create_sales_per_month_chart(data):
        data['month_year'] = data['data_venda'].dt.to_period('M').dt.to_timestamp()
        monthly_sales = data.groupby('month_year')['valor'].sum().reset_index()
        
        fig = px.bar(monthly_sales, x='month_year', y='valor', title='Total de Vendas por Mês', labels={'month_year': 'Mês', 'valor': 'Total de Vendas'})
        fig.update_layout(
            autosize=True,
            height=400,  # Aumentar a altura do gráfico
            width=600,   # Aumentar a largura do gráfico
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(240,240,240,0.1)'
        )
        fig.update_traces(marker=dict(color='mediumvioletred'))
        return fig

    def create_value_by_type_chart(data):
        avg_values = data.groupby('tipo_imovel')['valor'].mean().reset_index()
        avg_values.columns = ['Tipo de Imóvel', 'Valor Médio']
        
        fig = px.bar(avg_values, x='Tipo de Imóvel', y='Valor Médio', title='Valor Médio por Tipo de Imóvel', labels={'Tipo de Imóvel': 'Tipo de Imóvel', 'Valor Médio': 'Valor Médio'})
        fig.update_layout(
            autosize=True,
            height=400,  # Aumentar a altura do gráfico
            width=600,   # Aumentar a largura do gráfico
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(240,240,240,0.1)'
        )
        fig.update_traces(marker=dict(color='coral'))
        return fig

    def create_commissions_by_vendedor_chart(data):
        commissions_by_vendedor = data.groupby('vendedor')['comissao_vendedores'].sum().reset_index()
        commissions_by_vendedor.columns = ['Vendedor', 'Comissão Total']
        
        fig = px.bar(commissions_by_vendedor, x='Vendedor', y='Comissão Total', title='Comissão Total por Vendedor', labels={'Vendedor': 'Vendedor', 'Comissão Total': 'Comissão Total'})
        fig.update_layout(
            autosize=True,
            height=400,  # Aumentar a altura do gráfico
            width=600,   # Aumentar a largura do gráfico
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(240,240,240,0.1)'
        )
        fig.update_traces(marker=dict(color='royalblue'))
        return fig

    def create_sales_by_city_chart(data):
        sales_by_city = data.groupby('cidade')['valor'].sum().reset_index()
        sales_by_city.columns = ['Cidade', 'Total de Vendas']
        
        fig = px.bar(sales_by_city, x='Cidade', y='Total de Vendas', title='Vendas por Cidade', labels={'Cidade': 'Cidade', 'Total de Vendas': 'Total de Vendas'})
        fig.update_layout(
            autosize=True,
            height=400,  # Aumentar a altura do gráfico
            width=600,   # Aumentar a largura do gráfico
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(181,240,240,0.1)'
        )
        fig.update_traces(marker=dict(color='royalblue'))
        return fig


    def create_vendedor_performance_chart(data):
        performance = data.groupby('vendedor')['valor'].sum().reset_index()
        performance.columns = ['Vendedor', 'Total de Vendas']
        
        fig = px.bar(performance, x='Vendedor', y='Total de Vendas', title='Desempenho dos Vendedores', labels={'Vendedor': 'Vendedor', 'Total de Vendas': 'Total de Vendas'})
        fig.update_layout(
            autosize=True,
            height=400,  # Aumentar a altura do gráfico
            width=600,   # Aumentar a largura do gráfico
            margin=dict(l=50, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(240,240,240,0.1)'
        )
        fig.update_traces(marker=dict(color='purple'))
        return fig
    

 # Widgets do Streamlit para filtragem
st.sidebar.header("Filtros")

# Definir as datas mínima e máxima com base nos dados
min_date = df['data_venda'].min().date()
max_date = df['data_venda'].max().date()

# Filtro de datas
start_date = st.sidebar.date_input("Data de Início", min_date)
end_date = st.sidebar.date_input("Data de Fim", max_date)

# Verificar se a data de início é anterior à data de fim
if start_date > end_date:
    st.sidebar.error("A Data de Início não pode ser posterior à Data de Fim.")
    filtered_df = pd.DataFrame()  # Exibir um DataFrame vazio se a data estiver incorreta
else:
    # Aplicar o filtro de datas
    filtered_df = df[
        (df['data_venda'].dt.date >= start_date) &
        (df['data_venda'].dt.date <= end_date)
    ]

# Filtros de tipo de imóvel, vendedor e cidade
tipos_imovel = df['tipo_imovel'].unique().tolist() + ["Todos"]
selected_tipo_imovel = st.sidebar.multiselect("Selecione o tipo de imóvel", tipos_imovel, default=tipos_imovel[:-1])

vendedores = df['vendedor'].unique().tolist() + ["Todos"]
selected_vendedor = st.sidebar.multiselect("Selecione o vendedor", vendedores, default=vendedores[:-1])

cidades = df['cidade'].unique().tolist() + ["Todos"]
selected_cidade = st.sidebar.multiselect("Selecione a cidade", cidades, default=cidades[:-1])

# Aplicar filtros adicionais
filtered_df = filtered_df[
    (filtered_df['tipo_imovel'].isin(selected_tipo_imovel) if "Todos" not in selected_tipo_imovel else True) &
    (filtered_df['vendedor'].isin(selected_vendedor) if "Todos" not in selected_vendedor else True) &
    (filtered_df['cidade'].isin(selected_cidade) if "Todos" not in selected_cidade else True)
]



# Títulos e cabeçalhos
st.title("Dashboard Ponto Imobiliária 🏠")

# Criar colunas para os indicadores chave na horizontal
st.subheader("Indicadores Resumidos")
col7, col8, col9, col10, col11 = st.columns(5)

with col7:
    st.metric(label="Ticket Médio", value=f"R$ {filtered_df['valor'].mean():,.2f}", help="Valor médio das vendas realizadas.")

with col8:
    st.metric(label="Total de Imóveis Vendidos", value=f"{len(filtered_df)}", help="Número total de imóveis vendidos no período selecionado.")

with col9:
    st.metric(label="Fluxo de Caixa Gerado", value=f"R$ {filtered_df['fluxo_caixa'].sum():,.2f}", help="Total de fluxo de caixa gerado.")

with col10:
    st.metric(label="Comissão Total Imobiliária", value=f"R$ {filtered_df['comissao_imobiliaria'].sum():,.2f}", help="Total de comissões pagas para a imobiliária.")

with col11:
    st.metric(label="Comissão Total dos Vendedores", value=f"R$ {filtered_df['comissao_vendedores'].sum():,.2f}", help="Total de comissões pagas para os vendedores.")
st.header("Gráficos e Indicadores 📊")

# Exibir gráfico de linha na parte superior
st.plotly_chart(create_line_chart(filtered_df, 'data_venda', 'valor', 'Total de Vendas ao Longo do Tempo'), use_container_width=True)

# Layout de gráficos na linha superior
col1, col2 = st.columns([2, 2])

with col1:
    st.plotly_chart(create_bar_chart(filtered_df, 'tipo_imovel', 'valor', 'Vendas por Tipo de Imóvel'), use_container_width=True)

with col2:
    st.plotly_chart(create_pie_chart(filtered_df, 'valor', 'cidade'), use_container_width=True)

# Layout de gráficos na linha inferior
col3, col4 = st.columns([2, 2])

with col3:
    st.plotly_chart(create_sales_per_month_chart(filtered_df), use_container_width=True)

with col4:
    st.plotly_chart(create_value_by_type_chart(filtered_df), use_container_width=True)

# Adicionar a linha inferior com os gráficos restantes
col5, col6 = st.columns([2, 2])

with col5:
    st.plotly_chart(create_commissions_by_vendedor_chart(filtered_df), use_container_width=True)

with col6:
    st.plotly_chart(create_vendedor_performance_chart(filtered_df), use_container_width=True)

