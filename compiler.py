import sys
import re

# --- PHASE 1: LEXICAL ANALYZER (10 Marks) ---
TOKEN_SPEC = [
    ('PRINT',    r'PRINT'),
    ('NUMBER',   r'\d+'),
    ('ID',       r'[a-zA-Z_]\w*'),
    ('ASSIGN',   r'='),
    ('OP',       r'[+\-*/]'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('SEMI',     r';'),
    ('SKIP',     r'[ \t\n]+'),
    ('MISMATCH', r'.'),
]

def lex(code):
    tokens = []
    regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)
    for mo in re.finditer(regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP': continue
        elif kind == 'MISMATCH': 
            raise RuntimeError(f"Lexical Error: Unexpected character '{value}'")
        tokens.append((kind, value))
    return tokens

# --- PHASES 2-6: PARSER, SEMANTIC, IR, OPTIMIZATION, CODE GEN ---
class RetroCompiler:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.symbol_table = {} # Phase 3: Symbol Table
        self.ir_instructions = [] # Phase 5: Intermediate Representation

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type=None):
        token = self.tokens[self.pos]
        if expected_type and token[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, found {token[0]}")
        self.pos += 1
        return token

    def parse_program(self):
        while self.peek():
            self.parse_statement()
        return self.ir_instructions

    def parse_statement(self):
        token = self.peek()
        if token[0] == 'ID':
            var_name = self.consume('ID')[1]
            self.consume('ASSIGN')
            self.parse_expression()
            self.consume('SEMI')
            self.ir_instructions.append(f"STORE {var_name}")
            self.symbol_table[var_name] = "INT"
        elif token[0] == 'PRINT':
            self.consume('PRINT')
            self.parse_expression()
            self.consume('SEMI')
            self.ir_instructions.append("OUT")

    def parse_expression(self):
        self.parse_term()
        while self.peek() and self.peek()[1] in ('+', '-'):
            op = self.consume('OP')[1]
            self.parse_term()
            self.ir_instructions.append("ADD" if op == '+' else "SUB")

    def parse_term(self):
        self.parse_factor()
        while self.peek() and self.peek()[1] in ('*', '/'):
            op = self.consume('OP')[1]
            self.parse_factor()
            self.ir_instructions.append("MUL" if op == '*' else "DIV")

    def parse_factor(self):
        token = self.consume()
        if token[0] == 'NUMBER':
            # PHASE 6: OPTIMIZATION (Constant Folding)
            # In a real compiler, we'd pre-calculate math here. 
            # For this IR, we just push the value.
            self.ir_instructions.append(f"PUSH {token[1]}")
        elif token[0] == 'ID':
            # PHASE 3: SEMANTIC CHECK
            if token[1] not in self.symbol_table:
                raise NameError(f"Semantic Error: Variable '{token[1]}' undefined")
            self.ir_instructions.append(f"LOAD {token[1]}")
        elif token[0] == 'LPAREN':
            self.parse_expression()
            self.consume('RPAREN')

# --- PHASE 7: COMMAND LINE INTERFACE ---
# --- PHASE 7: UPDATED COMMAND LINE INTERFACE ---
def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <input.calc> [-o output.txt] [--debug]")
        return

    input_file = sys.argv[1]
    # Default output name if -o is not provided
    output_file = "output.asm"
    debug = "--debug" in sys.argv

    if "-o" in sys.argv:
        try:
            output_file = sys.argv[sys.argv.index("-o") + 1]
        except IndexError:
            print("Error: -o flag requires a filename.")
            return

    try:
        with open(input_file, 'r') as f:
            code = f.read()

        print(f"Reading {input_file}...")
        tokens = lex(code)
        compiler = RetroCompiler(tokens)
        ir_code = compiler.parse_program()
        result = "\n".join(ir_code)
        
        if debug:
            print("\n--- DEBUG: STACK MACHINE CODE ---")
            print(result)
            print("---------------------------------\n")

        # Force write to file
        with open(output_file, 'w') as f:
            f.write(result)
        
        print("-------------------------------------------")
        print(f"SUCCESS: Compiled '{input_file}'")
        print(f"TARGET FILE CREATED: {output_file}")
        print("-------------------------------------------")

    except FileNotFoundError:
        print(f"FILE ERROR: Could not find '{input_file}' in this folder.")
    except Exception as e:
        print(f"COMPILER ERROR: {e}")

if __name__ == "__main__":
    main()