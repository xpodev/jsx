def class_transformer():
    def matcher(key, _):
        return key == "class_name"

    def transformer(_, class_name, element):
        if isinstance(class_name, list):
            class_name = " ".join(class_name)

        element.props["class"] = " ".join(str(class_name).split())
        del element.props["class_name"]

    return matcher, transformer