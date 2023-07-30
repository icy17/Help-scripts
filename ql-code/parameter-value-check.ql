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

string target_api = "SSL_CTX_set_options"
int target_index = 0
    
Expr getSinkExpr(FunctionCall fc)
{
result = fc.getArgument(target_index) 
}

predicate isSinkFC(FunctionCall fc)
{

fc.getTarget().hasName(target_api)
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



//   if every path after target exists node

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


from FunctionCall target, Expr source
where
isSinkFC(target)
// and not exists(Expr check| check=getCheckExpr(target))
and source = getSourceOfFc(target)

// TODO: source后的每一条路径都有g
and not exists(GuardCondition g| 
    g = getGuard(target)
    and source.getASuccessor*() = g
    )
select source, target
