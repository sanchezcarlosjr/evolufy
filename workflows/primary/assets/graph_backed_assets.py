from dagster import asset, graph_asset, op, OpExecutionContext, AssetExecutionContext, Output


@asset(group_name="learning")
def upstream_asset(context: AssetExecutionContext):
    """My awesome upstream asset

    """
    return 0


@op
def add_one(input_num):
    return input_num + 1


@op
def multiply_by_two(input_num):
    return input_num * 2


@graph_asset(group_name="learning")
def middle_asset(upstream_asset):
    return multiply_by_two(add_one(upstream_asset))


@asset(group_name="learning", compute_kind="X API")
def downstream_asset(middle_asset):
    return middle_asset + 7
