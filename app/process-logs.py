# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
import os

# Configurações
sns.set_theme(style="whitegrid")
plt.rcParams['font.size'] = 11
plt.rcParams['savefig.dpi'] = 150
output_dir = "graficos_tcc"
os.makedirs(output_dir, exist_ok=True)

# --- 1. DEFINIR CATEGORIAS DE TEMPO (PADRÃO FINAL) ---
categorias = [
    'Menos de 10 minutos',
    'Entre 10 e 20 minutos',
    'Entre 20 e 30 minutos',
    'Entre 30 e 45 minutos',
    'Mais de 45 minutos'
]

# --- 2. MAPEAMENTO DE VARIANTES (para aceitar tudo que vier no CSV) ---
mapeamento_tempo = {
    'Menos de 10 minutos': 'Menos de 10 minutos',
    'Menos de 10 min': 'Menos de 10 minutos',
    'menos de 10 minutos': 'Menos de 10 minutos',
    'Entre 10 e 20 minutos': 'Entre 10 e 20 minutos',
    '10 a 20 minutos': 'Entre 10 e 20 minutos',
    'Entre 10 e 20 min': 'Entre 10 e 20 minutos',
    'entre 10 e 20 minutos': 'Entre 10 e 20 minutos',
    'Entre 20 e 30 minutos': 'Entre 20 e 30 minutos',
    '20 a 30 minutos': 'Entre 20 e 30 minutos',
    'Entre 30 e 45 minutos': 'Entre 30 e 45 minutos',
    '30 a 45 minutos': 'Entre 30 e 45 minutos',
    'Mais de 45 minutos': 'Mais de 45 minutos',
    'mais de 45 minutos': 'Mais de 45 minutos',
    'Mais de 45 min': 'Mais de 45 minutos',
}

# --- 3. CARREGAR CSV ---
csv_path = './input/Avaliação da Evolução dos Métodos de Planejamento de Aula.csv'
if not os.path.exists(csv_path):
    csv_path = './input/respostas.csv'

df = pd.read_csv(csv_path)
print(f"CSV carregado: {len(df)} respostas")

# Renomear colunas
df = df.rename(columns={
    'Qual função você exerce?': 'Funcao',
    '2.6 - No método MANUAL (papel), qual era o tempo médio estimado que você gastava para elaborar o planejamento de UMA aula? ': 'P2.6_Tempo_Aula_Manual',
    '2.7 - No método com PLANILHAS online, qual era o tempo médio estimado que você gastava para elaborar o planejamento de UMA aula?': 'P2.7_Tempo_Aula_Planilha'
})

professores = df[df['Funcao'] == 'Professor'].copy()
print(f"Professores no CSV: {len(professores)}")

# --- 4. PADRONIZAR TEMPOS DO CSV ---
def padronizar_tempo(valor):
    if pd.isna(valor):
        return None
    valor_str = str(valor).strip()
    return mapeamento_tempo.get(valor_str, None)

manual_raw = professores['P2.6_Tempo_Aula_Manual'].apply(padronizar_tempo)
planilha_raw = professores['P2.7_Tempo_Aula_Planilha'].apply(padronizar_tempo)

manual = manual_raw.dropna().tolist()
planilha = planilha_raw.dropna().tolist()

print(f"Respostas válidas após mapeamento - Manual: {len(manual)} | Planilha: {len(planilha)}")

# --- 5. CARREGAR LOGS.JSON ---
with open('./input/logs.json', 'r', encoding='utf-8') as f:
    logs = json.load(f)

user_metrics = logs['payload']['user_metrics']
overall = logs['payload']['overall_metrics']

print(f"Usuários no logs: {len(user_metrics)}")
print(f"Média geral (todos): {overall['average_seconds']:.1f}s → {overall['average_seconds']/60:.1f} min")

# --- 6. Filtrar professores válidos ---
prof_logs = [
    u for u in user_metrics
    if (u.get('owner', {}).get('predominantly_role') == 'Professor'
        and u.get('planning_count', 0) > 0
        and u.get('average_seconds') is not None
        and u.get('average_seconds', 0) > 0)
]

print(f"Professores com logs válidos: {len(prof_logs)}")

# --- 7. Categor...
def categorizar_minutos(minutos):
    if minutos < 10: return categorias[0]
    elif minutos < 20: return categorias[1]
    elif minutos < 30: return categorias[2]
    elif minutos < 45: return categorias[3]
    else: return categorias[4]

planning_individual = [
    categorizar_minutos(u['average_seconds'] / 60)
    for u in prof_logs
]

# --- 8. CÁLCULO DAS MÉDIAS EM MINUTOS ---
def tempo_para_minutos(categoria):
    if categoria == 'Menos de 10 minutos': return 5
    elif categoria == 'Entre 10 e 20 minutos': return 15
    elif categoria == 'Entre 20 e 30 minutos': return 25
    elif categoria == 'Entre 30 e 45 minutos': return 37.5
    elif categoria == 'Mais de 45 minutos': return 60
    return None

# Média estimada Manual e Planilha (em minutos)
media_manual_min = pd.Series([tempo_para_minutos(x) for x in manual]).mean()
media_planilha_min = pd.Series([tempo_para_minutos(x) for x in planilha]).mean()

# Média real PlanningApp (por professor)
media_planning_individual_min = sum(u['average_seconds'] for u in prof_logs) / sum(u['planning_count'] for u in prof_logs) / 60

# Média geral (overall)
media_geral_min = overall['average_seconds'] / 60

print(f"\nMédias calculadas:")
print(f"  Manual (estimado): {media_manual_min:.1f} min")
print(f"  Planilha (estimado): {media_planilha_min:.1f} min")
print(f"  PlanningApp (média ponderada por professor): {media_planning_individual_min:.1f} min")
print(f"  PlanningApp (geral): {media_geral_min:.1f} min")

# --- 9. FUNÇÃO DE PIZZA ---
def gerar_pizza(dados, titulo, arquivo, cores=None):
    if not dados:
        print(f"[AVISO] Sem dados válidos para: {titulo}")
        return

    contagem = pd.Series(dados).value_counts().reindex(categorias, fill_value=0)
    if contagem.sum() == 0:
        print(f"[AVISO] Soma zero após reindex em: {titulo}")
        return

    porcentagens = contagem / contagem.sum() * 100

    plt.figure(figsize=(8, 8))
    plt.pie(
        porcentagens,
        labels=[f"{cat}\n({p:.1f}%)" for cat, p in zip(categorias, porcentagens)],
        autopct='%1.1f%%',
        startangle=90,
        colors=cores or sns.color_palette("viridis", 5),
        textprops={'fontsize': 10}
    )
    plt.title(titulo, fontsize=14, pad=20, fontweight='bold')
    caminho = os.path.join(output_dir, arquivo)
    plt.savefig(caminho, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico salvo: {caminho}")

# --- 10. GERAR GRÁFICOS DE PIZZA ---
print("\nGerando gráficos de pizza...")

gerar_pizza(manual, 'Tempo Médio Estimado por Aula\nMétodo Manual', '22_manual_pizza.png')
gerar_pizza(planilha, 'Tempo Médio Estimado por Aula\nMétodo Planilha', '23_planilha_pizza.png')
gerar_pizza(planning_individual, 'Tempo Médio por Aula\nPlanningApp', '24_planningapp_individual_pizza.png')

# --- 11. GRÁFICO DE BARRAS: MÉDIAS DOS 3 MÉTODOS ---
plt.figure(figsize=(10, 6))
metodos = ['Manual', 'Planilha', 'PlanningApp']
medias = [media_manual_min, media_planilha_min, media_geral_min]

bars = plt.bar(metodos, medias, color=['#ff7f0e', '#1f77b4', '#2ca02c'], edgecolor='black', linewidth=1.2)
plt.ylabel('Tempo Médio (minutos)', fontsize=12)
plt.title('Comparação das Médias de Tempo por Método', fontsize=14, fontweight='bold', pad=20)

# Adicionar valores nas barras
for bar, valor in zip(bars, medias):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{valor:.1f} min', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.ylim(0, max(medias) * 1.2)
caminho_bar = os.path.join(output_dir, '25_medias_barras.png')
plt.savefig(caminho_bar, bbox_inches='tight')
plt.close()
print(f"[OK] Gráfico de barras salvo: {caminho_bar}")

# --- 12. COMPARATIVO COMPACTO (versão enxuta para artigo) ---
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
fig.suptitle('Comparação: Tempo Médio por Planejamento de Aula', fontsize=14, fontweight='bold')

# Preparar dados para gráfico de barras agrupadas
categorias_ordenadas = ['Menos de 10 min', '10-20 min', '20-30 min', '30-45 min', 'Mais de 45 min']
cores = ['#2E8B57', '#FF6347', '#4682B4', '#DDA0DD', '#8B4513']

# Normalizar dados para porcentagem
manual_contagem = pd.Series(manual).value_counts().reindex(categorias, fill_value=0)
planilha_contagem = pd.Series(planilha).value_counts().reindex(categorias, fill_value=0)
planning_contagem = pd.Series(planning_individual).value_counts().reindex(categorias, fill_value=0)

manual_pct = manual_contagem / manual_contagem.sum() * 100
planilha_pct = planilha_contagem / planilha_contagem.sum() * 100
planning_pct = planning_contagem / planning_contagem.sum() * 100

# Posições das barras
x = np.arange(len(categorias_ordenadas))
width = 0.25

# Plotar barras
bars1 = ax.bar(x - width, manual_pct, width, label='Manual (Estimado)', color=cores[0], alpha=0.8)
bars2 = ax.bar(x, planilha_pct, width, label='Planilha (Estimado)', color=cores[1], alpha=0.8)
bars3 = ax.bar(x + width, planning_pct, width, label='PlanningApp (Real)', color=cores[2], alpha=0.8)

# Adicionar valores nas barras
def add_value_labels(bars):
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.0f}%', ha='center', va='bottom', fontsize=8)

add_value_labels(bars1)
add_value_labels(bars2)
add_value_labels(bars3)

# Configurações do gráfico
ax.set_xlabel('Tempo de Planejamento', fontsize=11)
ax.set_ylabel('Porcentagem (%)', fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(categorias_ordenadas, rotation=45, ha='right')
ax.legend(loc='upper right', fontsize=10)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Adicionar nota sobre PlanningApp geral
ax.text(0.02, 0.85, f'PlanningApp - Média Geral: {media_geral_min:.1f} min', 
        transform=ax.transAxes, fontsize=9, verticalalignment='top',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))

plt.tight_layout()
caminho = os.path.join(output_dir, '21_comparacao_4_pizzas.png')
plt.savefig(caminho, bbox_inches='tight', dpi=150)
plt.close()
print(f"[OK] Comparativo compacto salvo: {caminho}")

print(f"\nTodos os gráficos salvos em: {output_dir}")