# ADS Web Tools (sandbox)

Stand-in for pi-web-tools, used to rehearse the GitHub Actions pipeline. It contains no IDEXX code.
The **Build and deploy** section below is written so it can be copied into the real pi-web-tools readme.

---

## Build and deploy

PIT is built and deployed with **GitHub Actions**. The Jenkins jobs are being retired.

### Build (automatic)

`pi-web-tools build` runs on every pull request and every push to `master`:

1. Compiles with JDK 11 (`javac release="8"` → Java 8 bytecode) and runs `ant war-tc7`.
2. Guardrails fail the build if any class is newer than Java 8, and flag a bundled `ojdbc*.jar`.
3. On `master`, publishes an **immutable** build to S3 as `gha<run>-<commit>`, e.g. `gha42-1a2b3c4`, with a SHA-256 checksum.

The version appears in the run summary. That's the value you deploy.

### Deploy (push-button)

Actions → **pi-web-tools deploy** → Run workflow:

| Input | Choose |
|---|---|
| environment | `dev`, `qa` or `prod` |
| action | `verify`: dry run, checks the build on the server and changes nothing<br>`deploy`: back up the current version, install, restart, health check, **automatic rollback if unhealthy**<br>`rollback`: restore the previous version<br>`restart`: restart Tomcat and health-check it |
| version | e.g. `gha42-1a2b3c4` (needed for verify/deploy) |

**Rules**
- Promote the **same version** through dev, then QA, then prod.
- **prod** needs approval from a reviewer (not the person who started the run), only runs from `master`, and only accepts builds made from `master`.
- One deploy per environment at a time.
- Server database settings (`conf/context.xml`) are never touched by the pipeline.

### If something goes wrong

- A failed health check rolls back automatically; the run is red and says so.
- To go back manually, run `rollback` on that environment.
- Each run's **Run on host via SSM** step shows the server-side log. The server also keeps `/var/lib/pit-deploy/history.log`.

### Access and security

No SSH keys or stored AWS credentials. Each environment has its own short-lived AWS role (via OIDC) that can only reach that environment's servers, and can only run the approved deploy script.
