import os
from Bio import SeqIO
from dna_features_viewer import GraphicFeature, GraphicRecord
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.plotting import figure
from bokeh.layouts import column

# Função para parsear os arquivos FASTA de ORFs para diferentes códigos genéticos
def parse_orf_fastas(file_paths):
    orf_data_by_contig = {}
    for file_path, code in file_paths:
        for record in SeqIO.parse(file_path, "fasta"):
            header = record.description
            parts = header.split()
            
            contig_full = parts[0]
            # Remover a parte "_ORF.26" do final do identificador da contig
            if '_ORF.' in contig_full:
                contig = contig_full[:contig_full.index('_ORF.')]
            else:
                contig = contig_full
            
            coordinates_strand = parts[1].replace('[', '').replace(']', '')
            
            if '(' in coordinates_strand:  # Verifica se '(' está presente na string
                coordinates, strand = coordinates_strand.split('(')  # Divide na '('
                coordinates = coordinates.strip()  # coordinates será "138-1149"
                strand = strand.replace(')', '').strip()  # strand será "-"
                start, end = map(int, coordinates.split('-'))
            else:
                continue  # Tratamento de erro: se a string não estiver no formato esperado

            # Extraindo informações adicionais
            additional_info = parts[2:]
            additional_info_dict = {info.split(':')[0]: info.split(':')[1] for info in additional_info}

            orf = {
                'contig_full': contig_full,
                'contig': contig,
                'start': start,
                'end': end,
                'strand': strand,
                'sequence': str(record.seq),
                'type': additional_info_dict.get('type'),
                'length': int(additional_info_dict.get('length', 0)),
                'frame': additional_info_dict.get('frame'),
                'start_codon': additional_info_dict.get('start'),
                'stop_codon': additional_info_dict.get('stop'),
                'code': code  # Adicionar o código genético associado à ORF
            }
            
            if contig not in orf_data_by_contig:
                orf_data_by_contig[contig] = {}
            
            if code not in orf_data_by_contig[contig]:
                orf_data_by_contig[contig][code] = []
            
            orf_data_by_contig[contig][code].append(orf)
    
    return orf_data_by_contig

# Função para parsear o arquivo FASTA de nucleotídeos
def parse_nuc_fasta(file_path):
    nuc_data = {}
    for record in SeqIO.parse(file_path, "fasta"):
        nuc_data[record.id] = str(record.seq)
    return nuc_data

# Função para criar gráficos e gerar arquivo HTML para cada código genético por contig
def create_graphics(output_file, orf_data_by_contig, nuc_data):
    html_content = []
    
    for contig, orfs_by_code in orf_data_by_contig.items():
        if contig not in nuc_data:
            print(f"Contig {contig} not found in nucleotide data, skipping...")
            continue
        
        for code, orfs in orfs_by_code.items():
            features = []
            for orf in orfs:
                strand = 1 if orf['strand'] == '+' else -1
                color = "#ffcccc" if strand == 1 else "#ccccff"
                label = f"{orf['contig_full']}: {orf['start']}-{orf['end']} ({orf['strand']}) \n Codons: start {orf['start_codon']}, stop {orf['stop_codon']}"
                feature = GraphicFeature(start=orf['start'], end=orf['end'], strand=strand, color=color, label=label)
                features.append(feature)
            
            sequence_length = len(nuc_data[contig])
            record = GraphicRecord(sequence_length=sequence_length, features=features)
            plot = record.plot_with_bokeh(figure_width=15)
            plot_html = file_html(plot, CDN, f"Contig: {contig} - Code: {code}")
            
            title_html = f"<h3>Contig: {contig} - Code: {code}</h3>"
            html_content.append(title_html + plot_html)

            # Debug: Print the HTML content length for each contig and code
            print(f"Generated HTML for contig {contig}, code {code}, length: {len(plot_html)}")

    with open(output_file, "w") as f:
        f.write(f"""<!DOCTYPE html>
                    <html>
                    <head>
                    <style>
                    body {{
                        font-family: 'Ubuntu', sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                    }}
                    .container {{
                        max-width: 800px;
                        padding: 20px;
                    }}
                    </style>
                    </head>
                    <body>
                    <div class="container">
                    <br><br>
                    {''.join(html_content)}
                    </div>
                    </body>
                    </html>""")

# Função principal
def main(orf_fasta_files, nuc_fasta_file, output_file):
    # Verificar se os arquivos fasta de ORFs existem
    for file_path, code in orf_fasta_files:
        if not os.path.isfile(file_path):
            print(f"Error: ORF FASTA file '{file_path}' for code '{code}' not found.")
            return
    if not os.path.isfile(nuc_fasta_file):
        print(f"Error: Nucleotide FASTA file '{nuc_fasta_file}' not found.")
        return

    # Parsear arquivos fasta de ORFs para diferentes códigos genéticos e contigs
    orf_data_by_contig = parse_orf_fastas(orf_fasta_files)

    print("Parsing nucleotide FASTA file...")
    nuc_data = parse_nuc_fasta(nuc_fasta_file)
    print(f"Found {len(nuc_data)} nucleotide sequences.")

    print("Creating graphics and writing to HTML file...")
    create_graphics(output_file, orf_data_by_contig, nuc_data)
    print(f"Plots saved in {output_file}")

# Caminhos para os arquivos FASTA de ORFs e o arquivo HTML de saída
orf_fasta_files = [
    ('teste_ORFgc1.fasta', 'Genetic Code 01'),
    ('teste_ORFgc5.fasta', 'Genetic Code 05'),
    ('teste_ORFgc11.fasta', 'Genetic Code 11')
]
nuc_fasta_file = 'teste_nonDNA.fasta'
output_file = 'orf_plots.html'

# Executa a função principal
main(orf_fasta_files, nuc_fasta_file, output_file)