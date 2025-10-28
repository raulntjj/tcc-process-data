Aqui está o `README.md` que você pode usar:

# Projeto de Análise de Dados

Este projeto processa e analisa dados de respostas e logs para gerar visualizações e relatórios.

## Pré-requisitos

- Docker
- Docker Compose

## Configuração

### 1. Preparar os arquivos de entrada

Crie a pasta `input` na raiz do projeto (se não existir) e adicione os seguintes arquivos:

#### Arquivos necessários na pasta `input/`:

- **Respostas**: Arquivo CSV com os dados das respostas
  - Nome sugerido: `respostas.csv`
  - Formato esperado: Colunas separadas por vírgula

- **Logs**: Arquivo JSON com os logs do sistema
  - Nome sugerido: `logs.json`
  - Formato esperado: Array de objetos JSON

### 2. Estrutura de pastas recomendada

```markdown
projeto/
├── app/
│   ├── input/           # ← Coloque seus arquivos aqui
│   │   ├── respostas.csv
│   │   └── logs.json
│   ├── output/          # ← Resultados gerados automaticamente
│   └── graficos_tcc/    # ← Gráficos gerados automaticamente
├── docker-compose.yml
└── README.md
```

## Execução

1. Certifique-se de que os arquivos `respostas.csv` e `logs.json` estão na pasta `input/`

2. Execute o comando:

```bash
docker compose up -d
```

3. Aguarde o processamento ser concluído

4. Os resultados estarão disponíveis nas pastas:
   - `app/output/` - Arquivos de saída processados
   - `app/graficos_tcc/` - Visualizações e gráficos gerados

## Novos Recursos Adicionados

### Análise de Porcentagens
- **percentages.py**: Calcula e exibe porcentagens exatas para todas as perguntas de perfil
- Gera gráficos com contagens absolutas e percentuais
- Cria arquivos CSV com resumos de porcentagens

### Análise Qualitativa
- **qualitative_analysis.py**: Analisa respostas abertas e extrai temas principais
- Identifica palavras-chave mais frequentes
- Analisa sentimentos por método (Manual, Planilha, PlanningApp)
- Gera visualizações de temas identificados

### Relatório Consolidado
- **consolidated_report.py**: Gera relatório completo com todos os dados
- Inclui dados essenciais para as seções 4.1 a 4.6 do TCC
- Cria arquivo com dados formatados para uso direto no trabalho

## Arquivos de Saída Gerados

### Dados de Perfil (Seção 4.1)
- `percentagens_professores.csv` - Porcentagens dos dados de perfil dos professores
- `percentagens_supervisores.csv` - Porcentagens dos dados de perfil dos supervisores

### Análise Comparativa (Seções 4.2-4.5)
- `medias_professores.csv` - Médias de concordância dos professores
- `medias_supervisores.csv` - Médias de concordância dos supervisores

### Análise Qualitativa (Seção 4.6)
- `analise_qualitativa_professores.csv` - Temas identificados nas respostas abertas dos professores
- `analise_qualitativa_supervisores.csv` - Temas identificados nas respostas abertas dos supervisores

### Relatórios Consolidados
- `relatorio_consolidado.txt` - Relatório completo em formato texto
- `dados_essenciais_tcc.csv` - Dados formatados para uso direto no TCC

### Gráficos com Porcentagens
- `01_prof_tempo_servico_pct.png` - Tempo de serviço com porcentagens
- `02_prof_segmentos_pct.png` - Segmentos com porcentagens
- `03_prof_conforto_tec_pct.png` - Conforto tecnológico com porcentagens
- `04_prof_num_turmas_pct.png` - Número de turmas com porcentagens
- `05_prof_num_planos_pct.png` - Número de planos com porcentagens
- `06_prof_outra_escola_pct.png` - Atuação em outras escolas com porcentagens
- `07_sup_funcao_pct.png` - Função dos supervisores com porcentagens
- `08_sup_tempo_gestao_pct.png` - Tempo na gestão com porcentagens
- `09_sup_outras_plat_pct.png` - Uso de outras plataformas com porcentagens
- `qualitative_prof_keywords.png` - Palavras-chave dos professores
- `qualitative_sup_keywords.png` - Palavras-chave dos supervisores

## Verificação

Para verificar os logs do container em execução:

```bash
docker compose logs -f
```

## Parar a execução

```bash
docker compose down
```

## Observações

- Os arquivos na pasta `input/` são lidos apenas na inicialização
- Para reprocessar com novos dados, substitua os arquivos na pasta `input/` e reinicie o container
- As pastas `output/` e `graficos_tcc/` são geradas automaticamente e não devem ser modificadas manualmente
```

Este README fornece instruções claras sobre:
- Onde colocar os arquivos de entrada
- Qual formato usar (CSV para respostas, JSON para logs)
- Como executar o projeto com Docker
- Onde encontrar os resultados
- Comandos úteis para gerenciar a execução

Você pode personalizar os nomes dos arquivos (`respostas.csv`, `logs.json`) conforme a necessidade do seu projeto específico.