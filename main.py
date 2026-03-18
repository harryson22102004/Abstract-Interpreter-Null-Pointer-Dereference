# Abstract interpretation for null pointer analysis
class AbsVal:  # Abstract values: NULL, NONNULL, MAYBE_NULL, TOP
    NULL='NULL'; NONNULL='NONNULL'; MAYBE='MAYBE_NULL'; TOP='TOP'
 
def join(a, b):
    if a==b: return a
    if AbsVal.TOP in (a,b): return AbsVal.TOP
    return AbsVal.MAYBE
 
class NullPointerAnalyser:
    def __init__(self): self.env={}; self.warnings=[]
    def assign(self, var, val): self.env[var]=val
    def assign_new(self, var): self.env[var]=AbsVal.NONNULL
    def assign_null(self, var): self.env[var]=AbsVal.NULL
    def deref(self, var, line):
        v=self.env.get(var, AbsVal.MAYBE)
        if v==AbsVal.NULL:
            self.warnings.append(f"Line {line}: DEFINITE null dereference of '{var}'")
        elif v==AbsVal.MAYBE:
            self.warnings.append(f"Line {line}: POSSIBLE null dereference of '{var}'")
    def branch_null(self, var): self.env={**self.env, var: AbsVal.NULL}
    def branch_nonnull(self, var): self.env={**self.env, var: AbsVal.NONNULL}
    def merge(self, env1, env2):
        keys=set(env1)|set(env2)
        return {k: join(env1.get(k,AbsVal.TOP),env2.get(k,AbsVal.TOP)) for k in keys}
 
ai=NullPointerAnalyser()
# Simulate: int* p = malloc(...); if(p==NULL) return; *p = 5;
ai.assign_new('p')         # p = malloc(...)
ai.deref('p',3)            # *p = 5  → NONNULL, ok
ai.assign_null('q')        # q = NULL
ai.deref('q',5)            # *q      → NULL dereference
r_env_null={**ai.env,'r':AbsVal.NULL}
r_env_nonnull={**ai.env,'r':AbsVal.NONNULL}
merged=ai.merge(r_env_null,r_env_nonnull)
ai.env=merged; ai.deref('r',10)  # After join → MAYBE
print("Warnings found:"); [print(f"  {w}") for w in ai.warnings]
