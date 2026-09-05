# ADR-0007: Android task maps to one host top-level

Status: **Proposed**

Date: 2026-09-05

## Context

A Task groups an application's navigation context, while individual activities/surfaces should usually remain inside it. A task leash does not expose composed pixels.

## Decision

Keep Task→top-level as policy. Integrate with the existing Shell organizer for initial snapshot and task events. Prototype A1: one trusted virtual display/composed sink per application task, using launch/reparent/bounds coordination. Compare A2 mirroring on a common freeform display and D1 targeted SF composition. Root organizer tasks must not become application windows.

## Alternatives and consequences

Secondary displays do not automatically enforce one task each. Dialogs, IME, overlays, existing-task reuse, cross-app launches, secure content and focus/configuration changes are acceptance gates. Do not parse layer names or use package name as identity. If A1 fails, revise this ADR before assuming buffer or input routing semantics.

## Evidence and validation

[A04–A07, R02](../SOURCES.md); [SPIKE-002](../SPIKES.md#spike-002), [SPIKE-006](../SPIKES.md#spike-006). Accept a specific output mechanism only after its matrix passes; mapping policy and mechanism can have different outcomes.
