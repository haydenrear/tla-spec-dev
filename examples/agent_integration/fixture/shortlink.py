"""A link shortener with expiry and a reservation window.

The fixture the integration agents are pointed at. It is deliberately small and
deliberately NOT trivial: it has real state (three maps), a real ordering
constraint (a reservation must be claimed before it expires), and one behaviour
that only shows up as a sequence (a claimed slug can be released and re-reserved
by a different owner, but never while the first owner still holds it).

That last property is the reason this file exists rather than a CRUD toy: it is
false for single states and true only over a trace, so a spec that models it has
to model the transition, not the shape. An agent that writes a spec for this
file and never represents `release` has under-modeled it, and the harness can
see that from the outside without being told the answer.

No third-party imports: the integration run must not depend on the fixture's
environment resolving.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class ShortlinkError(Exception):
    """A refused operation. The message names the rule that refused it."""


@dataclass
class Shortener:
    #: slug -> target url, for slugs that are live
    links: dict[str, str] = field(default_factory=dict)
    #: slug -> owner, for slugs reserved but not yet claimed
    reservations: dict[str, str] = field(default_factory=dict)
    #: slug -> owner, for slugs that are live and still owned
    owners: dict[str, str] = field(default_factory=dict)

    def reserve(self, slug: str, owner: str) -> None:
        if not slug or not owner:
            raise ShortlinkError("reserve: slug and owner are both required")
        if slug in self.reservations:
            raise ShortlinkError(f"reserve: {slug!r} is already reserved")
        if slug in self.links:
            raise ShortlinkError(f"reserve: {slug!r} is already live")
        self.reservations[slug] = owner

    def claim(self, slug: str, owner: str, target: str) -> None:
        held_by = self.reservations.get(slug)
        if held_by is None:
            raise ShortlinkError(f"claim: {slug!r} is not reserved")
        if held_by != owner:
            raise ShortlinkError(f"claim: {slug!r} is reserved by someone else")
        if not target:
            raise ShortlinkError("claim: a target is required")
        del self.reservations[slug]
        self.links[slug] = target
        self.owners[slug] = owner

    def release(self, slug: str, owner: str) -> None:
        """Give up a live slug. Only the owner may, and only while it is live."""
        if slug not in self.links:
            raise ShortlinkError(f"release: {slug!r} is not live")
        if self.owners.get(slug) != owner:
            raise ShortlinkError(f"release: {slug!r} is not yours")
        del self.links[slug]
        del self.owners[slug]

    def resolve(self, slug: str) -> str:
        target = self.links.get(slug)
        if target is None:
            raise ShortlinkError(f"resolve: {slug!r} is not live")
        return target
