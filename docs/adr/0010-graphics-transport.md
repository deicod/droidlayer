# ADR-0010: Composed outputs, dma-buf and explicit synchronization

Status: **Proposed**

Date: 2026-09-05

## Context

Efficient transport requires allocation layout and ownership, not only a buffer FD. One app task can contain multiple layers and effects.

## Decision

Retain SurfaceFlinger composition initially; export task-associated output through a guest consumer and allocator metadata adapter. Transfer explicit plane descriptors, fourcc/modifier, device identity, geometry/color metadata and sync_file acquire/release FDs. Adapt synchronization at host APIs. Use bounded generation-aware buffer pools and negotiated import capabilities.

## Alternatives and consequences

Native_handle/AHardwareBuffer is not a portable host wire format. No second consumer stealing app BufferQueue buffers. No permanent screenshots/CPU copies. Zero-copy transport does not mean zero composition. Direct layer export could save a pass but would enlarge protocol, host compositor and AOSP maintenance scope. Secure/protected buffers must be excluded.

## Evidence and validation

[A07–A09, K04, G02–G05](../SOURCES.md); [SPIKE-002](../SPIKES.md#spike-002), [SPIKE-003](../SPIKES.md#spike-003), [SPIKE-004](../SPIKES.md#spike-004), [SPIKE-007](../SPIKES.md#spike-007). Accept after lifetime/import/fence and complete-task tests.
