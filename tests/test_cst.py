from io import StringIO
from codemod_pip_requirements import (
    LocalPathRequirementLine,
    RequirementFile,
    RequirementLine,
    UnparsedLine,
    VcsRequirementLine,
)


def test_empty():
    expected = ""
    r = RequirementFile.parse(expected)
    assert len(r.children) == 1
    assert isinstance(r.children[0], UnparsedLine)
    t = StringIO()
    r.build(t)
    # This is a minor change that we can't roundtrip
    assert t.getvalue() == "\n"


def test_just_newline():
    expected = "\n"
    r = RequirementFile.parse(expected)
    assert len(r.children) == 1
    assert isinstance(r.children[0], UnparsedLine)
    t = StringIO()
    r.build(t)
    assert t.getvalue() == expected


def test_line_with_opts():
    expected = "-e foo\n"
    r = RequirementFile.parse(expected)
    assert len(r.children) == 1
    assert isinstance(r.children[0], UnparsedLine)
    t = StringIO()
    r.build(t)
    assert t.getvalue() == expected


def test_just_comment():
    expected = "# comment\n"
    r = RequirementFile.parse(expected)
    assert len(r.children) == 1
    assert isinstance(r.children[0], UnparsedLine)
    t = StringIO()
    r.build(t)
    assert t.getvalue() == expected


def test_requirement():
    expected = "x\n"
    r = RequirementFile.parse(expected)
    assert len(r.children) == 1
    assert isinstance(r.children[0], RequirementLine)
    assert r.children[0].requirement == "x"
    t = StringIO()
    r.build(t)
    assert t.getvalue() == expected


def test_requirement_comment():
    expected = "x # comment\n"
    r = RequirementFile.parse(expected)
    assert len(r.children) == 1
    assert isinstance(r.children[0], RequirementLine)
    assert r.children[0].requirement == "x"
    t = StringIO()
    r.build(t)
    assert t.getvalue() == expected


def test_local_requirement():
    expected = "../foo # comment\n"
    r = RequirementFile.parse(expected)
    assert len(r.children) == 1
    assert isinstance(r.children[0], LocalPathRequirementLine)
    assert r.children[0].requirement == "../foo"
    t = StringIO()
    r.build(t)
    assert t.getvalue() == expected


def test_requirement_cffi_url():
    expected = """\
cffi @ https://github.com/python-cffi/cffi/archive/refs/heads/main.zip; python_version > "3.12" # Temporary workaround for Python 3.13 until next CFFI release
"""
    r = RequirementFile.parse(expected)
    assert len(r.children) == 1
    assert isinstance(r.children[0], VcsRequirementLine)
    assert (
        r.children[0].requirement
        == 'cffi @ https://github.com/python-cffi/cffi/archive/refs/heads/main.zip; python_version > "3.12"'
    )
    t = StringIO()
    r.build(t)
    assert t.getvalue() == expected


def test_special_case_url_hash_mark():
    expected = "http://foo#egg_info=t\n"
    r = RequirementFile.parse(expected)
    assert len(r.children) == 1
    assert isinstance(r.children[0], VcsRequirementLine)
    assert r.children[0].requirement == "http://foo#egg_info=t"
    t = StringIO()
    r.build(t)
    assert t.getvalue() == expected
