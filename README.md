# scitex-resource

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>System resource info, processor usage logging, RAM limiting + host-identity config.</b></p>

<p align="center">
  <a href="https://scitex-resource.readthedocs.io/">Full Documentation</a> · <code>uv pip install scitex-resource[all]</code>
</p>

<!-- scitex-badges:start -->
<p align="center">
  <a href="https://pypi.org/project/scitex-resource/"><img src="https://img.shields.io/pypi/v/scitex-resource?label=pypi" alt="pypi"></a>
  <a href="https://pypi.org/project/scitex-resource/"><img src="https://img.shields.io/pypi/pyversions/scitex-resource?label=python" alt="python"></a>
  <a href="https://scitex-resource.readthedocs.io/en/latest/"><img src="https://img.shields.io/readthedocs/scitex-resource?label=docs" alt="docs"></a>
</p>
<p align="center">
  <a href="https://github.com/ywatanabe1989/scitex-resource/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/ywatanabe1989/scitex-resource/ci.yml?branch=develop&label=tests" alt="tests"></a>
  <a href="https://codecov.io/gh/ywatanabe1989/scitex-resource"><img src="https://img.shields.io/codecov/c/github/ywatanabe1989/scitex-resource/develop?label=cov" alt="cov"></a>
</p>
<!-- scitex-badges:end -->

---

## Quick Start

```python
import scitex_resource as r

print(r.get_host_name())           # canonical host identity
metrics = r.get_metrics()          # cpu / mem / disk / gpu / load
specs = r.get_specs()              # rich human-readable snapshot
```

## Demo

Host identity resolution and live metrics in four lines (see
[Quick Start](#quick-start) above):

```mermaid
flowchart LR
    env["$SCITEX_RESOURCE_HOST"] --> resolve["resolve canonical name"]
    proj["./.scitex/resource/config.yaml"] --> resolve
    home["~/.scitex/resource/config.yaml"] --> resolve
    host["socket.gethostname()"] --> resolve
    resolve --> name["get_host_name() → 'mba'"]
    resolve --> cfg["get_host_config()"]
    psutil["psutil"] --> metrics["get_metrics()"]
    metrics --> snapshot[("cpu / mem / disk / gpu / load")]
    psutil --> log["log_processor_usages(limit_min=30)"]
    log --> csv[("~/.scitex/resource/runtime/processor_usages.csv")]
```

<p align="center"><sub><b>Figure 1.</b> Host-identity resolution cascade and the metrics pipeline: psutil feeds one-shot snapshots and the continuous CSV logger.</sub></p>

## Installation

```bash
uv pip install "scitex-resource[all]"
```

Requires Python >= 3.9.

<details>
<summary><b>Per-module extras</b></summary>

<br>

| Extra | Pulls in |
|---|---|
| `all` | `sh` + `cli` + `dev` + `docs` (recommended) |
| `sh` | scitex-sh (shell helpers) |
| `cli` | ruamel.yaml (CLI machine-config round-trip) |
| `dev` | pytest, pytest-cov, ruff (contributors) |
| `docs` | Sphinx + RTD theme + myst-parser (docs build only) |

```bash
uv pip install -e ".[dev]"   # editable install for contributors
```

</details>

## Architecture

```mermaid
flowchart TD
    pkg["scitex_resource"]
    pkg --> core["core<br/>_host, _machine,<br/>_runtime, limit_ram"]
    pkg --> collect["collection<br/>_utils, _specs,<br/>_log_processor_usages"]
    pkg --> cli["interfaces<br/>_cli, _mcp"]
    pkg --> compat["_compat<br/>vendored str / gen helpers"]
    collect --> csv[("processor_usages.csv")]
    core --> cfg[("host config.yaml")]
```

<p align="center"><sub><b>Figure 2.</b> Package layout: core identity primitives, psutil-backed collection, and the CLI / MCP interfaces over a dependency-free compat layer.</sub></p>

## 1 Interfaces

<details open>
<summary><strong>Python API</strong></summary>

<br>

```python
import scitex_resource as r

# Hub-friendly metrics (cross-platform via psutil)
metrics = r.get_metrics()

# Canonical host identity
name = r.get_host_name()
cfg = r.get_host_config()        # {"canonical_name", "aliases", "role", "hpc": {...}}

# Rich snapshot
specs = r.get_specs()

# CPU/RAM/GPU/VRAM samples + continuous CSV logging
usage = r.get_processor_usages()
r.log_processor_usages(limit_min=30, interval_s=1)
# default: ~/.scitex/resource/runtime/processor_usages.csv

# Cap process RAM
r.limit_ram(0.5)
```

</details>

<details>
<summary><strong>CLI</strong></summary>

<br>

```bash
# Host identity
$ scitex-resource hosts show
$ scitex-resource hosts config show --json

# System specs and live metrics
$ scitex-resource specs
$ scitex-resource metrics show --json

# Processor usage snapshot + continuous CSV log
$ scitex-resource processor-usages show --json
$ scitex-resource processor-usages log --interval 5 --max-rows 12

# Cap process RAM
$ scitex-resource ram-limit 0.8
```

</details>

## Host identity config — `~/.scitex/resource/config.yaml`

```yaml
host:
  canonical_name: mba                 # what every scitex-* package uses to refer to this host
  aliases:                            # optional; cross-package discovery / drift detection
    - Yusukes-MacBook-Air
    - Yusukes-MacBook-Air.local
  role: head                          # generic role tag (head, worker, hpc-login, ...)
  hpc:                                # optional; HPC-only
    cluster: spartan
    login_only: true
    partitions: [physical, sapphire]
```

Resolution cascade (highest precedence first):

1. `$SCITEX_RESOURCE_HOST`
2. `<project>/.scitex/resource/config.yaml` `host.canonical_name`
3. `~/.scitex/resource/config.yaml` `host.canonical_name`
4. `socket.gethostname().split(".", 1)[0]`

(Deprecated `$SCITEX_RESOURCE_MACHINE` and `machine:` config block are
still honoured as fallbacks with a one-time ``DeprecationWarning``.)

## Status

Standalone fork of `scitex.resource`. Deps: pandas, psutil, PyYAML, click.

Decoupling notes:
- `scitex.str.readable_bytes` / `scitex.gen.fmt_size` / `scitex.str.printc` →
  vendored as small helpers in `_compat.py`.
- `scitex.io._load.load` / `scitex.io._save.save` → use `pandas.read_csv` /
  `to_csv` directly for the CSV log files.
- `scitex.sh.sh` → prefer `scitex_sh` if installed, fall back to plain
  `subprocess.run` (list-only).

The umbrella package's `scitex.resource` import path is preserved via a
`sys.modules`-alias bridge.

## Part of SciTeX

`scitex-resource` is part of [**SciTeX**](https://scitex.ai). Install via
the umbrella with `pip install scitex[resource]` to use as
`scitex.resource` (Python) or `scitex resource ...` (CLI).

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

## License

AGPL-3.0-only (see [LICENSE](./LICENSE)).

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>
