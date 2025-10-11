"""
Basic tests for VisualArray — pointer-free edition.
Covers construction, indexing, mutation, arithmetic, highlighting,
and error handling.  Designed for direct call-and-see execution.
"""
from manim import *
from Structures.arrays import VisualArray



def test_create(array:VisualArray):
    """Play the create animation to ensure array spawns properly."""
    array.play(array.create())
    print("✅ test_create completed")




def test_index_access(array:VisualArray):
    """Access elements and trigger highlight animations."""
    if not array.elements:
        array.play(array.create())
    _ = array[0]
    _ = array[1]
    _ = array[len(array) - 1]
    print("✅ test_index_access completed")




def test_arithmetic(array:VisualArray):
    """Perform arithmetic updates to ensure operator dunders behave."""
    if not array.elements:
        array.play(array.create())
    array[0] += 2
    array[1] -= 1
    array[2] *= 3
    array[3] //= 2
    array[4] %= 3
    print("✅ test_arithmetic completed")




def test_assignment_and_append(array:VisualArray):
    """Directly assign and append values, confirming redraw logic."""
    if not array.elements:
        array.play(array.create())
    array[0] = 99
    array[1] = -5
    array.append(42)
    array.play(array.highlight(len(array) - 1))
    print("test_assignment_and_append completed")




def test_highlight_unhighlight(array:VisualArray):
    """Check visual highlight/unhighlight animations."""
    if not array.elements:
        array.play(array.create())
    array.play(array.highlight(1))
    array.play(array.unhighlight(array[1]))
    print("test_highlight_unhighlight completed")




def test_index_bounds(array:VisualArray):
    """Ensure invalid indexes raise proper exceptions."""
    if not array.elements:
        array.play(array.create())
    try:
        _ = array[999]
    except IndexError:
        print("✅ test_index_bounds caught expected IndexError")
    else:
        print("❌ test_index_bounds failed to raise IndexError")
        
def test_full(array):
    """
    Run all VisualArray tests in sequence.
    This aggregates every pointer-free test into one smooth visual routine.
    """
    print("\n🚀 Running complete VisualArray test suite...\n")

    # Import self-contained tests (same file scope)
    tests = [
        test_create,
        test_index_access,
        test_arithmetic,
        test_assignment_and_append,
        test_highlight_unhighlight,
        test_index_bounds,
    ]

    for func in tests:
        name = func.__name__
        print(f"▶ Executing {name}...")
        try:
            func(array)
            print(f"✅ {name} passed.\n")
        except Exception as e:
            print(f"❌ {name} failed: {e}\n")

    print("🎯 All tests executed.\n")