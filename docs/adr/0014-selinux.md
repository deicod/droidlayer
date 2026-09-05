# ADR-0014: Resolve shared-kernel SELinux before claiming Android sandbox parity

Status: **Proposed**

Date: 2026-09-05

## Context

Linux7.2 has global SELinux state, Android init loads policy, and the current Arch session has no active SELinux. LXC namespaces do not create an independent Android policy.

## Decision

Treat full Android MAC enforcement as a production feasibility gate. Investigate a host-owned integrated SELinux policy retaining Android per-app/service/Binder labels, subordinate UID semantics and guest inability to mutate policy. The smallest proposed requirement adjustment is a production host-policy prerequisite, with its portability cost made explicit.

## Alternatives and consequences

A trusted-test-APK reduced-MAC development profile is only an option for a later explicit decision; it is not the selected default or equivalent security. Never load Android policy over host policy, disable host LSMs, or describe permissive behavior as isolation. If integration fails, report the conflict with the shared-kernel mission; do not substitute a VM silently.

## Evidence and validation

[K03, A11, A13](../SOURCES.md); [SPIKE-010](../SPIKES.md#spike-010). M0.4 completes the read-only policy audit; any policy-changing test needs an appropriate test environment. Boot tasks depend on an explicit profile decision.
