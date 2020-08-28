# type: ignore
import unittest
from hamcrest import (
    assert_that,
    same_instance,
    has_entries,
    anything,
    contains_exactly,
    not_,
)

import attr
import docattrs
import textwrap


def parse_doc(klass):
    stanzas = textwrap.dedent(klass.__doc__).split("\n\n")
    documented_parts = {}
    for stanza in stanzas:
        lines = iter(stanza.splitlines())
        for line in lines:
            if line != "":
                header = line
                break
        else:
            continue
        header = header.strip()
        if not header.endswith(":"):
            continue
        rest = [line.strip() for line in lines]
        documented_parts[header.strip(":")] = rest
    return documented_parts


class TestDocumentation(unittest.TestCase):
    def test_undocumented(self):
        simple_class = attr.make_class("simple", ["something"])
        documented_class = docattrs.google_style(simple_class)
        assert_that(documented_class, same_instance(simple_class))
        parts = parse_doc(simple_class)
        expected_attributes = expected_args = contains_exactly(
            "something: Undocumented"
        )
        assert_that(
            parts, has_entries(Args=expected_args, Attributes=expected_attributes)
        )

    def test_documented_simple(self):
        simple_class = attr.make_class("simple", dict(something=docattrs.doc("hooray")))
        documented_class = docattrs.google_style(simple_class)
        assert_that(documented_class, same_instance(simple_class))
        parts = parse_doc(simple_class)
        expected_attributes = expected_args = contains_exactly("something: hooray")
        assert_that(
            parts, has_entries(Args=expected_args, Attributes=expected_attributes)
        )

    def test_documented_with_doc(self):
        simple_class = attr.make_class(
            "simple", dict(something=docattrs.with_doc("hooray", attr.ib()))
        )
        documented_class = docattrs.google_style(simple_class)
        assert_that(documented_class, same_instance(simple_class))
        parts = parse_doc(simple_class)
        expected_attributes = expected_args = contains_exactly("something: hooray")
        assert_that(
            parts, has_entries(Args=expected_args, Attributes=expected_attributes)
        )

    def test_hidden_fields(self):
        simple_class = attr.make_class(
            "simple", dict(_something=docattrs.with_doc("hooray", attr.ib()))
        )
        documented_class = docattrs.google_style(simple_class)
        assert_that(documented_class, same_instance(simple_class))
        parts = parse_doc(simple_class)
        expected_args = contains_exactly("something: hooray")
        assert_that(parts, has_entries(Args=expected_args))
        assert_that(parts, not_(has_entries(Attributes=anything())))

    def test_no_init_fields(self):
        simple_class = attr.make_class(
            "simple", dict(something=docattrs.with_doc("hooray", attr.ib(init=False)))
        )
        documented_class = docattrs.google_style(simple_class)
        assert_that(documented_class, same_instance(simple_class))
        parts = parse_doc(simple_class)
        expected_attributes = contains_exactly("something: hooray")
        assert_that(parts, has_entries(Attributes=expected_attributes))
        assert_that(parts, not_(has_entries(Args=anything())))
