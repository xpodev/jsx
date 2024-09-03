from typing_extensions import Unpack
from pydom.element import Element

from ..types.html import HTMLSelectElement
from ..types import ChildType


class Select(Element):
    def __init__(self, *children: ChildType, **kwargs: Unpack[HTMLSelectElement]): ...