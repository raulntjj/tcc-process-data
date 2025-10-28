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