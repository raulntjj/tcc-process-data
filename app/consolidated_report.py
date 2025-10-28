# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
from datetime import datetime

# --- Carregar Dados Processados ---
try:
    df_professores = pd.read_csv("./output/professores_processado.csv")
    df_supervisores = pd.read_csv("./output/supervisores_processado.csv")
    df_results_prof = pd.read_csv("./output/medias_professores.csv", index_col=0)
    df_results_sup = pd.read_csv("./output/medias_supervisores.csv", index_col=0)
    
    # Carregar dados de porcentagens se existirem
    try:
        df_percent_prof = pd.read_csv("./output/percentagens_professores.csv")
        df_percent_sup = pd.read_csv("./output/percentagens_supervisores.csv")
    except FileNotFoundError:
        df_percent_prof = None
        df_percent_sup = None
    
    # Carregar análise qualitativa se existir
    try:
        df_qual_prof = pd.read_csv("./output/analise_qualitativa_professores.csv")
        df_qual_sup = pd.read_csv("./output/analise_qualitativa_supervisores.csv")
    except FileNotFoundError:
        df_qual_prof = None
        df_qual_sup = None
    
    print("Dados processados carregados com sucesso.")
except FileNotFoundError as e:
    print(f"Erro: Arquivo não encontrado: {e}")
    exit()
except Exception as e:
    print(f"Erro ao carregar arquivos CSV: {e}")
    exit()

# --- Funções para Gerar Relatório ---
def generate_profile_summary(data, prefix, title):
    """Gera resumo do perfil dos participantes."""
    summary = []
    
    # P1.1 - Tempo de Serviço
    if f'{prefix}1.1_Tempo_Servico' in data.columns:
        col = f'{prefix}1.1_Tempo_Servico'
        clean_data = data.dropna(subset=[col])
        if not clean_data.empty:
            counts = clean_data[col].value_counts()
            percentages = (counts / len(clean_data) * 100).round(1)
            summary.append(f"Tempo de Serviço (N={len(clean_data)}):")
            for value, count in counts.items():
                pct = percentages[value]
                summary.append(f"  {value}: {count} ({pct}%)")
            summary.append("")
    
    # P1.2 - Segmentos
    if f'{prefix}1.2_Segmentos' in data.columns:
        col = f'{prefix}1.2_Segmentos'
        clean_data = data.dropna(subset=[col])
        if not clean_data.empty:
            counts = clean_data[col].value_counts()
            percentages = (counts / len(clean_data) * 100).round(1)
            summary.append(f"Segmentos de Atuação (N={len(clean_data)}):")
            for value, count in counts.items():
                pct = percentages[value]
                summary.append(f"  {value}: {count} ({pct}%)")
            summary.append("")
    
    # P1.3 - Conforto com Tecnologia
    if f'{prefix}1.3_Conforto_Tec' in data.columns:
        col = f'{prefix}1.3_Conforto_Tec'
        clean_data = data.dropna(subset=[col])
        if not clean_data.empty:
            counts = clean_data[col].value_counts()
            percentages = (counts / len(clean_data) * 100).round(1)
            summary.append(f"Conforto com Tecnologia (N={len(clean_data)}):")
            for value, count in counts.items():
                pct = percentages[value]
                summary.append(f"  {value}: {count} ({pct}%)")
            summary.append("")
    
    # P1.4 - Número de Turmas
    if f'{prefix}1.4_Num_Turmas' in data.columns:
        col = f'{prefix}1.4_Num_Turmas'
        clean_data = data.dropna(subset=[col])
        if not clean_data.empty:
            counts = clean_data[col].value_counts()
            percentages = (counts / len(clean_data) * 100).round(1)
            summary.append(f"Número de Turmas (N={len(clean_data)}):")
            for value, count in counts.items():
                pct = percentages[value]
                summary.append(f"  {value}: {count} ({pct}%)")
            summary.append("")
    
    # P1.5 - Número de Planos
    if f'{prefix}1.5_Num_Planos' in data.columns:
        col = f'{prefix}1.5_Num_Planos'
        clean_data = data.dropna(subset=[col])
        if not clean_data.empty:
            counts = clean_data[col].value_counts()
            percentages = (counts / len(clean_data) * 100).round(1)
            summary.append(f"Número de Planos/Cronogramas (N={len(clean_data)}):")
            for value, count in counts.items():
                pct = percentages[value]
                summary.append(f"  {value}: {count} ({pct}%)")
            summary.append("")
    
    # P1.6 - Outra Escola (apenas para professores)
    if prefix == 'P' and f'{prefix}1.6_Outra_Escola_Metodo' in data.columns:
        col = f'{prefix}1.6_Outra_Escola_Metodo'
        clean_data = data.dropna(subset=[col])
        if not clean_data.empty:
            counts = clean_data[col].value_counts()
            percentages = (counts / len(clean_data) * 100).round(1)
            summary.append(f"Atuação em Outras Escolas (N={len(clean_data)}):")
            for value, count in counts.items():
                pct = percentages[value]
                summary.append(f"  {value}: {count} ({pct}%)")
            summary.append("")
    
    return summary

def generate_likert_summary(df_means, title):
    """Gera resumo das médias Likert."""
    summary = []
    summary.append(f"{title}:")
    summary.append("Médias de Concordância (1=Discordo Totalmente, 5=Concordo Totalmente)")
    summary.append("-" * 80)
    
    for idx, row in df_means.iterrows():
        summary.append(f"{idx}:")
        for method in ['Manual', 'Planilha', 'PlanningApp']:
            if method in row and not pd.isna(row[method]):
                summary.append(f"  {method}: {row[method]:.2f}")
        summary.append("")
    
    return summary

def generate_qualitative_summary(df_qual, title):
    """Gera resumo da análise qualitativa."""
    if df_qual is None or df_qual.empty:
        return [f"{title}: Nenhum dado qualitativo disponível."]
    
    summary = []
    summary.append(f"{title}:")
    summary.append("Principais Temas Identificados")
    summary.append("-" * 50)
    
    # Agrupar por pergunta
    for pergunta in df_qual['Pergunta'].unique():
        pergunta_data = df_qual[df_qual['Pergunta'] == pergunta]
        summary.append(f"\n{pergunta}:")
        
        # Pegar os 5 temas mais frequentes
        top_themes = pergunta_data.nlargest(5, 'Frequencia')
        for _, row in top_themes.iterrows():
            summary.append(f"  {row['Palavra_Chave']}: {row['Frequencia']} menções ({row['Porcentagem']}%)")
    
    return summary

# --- Gerar Relatório Consolidado ---
print("Gerando relatório consolidado...")

report = []
report.append("=" * 80)
report.append("RELATÓRIO CONSOLIDADO - ANÁLISE DE DADOS TCC")
report.append("=" * 80)
report.append(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
report.append("")

# Seção 4.1 - Perfil dos Participantes
report.append("SEÇÃO 4.1 - PERFIL DOS PARTICIPANTES")
report.append("=" * 50)

# Professores
prof_profile = generate_profile_summary(df_professores, 'P', "PROFESSORES (N=28)")
report.extend(prof_profile)

# Supervisores
if not df_supervisores.empty:
    sup_profile = generate_profile_summary(df_supervisores, 'S', "SUPERVISORES (N=4)")
    report.extend(sup_profile)
else:
    report.append("SUPERVISORES: Nenhum dado disponível.")

# Seções 4.2 a 4.5 - Análise Comparativa
report.append("SEÇÕES 4.2 a 4.5 - ANÁLISE COMPARATIVA")
report.append("=" * 50)

# Médias dos professores
prof_likert = generate_likert_summary(df_results_prof, "MÉDIAS DE CONCORDÂNCIA - PROFESSORES")
report.extend(prof_likert)

# Médias dos supervisores
if not df_results_sup.empty:
    sup_likert = generate_likert_summary(df_results_sup, "MÉDIAS DE CONCORDÂNCIA - SUPERVISORES")
    report.extend(sup_likert)

# Seção 4.6 - Síntese Qualitativa
report.append("SEÇÃO 4.6 - SÍNTESE QUALITATIVA")
report.append("=" * 50)

# Análise qualitativa dos professores
prof_qual = generate_qualitative_summary(df_qual_prof, "ANÁLISE QUALITATIVA - PROFESSORES")
report.extend(prof_qual)

# Análise qualitativa dos supervisores
if df_qual_sup is not None:
    sup_qual = generate_qualitative_summary(df_qual_sup, "ANÁLISE QUALITATIVA - SUPERVISORES")
    report.extend(sup_qual)

# Resumo dos Ns utilizados
report.append("RESUMO DOS Ns UTILIZADOS NO CÁLCULO")
report.append("=" * 50)
report.append(f"Professores: {len(df_professores)} participantes")
if not df_supervisores.empty:
    report.append(f"Supervisores: {len(df_supervisores)} participantes")
else:
    report.append("Supervisores: 0 participantes")

# Salvar relatório
report_text = "\n".join(report)
with open("output/relatorio_consolidado.txt", "w", encoding="utf-8") as f:
    f.write(report_text)

print("Relatório consolidado salvo em: output/relatorio_consolidado.txt")

# --- Gerar CSV com dados essenciais para o TCC ---
print("Gerando dados essenciais para o TCC...")

# Dados essenciais para Seção 4.1
essential_data = []

# Professores - Perfil
prof_columns = ['P1.1_Tempo_Servico', 'P1.2_Segmentos', 'P1.3_Conforto_Tec', 'P1.4_Num_Turmas', 'P1.5_Num_Planos', 'P1.6_Outra_Escola_Metodo']
for col in prof_columns:
    if col in df_professores.columns:
        clean_data = df_professores.dropna(subset=[col])
        if not clean_data.empty:
            counts = clean_data[col].value_counts()
            percentages = (counts / len(clean_data) * 100).round(1)
            for value, count in counts.items():
                pct = percentages[value]
                essential_data.append({
                    'Categoria': 'Professores',
                    'Pergunta': col,
                    'Resposta': value,
                    'Contagem': count,
                    'Porcentagem': pct,
                    'Total_Respondentes': len(clean_data)
                })

# Supervisores - Perfil
if not df_supervisores.empty:
    sup_columns = ['S1.1_Funcao_Gestora', 'S1.2_Tempo_Gestao', 'S1.3_Outras_Plataformas']
    for col in sup_columns:
        if col in df_supervisores.columns:
            clean_data = df_supervisores.dropna(subset=[col])
            if not clean_data.empty:
                counts = clean_data[col].value_counts()
                percentages = (counts / len(clean_data) * 100).round(1)
                for value, count in counts.items():
                    pct = percentages[value]
                    essential_data.append({
                        'Categoria': 'Supervisores',
                        'Pergunta': col,
                        'Resposta': value,
                        'Contagem': count,
                        'Porcentagem': pct,
                        'Total_Respondentes': len(clean_data)
                    })

# Salvar dados essenciais
if essential_data:
    df_essential = pd.DataFrame(essential_data)
    df_essential.to_csv("output/dados_essenciais_tcc.csv", index=False)
    print("Dados essenciais salvos em: output/dados_essenciais_tcc.csv")

print("\n" + "=" * 80)
print("RELATÓRIO CONSOLIDADO GERADO COM SUCESSO")
print("=" * 80)
print("Arquivos gerados:")
print("- output/relatorio_consolidado.txt")
print("- output/dados_essenciais_tcc.csv")
print("- Gráficos com porcentagens na pasta graficos_tcc/")
print("- Análise qualitativa na pasta output/")
