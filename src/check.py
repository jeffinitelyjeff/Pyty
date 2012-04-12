import ast
import logging

from util import cname, slice_range, node_is_int, node_is_None, valid_int_slice
from errors import TypeUnspecifiedError, ASTTraversalError
from ptype import PType
from settings import DEBUG_TYPECHECK
from logger import Logger
from ast_extensions import TypeDec
from infer import infer_expr, env_get

log = None

def t_debug(s, cond=True):
    log.debug(s, DEBUG_TYPECHECK and cond)

def call_function(fun_name, *args, **kwargs):
    return globals()[fun_name](*args, **kwargs)

int_t = PType.int()
float_t = PType.float()
bool_t = PType.bool()
str_t = PType.string()
unicode_t = PType.unicode()
unit_t = PType.unit()

bool_ops = set([ast.And, ast.Or])
arith_ops = set([ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
                 ast.Pow])
bit_ops = set([ast.LShift, ast.RShift, ast.BitOr, ast.BitAnd, ast.BitXor])
bin_ops = arith_ops | bit_ops
unary_ops = set([ast.Invert, ast.Not, ast.UAdd, ast.USub])

comp_eq_ops = set([ast.Eq, ast.NotEq, ast.Is, ast.IsNot])
comp_num_ops = set([ast.Lt, ast.LtE, ast.Gt, ast.GtE])
comp_ops = comp_num_ops | comp_eq_ops





## Module Typechecking.

def check_mod(mod):
    """
    Check whether the module node `mod` typechecks under its embedded
    environments.
    """

    t_debug("----- v Typechecking module v -----")

    if mod.__class__ != ast.Module:
        t_debug("Returning false because this isn't a module")
        t_debug("----- ^ Typechecking module ^ -----")
        return False

    result = check_stmt_list(mod.body, {})
    t_debug("return: " + str(result) + "\n----- ^ Typechecking module ^ -----")
    return result




## Statement List Typechecking.

def check_stmt_list(stmt_list, env):
    """
    Check whether each stmt in `stmt_list` typechecks correctly. `env` is the
    common type environment shared by all stmts in `stmt_list`
    """

    # Make duplicate of environment to add to as we encounter type declarations.
    w_env = env.copy()

    for s in stmt_list:

        if s.__class__ is TypeDec:
            # Add each binding to the environment for future statements.
            for tar in s.targets:
                w_env[tar.id] = s.t
        elif not check_stmt(s, w_env):
            # Break out if a statement doesn't typecheck.
            return False

    # Reaching here means all statements typechecked.
    return True




## Statement Typechecking.

stmt_template = "_check_%s_stmt"

def check_stmt(stmt, env):
    """
    Check whether the statement `stmt` typechecks under type environment `env`.

    We defer to the specific `check_X_stmt` functions to determine which type
    assignemnt rule to try. Information about the structure of each AST node is
    contained in the thesis PDF.
    """

    t_debug("--- v Typechecking " + stmt.__class__.__name__ + " stmt v ---"
            "\nStmt: " + str(stmt) + "\nEnv: " + str(env))

    n = stmt_template % stmt.__class__.__name__

    # if we get a KeyError, then we're inspecting an AST node that is not in
    # the subset of the language we're considering (note: the subset is
    # defined as whatever there are check function definitions for).
    try:
        result = call_function(n, stmt, env)
        t_debug("return: " + str(result) + "\n--- ^ Typechecking stmt ^ ---")
        return result
    except KeyError as e:
        t_debug("Found a stmt not in the language subset. (" + str(e) + ")")
        return False


def _check_FunctionDef_stmt(stmt, env):
    """Function Definition."""

    assert stmt.__class__ is ast.FunctionDef

    f = stmt.name
    a = stmt.args
    b = stmt.body
    d = stmt.decorator_list

    # All Fn-Def rules have specific forms for args and decorator_list.
    if (all(arg.__class__ is ast.Name for arg in a.args) and
        not a.vararg and not a.kwarg and not a.defaults and not d):

        f_t = env_get(env, f)

        # (Fn-Def1) assignment rule.
        if not a.args:
            new_env = dict(env.items() + [("return", f_t.ran)])
            return check_stmt_list(b, new_env)

        # (Fn-Def2) assignment rule.
        elif len(a.args) == 1 and f_t.dom != unit_t:
            arg_id = a.args[0].id
            new_env = dict(env.items() +
                           [(arg_id, f_t.dom), ("return", f_t.ran)])
            return check_stmt_list(b, new_env)

        # (Fn-Def3) assignment rule.
        elif f_t.dom.is_tuple() and f_t.dom.tuple_len() == len(a.args):
            arg_ids = map(lambda x: x.id, a.args)
            arg_ts = f_t.dom.elts
            new_env = dict(env.items() +
                           zip(arg_ids, arg_ts) + [("return", f_t.ran)])
            return check_stmt_list(b, new_env)

    # No assignment rule found.
    return False

def _check_Return_stmt(stmt, env):
    """Return Statement."""
    
    assert stmt.__class__ is ast.Return

    e = stmt.value

    try:
        r_t = env_get(env, "return")
    except TypeUnspecifiedError:
        return False

    # (RetU) assignment rule.
    if not e:
        return r_t == unit_t

    # (Ret) assignment rule.
    else:
        return check_expr(e, r_t, env)

def _check_Assign_stmt(stmt, env):
    """Assignment."""

    assert stmt.__class__ is ast.Assign

    v = stmt.value
    tars = stmt.targets

    # (Assmt) assignment rule.
    if tars:
        def valid_tar(t):
            if t.__class__ is ast.Subscript:
                col_t = infer_expr(t.value, env)
                sub_of_tup = col_t and col_t.is_tuple()
            else:
                sub_of_tup = False
            t_t = infer_expr(t, env)
            return t_t and check_expr(v, t_t, env) and not sub_of_tup
        return all(valid_tar(tar) for tar in tars)

    # No assignment rule found.
    else:
        return False

def _check_AugAssign_stmt(stmt, env):
    """Augmented Assignment."""
    
    assert stmt.__class__ is ast.AugAssign

    e0 = stmt.target
    op = stmt.op
    e1 = stmt.value

    e0_t = infer_expr(e0, env)

    # (Aug-Assmt) assignment rule. -- restricted by type inference
    return e0_t and check_expr(ast.BinOp(e0, op, e1), e0_t, env)

def _check_Print_stmt(stmt, env):
    """Print Statement."""

    assert stmt.__class__ is ast.Print

    d = stmt.dest

    # (Print) assignment rule.
    if not d:
        return True

    # No assignment rule found.
    else:
        return False

def _check_For_stmt(stmt, env):
    """For Loop."""

    assert stmt.__class__ is ast.For

    x = stmt.target
    e = stmt.iter
    b0 = stmt.body
    b1 = stmt.orelse

    x_t = infer_expr(x, env)

    # (For) assignment rule. -- restricted by type inference
    return (x_t and check_expr(e, PType.list(x_t), env) and
            check_stmt_list(b0, env) and check_stmt_list(b1, env))

def _check_While_stmt(stmt, env):
    """While Loop."""

    assert stmt.__class__ is ast.While

    e = stmt.test
    b0 = stmt.body
    b1 = stmt.orelse

    return (check_expr(e, bool_t, env) and
            check_stmt_list(b0, env) and
            check_stmt_list(b1, env))

def _check_If_stmt(stmt, env):
    """Conditional Block."""

    assert stmt.__class__ is ast.If

    e = stmt.test
    b0 = stmt.body
    b1 = stmt.orelse

    return (check_expr(e, bool_t, env) and
            check_stmt_list(b0, env) and
            check_stmt_list(b1, env))

def _check_Expr_stmt(stmt, env):
    """Expression Statement."""

    assert stmt.__class__ is ast.Expr

    e = stmt.value

    # (Expr-Stmt) assignment rule
    if e.__class__ is ast.Call and e.func.__class__ is ast.Name:
        f = e.func
        f_t = env_get(env, f.id)
        return check_expr(e, f_t.ran, env)

    # No assignment rule found.
    else:
        return False

def _check_Pass_stmt(stmt, env):
    """Pass Statement."""

    assert stmt.__class__ is ast.Pass

    return True

def _check_Break_stmt(stmt, env):
    """Break Statement."""

    assert stmt.__class__ is ast.Break

    return True

def _check_Continue_stmt(stmt, env):
    """Continue Statement."""

    assert stmt.__class__ is ast.Continue

    return True



## Expression Checking Functions.

expr_template = "_check_%s_expr"

def check_expr(expr, t, env):
    """
    Check whether the expression `expr` can be assigned type `t` under type
    environment `env`.

    We defer to the specific `check_X_expr` functions to determine which type
    assignment rule to try. Information about the structure of each AST node is
    contained in the thesis PDF.
    """

    assert isinstance(expr, ast.expr), \
           "Should be typechecking an expr node, not a " + cname(expr)
    assert isinstance(t, PType), \
           "Should be checking against a PType, not a " + cname(t)

    n = expr_template % expr.__class__.__name__

    t_debug("-- v Typechecking expr as " + str(t) + " v --\nExpr: " +
            str(expr) + "\nEnv: " + str(env))

    # if we get a KeyError, then we're inspecting an AST node that is not in
    # the subset of the language we're considering (note: the subset is
    # defined as whtaever there are check function definitions for).
    try:
        result = call_function(n, expr, t, env)
        t_debug("return: " + str(result) + "\n-- ^ Typechecking expr ^ --")
        return result
    except KeyError as e:
        t_debug("Found an expr not in the language subset. (" + str(e) + ")")
        return False


def _check_BoolOp_expr(boolop, t, env):
    """Boolean Operations."""

    assert boolop.__class__ is ast.BoolOp

    op = boolop.op
    es = boolop.values

    assert op.__class__ in bool_ops, "%s not in bool ops" % cname(op)

    # (BoolOp) assignment rule.
    return all(check_expr(e, t, env) for e in es)

def _check_BinOp_expr(binop, t, env):
    """Binary Operations."""

    assert binop.__class__ is ast.BinOp

    e0 = binop.left
    e1 = binop.right
    op = binop.op

    assert op.__class__ in bin_ops, "%s not in binary ops" % cname(op)

    # Numeric Operations.
    if t == int_t or t == float_t:

        # (Arith) assignment rule.
        if op.__class__ in arith_ops:
            return check_expr(e0, t, env) and check_expr(e1, t, env)

        # (BitOp) assignment rule.
        elif op.__class__ in bit_ops and t == int_t:
            return check_expr(e0, int_t, env) and check_expr(e1, int_t, env)

    # String and List Operations.
    elif t == str_t or t == unicode_t or t.is_list():

        # (Str-Cat) assignment rule.
        if op.__class__ is ast.Add:
            return check_expr(e0, t, env) and check_expr(e1, t, env)

        # (Str-Rep) assignment rule.
        elif op.__class__ is ast.Mult:
            return any(check_expr(l, int_t, env) and check_expr(r, t, env) for
                       (l, r) in [(e0, e1), (e1, e0)])

        # (Str-Form) assignment rule.
        elif not t.is_list() and op.__class__ is ast.Mod:
            return check_expr(e0, t, env)

    # Tuple Operations.
    elif t.is_tuple():

        # (Tup-Cat) assignment rule.
        if op.__class__ is ast.Add:

            return any(check_expr(e0, t.tuple_slice(0, m), env) and
                       check_expr(e1, t.tuple_slice(m), env)
                       for m in range(t.tuple_len()))

        # (Tup-Rep) assignment rule.
        elif (op.__class__ is ast.Mult and
              any(e.__class__ is ast.Num for e in [e0,e1])):
            m = e0.n if e0.__class__ is ast.Num else e1.n
            e = e0 if e1.__class__ is ast.Num else e1

            e_len = int(t.tuple_len() / m)
            e_t = t.tuple_slice(0, e_len)

            return (type(m) is int and t.tuple_len() % m == 0 and
                    check_expr(e, e_t, env) and
                    all(e_t == t.tuple_slice(e_len*i, e_len*(i+1))
                        for i in range(1, m)))

    # No assignment rule found.
    return False

def _check_UnaryOp_expr(unop, t, env):
    """Unary Operations."""

    assert unop.__class__ is ast.UnaryOp
    
    op = unop.op
    e = unop.operand

    assert op.__class__ in unary_ops, "%s not in unary ops" % cname(op)

    # (Inv) assignment rule.
    if op.__class__ is ast.Invert and t == int_t:
        return check_expr(e, int_t, env)

    # (Uadd) assignment rule.
    elif op.__class__ in [ast.UAdd, ast.USub] and t in [int_t, float_t]:
        return check_expr(e, t, env)

    # (Not) assignment rule.
    elif op.__class__ is ast.Not and t == bool_t:
        return check_expr(e, bool_t, env)

    # No assignment rule found.
    else:
        return False

def _check_Lambda_expr(lambd, t, env):
    """Abstraction."""

    assert lambd.__class__ is ast.Lambda

    a = lambd.args
    e = lambd.body

    # All Abs rules have specific forms for args.
    if (all(arg.__class__ is ast.Name for arg in a.args) and
        a.vararg is None and a.kwarg is None and not a.defaults):

        # (Abs1) assignment rule.
        if not a.args:
            return check_expr(e, t.ran, env)

        # (Abs2) assignment rule.
        elif len(a.args) == 1 and t.dom != unit_t:
            arg_id = a.args[0].id
            new_env = dict(env.items + [(arg_id, t.dom)])
            return check_expr(e, t.ran, new_env)

        # (Abs3) assignment rule.
        elif t.dom.is_tuple() and t.dom.tuple_len() == len(a.args):
            arg_ids = map(lambda x: x.id, a.args)
            arg_ts = t.dom.elts
            new_env = dict(env.items() + zip(arg_ids, arg_ts))
            return check_expr(e, t.ran, new_env)

    # No assignment rule found.
    else:
        return False    

def _check_IfExp_expr(ifx, t, env):
    """Conditional Expression."""

    assert ifx.__class__ is ast.IfExp

    e0 = ifx.body
    e1 = ifx.test
    e2 = ifx.orelse

    # (If-Exp) assignment rule.
    return (check_expr(e0, t, env) and
            check_expr(e1, bool_t, env) and
            check_expr(e2, t, env))

def _check_Compare_expr(compare, t, env):
    """Comparisons."""

    assert compare.__class__ is ast.Compare
    
    e0 = compare.left
    ops = compare.ops
    es = compare.comparators

    assert all(op.__class__ in comp_ops for op in ops)

    # (Eqlty) assigment rule.
    if len(ops) == 1 and ops[0].__class__ in comp_eq_ops and t == bool_t:
        return True

    # (Ineqlty) assignment rule.
    elif len(ops) == 1 and ops[0].__class__ in comp_num_ops and t == bool_t:
        possible_ts = (int_t, float_t, str_t, unicode_t)
        return any(check_expr(e0, pt, env) and check_expr(es[0], pt, env)
                   for pt in possible_ts)

    # (Comp-Chain) assignment rule.
    elif len(ops) > 1 and t == bool_t:
        head = ast.Compare(e0, ops[:1], es[:1])
        tail = ast.Compare(es[0], ops[1:], es[1:])
        return check_expr(head, bool_t, env) and check_expr(tail, bool_t, env)

    # No assignment rule found.
    else:
        return False

def _check_Call_expr(call, t, env):
    """Application."""

    assert call.__class__ is ast.Call

    f = call.func
    a = call.args
    k = call.keywords
    s = call.starargs
    kw = call.kwargs

    # All App rules have specific forms for keywords, starargs, and kwargs.
    if not k and not s and not kw and f.__class__ is ast.Name:

        f_t = env_get(env, f.id)

        # (App1) assignment rule.
        if not a:
            return f_t == PType.arrow(unit_t, t)

        # (App2) assignment rule.
        elif len(a) == 1:
            return check_expr(a[0], f_t.dom, env) and f_t.ran == t

        # (App3) assignment rule.
        else:
            tup = ast.Tuple([b for b in a], ast.Load())
            return check_expr(tup, f_t.dom, env) and f_t.ran == t

def _check_Num_expr(num, t, env):
    """Numeric Literals."""

    assert num.__class__ is ast.Num

    n = num.n

    # (Num) assignment rule.
    if t == int_t or t == float_t:
        return type(n) is (int if t == int_t else float)

    # No type assignment rule found.
    else:
        return False

def _check_Str_expr(strr, t, env):
    """String Literals."""

    assert strr.__class__ is ast.Str

    s = strr.s

    # (Str) assignment rule.
    if t == str_t or t == unicode_t:
        return type(s) is (str if t == str_t else unicode)

    # No type assignment rule found.
    else:
        return False

def _check_Subscript_expr(subs, t, env):
    """Subscription."""

    assert subs.__class__ is ast.Subscript

    c = subs.value
    s = subs.slice

    # Type inference is necessary off the bat; these rules are the polar
    # opposite of syntax direction.
    c_t = infer_expr(c, env)
    if not c_t:
        return False

    # Indexing.
    if s.__class__ is ast.Index:

        e = s.value

        # (Str-Idx) assignment rule.
        if c_t == str_t or c_t == unicode_t:
            return c_t == t and check_expr(e, int_t, env)

        # (Lst-Idx) assignment rule.
        elif c_t.is_list():
            return t == c_t.elt and check_expr(e, int_t, env)

        # (Tup-Idx) assignment rule.
        elif c_t.is_tuple():
            n = len(c_t.elts)
            return node_is_int(e) and -n <= e.n < n and c_t.elts[e.n] == t

    # Slicing.
    elif s.__class__ is ast.Slice:
        e0, e1, e2 = s.lower, s.upper, s.step

        # (Flat-Slc) assignment rule.
        if c_t == str_t or c_t == unicode_t or c_t.is_list():
            return c_t == t and valid_int_slice(e0, e1, e2, env)

        # (Tup-Slc) assignment rule.
        elif c_t.is_tuple() and ((not e0 or node_is_int(e0)) and
                                 (not e1 or node_is_int(e1)) and
                                 (not e2 or node_is_None(e2) or node_is_int(e2))):
            rng = slice_range(e0, e1, e2, c_t.tuple_len())
            return (t.is_tuple() and rng and len(rng) == t.tuple_len()
                    and all(c_t.elts[j] == t.elts[i]
                            for (i,j) in enumerate(rng)))

    # No assignment rule found
    return False

def _check_Name_expr(name, t, env):
    """Identifiers."""

    assert name.__class__ is ast.Name

    x = name.id

    base_env = {"True" : bool_t, "False" : bool_t, "None" : unit_t}

    # (Base-Env) assignment rule.
    if x in base_env:
        return t == base_env[x]

    # (Idn) assignment rule.
    elif env_get(env, x) == t:
        return True

    # No assignment rule found.
    else:
        return False

def _check_List_expr(lst, t, env):
    """List Construction."""

    assert lst.__class__ is ast.List

    es = lst.elts

    # (Lst) assignment rule.
    if t.is_list():
        return all(check_expr(e, t.elt, env) for e in es)

    # No assignment rule found.
    return False

def _check_Tuple_expr(tup, t, env):
    """Tuple Construction."""

    assert tup.__class__ is ast.Tuple

    es = tup.elts

    # (Tup) assignment rule.
    if t.is_tuple() and t.tuple_len() == len(es):
        return all(check_expr(e, elt_t, env) for (e, elt_t) in zip(es, t.elts))

    # No assignment rule found.
    return False
