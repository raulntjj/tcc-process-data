# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
import os

# --- Configurações Globais ---
sns.set_theme(style="whitegrid")
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

# --- Funções para Análise Qualitativa ---
def clean_text(text):
    """Limpa e normaliza texto para análise."""
    if pd.isna(text) or text == '':
        return ''
    
    # Converter para string e remover caracteres especiais
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_keywords(text, min_length=3):
    """Extrai palavras-chave de um texto."""
    if not text:
        return []
    
    # Palavras comuns em português para filtrar
    stop_words = {
        'que', 'para', 'com', 'uma', 'dos', 'das', 'pelo', 'pela', 'são', 'mais',
        'muito', 'bem', 'também', 'sistema', 'planejamento', 'aula', 'aulas',
        'professor', 'professores', 'escola', 'tempo', 'fácil', 'difícil',
        'novo', 'antigo', 'método', 'métodos', 'uso', 'usar', 'usado'
    }
    
    words = text.split()
    keywords = [word for word in words if len(word) >= min_length and word not in stop_words]
    return keywords

def analyze_open_ended_responses(data, columns, title_prefix):
    """Analisa respostas abertas e extrai temas principais."""
    print(f"\n{'='*60}")
    print(f"ANÁLISE QUALITATIVA - {title_prefix}")
    print(f"{'='*60}")
    
    all_keywords = []
    response_analysis = {}
    
    for col in columns:
        if col in data.columns:
            print(f"\n{col}:")
            responses = data[col].dropna().tolist()
            valid_responses = [r for r in responses if str(r).strip() and str(r) != '']
            
            if valid_responses:
                print(f"  Total de respostas: {len(valid_responses)}")
                
                # Extrair palavras-chave de todas as respostas
                col_keywords = []
                for response in valid_responses:
                    cleaned = clean_text(response)
                    keywords = extract_keywords(cleaned)
                    col_keywords.extend(keywords)
                    all_keywords.extend(keywords)
                
                # Contar frequência das palavras-chave
                keyword_counts = Counter(col_keywords)
                most_common = keyword_counts.most_common(10)
                
                print("  Palavras-chave mais frequentes:")
                for word, count in most_common:
                    percentage = (count / len(valid_responses)) * 100
                    print(f"    {word}: {count} ({percentage:.1f}%)")
                
                response_analysis[col] = {
                    'total_responses': len(valid_responses),
                    'keywords': dict(most_common),
                    'responses': valid_responses
                }
            else:
                print("  Nenhuma resposta válida encontrada.")
    
    return response_analysis, all_keywords

def create_keyword_visualization(keyword_counts, title, filename):
    """Cria visualização das palavras-chave mais frequentes."""
    if not keyword_counts:
        print(f"Aviso: Nenhuma palavra-chave encontrada para {title}")
        return
    
    # Pegar as 15 palavras mais frequentes
    top_keywords = dict(keyword_counts.most_common(15))
    
    plt.figure(figsize=(12, 8))
    words = list(top_keywords.keys())
    counts = list(top_keywords.values())
    
    # Criar gráfico de barras horizontais
    y_pos = np.arange(len(words))
    bars = plt.barh(y_pos, counts, color='skyblue', alpha=0.7)
    
    plt.yticks(y_pos, words)
    plt.xlabel('Frequência de Menção')
    plt.title(f'{title}\nPalavras-chave Mais Frequentes')
    plt.gca().invert_yaxis()
    
    # Adicionar valores nas barras
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    
    # Salvar gráfico
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, bbox_inches='tight')
    print(f"Gráfico '{title}' salvo como {filepath}")
    plt.close()

def save_qualitative_summary(analysis, title, filename):
    """Salva resumo da análise qualitativa em CSV."""
    summary_data = []
    
    for question, data in analysis.items():
        for keyword, count in data['keywords'].items():
            percentage = (count / data['total_responses']) * 100
            summary_data.append({
                'Pergunta': question,
                'Palavra_Chave': keyword,
                'Frequencia': count,
                'Porcentagem': round(percentage, 1),
                'Total_Respostas': data['total_responses']
            })
    
    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        df_summary = df_summary.sort_values(['Pergunta', 'Frequencia'], ascending=[True, False])
        df_summary.to_csv(f"output/{filename}", index=False)
        print(f"Resumo qualitativo salvo em: output/{filename}")
        return df_summary
    else:
        print(f"Nenhum dado qualitativo encontrado para {title}")
        return None

# --- Análise Qualitativa para Professores ---
prof_open_ended_cols = [col for col in df_professores.columns if col.startswith('P6.')]
prof_analysis, prof_keywords = analyze_open_ended_responses(df_professores, prof_open_ended_cols, "PROFESSORES")

# Visualização das palavras-chave dos professores
if prof_keywords:
    prof_keyword_counts = Counter(prof_keywords)
    create_keyword_visualization(prof_keyword_counts, "Professores: Análise de Respostas Abertas", "qualitative_prof_keywords.png")

# Salvar resumo qualitativo dos professores
save_qualitative_summary(prof_analysis, "Professores", "analise_qualitativa_professores.csv")

# --- Análise Qualitativa para Supervisores ---
if not df_supervisores.empty:
    sup_open_ended_cols = [col for col in df_supervisores.columns if col.startswith('S7.')]
    sup_analysis, sup_keywords = analyze_open_ended_responses(df_supervisores, sup_open_ended_cols, "SUPERVISORES")
    
    # Visualização das palavras-chave dos supervisores
    if sup_keywords:
        sup_keyword_counts = Counter(sup_keywords)
        create_keyword_visualization(sup_keyword_counts, "Supervisores: Análise de Respostas Abertas", "qualitative_sup_keywords.png")
    
    # Salvar resumo qualitativo dos supervisores
    save_qualitative_summary(sup_analysis, "Supervisores", "analise_qualitativa_supervisores.csv")
else:
    print("\nAviso: Nenhum dado de supervisor encontrado para análise qualitativa.")

# --- Análise de Sentimentos (Palavras-chave por método) ---
print(f"\n{'='*60}")
print("ANÁLISE DE SENTIMENTOS POR MÉODO")
print(f"{'='*60}")

def analyze_sentiment_words(data, sentiment_cols, title):
    """Analisa palavras de sentimento para diferentes métodos."""
    print(f"\n{title}:")
    
    for col in sentiment_cols:
        if col in data.columns:
            responses = data[col].dropna().tolist()
            valid_responses = [r for r in responses if str(r).strip() and str(r) != '']
            
            if valid_responses:
                print(f"\n{col}:")
                print(f"  Total de respostas: {len(valid_responses)}")
                
                # Categorizar sentimentos
                positive_words = ['bom', 'ótimo', 'excelente', 'fácil', 'prático', 'eficiente', 'organizado', 'rápido', 'simples', 'agilidade', 'alívio', 'esperança', 'possibilidades', 'revolucionário', 'objetividade', 'conforto', 'eficiência', 'praticidade', 'comodidade', 'segurança']
                negative_words = ['difícil', 'complicado', 'cansativo', 'estressante', 'frustrante', 'trabalhoso', 'exaustivo', 'desgastante', 'retrocesso', 'obsolescência', 'ódio', 'insatisfação', 'incerteza', 'insegurança', 'dúvidas', 'cansaço', 'desânimo', 'frustração', 'exaustão', 'improvável']
                neutral_words = ['normal', 'médio', 'neutro', 'indiferente', 'aceitável', 'regular', 'moderado']
                
                positive_count = 0
                negative_count = 0
                neutral_count = 0
                
                for response in valid_responses:
                    cleaned = clean_text(response)
                    words = cleaned.split()
                    
                    pos_score = sum(1 for word in words if word in positive_words)
                    neg_score = sum(1 for word in words if word in negative_words)
                    neu_score = sum(1 for word in words if word in neutral_words)
                    
                    if pos_score > neg_score and pos_score > neu_score:
                        positive_count += 1
                    elif neg_score > pos_score and neg_score > neu_score:
                        negative_count += 1
                    else:
                        neutral_count += 1
                
                total = positive_count + negative_count + neutral_count
                if total > 0:
                    print(f"  Sentimentos:")
                    print(f"    Positivo: {positive_count} ({(positive_count/total)*100:.1f}%)")
                    print(f"    Negativo: {negative_count} ({(negative_count/total)*100:.1f}%)")
                    print(f"    Neutro: {neutral_count} ({(neutral_count/total)*100:.1f}%)")

# Análise de sentimentos para professores
sentiment_cols_prof = ['P6.3_Sentimento_Manual', 'P6.4_Sentimento_Planilha', 'P6.5_Sentimento_PlanningApp']
analyze_sentiment_words(df_professores, sentiment_cols_prof, "Sentimentos dos Professores por Método")

print(f"\n{'='*60}")
print("ANÁLISE QUALITATIVA CONCLUÍDA")
print(f"{'='*60}")
print(f"Gráficos de análise qualitativa salvos na pasta: {output_dir}")
print("Resumos qualitativos salvos na pasta: output/")
