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

 predicate isFreeFC(FunctionCall fc)
 {
 fc.getTarget().hasName("Target_API")
 }

 class MallocConfiguration extends DataFlow::Configuration {
    MallocConfiguration() { this = "MallocConfiguration" }
   
    override predicate isSource(DataFlow::Node source) {
        exists(FunctionCall fc | 
            source.asExpr() = fc
            
        )
        or exists(FunctionCall fc, AddressOfExpr ae | 
            source.asDefiningArgument() = ae
            and ae = fc.getAnArgument()
            )
      }
     override predicate isSink(DataFlow::Node sink) {
       // sink.asExpr()
       exists(Expr e |
         sink.asExpr() = e
         or sink.asDefiningArgument() = e
       )
     }
   }


   class FreeConfiguration extends DataFlow::Configuration {
    FreeConfiguration() { this = "FreeConfiguration" }
   
    override predicate isSource(DataFlow::Node source) {
        exists(FunctionCall fc | 
            (source.asDefiningArgument() = getFreeExpr(fc) or source.asExpr() = getFreeExpr(fc))
            and isFreeFC(fc)
        )
      }
     override predicate isSink(DataFlow::Node sink) {
        exists(PointerDereferenceExpr e |
                sink.asExpr() = e
              )
             or
        exists(PointerFieldAccess fa, Expr e |
                fa.getAChild() = sink.asExpr()
              )
     }
     override predicate isBarrier(DataFlow::Node barrier) {
        exists(Assignment assign |
          barrier.asExpr() = assign.getLValue()
        )
        or
        exists(AddressOfExpr ae, FunctionCall fc| 
            barrier.asDefiningArgument() = ae
            and fc.getAnArgument() = ae
            )
   }
}
   Expr test(PointerFieldAccess fa) {
    
    result = fa.getAChild()
   }

   Expr hasFlowtoAPI(FunctionCall fc) {
    isFreeFC(fc)
    and
    exists(FreeConfiguration p| 
        not fc.getAnArgument() = result
        and
        p.hasFlow(DataFlow::exprNode(getFreeExpr(fc)), DataFlow::exprNode(result))
        )
}

//2024.7.1
//  target is a free function
from FunctionCall target, Expr use
where
isFreeFC(target)
// and exists(FunctionCall malloc | isSourceFC(malloc) and target.getAPredecessor*() = malloc)
and use = hasFlowtoAPI(target)
and not exists(PointerFieldAccess fa | 
    getFreeExpr(target).getAChild*() = fa)
// Control Flow filter::
// and target.getEnclosingFunction().hasName("store_info_free")
and 
(
    (target.getASuccessor+() = use
     and not exists(Assignment assign |
        (target.getASuccessor+() = assign and assign.getASuccessor+() = use)
      )
    )
    // or
    // (exists(FunctionCall fc | use.getEnclosingFunction() = fc.getTarget()
    // and target.getASuccessor+() = fc)
    // // )
    // or
    // (
    //     exists(FunctionCall fc | target.getEnclosingFunction() = fc.getTarget()
    //     and not exists(PointerFieldAccess fa | fc.getAnArgument() = fa)
    // and fc.getASuccessor+() = use
    // and not exists(Assignment assign |
    //     (fc.getASuccessor+() = assign and assign.getASuccessor+() = use)
    //     or target.getASuccessor+() = assign
    //   )
    //     )
    // )
    // or
    // (
    //     exists(FunctionCall fc1, FunctionCall fc2 | 
    //         target.getEnclosingFunction() = fc1.getTarget()
    //         and use.getEnclosingFunction() = fc2.getTarget()
    //         and fc1.getASuccessor+() = fc2
    //         )
    // )
)


select target, "Freed in " + target.getLocation().toString() + ". Used in " + use.getLocation().toString()
