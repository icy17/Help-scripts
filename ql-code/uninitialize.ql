/**
 * @name uninitialize
 * @description description
 * @kind problem
 * @problem.severity error
 * @precision high
 * @id cpp/uninitialize
 * @tags security
 */

 import cpp
 import semmle.code.cpp.dataflow.TaintTracking
 import semmle.code.cpp.dataflow.DataFlow
 import semmle.code.cpp.security.Security
 import semmle.code.cpp.controlflow.Guards
 import semmle.code.cpp.valuenumbering.GlobalValueNumbering
 

 predicate isTargetFC(FunctionCall fc)
 {
 fc.getTarget().hasName("Target_API")
 }

//  DataFlow::Node getSourceNode(FunctionCall fc)
//  {
//      result.asExpr() = getMallocExpr(fc)
//      or
//      result.asDefiningArgument() = getMallocExpr(fc)
//  }

 Expr getTargetExpr(FunctionCall fc)
 {
    isTargetFC(fc)
    and
 result = fc.getArgument(Target_INDEX) 
 }


//  class PathConfiguration extends DataFlow::Configuration {
//     PathConfiguration() { this = "PathConfiguration" }
   
//      override predicate isSource(DataFlow::Node source) {
//        exists(FunctionCall fca, AddressOfExpr ae| 
//             source.asExpr() = ae.getAChild+()
//             and fca.getAnArgument() = ae
//             )
//      }
//      override predicate isSink(DataFlow::Node sink) {
//        // sink.asExpr()
//        exists(FunctionCall fc |
//         isTargetFC(fc)
//         and
//         sink.asExpr() = getTargetExpr(fc)
//     )
//      }
//    }

//    DataFlow::Node hasFlowtoAPI(FunctionCall fc) {
//     isTargetFC(fc)
//     and
//     exists(PathConfiguration p, DataFlow::Node source| 
//         p.hasFlow(source, DataFlow::exprNode(getTargetExpr(fc)))
//       and source.asExpr().getEnclosingFunction() = fc.getEnclosingFunction()
//       and result = source
//         )
// }
 predicate isAssignBefore(Expr e) {
    exists(Variable v, Initializer i|
        v.getAnAccess() = e
        and v.getInitializer() = i
  )
  or
  exists(Assignment a, Variable v| 
    v.getAnAccess() = e
    and v.getAnAccess() = a.getLValue()
    )
}

predicate isAddressAssign(Expr e) {
  exists(FunctionCall fc, AddressOfExpr ae, Variable v| 
    fc.getAnArgument() = ae
    and fc.getASuccessor+() = e
    and v.getAnAccess() = e
    and v.getAnAccess() = ae.getAChild+()
    )
  
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
 

 
 //0703-major
 from FunctionCall target
 where
 isTargetFC(target)
 and not isAssignBefore(getTargetExpr(target))
 and not isAddressAssign(getTargetExpr(target))
 select target, target.getLocation().toString()
 