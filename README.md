[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![PyPI-Server](https://img.shields.io/pypi/v/evolufy.svg)](https://pypi.org/project/evolufy/)

<!-- These are examples of badges you might also want to add to your README. Update the URLs accordingly.
[![Built Status](https://api.cirrus-ci.com/github/<USER>/evolufy.svg?branch=main)](https://cirrus-ci.com/github/<USER>/evolufy)
[![ReadTheDocs](https://readthedocs.org/projects/evolufy/badge/?version=latest)](https://evolufy.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/evolufy/main.svg)](https://coveralls.io/r/<USER>/evolufy)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/evolufy.svg)](https://anaconda.org/conda-forge/evolufy)
[![Monthly Downloads](https://pepy.tech/badge/evolufy/month)](https://pepy.tech/project/evolufy)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/evolufy)
-->

# evolufy

> Yet another algotrade framework

Evolufy is a framework designed for the development, deployment, and observability of trading algorithms, featuring options for DataOps/MLOps through open-source tools. It offers simplicity and flexibility, allowing the use of any algorithm, incorporation of any data source, and ensuring easy local deployment without the need for TripleO (OpenStack on OpenStack on OpenStack).
We have integrated a suite of DataOps to deliver production-ready features:
## Infrastructure
- Use conda, micrombamba and virtual environment to create a rapid prototype.
- You likely need a database, a straightforward method for creating dashboards and reports from various data sources, and an easy way to manipulate your data. For these purposes, we provide you with the ```workspace``` Git submodule.

## Workflow Orchestration
* [Dagster](https://dagster.io/) is an open-source data orchestrator that defines assets through software. It's designed to facilitate the easy creation of data pipelines locally, and it also offers straightforward deployment on Kubernetes.
This makes it a versatile tool for managing data workflows, particularly in environments where both local development and scalable deployment are important.
* Strategies can be formulated using a configuration file (Domain-Specific Language) or directly in Python.
* TODO: Drag & Drop Orchestration
## Asset Tracking and Model Metadata Management Tools
* Track your experiments and data with dvc and DAGsHub.
## Experimentation
* Employ time series analysis.
* Optimize your investment portfolio with Modern Portfolio Theory.
* Create another strategy.
## Testing
* Analyze your strategies with backtesting and traditional machine learning metrics.
* Utilize typical strategies or build on top of them.
* Useful notebooks, streamlit, and CLI.
## Deployment and Interoperability
* Utilize Gradio or FastAPI to build microservices based on your models, or deploy them on your own infrastructure using ONNX. 
* Employ Dagster to develop workflows in your cluster or locally, integrating your data sources and preferred brokers.
## Self-hosted web
- We recommend using Cloudflare Tunnels for self-hosting your web applications.


## Installation

In order to set up the necessary environment:

1. review and uncomment what you need in `environment.yml` and create an environment `evolufy` with the help of [conda]:
   ```
   conda env create -f environment.yml
   ```
2. activate the new environment with:
   ```
   conda activate evolufy
   ```

> **_NOTE:_**  The conda environment will have evolufy installed in editable mode.
> Some changes, e.g. in `setup.cfg`, might require you to run `pip install -e .` again.


Optional and needed only once after `git clone`:

3. install several [pre-commit] git hooks with:
   ```bash
   pre-commit install
   # You might also want to run `pre-commit autoupdate`
   ```
   and checkout the configuration under `.pre-commit-config.yaml`.
   The `-n, --no-verify` flag of `git commit` can be used to deactivate pre-commit hooks temporarily.

4. install [nbstripout] git hooks to remove the output cells of committed notebooks with:
   ```bash
   nbstripout --install --attributes notebooks/.gitattributes
   ```
   This is useful to avoid large diffs due to plots in your notebooks.
   A simple `nbstripout --uninstall` will revert these changes.

   
Then take a look into the `scripts` and `notebooks` folders.


## Dependency Management & Reproducibility

1. Always keep your abstract (unpinned) dependencies updated in `environment.yml` and eventually
   in `setup.cfg` if you want to ship and install your package via `pip` later on.
2. Create concrete dependencies as `environment.lock.yml` for the exact reproduction of your
   environment with:
   ```bash
   conda env export -n evolufy -f environment.lock.yml
   ```
   For multi-OS development, consider using `--no-builds` during the export.
3. Update your current environment with respect to a new `environment.lock.yml` using:
   ```bash
   conda env update -f environment.lock.yml --prune
   ```
## Project Organization

```
├── AUTHORS.md              <- List of developers and maintainers.
├── CHANGELOG.md            <- Changelog to keep track of new features and fixes.
├── CONTRIBUTING.md         <- Guidelines for contributing to this project.
├── Dockerfile              <- Build a docker container with `docker build .`.
├── LICENSE.txt             <- License as chosen on the command-line.
├── README.md               <- The top-level README for developers.
├── configs                 <- Directory for configurations of model & application.
├── data
│   ├── external            <- Data from third party sources.
│   ├── interim             <- Intermediate data that has been transformed.
│   ├── processed           <- The final, canonical data sets for modeling.
│   └── raw                 <- The original, immutable data dump.
├── docs                    <- Directory for Sphinx documentation in rst or md.
├── environment.yml         <- The conda environment file for reproducibility.
├── models                  <- Trained and serialized models, model predictions,
│                              or model summaries.
├── notebooks               <- Jupyter notebooks. Naming convention is a number (for
│                              ordering), the creator's initials and a description,
│                              e.g. `1.0-fw-initial-data-exploration`.
├── pyproject.toml          <- Build configuration. Don't change! Use `pip install -e .`
│                              to install for development or to build `tox -e build`.
├── references              <- Data dictionaries, manuals, and all other materials.
├── reports                 <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures             <- Generated plots and figures for reports.
├── scripts                 <- Analysis and production scripts which import the
│                              actual PYTHON_PKG, e.g. train_model.
├── setup.cfg               <- Declarative configuration of your project.
├── setup.py                <- [DEPRECATED] Use `python setup.py develop` to install for
│                              development or `python setup.py bdist_wheel` to build.
├── src
│   └── evolufy             <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `pytest`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```

<!-- pyscaffold-notes -->

## Note

This project has been set up using [PyScaffold] 4.5 and the [dsproject extension] 0.0.post158+g5fb5c40.d20231203.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[Jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[Google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[PyScaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
