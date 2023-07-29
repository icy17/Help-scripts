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
             (fc.getTarget().hasName("strlen") and e = fc.getArgument(0))
         or
         (fc.getTarget().hasName("test_init") and e = fc.getArgument(0))
         // TODO-addMallocHere
         )
     )
 }

 predicate isSourceFC(FunctionCall fc)
 {
 fc.getTarget().hasName("test_init")
 or 
 fc.getTarget().hasName("strlen")
 }

 DataFlow::Node getSourceNode(FunctionCall fc)
 {
     result.asExpr() = getMallocExpr(fc)
     or
     result.asDefiningArgument() = getMallocExpr(fc)
 }

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
         rt = source.asExpr()
         or rt = source.asDefiningArgument()
         )

        or
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


predicate isFlow(Expr source, Expr sink) {
    exists(FunctionCall sourcefc, FunctionCall sinkfc | 
        isSourceFC(sourcefc)
        and isSinkFC(sinkfc)
        and source = getMallocExpr(sourcefc)
        and sink = getSinkExpr(sinkfc)
        and exists(ParameterConfiguration cfg | 
            cfg.hasFlow(getSourceNode(sourcefc), getSinkNode(sinkfc))
            )
        )
    
}
   
ControlFlowNode getTargetNode() {
    exists(FunctionCall target | 
        isSinkFC(target)
    // target.getTarget().hasName("free")
    and result = target
    )
}

ControlFlowNode getBeforeNode(FunctionCall target) {
    exists(FunctionCall sourcefc, ParameterConfiguration cfg| 
        cfg.hasFlow(getSourceNode(sourcefc), getSinkNode(target))
        and target.getAPredecessor*() = sourcefc
        // and not e = target.getAnArgument()
        and result = sourcefc)
}

// return True说明该node是 conditional的，会leak
predicate isConditionalBefore(ControlFlowNode node, ControlFlowNode target) {
    target = getTargetNode()
    and
    node = getBeforeNode(target)
    and not node.getBasicBlock() = target.getBasicBlock()
    and
    exists(BasicBlock bb | 
        bb.getASuccessor().getANode() = node
        and bb.getASuccessor().getANode() = target
        
        )
}


BasicBlock getLeakBBBefore(ControlFlowNode target) {
    isSinkFC(target)
    and
    // result.getASuccessor*() = target
    // and
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
 
 
 from FunctionCall target, BasicBlock bb
 where
 target = getTargetNode()
 and
 isLocalVariable(getSinkExpr(target))
//  and after.getTarget().hasName("free")
 // and not exists(Expr check| check=getCheckExpr(target))
 and bb = getLeakBBBefore(target)
 select target
 