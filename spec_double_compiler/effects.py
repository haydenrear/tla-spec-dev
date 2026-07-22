"""Small project-author helpers for semantic effect providers.

The framework owns deterministic seed derivation and scope cleanup. Projects
still own every concrete response, exception, state transition, and assertion.
"""

from __future__ import annotations

from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, Generic, TypeVar

from .runtime import EffectProviderContext


EFFECT_SEED_VERSION = "tla-spec-dev/effect-seed/v1"

T = TypeVar("T")


def derive_effect_seed(root_seed: int, case_name: str, iteration: int, port_name: str) -> int:
    """Return the versioned, process-independent seed for one bound port.

    JSON supplies an unambiguous UTF-8 framing; SHA-256 avoids Python's salted
    ``hash()`` and makes the protocol stable across processes and platforms.
    The first 128 digest bits are ample for project-local ``random.Random``.
    """

    payload = json.dumps(
        [EFFECT_SEED_VERSION, int(root_seed), str(case_name), int(iteration), str(port_name)],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:16], "big")


class EffectProviderEnterCleanupError(RuntimeError):
    """An installer failed and its already-entered resources also failed cleanup."""

    def __init__(
        self,
        primary: Exception,
        cleanup_errors: tuple[Exception, ...],
    ) -> None:
        self.primary = primary
        self.cleanup_errors = cleanup_errors
        cleanup_summary = "; ".join(
            f"{type(error).__name__}: {error}" for error in cleanup_errors
        )
        super().__init__(
            f"provider enter failed with {type(primary).__name__}: {primary}; "
            f"partial cleanup also failed: {cleanup_summary}"
        )


def _ordered_cleanup_errors(
    cleanup_error: Exception,
    primary: Exception,
) -> tuple[Exception, ...]:
    """Recover ExitStack cleanup failures in the order cleanup attempted them."""

    newest_first: list[Exception] = []
    seen: set[int] = set()
    current: BaseException | None = cleanup_error
    while isinstance(current, Exception) and current is not primary and id(current) not in seen:
        seen.add(id(current))
        newest_first.append(current)
        current = current.__context__
    newest_first.reverse()
    return tuple(newest_first)


class _StackBinding(Generic[T]):
    """One-shot binding whose resources are acquired only during ``__enter__``."""

    def __init__(
        self,
        context: EffectProviderContext,
        installer: Callable[[EffectProviderContext, ExitStack], T],
    ) -> None:
        self._context = context
        self._installer = installer
        self._stack: ExitStack | None = None
        self._entered = False

    def __enter__(self) -> T:
        if self._entered:
            raise RuntimeError("effect provider bindings are one-shot; call provider.bind(context) again")
        self._entered = True
        stack = ExitStack()
        stack.__enter__()
        self._stack = stack
        try:
            return self._installer(self._context, stack)
        except BaseException as primary:
            # Close every context successfully entered before a later installer
            # step failed. Ignore a truthy return; helpers never suppress.
            self._stack = None
            try:
                stack.__exit__(type(primary), primary, primary.__traceback__)
            except BaseException as cleanup_error:
                if isinstance(primary, Exception) and isinstance(cleanup_error, Exception):
                    raise EffectProviderEnterCleanupError(
                        primary,
                        _ordered_cleanup_errors(cleanup_error, primary),
                    ) from cleanup_error
                # Cancellation/control-flow exceptions must remain the primary
                # signal even if partial cleanup also fails. Retain that cleanup
                # failure explicitly as the cause instead of replacing the
                # KeyboardInterrupt/SystemExit/GeneratorExit.
                raise primary.with_traceback(primary.__traceback__) from cleanup_error
            raise

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        stack, self._stack = self._stack, None
        if stack is not None:
            stack.__exit__(exc_type, exc, traceback)
        return False


class _FactoryProvider(Generic[T]):
    def __init__(self, installer: Callable[[EffectProviderContext, ExitStack], T]) -> None:
        self._installer = installer

    def bind(self, context: EffectProviderContext) -> _StackBinding[T]:
        return _StackBinding(context, self._installer)


def context_provider(
    installer: Callable[[EffectProviderContext, ExitStack], T],
) -> _FactoryProvider[T]:
    """Build a provider from a lazy patch/context installer.

    ``installer(context, stack)`` may call ``stack.enter_context(...)`` once or
    many times and returns the value injected at ``context.effects[port]`` (or
    ``None`` for a self-installed patch). Each ``bind`` gets a fresh one-shot
    stack. If a later nested acquisition fails, earlier entries are restored.
    """

    return _FactoryProvider(installer)


def temporary_root_provider(
    builder: Callable[[Path, EffectProviderContext], T],
    *,
    prefix: str = "effect-root-",
) -> _FactoryProvider[T]:
    """Build an explicit-DI provider around a fresh temporary directory.

    The directory is created lazily inside the case-iteration work directory,
    passed to ``builder(root, context)``, and removed after every success or
    failure path. This is a root lifecycle helper, not a fake operating system.
    """

    if (
        not isinstance(prefix, str)
        or not prefix
        or prefix in {".", ".."}
        or Path(prefix).is_absolute()
        or "/" in prefix
        or "\\" in prefix
        or "\x00" in prefix
    ):
        raise ValueError("temporary-root prefix must be a non-empty path-free filename prefix")

    def install(context: EffectProviderContext, stack: ExitStack) -> T:
        context.work_dir.mkdir(parents=True, exist_ok=True)
        root = Path(
            stack.enter_context(
                TemporaryDirectory(prefix=prefix, dir=context.work_dir)
            )
        )
        return builder(root, context)

    return context_provider(install)
