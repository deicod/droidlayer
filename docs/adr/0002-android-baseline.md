# ADR-0002: Stable Android 17 baseline

Status: **Accepted**

Date: 2026-09-05

## Context

A reproducible release needs a concrete source baseline, not a rolling product label.

## Decision

Select android-17.0.0_r1, CP2A.260605.016, API 37, SPL 2026-06-05. Manifest tag object 7a9e46ba6ed424f922a3457f4964e67e0b966201 resolves to 5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f. Record a fully resolved manifest before building. Use a 64-bit-only x86_64 product; cp2a is the candidate release configuration to verify.

## Alternatives and consequences

Acceptance covers source selection only; no build/reproducibility result exists. The observed manifest refs contain one Android17 tag. Audit published security fixes separately and do not claim September patch coverage. Future stable/QPR source updates require a reviewed rebase, never automatic beta tracking.

## Evidence and validation

[A01–A03, A07](../SOURCES.md); [SPIKE-009](../SPIKES.md#spike-009), M2. Record actual product/release configuration and two-build comparison.
