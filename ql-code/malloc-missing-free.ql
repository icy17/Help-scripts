/**
 * @name mallocfree
 * @description description
 * @kind problem
 * @problem.severity error
 * @precision high
 * @id cpp/memleak
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
 predicate isMallocFC(FunctionCall fc)
 {
//  fc.getTarget().hasName("new_malloc")
//  or 
 fc.getTarget().hasName("Target_Malloc")
 }

 predicate isFreeFC(FunctionCall fc)
 {
 fc.getTarget().hasName("free")
//  or
//  fc.getTarget().hasName("new_free")
 }
 DataFlow::Node getFreeNode(FunctionCall fc)
 {
     result.asExpr() = getFreeExpr(fc)
     or
     result.asDefiningArgument() = getFreeExpr(fc)
 }
    
 DataFlow::Node getMallocNode(FunctionCall fc)
 {
     result.asExpr() = getMallocExpr(fc)
     or
     result.asDefiningArgument() = getMallocExpr(fc)
 }
 class MallocConfiguration extends DataFlow::Configuration {
    MallocConfiguration() { this = "MallocConfiguration" }
   
     override predicate isSource(DataFlow::Node source) {
       exists(FunctionCall fc | 
        isMallocFC(fc)
        and
        source = getMallocNode(fc)
         )
     }
     override predicate isSink(DataFlow::Node sink) {
       // sink.asExpr()
       exists(FunctionCall fc |
         isFreeFC(fc)
         and sink = getFreeNode(fc)
       )
     }
   }

FunctionCall getTargetFree(FunctionCall malloc) {
    isMallocFC(malloc)
    and isFreeFC(result)
    // and malloc.getASuccessor+() = result
    and exists(MallocConfiguration p | p.hasFlow(getMallocNode(malloc), getFreeNode(result)))
}

predicate isSpecialCondition(FunctionCall malloc, IfStmt ifstmt) {
    isMallocFC(malloc)
    and not ifstmt.getCondition().getAChild*() = malloc
    and exists(Variable v | 
        ifstmt.getCondition().getAChild*() = v.getAnAccess()
        and getMallocExpr(malloc).getAChild*() = v.getAnAccess()
        
        )
        
}

class ExitFunction extends Function {
    ExitFunction() {

      exists(FunctionCall exit |
        exit.getEnclosingFunction() = this
        and 
        (
            exit.getTarget() instanceof ExitFunction
            or exit.getTarget().hasName("exit")
            or exit.getTarget().hasName("abort")
        )
        // and forall(BasicBlock bb | bb.getEnclosingFunction() = this | bb.getASuccessor*() = exit or bb.getANode() = exit)
      )
      and
      (
        this.getAnAttribute().hasName(["noreturn", "__noreturn__"])
        or
        this.getASpecifier().hasName("noreturn")
        or
        this.hasGlobalOrStdName([
            "exit", "_exit", "_Exit", "abort", "__assert_fail", "longjmp", "__builtin_unreachable"
        ])
      )
    //   and 
    //   exists(ReturnStmt rt | 
    //     rt.getEnclosingFunction() = this
    //     )
    //     and this.hasName("exit_tcpdump")
    }
  }

  ReturnStmt hasBB(ExitFunction exit) {
    result.getEnclosingFunction() = exit
    
}

 BasicBlock getLeakAfterBB(FunctionCall malloc) {
    isMallocFC(malloc)
    and
    exists(IfStmt ifStmt | 
        result = ifStmt.getThen().getAChild*()
        and not isSpecialCondition(malloc, ifStmt)
        and not exists(Stmt elseStmt | elseStmt = ifStmt.getElse())
        and not exists(FunctionCall free | free = getTargetFree(malloc) and not (free.getASuccessor+() = malloc and malloc.getASuccessor+() = free )and (free = result.getANode() or free.getASuccessor+() = result))
        and (malloc.getASuccessor*() = result)
        and (exists(ReturnStmt rt | result.getANode() = rt) or exists(FunctionCall fc | fc.getTarget() instanceof ExitFunction and result.getANode() = fc) or exists(GotoStmt goto | result.getANode() = goto and not result.getASuccessor+() = getTargetFree(malloc)))
          )
    // malloc.getASuccessor+() = result
    // and not exists(FunctionCall free | 
    //     isFreeFC(free)
    //     and result.getASuccessor+() = free
    //     and free.getASuccessor+() = result
        
    //     )
    // and exists(ReturnStmt rt | 
    //     result.getASuccessor+() = rt
        
    //     )
 }
 
//  Stmt testgetLeakAfterBB(FunctionCall malloc) {
//     isMallocFC(malloc)
//     and
//     exists(IfStmt ifStmt | 
//         result = ifStmt.getThen().getChildStmt()
//         and not isSpecialCondition(malloc, ifStmt)
//         and not exists(Stmt elseStmt | elseStmt = ifStmt.getElse())
//         // and not exists(FunctionCall free | free = getTargetFree(malloc) and not (free.getASuccessor+() = malloc and malloc.getASuccessor+() = free )and (free = result.getANode() or free.getASuccessor+() = result))
//         and (malloc.getASuccessor*() = result)
//         and (exists(ReturnStmt rt | result = rt))
//           )
//     // malloc.getASuccessor+() = result
//     // and not exists(FunctionCall free | 
//     //     isFreeFC(free)
//     //     and result.getASuccessor+() = free
//     //     and free.getASuccessor+() = result
        
//     //     )
//     // and exists(ReturnStmt rt | 
//     //     result.getASuccessor+() = rt
        
//     //     )
//  }

 predicate isLocalVariable(Expr e) {
    exists(LocalVariable a| 
    a.getAnAccess() = e.getAChild*()
    and not exists(ReturnStmt rt | 
        rt.getAChild*() = a.getAnAccess())
    )
 }

 //0702-after check FN
 from FunctionCall target
 where
 isMallocFC(target)
 and 
isLocalVariable(getMallocExpr(target))

 and 
 (
    exists(BasicBlock bb | bb = getLeakAfterBB(target) )
    or
    not exists(FunctionCall free| free = getTargetFree(target))
 )
 select target, target.getLocation().toString()