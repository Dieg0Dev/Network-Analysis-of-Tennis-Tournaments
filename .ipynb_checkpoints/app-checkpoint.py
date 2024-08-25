import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import torneios 

ano = 2023
st.title('Rede do Torneio')

st.sidebar.title('Aplique as Definições')
torneio = st.sidebar.selectbox('Selecione o Torneio',('Todos os Grand Slans', 'Australian Open', 'Roland Garros', 'Wimblendom', 'US Open'))
#physics=st.sidebar.checkbox('add physics interactivity?')
ano = st.sidebar.selectbox('Selecione o Ano',('2023', '2022'))

if torneio == 'Todos os Grand Slans':
  torneios.todos_func(ano)
  HtmlFile = open("html_files/todos.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 1200,width=1000)

if torneio == 'Australian Open':
  torneios.ao_func(ano)
  HtmlFile = open("html_files/ao.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 1200,width=1000)
  
if torneio == 'Roland Garros':
  torneios.fo_func(ano)
  HtmlFile = open("html_files/fo.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 1200,width=1000)

if torneio == 'Wimblendom':
  torneios.wb_func(ano)
  HtmlFile = open("html_files/wb.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 1200,width=1000)
  
if torneio == 'US Open':
  torneios.uo_func(ano)
  HtmlFile = open("html_files/uo.html", 'r', encoding='utf-8')
  source_code = HtmlFile.read() 
  components.html(source_code, height = 1200,width=1000)