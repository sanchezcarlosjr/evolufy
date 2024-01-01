from dagster import asset, graph_asset, op, OpExecutionContext, AssetExecutionContext, Output
from dagster_shell import create_shell_script_op, create_shell_command_op
from dagster import file_relative_path, job


@asset(group_name="learning", key_prefix=['a', 'b'])
def upstream_asset():
    """My awesome upstream asset

    """
    return 0



@op
def multiply_by_two(input_num):
    return input_num


@graph_asset(group_name="learning")
def middle_asset():
    result=create_shell_command_op('echo "hello, world!"', name="hello_world")
    return result()


@asset(group_name="learning", compute_kind="X API")
def downstream_asset(middle_asset):
    return middle_asset+" 2"
