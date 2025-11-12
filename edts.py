# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, List, Dict

# Lexico

class TokenType:
    ID="ID"; NUM="NUM"; PLUS="PLUS"; MINUS="MINUS"; MUL="MUL"; DIV="DIV"
    ASSIGN="ASSIGN"; LPAREN="LPAREN"; RPAREN="RPAREN"; SEMI="SEMI"; EOF="EOF"

@dataclass
class Token:
    type: str
    lexeme: str
    pos: int

class Lexer:
    def __init__(self, s: str):
        self.s = s
        self.i = 0
        self.n = len(s)

    def _skip_ws(self):
        while self.i < self.n and self.s[self.i].isspace():
            self.i += 1

    def next(self) -> Token:
        self._skip_ws()
        if self.i >= self.n:
            return Token(TokenType.EOF, "", self.i)
        c = self.s[self.i]

        # Identificadores
        if c.isalpha():
            j = self.i
            self.i += 1
            while self.i < self.n and (self.s[self.i].isalnum() or self.s[self.i] == "_"):
                self.i += 1
            return Token(TokenType.ID, self.s[j:self.i], j)

        # Números
        if c.isdigit() or c == ".":
            j = self.i
            dot = (c == ".")
            self.i += 1
            while self.i < self.n:
                t = self.s[self.i]
                if t.isdigit():
                    self.i += 1
                elif t == "." and not dot:
                    dot = True
                    self.i += 1
                else:
                    break
            return Token(TokenType.NUM, self.s[j:self.i], j)

        # Símbolos
        self.i += 1
        if c == "+": return Token(TokenType.PLUS, "+", self.i - 1)
        if c == "-": return Token(TokenType.MINUS, "-", self.i - 1)
        if c == "*": return Token(TokenType.MUL, "*", self.i - 1)
        if c == "/": return Token(TokenType.DIV, "/", self.i - 1)
        if c == "=": return Token(TokenType.ASSIGN, "=", self.i - 1)
        if c == "(": return Token(TokenType.LPAREN, "(", self.i - 1)
        if c == ")": return Token(TokenType.RPAREN, ")", self.i - 1)
        if c == ";": return Token(TokenType.SEMI, ";", self.i - 1)
        raise SyntaxError(f"Símbolo léxico desconocido en posición {self.i-1}: '{c}'")

# AST

class AST:
    def __init__(self):
        self.val: Optional[float] = None
    def accept(self, v):
        raise NotImplementedError

class Num(AST):
    def __init__(self, value: float):
        super().__init__()
        self.value = value
    def accept(self, v): return v.visit_Num(self)

class Var(AST):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    def accept(self, v): return v.visit_Var(self)

class Assign(AST):
    def __init__(self, name: str, expr: AST):
        super().__init__()
        self.name = name
        self.expr = expr
    def accept(self, v): return v.visit_Assign(self)

class Op:
    ADD="ADD"; SUB="SUB"; MUL="MUL"; DIV="DIV"

class Binary(AST):
    def __init__(self, op: str, left: AST, right: AST):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
    def accept(self, v): return v.visit_Binary(self)

# Tabla de simbolos

class SymTable:
    def __init__(self): self.map: Dict[str, float] = {}
    def get(self, k: str) -> Optional[float]: return self.map.get(k)
    def put(self, k: str, v: float) -> None: self.map[k] = v
    def contains(self, k: str) -> bool: return k in self.map
    def __str__(self) -> str: return "{" + ", ".join(f"{k}={v}" for k, v in self.map.items()) + "}"

# PARSER LL(1) + EDTS

class Parser:
    def __init__(self, lx: Lexer, st: SymTable):
        self.st = st
        self.toks: List[Token] = []
        t = lx.next(); self.toks.append(t)
        while t.type != TokenType.EOF:
            t = lx.next(); self.toks.append(t)
        self.k = 0

    def LA(self): return self.toks[self.k]
    def match(self, tt: str):
        t = self.LA()
        if t.type != tt:
            raise SyntaxError(f"Se esperaba {tt} y se encontro {t.type} (pos {t.pos})")
        self.k += 1
        return t

    def parseLista(self) -> AST:
        stmts = [self.parseStmt()]
        while self.LA().type == TokenType.SEMI:
            self.match(TokenType.SEMI)
            stmts.append(self.parseStmt())
        self.match(TokenType.EOF)
        return stmts[-1]

    def parseStmt(self) -> AST:
        if self.LA().type == TokenType.ID and (self.k+1)<len(self.toks) and self.toks[self.k+1].type==TokenType.ASSIGN:
            idtok = self.match(TokenType.ID)
            self.match(TokenType.ASSIGN)
            e = self.parseE()
            return Assign(idtok.lexeme, e)
        return self.parseE()

    def parseE(self) -> AST:
        t = self.parseT()
        return self.parseEPrime(t)

    def parseEPrime(self, inherited: AST) -> AST:
        tt = self.LA().type
        if tt == TokenType.PLUS:
            self.match(TokenType.PLUS)
            t = self.parseT()
            return self.parseEPrime(Binary(Op.ADD, inherited, t))
        if tt == TokenType.MINUS:
            self.match(TokenType.MINUS)
            t = self.parseT()
            return self.parseEPrime(Binary(Op.SUB, inherited, t))
        return inherited

    def parseT(self) -> AST:
        f = self.parseF()
        return self.parseTPrime(f)

    def parseTPrime(self, inherited: AST) -> AST:
        tt = self.LA().type
        if tt == TokenType.MUL:
            self.match(TokenType.MUL)
            f = self.parseF()
            return self.parseTPrime(Binary(Op.MUL, inherited, f))
        if tt == TokenType.DIV:
            self.match(TokenType.DIV)
            f = self.parseF()
            return self.parseTPrime(Binary(Op.DIV, inherited, f))
        # Multiplicación implícita
        if tt in (TokenType.LPAREN, TokenType.NUM, TokenType.ID):
            f = self.parseF()
            return self.parseTPrime(Binary(Op.MUL, inherited, f))
        return inherited

    def parseF(self) -> AST:
        tt = self.LA().type
        if tt == TokenType.PLUS:
            self.match(TokenType.PLUS)
            return self.parseF()
        if tt == TokenType.MINUS:
            self.match(TokenType.MINUS)
            right = self.parseF()
            return Binary(Op.SUB, Num(0.0), right)
        if tt == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            e = self.parseE()
            self.match(TokenType.RPAREN)
            return e
        if tt == TokenType.NUM:
            v = float(self.match(TokenType.NUM).lexeme)
            return Num(v)
        if tt == TokenType.ID:
            name = self.match(TokenType.ID).lexeme
            return Var(name)
        raise SyntaxError(f"Se esperaba factor y se encontro {tt} (pos {self.LA().pos})")


# Interprete

class Evaluator:
    def __init__(self, st: SymTable): self.st = st
    def visit_Num(self, n: Num): n.val=n.value; return n.val
    def visit_Var(self, v: Var):
        if not self.st.contains(v.name): raise NameError(f"Variable no definida: {v.name}")
        v.val=self.st.get(v.name); return v.val
    def visit_Assign(self, a: Assign):
        val=a.expr.accept(self); self.st.put(a.name,val); a.val=val; return val
    def visit_Binary(self, b: Binary):
        l=b.left.accept(self); r=b.right.accept(self)
        if b.op==Op.ADD: b.val=l+r
        elif b.op==Op.SUB: b.val=l-r
        elif b.op==Op.MUL: b.val=l*r
        elif b.op==Op.DIV: b.val=l/r
        else: raise RuntimeError("Operador desconocido")
        return b.val


class ASTPrinter:
    def __init__(self): self.sb=[]; self.indent=0
    def _line(self,s): self.sb.append(" "*self.indent+s+"\n")
    def print(self,node):
        self.sb.clear(); self.indent=0; self._visit(node); return "".join(self.sb)
    def _visit(self,n): n.accept(self)
    def visit_Num(self,n): self._line(f"Num({n.value}) : val={self._fmt(n.val)}")
    def visit_Var(self,v): self._line(f"Var({v.name}) : val={self._fmt(v.val)}")
    def visit_Assign(self,a):
        self._line(f"Assign({a.name}) : val={self._fmt(a.val)}")
        self.indent+=2; self._visit(a.expr); self.indent-=2
    def visit_Binary(self,b):
        self._line(f"{b.op} : val={self._fmt(b.val)}")
        self.indent+=2; self._visit(b.left); self._visit(b.right); self.indent-=2
    def _fmt(self,d): return "?" if d is None else repr(d)

class AsciiTreePrinter:
    # Imprime el AST como un arbol ASCII.
    def _label(self, n: AST) -> str:
        if isinstance(n, Num): return f"Num({n.value})"
        if isinstance(n, Var): return f"Var({n.name})"
        if isinstance(n, Assign): return f"Assign({n.name})"
        if isinstance(n, Binary):
            op = {Op.ADD:"+", Op.SUB:"-", Op.MUL:"*", Op.DIV:"/"}[n.op]
            return f"Binary({op})"
        return n.__class__.__name__
    def _children(self, n: AST):
        if isinstance(n, Assign): return [n.expr]
        if isinstance(n, Binary): return [n.left, n.right]
        return []
    def print(self, node: AST) -> str:
        lines=[]
        def walk(n,prefix="",is_last=True):
            branch="└── " if is_last else "├── "
            lines.append(prefix+branch+self._label(n))
            kids=self._children(n)
            if not kids: return
            new_prefix=prefix+("    " if is_last else "│   ")
            for i,ch in enumerate(kids):
                walk(ch,new_prefix,i==len(kids)-1)
        walk(node,"",True)
        return "\n".join(lines)


def main():
    print("Calculadora EDTS. Escribe expresiones o asignaciones. Enter vacio o 'exit' para salir.")
    st = SymTable()
    while True:
        try:
            line = input(">>> ").strip()
        except EOFError: break
        if not line or line.lower()=="exit": break
        try:
            lx=Lexer(line); p=Parser(lx,st); ast=p.parseLista()
            ev=Evaluator(st); val=ast.accept(ev)
            print("AST decorado:\n"+ASTPrinter().print(ast), end="")
            print("Resultado:", val)
            print("Árbol ASCII:\n"+AsciiTreePrinter().print(ast))
            if "=" in line: print("Tabla de símbolos:", st)
        except Exception as ex:
            print("Error:", ex)
    print("Fin.")

if __name__ == "__main__":
    main()
