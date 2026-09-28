# Installation

[Back to README](../README.md)

## Requirements

- Python 3.9–3.12. Python 3.13 and later are not recommended: the pinned `matplotlib<3.9` has no prebuilt wheels for
  them and fails to build (confirmed on Python 3.14).
- `pip` and `git` available on your `PATH`

The main dependencies are installed automatically (see [setup.cfg](../setup.cfg)): numpy (below 2.0), numba 0.59 or
later, pandas, scipy, matplotlib (below 3.9), pyedflib, scikit-learn, toml, flatten-dict, fpdf, openpyxl,
msoffcrypto-tool and nimbaldetach.

## 1. Create an environment (recommended)

Using `venv` (with a Python 3.9–3.12 interpreter):

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
```

Using `uv`, which can download a suitable Python for you:

```bash
uv venv -p 3.12 .venv
source .venv/bin/activate
```

Using conda:

```bash
conda create -n nimbalwear python=3.11
conda activate nimbalwear
```

## 2. Install nimbalwear

These instructions install from the [Brain-Institute/nimbalwear](https://github.com/Brain-Institute/nimbalwear) fork.

Latest version (the `main` branch):

```bash
pip install git+https://github.com/Brain-Institute/nimbalwear
```

A specific version, pinned to a tag or commit hash:

```bash
pip install git+https://github.com/Brain-Institute/nimbalwear@<tag-or-commit>
```

Pinning to a commit gives reproducible installs. The fork has no per-release branches such as `0.21`.

As a dependency of another package (`setup.py` / `setup.cfg`):

```python
install_requires=['nimbalwear@git+https://github.com/Brain-Institute/nimbalwear@[ref]']
```

The fork is based on the original [nimbal/nimbalwear](https://github.com/nimbal/nimbalwear) project, which
has per-release branches (`0.18` to `0.21`).

## 3. Check the install

```bash
python -c "import nimbalwear; print(nimbalwear.__version__)"
```

The top-level package exposes the two main classes:

```python
from nimbalwear import Study, Device
```

## Installing for development

Clone the repository and install it in editable mode, so changes to the source take effect without reinstalling:

```bash
git clone https://github.com/Brain-Institute/nimbalwear.git
cd nimbalwear
pip install -e .
```

The default settings file ([settings.toml](../src/nimbalwear/settings/settings.toml)) and the gait template
([pushoff_df.csv](../src/nimbalwear/data/pushoff_df.csv)) are package data and are installed with the package.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Failed building wheel for matplotlib` | Your Python is too new for `matplotlib<3.9`. Use Python 3.9–3.12. |
| Errors about numpy 2.x | nimbalwear requires `numpy<2.0.0`. Reinstall with `pip install "numpy<2"`. |
| numba install fails on Python 3.12 | Make sure numba is 0.59 or later: `pip install "numba>=0.59"`. |
| `ModuleNotFoundError: nimbaldetach` | Reinstall nimbalwear, or install it directly with `pip install nimbaldetach`. |
| Matplotlib API errors in reports | nimbalwear requires `matplotlib<3.9`. |
