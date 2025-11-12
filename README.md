# Calculadora EDTS en Python

Este proyecto implementa una **calculadora con análisis léxico, sintactico, semantico e interpretacion** de expresiones matematicas simples, usando el enfoque EDTS.  

El sistema analiza, construye y evalúa árboles de sintaxis abstracta (**AST**) para expresiones aritméticas y asignaciones de variables, mostrando además el árbol en formato ASCII.


## Caracteristicas principales

- Analisis lexico (Lexer): Divide la entrada en tokens (numeros, identificadores, operadores, parentesis, etc.).  
- Análisis sintactico (Parser LL(1)): Construye un **árbol de sintaxis abstracta (AST)** según una gramatica definida.  
- Evaluación (Evaluator): Calcula el resultado de las expresiones y maneja una **tabla de símbolos** para almacenar variables.  
- Visualización:  
  - Impresión del AST decorado con valores.
  - Representación del árbol en formato ASCII.
 
## CONJUNTOS:
    Primeros(E) = { '(', num, id }
    Primeros(E') = { '+', '-', ε }
    Primeros(T) = { '(', num, id }
    Primeros(T') = { '*', '/', ε }
    Primeros(F) = { '(', num, id }
    Primeros(Stmt) = { id, '(', num }
    Siguientes(E) = { ')', ';', EOF }
    Siguientes(E') = { ')', ';', EOF }
    Siguientes(T) = { '+', '-', ')', ';', EOF }
    Siguientes(T') = { '+', '-', ')', ';', EOF }
    Siguientes(F) = { '*', '/', '+', '-', ')', ';', EOF }
    Siguientes(Stmt) = { ';', EOF }


## Ejecución

python edts.py

4. Escribe expresiones o asignaciones.  
   Para salir, presiona **Enter** en blanco o escribe `exit`.


## Ejemplos de uso

### Expresiones aritméticas

```
>>> 2 + 3 * 4
AST decorado:
ADD : val=14.0
  Num(2.0) : val=2.0
  MUL : val=12.0
    Num(3.0) : val=3.0
    Num(4.0) : val=4.0
Resultado: 14.0
Árbol ASCII:
└── Binary(+)
    ├── Num(2.0)
    └── Binary(*)
        ├── Num(3.0)
        └── Num(4.0)
```

### Asignaciones de variables

```
>>> x = 5 * 2
AST decorado:
Assign(x) : val=10.0
  MUL : val=10.0
    Num(5.0) : val=5.0
    Num(2.0) : val=2.0
Resultado: 10.0
Árbol ASCII:
└── Assign(x)
    └── Binary(*)
        ├── Num(5.0)
        └── Num(2.0)
Tabla de símbolos: {x=10.0}
```

## Gramatica soportada

La gramática LL(1) implementada es:

```
Lista  → Stmt (';' Stmt)* EOF
Stmt   → ID '=' E | E
E      → T E'
E'     → '+' T E' | '-' T E' | ε
T      → F T'
T'     → '*' F T' | '/' F T' | (F T') [multiplicación implicita] | ε
F      → '+' F | '-' F | '(' E ')' | NUM | ID
```

---

## Estructura del codigo

| Sección | Descripcion |
|----------|--------------|
| **Lexer** | Convierte la entrada en tokens. |
| **AST (Arbol de Sintaxis Abstracta)** | Define los nodos para números, variables, operaciones y asignaciones. |
| **Parser** | Construye el AST siguiendo la gramática LL(1). |
| **Evaluator** | Recorre el AST y calcula el resultado. |
| **SymTable** | Guarda las variables y sus valores. |
| **ASTPrinter / AsciiTreePrinter** | Muestran el árbol en formato decorado y ASCII. |
| **main()** | Interfaz de consola que ejecuta la calculadora. |

---

## Ejemplo de sesion completa

```
Calculadora EDTS. Escribe expresiones o asignaciones. Enter vacio o 'exit' para salir.
>>> a = 10
>>> b = 2.5
>>> a / b + 3
Resultado: 7.0
>>> exit
Fin.
```

