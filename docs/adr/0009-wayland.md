# ADR-0009: Native Wayland client backend with nested development

Status: **Accepted**

Date: 2026-09-05

## Context

Wayland must have parity without requiring the developer to replace their X11 session.

## Decision

DroidLayer is a Wayland client with one xdg_toplevel per task. Negotiate linux-dmabuf feedback, configure/ack, scale, decorations, input and synchronization capabilities. Develop protocol behavior under Weston with X11/headless backends; verify accelerated imports and another compositor separately.

## Alternatives and consequences

Do not make DroidLayer a general-purpose compositor or leak Wayland objects into container/task control. Compositor policy determines placement/activation; lack of a minimize notification is not task destruction. Direct DRM/KMS is a later backend. Buffer release depends on the negotiated synchronization protocol, not frame callbacks.

## Evidence and validation

[G03, G09](../SOURCES.md); [SPIKE-007](../SPIKES.md#spike-007), M11. Backend target accepted; Rust helpers and fallback sync/decorations remain prototype choices.
