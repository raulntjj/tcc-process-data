# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
import os

# --- Configurações Globais ---
sns.set_theme(style="whitegrid")
plt.style.use('seaborn-v0_8-colorblind')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['figure.autolayout'] = True
plt.rcParams['savefig.dpi'] = 150

# Criar diretório para salvar gráficos se não existir
output_dir = "graficos_tcc"
os.makedirs(output_dir, exist_ok=True)

# --- Carregar Dados Processados ---
try:
    df_professores = pd.read_csv("./output/professores_processado.csv")
    df_supervisores = pd.read_csv("./output/supervisores_processado.csv")
    print("Dados processados carregados com sucesso.")
except FileNotFoundError:
    print("Erro: Arquivos CSV processados não encontrados. Execute o process.py primeiro.")
    exit()
except Exception as e:
    print(f"Erro ao carregar arquivos CSV: {e}")
    exit()

# --- Funções Auxiliares ---
def save_plot(filename, title):
    """Salva a figura atual no diretório de saída."""
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, bbox_inches='tight')
    print(f"Gráfico '{title}' salvo como {filepath}")
    plt.close()

def calculate_percentages(data, column, title):
    """Calcula porcentagens para uma coluna específica."""
    if column not in data.columns or data[column].isnull().all():
        print(f"Aviso: Coluna '{column}' não encontrada ou vazia.")
        return None, None
    
    clean_data = data.dropna(subset=[column])
    if clean_data.empty:
        print(f"Aviso: Sem dados válidos para {column} após remover NaNs.")
        return None, None
    
    counts = clean_data[column].value_counts()
    percentages = (counts / len(clean_data) * 100).round(1)
    
    print(f"\n{title}:")
    print(f"Total de respondentes: {len(clean_data)}")
    print("Distribuição:")
    for value, count in counts.items():
        pct = percentages[value]
        print(f"  {value}: {count} ({pct}%)")
    
    return counts, percentages

def plot_percentage_chart(data, column, title, filename, plot_type='bar', order=None, xlabel=None):
    """Gera gráficos com porcentagens para perfil."""
    if column not in data.columns or data[column].isnull().all():
        print(f"Aviso: Coluna '{column}' não encontrada ou vazia. Gráfico '{title}' não gerado.")
        return

    plt.figure(figsize=(12, 8))
    plt.suptitle(title, fontsize=16, y=1.02)
    clean_data = data.dropna(subset=[column])

    if clean_data.empty:
        print(f"Aviso: Sem dados válidos para plotar para {column} após remover NaNs.")
        plt.close()
        return

    counts = clean_data[column].value_counts()
    percentages = (counts / len(clean_data) * 100).round(1)

    if plot_type == 'pie':
        labels = [f'{label}\n({value} - {percentages[label]:.1f}%)' for label, value in counts.items()]
        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85, textprops={'fontsize': 10})
        plt.title("Distribuição Percentual", fontsize=12)

    elif plot_type == 'bar':
        if order:
            valid_order = [o for o in order if o in clean_data[column].unique()]
            counts = counts.reindex(valid_order).fillna(0)
            percentages = percentages.reindex(valid_order).fillna(0)

        if not counts.empty:
            ax = sns.barplot(x=counts.index, y=counts.values, palette='viridis')
            ax.set_title("Contagem Absoluta e Percentual", fontsize=12)
            ax.set_ylabel('Número de Participantes', fontsize=12)
            ax.set_xlabel(xlabel if xlabel else column.split('_', 1)[-1].replace('_', ' '), fontsize=12)

            # Add counts and percentages above bars
            for container in ax.containers:
                labels = []
                for i, v in enumerate(container.datavalues):
                    if i < len(percentages):
                        pct_value = percentages.iloc[i] if hasattr(percentages, 'iloc') else list(percentages.values)[i]
                        labels.append(f'{int(v)}\n({pct_value:.1f}%)')
                    else:
                        labels.append(f'{int(v)}')
                ax.bar_label(container, labels=labels, label_type='edge', padding=3, fontsize=9)

            # Wrap long x-axis labels if necessary
            if max(len(str(label)) for label in counts.index) > 15:
                ax.set_xticklabels([textwrap.fill(str(label), width=15) for label in counts.index], rotation=0, ha='center')
            else:
                ax.set_xticklabels(counts.index, rotation=0, ha='center')
        else:
            print(f"Aviso: Sem dados para plotar barras para {column}")
            plt.close()
            return

    save_plot(filename, title)

def create_percentage_summary(data, columns, title, filename):
    """Cria um resumo de porcentagens para múltiplas colunas."""
    summary_data = []
    
    for col in columns:
        if col in data.columns and not data[col].isnull().all():
            clean_data = data.dropna(subset=[col])
            if not clean_data.empty:
                counts = clean_data[col].value_counts()
                percentages = (counts / len(clean_data) * 100).round(1)
                
                for value, count in counts.items():
                    pct = percentages[value]
                    summary_data.append({
                        'Pergunta': col,
                        'Resposta': value,
                        'Contagem': count,
                        'Porcentagem': pct,
                        'Total_Respondentes': len(clean_data)
                    })
    
    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_csv(f"output/{filename}", index=False)
        print(f"Resumo de porcentagens salvo em: output/{filename}")
        return df_summary
    else:
        print(f"Nenhum dado encontrado para {title}")
        return None

# --- Análise de Porcentagens para Professores ---
print("\n" + "="*60)
print("ANÁLISE DE PORCENTAGENS - PROFESSORES (N=28)")
print("="*60)

# P1.1 - Tempo de Serviço
order_tempo_srv = ['Menos de 2 anos', 'Entre 2 e 5 anos', 'Entre 6 e 10 anos', 'Mais de 10 anos']
counts, percentages = calculate_percentages(df_professores, 'P1.1_Tempo_Servico', 'P1.1 - Tempo de Serviço')
plot_percentage_chart(df_professores, 'P1.1_Tempo_Servico', 'Professores: Tempo de Serviço (com Porcentagens)', '01_prof_tempo_servico_pct.png', order=order_tempo_srv, xlabel="Tempo de Serviço")

# P1.2 - Segmentos
counts, percentages = calculate_percentages(df_professores, 'P1.2_Segmentos', 'P1.2 - Segmentos de Atuação')
plot_percentage_chart(df_professores, 'P1.2_Segmentos', 'Professores: Segmentos de Atuação (com Porcentagens)', '02_prof_segmentos_pct.png', plot_type='pie')

# P1.3 - Conforto com Tecnologia
order_conforto = ['Muito baixo', 'Baixo', 'Médio', 'Alto', 'Muito alto']
counts, percentages = calculate_percentages(df_professores, 'P1.3_Conforto_Tec', 'P1.3 - Conforto com Tecnologia')
plot_percentage_chart(df_professores, 'P1.3_Conforto_Tec', 'Professores: Conforto com Tecnologia (com Porcentagens)', '03_prof_conforto_tec_pct.png', order=order_conforto, xlabel="Nível de Conforto")

# P1.4 - Número de Turmas
order_turmas = ['1 a 3 turmas', '4 a 6 turmas', '7 a 9 turmas', '10 ou mais turmas']
counts, percentages = calculate_percentages(df_professores, 'P1.4_Num_Turmas', 'P1.4 - Número de Turmas')
plot_percentage_chart(df_professores, 'P1.4_Num_Turmas', 'Professores: Número de Turmas (com Porcentagens)', '04_prof_num_turmas_pct.png', order=order_turmas, xlabel="Número de Turmas")

# P1.5 - Número de Planos
order_planos = ['1 a 4 diários', '5 a 8 diários', '9 a 12 diários', '13 ou mais diários']
counts, percentages = calculate_percentages(df_professores, 'P1.5_Num_Planos', 'P1.5 - Número de Planos/Cronogramas')
plot_percentage_chart(df_professores, 'P1.5_Num_Planos', 'Professores: Número de Planos/Cronogramas (com Porcentagens)', '05_prof_num_planos_pct.png', order=order_planos, xlabel="Número de Planos")

# P1.6 - Outra Escola
counts, percentages = calculate_percentages(df_professores, 'P1.6_Outra_Escola_Metodo', 'P1.6 - Atuação em Outras Escolas')
plot_percentage_chart(df_professores, 'P1.6_Outra_Escola_Metodo', 'Professores: Atuação em Outras Escolas (com Porcentagens)', '06_prof_outra_escola_pct.png', plot_type='bar', xlabel="Método na Outra Escola")

# --- Análise de Porcentagens para Supervisores ---
print("\n" + "="*60)
print("ANÁLISE DE PORCENTAGENS - SUPERVISORES (N=4)")
print("="*60)

if not df_supervisores.empty:
    # S1.1 - Função
    counts, percentages = calculate_percentages(df_supervisores, 'S1.1_Funcao_Gestora', 'S1.1 - Função na Equipe Gestora')
    plot_percentage_chart(df_supervisores, 'S1.1_Funcao_Gestora', 'Supervisores: Função na Equipe Gestora (com Porcentagens)', '07_sup_funcao_pct.png', plot_type='pie')

    # S1.2 - Tempo na Gestão
    order_tempo_gest = ['Menos de 2 anos', 'Entre 2 e 5 anos', 'Entre 5 e 10 anos', 'Mais de 10 anos']
    counts, percentages = calculate_percentages(df_supervisores, 'S1.2_Tempo_Gestao', 'S1.2 - Tempo no Cargo de Gestão')
    plot_percentage_chart(df_supervisores, 'S1.2_Tempo_Gestao', 'Supervisores: Tempo no Cargo (com Porcentagens)', '08_sup_tempo_gestao_pct.png', order=order_tempo_gest, xlabel="Tempo no Cargo")

    # S1.3 - Experiência Outras Plataformas
    counts, percentages = calculate_percentages(df_supervisores, 'S1.3_Outras_Plataformas', 'S1.3 - Experiência com Outras Plataformas')
    plot_percentage_chart(df_supervisores, 'S1.3_Outras_Plataformas', 'Supervisores: Uso de Outras Plataformas (com Porcentagens)', '09_sup_outras_plat_pct.png', plot_type='pie')
else:
    print("Aviso: Nenhum dado de supervisor encontrado para análise de porcentagens.")

# --- Análise de Distribuição Likert (Opcional) ---
print("\n" + "="*60)
print("ANÁLISE DE DISTRIBUIÇÃO LIKERT - PERGUNTAS CHAVE")
print("="*60)

def analyze_likert_distribution(data, column, title):
    """Analisa a distribuição de respostas Likert."""
    if column not in data.columns or data[column].isnull().all():
        return None
    
    clean_data = data.dropna(subset=[column])
    if clean_data.empty:
        return None
    
    counts = clean_data[column].value_counts().sort_index()
    percentages = (counts / len(clean_data) * 100).round(1)
    
    print(f"\n{title}:")
    print(f"Total de respondentes: {len(clean_data)}")
    print("Distribuição:")
    for value, count in counts.items():
        pct = percentages[value]
        print(f"  {value}: {count} ({pct}%)")
    
    return counts, percentages

# Análise de perguntas Likert importantes para professores
likert_cols_prof = [col for col in df_professores.columns if any(m in col for m in ['_Manual', '_Planilha', '_PlanningApp']) and not col.startswith('P2.6') and not col.startswith('P2.7')]

# Perguntas chave para análise de distribuição
key_questions_prof = [
    'P3.6_Satisfacao_Geral_PlanningApp',  # Satisfação geral com PlanningApp
    'P5.1_Reduz_Estresse_PlanningApp',    # Reduz estresse com PlanningApp
    'P5.2_Causa_Frustracao_PlanningApp'   # Causa frustração com PlanningApp
]

for col in key_questions_prof:
    if col in df_professores.columns:
        analyze_likert_distribution(df_professores, col, f"Distribuição - {col}")

# --- Criar Resumos de Porcentagens ---
print("\n" + "="*60)
print("CRIANDO RESUMOS DE PORCENTAGENS")
print("="*60)

# Resumo para professores
prof_columns = ['P1.1_Tempo_Servico', 'P1.2_Segmentos', 'P1.3_Conforto_Tec', 'P1.4_Num_Turmas', 'P1.5_Num_Planos', 'P1.6_Outra_Escola_Metodo']
create_percentage_summary(df_professores, prof_columns, "Resumo de Porcentagens - Professores", "percentagens_professores.csv")

# Resumo para supervisores
if not df_supervisores.empty:
    sup_columns = ['S1.1_Funcao_Gestora', 'S1.2_Tempo_Gestao', 'S1.3_Outras_Plataformas']
    create_percentage_summary(df_supervisores, sup_columns, "Resumo de Porcentagens - Supervisores", "percentagens_supervisores.csv")

print("\n" + "="*60)
print("ANÁLISE DE PORCENTAGENS CONCLUÍDA")
print("="*60)
print(f"Gráficos com porcentagens salvos na pasta: {output_dir}")
print("Resumos de porcentagens salvos na pasta: output/")
