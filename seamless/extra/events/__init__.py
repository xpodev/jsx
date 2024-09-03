from typing import Callable

from pydom.context import Context
from pydom.rendering.render_state import RenderState
from pydom.rendering.tree.nodes import ContextNode

from .database import ElementsDatabase, Action

from ..feature import Feature
from ...internal.constants import (
    CLAIM_COOKIE_NAME,
    SEAMLESS_ELEMENT_ATTRIBUTE,
    SEAMLESS_INIT_ATTRIBUTE,
)
from ...internal.cookies import Cookies
from ...internal.validation import wrap_with_validation
from ...rendering.render_state import RenderState


class EventsFeature(Feature):
    def __init__(self, context: ContextBase, claim_time=20.0):
        super().__init__(context)

        self.DB = ElementsDatabase(claim_time=claim_time)
        self.context.add_prop_transformer(*self.events_transformer())

        from ...context import Context

        if isinstance(self.context, Context):
            self.context.on("connect", self.on_connect)
            self.context.on("disconnect", self.on_disconnect)
            self.context.on("event", self.event)

    async def event(self, sid: str, data: str, event_data: dict):
        return await self.DB.invoke_event(data, event_data, scope=sid)

    async def on_connect(self, sid: str, env: dict):
        cookies = Cookies(env.get("HTTP_COOKIE", ""))
        claim_id = cookies[CLAIM_COOKIE_NAME]
        if not claim_id:
            return await self.context.server.disconnect(sid)  # type: ignore - since on_connect is called only when self.context is a Context, we can safely ignore the type error

        self.DB.claim(claim_id, sid)

    async def on_disconnect(self, sid: str):
        self.DB.release_actions(sid)

    def events_transformer(self):

        def matcher(key: str, value):
            return key.startswith("on_") and callable(value)

        def transformer(
            key: str, value: Callable, element: ContextNode, render_state: RenderState
        ):
            event_name = key.removeprefix("on").replace("_", "").lower()
            action = self.DB.add_event(
                Action(
                    wrap_with_validation(
                        self.context.inject(value), context=self.context
                    ),
                    str(hash(value)),
                ),
                render_state.custom_data.get("events_scope", None),
            )
            element.props[SEAMLESS_INIT_ATTRIBUTE] = (
                str(element.props.get(SEAMLESS_INIT_ATTRIBUTE, ""))
                + f"""this.addEventListener('{event_name}', (event) => {{
              const outEvent = seamless.instance.eventObjectTransformer(
                event, 
                seamless.instance.serializeEventObject(event)
              );
            seamless.instance.socket.emit("event", "{action.id}", outEvent);
          }});"""
            )

            element.props[SEAMLESS_ELEMENT_ATTRIBUTE] = True
            del element.props[key]

        return matcher, transformer
