# ADR-0012: Separate rendering, allocation and presentation devices

Status: **Accepted**

Date: 2026-09-05

## Context

The guest driver and host display need not use the same GPU or libc. NVIDIA cannot be treated as merely another Mesa driver.

## Decision

Define a common descriptor/capability/ownership contract with distinct native-Mesa and forwarded-host rendering providers. Expose render, allocation and presentation device identities separately. Negotiate compatible format/modifier/usage/synchronization sets. Backend presenters import or perform a measured GPU conversion; device selection uses stable identity, not renderD numbering.

## Alternatives and consequences

No universal GBM layout, linear-buffer importability, implicit synchronization or cross-GPU PRIME guarantee. Keep safe wrappers around driver-specific FFI. Start with modules and concrete providers; no dynamic plugin framework. Protected/HDR/YUV paths require future explicit capabilities.

## Evidence and validation

[G04–G08, R04](../SOURCES.md); [SPIKE-003](../SPIKES.md#spike-003), [SPIKE-005](../SPIKES.md#spike-005), [SPIKE-008](../SPIKES.md#spike-008). Separation is accepted; providers are unimplemented and unverified.
