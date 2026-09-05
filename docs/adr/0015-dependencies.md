# ADR-0015: Small reviewed dependency set introduced at point of use

Status: **Proposed**

Date: 2026-09-05

## Context

Low-level ownership and maintained interfaces matter more than convenient APIs or a long initial dependency list.

## Decision

Use the dated shortlist in DEPENDENCIES.md, then audit actual APIs/transitives/licenses/advisories at introduction. Prefer rustix, tracing, clap and explicit serde control schemas for early host code; choose one event-loop owner per connection. x11rb/Wayland clients, ash/drm and zbus are candidates for their milestones. Pin reviewed versions in Cargo.lock.

## Alternatives and consequences

gbm, khronos-egl and ash have older releases with different upstream activity; recency alone is not a quality verdict. lxc-rs needs LXC7 ABI review. Initially use fixed-argument LXC tools; a tiny dynamic FFI shim is justified if lifecycle requirements demand it. No Binder userspace stack or compositor framework without a specific need.

## Evidence and validation

[DEPENDENCIES.md](../DEPENDENCIES.md), [L01](../SOURCES.md). Each introduction task records API/safety findings and tests. M1 accepts only the foundation subset; graphics/provider dependencies remain proposed until their spikes.
