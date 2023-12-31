ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

activate:
	micromamba activate evolufy

launch_dagster:
	export DAGSTER_HOME=$(ROOT_DIR); nohup dagster dev -w ./workspace.yml |> dagster.log


export:
	micromamba env export -n evolufy -f environment.lock.yml
	micromamba activate evolufy