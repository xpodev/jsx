from seamless import Component


class Route(Component):
    def __init__(self, path, component: Component):
        self.path = path
        self.component = component

    def render(self):
        return self.component.render()