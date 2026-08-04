"""Project-owned semantic effect provider.

Generated cases select the abstract effect outcome. Providers choose concrete
representatives and bind repository-owned implementations for one case and one
deterministic fuzz iteration. Read references/effect_providers.md.

SCAFFOLD: implement one provider against the generated port Protocols before
enabling its mapping tables. The framework ships no domain implementations.
"""

from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator
from typing import Any

from spec_double_compiler.runtime import EffectProviderContext


class ProjectEffectProvider:
    @contextmanager
    def bind(self, context: EffectProviderContext) -> Iterator[Any | None]:
        # SCAFFOLD: acquire the repository-owned implementation selected by
        # context.port_name and context.case. Use context.derived_seed for
        # deterministic representatives. Yield the generated-port
        # implementation, or None only when this scope installs and restores
        # its own bounded integration.
        raise NotImplementedError(
            f"SCAFFOLD: bind generated port {context.port_name}"
        )
        yield None


effect_provider = ProjectEffectProvider()
