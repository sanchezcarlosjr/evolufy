# Evolufy
Yet Another Investment Portfolio Optimization Library

[Check out my Thesis to know more](https://carlos-eduardo-sanchez-torres.sanchezcarlosjr.com/Evolufy-Making-Sustainable-Finance-a-Reality-with-a-Web-based-Investment-Portfolio-Library-that-Uti-c3a1983ae6d24851b979d114b3784c2d)

# Getting started
Learn how you can change the library for your needss.
[Getting started](./1.0-cest-getting_started.ipynb)

# Datasets
## Mexico Issuers
We got the Mexico issuers dataset from [emisoras](https://databursatil.com/docs.html#emisoras) after applying

```bash
[.[] | to_entries[] | .value[] + {"Nombre": .key}]
```

## History
We got the Mexico prices history dataset from [historicos](https://databursatil.com/docs.html#historicos) after applying
```bash
[.[] 
| to_entries[] 
| .value[] + {"Nombre": .key} 
| select( .Estatus | contains("ACTIVA")) 
| "\(.Nombre)\(.Serie)"
] 
```
