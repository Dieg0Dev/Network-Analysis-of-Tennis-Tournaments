import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import streamlit as st
from IPython.display import HTML, display

# Carregar os dados
tennis_df = pd.read_csv("https://raw.githubusercontent.com/Dieg0Dev/datasets/main/atp_tennis.csv")
tennis_df['Date'] = pd.to_datetime(tennis_df['Date'], errors='coerce')

# Filtrar os Grand Slams
grand_slams = tennis_df[tennis_df['Series'] == 'Grand Slam']
australian_open = tennis_df[tennis_df['Tournament'] == 'Australian Open']
french_open = tennis_df[tennis_df['Tournament'] == 'French Open']
wimbledon = tennis_df[tennis_df['Tournament'] == 'Wimbledon']
us_open = tennis_df[tennis_df['Tournament'] == 'US Open']

# Função para criar o grafo
def criar_grafo(torneio, ano):
    torneio_ano = torneio[torneio['Date'].dt.year == ano]
    G = nx.DiGraph()
    for index, row in torneio_ano.iterrows():
        player1 = row['Player_1']
        player2 = row['Player_2']
        winner = row['Winner']
        if player1 == winner: 
            G.add_edge(player1, player2)
        else:
            G.add_edge(player2, player1)
    return G

# Função para exibir o gráfico Pyvis
def exibir_grafo_pyvis(G, torneio_nome, ano):
    st.header(f"{torneio_nome} {ano}:")
    tennis_net = Network(height="500px", width="700px", bgcolor="#222222", font_color="white", directed=True)
    tennis_net.from_nx(G)
    filename = f"html_files/{torneio_nome.lower().replace(' ', '_')}.html"
    tennis_net.write_html(filename)
    HtmlFile = open(filename, 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=800, width=1200)

# Sidebar para seleção
st.set_page_config(layout="wide")
st.sidebar.title('Aplique as Definições')
torneio = st.sidebar.selectbox('Selecione o Torneio', ['Australian Open', 'Roland Garros', 'Wimbledon', 'US Open', 'Todos os Grand Slams'])
ano = int(st.sidebar.selectbox('Selecione o Ano', list(range(2000, 2025))))
opcao_visualizacao = st.sidebar.radio("Selecione o que deseja visualizar", ['Grafo Interativo Pyvis', 'Matriz de Adjacência', 'Diâmetro e Periferia da rede', 'Densidade e Assortatividade Geral da Rede', 'Histograma de Distribuição Empírica de Grau', 'Coeficiente de Clustering e Componentes Conectados', 'Nós mais importantes por medidas de centralidade'])

# Selecionar o torneio correspondente
torneio_map = {
    'Australian Open': australian_open,
    'Roland Garros': french_open,
    'Wimbledon': wimbledon,
    'US Open': us_open,
    'Todos os Grand Slams': grand_slams
}

def categorize_ranking(rank):
    if rank <= 50:
        return '1-50'
    elif rank <= 100:
        return '51-100'
    elif rank <= 150:
        return '101-150'
    else:
        return '151+'

# Criar o grafo com base no torneio selecionado
G = criar_grafo(torneio_map[torneio], ano)

# Exibição condicional com base na opção selecionada
if opcao_visualizacao == 'Grafo Interativo Pyvis':
    exibir_grafo_pyvis(G, torneio, ano)
    
elif opcao_visualizacao == 'Matriz de Adjacência':
    labels = list(G.nodes())
    adj_matrix = nx.adjacency_matrix(G).todense()
    df = pd.DataFrame(adj_matrix, index=labels, columns=labels)
    st.header("Matriz de Adjacência:")
    st.dataframe(df)

elif opcao_visualizacao == 'Diâmetro e Periferia da rede':
    st.header("Diâmetro e Periferia da Rede")
    
    comComponenteConexo = False
    components = list(nx.strongly_connected_components(G))
    subgraphs = []

    for component in components:
        subgraph = G.subgraph(component).copy()
        
        if len(subgraph) > 1:
            comComponenteConexo = True
            diameter = nx.diameter(subgraph)
            periphery = nx.periphery(subgraph)
            
            subgraphs.append({
                'nodes': component,
                'subgraph': subgraph,
                'diameter': diameter,
                'periphery': periphery
            })
            
            st.subheader(f"Componente {component}")
            st.write(f"**Diâmetro:** {diameter}")
            st.write(f"**Periferia:** {periphery}")
            
            # Exibir a visualização do subgrafo
            fig, ax = plt.subplots(figsize=(10, 8))
            pos = nx.spring_layout(subgraph)  # Layout para melhor visualização
            nx.draw(subgraph, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500, font_size=10, ax=ax)
            st.pyplot(fig)
    
    if not comComponenteConexo:
        st.header("Sem Componente Conexo")
        st.write("Nenhum componente conexo encontrado.")

elif opcao_visualizacao == 'Densidade e Assortatividade Geral da Rede':
    st.header("Análise de Densidade e Assortatividade da Rede")

    # Calcular e exibir a densidade da rede
    density = nx.density(G)
    st.markdown(f"### Densidade da Rede")
    st.markdown(f"A densidade da rede é **{density:.4f}**.")

    # Verificar se as colunas de ranking estão presentes no DataFrame
    if 'Rank_1' in torneio_map[torneio].columns and 'Rank_2' in torneio_map[torneio].columns:
        
        # Atribuir grupos de ranking aos nós do grafo
        for index, row in torneio_map[torneio].iterrows():
            player1 = row['Player_1']
            player2 = row['Player_2']
            
            # Atribuir o grupo de ranking baseado no ranking do jogador
            if player1 in G:
                G.nodes[player1]['rank_group'] = categorize_ranking(row['Rank_1'])
            if player2 in G:
                G.nodes[player2]['rank_group'] = categorize_ranking(row['Rank_2'])
        
        # Verificar se os nós têm o atributo 'rank_group' antes de calcular a assortatividade
        try:
            assortativity = nx.attribute_assortativity_coefficient(G, 'rank_group')
            st.markdown(f"### Assortatividade da Rede Baseada nos Grupos de Ranking")
            st.markdown(f"A assortatividade da rede, com base nos grupos de ranking dos jogadores, é **{assortativity:.4f}**")

            # Exibir gráficos de estatísticas
            fig, ax = plt.subplots()
            ax.bar(['Densidade', 'Assortatividade'], [density, assortativity], color=['skyblue', 'salmon'])
            ax.set_ylabel('Valor')
            ax.set_title('Estatísticas da Rede')
            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Erro ao calcular a assortatividade: {e}")
    else:
        st.warning("Colunas de ranking não encontradas no DataFrame. Assortatividade não pode ser calculada.")

elif opcao_visualizacao == 'Histograma de Distribuição Empírica de Grau':
    # Obter os graus de entrada (indegree) e de saída (outdegree) dos nós no grafo
    indegrees = [degree for node, degree in G.in_degree()]
    outdegrees = [degree for node, degree in G.out_degree()]

    # Criação das colunas no Streamlit
    col1, col2 = st.columns(2)

    # Exibir o histograma de indegree
    with col1:
        st.subheader("Distribuição do Grau de Entrada (Indegree)")
        fig_in, ax_in = plt.subplots()
        ax_in.hist(indegrees, bins=20, color='skyblue', edgecolor='black')
        ax_in.set_title('Indegree')
        ax_in.set_xlabel('Grau de Entrada')
        ax_in.set_ylabel('Frequência')
        st.pyplot(fig_in)

    # Exibir o histograma de outdegree
    with col2:
        st.subheader("Distribuição do Grau de Saída (Outdegree)")
        fig_out, ax_out = plt.subplots()
        ax_out.hist(outdegrees, bins=20, color='salmon', edgecolor='black')
        ax_out.set_title('Outdegree')
        ax_out.set_xlabel('Grau de Saída')
        ax_out.set_ylabel('Frequência')
        st.pyplot(fig_out)

elif opcao_visualizacao == 'Coeficiente de Clustering e Componentes Conectados':
    st.header("Análise de Clustering e Componentes Conectados")
    
    clustering_global = nx.average_clustering(G)
    st.subheader("Coeficiente de Clustering Global")
    st.write(f"O coeficiente de clustering global da rede é: {clustering_global:.4f}")
    st.write("Acaso esteja sendo analisado apenas um torneio, essa medida naturalmente será 0, pois jogadores derrotados anteriormente não poderão enfrentar jogadores que futuramente poderão ser enfrentados.")

    selected_nodes = st.multiselect('Escolha os nós para calcular o coeficiente de clustering local', list(G.nodes()))
    
    if selected_nodes:
        local_clustering = nx.clustering(G, selected_nodes)
        st.subheader("Coeficiente de Clustering Local")
        st.write("Aqui estão os coeficientes de clustering locais para os nós escolhidos:")
        st.write(local_clustering)

    strongly_connected = list(nx.strongly_connected_components(G))
    num_strongly_connected = len(strongly_connected)
    st.subheader("Componentes Fortemente Conectados")
    st.write(f"A rede contém {num_strongly_connected} componentes fortemente conectados.")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Visualização de um dos Componentes Fortemente Conectados:")
        if strongly_connected:
            largest_strongly_connected = max(strongly_connected, key=len)
            subgraph_strongly = G.subgraph(largest_strongly_connected)
            fig_strong, ax_strong = plt.subplots()
            nx.draw(subgraph_strongly, with_labels=True, node_color='lightblue', edge_color='gray', ax=ax_strong)
            st.pyplot(fig_strong)
    
    weakly_connected = list(nx.weakly_connected_components(G))
    num_weakly_connected = len(weakly_connected)
    st.subheader("Componentes Fracamente Conectados")
    st.write(f"A rede contém {num_weakly_connected} componentes fracamente conectados.")
    
    with col2:
        st.write("Visualização de um dos Componentes Fracamente Conectados:")
        if weakly_connected:
            largest_weakly_connected = max(weakly_connected, key=len)
            subgraph_weakly = G.subgraph(largest_weakly_connected)
            fig_weak, ax_weak = plt.subplots()
            nx.draw(subgraph_weakly, with_labels=True, node_color='lightgreen', edge_color='gray', ax=ax_weak)
            st.pyplot(fig_weak)

elif opcao_visualizacao == 'Nós mais importantes por medidas de centralidade':
    st.header("Nós mais importantes por Medidas de Centralidade")
    
    degree_centrality = nx.degree_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    
    eigenvector_centrality = {}
    try:
        eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000, tol=1e-06)
    except nx.PowerIterationFailedConvergence:
        st.write("Erro: O cálculo da centralidade de eigenvector não convergiu. O grafo pode ser muito grande ou mal condicionado.")
        eigenvector_centrality = {}

    centrality_df = pd.DataFrame({
        'Degree Centrality': pd.Series(degree_centrality),
        'Closeness Centrality': pd.Series(closeness_centrality),
        'Betweenness Centrality': pd.Series(betweenness_centrality),
        'Eigenvector Centrality': pd.Series(eigenvector_centrality)
    })
    
    top_5_degree = centrality_df['Degree Centrality'].nlargest(5).reset_index().rename(columns={'index': 'Node', 'Degree Centrality': 'Degree Centrality'})
    top_5_closeness = centrality_df['Closeness Centrality'].nlargest(5).reset_index().rename(columns={'index': 'Node', 'Closeness Centrality': 'Closeness Centrality'})
    top_5_betweenness = centrality_df['Betweenness Centrality'].nlargest(5).reset_index().rename(columns={'index': 'Node', 'Betweenness Centrality': 'Betweenness Centrality'})
    top_5_eigenvector = centrality_df['Eigenvector Centrality'].nlargest(5).reset_index().rename(columns={'index': 'Node', 'Eigenvector Centrality': 'Eigenvector Centrality'})
    
    fig, axs = plt.subplots(2, 2, figsize=(14, 10), tight_layout=True)
    
    def plot_barh_with_values(ax, data, title, color):
        bars = ax.barh(data.index, data.values, color=color, edgecolor='black')
        ax.set_title(title)
        ax.set_xlabel(title)
        ax.invert_yaxis()
        for bar in bars:
            width = bar.get_width()
            ax.text(width / 2, bar.get_y() + bar.get_height() / 2, f'{width:.4f}', ha='center', va='center', fontsize=10, color='black')

    # Degree Centrality
    plot_barh_with_values(axs[0, 0], top_5_degree.set_index('Node')['Degree Centrality'], 'Top 5 Degree Centrality', 'skyblue')
    
    # Closeness Centrality
    plot_barh_with_values(axs[0, 1], top_5_closeness.set_index('Node')['Closeness Centrality'], 'Top 5 Closeness Centrality', 'lightgreen')
    
    # Betweenness Centrality
    plot_barh_with_values(axs[1, 0], top_5_betweenness.set_index('Node')['Betweenness Centrality'], 'Top 5 Betweenness Centrality', 'salmon')
    
    # Eigenvector Centrality
    if not top_5_eigenvector.empty:
        plot_barh_with_values(axs[1, 1], top_5_eigenvector.set_index('Node')['Eigenvector Centrality'], 'Top 5 Eigenvector Centrality', 'orange')
    else:
        axs[1, 1].barh([], [])
        axs[1, 1].set_title('Top 5 Eigenvector Centrality')
        axs[1, 1].set_xlabel('Eigenvector Centrality')
        axs[1, 1].text(0.5, 0.5, 'Não foi possível calcular a centralidade de eigenvector.', horizontalalignment='center', verticalalignment='center', transform=axs[1, 1].transAxes)
    
    st.pyplot(fig)