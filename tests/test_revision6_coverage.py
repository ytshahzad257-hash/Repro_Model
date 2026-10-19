from apr.model import TransitionSystem
from apr.explorer import explore,self_composition
from apr.policies import Configuration

def test_approved_release_is_not_raw_noninterference():
    s=TransitionSystem('ApprovedSecretRelease')
    assert explore(s,0).info_safe and explore(s,1).info_safe
    assert self_composition(s).witness is not None
    assert self_composition(s,payload_only=True).witness is not None
    assert self_composition(s,equal_release=True).witness is None

def test_named_refusal_mutation_is_observable():
    s=TransitionSystem('RefusalMutation')
    assert self_composition(s).witness is not None
    assert self_composition(s,payload_only=True).witness is None

def test_independent_nonrevoked_source_remains_usable():
    s=TransitionSystem('Governed',3,secrets='independent',revoked={0})
    st=s.initial(2)
    for a in ['RequestRevoke','UpdatePolicy','Isolate','Fence','Persist','CommitCut','Read[1]','Derive[1]','Load[1]']:
        st=s.successor(st,a).target
    t=s.successor(st,'OpUse')
    assert t.observation.payload==2 and s.info_safe(t.target)
    assert self_composition(s,left_secret=2,right_secret=3).witness is None

def test_cut_clears_revoked_session_cache_but_preserves_allowed_cache():
    s=TransitionSystem('Governed',2,secrets='independent',revoked={0})
    st=s.initial(0)
    for a in ['Read[0]','Derive[0]','Load[0]','Read[1]','Derive[1]','Load[1]','RequestRevoke','UpdatePolicy','Isolate']:
        st=s.successor(st,a).target
    assert st.session_cache==(False,True) and st.loaded==(False,True)

def test_session_extension_preserves_original_verdicts():
    for c in list(Configuration)[:7]:
        with_cache=TransitionSystem(c,session_cache=True)
        without=TransitionSystem(c,session_cache=False)
        for bit in (0,1):
            x,y=explore(with_cache,bit),explore(without,bit)
            assert (x.info_safe,x.auth_safe,x.review_failures>0)==(y.info_safe,y.auth_safe,y.review_failures>0)
        for payload in (False,True):
            assert (self_composition(with_cache,payload_only=payload).witness is None)==(self_composition(without,payload_only=payload).witness is None)
