def flatten_array(result,objs) -> list:
    """Flattens an iterable"""
    if not isinstance(objs,(tuple,list)):
            result.append(objs)
            return 
    for obj in objs:
        flatten_array(result=result,objs=obj)
    return result
def make_grid(self,r=3,c=3,cell_height=1,cell_width=1):
    """
    Creates a grid of VisualArrays in the scene.

    Parameters
    ----------
    r : int, optional
        Number of rows in the grid. Defaults to 3.
    c : int, optional
        Number of columns in the grid. Defaults to 3.
    cell_height : float, optional
        Height of each cell in the arrays. Defaults to 1.
    cell_width : float, optional
        Width of each cell in the arrays. Defaults to 1.

    Returns
    -------
    list
        A list of VisualArrays that make up the grid.
    """
    from Structures.arrays import VisualArray
    from manim import UP,DOWN,VGroup
    arrays = []
    prev_array:VisualArray = None
    for i in range(r):
        if prev_array:
            start_pos = prev_array.get_top() + UP*0.533
        else:
            start_pos = DOWN*0.5*r
            
        array = VisualArray([""] * c,label=f"Array at row {i}",scene=self,start_pos=start_pos,cell_height=cell_height,cell_width=cell_width)
        arrays.append(array)
        self.play(array.create())
        prev_array = array

    return arrays


def is_user_file(path_str: str) -> bool:
    """Return True if the given path belongs to user-authored code.

    Priority:
    - If Components.runtime.ACTIVE_SCRIPT is set, only that exact file counts.
    - Otherwise, accept files under PROJECT_ROOT (or CWD) and not under
      EXCLUDED_DIRS.
    """
    from pathlib import Path
    import Components.runtime as runtime

    try:
        p = Path(path_str).resolve()
    except Exception:
        return False

    active = getattr(runtime, "ACTIVE_SCRIPT", None)
    if active is not None:
        try:
            return p == Path(active).resolve()
        except Exception:
            return False

    root = getattr(runtime, "PROJECT_ROOT", Path.cwd().resolve())
    try:
        rel = p.relative_to(root)
    except Exception:
        return False

    excludes = getattr(runtime, "EXCLUDED_DIRS", set())
    excluded_lc = {str(x).lower() for x in excludes}
    parts_lc = [part.lower() for part in rel.parts]
    if any(part in excluded_lc for part in parts_lc):
        return False
    return True

