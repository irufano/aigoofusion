from copy import deepcopy
from typing import Dict, Any, List, Optional

class WorkflowState:
    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        self._state = initial_state or {}
        self._history: List[Dict[str, Any]] = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state."""
        # Return a deep copy to prevent direct modifications
        value = self._state.get(key, default)
        return deepcopy(value)
    
    def get_current(self) -> Dict[str, Any]:
        """Get the current state."""
        return deepcopy(self._state)
    
    def _update(self, values: Dict[str, Any]) -> None:
        """Internal method to update state. Only used by Workflow class."""
        self._state.update(deepcopy(values))
        self._history.append(deepcopy(self._state))
        
# class WorkflowState:
# 	def __init__(self, initial_state: Dict[str, Any] = None): # type: ignore
# 		self._state = initial_state or {}
# 		self._history: List[Dict[str, Any]] = []

# 	def get(self, key: str, default: Any = None) -> Any:
# 		"""Get a value from the state."""
# 		return self._state.get(key, default)

# 	def set(self, key: str, value: Any) -> None:
# 		"""Set a value in the state."""
# 		self._state[key] = value
# 		self._history.append(deepcopy(self._state))

# 	def update(self, values: Dict[str, Any]) -> None:
# 		"""Update multiple values in the state."""
# 		self._state.update(values)
# 		self._history.append(deepcopy(self._state))

# 	def delete(self, key: str) -> None:
# 		"""Delete a key from the state."""
# 		if key in self._state:
# 			del self._state[key]
# 			self._history.append(deepcopy(self._state))

# 	def clear(self) -> None:
# 		"""Clear all state."""
# 		self._state.clear()
# 		self._history.append(deepcopy(self._state))

# 	def get_history(self) -> List[Dict[str, Any]]:
# 		"""Get the state history."""
# 		return self._history

# 	def get_current(self) -> Dict[str, Any]:
# 		"""Get the current state."""
# 		return deepcopy(self._state)

# 	def rollback(self, steps: int = 1) -> None:
# 		"""Rollback state by n steps."""
# 		if steps <= 0 or not self._history:
# 			return

# 		if steps > len(self._history):
# 			steps = len(self._history)

# 		self._history = self._history[:-steps]
# 		self._state = deepcopy(self._history[-1]) if self._history else {}
