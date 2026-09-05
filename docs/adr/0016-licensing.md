# ADR-0016: Recommend Apache-2.0 with explicit third-party provenance

Status: **Proposed**

Date: 2026-09-05

## Context

The project intends public collaboration, upstream AOSP contribution and native library interoperability; source reuse creates distinct obligations.

## Decision

Recommend Apache-2.0 for original host code and documentation because it provides patent terms and fits AOSP contributions. Retain upstream licenses for modifications, bindings, generated files and bundled components. Do not add a blanket project LICENSE until the maintainer adopts the recommendation.

## Alternatives and consequences

AOSP is mixed-license; Waydroid host is GPLv3 and individual hardware files differ. No GPL copying is authorized by reference study. LXC library LGPL-2.1-or-later and dynamic-link distribution obligations must be honored; Linux UAPI syscall exceptions are not permission to copy kernel internals. NVIDIA binary redistribution needs a separate audit. Apache-2.0 does not erase any upstream obligation.

## Evidence and validation

[A14, K08, L01, R01–R04](../SOURCES.md); M1.1 records adoption/provenance before code publication, M16 audits actual packages and source obligations. This record is a recommendation, not legal clearance or a current license grant.
