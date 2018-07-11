# coding: utf8
"""
Tests for validate.py
"""

import os
import textwrap

from path import Path

from i18n import validate

from . import I18nToolTestCase


HERE = Path(__file__).dirname()
TEST_DATA = HERE / "data"


VALIDATION_PROBLEMS = [
    (
        'Different tags in source and translation',
        u'Your name is {name}',
        u'Su nombre es {nombre}',
        u'"{name}" vs "{nombre}"',
    ),
    (
        'Different tags in source and translation',
        u'Two tags: {one} and {two}',
        u'One tag: {one} and not two',
        u'"{two}" missing',
    ),
    (
        'Different tags in source and translation',
        u'One tag: {one}',
        u'Two tags: {one} and {two}',
        u'"{two}" added',
    ),
    (
        'Different tags in source and translation',
        'No tags',
        "Added some <a href='https://en.wikipedia.org/wiki/HTML'>HTML</a>",
        '"</a>", "<a href=\'https://en.wikipedia.org/wiki/HTML\'>" added'
    ),
    (
        'Non-BMP char',
        u'Astral character (pile of poo), bad for JavaScript: \U0001f4a9',
        u'Astral character (pile of poo), bad for JavaScript: \U0001f4a9',
    ),
    (
        'Different tags in source and translation',
        u'1. There are {num} things | 1. There are {num} things',
        u'1. Estas {num} objectos | 1. Estas {nomx} objectos',
        u'"{nomx}" added',
    ),
    (
        'Different tags in source and translation',
        u'2. There are {num} things | 2. There are {num} things',
        u'2. Estas {nomx} objectos | 2. Estas {num} objectos',
        u'"{nomx}" added',
    ),
    ('Empty translation', u'This string should not be empty'),
]


class TestValidate(I18nToolTestCase):
    """
    Tests functionality in i18n/validate.py, because if Sarina weren't
    quitting, she'd be making me write tests.

    """

    maxDiff = None

    def test_no_problems(self):
        problems = validate.check_messages(TEST_DATA / "django_before.po")
        self.assertEqual(problems, [])

    def test_problems(self):
        problems = validate.check_messages(TEST_DATA / "validation_problems.po", report_empty=True)
        self.assertEqual(problems, VALIDATION_PROBLEMS)

    def test_problems_no_empty(self):
        problems = validate.check_messages(TEST_DATA / "validation_problems.po", report_empty=False)
        without_empty = [p for p in VALIDATION_PROBLEMS if p[0] != 'Empty translation']
        self.assertEqual(problems, without_empty)

    def test_report_problems(self):
        self.addCleanup(os.remove, "foo.prob")
        validate.report_problems("foo.po", [
            ('Silly text', u'¿This is silly?'),
            ('Problematic', u'ƧƬЯIПG 1', u'ŚŤŔĨŃĞ 2'),
        ])
        expected_output = textwrap.dedent("""\
            Silly text
              msgid: ¿This is silly?

            Problematic
              msgid: ƧƬЯIПG 1
              -----> ŚŤŔĨŃĞ 2

            """)
        with open("foo.prob") as f:
            self.assertEqual(f.read(), expected_output)
