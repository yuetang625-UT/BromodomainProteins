# BromodomainProteins

transfer_id.py automatically combines the mutation information of a specific gene with metadata and FPKM expression levels of target genes.

usage transfer_id.py -h gives you all the parameters

-f MAF, --input_file=MAF MAF file contains the somatic mutations from TCGA

-i ESMLID, --inqury_gene_file=ESMLID Ensembl id for your research gene

-g GENEID, --gene_id=GENEID input the gene name you want to inqure

-o OUTDIR, --output-dir=OUTDIR Output directory (default: current)

first step: download your mutation MAF files for TCGA portal (https://portal.gdc.cancer.gov/), typically there are four 
methods for TCGA to call somatic mutations. Choose either one or combine them.

second step: choose the gene list you would like to inquire about expression level. (please transfer the gene_id to Ensembl gene id)

third step: choose the gene that you're interested in its mutation. (support one gene)
