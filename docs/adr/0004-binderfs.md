# ADR-0004: Private Binder instances through binderfs

Status: **Accepted**

Date: 2026-09-05

## Context

Global Binder nodes can inadvertently join users/instances to the same Binder context.

## Decision

Allocate devices in one fresh binderfs mount per instance generation. The helper owns binder-control and exposes only required nodes and read-only feature information. Android sees conventional device paths backed by private devices. Use dynamic major/minor results for device policy. Support C or Rust host Binder by UAPI behavior, not implementation language.

## Alternatives and consequences

binder is mandatory; hwbinder/vndbinder remain conditional on VINTF and service closure. Bootstrap can expose all three privately, then remove unused ones based on evidence. No host Binder stack or out-of-tree driver by default. Mounts/FDs must be torn down after users exit; unlink alone is not complete cleanup.

## Evidence and validation

[K01–K02, A10](../SOURCES.md); [SPIKE-001](../SPIKES.md#spike-001) validates isolation, permissions, feature lookup and failure cleanup. Decision is accepted; implementation is absent.
