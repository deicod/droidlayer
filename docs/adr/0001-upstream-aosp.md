# ADR-0001: Upstream AOSP, independent product

Status: **Accepted**

Date: 2026-09-05

## Context

A real Android runtime is required, but inheriting another distribution's product and patch stack would make provenance and future releases harder to control.

## Decision

Use upstream AOSP with a DroidLayer product/vendor overlay and an individually documented patch series. Do not use LineageOS or a Waydroid image. Keep ART, Bionic and APK execution semantics upstream unless evidence requires a narrow change.

## Alternatives and consequences

A GSI is a build reference, not a complete container image. Waydroid/Anbox are references with per-file licensing constraints; no GPL implementation copying is authorized. Cuttlefish is a HAL/build reference and does not authorize a VM runtime.

## Evidence and validation

[A01–A03, R01–R03](../SOURCES.md); [SPIKE-009](../SPIKES.md#spike-009). M2 validates the product closure and updates this ADR if upstream components are insufficient.
