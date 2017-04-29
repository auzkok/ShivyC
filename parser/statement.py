"""Parser logic that parses statement nodes."""

import token_kinds
import tree.nodes

from parser.declaration import parse_declaration
from parser.expression import parse_expression
from parser.utils import (add_range, log_error, match_token, token_is,
                          ParserError)


@add_range
def parse_statement(index):
    """Parse a statement.

    Try each possible type of statement, catching/logging exceptions upon
    parse failures. On the last try, raise the exception on to the caller.

    """
    try:
        return parse_compound_statement(index)
    except ParserError as e:
        log_error(e)

    try:
        return parse_return(index)
    except ParserError as e:
        log_error(e)

    try:
        return parse_if_statement(index)
    except ParserError as e:
        log_error(e)

    try:
        return parse_while_statement(index)
    except ParserError as e:
        log_error(e)

    return parse_expr_statement(index)


@add_range
def parse_compound_statement(index):
    """Parse a compound statement.

    A compound statement is a collection of several
    statements/declarations, enclosed in braces.

    """
    index = match_token(index, token_kinds.open_brack, ParserError.GOT)

    # Read block items (statements/declarations) until there are no more.
    nodes = []
    while True:
        try:
            node, index = parse_statement(index)
            nodes.append(node)
            continue
        except ParserError as e:
            log_error(e)

        try:
            node, index = parse_declaration(index)
            nodes.append(node)
            continue
        except ParserError as e:
            log_error(e)
            # When both of our parsing attempts fail, break out of the loop
            break

    index = match_token(index, token_kinds.close_brack, ParserError.GOT)

    return tree.nodes.Compound(nodes), index


@add_range
def parse_return(index):
    """Parse a return statement.

    Ex: return 5;

    """
    index = match_token(index, token_kinds.return_kw, ParserError.GOT)
    node, index = parse_expression(index)

    index = match_token(index, token_kinds.semicolon, ParserError.AFTER)
    return tree.nodes.Return(node), index


@add_range
def parse_if_statement(index):
    """Parse an if statement."""

    index = match_token(index, token_kinds.if_kw, ParserError.GOT)
    index = match_token(index, token_kinds.open_paren, ParserError.AFTER)
    conditional, index = parse_expression(index)
    index = match_token(index, token_kinds.close_paren, ParserError.AFTER)
    statement, index = parse_statement(index)

    # If there is an else that follows, parse that too.
    is_else = token_is(index, token_kinds.else_kw)
    if not is_else:
        else_statement = None
    else:
        index = match_token(index, token_kinds.else_kw, ParserError.GOT)
        else_statement, index = parse_statement(index)

    return tree.nodes.IfStatement(
        conditional, statement, else_statement), index


@add_range
def parse_while_statement(index):
    """Parse a while statement."""
    index = match_token(index, token_kinds.while_kw, ParserError.GOT)
    index = match_token(index, token_kinds.open_paren, ParserError.AFTER)
    conditional, index = parse_expression(index)
    index = match_token(index, token_kinds.close_paren, ParserError.AFTER)
    statement, index = parse_statement(index)

    return tree.nodes.WhileStatement(conditional, statement), index


@add_range
def parse_expr_statement(index):
    """Parse a statement that is an expression.

    Ex: a = 3 + 4

    """
    node, index = parse_expression(index)
    index = match_token(index, token_kinds.semicolon, ParserError.AFTER)
    return tree.nodes.ExprStatement(node), index