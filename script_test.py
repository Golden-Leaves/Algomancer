# test_eq_logic.py
from Structures.arrays import VisualArray  # or wherever your class lives

# Make a dummy scene or pass None for now
arr = VisualArray([1, 2, 3])
a, b = arr.get_element(0), arr.get_element(1)

# Ensure parent is linked (should be by constructor)
print(a.parent is arr)  # expect True

# Perform comparison
print(a == b)           # triggers __eq__

# Check event trace
print(arr._trace[-1].__dict__)  # or whatever structure your log_event appends to