# ADR-0013: NVIDIA rendering provider is an early feasibility gate

Status: **Proposed**

Date: 2026-09-05

## Context

NVIDIA host GBM/Vulkan support does not provide a Bionic Android driver. The existing Xorg desktop must remain usable.

## Decision

Prioritize a no-VM Venus Unix transport to a sandboxed host Vulkan renderer, GLES through ANGLE, and coordinated host allocation/guest mapper support. Audit current experimental work and upstream delta without copying GPL integration code. Start host-only allocation/fence tests before waiting for a full Android build.

## Alternatives and consequences

Intel→NVIDIA offload is useful but does not prove RTX guest rendering. NVK/Nouveau is a separate supported-hardware investigation, not an automatic replacement for nvidia-open. Open and proprietary NVIDIA kernel modules share userspace needs but may differ in the tested dma-buf path; maintain separate results. The current experimental reference is not turnkey upstream Android17 support.

## Evidence and validation

[G06–G08, R01, R04](../SOURCES.md); [SPIKE-005](../SPIKES.md#spike-005), [SPIKE-008](../SPIKES.md#spike-008). Accept after real Android GLES/Vulkan output and bounded renderer/fence tests; record patch rebase cost and exact supported driver configuration.
