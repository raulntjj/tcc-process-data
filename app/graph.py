# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
import os

# --- Configurações Globais ---
sns.set_theme(style="whitegrid")
plt.style.use('seaborn-v0_8-colorblind') # Estilo de cores acessível
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11 # Ajustar tamanho da fonte se necessário
plt.rcParams['figure.autolayout'] = True # Tenta ajustar layout automaticamente
plt.rcParams['savefig.dpi'] = 150 # Aumentar resolução das imagens salvas

# Criar diretório para salvar gráficos se não existir
output_dir = "graficos_tcc"
os.makedirs(output_dir, exist_ok=True)

# --- Carregar Dados Processados ---
try:
    df_professores = pd.read_csv("./output/professores_processado.csv")
    df_supervisores = pd.read_csv("./output/supervisores_processado.csv")
    df_results_prof = pd.read_csv("./output/medias_professores.csv", index_col=0)
    df_results_sup = pd.read_csv("./output/medias_supervisores.csv", index_col=0)
    print("Dados processados carregados com sucesso.")
except FileNotFoundError:
    print("Erro: Arquivos CSV processados não encontrados. Execute o Bloco de Análise primeiro.")
    exit()
except Exception as e:
    print(f"Erro ao carregar arquivos CSV: {e}")
    exit()

# --- Funções Auxiliares de Plotagem ---

def save_plot(filename, title):
    """Salva a figura atual no diretório de saída."""
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, bbox_inches='tight')
    print(f"Gráfico '{title}' salvo como {filepath}")
    plt.close() # Fechar figura

def plot_profile_chart(data, column, title, filename, plot_type='bar', order=None, xlabel=None, ylabel='Número de Participantes'):
    """Gera gráficos de barras ou pizza para perfil."""
    if column not in data.columns or data[column].isnull().all():
        print(f"Aviso: Coluna '{column}' não encontrada ou vazia. Gráfico '{title}' não gerado.")
        return

    plt.figure(figsize=(10, 6))
    plt.suptitle(title, fontsize=16, y=1.02)
    clean_data = data.dropna(subset=[column]) # Remover NaNs antes de contar

    if clean_data.empty:
         print(f"Aviso: Sem dados válidos para plotar para {column} após remover NaNs.")
         plt.close()
         return

    if plot_type == 'pie':
        counts = clean_data[column].value_counts()
        labels = [f'{label} ({value})' for label, value in counts.items()] # Label com contagem
        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85, textprops={'fontsize': 10})
        plt.title("Distribuição Percentual", fontsize=12)

    elif plot_type == 'bar':
        if order:
            valid_order = [o for o in order if o in clean_data[column].unique()]
            counts = clean_data[column].value_counts().reindex(valid_order).fillna(0) # Reindexar e preencher com 0
        else:
            counts = clean_data[column].value_counts()

        if not counts.empty:
            ax = sns.barplot(x=counts.index, y=counts.values, palette='viridis')
            ax.set_title("Contagem Absoluta", fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_xlabel(xlabel if xlabel else column.split('_', 1)[-1].replace('_', ' '), fontsize=12)

            # Add counts above bars only if height > 0
            for container in ax.containers:
                ax.bar_label(container, label_type='edge', padding=3)

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


def plot_likert_comparison(df_means, title, filename, participant_type=""):
    """Gera gráfico de barras agrupadas para médias Likert."""
    if df_means.empty:
        print(f"Aviso: Sem dados de médias para plotar '{title}'")
        return

    # Mapeamento para rótulos mais curtos e descritivos
    short_labels = {
        # Professor
        'P2.1_Rapidez': 'Rapidez Registro', 'P2.2_Acesso_Fora': 'Acesso Remoto',
        'P2.3_Encontrar_Info': 'Encontrar Info.', 'P2.4_Retrabalho': 'Baixo Retrabalho',
        'P2.5_Tempo_Admin': 'Tempo Admin.',
        'P3.1_Facil_Aprender': 'Fácil Aprender', 'P3.2_Org_Clara': 'Org. Clara',
        'P3.3_Prev_Erros': 'Previne Erros', 'P3.4_Seguro_Dados': 'Segurança Dados',
        'P3.5_Suporte_Facil': 'Suporte Fácil', 'P3.6_Satisfacao_Geral': 'Satisfação Geral',
        'P4.1_Alinhamento_BNCC': 'Alinh. Normas', 'P4.2_Visao_Progresso': 'Visão Progresso',
        'P4.3_Colaboracao': 'Colaboração Profs.', 'P4.4_Comun_Coord': 'Comun. Coord.',
        'P5.1_Reduz_Estresse': 'Reduz Estresse', 'P5.2_Causa_Frustracao': 'Causa Frustração (-)', # Added (-) for clarity
        'P5.3_Controle_Autonomia': 'Controle/Auton.', 'P5.4_Profissionalismo': 'Profissionalismo',
        'P5.5_Libera_Tempo': 'Libera Tempo',
        # Supervisor (Adicione mapeamentos para TODAS as perguntas de S2 a S6)
        'S2.1_Visao_Geral': 'Visão Geral Status', 'S2.2_Feedback_Agil': 'Feedback Ágil',
        'S2.3_Identifica_Pendentes': 'Identif. Pendentes', 'S2.4_Verifica_Alinhamento': 'Verif. Alinham.',
        'S2.5_Tempo_Operacional': 'Tempo Operac. Supervisão',
        'S3.1_Facil_Aprender': 'Fácil Aprender', 'S3.2_Org_Clara': 'Org. Clara',
        'S3.3_Prev_Erros': 'Previne Erros', 'S3.4_Seguro_Dados': 'Segurança Dados',
        'S3.5_Suporte_Facil': 'Suporte Fácil', 'S3.6_Satisfacao_Geral': 'Satisfação Geral', # Check if S3.6 exists
        'S4.1_Config_Ano': 'Config. Ano Letivo', 'S4.2_Gerencia_Profs': 'Gerenciar Profs.',
        'S4.3_Confianca_Dados': 'Confiança Dados',
        'S5.1_Extrai_Dados_Decisao': 'Extrai Dados Decisão', 'S5.2_Otimiza_Comun': 'Otimiza Comun./Transp.',
        'S6.1_Reduz_Estresse': 'Reduz Estresse Gestão', 'S6.2_Causa_Frustracao': 'Causa Frustração (-)',
        'S6.3_Controle_Autonomia': 'Controle/Auton. Processos', 'S6.4_Profissionalismo': 'Profiss. Escola',
        'S6.5_Libera_Tempo': 'Libera Tempo Estratégico'
        # Adicione outros mapeamentos S... conforme necessário
    }
    # Pegar apenas os índices presentes no df_means e mapeá-los
    plot_labels = [short_labels.get(idx, idx) for idx in df_means.index]

    ax = df_means[['Manual', 'Planilha', 'PlanningApp']].plot(kind='bar', figsize=(15, 8), width=0.75)
    plt.title(title, fontsize=16)
    plt.ylabel('Média de Concordância (1=Discordo Totalmente, 5=Concordo Totalmente)', fontsize=12)
    plt.xlabel('Afirmação Avaliada', fontsize=12)
    plt.xticks(range(len(plot_labels)), plot_labels, rotation=45, ha='right', fontsize=10) # Rotacionar para caber
    plt.ylim(1, 5.5) # Limite da escala Likert com margem
    plt.legend(title='Método', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add values above bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', fontsize=9, padding=3, rotation=90) # Rotacionar valores

    # Adicionar linha de referência no Neutro (3)
    ax.axhline(3, color='grey', linestyle='--', linewidth=0.8, label='Neutro')
    ax.legend(title='Método', bbox_to_anchor=(1.02, 1), loc='upper left') # Recriar legenda

    save_plot(filename, title)


# --- Geração dos Gráficos ---

# I. Gráficos de Perfil
print("\n--- Gerando Gráficos de Perfil ---")
# Professores
order_tempo_srv = ['Menos de 2 anos', 'Entre 2 e 5 anos', 'Entre 6 e 10 anos', 'Mais de 10 anos']
order_conforto = ['Muito baixo', 'Baixo', 'Médio', 'Alto', 'Muito alto']
order_turmas = ['1 a 3 turmas', '4 a 6 turmas', '7 a 9 turmas', '10 ou mais turmas']
order_planos = ['1 a 4 diários', '5 a 8 diários', '9 a 12 diários', '13 ou mais diários']

plot_profile_chart(df_professores, 'P1.1_Tempo_Servico', 'Professores: Tempo de Serviço', '01_prof_tempo_servico.png', order=order_tempo_srv, xlabel="Tempo de Serviço")
plot_profile_chart(df_professores, 'P1.2_Segmentos', 'Professores: Segmentos de Atuação', '02_prof_segmentos.png', plot_type='pie')
plot_profile_chart(df_professores, 'P1.3_Conforto_Tec', 'Professores: Conforto com Tecnologia', '03_prof_conforto_tec.png', order=order_conforto, xlabel="Nível de Conforto")
plot_profile_chart(df_professores, 'P1.4_Num_Turmas', 'Professores: Número de Turmas', '04_prof_num_turmas.png', order=order_turmas, xlabel="Número de Turmas")
plot_profile_chart(df_professores, 'P1.5_Num_Planos', 'Professores: Número de Planos/Cronogramas', '05_prof_num_planos.png', order=order_planos, xlabel="Número de Planos")
plot_profile_chart(df_professores, 'P1.6_Outra_Escola_Metodo', 'Professores: Atuação em Outras Escolas', '06_prof_outra_escola.png', plot_type='bar', xlabel="Método na Outra Escola")

# Supervisores
order_tempo_gest = ['Menos de 2 anos', 'Entre 2 e 5 anos', 'Entre 5 e 10 anos', 'Mais de 10 anos'] # Ordem para supervisores
# Ajuste 'Mais de 5 anos' se for diferente, ex: 'Entre 5 e 10 anos', 'Mais de 10 anos'

# Verificar se as colunas existem antes de plotar (evita erros se não houver supervisor)
if not df_supervisores.empty:
    if 'S1.1_Funcao_Gestora' in df_supervisores.columns:
        plot_profile_chart(df_supervisores, 'S1.1_Funcao_Gestora', 'Supervisores: Função na Equipe Gestora', '07_sup_funcao.png', plot_type='pie')
    if 'S1.2_Tempo_Gestao' in df_supervisores.columns:
         plot_profile_chart(df_supervisores, 'S1.2_Tempo_Gestao', 'Supervisores: Tempo no Cargo', '08_sup_tempo_gestao.png', order=order_tempo_gest, xlabel="Tempo no Cargo") # Use order aqui se fizer sentido
    if 'S1.3_Outras_Plataformas' in df_supervisores.columns:
        plot_profile_chart(df_supervisores, 'S1.3_Outras_Plataformas', 'Supervisores: Uso de Outras Plataformas', '09_sup_outras_plat.png', plot_type='pie')
else:
    print("Aviso: Nenhum dado de supervisor encontrado para gerar gráficos de perfil.")


# II. Gráficos Comparativos Likert
print("\n--- Gerando Gráficos Comparativos Likert ---")
# Professores
df_means_prof_eficiencia = df_results_prof[df_results_prof.index.str.startswith('P2.')]
df_means_prof_usabilidade = df_results_prof[df_results_prof.index.str.startswith('P3.')]
df_means_prof_alinhamento = df_results_prof[df_results_prof.index.str.startswith('P4.')]
df_means_prof_bemestar = df_results_prof[df_results_prof.index.str.startswith('P5.')]

plot_likert_comparison(df_means_prof_eficiencia, 'Professores: Eficiência e Carga de Trabalho', '10_comp_prof_eficiencia.png')
plot_likert_comparison(df_means_prof_usabilidade, 'Professores: Usabilidade e Satisfação', '11_comp_prof_usabilidade.png')
plot_likert_comparison(df_means_prof_alinhamento, 'Professores: Alinhamento Pedagógico e Colaboração', '12_comp_prof_alinhamento.png')
plot_likert_comparison(df_means_prof_bemestar, 'Professores: Bem-Estar e Impacto Profissional', '13_comp_prof_bemestar.png')

# Supervisores
if not df_supervisores.empty:
    df_means_sup_supervisao = df_results_sup[df_results_sup.index.str.startswith('S2.')]
    df_means_sup_usabilidade = df_results_sup[df_results_sup.index.str.startswith('S3.')]
    df_means_sup_gestao_adm = df_results_sup[df_results_sup.index.str.startswith('S4.')]
    df_means_sup_visao_estr = df_results_sup[df_results_sup.index.str.startswith('S5.')]
    df_means_sup_bemestar = df_results_sup[df_results_sup.index.str.startswith('S6.')] # Confirme se é S6

    plot_likert_comparison(df_means_sup_supervisao, 'Supervisores: Gestão e Supervisão', '14_comp_sup_supervisao.png')
    plot_likert_comparison(df_means_sup_usabilidade, 'Supervisores: Usabilidade e Satisfação', '15_comp_sup_usabilidade.png')
    plot_likert_comparison(df_means_sup_gestao_adm, 'Supervisores: Gestão Administrativa', '16_comp_sup_gestao_adm.png')
    plot_likert_comparison(df_means_sup_visao_estr, 'Supervisores: Visão Estratégica', '17_comp_sup_visao_estr.png')
    plot_likert_comparison(df_means_sup_bemestar, 'Supervisores: Bem-Estar e Impacto Profissional', '18_comp_sup_bemestar.png')
else:
     print("Aviso: Nenhum dado de supervisor encontrado para gerar gráficos comparativos.")


# III. Gráficos de Tempo Estimado
print("\n--- Gerando Gráficos de Tempo Estimado ---")
order_tempo_aula = ['Menos de 10 minutos', 'Entre 10 e 20 minutos', 'Entre 20 e 30 minutos', 'Entre 30 e 45 minutos', 'Mais de 45 minutos']

# Professores
if 'P2.6_Tempo_Aula_Manual' in df_professores.columns:
    plot_profile_chart(df_professores, 'P2.6_Tempo_Aula_Manual', 'Professores: Tempo Estimado por Aula (Manual)', '19_tempo_manual_prof.png', plot_type='bar', order=order_tempo_aula, xlabel="Tempo Estimado (min)")
if 'P2.7_Tempo_Aula_Planilha' in df_professores.columns:
    plot_profile_chart(df_professores, 'P2.7_Tempo_Aula_Planilha', 'Professores: Tempo Estimado por Aula (Planilha)', '20_tempo_planilha_prof.png', plot_type='bar', order=order_tempo_aula, xlabel="Tempo Estimado (min)")

# Supervisores (Adicione mapeamentos S2.6 e S2.7 se existirem)
# Exemplo de como seria se as colunas existissem e fossem mapeadas:
# if not df_supervisores.empty:
#     if 'S2.6_Tempo_Aula_Manual_Percepcao' in df_supervisores.columns:
#         plot_profile_chart(df_supervisores, 'S2.6_Tempo_Aula_Manual_Percepcao', './output/graphs/Supervisores: Percepção Tempo por Aula (Manual)', '21_tempo_manual_sup.png', plot_type='bar', order=order_tempo_aula, xlabel="Tempo Estimado (min)")
#     if 'S2.7_Tempo_Aula_Planilha_Percepcao' in df_supervisores.columns:
#         plot_profile_chart(df_supervisores, 'S2.7_Tempo_Aula_Planilha_Percepcao', './output/graphs/Supervisores: Percepção Tempo por Aula (Planilha)', '22_tempo_planilha_sup.png', plot_type='bar', order=order_tempo_aula, xlabel="Tempo Estimado (min)")
# else:
#      print("Aviso: Nenhum dado de supervisor encontrado para gerar gráficos de tempo.")

print("\n--- Geração de Gráficos Concluída ---")
print(f"Todos os gráficos foram salvos na pasta: {output_dir}")