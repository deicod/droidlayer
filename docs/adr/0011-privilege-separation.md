# ADR-0011: Privileged setup separated from user/session services

Status: **Accepted**

Date: 2026-09-05

## Context

Rendering untrusted Android output in a root daemon would unnecessarily combine device/setup authority with complex parsers and graphics APIs.

## Decision

Use a narrow system helper, an unprivileged user daemon and an unprivileged session process. The helper owns container configuration, Binder/mount/network/device/cgroup setup and cleanup. Authenticate caller UID and authorize bounded operations; evaluate Polkit for local policy. Host display/desktop bus access belongs only to session code. GPU command forwarding uses separately sandboxed workers.

## Alternatives and consequences

The helper must reject arbitrary hooks/configuration/paths/commands and unsafe images. Namespace UID mappings, device cgroups, seccomp, Android permissions and host MAC are independent controls. Android SELinux is unresolved in ADR-0014. An unprivileged process using a render node still reaches a large kernel driver surface.

## Evidence and validation

[L01, K03–K05](../SOURCES.md); [SPIKE-001](../SPIKES.md#spike-001), [SPIKE-010](../SPIKES.md#spike-010). Boundary accepted; exact capability/LSM profile requires measured proof before production.
