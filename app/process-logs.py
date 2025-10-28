# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
import os
import json

# --- Configurações Globais ---
sns.set_theme(style="whitegrid")
plt.style.use('seaborn-v0_8-colorblind')  # Estilo de cores acessível
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11  # Ajustar tamanho da fonte se necessário
plt.rcParams['figure.autolayout'] = True  # Tenta ajustar layout automaticamente
plt.rcParams['savefig.dpi'] = 150  # Aumentar resolução das imagens salvas

# Criar diretório para salvar gráficos se não existir
output_dir = "graficos_tcc"
os.makedirs(output_dir, exist_ok=True)

# --- Carregar Dados Processados ---
try:
    df = pd.read_csv('./input/respostas.csv')  # Ou 'Avaliação da Evolução dos Métodos de Planejamento de Aula.csv' se o nome for exato
    print("CSV de respostas carregado com sucesso.")
except FileNotFoundError:
    print("Erro: CSV file not found. Make sure 'respostas.csv' or 'Avaliação da Evolução dos Métodos de Planejamento de Aula.csv' is in the input directory.")
    exit()
except Exception as e:
    print(f"Erro ao carregar arquivo CSV: {e}")
    exit()

# Renomear colunas relevantes (baseado no primeiro script)
df = df.rename(columns={
    'Qual função você exerce?': 'Funcao',
    '2.6 - No método MANUAL (papel), qual era o tempo médio estimado que você gastava para elaborar o planejamento de UMA aula? ': 'P2.6_Tempo_Aula_Manual',
    '2.7 - No método com PLANILHAS online, qual era o tempo médio estimado que você gastava para elaborar o planejamento de UMA aula?': 'P2.7_Tempo_Aula_Planilha'
})

# Filtrar apenas professores
df_professores = df[df['Funcao'] == 'Professor'].copy()

# Carregar logs.json
try:
    with open('./input/logs.json', 'r', encoding='utf-8') as f:
        logs_data = json.load(f)
    print("logs.json carregado com sucesso.")
except FileNotFoundError:
    print("Erro: logs.json not found in the input directory.")
    exit()
except Exception as e:
    print(f"Erro ao carregar logs.json: {e}")
    exit()

# Extrair métricas de professores do logs.json
user_metrics = logs_data.get('payload', {}).get('user_metrics', [])
professores_logs = [user for user in user_metrics if user.get('predominantly_role') == 'Professor' and user.get('planning_count', 0) > 0]

# --- Análise dos Logs ---
print("\n--- Análise dos Logs (PlanningApp) ---")
if professores_logs:
    num_professores = len(professores_logs)
    total_plannings = sum(user['planning_count'] for user in professores_logs)
    total_seconds = sum(user['total_seconds'] for user in professores_logs)
    overall_avg_seconds = logs_data.get('payload', {}).get('overall_metrics', {}).get('average_seconds', 0)
    avg_minutes = overall_avg_seconds / 60
    print(f"Número de professores: {num_professores}")
    print(f"Planejamentos totais: {total_plannings}")
    print(f"Segundos totais: {total_seconds}")
    print(f"Média de segundos por planejamento (geral): {overall_avg_seconds:.2f} segundos ({avg_minutes:.2f} minutos)")
    
    # Distribuição de tempos médios por usuário
    avg_seconds_list = [user['average_seconds'] for user in professores_logs]
    print(f"Média dos tempos médios por professor: {np.mean(avg_seconds_list):.2f} segundos")
    print(f"Mediana dos tempos médios por professor: {np.median(avg_seconds_list):.2f} segundos")
    print(f"Mínimo: {np.min(avg_seconds_list):.2f} segundos")
    print(f"Máximo: {np.max(avg_seconds_list):.2f} segundos")
else:
    print("Nenhum dado de professores encontrado nos logs.")

# Converter average_seconds para minutos e categorizar
categories = ['Menos de 10 minutos', 'Entre 10 e 20 minutos', 'Entre 20 e 30 minutos', 'Entre 30 e 45 minutos', 'Mais de 45 minutos']
def categorize_time(seconds):
    minutes = seconds / 60
    if minutes < 10:
        return categories[0]
    elif 10 <= minutes < 20:
        return categories[1]
    elif 20 <= minutes < 30:
        return categories[2]
    elif 30 <= minutes < 45:
        return categories[3]
    else:
        return categories[4]

planning_app_times = [categorize_time(user['average_seconds']) for user in professores_logs]
df_planning_app = pd.DataFrame({'Tempo': planning_app_times})

# Imprimir distribuição em porcentagem para PlanningApp
print("\nDistribuição de Tempos (PlanningApp):")
print(df_planning_app['Tempo'].value_counts(normalize=True).map("{:.1%}".format))

# --- Funções Auxiliares de Plotagem ---
def save_plot(filename, title):
    """Salva a figura atual no diretório de saída."""
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, bbox_inches='tight')
    print(f"Gráfico '{title}' salvo como {filepath}")
    plt.close()  # Fechar figura

def plot_time_comparison_pie(manual_series, planilha_series, planning_app_series, title, filename, order):
    """Gera gráficos de pizza com porcentagens para comparação de tempos."""
    # Calcular porcentagens
    manual_pct = manual_series.value_counts(normalize=True).reindex(order).fillna(0) * 100
    planilha_pct = planilha_series.value_counts(normalize=True).reindex(order).fillna(0) * 100
    planning_app_pct = planning_app_series.value_counts(normalize=True).reindex(order).fillna(0) * 100

    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(title, fontsize=16)

    # Pizza para Manual
    axs[0].pie(manual_pct, labels=[textwrap.fill(label, width=15) for label in manual_pct.index], autopct='%1.1f%%', startangle=90)
    axs[0].set_title('Manual')

    # Pizza para Planilha
    axs[1].pie(planilha_pct, labels=[textwrap.fill(label, width=15) for label in planilha_pct.index], autopct='%1.1f%%', startangle=90)
    axs[1].set_title('Planilha')

    # Pizza para PlanningApp
    axs[2].pie(planning_app_pct, labels=[textwrap.fill(label, width=15) for label in planning_app_pct.index], autopct='%1.1f%%', startangle=90)
    axs[2].set_title('PlanningApp')

    save_plot(filename, title)

# --- Geração do Gráfico de Comparação de Tempos ---
print("\n--- Gerando Gráfico de Comparação de Tempos ---")
order_tempo_aula = ['Menos de 10 minutos', 'Entre 10 e 20 minutos', 'Entre 20 e 30 minutos', 'Entre 30 e 45 minutos', 'Mais de 45 minutos']

# Extrair séries de tempos (remover NaNs)
manual_times = df_professores['P2.6_Tempo_Aula_Manual'].dropna()
planilha_times = df_professores['P2.7_Tempo_Aula_Planilha'].dropna()
planning_app_times_series = df_planning_app['Tempo']

# Imprimir distribuições em porcentagem para Manual e Planilha
print("\nDistribuição de Tempos (Manual):")
print(manual_times.value_counts(normalize=True).map("{:.1%}".format))
print("\nDistribuição de Tempos (Planilha):")
print(planilha_times.value_counts(normalize=True).map("{:.1%}".format))

if manual_times.empty or planilha_times.empty or planning_app_times_series.empty:
    print("Aviso: Dados insuficientes para gerar o gráfico de comparação de tempos.")
else:
    plot_time_comparison_pie(manual_times, planilha_times, planning_app_times_series,
                             'Comparação do Tempo Estimado por Planejamento de Aula (Professores)',
                             '21_tempo_comparacao_pie.png', order_tempo_aula)

print("\n--- Geração do Gráfico de Comparação de Tempos Concluída ---")
print(f"O gráfico foi salvo na pasta: {output_dir}")