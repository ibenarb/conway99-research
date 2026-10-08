"""Fail-closed production preflight; only small controls may start native work."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import accounting
import preflight as p
import runtime as r


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--worker',type=Path,required=True)
    parser.add_argument('--checker',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve();out.mkdir(exist_ok=False)
    repo=Path(__file__).resolve().parents[3]
    rows=[]
    def record(name,**details):
        rows.append(dict(test=name,passed=True,**details));print(name,'PASS',flush=True)
    def command(root,action,*extra):
        log=out/(root.name+'-'+action+'-'+str(time.time_ns())+'.log')
        with log.open('wb') as stream:
            result=subprocess.run([sys.executable,r.__file__,action,str(root),*map(str,extra)],
                stdout=stream,stderr=subprocess.STDOUT)
        return result.returncode,log
    def init(root,cnf,*extra):
        return command(root,'init','--cnf',cnf,'--worker',args.worker,'--checker',args.checker,
                       '--budget',60,*extra)[0]
    def rejected(operation):
        try:operation()
        except (ValueError,OSError):return
        raise AssertionError('invalid preflight input accepted')
    cnf=out/'small.cnf';cnf.write_text('p cnf 1 1\n1 0\n')
    root=out/'control'
    require(init(root,cnf)==0,'control init')
    report=p.inspect(root)
    require(report['allowed'] and report['status']=='CONTROL_READY' and
            not report['production_launch_authorized'],'control readiness')
    require(command(root,'run')[0]==0 and r.read(root/'state.json')['status']=='SAT_CNF_VERIFIED',
            'control start')
    record('small_control_preflight_and_native_start_allowed')

    # Real inputs are recovered from the immutable archived calibration, never solved.
    archive=repo/'docs/augmentation/root8105_n1_20261006/CLASSES.tar.xz'
    catdir=repo/'docs/augmentation/root8105_n1_catalog_20261007'
    catalog=catdir/'CATALOG_RECEIPT.json'
    require(r.sha(catalog)==p.CATALOG_SHA256,'test catalogue source hash')
    production=[]
    with tarfile.open(archive) as t:
        for rid in (210,6682):
            cnf=out/('r%d.cnf'%rid)
            cnf.write_bytes(t.extractfile('r%d_class000.cnf'%rid).read())
            binding=catdir/('r%d_class000_binding.json'%rid)
            rejected(lambda:p.control_input(cnf,binding))
            root=out/('production%d'%rid)
            require(init(root,cnf,'--binding',binding,'--catalog',catalog,'--profile','n1-production',
                '--total-budget',120,'--max-rss-bytes',2**30,'--min-free-bytes',2**27,
                '--min-available-bytes',2**27)==0,'production inspection init')
            before={str(f.relative_to(root)):r.sha(f) for f in root.rglob('*') if f.is_file()}
            report=p.inspect(root)
            after={str(f.relative_to(root)):r.sha(f) for f in root.rglob('*') if f.is_file()}
            require(before==after,'inspection modified run')
            passed={x['name'] for x in report['checks'] if x['passed']}
            require({'catalogue_binding','mandatory_guard_and_budget_history','bound_CLI_account_history'}<=passed,
                    'valid catalogue or guard rejected')
            require(not report['allowed'] and 'target_hardware_acceptance' in report['blockers'],
                    'production released without target acceptance')
            r.raw_atomic(out/('PREFLIGHT_ROOT_%d.json'%rid),report)
            for action in ('run','resume'):
                require(command(root,action)[0]!=0,'production native launch was not blocked')
            require(not list((root/'attempts').iterdir()),'blocked preflight launched child')
            require(before=={n:r.sha(root/n) for n in before},'blocked start changed original files')
            production.append(root)
    record('both_real_class_zero_bindings_pass_catalogue_but_run_and_resume_are_blocked')
    record('real_N1_inputs_cannot_use_small_control_profile')
    record('inspection_read_only_and_blocked_start_preserves_scientific_state')

    root=production[0]
    m=r.read(root/'manifest.json');s=r.read(root/'state.json')
    # A forged old PASS file and editable approval flag are not start capabilities.
    r.raw_atomic(root/'preflights'/'forged.json',dict(allowed=True,production_launch_authorized=True))
    changed=dict(m,production_approved=True)
    r.raw_atomic(root/'manifest.json',changed)
    require(command(root,'run')[0]!=0 and not list((root/'attempts').iterdir()),'forged PASS granted launch')
    r.raw_atomic(root/'manifest.json',m)
    record('cached_PASS_and_manifest_approval_flag_cannot_grant_start')
    # Changing the profile cannot turn a large root CNF into a control.
    r.raw_atomic(root/'manifest.json',dict(m,execution_profile='control'))
    require(command(root,'run')[0]!=0 and not list((root/'attempts').iterdir()),'profile downgrade bypass')
    r.raw_atomic(root/'manifest.json',m)
    record('resealed_profile_downgrade_cannot_bypass_input_scope')
    report=p.inspect(root,dict(m,guard=None))
    require('mandatory_guard_and_budget_history' in report['blockers'],'missing guard accepted')
    record('production_guard_is_mandatory')
    report=p.inspect(root,dict(m,catalog_sha256=None))
    require('catalogue_binding' in report['blockers'],'missing catalogue accepted')
    record('production_catalogue_is_mandatory')
    old=(root/'catalog.json').read_bytes()
    (root/'catalog.json').write_bytes(old+b' ')
    require('catalogue_binding' in p.inspect(root)['blockers'],'modified catalogue accepted')
    (root/'catalog.json').write_bytes(old)
    record('byte_changed_catalogue_rejected')
    other=(production[1]/'binding.json').read_bytes()
    original=(root/'binding.json').read_bytes();(root/'binding.json').write_bytes(other)
    require('catalogue_binding' in p.inspect(root)['blockers'],'wrong root binding accepted')
    (root/'binding.json').write_bytes(original)
    record('binding_from_other_root_rejected')
    # Explicit preflight CLI is measured but does not create a scientific attempt.
    code,log=command(root,'preflight')
    require(code==0 and '"status": "BLOCKED"' in log.read_text() and
            not list((root/'attempts').iterdir()),'preflight inspection CLI')
    record('preflight_CLI_reports_blockers_without_solver')

    # Map the process's actual hierarchy path through mountinfo; do not assume
    # the filesystem root is its cgroup. Ancestor constraints must also appear.
    fixture=out/'cgroup fixture';child=fixture/'team';child.mkdir(parents=True)
    for path,limit,current in ((fixture,1000,400),(child,2000,100)):
        for name,value in {'memory.max':str(limit),'memory.high':'max','memory.current':str(current),
                           'cpu.max':'max 100000','memory.events':'oom 0\noom_kill 0'}.items():
            (path/name).write_text(value+'\n')
    mountpoint=str(fixture).replace(' ','\\040')
    mount='1 0 0:1 / '+mountpoint+' ro - cgroup2 cgroup2 rw\n'
    probe=p.cgroup_probe('0::/team\n',mount)
    require(probe['visible_memory_ceiling_bytes']==1000 and probe['visible_memory_headroom_bytes']==600
            and len(probe['visible_ancestors'])==2,'ancestor or escaped mount mapping')
    require(probe['mount_read_only'] and not probe['limits_modified'],'probe altered limits')
    record('cgroup_mount_mapping_and_tighter_visible_ancestor_checked')
    (child/'memory.current').unlink()
    rejected(lambda:p.cgroup_probe('0::/team\n',mount))
    rejected(lambda:p.cgroup_probe('0::/../escape\n',mount))
    record('missing_cgroup_counter_and_path_escape_fail_closed')
    data=dict(complete=True,tests=rows,N1_class_searches=0,production_approved=False,
              host_probe=p.host_probe())
    r.raw_atomic(out/'TEST_RESULTS.json',data)
    print('PASS',len(rows),flush=True)


if __name__=='__main__':
    main()
