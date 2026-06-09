from flask import Flask, render_template, request, jsonify
import ast
import operator

app = Flask(__name__)

# Safely map AST operators to safe operator functions
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Dynamic check for older ast attributes (like ast.Num) to support legacy Python versions safely
AST_NUM = getattr(ast, 'Num', None)

def safe_eval(expression):
    """
    Safely evaluate a mathematical expression string without using eval().
    Only basic arithmetic and unary positive/negative operators are allowed.
    """
    if not expression or not isinstance(expression, str):
        return "0"
        
    try:
        # Parse the mathematical string into an AST
        node = ast.parse(expression, mode='eval')
        
        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            elif isinstance(node, ast.Constant):  # Python 3.8+
                if isinstance(node.value, (int, float)):
                    return node.value
                raise TypeError("Only integers and floats are allowed")
            elif AST_NUM is not None and isinstance(node, AST_NUM):  # Fallback for Python < 3.8
                return node.n
            elif isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                op_type = type(node.op)
                if op_type in ALLOWED_OPERATORS:
                    if op_type == ast.Div and right == 0:
                        raise ZeroDivisionError("Division by zero")
                    return ALLOWED_OPERATORS[op_type](left, right)
                raise ValueError(f"Operator {op_type.__name__} is not allowed")
            elif isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                op_type = type(node.op)
                if op_type in ALLOWED_OPERATORS:
                    return ALLOWED_OPERATORS[op_type](operand)
                    
                raise ValueError(f"Operator {op_type.__name__} is not allowed")
            else:
                raise ValueError(f"Unsupported AST node type: {type(node).__name__}")
                
        result = _eval(node)
        # format float results to avoid trailing .0 if integer
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return result
    except Exception as e:
        raise ValueError(f"Evaluation error: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json() or {}
    expression = data.get("expression", "").strip()

    try:
        result = safe_eval(expression)
        return jsonify({"result": str(result)})
    except Exception as e:
        app.logger.error(f"Error evaluating expression '{expression}': {e}")
        return jsonify({"result": "Error"})

if __name__ == "__main__":
    app.run(debug=True)
