from typing import Any
class Event:
    """Structured record of a single visualization action.

    Parameters
    ----------
    _type : str
        Category of the event (e.g. ``"compare"``, ``"swap"``).
    target : object
        Metadata describing the structure that emitted the event.
    indices : list[int] | None, optional
        Index or indices affected by the event.
    other : Any | None, optional
        Secondary operand (e.g. another cell/pointer) involved in the event.
    value : Any | None, optional
        Payload value (new assignment, lookup result, etc.).
    step_id : int | None, optional
        Optional sequential identifier when replaying events.
    result : bool | None, optional
        Outcome flag for comparisons or predicates.
    comment : str | None, optional
        Free-form annotation.
    line_info : tuple[str, int, str] | None, optional
        Source metadata captured by the tracer as ``(filename, lineno, func_name)``.
    """

    def __init__(self,_type:str,target:object,
    indices:list[int]|None=None,other:Any|None=None,value:Any|None=None,step_id:int|None=None,result:bool|None=None,comment:str|None=None,
    line_info:tuple[str,int,str]|None=None):
        self._type = _type
        self.target = target
        self.indices = indices
        self.other = other
        self.value = value
        self.step_id = step_id
        self.result = result
        self.comment = comment
        self.line_info = line_info
    def __repr__(self):
        return f"<Event type={self._type} target={type(self.target).__name__}>"
