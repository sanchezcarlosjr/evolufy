from zipline.data.bundles import register as register_bundle


def register(**args):
    def decorator(bundle):
        return register_bundle(
            bundle.__name__,
            bundle,
            **args
        )
    return decorator
