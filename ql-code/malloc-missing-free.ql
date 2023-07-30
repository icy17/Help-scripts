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
            (fc.getTarget().hasName("Target_Malloc") and e = fc.getArgument(Target_INDEX))
        // or
        // (fc.getTarget().hasName("new_malloc") and e = fc.getArgument(0))
        // TODO-addMallocHere
        )
    )
}

Expr getFreeExpr(FunctionCall fc)
{

        result = fc.getArgument(0)
        and
        (
            fc.getTarget().hasName("free")
        // or
        //  fc.getTarget().hasName("new_free")
        // TODO-addFreeHere
        )
}


//  Expr getSinkExpr(FunctionCall fc)
//  {
//  result = fc.getArgument(0) 
//  }
//  Expr getSourceExpr(FunctionCall fc)
//  {
//  result = fc.getArgument(0) 
//  }
 predicate isSourceFC(FunctionCall fc)
 {
//  fc.getTarget().hasName("new_malloc")
//  or 
 fc.getTarget().hasName("Target_Malloc")
 }

 predicate isSinkFC(FunctionCall fc)
 {
 fc.getTarget().hasName("free")
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

ControlFlowNode getTargetNode() {
    exists(FunctionCall target | 
    isSourceFC(target)
    and result = target
    )
}
   
ControlFlowNode getAfterNode(ControlFlowNode target) {
    isSourceFC(target)
    and
    exists(FunctionCall fc | 
        target.getASuccessor*() = fc
        and result = fc
        and isSinkFC(fc)
        and exists(MallocConfiguration cfg| 
            cfg.hasFlow(getSourceNode(target), getSinkNode(fc))
            )
        )
}


// return True说明该node是 conditional的，会leak
predicate isConditionalAfter(ControlFlowNode node, ControlFlowNode target) {
    target = getTargetNode()
    and
    node = getAfterNode(target)
    and
    exists(BasicBlock bb | 
        bb.getAPredecessor().getANode() = node
        and bb.getAPredecessor().getANode() = target
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

 
 from FunctionCall target, BasicBlock bb
 where
 target = getTargetNode()
 and 
isLocalVariable(getMallocExpr(target))
 
//  and after.getTarget().hasName("free")
 // and not exists(Expr check| check=getCheckExpr(target))
 and bb = getLeakBBAfter(target)
 select target, target.getLocation().toString()
 