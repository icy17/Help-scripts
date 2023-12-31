/**
 * @name UAF
 * @description description
 * @kind problem
 * @problem.severity error
 * @precision high
 * @id cpp/UAF
 * @tags security
 */

 import cpp
 import semmle.code.cpp.dataflow.TaintTracking
 import semmle.code.cpp.dataflow.DataFlow
 import semmle.code.cpp.security.Security
 import semmle.code.cpp.controlflow.Guards
 import semmle.code.cpp.valuenumbering.GlobalValueNumbering
 
Expr getMallocExpr(FunctionCall fc)
{
    exists(Expr e | 
        result = e
        and
        (
            (fc.getTarget().hasName("malloc_parameter") and e = fc)
        // or
        // (fc.getTarget().hasName("new_malloc") and e = fc.getArgument(0))
        // TODO-addMallocHere
        )
    )
}


FunctionCall getFreeClass()
{
    exists(FunctionCall fc | 
    fc.getTarget().hasName("free")
    and result = fc
    )
}

Expr getFreeExpr(FunctionCall fc)
{

        result = fc.getArgument(Target_INDEX)
        and
        (
            // TODO-Target-change
            fc.getTarget().hasName("Target_API")
        // or
        //  fc.getTarget().hasName("new_free")
        
        )
}
 predicate isSourceFC(FunctionCall fc)
 {
//  fc.getTarget().hasName("new_malloc")
//  or 
// // TODO-addMallocFCHere
 fc.getTarget().hasName("malloc")
 }

 predicate isSinkFC(FunctionCall fc)
 {
 fc.getTarget().hasName("Target_API")
//  or
//  fc.getTarget().hasName("new_free")
 }
 DataFlow::Node getSinkNode(FunctionCall fc)
 {
     result.asExpr() = getFreeExpr(fc)
     or
     result.asDefiningArgument() = getFreeExpr(fc)
 }
    
 DataFlow::Node getSourceNode(FunctionCall fc)
 {
     result.asExpr() = getMallocExpr(fc)
     or
     result.asDefiningArgument() = getMallocExpr(fc)
 }
 class MallocConfiguration extends DataFlow::Configuration {
    MallocConfiguration() { this = "MallocConfiguration" }
   
     override predicate isSource(DataFlow::Node source) {
       exists(FunctionCall fc | 
        isSourceFC(fc)
        and
        source = getSourceNode(fc)
         )
     }
     override predicate isSink(DataFlow::Node sink) {
       // sink.asExpr()
       exists(FunctionCall fc |
         isSinkFC(fc)
         and sink = getSinkNode(fc)
       )
     }
   }

 predicate isLocalVariable(Expr e) {
     exists(LocalVariable lv | 
        exists(FunctionCall fc| 
            fc = e and
            exists(AssignExpr ae | 
            ae.getAChild() = fc and lv.getAnAccess() = ae.getLValue())
        )
            or
            lv.getAnAccess() = e
            )
 }
 
 from FunctionCall target
 where
isSinkFC(target)
//  and 
// isLocalVariable(getMallocExpr(target))
 and  exists(FunctionCall free | 
    free = getFreeClass()
    and free.getASuccessor*() = target
    and not exists(FunctionCall malloc, MallocConfiguration cfg | 
        free.getASuccessor*() = malloc 
        and
        isSourceFC(malloc)
    and malloc.getASuccessor*() = target
    and
    cfg.hasFlow(getSourceNode(malloc), getSinkNode(target))
    )
        )

 select target, target.getLocation().toString()