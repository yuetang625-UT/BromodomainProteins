#!/usr/bin/env python

"""
Script Created by Yue. 
version = beta1, Date:2019/8/27
TCGA data caseid UUID and RNA expression combine
Need to downlowad the MAF files that you needed from TCGA, this script begin with the MAF file
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
parser.add_option("-f", "--input_file", help='MAF file contains the somatic mutations from TCGA', dest='MAF')
parser.add_option("-i", "--inqury_gene_file", help='Ensembl id for your research gene', dest='esmlid')
parser.add_option("-g", "--gene_id", help='input the gene name you want to inqure', dest='geneid')
parser.add_option('-o', '--output-dir', help='Output directory (default: current)', dest='outdir', default='.')
(options, args) = parser.parse_args()

'''try: 
    #os.mkdir('%s' %(options.outdir))
    os.chdir(os.path.dirname('%s' %(options.outdir)))
    #os.mkdir('fin_result')
except OSError,e:    
    print "output dir existence, check if you get your results" 
    #sys.exit()'''
    
###################calling external procedures method####################
def RunCommand(command,description):
    printtime(' ')
    printtime('Task    : ' + description)
    printtime('Command : ' + command)
    printtime(' ')
    stat = subprocess.call(command,shell=True)
    if stat != 0:
        printtime('ERROR: command failed with status %d' % stat)
        sys.exit(1)
                
####extract esem-list####
def eml(esmlid):
    esm_list = []
    with open (esmlid, 'r') as esm_f:
        for line in esm_f:
            l_i = line.rstrip()
            esm_list.append(l_i)
    return esm_list
        
            
####extract meta-data####
def metadata(UUID):
    cases_endpt = 'https://api.gdc.cancer.gov/cases?filters='
    cases_ending = '&expand=diagnoses,demographic&pretty=true'
    parm = '{"op":"and","content":[{"op":"in","content":{"field":"cases.case_id","value":["%s"]}}]}' %(UUID)
    j_parm = quote(parm)
    meta_url = cases_endpt + j_parm + cases_ending
    commands.getoutput('curl "%s" > metadata.json' %(meta_url))
    meta_infor = []
    meta_d = jdc('metadata.json')
    prim_diag = meta_d['data']['hits'][0]['diagnoses'][0]['primary_diagnosis']
    meta_infor.append(str(prim_diag))
    tum_s = meta_d['data']['hits'][0]['diagnoses'][0]['tumor_stage']
    meta_infor.append(str(tum_s))
    age = meta_d['data']['hits'][0]['diagnoses'][0]['age_at_diagnosis']
    meta_infor.append(str(age))
    gender = meta_d['data']['hits'][0]['demographic']['gender']
    meta_infor.append(str(gender))
    race = meta_d['data']['hits'][0]['demographic']['race']
    meta_infor.append(str(race))
    status = meta_d['data']['hits'][0]['demographic']['vital_status']
    meta_infor.append(str(status))
    return meta_infor
    

####extract FPKM-data####
def FPKMdata(UUID):
    files_endpt = 'https://api.gdc.cancer.gov/files?filters='
    parm = '{"op":"and","content":[{"op":"in","content":{"field":"cases.case_id","value":["%s"]}},{"op":"=","content":{"field":"files.data_type","value":"Gene Expression Quantification"}}]}' %(UUID)
    files_ending = '&pretty=true'
    j_parm = quote(parm)
    FPKM_url = files_endpt + j_parm + files_ending
    commands.getoutput('curl "%s" > FPKMdata.json' %(FPKM_url))
    exp_endpt = 'https://api.gdc.cancer.gov/data/'
    load_d = jdc('FPKMdata.json')
    for i in range(len(load_d['data']['hits'])):
        if 'FPKM.txt.gz' in load_d['data']['hits'][i]['file_name']:
            exp_nm = load_d['data']['hits'][i]['file_name']
            exp_id = load_d['data']['hits'][i]['file_id']
            exp_url = exp_endpt + exp_id
            commands.getoutput ('curl --remote-name --remote-header-name %s' %(exp_url))
                #exp_extract_command = 'cat %s | while read line;do zgrep ${line} %s >> expression.txt;done' %(options.esmlid, exp_nm)                    
        else:
            continue
    return exp_nm
            
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
m_all = ["prim_diag","tum_s","age","gender","race","status"]
with open ('combined_infor.xls', 'w') as fin:
    with open (options.MAF, 'r') as origl:
        esm_list = eml(options.esmlid)
        for line in origl:
            l_item = line.rstrip().split("\t")
            if 'Hugo_Symbol' in l_item:
                UUID_id = l_item.index("case_id")
                H_symbol = l_item.index("Hugo_Symbol")
                fin.write("\t".join(l_item + m_all + esm_list) + "\n")
                #fin.write("\n")
            else:
                if options.geneid in l_item[H_symbol]:
                    print "#############"
                    print l_item[UUID_id]
                    m_infor = metadata(l_item[UUID_id])
                    exp_num = []
                    exp_nm = FPKMdata(l_item[UUID_id])
                    FL = FPKML(("%s") %(exp_nm))
                    for i in esm_list:
                        if i in FL.keys():
                            exp_num.append(str(FL[i]))
                    fin.write("\t".join(l_item+m_infor+exp_num) + "\n")
                else:
                    continue
                
origl.close()
fin.close()
   