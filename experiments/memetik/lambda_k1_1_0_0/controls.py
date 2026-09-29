"""Real preflight: independent witnesses, all input pairs, largest model and kernels."""
import gc,sys
from common import *
from verify import checked,record,task_check


def main():
    directory=Path(sys.argv[1]);directory.mkdir(parents=True,exist_ok=True)
    manifest=read(HERE/'MANIFEST.json');roots={g['id']:g for g in manifest['founders']}
    for g in roots.values():
        v=record(g['graph6']);assert v['scores']==g['scores'] and v['state']==g['state']
    paired={}
    for t in manifest['tasks']:
        if t['kind']=='cp':
            task_check(roots[t['founder']]['graph6'],roots[t['founder']]['graph6'],t)
            if t['family']=='C1' and t['arm']=='D':
                task_check(roots[t['parent_b']]['graph6'],roots[t['founder']]['graph6'],t)
        if t['family']=='B':paired.setdefault((t['source_window'],t['seed']),[]).append(t)
    for group in paired.values():
        assert len(group)==4
        assert len({(t['founder'],tuple(t['vertices']),t['seed'],t['cpu_limit_seconds']) for t in group})==1
        assert {(t['linearization_level'],t['radius']) for t in group}=={(0,None),(0,16),(2,None),(2,16)}
    import k1_cp_tests
    k1_cp_tests.main()
    import k1_catalog_tests
    oldargv=sys.argv;sys.argv=['k1_catalog_tests','--pool',str(HERE/'CANDIDATES_25.json'),'--census',str(HERE/'STAR_CENSUS.json')]
    try:k1_catalog_tests.main()
    finally:sys.argv=oldargv
    import unittest,k1_packing_tests
    result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(k1_packing_tests))
    assert result.testsRun>=5 and result.wasSuccessful()
    # The largest variable window is calibrated only here, on the auxiliary account.
    from model import build
    from worker import evaluate_assignment
    largest=max((t for t in manifest['tasks'] if t['kind']=='cp'),key=lambda t:len(t.get('edge_mask',[])) if 'edge_mask' in t else len(t['vertices'])*(len(t['vertices'])-1)//2)
    rows,_=checked(roots[largest['founder']]['graph6'])
    m,e,o,mult,h=build(rows,largest.get('vertices',[]),edge_mask=largest.get('edge_mask'),radius=largest.get('radius'))
    evaluate_assignment(m,h)
    model_size={'variables':len(m.proto.variables),'constraints':len(m.proto.constraints),'proto_bytes':m.proto.ByteSize()}
    del m,e,o,h;gc.collect()
    atomic(directory/'result.json',{'status':'PASS','founders_checked':len(roots),'paired_B_cells':len(paired),'largest_model':model_size,'process_cpu_seconds':cpu(),'scope':'Kernel/constraint and witness controls; Windows scheduler test is separate; no full-size search guarantee'})


if __name__=='__main__':main()
