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
 
     
Expr getTargetExpr(FunctionCall fc)
{
    // CHANGE
    result = fc.getArgument(0) 
}

 predicate isTargetFC(FunctionCall fc)
 {
    // CHANGE
 fc.getTarget().hasName("target")
 }

 predicate isbeforeFC(FunctionCall fc)
 {
    // CHANGE
 fc.getTarget().hasName("target-before")
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

//  predicate isConditional(BasicBlock bb) {
//     exists(GuardCondition g | 
//        g.controls(bb, _) 
//        )
    
//  }
 
//  API XX must be called before target
 from FunctionCall target
 where
 isTargetFC(target)
 and isLocalVariable(getTargetExpr(target))
 and not exists(FunctionCall beforefc | 
    isbeforeFC(beforefc)
    and beforefc.getASuccessor*() = target
    )

//  and after.getTarget().hasName("free")
 // and not exists(Expr check| check=getCheckExpr(target))
//  and bb = getLeakBBBefore(target)
 select target, target.getLocation().toString()
 