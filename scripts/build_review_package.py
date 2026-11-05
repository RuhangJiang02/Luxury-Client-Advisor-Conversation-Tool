"""Build an allowlisted private review package; never invokes model/evaluation APIs.

Existing archives are not overwritten. --stage-only/--finalize support logging
between the content audit and final archive creation.
"""
import argparse
import hashlib
import json
import re
import shutil
import zipfile
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from client_advisor import TOOL_VERSION, PROMPT_VERSION
VERSION=TOOL_VERSION.removeprefix('tool-')
BUILDER='chengxu-review-package-v2'
EVIDENCE={
 'runs/full-50-v0.8.2':'evidence/full-50',
 'runs/guardrails-v0.8.2':'evidence/guardrails',
 'runs/full-50-v0.7.1':'evidence/baseline-v0.7.1',
 'runs/full-50-v0.6.1':'evidence/baseline-v0.6.1-initial',
 'runs/full-50-recovery-v0.6.1':'evidence/baseline-v0.6.1-recovery',
 'runs/full-50-reconciled-v0.6.1':'evidence/baseline-v0.6.1',
 'runs/pre-freeze-regression-v0.6.1':'evidence/pre-freeze-regression-v0.6.1',
 'runs/source-repair-v0.7.0':'evidence/iterations/source-repair-v0.7.0',
 'runs/source-repair-v0.7.1':'evidence/iterations/source-repair-v0.7.1',
 'runs/composition-validation-v0.8.0':'evidence/iterations/composition-validation-v0.8.0',
 'runs/composition-validation-v0.8.1':'evidence/iterations/composition-validation-v0.8.1',
 'runs/composition-validation-v0.8.2':'evidence/iterations/composition-validation-v0.8.2',
}

# Keep current and new iteration paths portable for the source-linked verifier.
for item in ['full-50-v0.9.2','full-50-v0.9.3','full-50-v0.9.4','full-50-v0.9.5','full-50-v0.9.6','full-50-v0.9.7','guardrails-v0.9.7','quality-targets-v0.9.0','quality-targets-v0.9.1']:
 EVIDENCE['runs/'+item]='runs/'+item


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def build(name,stage_only=False,finalize=False):
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',name):raise ValueError('Use a plain archive name without path separators.')
 parent=ROOT/'submission';parent.mkdir(exist_ok=True)
 dest=parent/name;archive=parent/(name+'.zip');marker=dest/'PACKAGE_MANIFEST.json'
 if archive.exists():raise FileExistsError('Existing ZIP preserved; choose a new package name.')
 if dest.exists():
  if dest.is_symlink() or any(p.is_symlink() for p in dest.rglob('*')):raise ValueError('Refusing symbolic links in staging directory.')
  if not finalize or not marker.exists():raise FileExistsError('Existing directory preserved; choose a new name or finalize a staged package.')
  previous=json.loads(marker.read_text())
  if previous.get('builder')!=BUILDER or previous.get('package_name')!=name:raise ValueError('Not a staging folder from this builder.')
 else:
  if finalize:raise ValueError('No staged package exists.')
  dest.mkdir()
 marker.write_text(json.dumps({'builder':BUILDER,'package_name':name,'state':'staging'},indent=2)+'\n')
 def copy(source,target):
  if source.is_symlink():raise ValueError('Refusing symbolic-link input: '+str(source))
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 for directory in ['client_advisor','scripts','tests','data','examples','models','docs']:
  for p in (ROOT/directory).rglob('*'):
   if not p.is_file() or '__pycache__' in p.parts or any(part.startswith('.') for part in p.relative_to(ROOT/directory).parts):continue
   if p.suffix not in {'.py','.json','.md','.txt','.csv','.svg','.mmd'} and p.name!='Modelfile':continue
   copy(p,dest/p.relative_to(ROOT))
 for name_root in ['README.md','START_HERE.md','WORK_LOG.md','AGENTS.md','app.py','preview_service.py','requirements.txt','.gitignore','.env.example']:
  copy(ROOT/name_root,dest/name_root)
 copy(ROOT/'.streamlit/config.toml',dest/'.streamlit/config.toml');copy(ROOT/'submission/INDEX.md',dest/'INDEX.md')
 original_map=ROOT/'evidence/ORIGINAL_PATHS.json';fallback=json.loads(original_map.read_text()).get('prefixes',{}) if original_map.exists() else {}
 copied_evidence=[];used={}
 for original,target in EVIDENCE.items():
  source=ROOT/original
  if not source.exists() and original in fallback:source=ROOT/fallback[original]
  if not source.exists():
   if original in {'runs/full-50-v0.8.2','runs/guardrails-v0.8.2'}:raise FileNotFoundError('Required saved evidence missing: '+original)
   continue
  used[original]=target
  for p in source.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.json','.csv','.py','.md'}:
    q=dest/target/p.relative_to(source);copy(p,q);copied_evidence.append((p,q))
 (dest/'evidence/ORIGINAL_PATHS.json').write_text(json.dumps({'note':'Original artifact paths are preserved; prefixes map them to portable copies. Evidence is copied, not evaluated/regenerated.','prefixes':used},indent=2)+'\n')
 for p in dest.rglob('*.md'):
  text=p.read_text();text=re.sub(r'\[([^\]]+)\]\([^)]*Written_Challenge_Brief[^)]*\)',r'\1 (private brief excluded from package)',text)
  if p==dest/'README.md':text=text.replace('(submission/INDEX.md)','(INDEX.md)')
  if p==dest/'INDEX.md':text=text.replace('](../docs/','](docs/').replace('](../README.md)','](README.md)').replace('](../START_HERE.md)','](START_HERE.md)')
  p.write_text(text)
 files=[p for p in dest.rglob('*') if p.is_file()]
 for p in files:
  relative=p.relative_to(dest)
  if p.is_symlink() or p.name in {'.env','runs.sqlite3','ollama-server.log'} or p.suffix in {'.pdf','.gguf','.db','.sqlite3','.log'} or any(part in {'.venv','.venv-demo','.git','.models','__pycache__'} for part in relative.parts):raise ValueError('Forbidden package file: '+str(relative))
  if re.search(rb'sk-[A-Za-z0-9_-]{20,}',p.read_bytes()):raise ValueError('Potential credential pattern: '+str(relative))
 for directory in ['client_advisor','scripts','tests']:
  for p in (ROOT/directory).glob('*.py'):
   if p.read_bytes()!=(dest/p.relative_to(ROOT)).read_bytes():raise ValueError('Source copy mismatch.')
 for p,q in copied_evidence:
  if p.read_bytes()!=q.read_bytes():raise ValueError('Evidence copy mismatch.')
 broken=[]
 for p in dest.rglob('*.md'):
  for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',p.read_text()):
   link=unquote(link.strip('<>').split('#')[0])
   if not link or link.startswith(('https:','http:','mailto:','/')):continue
   if not (p.parent/link).exists():broken.append({'file':str(p.relative_to(dest)),'target':link})
 if broken:raise ValueError('Broken relative links: '+json.dumps(broken))
 freeze=json.loads((ROOT/'docs/verification'/('evaluation-freeze-'+VERSION+'.json')).read_text())
 if not all(sha(ROOT/p)==h for p,h in freeze.get('source_hashes',freeze.get('file_hashes',{})).items()):raise ValueError('Original measured runtime/input file changed; document a new version instead.')
 audit={'builder':BUILDER,'package_name':name,'verified_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'runtime_version':TOOL_VERSION+' / '+PROMPT_VERSION,'scope':'private review-package assembly; current strict AI review complete, genuine human quality acceptance pending','state':'draft; human quality acceptance incomplete','broken_relative_links':broken,'source_code_bytes_preserved':True,'saved_evidence_bytes_preserved':True,'original_frozen_files_unchanged':True,'sensitive_filename_and_credential_pattern_checks_passed':True,'new_model_calls':0,'case_evaluation_runs':0,'published_or_sent':False}
 auditpath=ROOT/'docs/verification'/('package-check-'+name+'.json');auditpath.write_text(json.dumps(audit,indent=2)+'\n');copy(auditpath,dest/'docs/verification'/auditpath.name)
 files=[p for p in dest.rglob('*') if p.is_file() and p!=marker]
 manifest={**audit,'state':'staged' if stage_only else 'archived draft','file_count_including_manifest':len(files)+1,'file_sha256':{str(p.relative_to(dest)):sha(p) for p in sorted(files)},'manifest_self_hash_omitted':True,'markdown_transformations':['Private brief links marked excluded','Package root index links corrected'],'original_path_map':'evidence/ORIGINAL_PATHS.json'}
 marker.write_text(json.dumps(manifest,indent=2)+'\n')
 if not stage_only:
  with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
   for p in sorted(dest.rglob('*')):
    if p.is_file():z.write(p,p.relative_to(parent))
  with zipfile.ZipFile(archive) as z:
   if z.testzip() is not None:raise ValueError('ZIP integrity check failed.')
  (parent/(name+'.sha256')).write_text(sha(archive)+'  '+archive.name+'\n')
 return {'package_folder':str(dest.relative_to(ROOT)),'file_count':len(files)+1,'archive':str(archive.relative_to(ROOT)) if not stage_only else None,'checks':'relative links, source/evidence equality, frozen hashes, sensitive patterns','actual_model_calls':0}


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--name',required=True)
 modes=p.add_mutually_exclusive_group();modes.add_argument('--stage-only',action='store_true');modes.add_argument('--finalize',action='store_true');modes.add_argument('--refresh-stage',action='store_true')
 a=p.parse_args();print(json.dumps(build(a.name,a.stage_only or a.refresh_stage,a.finalize or a.refresh_stage),indent=2))

if __name__=='__main__':main()
