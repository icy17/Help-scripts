/**
 * @name parameterCheck
 * @description description
 * @kind problem
 * @problem.severity error
 * @precision high
 * @id cpp/paracheck
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
     //Change
 result = fc.getArgument(0) 
 }
 
 predicate isSinkFC(FunctionCall fc)
 {
     // Change
 fc.getTarget().hasName("SSL_CTX_set_options")
 }
 GuardCondition getGuard(FunctionCall fc) {
    isSinkFC(fc)
    and
     exists(Expr e, Variable a| e = getSinkExpr(fc)
    //  and isLocalVariable(a)
     and a.getAnAccess() = e
     and exists(GuardCondition g, Expr ge| 
         a.getAnAccess() = ge
         and g.getASuccessor*() = fc
         and g.getAChild*() = ge
         and not exists(FunctionCall fc_in | 
            g.getAChild*() = fc_in
            and fc_in.getAnArgument() = a.getAnAccess()
            )
         and result = g
         )
     )
 }
 
// predicate getMalloc(FunctionCall fc) {
//   fc.getTarget().hasName("malloc")
  
// }

 class PathConfiguration extends DataFlow::Configuration {
    PathConfiguration() { this = "PathConfiguration" }
   
     override predicate isSource(DataFlow::Node source) {
       exists(AssignExpr a | 
        source.asExpr() = a.getRValue()
        and a.getRValue() instanceof StringLiteral
        // and exists(Variable v | 
        //   v.getAnAccess() = a.getRValue()
        //   and v instanceof ExcludeArrayAndConstantPointer
        //   )
         )
         or exists(Variable v | 
          source.asExpr() = v.getInitializer().getExpr()
          and v.getInitializer().getExpr() instanceof StringLiteral
          // and v instanceof ExcludeArrayAndConstantPointer
          )
          or exists(FunctionCall fca, AddressOfExpr ae| 
            source.asDefiningArgument() = ae
            and fca.getAnArgument() = ae
            )
     }
     override predicate isSink(DataFlow::Node sink) {
       // sink.asExpr()
       exists(FunctionCall fc |
        isSinkFC(fc)
        and
        sink.asExpr() = getSinkExpr(fc)
    )
     }
   }

//  FunctionCall useSamePara(Expr p) {
//     exists(Variable v | 
//         result.getAnArgument() = v.getAnAccess()
//         and v.getAnAccess() = p
//         )
//  }

//  predicate notUsedbefore(FunctionCall fc, Expr p) {
//     isSinkFC(fc)
//     and p = getSinkExpr(fc)
//     and
//     exists(ControlFlowNode n | 
//         n.getASuccessor+() = fc
//         and not exists(FunctionCall usefc | 
//             usefc = useSamePara(p)
//             and usefc.getASuccessor+() = fc
//             and
//             (usefc.getASuccessor+() = n or n.getASuccessor+() = usefc)
            
//             )
//     )

//  }

//  predicate notUsedBefore(FunctionCall fc, Expr p) {
//     isTargetFunction(fc)
//     and p = fc.getArgument(0)
//     and
//     exists(ControlFlowNode start |
//       start.getBasicBlock() = fc.getEnclosingFunction().getEntryBlock() and
//       // 确保从函数入口到目标函数有一条路径不经过其他函数调用使用目标参数
//       exists(ControlFlowNode n |
//         n.getASuccessor*() = fc.getBasicBlock() and
//         not exists(FunctionCall f |
//           f.getBasicBlock() = n and
//           f != fc and
//           p = f.getArgument(0)
//         )
//       )
//     )
//   }
predicate hasFlowtoAPI(FunctionCall fc) {
    isSinkFC(fc)
    and
    exists(PathConfiguration p, DataFlow::Node source| 
        p.hasFlow(source, DataFlow::exprNode(getSinkExpr(fc)))
      and source.asExpr().getEnclosingFunction() = fc.getEnclosingFunction()
        )
}
//  predicate 


predicate hasSpecifiedFunctionInThen(FunctionCall fc) {
    // isSinkFC(fc) 
    // and isuseSamePara(fc, barrier)
    // and
    exists(IfStmt ifStmt | 
      fc.getEnclosingStmt() = ifStmt.getThen().getAChild*()
      and not exists(Stmt elseStmt | elseStmt = ifStmt.getElse())
        )
  }

  class ExcludeArrayAndConstantPointer extends Variable {
    ExcludeArrayAndConstantPointer() {
      exists(Type t |
        // Exclude array types
        t = this.getType() and
        t instanceof ArrayType or
  
        // Exclude constant pointer types
        t = this.getType() and
        t instanceof PointerType and
        exists(Expr initializer |
            this.getInitializer().getExpr() = initializer and
            initializer instanceof StringLiteral)
      )
    }
  }

  predicate isuseSamePara(FunctionCall target, FunctionCall barrier) {
    isSinkFC(target)
    and barrier.getASuccessor+() = target
    and not barrier = target
    and
    (
      (isBarrierFC(barrier)
      and
      exists(Variable v, Expr p| 
          p = getSinkExpr(target)
          and
          barrier.getAnArgument().getAChild*() = v.getAnAccess()
          and v.getAnAccess() = p
          
          ))
        // or
        // (
        //   exists(Variable v, Expr p, Expr barrierp| 
        //     p = getSinkExpr(target)
        //     and  barrier.getAnArgument() = barrierp
        //     and
        //     barrierp.getAChild+() = v.getAnAccess()
        //     and barrierp instanceof AddressOfExpr
        //     and v.getAnAccess() = p
        //     )  
        // )
    )

      
}

predicate isBarrierFC(FunctionCall fc) {
  fc.getTarget().hasName("NEED CHECK API")
  // or fc.getTarget().hasName("DH_set0_pqg")
  // or fc.getTarget().hasName("X509_STORE_CTX_get_error")
  // or fc.getTarget().hasName("mbedtls_x509_crt_info")
  // or fc.getTarget().hasName("mbedtls_ssl_session_init")
  // or fc.getTarget().hasName("mbedtls_x509_crt_init")
  // or fc.getTarget().hasName("BN_GF2m_mod_arr")
  // or fc.getTarget().hasName("EC_GROUP_get_cofactor")
  // or fc.getTarget().hasName("BIO_puts")
  // or fc.getTarget().hasName("EVP_PKEY_get0_DH")
}



 from FunctionCall target
 where
 (isSinkFC(target)
 and not hasFlowtoAPI(target)

 // and not exists(Expr check| check=getCheckExpr(target))
//  and source = getSourceOfFc(target)
 
 // TODO: source后的每一条路径都有g
 and not exists(GuardCondition g| 
     g = getGuard(target)
    //  and source.getASuccessor*() = g
     )
and exists(Expr e, LocalVariable a| e = getSinkExpr(target)
//  and isLocalVariable(a)
 and a.getAnAccess() = e.getAChild*()
)

and not exists(AddressOfExpr ae | 
    ae = getSinkExpr(target)))

    and 
    (

        (not exists(FunctionCall barrier | isuseSamePara(target, barrier)))
    or (
        exists(FunctionCall barrier | 
        isuseSamePara(target, barrier)
        and hasSpecifiedFunctionInThen(barrier)
        )
        )

    )

    and exists(Variable v | 
        v.getAnAccess() = getSinkExpr(target)
        and not v instanceof ExcludeArrayAndConstantPointer
        )
 select target, target.getLocation().toString()