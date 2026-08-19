# Production Incident: Deploys Silently No-Op Due to Lost Swarm Manager Quorum

**Date:** 2026-08-16
**Status:** Unresolved — needs direct SSH access to swarm manager nodes to confirm and recover

---

## Symptom

`hubsign.io` was showing the old 4-tier pricing layout (Personal / Individual $15 / Business $60 / Enterprise $200, no "Team" tier) instead of the new 5-tier layout (Free / Individual / Team / Business / Enterprise, with Enterprise as a full-width banner) that had already been merged to `main` and verified working on localhost.

This looked at first like the stale-image problem described in [PRODUCTION_INCIDENT.md](PRODUCTION_INCIDENT.md) (Build without Deploy, or a Cloudflare cache hit), but a Build **and** a Deploy had both been run in Komodo, and the symptom persisted. It also happened more than once: a code change would appear correct on localhost, get built and deployed, and production would still revert to the old layout.

---

## Investigation

1. **Ruled out the code.** `git status` showed `main` clean and up to date with `origin/main` at commit `ef5bb5d`. Both `main` and `new-layout-update` point to the identical commit on the remote — no branch mismatch. `landing/pricing.py` at that commit already contains the correct 5-tier fallback ladder.

2. **Ruled out Stripe as the cause.** In `landing/pricing.py`, the `team` and `enterprise` tiers are always sourced from the hardcoded fallback — never overwritten by live Stripe data (see the `TODO(pricing)` comment at line 95). A missing "Team" card cannot be explained by stale/live Stripe prices; only a stale *deployed image* explains it.

3. **Confirmed the build was correct.** Komodo's Build resource for `hubsign-landing` showed build `v1.0.13` (Aug 16, 17:09) was built from commit `ef5bb5d` — the exact commit with the fix — and pushed successfully to `172.16.15.51:5000/futureedge/hubsign-landing:1.0.13-latest`.

4. **Confirmed the deploy action reported success.** The Komodo procedure (`PullRepo` → `RunBuild` → `RunAction`) completed in 3.6s with no errors. The deploy action's own log showed:
   ```
   Deploying hubsign-landing image tag: 1.0.13-latest
   Variable hubsign_landing_image_tag updated to 1.0.13-latest
   DeployStack triggered for hubsign-landing
   Action completed successfully
   ```

5. **But the Stack Service itself showed `UNHEALTHY`, 1 replica desired, with no error logged anywhere in Komodo's UI.** Queried Komodo's API directly (`POST /read`) to dig further:
   - `GetStackLog` (`docker service logs`) returned **empty stdout/stderr with `success: true`** — not a crash trace, but proof no container ever produced any output at all.
   - `ListStackServices` confirmed `RunningTasks: 0, DesiredTasks: 1, CompletedTasks: 0, State: "Unhealthy"`.
   - `GetStack` showed the compose spec has a placement constraint: `node.labels.hubsign-landing == true`. Initially suspected as the cause, but `ListSwarmNodes` showed two manager nodes (`us-flint-1`, `us-flint-2`) both carrying that label and reporting `State: "ready"` — so a matching node does exist, at least per Komodo's last known state.
   - `ListSwarmTasks` returned 465 tasks swarm-wide, but **zero were ever created for the `hubsign-landing` service**, and **no task of any kind, for any service, had been created since ~20:27 UTC** — over two hours before the `hubsign-landing` service spec was last updated (22:52 UTC). The whole swarm had stopped scheduling anything.
   - A live pass-through call (`InspectSwarmService`) failed outright:
     ```
     Docker responded with status code 503: This node is not a swarm manager.
     Worker nodes can't be used to view or modify cluster state.
     Please run this command on a manager node or promote the current node to a manager.
     ```

---

## Root Cause (most likely — unconfirmed pending node access)

`production-swarm` has exactly **two** manager nodes (`us-flint-1` @ `172.16.15.51`, `us-flint-2` @ `172.16.15.52`) and one worker (`us-flint-registry`). Two managers gives **zero fault tolerance**: Raft quorum requires a strict majority, so if either manager goes down or becomes unreachable, the cluster loses quorum entirely and cannot schedule *any* new tasks, for *any* service, until quorum is restored.

Everything observed is consistent with quorum loss:
- Komodo can still write/read the desired service spec (this appears to go through even without quorum, or is served from Komodo's own cached state).
- Docker Swarm accepts the "deploy" call as a spec update but never actually reconciles it into a running task, because the scheduler can't make cluster-state decisions without quorum.
- No container is ever created → no logs, no crash trace, no error surfaced to Komodo's UI — it just looks like the deploy silently did nothing.
- The previous (older) container was never torn down, since Swarm never got as far as replacing it — explaining why production kept reverting to the old pricing layout instead of erroring out.

**This is not specific to `hubsign-landing`.** Any service on `production-swarm` needing a new task right now — a fresh deploy, or an existing container crashing and needing to be rescheduled — would silently fail the same way.

---

## What's Needed to Confirm and Fix

This cannot be diagnosed or fixed further through the Komodo API or UI — it requires direct access to the manager nodes:

1. SSH to `us-flint-1` (`172.16.15.51`) and `us-flint-2` (`172.16.15.52`).
2. On each, run `docker node ls` and `docker info` (check the `Swarm` section — `Is Manager`, `Managers`, `Nodes`, and any raft/quorum error state).
3. Determine whether one node is down, unreachable, or its Docker daemon has crashed, and whether the surviving node still holds leadership.
4. If one manager is confirmed lost and unrecoverable, `docker swarm init --force-new-cluster` on the surviving manager will recover quorum — **this is destructive to the raft log and should only be run deliberately, by someone with hands-on access, after confirming the other manager truly cannot be brought back.**

---

## Recommended Prevention

- **Move to 3 manager nodes** (or any odd number ≥ 3). A 2-manager swarm is strictly worse than a 1-manager swarm for availability — it has the operational overhead of a cluster with none of the fault tolerance. 3 managers tolerates the loss of 1 without losing quorum.
- **Add monitoring/alerting on manager quorum and node count** for `production-swarm`, so quorum loss is caught immediately rather than discovered indirectly through a "the website looks wrong" report.
- **Treat a Komodo "deploy succeeded" as necessary, not sufficient.** It only confirms the API call to update the service spec succeeded — not that a healthy task actually came up. Worth adding a post-deploy check (e.g. poll `RunningTasks == DesiredTasks` or hit `/api/health/` through the load balancer) before considering a deploy verified.

---

## Related: Credentials Exposed During This Investigation

While diagnosing this, live credentials were pasted into / returned within a chat session and should be rotated once the above is resolved:
- Komodo API key/secret pair
- Stripe restricted API key (`rk_live_...`) and webhook signing secret, which were visible in plaintext inside the deployed compose environment returned by Komodo's `GetStack` API call
- Django `SECRET_KEY` (same source)

None of the actual values are recorded in this file. Rotate in Komodo (Settings → API Keys), the Stripe dashboard, and Komodo's environment variables for `hubsign-landing` respectively.
