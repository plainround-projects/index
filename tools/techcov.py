"""Tech-notes coverage check.

For every repository under the parent folder (or the one repository given as
the second argument), count the non-blank, non-comment lines of every tracked
source, script and configuration file (docs, tech notes, data and binary files
are skipped) and report how many of those lines are quoted somewhere in the
repository's tech/*.md files. The acceptance bar is 95 percent per repository
(TEMPLATE.md, "Technology notes").

Usage: python3 tools/techcov.py <report.json> [repo-folder-name]
"""
import os, subprocess, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_EXT={'.md','.png','.jpg','.jpeg','.gif','.svg','.ico','.pdf','.lock','.sum','.jar','.gguf','.bin','.parquet','.csv','.json','.txt','.log','.gz','.zip','.woff','.woff2','.ttf'}
SKIP_DIR=('tech/','docs/','.github/ISSUE','target/','node_modules/')
out=[]
ONLY=sys.argv[2] if len(sys.argv)>2 else None
for repo in sorted(os.listdir(ROOT)):
    if ONLY and repo!=ONLY: continue
    r=os.path.join(ROOT,repo)
    if not os.path.isdir(os.path.join(r,'.git')): continue
    tech=os.path.join(r,'tech')
    notes=''
    nfiles=0
    if os.path.isdir(tech):
        for f in os.listdir(tech):
            if f.endswith('.md'):
                nfiles+=1
                notes+=open(os.path.join(tech,f),errors='ignore').read()
    noteset=set(l.strip() for l in notes.splitlines() if l.strip())
    try:
        files=subprocess.run(['git','-C',r,'ls-files'],capture_output=True,text=True).stdout.split('\n')
    except Exception: files=[]
    tot=cov=0; worst=[]
    for f in files:
        if not f or f.startswith(SKIP_DIR) or os.path.splitext(f)[1].lower() in SKIP_EXT or f in('LICENSE','.gitignore','.editorconfig','CHANGELOG.md'): continue
        p=os.path.join(r,f)
        if not os.path.isfile(p) or os.path.getsize(p)>200000: continue
        try: lines=[l.strip() for l in open(p,errors='ignore').read().splitlines()]
        except Exception: continue
        lines=[l for l in lines if l and not l.startswith('#') and len(l)>3]
        if not lines: continue
        c=sum(1 for l in lines if l in noteset)
        tot+=len(lines); cov+=c
        if len(lines)>=8: worst.append((c/len(lines),f,c,len(lines)))
    worst.sort()
    pct= round(100*cov/tot,1) if tot else None
    out.append({'repo':repo,'tech_files':nfiles,'lines':tot,'quoted':cov,'pct':pct,'worst':[(round(100*w[0]),w[1],w[2],w[3]) for w in worst[:3]]})
json.dump(out,open(sys.argv[1],'w'),indent=1)
for o in sorted(out,key=lambda x:(x['pct'] if x['pct'] is not None else -1)):
    print(f"{o['pct']!s:>6} {o['tech_files']:>3} {o['quoted']:>6}/{o['lines']:<6} {o['repo']}")
    for w in o['worst']: print(f"           worst: {w[0]}% {w[1]} ({w[2]}/{w[3]})")
