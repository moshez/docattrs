from __future__ import annotations
from typing import Any, Sequence, Mapping

import textwrap

import attr
import publication

AttribType = Any


@attr.s(frozen=True, auto_attribs=True)
class Description:
    content: str


def doc(
    content: str, /, *args: Sequence[Any], **kwargs: Mapping[str, Any]
) -> AttribType:
    ret_value = attr.ib(*args, **kwargs)  # type: ignore
    with_doc(content, ret_value)
    return ret_value


def with_doc(content: str, attrib: AttribType) -> AttribType:
    attrib.metadata.update({Description: Description(content)})
    return attrib


def google_style(x: type) -> type:
    data = textwrap.dedent(x.__doc__ or "")
    attributes = []
    args = []
    undocumented = Description("Undocumented")
    for field in attr.fields(x):
        description = field.metadata.get(Description, undocumented)
        name = field.name.lstrip("_")
        message = f"    {name}: {description.content}"
        if not field.name.startswith("_"):
            attributes.append(message)
        if field.init:
            args.append(message)
    if args:
        data += "\nArgs:\n" + "\n".join(args) + "\n"
    if attributes:
        data += "\nAttributes:\n" + "\n".join(attributes) + "\n"
    x.__doc__ = data
    return x


__all__ = ["doc", "with_doc", "google_style"]

publication.publish()
