"""
Basic tests for VisualArray — pointer-free edition.
Covers construction, indexing, mutation, arithmetic, highlighting,
and error handling.  Designed for direct call-and-see execution.
"""
from manim import *
from Structures.arrays import VisualArray
from Structures.pointers import Pointer
from Tests.test_decorator import test


def create_array(array:VisualArray) -> None:
    """Creates the array if it's not created yet."""
    if not array.elements:
        array.play(array.create())

@test
def test_create(array:VisualArray):
    """Play the create animation to ensure array spawns properly."""
    create_array(array)




@test
def test_index_access(array:VisualArray):
    """Access elements and trigger highlight animations."""
    create_array(array)
    _ = array[0]
    _ = array[1]
    _ = array[len(array) - 1]




@test
def test_arithmetic(array:VisualArray):
    """Perform arithmetic updates to ensure operator dunders behave."""
    create_array(array)
    array[0] += 2
    array[1] -= 1
    array[2] *= 3
    array[3] //= 2
    array[4] %= 3



@test
def test_assignment_and_append(array:VisualArray):
    """Directly assign and append values, confirming redraw logic."""
    create_array(array)
    array[0] = 99
    array[1] = -5
    array.append(42)
    array.play(array.highlight(len(array) - 1))


@test
def test_internal_comparisons(array: VisualArray) -> None:
    """
    Tests comparison behavior between elements *within the same VisualArray*.
    No new structures or .create() calls are made.
    """


    n = len(array)
    assert n >= 2, "Array must have at least two elements for comparison tests"

    # compare each adjacent pair
    for i in range(n - 1):
        left = array[i]
        right = array[i + 1]

        # value-level comparisons
        lt = left < right
        gt = left > right
        eq = left == right
        ne = left != right

        # internal consistency
        assert not (lt and gt), f"Inconsistent order at indices {i}, {i+1}"
        assert eq != ne, f"Equality inconsistency at indices {i}, {i+1}"

        print(f"cells[{i}]={left.value} vs cells[{i+1}]={right.value} → "
              f"lt={lt}, gt={gt}, eq={eq}")

@test
def test_highlight_unhighlight(array:VisualArray):
    """Check visual highlight/unhighlight animations."""
    create_array(array)
    array.play(array.highlight(1))
    array.play(array.unhighlight(array[1]))
    array.play(array.highlight(1))


@test
def test_pointer_basic(array: VisualArray, ptr: Pointer) -> None:
    """Ensure a pointer can move and still reference correct cells."""
    create_array(array)
    assert ptr.master is array, "Pointer.master mismatch"
    ptr += 1
    ptr -= 1


@test
def test_pointer_move_sequence(array: VisualArray, ptr: Pointer) -> None:
    """
    Safely tests pointer movement across valid indices within the array.
    Prevents out-of-bounds moves (no Shadow Realm excursions).
    """
   
    n = len(array)
    assert n >= 2, "Array must have at least two elements to move pointer."

    # Define a movement pattern relative to array bounds
    # We’ll make sure every move keeps the pointer inside [0, n-1].
    move_pattern = [1, -1, 2, -2, n - 2, -(n - 2)]
    for step in move_pattern:
        target = ptr.value + step
        if 0 <= target < n:
            ptr += step
            print(f"Pointer moved to index {ptr.value}")
        else:
            print(f"⚠️ Skipped invalid move: {ptr.value} + ({step}) = {target}")



@test
def test_pointer_vs_index_highlight(array: VisualArray, ptr: Pointer) -> None:
    """Use pointer index directly in array highlight/unhighlight."""
    create_array(array)
    assert ptr.master is array
    idx = ptr.value
    array.play(array.highlight(idx))
    array.play(array.unhighlight(idx))


@test
def test_pointer_comparison(array: VisualArray, ptr_a: Pointer, ptr_b: Pointer) -> None:
    """Compare two pointers’ values and animate the larger one."""
    create_array(array)
    assert ptr_a.master is array and ptr_b.master is array
    ia, ib = ptr_a.value, ptr_b.value
    va, vb = array[ia].value, array[ib].value
    hi = ia if va >= vb else ib
    array.play(array.highlight(hi))
    array.play(array.unhighlight(hi))


@test
def test_pointer_guided_swap(array: VisualArray, ptr_a: Pointer, ptr_b: Pointer) -> None:
    """Swap values pointed to by two pointers."""
    create_array(array)
    assert ptr_a.master is array and ptr_b.master is array
    array.play(array.swap(ptr_a.value, ptr_b.value))




@test
def test_full_with_pointers(array: VisualArray, ptr_a: Pointer, ptr_b: Pointer | None = None) -> None:
    """Run the full array + pointer integration suite."""

    create_array(array)
    base_tests = [
        test_create,
        test_index_access,
        test_arithmetic,
        test_assignment_and_append,
        test_highlight_unhighlight,
    ]
    #the reason for doing this is just to pre-pass ptr_a and ptr_b, no need to pass later
    pointer_tests = [
        lambda arr: test_pointer_basic(arr, ptr_a), 
        lambda arr: test_pointer_move_sequence(arr, ptr_a),
        lambda arr: test_pointer_vs_index_highlight(arr, ptr_a),
    ]
    if ptr_b is not None:
        pointer_tests += [
            lambda arr: test_pointer_comparison(arr, ptr_a, ptr_b),
            lambda arr: test_pointer_guided_swap(arr, ptr_a, ptr_b),
        ]

    for func in base_tests + pointer_tests:
        func(array)



@test
def test_pointers_only(array: VisualArray, ptr_a: Pointer, ptr_b: Pointer | None = None) -> None:
    """Run only pointer-related tests without touching array internals."""

    create_array(array)
    tests = [
        lambda arr: test_pointer_basic(arr, ptr_a),
        lambda arr: test_pointer_move_sequence(arr, ptr_a),
        lambda arr: test_pointer_vs_index_highlight(arr, ptr_a),
    ]
    if ptr_b is not None:
        tests += [
            lambda arr: test_pointer_comparison(arr, ptr_a, ptr_b),
            lambda arr: test_pointer_guided_swap(arr, ptr_a, ptr_b),
        ]

    for func in tests:
        func(array)
