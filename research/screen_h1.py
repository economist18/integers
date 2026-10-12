import sys,json,importlib.util
from fractions import Fraction as Q
from collections import Counter
V=sys.argv[1]
def load(n):
 p=f'{V}/work/pr361/code/engines/{n}.py';s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=load('moment')
L484={1:2057,2:928,3:50,4:274,5:314,6:2,7:1,8:17}
L501={1:2385,2:264,3:530,4:84,5:270,6:92,7:1,8:17}
P505={1:148240,2:66816,3:7032,4:19728,5:26109,6:144,7:2209,8:1224,16:1,48:408}
P501={1:172056,2:19008,3:42032,4:6048,5:22496,6:6624,7:1800,8:4120}
idle=Counter(P505);[idle.subtract({r:72*n}) for r,n in L484.items()]
idle={r:n for r,n in idle.items() if n}
print('idle505',idle)
comp=Counter(idle);[comp.update({r:72*n}) for r,n in L501.items()];comp=dict(sorted(comp.items()))
print('composed',comp, 'mass',sum(r*n for r,n in comp.items()), 73*7680-sum(r*n for r,n in comp.items()))
for name,P in [('505',P505),('501',P501),('H1',comp)]:
 rc=M.certify(P,73,7680,True);print(name,rc['lower'])
