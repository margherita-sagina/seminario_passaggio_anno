"""Prepare updated presentation evidence without writing anywhere in CODICE."""
from pathlib import Path
import json,shutil,hashlib,subprocess,os
ROOT=Path(__file__).resolve().parent
ANALYSIS=Path('/Users/margherita/Desktop/UNIPI/TESI/CODICE/CODICI_PHASE-SHIFTS/PARALLEL-PETSC/Analisi/analysis_results')
manifest=json.loads((ROOT/'assets/provenance.json').read_text())
for name in ['LO_overview_results.txt','rcf0=1.500/clustering_results/NLO_Clusters_Report_rcf0_1.5_n_clusters_2_max_chi2_1.2.txt','rcf0=1.0/overview/NLO_Clusters_Report_rcf0_1.0_n_clusters_3_max_chi2_1.2.txt','rcf0=2.0/overview/NLO_Clusters_Report_rcf0_2.0_n_clusters_4_max_chi2_1.1.txt']:
 p=ANALYSIS/name; target=ROOT/'assets'/p.name;shutil.copyfile(p,target)
 manifest[p.name]={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
# Use locally copied, pre-existing compiled solver solely to evaluate selected LECs.
# No optimizer is run. All generated files and process working directory are local.
env=os.environ.copy();env['LAMBDA_N_DATA_FILE']=str(ROOT/'assets/experimental_cross_section.dat');env['LAMBDA_N_MAX_ENERGY_MEV']='220'
p=ROOT/'assets/cross_section_uncertainty_lo_r0_1p5.csv'
with (ROOT/'work/solver_corrected_lo.log').open('w') as log:
 subprocess.run([str(ROOT/'work/solver'),'LO','1.5',str(p),'-2.2261','0.1821'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copyfile(p,ROOT/'assets/lo_r01p5.csv')
manifest['lo_r01p5.csv']={'source':str(ANALYSIS/'LO_overview_results.txt'),'calculation':'Locally copied pre-existing solver, R0=1.5, Cs=-2.2261, Ct=0.1821. Rank 1 selected representative. No refit.','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
manifest['cross_section_uncertainty_lo_r0_1p5.csv']=manifest['lo_r01p5.csv']
(ROOT/'assets/provenance.json').write_text(json.dumps(manifest,indent=2))
print('Updated LO R0=1.5 evidence and copied analysis reports. Originals unchanged.')
