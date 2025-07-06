"""
Calculator tool for AI Agent
"""
import ast
import operator
import math
from typing import Dict, Any, Union
from .base_tool import BaseTool, ToolResult

class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations including basic arithmetic, trigonometry, and advanced functions"
        )
        
        # Safe operators and functions
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
            ast.USub: operator.neg,
        }
        
        # Safe functions
        self.functions = {
            'abs': abs,
            'round': round,
            'max': max,
            'min': min,
            'sum': sum,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'ceil': math.ceil,
            'floor': math.floor,
            'pi': math.pi,
            'e': math.e,
        }
    
    async def execute(self, expression: str) -> ToolResult:
        """
        Execute mathematical calculation
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            ToolResult with calculation result
        """
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Replace common mathematical constants and functions
            expression = self._preprocess_expression(expression)
            
            # Parse and evaluate safely
            result = self._safe_eval(expression)
            
            return ToolResult(
                success=True,
                result={
                    "expression": expression,
                    "result": result,
                    "type": type(result).__name__
                },
                metadata={"operation": "mathematical_calculation"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Calculation failed: {str(e)}"
            )
    
    def _preprocess_expression(self, expression: str) -> str:
        """
        Preprocess expression to handle common mathematical notation
        
        Args:
            expression: Raw mathematical expression
            
        Returns:
            Preprocessed expression
        """
        # Replace common mathematical notation
        replacements = {
            '^': '**',  # Power operator
            'π': str(math.pi),
            'pi': str(math.pi),
            'e': str(math.e),
        }
        
        for old, new in replacements.items():
            expression = expression.replace(old, new)
        
        return expression
    
    def _safe_eval(self, expression: str) -> Union[int, float]:
        """
        Safely evaluate mathematical expression
        
        Args:
            expression: Expression to evaluate
            
        Returns:
            Evaluation result
        """
        try:
            # Parse the expression
            node = ast.parse(expression, mode='eval')
            
            # Evaluate the parsed tree
            return self._eval_node(node.body)
            
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def _eval_node(self, node) -> Union[int, float]:
        """
        Recursively evaluate AST node
        
        Args:
            node: AST node to evaluate
            
        Returns:
            Evaluation result
        """
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            return self.operators[type(node.op)](operand)
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            if func_name in self.functions:
                args = [self._eval_node(arg) for arg in node.args]
                return self.functions[func_name](*args)
            else:
                raise ValueError(f"Unknown function: {func_name}")
        elif isinstance(node, ast.Name):
            if node.id in self.functions:
                return self.functions[node.id]
            else:
                raise ValueError(f"Unknown variable: {node.id}")
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get parameters schema for calculator tool"""
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to calculate. Supports basic arithmetic (+, -, *, /, **), trigonometry (sin, cos, tan), logarithms (log, log10), and constants (pi, e). Example: '2 + 3 * 4', 'sin(pi/2)', 'sqrt(16)'"
                }
            },
            "required": ["expression"]
        }
