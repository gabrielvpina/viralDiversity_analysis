import os
import pandas as pd
import argparse
import re
from modules.tblfmt import process_diamondTbl,renameFasta
from modules.findorf import findorf
from modules.newORF import gc1_ORFs,gc5_ORFs,gc11_ORFs
from modules.plots import scatterPlot

# Importando dados
ncbiSpecie = pd.read_csv("data/NCBI_virSpecies.csv", names=["Species", "Genome.composition"])
ncbiNames = pd.read_csv("data/NCBI_virName.csv", names=["Species", "Genome.composition"])
# Merge de todas as tabelas
allVirus = pd.concat([ncbiNames, ncbiSpecie])


parser = argparse.ArgumentParser()
parser.add_argument("-o","--outdir", type=str, help="Output directory")
args = parser.parse_args()

########################### INPUT ###########################
# Output dir
vvfolder = str(args.outdir)
if vvfolder == "None":
    vvfolder = "ViewVir-results"

# Input contig
# arquivo input


######################################## Processando contigs ##############################
# Renomear arquivo fasta original
#renameFasta(arquivo_input)

###########################################################################################

######################################## Processando diamond ##############################
dmndtable = "diamond.tsv"
process_diamondTbl(dmndtable,vvfolder)
#renameFasta(vvfolder)

# Criar Orfs
findorf(vvfolder)

# Processing ORFs
gc1_ORFs(vvfolder)
gc5_ORFs(vvfolder)
gc11_ORFs(vvfolder)

# Scatter Plot
scatterPlot(vvfolder)



