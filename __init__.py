"""ComfyUI MiniMax H3 GH + RefMod — unified pack.

Merges two community packs into a single extension:

* Goohai-MiniMax-H3_Integration — the "智能一体化(GH)" conditioning node, its
  adapter, the T8 dual-clock sampler / AV decoder, the tiled sampler and the
  latent upscaler.
* ComfyUI-MiniMaxH3Mod — no-training RefMod reference adapters (create / load /
  apply / inspect / library nodes).

The integrated node now owns the "Load H3 RefMods" functionality: the panel
adds RefMod rows that are bound to ``<Video n>`` tags in order (``mod_1`` ->
``<Video 1>``, ``mod_2`` -> ``<Video 2>``, ...) and the node exposes one merged
``mods`` output next to its private ``MiniMax`` pipe.

Both packs originally used different ComfyUI node APIs (V3 ``comfy_entrypoint``
for GH, V1 ``NODE_CLASS_MAPPINGS`` for RefMod).  A module may only expose one
of them, so this pack registers the GH ``io.ComfyNode`` classes through the V1
mapping as well — ComfyUI executes V3 classes natively there, and the RefMod
nodes stay untouched.
"""

from __future__ import annotations

WEB_DIRECTORY = "./web"

from .gh import nodes as _gh_nodes
from .gh import long_video as _gh_long_video
from .gh import prompt_optimizer as _gh_prompt_optimizer  # noqa: F401  (registers API routes)

_GH_NODE_CLASSES = {
    "LanxiH3Studio": _gh_nodes.MiniMaxH3IntegrationGH,
    "LanxiH3LongVideo": _gh_long_video.MiniMaxH3LongVideoRunnerGH,
}

_GH_DISPLAY_NAMES = {
    "LanxiH3Studio": "MiniMaxH3长视频操作台（lanxi)",
    "LanxiH3LongVideo": "MiniMax-H3 长视频分段采样（lanxi）",
}

NODE_CLASS_MAPPINGS = {
    **_GH_NODE_CLASSES,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **_GH_DISPLAY_NAMES,
}

# LoRA list for the per-segment LoRA slots.  ``folder_paths`` is resolved at
# request time so extra_model_paths.yaml changes are picked up on refresh.
def _register_loras_route() -> None:
    try:
        from aiohttp import web
        import folder_paths
        from server import PromptServer

        instance = getattr(PromptServer, "instance", None)
        if instance is None:
            return

        @instance.routes.get("/lanxi/minimax_h3/loras")
        async def _list_loras(_request):
            try:
                names = list(folder_paths.get_filename_list("loras"))
            except Exception:
                names = []
            return web.json_response({"loras": names})
    except Exception:
        # API-only / CLI contexts: the panel simply falls back to its cache.
        pass


_register_loras_route()

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
