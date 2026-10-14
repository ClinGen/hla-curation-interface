"""Builds the family tree of a published curation for its HLArepo page.

A curation's family is every published curation connected to it through
copied_from: the original, its updates, their updates, and so on. A family can
branch when more than one update is made from the same curation. Unpublished
copies are HCI drafts, so they're left out. Updates can only be made from
published curations, so leaving drafts out never cuts the tree in the middle.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from curation.constants.models.common import Status

if TYPE_CHECKING:
    from curation.models import Curation
    from repo.models import PublishedCuration


@dataclass
class LineageNode:
    """One published curation in a family tree.

    Attributes:
        published: The published curation.
        children: The published updates made from it, oldest first.
        prefix: The box-drawing characters that draw its place in the tree.
        is_current: Whether it's the curation whose page is showing the tree.
        is_newest: Whether it's the most recently published in the family.
    """

    published: "PublishedCuration"
    children: list["LineageNode"] = field(default_factory=list)
    prefix: str = ""
    is_current: bool = False
    is_newest: bool = False


@dataclass
class Lineage:
    """A published curation's family tree and its text description.

    Attributes:
        root: The original curation of the family.
        description: Sentences that state the tree in words, for readers who
            can't see it.
    """

    root: LineageNode
    description: list[str]


def _published_copies(curation: "Curation") -> list["Curation"]:
    copies = [
        copy
        for copy in curation.copies.all()  # type: ignore
        if copy.status == Status.PUBLISHED
    ]
    return sorted(copies, key=lambda copy: copy.publication.published_at)  # type: ignore


def _build(
    curation: "Curation", current: "Curation", nodes: list[LineageNode]
) -> LineageNode:
    node = LineageNode(
        published=curation.publication,  # type: ignore
        is_current=curation.pk == current.pk,
    )
    nodes.append(node)
    node.children = [
        _build(copy, current, nodes) for copy in _published_copies(curation)
    ]
    return node


def _draw(node: LineageNode, indent: str) -> None:
    """Sets each child's prefix, the way the tree command draws a directory."""
    for index, child in enumerate(node.children):
        is_last = index == len(node.children) - 1
        child.prefix = indent + ("└── " if is_last else "├── ")
        _draw(child, indent + ("    " if is_last else "│   "))


def _join(slugs: list[str]) -> str:
    if len(slugs) <= 2:
        return " and ".join(slugs)
    return ", ".join(slugs[:-1]) + f", and {slugs[-1]}"


def _describe(root: LineageNode, nodes: list[LineageNode]) -> list[str]:
    def slug(node: LineageNode) -> str:
        return node.published.curation.slug

    current = next(node for node in nodes if node.is_current)
    newest = next(node for node in nodes if node.is_newest)
    sentences = [
        f"This family has {len(nodes)} published classifications.",
        f"{slug(root)} is the original.",
    ]
    for node in nodes:
        updates = [slug(child) for child in node.children]
        if len(updates) == 1:
            sentences.append(f"{updates[0]} is an update of {slug(node)}.")
        elif updates:
            sentences.append(f"{_join(updates)} are updates of {slug(node)}.")
    if current is newest:
        sentences.append(f"You're viewing {slug(current)}, the newest classification.")
    else:
        sentences.append(
            f"You're viewing {slug(current)}. The newest classification is "
            f"{slug(newest)}."
        )
    return sentences


def build_lineage(published: "PublishedCuration") -> Lineage | None:
    """Builds the family tree of a published curation.

    Args:
        published: The published curation whose page shows the tree.

    Returns:
        The family tree with its description, or None if the curation has no
        published original or updates.
    """
    current = published.curation
    root = current
    while root.copied_from is not None:
        root = root.copied_from
    nodes: list[LineageNode] = []
    root_node = _build(root, current, nodes)
    if len(nodes) == 1:
        return None
    max(nodes, key=lambda node: node.published.published_at).is_newest = True
    _draw(root_node, "")
    return Lineage(root=root_node, description=_describe(root_node, nodes))
