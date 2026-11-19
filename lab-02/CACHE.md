# Cache — cold vs warm

Two caches in `publish-lab-02.yml`:

- **pip** — `actions/setup-python` with `cache: pip`, keyed on a hash of `lab-02/requirements*.txt`.
- **Docker layers** — buildx `cache-from: type=gha` / `cache-to: type=gha,mode=max`, so the build stage is cached too.

| step | cold (run 44492692596, first ever) | warm (run 44492988657, next push) |
|---|---|---|
| `docker build` (Build step) | 48 s | 10 s |
| `pip install` in the test job | 5 s | 3 s |
| setup-python (restores the pip cache) | 5 s | 3 s |

The `docker build` got faster: with the gha layer cache, `pip install` inside the image and the venv copy were
`CACHED` instead of re-run, and only the layers after the changed workflow inputs were rebuilt.
