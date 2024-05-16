# Resultados criando um arquivo FASTA e .bed junto.

import os
import pandas as pd
import plotly.express as px
from plotly.offline import plot
import subprocess

# Leitura dos dados de vírus
ictvMSL = pd.read_csv("data/ICTV_MSL.csv", names=["Species", "Genome.composition"])
ictvVMR_species = pd.read_csv("data/ICTV_VMR-species.csv")
ictvVMR_virNames = pd.read_csv("data/ICTV_VMR-virNames.csv")
ncbiSpecie = pd.read_csv("data/NCBI_virSpecies.csv", names=["Species", "Genome.composition"])
ncbiNames = pd.read_csv("data/NCBI_virName.csv", names=["Species", "Genome.composition"])

# Merge de todas as tabelas
allVirus = pd.concat([ncbiNames, ncbiSpecie])

# Listar arquivos .tsv
def list_full_paths(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory)]

arquivos = list_full_paths("diamond-processed/")

# Crie a pasta para os resultados
output_folder = "ViewVir-results"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Loop para cada tabela .tsv
for arquivo_path in arquivos:
    # Processando a Tabela
    # Leia o arquivo
    arquivo = pd.read_csv(arquivo_path, sep="\t")

    # Realize a operação de junção
    arquivo = pd.merge(arquivo, allVirus, on="Species", how="left")

    # Mude a ordem das colunas
    outrasCols = list(set(arquivo.columns) - {"Genome.composition"})
    arquivo = arquivo[["QuerySeq", "SubjectSeq", "QseqLength", "SseqLength", "Pident", "Evalue", "QCover",
                      "SubjTitle", "Species", "Genome.composition", "FullQueryLength"]]

    # Filtro de sequencias
    arquivo = arquivo[arquivo["QseqLength"] >= 500]

    # Remover duplicatas
    arquivo = arquivo.drop_duplicates()

    # Obtenha o nome do arquivo de entrada
    nome_arquivo_input = os.path.basename(arquivo_path)

    # Crie o diretório com o nome do arquivo dentro de "diamond-results"
    pasta_nome_arquivo = os.path.join(output_folder, nome_arquivo_input.replace(".fasta_merged.fasta.tsv", ""))
    os.makedirs(pasta_nome_arquivo, exist_ok=True)

    # Defina o caminho completo do arquivo de saída dentro do diretório criado
    caminho_arquivo_output = os.path.join(pasta_nome_arquivo, nome_arquivo_input.replace(".fasta_merged.fasta.tsv", "_output.tsv"))

    plot_output_bubble = os.path.join(pasta_nome_arquivo, nome_arquivo_input.replace(".fasta_merged.fasta.tsv", "_bubblePlt.html"))

    # Escreva os dados em um arquivo de saída dentro do diretório criado
    arquivo.to_csv(caminho_arquivo_output, sep="\t", index=False)

    # Filtro para vírus de RNA
    arquivo_RNA = arquivo[arquivo["Genome.composition"].isin(["ssRNA(-)", "ssRNA(+/-)", "ssRNA(+)", "ssRNA-RT", "RNA", "unknown", "NA"])]
    arquivo_RNA = arquivo_RNA.drop_duplicates()

    # Escreva os dados em um arquivo de saída separado para vírus de RNA
    output_RNA_table = os.path.join(pasta_nome_arquivo, nome_arquivo_input.replace(".fasta_merged.fasta.tsv", "_RNA-virus.tsv"))
    arquivo_RNA.to_csv(output_RNA_table, sep="\t", index=False)

    # Salve as sequências em formato fasta
    output_pre = os.path.join(pasta_nome_arquivo, nome_arquivo_input.replace(".fasta_merged.fasta.tsv", "_pre_fasta.tsv"))
    arquivo_PRE = arquivo_RNA[["QuerySeq", "FullQueryLength"]]
    arquivo_PRE.to_csv(output_pre, sep="\t", index=False)

    # Processar _pre_fasta.tsv para gerar RNA-virus.fasta
    samp = os.path.basename(output_pre).replace("_pre_fasta.tsv", "")
    with open(output_pre, "r") as infile, open(f"{pasta_nome_arquivo}/{samp}_RNA-virus.fasta", "w") as outfile:
        lines = infile.readlines()
        for line in lines[1:]:  # Ignorar a primeira linha
            line = line.strip().replace('\t', '\n')
            outfile.write(f">{line}\n")

    # Gráfico Interativo
    arquivo["MatchSequence"] = arquivo["Species"] + " -> " + arquivo["SubjTitle"]
    arquivo["Genome.composition"] = arquivo["Genome.composition"].fillna("NA")

    fig = px.scatter(arquivo, x="QseqLength", y="MatchSequence", size="QCover", color="Genome.composition",
                     hover_data=["Pident", "Evalue"])
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, title='ViewVir interactive scatter plot')
    plot(fig, filename=plot_output_bubble)

    # Processar arquivos fasta com orfipy
    lista_arquivos = [os.path.join(pasta_nome_arquivo, file)
                      for file in os.listdir(pasta_nome_arquivo)
                      if file.endswith(".fasta")]

    for arquivo in lista_arquivos:
        entrada = arquivo
        nome = os.path.basename(arquivo).replace(".fasta", "")
        saida = pasta_nome_arquivo

        # Executa orfipy
        orfipy_cmd = [
            "orfipy", "--partial-3", "--partial-5", "--outdir", saida, entrada, "--bed", f"{nome}.bed"
        ]
        subprocess.run(orfipy_cmd, check=True)

    # Remove arquivos .log
    log_files = [os.path.join(pasta_nome_arquivo, file) for file in os.listdir(pasta_nome_arquivo) if file.endswith(".log")]
    for log_file in log_files:
        os.remove(log_file)

    



