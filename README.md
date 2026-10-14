# SARS-CoV-2 Nsp1 nascent chain tracking analysis

This repository contains analysis code associated with the manuscript:
"Live-cell, single-molecule imaging resolves the dual nature of mRNA silencing by SARS-CoV-2 Nsp1"

## Overview

This study uses live-cell nascent chain tracking to quantify how SARS-CoV-2 Nsp1 alters reporter and endogenous mRNA abundance, translation-site formation, nascent-chain signal, elongation/runoff behavior, and mRNA degradation.

## Repository structure

- `analysis/`: final analysis notebooks used for manuscript quantification.
- `environment/`: software environment files.
- `docs/`: workflow notes and input descriptions.
- `example_data/`: small example files for testing code structure.

## Main analyses

| File | Purpose | Manuscript figures |
|---|---|---|
| `analysis/crop_array_analysis.ipynb` | Reporter mRNA and translation-site quantification | All figures except those listed below |
| `analysis/tethered_HT_analysis_full_runoff_tanh_plot_refactor.ipynb` | Harringtonine runoff analysis and elongation/initiation estimates | Fig. 2 and Fig. S7 |
| `analysis/Endogenous_Data.ipynb` | Endogenous MYH9 analysis | Fig. 6 and Fig. S6 |

## Data availability

Full imaging datasets and processed source data are available at:
[DOI placeholder]

This GitHub repository contains analysis code but not full raw microscopy datasets.

## Software environment

See `environment/environment.yml` or `environment/requirements.txt`.

## Citation

If using this code, please cite:
[Manuscript citation placeholder]
