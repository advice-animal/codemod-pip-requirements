# This code will eventually be available in the 'bumpreqs' project.

import re
from dataclasses import dataclass, replace
from typing import Generator, Optional

from packaging.requirements import Requirement


@dataclass
class BaseNode:
    def with_changes(self, **kwargs):
        return replace(self, **kwargs)

    def build(self, buf):
        raise NotImplementedError

    def dump(self, buf, indent=""):
        raise NotImplementedError


@dataclass
class UnparsedLine(BaseNode):
    orig_line: str

    def build(self, buf):
        buf.write(self.orig_line)

    def dump(self, buf, indent=""):
        buf.write(indent + repr(self) + "\n")


@dataclass
class VcsRequirementLine(BaseNode):
    requirement: str
    newline: str = "\n"

    def build(self, buf):
        buf.write(self.requirement)
        buf.write(self.newline)

    def dump(self, buf, indent=""):
        buf.write(indent + repr(self) + "\n")


@dataclass
class UrlRequirementLine(BaseNode):
    requirement: str
    newline: str = "\n"

    def build(self, buf):
        buf.write(self.requirement)
        buf.write(self.newline)

    def dump(self, buf, indent=""):
        buf.write(indent + repr(self) + "\n")


@dataclass
class LocalPathRequirementLine(BaseNode):
    # ./foo
    # -e ../foo
    requirement: str
    newline: str = "\n"

    def build(self, buf):
        buf.write(self.requirement)
        buf.write(self.newline)

    def dump(self, buf, indent=""):
        buf.write(indent + repr(self) + "\n")


@dataclass
class RequirementLine(BaseNode):
    # a parsed Requirement can't roundtrip
    requirement: str
    whitespace_before_requirement: str = ""
    whitespace_after_requirement: str = ""
    comment: str = ""
    newline: str = "\n"

    def build(self, buf):
        buf.write(self.requirement)
        buf.write(self.whitespace_before_requirement)
        buf.write(self.whitespace_after_requirement)
        buf.write(self.comment)
        buf.write(self.newline)

    def dump(self, buf, indent=""):
        buf.write(indent + repr(self) + "\n")


WELL_FORMED_REQUIREMENT_LINE = re.compile(
    r"([ \t]*)([^# \t][^#]*?)([ \t]*)(#.*?)?(\r?\n)$"
)


@dataclass
class RequirementFile:
    children: [BaseNode] = ()

    @classmethod
    def parse(cls, data: str) -> "RequirementFile":
        children: List[BaseNode] = []
        if not data.endswith("\n"):
            if "\r\n" in data:
                data += "\r\n"
            else:
                data += "\n"

        for line in data.splitlines(True):
            match = WELL_FORMED_REQUIREMENT_LINE.match(line)
            if not match:
                children.append(UnparsedLine(line))
                continue

            (
                whitespace_before_requirement,
                value,
                whitespace_after_requirement,
                comment,
                newline,
            ) = match.groups()

            if value.startswith(("-", "#")):
                children.append(UnparsedLine(line))
                continue
            elif value.startswith((".", "/")):
                assert whitespace_before_requirement == ""
                assert whitespace_after_requirement == ""
                assert not comment
                children.append(LocalPathRequirementLine(value, newline))
                continue
            # N.b. see COMMENT_RE in pip/req/req_file.py
            elif value and comment and not whitespace_after_requirement:
                # TODO strip
                value = value + whitespace_after_requirement + comment
                children.append(VcsRequirementLine(value, newline))
                continue
            elif "://" in value:
                assert whitespace_before_requirement == ""
                assert whitespace_after_requirement == ""
                assert not comment
                children.append(VcsRequirementLine(value, newline))
                continue

            Requirement(value)  # validates

            children.append(
                RequirementLine(
                    requirement=value,
                    whitespace_before_requirement=whitespace_before_requirement,
                    whitespace_after_requirement=whitespace_after_requirement,
                    comment=comment or "",
                    newline=newline,
                )
            )

        return cls(children=children)

    def build(self, buf):
        for c in self.children:
            c.build(buf)

    def dump(self, buf, indent=""):
        for c in self.children:
            c.dump(buf, indent)


if __name__ == "__main__":
    import sys

    try:
        RequirementFile.parse(open(sys.argv[1]).read())
    except Exception as e:
        print(sys.argv[1])
        raise
