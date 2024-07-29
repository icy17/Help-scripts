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

        result = fc.getArgument(0)
        and
        (
            // TODO-Target-change
            fc.getTarget().hasName("Free_API")
        )
}

 predicate isFreeFC(FunctionCall fc)
 {
    fc.getTarget().hasName("Free_API")
 }

 Expr getTargetExpr(FunctionCall fc)
 {
    result = fc.getArgument(Target_INDEX)
        and
        (
            // TODO-Target-change
            fc.getTarget().hasName("Target_Free")
        // or
        //  fc.getTarget().hasName("new_free")
        
        )
 }
 predicate isTargetFC(FunctionCall fc)
 {
 fc.getTarget().hasName("Target_Free")
 }

//  class MallocConfiguration extends DataFlow::Configuration {
//     MallocConfiguration() { this = "MallocConfiguration" }
   
//     override predicate isSource(DataFlow::Node source) {
//         exists(FunctionCall fc | 
//             source.asExpr() = fc
            
//         )
//         or exists(FunctionCall fc, AddressOfExpr ae | 
//             source.asDefiningArgument() = ae
//             and ae = fc.getAnArgument()
//             )
//       }
//      override predicate isSink(DataFlow::Node sink) {
//        // sink.asExpr()
//        exists(Expr e |
//          sink.asExpr() = e
//          or sink.asDefiningArgument() = e
//        )
//      }
//    }


   class FreeConfiguration extends DataFlow::Configuration {
    FreeConfiguration() { this = "FreeConfiguration" }
   
    override predicate isSource(DataFlow::Node source) {
        exists(FunctionCall fc | 
            (source.asDefiningArgument() = getFreeExpr(fc) or source.asExpr() = getFreeExpr(fc))
            and isFreeFC(fc)
        )
      }
     override predicate isSink(DataFlow::Node sink) {
        exists(FunctionCall fc | 
            (sink.asDefiningArgument() = getTargetExpr(fc) or sink.asExpr() = getTargetExpr(fc))
            and isTargetFC(fc)
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

  FunctionCall hasFlowtoAPI(FunctionCall fc) {
    isTargetFC(fc)
    and isFreeFC(result)
    and
    exists(FreeConfiguration p| 
        not fc = result
        and
        p.hasFlow(DataFlow::exprNode(getFreeExpr(result)), DataFlow::exprNode(getTargetExpr(fc)))
        )
}

//702-major-revision
//  target is a free function
from FunctionCall target, FunctionCall free
where
isFreeFC(target)
// and exists(FunctionCall malloc | isSourceFC(malloc) and target.getAPredecessor*() = malloc)
and free = hasFlowtoAPI(target)
and not exists(PointerFieldAccess fa | 
    getFreeExpr(target).getAChild*() = fa)
// Control Flow filter::
and 
(
    (free.getASuccessor+() = target
     and not exists(Assignment assign |
        (target.getASuccessor+() = assign and assign.getASuccessor+() = free)
      )
    )
    // or
    // (exists(FunctionCall fc | free.getEnclosingFunction() = fc.getTarget()
    // and fc.getASuccessor+() = target)
    
    // )
    // or
    // (
    //     exists(FunctionCall fc | target.getEnclosingFunction() = fc.getTarget()
    // and free.getASuccessor+() = fc
    // // and not exists(Assignment assign |
    // //     (fc.getASuccessor+() = assign and assign.getASuccessor+() = use)
    // //     or target.getASuccessor+() = assign
    // //   )
    //     )
    // )
    // or
    // (
    //     exists(FunctionCall fc1, FunctionCall fc2 | 
    //         target.getEnclosingFunction() = fc1.getTarget()
    //         and free.getEnclosingFunction() = fc2.getTarget()
    //         and fc2.getASuccessor+() = fc1
    //         )
    // )
)


select target, "Freed in " + free.getLocation().toString() + ". Dangle used in " + target.getLocation().toString()
