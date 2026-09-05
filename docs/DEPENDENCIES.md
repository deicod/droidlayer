# Host dependency review

Observed 2026-09-05 from the crates.io API (`/api/v1/crates/<name>`) and upstream
repository APIs. These are candidates, **not an installed dependency set**.
No Cargo workspace/lockfile exists. Recheck advisories, licenses, native-library
ABIs and target toolchain at the task that first introduces a dependency.

| Category / candidate | Stable release observed; date | License metadata | Assessment |
|---|---|---|---|
| [x11rb](https://crates.io/crates/x11rb) | 0.14.0; 2026-07-16 | MIT OR Apache-2.0 | Preferred X11 candidate; XCB FFI connection can support native WSI, with unsafe pointer lifetime isolated. Inspect extension coverage. |
| [xcb](https://crates.io/crates/xcb) | 1.7.1; 2026-08-09 | MIT | Maintained direct libxcb alternative if x11rb integration is awkward; do not use both casually. |
| [wayland-client](https://crates.io/crates/wayland-client) | 0.31.15; 2026-07-22 | MIT | Preferred protocol client; choose native backend for WSI where needed. |
| [wayland-protocols](https://crates.io/crates/wayland-protocols) | 0.32.13; 2026-06-19 | MIT | Enable only required client/staging protocols; confirm syncobj bindings and runtime versions. |
| [smithay-client-toolkit](https://crates.io/crates/smithay-client-toolkit) | 0.21.1; 2026-07-23 | MIT | Evaluate for seat/output/shell helpers; direct protocol use is sufficient for small spikes. Not the Smithay compositor framework. |
| [drm](https://crates.io/crates/drm) | 0.15.0; 2026-03-19 | MIT | Candidate safe DRM wrapper; isolate missing syncobj ioctls rather than bypassing ownership globally. |
| [gbm](https://crates.io/crates/gbm) | 0.18.0; 2024-12-03 | MIT | Slow release cadence, upstream activity 2025. Audit modifier/plane APIs and pointer/FD lifetimes; no assumption of NVIDIA allocation coverage. |
| [khronos-egl](https://crates.io/crates/khronos-egl) | 6.0.0; 2023-10-05 | MIT/Apache-2.0 | Stable-looking API but stale release/commit history. Defer selection; assess dynamic extension loading and maintained alternatives before EGL code. |
| [ash](https://crates.io/crates/ash) | 0.38.0+1.3.281; 2024-04-01 | MIT OR Apache-2.0 | Vulkan candidate; repository active in 2026 despite old release. Check needed extensions in released bindings; do not assume Vulkan1.4 completeness. |
| [rustix](https://crates.io/crates/rustix) | 1.1.4; 2026-02-22 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT | Preferred Unix FD/syscall layer, using OwnedFd/BorrowedFd. Enable bounded feature set. |
| [nix](https://crates.io/crates/nix) | 0.31.3; 2026-05-11 | MIT | Credible alternative for socket/control APIs; avoid overlapping Unix wrapper layers unless a concrete gap exists. |
| [lxc](https://crates.io/crates/lxc) | 0.8.0; 2024-04-07 | MIT | Upstream active June 2026, but release predates LXC7. Needs ABI/safety audit; not selected merely because it exists. `liblxc` crate lookup returned 404. |
| [zbus](https://crates.io/crates/zbus) | 5.19.0; 2026-08-09 | MIT | Preferred host D-Bus candidate for helper authorization/systemd/portals. MSRV observed 1.87; scope features. |
| [libsystemd](https://crates.io/crates/libsystemd) | 0.7.2; 2025-04-30 | MIT/Apache-2.0 | Candidate pure Rust service/notify helpers; assess whether small required surface is already covered. No requirement to link all libsystemd. |
| [serde](https://crates.io/crates/serde) / [serde_json](https://crates.io/crates/serde_json) | 1.0.229 / 1.0.151; July 2026 | MIT OR Apache-2.0 | Control/config candidates, with explicit protocol limits and schema/version rules; no Rust enum serialization as an implicit wire specification. |
| [tracing](https://crates.io/crates/tracing) | 0.1.44; 2025-12-18 | MIT | Structured events from first host task; field redaction and stable event IDs. |
| [clap](https://crates.io/crates/clap) | 4.6.6; 2026-08-06 | MIT OR Apache-2.0 | CLI candidate; bounded parsing is more valuable than custom parser code. |
| [tokio](https://crates.io/crates/tokio) | 1.53.1; 2026-07-20 | MIT | Candidate daemon/control runtime. Do not block it with Binder/GPU waits or LXC subprocesses. |
| [calloop](https://crates.io/crates/calloop) | 0.14.4; 2026-02-13 | MIT | Alternative session event loop aligned with Wayland tooling. Pick one owner per connection, not competing runtimes over the same FD. |
| [pipewire](https://crates.io/crates/pipewire) | 0.10.1; 2026-08-19 | MIT | Later media integration candidate; C library/SPA bindings and thread lifetime need a separate audit. |

Repository activity cross-checks (all non-archived when queried):

| Upstream | Latest observed commit | Commit date |
|---|---|---|
| [psychon/x11rb](https://github.com/psychon/x11rb) | `e4ba6cfec99bfda8ff25ea8051d3cc14c1a36ee9` | 2026-08-19 |
| [rust-x-bindings/rust-xcb](https://github.com/rust-x-bindings/rust-xcb) | `ad8cd4c07a769148a16ddec509f5f341f5058f00` | 2026-08-09 |
| [smithay/wayland-rs](https://github.com/smithay/wayland-rs) | `0813584ea50379bd22e95dc1e0b50f02a4b36ca2` | 2026-08-25 |
| [smithay/client-toolkit](https://github.com/smithay/client-toolkit) | `e97622a8796cd2ab4f4105ab89584f2ace1f5a40` | 2026-09-04 |
| [Smithay/drm-rs](https://github.com/Smithay/drm-rs) | `806a0db38db2c0d551f42bd34375693bf09f32f7` | 2026-04-20 |
| [Smithay/gbm.rs](https://github.com/Smithay/gbm.rs) | `54a6449bed83f942a78e83e2510b62ac08fbd268` | 2025-06-05 |
| [khronos-egl](https://github.com/timothee-haudebourg/khronos-egl) | `5605af04fb91ca3e5cc314ac374d21c452bb6855` | 2023-10-05 |
| [ash-rs/ash](https://github.com/ash-rs/ash) | `f4c2ca3e4f6b998d5254ad101a32f024d87cdec2` | 2026-07-27 |
| [bytecodealliance/rustix](https://github.com/bytecodealliance/rustix) | `9640071aef0dfd65d21bf01c1dd1baa0a1b13310` | 2026-08-25 |
| [sanpii/lxc-rs](https://github.com/sanpii/lxc-rs) | `342cb842416b2658aa910f8bdde0e684d4c4f1a6` | 2026-06-22 |
| [z-galaxy/zbus](https://github.com/z-galaxy/zbus) | `e10679486a42763e7478f11f2646acad6cbd4d9d` | 2026-09-04 |
| [lucab/libsystemd-rs](https://github.com/lucab/libsystemd-rs) | `a098728395d1518c18df6985d708f7406c6e3345` | 2026-06-03 |
| [tokio-rs/tokio](https://github.com/tokio-rs/tokio) | `060cc4e46aedc40b0a44dcbc31deb0df39abdb4e` | 2026-09-05 |

Recency is evidence of activity, not a safety assessment. The later introduction
task must inspect the exact APIs, unsafe implementation boundaries, open relevant
issues, transitive graph, native dependencies and advisory state. Lock reviewed
releases; a Git revision is a fallback requiring justification and a removal plan.

For LXC initially prefer fixed-argument lifecycle tools behind the helper, using
documented state/exit codes and helper-owned configs. This avoids prematurely
selecting a binding with an unverified LXC7 ABI. If structured lifecycle/events
require FFI, use a tiny audited dynamic liblxc shim or audited wrapper, with
LGPL notices/replaceability handled. Shell command concatenation and user hooks
are forbidden helper interfaces. [L01](SOURCES.md)

Rust host code does not need gbinder/rsbinder, a compositor framework, wgpu,
emulator code, or Go by default. wgpu is not selected for this boundary because
external allocation/modifier/fence interop needs explicit low-level API control;
that is a scope choice, not a claim that wgpu can never interoperate.

See [ADR-0015](adr/0015-dependencies.md). Dependency selection remains provisional
until its small integration test passes; these versions are not compatibility
promises or a reason to install the whole list at M1.
