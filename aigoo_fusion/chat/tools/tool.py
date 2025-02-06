import inspect
import re
from typing import Any, Callable, Dict, Union, get_type_hints


class Tool:
	"""
	Decorator class for creating tool definitions.
	"""
	def __init__(self, strict: bool = True):
		self.strict = strict

	def __call__(self, func: Callable) -> Callable:
		func._is_tool = True # type: ignore # Mark the function as a tool
		func._tool_strict = self.strict # type: ignore # Store strict setting
		return func

	@staticmethod
	def _get_tool_definition(func: Callable, strict: bool = True) -> Dict[str, Any]:
		"""
		Generates tool metadata dictionary from a Python function.
		"""
		# Map Python types to JSON Schema types
		type_mapping = {
			int: "integer",
			float: "number",
			str: "string",
			bool: "boolean",
			list: "array",
			dict: "object",
			type(None): "null"
		}

		# Get function metadata
		func_name = func.__name__
		docstring = inspect.getdoc(func)
		signature = inspect.signature(func)
		parameters = signature.parameters

		# Format description
		desc = docstring if docstring else ""
		desc_pattern = r'^(.*?)(?:\n\s*(Args|Parameters):)'
		dec_match = re.search(desc_pattern, desc, re.DOTALL)
		if dec_match:
			extracted_description = dec_match.group(1).strip()
			desc = extracted_description

		# Create the tool definition
		tool_def = {
			"name": func_name,
			"description": desc or "",
			"strict": strict,
			"parameters": {
				"type": "object",
				"properties": {},
				"required": [],
				"additionalProperties": False,
			}
		}

		# Get type hints for better type information
		type_hints = get_type_hints(func)

		# Process each parameter
		for param_name, param in parameters.items():
			# Skip 'self' parameter for methods
			if param_name == 'self':
				continue

			# Get parameter type from type hints or annotation
			python_type = type_hints.get(param_name, param.annotation)

			# Handle Union types
			if hasattr(python_type, "__origin__") and python_type.__origin__ is Union:
				# Get all non-None types from the Union
				types = [t for t in python_type.__args__ if t is not type(None)]
				if len(types) == 1:
					python_type = types[0]
				else:
					# If multiple types, default to string
					python_type = str

			param_type = type_mapping.get(python_type, "string")

			# Extract parameter description from docstring
			param_description = ""
			if docstring:
				# Look for parameter in docstring (supports various docstring formats)
				param_patterns = [
					f"{param_name} (", # Google style
					f"{param_name}:", # Sphinx style
					f":param {param_name}:", # reST style
				]
				for pattern in param_patterns:
					if pattern in docstring:
						start = docstring.find(pattern) + len(pattern)
						end = docstring.find("\n", start)
						if end != -1:
							param_description = docstring[start:end].strip()
							if "):" in param_description:
								match = re.search(r"\):\s*(.*)", param_description)
								if match:
									param_description = match.group(1)
							break

			# Extract default value
			param_default_value = None
			if param.default != inspect.Parameter.empty:
				param_default_value = f" (default: {param.default})"

			# Add parameter details
			tool_def["parameters"]["properties"][param_name] = {
				"type": param_type,
				"description": param_description + (param_default_value if param_default_value else "")
			}

			# Add required params
			if strict:
				# Direct add param as required
				tool_def["parameters"]["required"].append(param_name)
			else:
				# Add to required if no default value
				if param.default == inspect.Parameter.empty:
					tool_def["parameters"]["required"].append(param_name)

		return tool_def
