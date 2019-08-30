#!/usr/bin/env python

"""
Script Created by Yue. 
version = beta1, Date:2019/8/30
TCGA data caseid UUID and RNA expression combine
Need to downlowad the case_id that you needed from TCGA, this script begin with the clinical meta data file
"""

from optparse import OptionParser
import subprocess
import commands
import sys
import os
import json
from urllib import quote
import gzip


####input paramater####
parser = OptionParser()
parser.add_option("-f", "--input_file", help='clinical information from TCGA portal', dest='MAF')
parser.add_option("-i", "--inqury_gene_file", help='Ensembl id for your research gene', dest='esmlid')
parser.add_option('-o', '--output-dir', help='Output directory (default: current)', dest='outdir', default='.')
(options, args) = parser.parse_args()

####extract esem-list####
def eml(esmlid):
    esm_list = []
    with open (esmlid, 'r') as esm_f:
        for line in esm_f:
            l_i = line.rstrip()
            esm_list.append(l_i)
    return esm_list
        
####extract FPKM-data####
def FPKMdata(UUID):
    files_endpt = 'https://api.gdc.cancer.gov/files?filters='
    parm = '{"op":"and","content":[{"op":"in","content":{"field":"cases.case_id","value":["%s"]}},{"op":"=","content":{"field":"files.data_type","value":"Gene Expression Quantification"}}]}' %(UUID)
    files_ending = '&pretty=true'
    j_parm = quote(parm)
    FPKM_url = files_endpt + j_parm + files_ending
    commands.getoutput('curl "%s" > %s_FPKMdata.json' %(FPKM_url, UUID))
    exp_endpt = 'https://api.gdc.cancer.gov/data/'
    load_d = jdc(('%s_FPKMdata.json') %(UUID))
    count = 0
    exp_nm_l = []
    for i in range(len(load_d['data']['hits'])):
        if 'FPKM.txt.gz' in load_d['data']['hits'][i]['file_name']:
            print load_d['data']['hits'][i]['file_name']
            exp_nm = load_d['data']['hits'][i]['file_name']
            exp_id = load_d['data']['hits'][i]['file_id']
            exp_url = exp_endpt + exp_id
            commands.getoutput('curl --remote-name --remote-header-name %s' %(exp_url))
            commands.getoutput('curl "https://api.gdc.cancer.gov/files/"%s"?expand=cases.samples&pretty=true" > %s.json' %(exp_id, exp_nm))
            exp_nm_l.append(exp_nm)
            count = count + 1
            #exp_extract_command = 'cat %s | while read line;do zgrep ${line} %s >> expression.txt;done' %(options.esmlid, exp_nm)                    
        else:
            continue
    print "total sample type" + "\t" + str(count)
    return exp_nm_l
            
####gene-FPKM-level####
def FPKML(exp_nm):
    f_d = {}
    with gzip.open(exp_nm, 'r') as FL:
        for line in FL:
            #(key, value) = line.rstrip().split("\t")
            key = line.rstrip().split("\t")[0].split(".")[0]
            value = line.rstrip().split("\t")[1]
            f_d[key] = value
    return f_d        
            
####json-decode####
def jdc(jfile):
    with open(jfile, 'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict

####read MAF file####
with open ('combined_infor.xls', 'w') as fin:
    with open (options.MAF, 'r') as origl:
        esm_list = eml(options.esmlid)
        for line in origl:
            l_item = line.rstrip().split("\t")
            if 'case_id' in l_item:
                UUID_id = l_item.index("case_id")
                fin.write("\t".join(l_item + esm_list) + "\t" + "sample_type" + "\n")
            else:
                print "#############"
                print l_item[UUID_id]
                exp_nm_l = FPKMdata(l_item[UUID_id])
                for f in exp_nm_l:
                    exp_num = []
                    FL = FPKML(("%s") %(f))
                    sample_type = jdc(('%s.json')%(f))['data']['cases'][0]['samples'][0]['sample_type']
                    for i in esm_list:
                        if i in FL.keys():
                            exp_num.append(str(FL[i]))
                    fin.write("\t".join(l_item+exp_num) + "\t" + str(sample_type) + "\n")
                else:
                    continue
                
origl.close()
fin.close()