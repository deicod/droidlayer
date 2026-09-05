# Planning review and handoff

Reviewed 2026-09-05. Scope: documentation, source research and read-only local
inventory. No Android build/boot, runtime code, driver change, policy load or
graphics interoperability spike occurred.

## Outcome

The plan provides a credible investigation/implementation route, but it does not
establish feasibility of the full mission. In particular, stock Arch plus LXC
does not independently supply Android enforcing SELinux, and a host NVIDIA
Vulkan extension list does not supply an Android graphics driver.

The recommended direction is upstream AOSP17 + LXC + private binderfs + Rust
host services, with Android retaining task/window management and composition.
The proposed task-associated composed output and NVIDIA rendering provider remain
gated by explicit experiments. X11 native top-levels are the first visible proof;
Wayland is an equal interface with early nested tests.

## Critical review findings incorporated

| Finding | Resolution in the plan | Remaining evidence |
|---|---|---|
| “TaskOrganizer gives a task buffer” is false | Separate metadata/leash observation from composed output ownership; compare A1/A2/C/D1 | SPIKE-002/003. |
| A virtual display can contain multiple tasks | Explicit launch/reparent/reuse policy and root/leaf task tests | Multi-task, IME/system surfaces and transition matrix. |
| Legacy binder Kconfig checks would reject this host | Detect Rust Binder and actual binder filesystem/UAPI | Isolated provisioning/ioctl tests. |
| Full security proof cannot precede boot/app tests | Separate pre-boot profile decision/preparation from post-boot per-app enforcement proof | M3.4 preparation; M15.2 full proof. |
| NVIDIA would otherwise arrive too late | Host-only tests and renderer audit in M0; guest renderer tasks eligible before M7 | SPIKE-005 real AOSP17 graphics result. |
| Generic AOSP/GSI is not a container vendor image | Product/VINTF/HAL/init closure audit and specific replacement tasks | Actual image build, boot and reproducibility. |
| A complete composer/allocator implementation may exceed one session | M4.2 integrates audited references; absent references require new scoped HAL tasks first | M4.1 names actual module/API boundaries. |
| Requiring an unpublished stable release could stall all production work | Rehearse current patch application; explicitly defer cross-release proof if no later stable exists | A real stable rebase remains a separate maintenance risk. |
| Sandboxing a shared renderer does not isolate its clients | Credential-derived app/context identity and allocation ownership in graphics contract | Cross-app malicious-client tests. |
| A compositor frame callback is not permission to reuse a buffer | Explicit acquire/release dependencies and protocol-specific lifetime tests | Delayed-fence, disconnect and 10,000-frame stress. |
| Nested Weston could be mistaken for the final X11 backend | Separate native XCB acceptance from nested Wayland protocol tests | Real Xorg WM proof and native Wayland parity. |
| Supporting the reference P530 could be falsely reported | Inventory explicitly says not enumerated; hardware gates remain open | Device availability and actual driver tests. |

## Requirement coverage audit

| Requirement group | Where execution is specified |
|---|---|
| Stable upstream AOSP17, x86_64, persistent user instance | ADR-0001/0002, M2–M5. |
| Host kernel, LXC, private Binder, Android init/services | ADR-0003/0004, SPIKE-001/009/010, M3/M4. |
| Architecture alternatives and all 20 critical questions | RESEARCH.md sections 7 and 25, SPIKES.md. |
| Independent X11 task windows and basic input proof | SPIKE-002/004/006, M6/M7. |
| Acceleration, Vulkan/GLES, dma-buf/modifiers/fences, NVIDIA and multi-GPU | ADR-0010/0012/0013, M0.5/M0.6 and M8. |
| Keyboard layouts/shortcuts, pointer/capture/scroll, multiple tasks | M9/M10. |
| Equal Wayland backend and X11-based development | ADR-0009, M0.7/M11, DEVELOPMENT.md. |
| Audio output and microphone | M12. |
| Clipboard, notifications, .desktop entries and icons | M13. |
| File sharing/chooser/portals, URI/MIME intents, drag-and-drop, camera | M14. |
| Privileges/security, clean lifecycle, crash/suspend recovery and diagnostics | M1/M3, ADR-0011/0014, M15. |
| Layered tests and dedicated test APK | M5.1 and per-milestone test strategies; DEVELOPMENT.md. |
| Reproducibility, incremental Android/host builds and Arch packaging | M2/M4.6/M16, DEVELOPMENT.md. |
| Future standalone DRM/KMS, one monitor, no desktop migration | M17 and DEVELOPMENT.md. |
| License/dependency/provenance decisions | DEPENDENCIES.md, ADR-0015/0016, M1.1/M16.3. |

No ARM translation, Google services, integrity bypasses, phone emulation or
multi-distribution packaging task is on the critical path to the first window.

## Validation performed

- Offline documentation validation: local file/fragment links, task/spike/ADR
  references, unique checkboxes, milestone fields and planning-only checked-task
  guard. Re-run `python tools/check_docs.py` for the current counts.
- `git diff --check` for tracked changes; additional whitespace validation covers
  new documentation/tool files before handoff.
- All **85 distinct external URLs in SOURCES.md** returned HTTP 200 to a HEAD
  check on the review date. Availability does not certify source content or
  reproduce reported runtime behavior. Content was researched as described in
  the source register, not inferred from these HEAD responses.
- Rust tests/AOSP builds/Android instrumentation/GPU spikes: **not run**, because
  their implementation/artifacts do not exist. No runtime checkbox is checked.
- Mermaid syntax was reviewed as source; the lightweight checker does not render
  diagrams. No rendered-diagram validation result is claimed.

## Handoff

Execute **M0.3**, the read-only preflight probe, next. Start M1's small Rust
foundation after it, while the security-profile audit and host-only graphics
experiments reduce the largest uncertainties. Keep proposed ADRs proposed until
their recorded evidence justifies acceptance.

Largest feasibility conflict: preserving Android enforcing SELinux while sharing
an otherwise stock GNU/Linux desktop kernel. Largest graphics risk: complete,
independently configured task output without extensive SF/WM changes. Largest
NVIDIA risk: maintainable Bionic Venus/allocator/AHB/fence interoperability with
host proprietary userspace. Largest AOSP-maintenance risk: private Shell/WM/SF
and init/policy interfaces evolving together across stable releases.
