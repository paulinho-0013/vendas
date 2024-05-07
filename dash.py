import streamlit as st
import requests
import pandas as pd
import plotly.express as px

#CONFIGURAÇÃO DE PAGINA
st.set_page_config(layout='wide')



#CRIANDO FUNCAO FORMATA NUMERO
def formata_numero(valor, prefixo=''):
    for unidade in ['','mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /=1000
    return f'{prefixo} {valor:.2f} milhoes'



#TITULO DO APP
st.title("Dashboard de Vendas :shopping_trolley:")

#IMPORTANDO DADOS DA API
url = 'https://labdados.com/produtos'

#FILTROS DE REGIÕES
regioes=['Brasil','Centro-Oeste','Nordeste','Sudeste','Sul']
#SIDEBAR
st.sidebar.title('Filtros')
#REGRA PARA QUANDO ESTIVER BRASIL RETORNAR NULO
regiao = st.sidebar.selectbox('Região',regioes)
if regiao == 'Brasil':
    regiao = ''
#FILTRO ANOS
todos_anos = st.sidebar.checkbox('Dados de todo o periodo', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

#CRIANDO QUERY
query_string = {'regiao':regiao.lower(), 'ano':ano}

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra']=pd.to_datetime(dados['Data da Compra'],format='%d/%m/%Y')


#FILTROS VENDEDORES
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]



#TABELAS
##TABELAS DE RECEITAS
###TABELA_RECEITA ESTADO
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(receita_estados, left_on='Local da compra',right_index=True).sort_values('Preço', ascending=False)

###TABELA_RECEITA MENSAL
receita_mensal =dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano']=receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes']=receita_mensal['Data da Compra'].dt.month_name()

###TABELA_RECEITA CATEGORIAS
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)


##TABELA_QUANTIDADE VENDAS
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

##TABELA_QUANTIDADE MENSAL
vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

##TABELA_QUATIDADE CATEGORIA PRODUTO
vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

##TABELA_QUANTIDADE VENDEDORES
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))



##GRAFICOS
#MAPA
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope='south america',
                                  size = 'Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon':False},
                                  title = 'Receita por estado')
#LINHA
fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0,receita_mensal.max()),
                             color = 'Ano',
                             line_dash='Ano',
                             title='Receita mensal')

fig_receita_mensal.update_layout(yaxis_title='Receita')

#GRAFICO DE BARRA ESTADOS
fig_receita_estados = px.bar(receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto= True,
                             title = 'Top estados (receita)')

fig_receita_estados.update_layout(yaxis_title='Receita')

#GRAFICO DE BARRA CATEGORIA
fig_receita_categorias = px.bar(receita_categorias,
                             text_auto=True,
                             title='Receita por categoria')

fig_receita_categorias.update_layout(yaxis_title='Receita')


#GRAFICO DE MAPA DE QUATIDADE POR ESTADO
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

#GRAFICO DE QUANTIDADE DE VENDAS MENSAL
fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

#GRAFICO DOS 5 ESTADOS COM MAIOR QUANTIDADE DE VENDAS
fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')


#GRAFICO DE QUANTIDADE DE VENDAS POR CATEGORIA DE PRODUTOS
fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')





##VISUALIZACAO NO STREAMLIT
#CRIANDO ABAS NO RELATORIO
aba1, aba2, aba3 = st.tabs(['Receita','Quantidade de vendas','Vendedores'])
#CRIANDO COLUNAS
with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True) #user - garante que ele respeite o tamanho do conteiner
        st.plotly_chart(fig_receita_estados,use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias,use_container_width=True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

with aba3:
    qtde_vendedores = st.number_input('Quantidade Vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        #FOI CRIADO O GRAFICO ABAIXO POR CONTA DO BOTAO QTDE_VENDEDORES
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum',ascending=False).head(qtde_vendedores),
                                        x = 'sum',
                                        y= vendedores[['sum']].sort_values('sum',ascending=False).head(qtde_vendedores).index,
                                        text_auto = True,
                                        title = f'Top{qtde_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count',ascending=False).head(qtde_vendedores),
                                        x = 'count',
                                        y= vendedores[['count']].sort_values('count',ascending=False).head(qtde_vendedores).index,
                                        text_auto = True,
                                        title = f'Top{qtde_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_receita_vendedores)






