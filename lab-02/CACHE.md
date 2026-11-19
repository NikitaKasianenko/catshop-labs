# Cache — cold vs warm

Two caches in `publish-lab-02.yml`:

- **pip** — `actions/setup-python` with `cache: pip`, keyed on a hash of `lab-02/requirements*.txt`.
- **Docker layers** — buildx `cache-from: type=gha` / `cache-to: type=gha,mode=max`, so the build stage is cached too.

| step | cold (run 44492692596, first ever) | warm (run 44492988657, next push) |
|---|---|---|
| `docker build` (Build step) | 48 s | 10 s |
| `pip install` in the test job | 5 s | 3 s |
| setup-python (restores the pip cache) | 5 s | 3 s |

The `docker build` got faster: on the warm run every step — `useradd`, `python -m venv`, `COPY requirements.txt`,
`pip install` — came back `CACHED` from the gha layer cache, so the 48 s cold build was mostly the base-image pull
and the in-image `pip install`, and the warm one only had to export layers.
