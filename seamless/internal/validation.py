# type: ignore

from typing import Any

from pydom.context import Context

from .utils import Promise, _obj, wraps
from ..errors import ClientError

class _DataValidationError(ClientError): ...


def wrap_with_validation(func, *, context: "Context"):
    @wraps(func)
    def no_validation(*args):
        return func(*[_obj(arg) if isinstance(arg, dict) else arg for arg in args])

    try:
        from pydantic import create_model, ValidationError
    except ImportError:
        return no_validation

    import inspect

    signature = inspect.signature(func)
    parameters = signature.parameters
    if not parameters:
        return no_validation

    func_parameters = {
        name: (
            parameter.annotation if parameter.annotation is not inspect._empty else Any,
            parameter.default if parameter.default is not inspect._empty else None,
        )
        for name, parameter in parameters.items() if parameter.annotation not in context.injector.dependencies
    }

    model = create_model(
        "SeamlessModel",
        **func_parameters,
    )

    @wraps(func)
    async def wrapper(*args):
        kwargs = {parameter: args[i] for i, parameter in enumerate(func_parameters)}

        try:
            data = model(**kwargs)
        except ValidationError as e:
            raise _DataValidationError(e.json(include_url=False))

        return await Promise(
            func(**{name: getattr(data, name) for name in func_parameters})
        )

    return wrapper
