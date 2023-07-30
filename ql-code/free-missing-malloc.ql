/**
 * @name squid
 * @description description
 * @kind problem
 * @problem.severity error
 * @precision high
 * @id cpp/squid
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
            (fc.getTarget().hasName("malloc_with_parameter") and e = fc)
        // or
        // (fc.getTarget().hasName("new_malloc") and e = fc.getArgument(0))
        // TODO-addMallocHere
        )
    )
}

Expr getFreeExpr(FunctionCall fc)
{

        result = fc.getArgument(Target_INDEX)
        and
        (
            fc.getTarget().hasName("Target_Free")
        // or
        //  fc.getTarget().hasName("new_free")
        // TODO-addFreeHere
        )
}
 predicate isSourceFC(FunctionCall fc)
 {
//  fc.getTarget().hasName("new_malloc")
//  or 
 fc.getTarget().hasName("malloc")
 }

 predicate isSinkFC(FunctionCall fc)
 {
 fc.getTarget().hasName("Target_Free")
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
 and not 
 exists(MallocConfiguration cfg, FunctionCall malloc| 
    isSourceFC(malloc)
    and malloc.getASuccessor*() = target
    and
    cfg.hasFlow(getSourceNode(malloc), getSinkNode(target))
    )

 select target, target.getLocation().toString()
 