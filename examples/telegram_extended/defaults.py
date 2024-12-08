from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from stollen import Stollen, StollenMethod

if TYPE_CHECKING:
    from .types import LinkPreviewOptions


def default_link_preview_options(
    stollen: Stollen,
    _: StollenMethod[Any, Any],
) -> LinkPreviewOptions:
    from .client import TelegramBot
    from .types import LinkPreviewOptions

    bot = cast(TelegramBot, stollen)
    return LinkPreviewOptions(is_disabled=bot.link_preview_disabled)
