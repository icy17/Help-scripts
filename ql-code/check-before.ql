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
 
     
 Expr getSinkExpr(FunctionCall fc)
 {
 result = fc.getArgument(0) 
 }
 
 predicate isSinkFC(FunctionCall fc)
 {
 fc.getTarget().hasName("target")
 }
 DataFlow::Node getSinkNode(FunctionCall fc)
 {
     result.asExpr() = getSinkExpr(fc)
     or
     result.asDefiningArgument() = getSinkExpr(fc)
 }
    
 class ParameterConfiguration extends DataFlow::Configuration {
     ParameterConfiguration() { this = "ParameterConfiguration" }
   
     override predicate isSource(DataFlow::Node source) {
       exists(Expr rt | 
         rt = source.asExpr())
     }
     override predicate isSink(DataFlow::Node sink) {
       // sink.asExpr()
       exists(FunctionCall fc |
         isSinkFC(fc)
         and sink = getSinkNode(fc)
       )
     }
   }

ControlFlowNode getTargetNode() {
    exists(FunctionCall target | 
    target.getTarget().hasName("free")
    and result = target
    )
}
   
ControlFlowNode getAfterNode(ControlFlowNode target) {
    exists(FunctionCall fc | 
        fc.getTarget().hasName("free")
        and target.getASuccessor*() = fc
        and result = fc)
}

ControlFlowNode getBeforeNode(ControlFlowNode target) {
    exists(FunctionCall fc | 
        fc.getTarget().hasName("malloc")
        and target.getAPredecessor*() = fc
        and result = fc)
}

// return True说明该node是 conditional的，会leak
predicate isConditionalBefore(ControlFlowNode node, ControlFlowNode target) {
    target = getTargetNode()
    and
    node = getBeforeNode(target)
    and
    exists(BasicBlock bb | 
        bb.getASuccessor().getANode() = node
        and bb.getASuccessor().getANode() = target
        )
}
// return True说明该node是 conditional的，会leak
predicate isConditionalAfter(ControlFlowNode node, ControlFlowNode target) {
    target = getTargetNode()
    and
    node = getBeforeNode(target)
    and
    exists(BasicBlock bb | 
        bb.getAPredecessor().getANode() = node
        and bb.getAPredecessor().getANode() = target
        )
}

BasicBlock getLeakBBBefore(ControlFlowNode target)
{
    not exists(ControlFlowNode node | 
        node = getBeforeNode(target)
        and (not
        exists(BasicBlock bb | 
            bb.getASuccessor*() = target
            // and bb.getAPredecessor*() = node
            and not bb.getANode() = node
        and result = bb
        and not bb.getAPredecessor*() = node.getBasicBlock()
        and not bb.getASuccessor*() = node.getBasicBlock()
        )
        and not isConditionalBefore(node, target)
        )
        )
}

 //   if every path after target exists node
BasicBlock getLeakBBAfter(ControlFlowNode target) {
     not exists(ControlFlowNode node | 
        node = getAfterNode(target)
        and (not
        exists(BasicBlock bb | 
            not bb.getANode() = node
            and bb = target.getASuccessor*()
            and exists(ExitBasicBlock exit | 
                bb.getASuccessor*() = exit)
            and target.getASuccessor*() = bb
            and not bb.getAPredecessor*() = node.getBasicBlock()
            and not bb.getASuccessor*() = node.getBasicBlock()
            and result = bb
         )
         and not isConditionalAfter(node, target)
        )
     )
    
 }
 
 Expr getCheckExpr(FunctionCall fc)
 {
     isSinkFC(fc)
     and exists(ParameterConfiguration cfg, Expr source|
         cfg.hasFlow(DataFlow::exprNode(source), getSinkNode(fc)
         )
         and
     result = source
     )
     
 }
 
 Expr getSourceOfFc(FunctionCall fc)
 {
     isSinkFC(fc)
     and exists(ParameterConfiguration cfg, Expr source|
         cfg.hasFlow(DataFlow::exprNode(source), getSinkNode(fc)
         )
         and
     result = source
     and result.getASuccessor*() = fc
     and not result = getSinkExpr(fc)
     )
 }
 
 
 predicate isLocalVariable(Variable v) {
     exists(LocalVariable lv | lv = v)
 }
 
 GuardCondition getGuard(FunctionCall fc) {
     exists(Expr e, Variable a| e = getSinkExpr(fc)
     and isLocalVariable(a)
     and a.getAnAccess() = e
     and exists(GuardCondition g, Expr ge| 
         a.getAnAccess() = ge
         and g.getASuccessor*() = fc
         and result = g
         )
     )
 }

//  predicate isConditional(BasicBlock bb) {
//     exists(GuardCondition g | 
//        g.controls(bb, _) 
//        )
    
//  }
 
 
 from FunctionCall target, BasicBlock bb
 where
 target = getTargetNode()
//  and after.getTarget().hasName("free")
 // and not exists(Expr check| check=getCheckExpr(target))
 and bb = getLeakBBBefore(target)
 select target
 