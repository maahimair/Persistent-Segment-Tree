import sys
from collections import deque
d=list(map(int,sys.stdin.read().split())); it=iter(d)
n=next(it); q=next(it)
vals=[next(it) for _ in range(n)]
comp=sorted(set(vals)); m=len(comp); idx={v:i for i,v in enumerate(comp)}
a=[0]+[idx[v] for v in vals]
g=[[] for _ in range(n+1)]
for _ in range(n-1):
    u=next(it); v=next(it); g[u].append(v); g[v].append(u)

L=[0];R=[0];C=[0]
def nn(l=0,r=0,c=0): L.append(l); R.append(r); C.append(c); return len(C)-1
def upd(p,l,r,x):
    cur=nn(L[p],R[p],C[p]+1)
    if l+1==r: return cur
    mid=(l+r)//2
    if x<mid: L[cur]=upd(L[p],l,mid,x)
    else: R[cur]=upd(R[p],mid,r,x)
    return cur
def kth(ru,rv,rl,rr,l,r,k):
    while l+1<r:
        mid=(l+r)//2
        lc=C[L[ru]]+C[L[rv]]-C[L[rl]]-C[L[rr]]
        if k<=lc:
            ru,rv,rl,rr=L[ru],L[rv],L[rl],L[rr]; r=mid
        else:
            k-=lc; ru,rv,rl,rr=R[ru],R[rv],R[rl],R[rr]; l=mid
    return l

par=[0]*(n+1); depth=[0]*(n+1); order=[]
dq=deque([1])
while dq:
    u=dq.popleft(); order.append(u)
    for v in g[u]:
        if v==par[u]: continue
        par[v]=u; depth[v]=depth[u]+1; dq.append(v)

LOG=(n).bit_length()
up=[par[:] for _ in range(LOG)]
for k in range(1,LOG):
    for v in range(1,n+1): up[k][v]=up[k-1][ up[k-1][v] ]

root=[0]*(n+1)
for u in order: root[u]=upd(root[par[u]] if par[u] else 0,0,m,a[u])

def lca(u,v):
    if depth[u]<depth[v]: u,v=v,u
    diff=depth[u]-depth[v]; k=0
    while diff:
        if diff&1: u=up[k][u]
        diff>>=1; k+=1
    if u==v: return u
    for k in range(LOG-1,-1,-1):
        if up[k][u]!=up[k][v]:
            u=up[k][u]; v=up[k][v]
    return up[0][u]

out=[]
for _ in range(q):
    u=next(it); v=next(it); kq=next(it)
    LCA=lca(u,v); PL=up[0][LCA]; rpar=root[PL] if PL else 0
    tot=C[root[u]]+C[root[v]]-C[root[LCA]]-C[rpar]
    out.append("invalid" if not (1<=kq<=tot) else str(comp[kth(root[u],root[v],root[LCA],rpar,0,m,kq)]))
print("\n".join(out))
