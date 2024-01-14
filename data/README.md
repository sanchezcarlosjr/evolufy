# Data sources
The directories listed below are tracked by dvc instead of git.


```
   ├── external            <- Data from third party sources.
   ├── interim             <- Intermediate data that has been transformed.
   ├── processed           <- The final, canonical data sets for modeling.
   └── raw                 <- The original, immutable data dump.
   └── data                <- zipline bundles
```

If you wish to pull datasets from any remote that has evolved data, use ```dvc pull```.

When you need to save your changes, use:
```
dvc add external interim proccesed
```

If you wish to download a file and track it in the same step, use ```dvc import```.

