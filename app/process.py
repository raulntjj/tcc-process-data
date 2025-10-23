import pandas as pd
import numpy as np

# --- 1. Load and Initial Clean ---
try:
    df = pd.read_csv('./input/respostas.csv')
    print("CSV loaded successfully.")
except FileNotFoundError:
    print("Error: CSV file not found. Make sure 'Avaliação da Evolução dos Métodos de Planejamento de Aula.csv' is in the current directory.")
    exit()

# Drop potentially empty/redundant score/feedback columns
cols_to_drop = [col for col in df.columns if '[Pontuação]' in col or '[Feedback]' in col]
df = df.drop(columns=cols_to_drop)

# Rename function column
df = df.rename(columns={'Qual função você exerce?': 'Funcao'})

# --- 2. Separate DataFrames ---
# !! IMPORTANT: Update 'Supervisor' if the actual value in your form is different !!
supervisor_role_name = 'Supervisor' # Or 'Coordenador(a) / Supervisor(a) Pedagógico(a)' etc.
df_professores = df[df['Funcao'] == 'Professor'].copy()
df_supervisores = df[df['Funcao'] == supervisor_role_name].copy()

# Drop function column after separation
df_professores = df_professores.drop(columns=['Funcao'])
df_supervisores = df_supervisores.drop(columns=['Funcao'])

print(f"Separated data: {len(df_professores)} Professors, {len(df_supervisores)} Supervisors.")

# --- 3. Comprehensive Column Renaming ---

# !! REVIEW CAREFULLY !! - Map long names to short, usable names
rename_map_prof = {
    '1.1 - Há quantos anos você leciona na Escola Estadual Doutor José Augusto? ': 'P1.1_Tempo_Servico',
    '1.2 - Quais segmentos você leciona atualmente?': 'P1.2_Segmentos',
    '1.3 - Em uma escala de muito baixo a muito alto, qual seu nível de conforto geral com o uso de tecnologias digitais?': 'P1.3_Conforto_Tec',
    '1.4 - Para quantas TURMAS diferentes você leciona neste ano letivo?': 'P1.4_Num_Turmas',
    '1.5 - Ao todo, quantos "PLANOS DE AULA/CRONOGRAMA DE AULA" (Conjunto de planejamentos de uma disciplina em um bimestre) você é responsável por desempenhar?': 'P1.5_Num_Planos',
    '1.6 - Você também leciona em outra(s) escola(s) além da E.E. Doutor José Augusto?  Se sim, qual é o principal método de gestão acadêmica utilizado?': 'P1.6_Outra_Escola_Metodo',
    # Section 2: Eficiência
    '2.1 - O método era rápido para registrar planejamentos de aula [Manual]': 'P2.1_Rapidez_Manual',
    '2.1 - O método era rápido para registrar planejamentos de aula [Planilha]': 'P2.1_Rapidez_Planilha',
    '2.1 - O método era rápido para registrar planejamentos de aula [PlanningApp]': 'P2.1_Rapidez_PlanningApp',
    '2.2 - Acessar os registros fora do ambiente escolar era uma tarefa simples.   [Manual]': 'P2.2_Acesso_Fora_Manual',
    '2.2 - Acessar os registros fora do ambiente escolar era uma tarefa simples.   [Planilha]': 'P2.2_Acesso_Fora_Planilha',
    '2.2 - Acessar os registros fora do ambiente escolar era uma tarefa simples.   [PlanningApp]': 'P2.2_Acesso_Fora_PlanningApp',
    '2.3 - Era fácil encontrar informações de planejamentos passados.   [Manual]': 'P2.3_Encontrar_Info_Manual',
    '2.3 - Era fácil encontrar informações de planejamentos passados.   [Planilha]': 'P2.3_Encontrar_Info_Planilha',
    '2.3 - Era fácil encontrar informações de planejamentos passados.   [PlanningApp]': 'P2.3_Encontrar_Info_PlanningApp',
    '2.4 - A necessidade de retrabalho (corrigir erros, refazer lançamentos) era baixa.   [Manual]': 'P2.4_Retrabalho_Manual',
    '2.4 - A necessidade de retrabalho (corrigir erros, refazer lançamentos) era baixa.   [Planilha]': 'P2.4_Retrabalho_Planilha',
    '2.4 - A necessidade de retrabalho (corrigir erros, refazer lançamentos) era baixa.   [PlanningApp]': 'P2.4_Retrabalho_PlanningApp',
    '2.5 - O tempo total gasto com tarefas administrativas era razoável.   [Manual]': 'P2.5_Tempo_Admin_Manual',
    '2.5 - O tempo total gasto com tarefas administrativas era razoável.   [Planilha]': 'P2.5_Tempo_Admin_Planilha',
    '2.5 - O tempo total gasto com tarefas administrativas era razoável.   [PlanningApp]': 'P2.5_Tempo_Admin_PlanningApp',
    '2.6 - No método MANUAL (papel), qual era o tempo médio estimado que você gastava para elaborar o planejamento de UMA aula? ': 'P2.6_Tempo_Aula_Manual',
    '2.7 - No método com PLANILHAS online, qual era o tempo médio estimado que você gastava para elaborar o planejamento de UMA aula?': 'P2.7_Tempo_Aula_Planilha',
    # Section 3: Usabilidade
    '3.1 - O método era fácil de aprender e usar.   [Manual]': 'P3.1_Facil_Aprender_Manual',
    '3.1 - O método era fácil de aprender e usar.   [Planilha]': 'P3.1_Facil_Aprender_Planilha',
    '3.1 - O método era fácil de aprender e usar.   [PlanningApp]': 'P3.1_Facil_Aprender_PlanningApp',
    '3.2 - As informações estavam organizadas de forma clara e intuitiva.   [Manual]': 'P3.2_Org_Clara_Manual',
    '3.2 - As informações estavam organizadas de forma clara e intuitiva.   [Planilha]': 'P3.2_Org_Clara_Planilha',
    '3.2 - As informações estavam organizadas de forma clara e intuitiva.   [PlanningApp]': 'P3.2_Org_Clara_PlanningApp',
    '3.3 - O método ajudava a prevenir erros comuns no planejamento. [Manual]': 'P3.3_Prev_Erros_Manual',
    '3.3 - O método ajudava a prevenir erros comuns no planejamento. [Planilha]': 'P3.3_Prev_Erros_Planilha',
    '3.3 - O método ajudava a prevenir erros comuns no planejamento. [PlanningApp]': 'P3.3_Prev_Erros_PlanningApp',
    '3.4 - Eu me sentia seguro(a) de que os registros não seriam perdidos. [Manual]': 'P3.4_Seguro_Dados_Manual',
    '3.4 - Eu me sentia seguro(a) de que os registros não seriam perdidos. [Planilha]': 'P3.4_Seguro_Dados_Planilha',
    '3.4 - Eu me sentia seguro(a) de que os registros não seriam perdidos. [PlanningApp]': 'P3.4_Seguro_Dados_PlanningApp',
    '3.5 - Era fácil obter ajuda ou suporte em caso de dúvidas sobre o uso. [Manual]': 'P3.5_Suporte_Facil_Manual',
    '3.5 - Era fácil obter ajuda ou suporte em caso de dúvidas sobre o uso. [Planilha]': 'P3.5_Suporte_Facil_Planilha',
    '3.5 - Era fácil obter ajuda ou suporte em caso de dúvidas sobre o uso. [PlanningApp]': 'P3.5_Suporte_Facil_PlanningApp',
    '3.6 - Minha satisfação geral com o método era alta. [Manual]': 'P3.6_Satisfacao_Geral_Manual',
    '3.6 - Minha satisfação geral com o método era alta. [Planilha]': 'P3.6_Satisfacao_Geral_Planilha',
    '3.6 - Minha satisfação geral com o método era alta. [PlanningApp]': 'P3.6_Satisfacao_Geral_PlanningApp',
    # Section 4: Alinhamento
    '4.1 - O método facilitava o alinhamento do planejamento com a BNCC (Base Nacional Comum Curricular), CRMG (Currículo Referência de Minas Gerais), ENADE (Exame Nacional de Desempenho de Estudantes) e o SAEB (Sistema de Avaliação da Educação Básica). [Manual]': 'P4.1_Alinhamento_BNCC_Manual',
    '4.1 - O método facilitava o alinhamento do planejamento com a BNCC (Base Nacional Comum Curricular), CRMG (Currículo Referência de Minas Gerais), ENADE (Exame Nacional de Desempenho de Estudantes) e o SAEB (Sistema de Avaliação da Educação Básica). [Planilha]': 'P4.1_Alinhamento_BNCC_Planilha',
    '4.1 - O método facilitava o alinhamento do planejamento com a BNCC (Base Nacional Comum Curricular), CRMG (Currículo Referência de Minas Gerais), ENADE (Exame Nacional de Desempenho de Estudantes) e o SAEB (Sistema de Avaliação da Educação Básica). [PlanningApp]': 'P4.1_Alinhamento_BNCC_PlanningApp',
    '4.2 - A ferramenta me dava uma visão clara do progresso do planejamento disciplinar ao longo do ano. [Manual]': 'P4.2_Visao_Progresso_Manual',
    '4.2 - A ferramenta me dava uma visão clara do progresso do planejamento disciplinar ao longo do ano. [Planilha]': 'P4.2_Visao_Progresso_Planilha',
    '4.2 - A ferramenta me dava uma visão clara do progresso do planejamento disciplinar ao longo do ano. [PlanningApp]': 'P4.2_Visao_Progresso_PlanningApp',
    '4.3 - O método facilitava a colaboração e o compartilhamento de planos com outros professores. [Manual]': 'P4.3_Colaboracao_Manual',
    '4.3 - O método facilitava a colaboração e o compartilhamento de planos com outros professores. [Planilha]': 'P4.3_Colaboracao_Planilha',
    '4.3 - O método facilitava a colaboração e o compartilhamento de planos com outros professores. [PlanningApp]': 'P4.3_Colaboracao_PlanningApp',
    '4.4 - A comunicação com a coordenação pedagógica era eficiente.   [Manual]': 'P4.4_Comun_Coord_Manual',
    '4.4 - A comunicação com a coordenação pedagógica era eficiente.   [Planilha]': 'P4.4_Comun_Coord_Planilha',
    '4.4 - A comunicação com a coordenação pedagógica era eficiente.   [PlanningApp]': 'P4.4_Comun_Coord_PlanningApp',
    # Section 5: Bem-Estar
    '5.1 - O método contribuía para reduzir meu nível de estresse com tarefas burocráticas.   [Manual]': 'P5.1_Reduz_Estresse_Manual',
    '5.1 - O método contribuía para reduzir meu nível de estresse com tarefas burocráticas.   [Planilha]': 'P5.1_Reduz_Estresse_Planilha',
    '5.1 - O método contribuía para reduzir meu nível de estresse com tarefas burocráticas.   [PlanningApp]': 'P5.1_Reduz_Estresse_PlanningApp',
    '5.2 - O uso da ferramenta frequentemente me causava frustração (tecnoestresse).   [Manual]': 'P5.2_Causa_Frustracao_Manual',
    '5.2 - O uso da ferramenta frequentemente me causava frustração (tecnoestresse).   [Planilha]': 'P5.2_Causa_Frustracao_Planilha',
    '5.2 - O uso da ferramenta frequentemente me causava frustração (tecnoestresse).   [PlanningApp]': 'P5.2_Causa_Frustracao_PlanningApp',
    '5.3 - Eu sentia que tinha controle e autonomia sobre meus planejamentos.   [Manual]': 'P5.3_Controle_Autonomia_Manual',
    '5.3 - Eu sentia que tinha controle e autonomia sobre meus planejamentos.   [Planilha]': 'P5.3_Controle_Autonomia_Planilha',
    '5.3 - Eu sentia que tinha controle e autonomia sobre meus planejamentos.   [PlanningApp]': 'P5.3_Controle_Autonomia_PlanningApp',
    '5.4 - O método passava uma imagem de maior profissionalismo e organização do meu trabalho.   [Manual]': 'P5.4_Profissionalismo_Manual',
    '5.4 - O método passava uma imagem de maior profissionalismo e organização do meu trabalho.   [Planilha]': 'P5.4_Profissionalismo_Planilha',
    '5.4 - O método passava uma imagem de maior profissionalismo e organização do meu trabalho.   [PlanningApp]': 'P5.4_Profissionalismo_PlanningApp',
    '5.5 - O método liberava meu tempo para focar em atividades mais estratégicas.   [Manual]': 'P5.5_Libera_Tempo_Manual',
    '5.5 - O método liberava meu tempo para focar em atividades mais estratégicas.   [Planilha]': 'P5.5_Libera_Tempo_Planilha',
    '5.5 - O método liberava meu tempo para focar em atividades mais estratégicas.   [PlanningApp]': 'P5.5_Libera_Tempo_PlanningApp',
    # Section 6: Abertas
    '6.1 - Por favor, descreva uma situação ou tarefa específica que o novo Sistema de Planejamento tornou muito mais simples de realizar em comparação com os métodos anteriores.  ': 'P6.1_Situacao_Simples',
    '6.2 - Pensando no impacto final do nosso trabalho, você acredita que a organização proporcionada pelo Sistema de Planejamento pode, de alguma forma, beneficiar os alunos indiretamente? Se sim, como?  ': 'P6.2_Beneficio_Alunos',
    '6.3 - Se você pudesse definir em uma única palavra ou expressão o sentimento ao usar o método manual, qual seria?': 'P6.3_Sentimento_Manual',
    '6.4 - Se você pudesse definir em uma única palavra ou expressão o sentimento ao usar o método de Planilhas, qual seria?': 'P6.4_Sentimento_Planilha',
    '6.5 - Se você pudesse definir em uma única palavra ou expressão o sentimento ao usar o método de Sistema de Planejamento Online, qual seria?': 'P6.5_Sentimento_PlanningApp',
    '6.6 - Você tem alguma sugestão de melhoria para o módulo de professor do sistema de planejamento? (Ex: novos relatórios, dashboards, notificações, etc.). ': 'P6.6_Sugestao_Melhoria',
    '6.7 - Pensando nas funcionalidades pedagógicas (criação de planejamentos, gestão de turmas etc.), quais foram os principais benefícios ou desafios encontrados no novo  sistema de planejamento?': 'P6.7_Beneficios_Desafios'
}

# Apply renaming (ignore errors for columns not present, e.g., supervisor questions)
df_professores = df_professores.rename(columns=rename_map_prof, errors='ignore')

# --- Renaming for Supervisors (Create a separate map based on supervisor questionnaire) ---
rename_map_sup = {
    # Perfil (1.1 a 1.3)
    '1.1 - Qual sua principal função na equipe gestora?': 'S1.1_Funcao_Gestora',
    '1.2 - Há quantos anos você atua em cargos de gestão ou supervisão nesta escola?  ': 'S1.2_Tempo_Gestao',
    '1.3 - Sua rotina de trabalho envolve ou envolveu o uso de outras plataformas ou sistemas de gestão em outras instituições?  ': 'S1.3_Outras_Plataformas',
    # Seção 2: Supervisão
    '2.1 - Era fácil ter uma visão geral e centralizada do status dos planejamentos de todos os professores.   [Manual]': 'S2.1_Visao_Geral_Manual',
    '2.1 - Era fácil ter uma visão geral e centralizada do status dos planejamentos de todos os professores.   [Planilha]': 'S2.1_Visao_Geral_Planilha',
    '2.1 - Era fácil ter uma visão geral e centralizada do status dos planejamentos de todos os professores.   [PlanningApp]': 'S2.1_Visao_Geral_PlanningApp',
    '2.2 - O processo de fornecer feedback (avaliacão) aos professores era ágil e bem documentado.   [Manual]': 'S2.2_Feedback_Agil_Manual',
    '2.2 - O processo de fornecer feedback (avaliacão) aos professores era ágil e bem documentado.   [Planilha]': 'S2.2_Feedback_Agil_Planilha',
    '2.2 - O processo de fornecer feedback (avaliacão) aos professores era ágil e bem documentado.   [PlanningApp]': 'S2.2_Feedback_Agil_PlanningApp',
    '2.3 - Identificar planejamentos pendentes ou que precisavam de revisão era uma tarefa rápida.   [Manual]': 'S2.3_Identifica_Pendentes_Manual',
    '2.3 - Identificar planejamentos pendentes ou que precisavam de revisão era uma tarefa rápida.   [Planilha]': 'S2.3_Identifica_Pendentes_Planilha',
    '2.3 - Identificar planejamentos pendentes ou que precisavam de revisão era uma tarefa rápida.   [PlanningApp]': 'S2.3_Identifica_Pendentes_PlanningApp',
    '2.4 - Verificar o alinhamento dos planejamentos com a BNCC , CRMG, ENADE, SAEB e outras diretrizes era um processo simples. [Manual]': 'S2.4_Verifica_Alinhamento_Manual',
    '2.4 - Verificar o alinhamento dos planejamentos com a BNCC , CRMG, ENADE, SAEB e outras diretrizes era um processo simples. [Planilha]': 'S2.4_Verifica_Alinhamento_Planilha',
    '2.4 - Verificar o alinhamento dos planejamentos com a BNCC , CRMG, ENADE, SAEB e outras diretrizes era um processo simples. [PlanningApp]': 'S2.4_Verifica_Alinhamento_PlanningApp',
    '2.5 - O tempo gasto em tarefas operacionais de supervisão (procurar arquivos, controlar versões) era baixo.   [Manual]': 'S2.5_Tempo_Operacional_Manual',
    '2.5 - O tempo gasto em tarefas operacionais de supervisão (procurar arquivos, controlar versões) era baixo.   [Planilha]': 'S2.5_Tempo_Operacional_Planilha',
    '2.5 - O tempo gasto em tarefas operacionais de supervisão (procurar arquivos, controlar versões) era baixo.   [PlanningApp]': 'S2.5_Tempo_Operacional_PlanningApp',
    # Seção 3: Usabilidade
    '3.1 - O método era fácil de aprender e usar.   [Manual]': 'S3.1_Facil_Aprender_Manual',
    '3.1 - O método era fácil de aprender e usar.   [Planilha]': 'S3.1_Facil_Aprender_Planilha',
    '3.1 - O método era fácil de aprender e usar.   [PlanningApp]': 'S3.1_Facil_Aprender_PlanningApp',
    # Seção 3: Usabilidade (continuação)
    '3.2 - As informações estavam organizadas de forma clara e intuitiva.   [Manual]': 'S3.2_Org_Clara_Manual',
    '3.2 - As informações estavam organizadas de forma clara e intuitiva.   [Planilha]': 'S3.2_Org_Clara_Planilha',
    '3.2 - As informações estavam organizadas de forma clara e intuitiva.   [PlanningApp]': 'S3.2_Org_Clara_PlanningApp',
    '3.3 - O método ajudava a prevenir erros comuns no planejamento. [Manual]': 'S3.3_Prev_Erros_Manual',
    '3.3 - O método ajudava a prevenir erros comuns no planejamento. [Planilha]': 'S3.3_Prev_Erros_Planilha',
    '3.3 - O método ajudava a prevenir erros comuns no planejamento. [PlanningApp]': 'S3.3_Prev_Erros_PlanningApp',
    '3.4 - Eu me sentia seguro(a) de que os registros não seriam perdidos. [Manual]': 'S3.4_Seguro_Dados_Manual',
    '3.4 - Eu me sentia seguro(a) de que os registros não seriam perdidos. [Planilha]': 'S3.4_Seguro_Dados_Planilha',
    '3.4 - Eu me sentia seguro(a) de que os registros não seriam perdidos. [PlanningApp]': 'S3.4_Seguro_Dados_PlanningApp',
    '3.5 - Era fácil obter ajuda ou suporte em caso de dúvidas sobre o uso. [Manual]': 'S3.5_Suporte_Facil_Manual',
    '3.5 - Era fácil obter ajuda ou suporte em caso de dúvidas sobre o uso. [Planilha]': 'S3.5_Suporte_Facil_Planilha',
    '3.5 - Era fácil obter ajuda ou suporte em caso de dúvidas sobre o uso. [PlanningApp]': 'S3.5_Suporte_Facil_PlanningApp',
    '3.7 - Minha satisfação geral com o método era alta. [Manual]': 'S3.7_Satisfacao_Geral_Manual',
    '3.7 - Minha satisfação geral com o método era alta. [Planilha]': 'S3.7_Satisfacao_Geral_Planilha',
    '3.7 - Minha satisfação geral com o método era alta. [PlanningApp]': 'S3.7_Satisfacao_Geral_PlanningApp',
    # Seção 4: Gestão Administrativa
    '4.1 - O processo de configurar a estrutura do ano letivo (turmas, disciplinas) era organizado.   [Manual]': 'S4.1_Config_Ano_Manual',
    '4.1 - O processo de configurar a estrutura do ano letivo (turmas, disciplinas) era organizado.   [Planilha]': 'S4.1_Config_Ano_Planilha',
    '4.1 - O processo de configurar a estrutura do ano letivo (turmas, disciplinas) era organizado.   [PlanningApp]': 'S4.1_Config_Ano_PlanningApp',
    '4.2 - Gerenciar os professores era uma tarefa simples.   [Manual]': 'S4.2_Gerencia_Profs_Manual',
    '4.2 - Gerenciar os professores era uma tarefa simples.   [Planilha]': 'S4.2_Gerencia_Profs_Planilha',
    '4.2 - Gerenciar os professores era uma tarefa simples.   [PlanningApp]': 'S4.2_Gerencia_Profs_PlanningApp',
    '4.3 - Eu tinha confiança na segurança e na integridade dos registros sob minha responsabilidade.   [Manual]': 'S4.3_Confianca_Dados_Manual',
    '4.3 - Eu tinha confiança na segurança e na integridade dos registros sob minha responsabilidade.   [Planilha]': 'S4.3_Confianca_Dados_Planilha',
    '4.3 - Eu tinha confiança na segurança e na integridade dos registros sob minha responsabilidade.   [PlanningApp]': 'S4.3_Confianca_Dados_PlanningApp',
    # Seção 5: Visão Estratégica
    '5.1 - O metodo permitia extrair registros consolidados para apoiar a tomada de decisões pedagógicas.   [Manual]': 'S5.1_Extrai_Dados_Decisao_Manual',
    '5.1 - O metodo permitia extrair registros consolidados para apoiar a tomada de decisões pedagógicas.   [Planilha]': 'S5.1_Extrai_Dados_Decisao_Planilha',
    '5.1 - O metodo permitia extrair registros consolidados para apoiar a tomada de decisões pedagógicas.   [PlanningApp]': 'S5.1_Extrai_Dados_Decisao_PlanningApp',
    '5.2 - O método otimizava a comunicação e a transparência entre a equipe gestora e o corpo docente.   [Manual]': 'S5.2_Otimiza_Comun_Manual',
    '5.2 - O método otimizava a comunicação e a transparência entre a equipe gestora e o corpo docente.   [Planilha]': 'S5.2_Otimiza_Comun_Planilha',
    '5.2 - O método otimizava a comunicação e a transparência entre a equipe gestora e o corpo docente.   [PlanningApp]': 'S5.2_Otimiza_Comun_PlanningApp',
    # Seção 6: Bem-Estar
    '6.1 - O método contribuía para reduzir meu nível de estresse com tarefas burocráticas.   [Manual]': 'S6.1_Reduz_Estresse_Manual',
    '6.1 - O método contribuía para reduzir meu nível de estresse com tarefas burocráticas.   [Planilha]': 'S6.1_Reduz_Estresse_Planilha',
    '6.1 - O método contribuía para reduzir meu nível de estresse com tarefas burocráticas.   [PlanningApp]': 'S6.1_Reduz_Estresse_PlanningApp',
    '6.2 - O uso da ferramenta frequentemente me causava frustração (tecnoestresse).   [Manual]': 'S6.2_Causa_Frustracao_Manual',
    '6.2 - O uso da ferramenta frequentemente me causava frustração (tecnoestresse).   [Planilha]': 'S6.2_Causa_Frustracao_Planilha',
    '6.2 - O uso da ferramenta frequentemente me causava frustração (tecnoestresse).   [PlanningApp]': 'S6.2_Causa_Frustracao_PlanningApp',
    '6.3 - Eu sentia que tinha controle e autonomia sobre meus planejamentos.   [Manual]': 'S6.3_Controle_Autonomia_Manual',
    '6.3 - Eu sentia que tinha controle e autonomia sobre meus planejamentos.   [Planilha]': 'S6.3_Controle_Autonomia_Planilha',
    '6.3 - Eu sentia que tinha controle e autonomia sobre meus planejamentos.   [PlanningApp]': 'S6.3_Controle_Autonomia_PlanningApp',
    '6.4 - O método passava uma imagem de maior profissionalismo e organização do meu trabalho.   [Manual]': 'S6.4_Profissionalismo_Manual',
    '6.4 - O método passava uma imagem de maior profissionalismo e organização do meu trabalho.   [Planilha]': 'S6.4_Profissionalismo_Planilha',
    '6.4 - O método passava uma imagem de maior profissionalismo e organização do meu trabalho.   [PlanningApp]': 'S6.4_Profissionalismo_PlanningApp',
    '6.5 - O método liberava meu tempo para focar em atividades mais estratégicas.   [Manual]': 'S6.5_Libera_Tempo_Manual',
    '6.5 - O método liberava meu tempo para focar em atividades mais estratégicas.   [Planilha]': 'S6.5_Libera_Tempo_Planilha',
    '6.5 - O método liberava meu tempo para focar em atividades mais estratégicas.   [PlanningApp]': 'S6.5_Libera_Tempo_PlanningApp',
    # Seção 7: Abertas
    '7.1 - Do ponto de vista da supervisão, qual era o maior ""gargalo"" ou dificuldade no processo de supervisão e acompanhamento dos planejamentos durante a fase das planilhas online?  ': 'S7.1_Gargalo_Planilhas',
    '7.2 - Qual foi o impacto mais significativo (positivo ou negativo) que o novo sistema de planejamento trouxe para a sua rotina de trabalho como gestor(a)?  ': 'S7.2_Impacto_Significativo',
    '7.3 - Como o novo sistema de planejamento alterou a dinâmica de feedback (avaliação) e comunicação entre você e os professores sobre os planejamentos?  ': 'S7.3_Dinamica_Feedback',
    '7.4 - Pensando nas funcionalidades administrativas (criação de turmas, gestão de usuários, etc.), quais foram os principais benefícios ou desafios encontrados no novo  sistema de planejamento ?  ': 'S7.4_Beneficios_Desafios_Admin',
     '7.5 - Você tem alguma sugestão de melhoria para o módulo de supervisão/administração do sistema de planejamento? (Ex: novos relatórios, dashboards, notificações, etc.).  ': 'S7.5_Sugestao_Melhoria_Sup'

}
df_supervisores = df_supervisores.rename(columns=rename_map_sup, errors='ignore')


# --- 4. Codify Likert Scale ---
likert_map = {
    'Discordo totalmente': 1,
    'Discordo parcialmente': 2,
    'Neutro/Indiferente': 3,
    'Concordo parcialmente': 4,
    'Concordo totalmente': 5
}

likert_cols_prof = [col for col in df_professores.columns if any(m in col for m in ['_Manual', '_Planilha', '_PlanningApp']) and not col.startswith('P2.6') and not col.startswith('P2.7')]
df_professores[likert_cols_prof] = df_professores[likert_cols_prof].replace(likert_map)
# Convert to numeric, coercing errors (e.g., if a non-likert value exists)
for col in likert_cols_prof:
    df_professores[col] = pd.to_numeric(df_professores[col], errors='coerce')


likert_cols_sup = [col for col in df_supervisores.columns if any(m in col for m in ['_Manual', '_Planilha', '_PlanningApp'])]
df_supervisores[likert_cols_sup] = df_supervisores[likert_cols_sup].replace(likert_map)
for col in likert_cols_sup:
    df_supervisores[col] = pd.to_numeric(df_supervisores[col], errors='coerce')

# --- 5. Quantitative Analysis ---

# 5.1 Profile Analysis (Frequencies)
print("\n--- Perfil dos Professores ---")
for col in df_professores.columns:
    if col.startswith('P1.'):
        print(f"\n{col}:")
        print(df_professores[col].value_counts(normalize=True).map("{:.1%}".format)) # Percentages

# (Repeat for Supervisors if needed)
print("\n--- Perfil dos Supervisores ---")
for col in df_supervisores.columns:
     if col.startswith('S1.'):
        print(f"\n{col}:")
        print(df_supervisores[col].value_counts(normalize=True).map("{:.1%}".format))

# 5.2 Likert Analysis (Means) - Professors
print("\n--- Médias de Concordância (Professores) ---")
results_prof = {}
for col in likert_cols_prof:
    base_name = col[:-len('_Manual')] if col.endswith('_Manual') else \
                  col[:-len('_Planilha')] if col.endswith('_Planilha') else \
                  col[:-len('_PlanningApp')] if col.endswith('_PlanningApp') else col
    method = 'Manual' if col.endswith('_Manual') else \
             'Planilha' if col.endswith('_Planilha') else \
             'PlanningApp' if col.endswith('_PlanningApp') else 'Unknown'

    if base_name not in results_prof:
        results_prof[base_name] = {}
    results_prof[base_name][method] = df_professores[col].mean(skipna=True) # skipna=True handles potential errors during conversion

df_results_prof = pd.DataFrame(results_prof).T[['Manual', 'Planilha', 'PlanningApp']] # Ensure order
print(df_results_prof.to_string(float_format="%.2f"))

# (Repeat for Supervisors)
print("\n--- Médias de Concordância (Supervisores) ---")
results_sup = {}
for col in likert_cols_sup:
    # Similar logic to extract base_name and method for supervisors
    base_name = col[:-len('_Manual')] if col.endswith('_Manual') else \
                  col[:-len('_Planilha')] if col.endswith('_Planilha') else \
                  col[:-len('_PlanningApp')] if col.endswith('_PlanningApp') else col
    method = 'Manual' if col.endswith('_Manual') else \
             'Planilha' if col.endswith('_Planilha') else \
             'PlanningApp' if col.endswith('_PlanningApp') else 'Unknown'

    if base_name not in results_sup:
        results_sup[base_name] = {}
    results_sup[base_name][method] = df_supervisores[col].mean(skipna=True)

df_results_sup = pd.DataFrame(results_sup).T[['Manual', 'Planilha', 'PlanningApp']]
print(df_results_sup.to_string(float_format="%.2f"))


# 5.3 Time Estimation Analysis (Frequencies) - Professors
print("\n--- Análise Tempo Estimado por Aula (Professores) ---")
if 'P2.6_Tempo_Aula_Manual' in df_professores.columns:
    print("\nMétodo Manual:")
    print(df_professores['P2.6_Tempo_Aula_Manual'].value_counts(normalize=True).map("{:.1%}".format))
if 'P2.7_Tempo_Aula_Planilha' in df_professores.columns:
    print("\nMétodo Planilha:")
    print(df_professores['P2.7_Tempo_Aula_Planilha'].value_counts(normalize=True).map("{:.1%}".format))

# (Repeat for Supervisors if needed - create S2.6, S2.7 mappings first)


# --- 6. Qualitative Analysis Preparation (Extract Open-Ended Responses) ---
print("\n--- Respostas Abertas (Professores) ---")
open_ended_cols_prof = [col for col in df_professores.columns if col.startswith('P6.')]
for col in open_ended_cols_prof:
    print(f"\n{col}:")
    # Print non-empty responses
    responses = df_professores[col].dropna().tolist()
    if responses:
        for i, response in enumerate(responses):
            print(f"- Resposta {i+1}: {response}")
    else:
        print("Nenhuma resposta.")

# (Repeat for Supervisors)
print("\n--- Respostas Abertas (Supervisores) ---")
open_ended_cols_sup = [col for col in df_supervisores.columns if col.startswith('S7.')] # Adjust if section number is different
for col in open_ended_cols_sup:
    print(f"\n{col}:")
    responses = df_supervisores[col].dropna().tolist()
    if responses:
         for i, response in enumerate(responses):
            print(f"- Resposta {i+1}: {response}")
    else:
        print("Nenhuma resposta.")

print("\n--- Fim da Análise ---")
# Store processed dataframes for graphing block
# %store df_professores
# %store df_supervisores
# %store df_results_prof
# %store df_results_sup

# Save to CSV if needed (useful for checking)
df_professores.to_csv("output/professores_processado.csv", index=False)
df_supervisores.to_csv("output/supervisores_processado.csv", index=False)
df_results_prof.to_csv("output/medias_professores.csv")
df_results_sup.to_csv("output/medias_supervisores.csv")
print("\nDados processados e médias salvos em arquivos CSV.")