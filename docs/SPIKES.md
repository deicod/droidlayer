# Falsifiable architecture spikes

All spikes are **Not run** as of 2026-09-05. Source inspection and local capability
queries in [RESEARCH.md](RESEARCH.md) are not spike passes. Spikes may use small
disposable programs; do not build production abstractions until their question
is answered. Preserve results even when the answer is negative.

For each run, create `docs/results/SPIKE-NNN-YYYY-MM-DD.md` containing: question,
exact source/image/driver/tool revisions, relevant ADR, commands, configuration,
test artifact hashes, observations, evidence links, result (pass/fail/inconclusive),
limitations, and next decision. Redact host identifiers and secrets. Record CPU
copies separately from GPU composition passes. A debug screenshot proves visible
content only, not zero-copy or acceleration.

The dependency graph is deliberately staged: host-only graphics checks can run
before AOSP; task/output checks require a booted image. M0 does not require
completing every spike before starting M1. See the task references below.

## SPIKE-001

**Question:** Can a small helper provision private Binder and a minimally
privileged Android container, with an unprivileged controlling daemon?

- Dependencies: local inventory; explicit security-profile decision from
  SPIKE-010's design stage for the Android phase; M2 image for boot. Binder
  isolation can be tested first. Full Android security proof comes after boot.
- Method: construct two fresh binderfs mounts and context managers in isolated
  test namespaces; allocate nodes through `BINDER_CTL_ADD`; test transactions,
  FD passing and inability to resolve the other instance's services. Repeat with
  C/Rust Binder where hardware/kernel access permits. Test feature-file paths,
  device cgroup denies, subordinate-ID ownership and cleanup after killed setup.
- Android phase: start the prepared init under LXC, record all failing operations
  and capabilities, verify shared kernel/container PID 1 and distinct namespaces.
  Audit UID/GID coverage rather than assuming a standard 65,536-ID map suffices.
- Pass: no global Binder dependency; no cross-instance service visibility; helper
  setup/recovery is bounded; daemon has no capabilities or root operations;
  data/mount/device cleanup survives injected failures.
- Falsifier: required boot operations cannot be mediated without exposing global
  host policy/devices, or UID mappings break fundamental per-app isolation.
- Output: mount/device/capability contract and boot-gap report. Update ADR-0003,
  0004, 0011. Tasks M0.3 and M3.1–M3.5.

## SPIKE-002

**Question:** Which AOSP17 boundary gives one complete task output with manageable
patches and correct Android behavior?

- Dependencies: M4 healthy userdebug image under an approved security profile;
  deterministic test APK from M5.1. A temporary output viewer suffices.
- Method, first session: instrument a listener within the product's existing
  ShellTaskOrganizer; capture initial task snapshot, appeared/vanished/info deltas,
  root/leaf roles, display IDs and transition/reconnect ordering. Do not register
  a rival organizer without characterizing displaced Shell behavior.
- Method, second session: create a trusted own-content virtual display with a
  Surface sink; launch/move one task there. Exercise two activities in one task,
  two tasks of one package, a cross-app task launch and existing-task reuse.
  Prove how newly created tasks are assigned to outputs without migration loops.
- Method, third session: compare common-display task mirroring/cropping (A2).
  Inspect whether D1 needs a narrow SF composition entry point if A1/A2 fail.
  Record methods, flags and patch paths; identify which Android17 virtual-display
  implementation is active. Do not use repeated captureLayers as the final path.
- Acceptance matrix: resize/density/orientation, non-resizable app, SurfaceView,
  dialogs/popups, dimming, IME and permission dialog, hide/show, back navigation,
  process death, task disappearance and secure-layer exclusion. Record each result.
- Pass: complete output/metadata/input-space definition for a task with explicit
  exceptions; no layer-name parsing; no permanent screenshots; small reviewable
  patch inventory. Two tasks do not leak pixels or input to each other.
- Falsifier: required surfaces cannot be included safely, tasks cannot remain
  independently configured, or maintaining a private compositor is necessary.
- Output: A1/A2/C/D1 comparison with measured cost, compatibility and proposed
  accepted boundary. Update ADR-0007/0010. Tasks M6.1–M6.3; larger multi-task
  compatibility remains M10 rather than being claimed from a simple test.

## SPIKE-003

**Question:** Can the chosen Android output allocation and fences cross into a
host process with no CPU pixel copy and correct lifetime?

- Dependencies: SPIKE-002 output sink; native Android Mesa provider or a renderer
  candidate. A synthetic host allocator/consumer pair can validate IPC first.
- Method: consume one SF output using Android GraphicBuffer/BufferQueue APIs;
  obtain allocator-defined plane metadata; pass duplicated dma-buf and acquire
  sync_file FDs; import on the host; return a release dependency to BufferQueue.
  Use a bounded reusable pool and changing frame IDs embedded in the image.
- Tests: delayed acquire, delayed release, shared FD planes, modifier rejection,
  resize generations, disconnection with frames in flight, repeated reuse and
  close-on-exec. Trace allocation IDs and FD counts to detect reuse/leaks.
- Pass: matching pixels and frame ordering across at least 10,000 frames; no CPU
  readback in the accelerated path; memory/FD use plateaus; blocked consumers do
  not deadlock system_server or SF. Report GPU passes independently.
- Falsifier: output handles cannot be described/imported portably, allocator
  metadata is unavailable, or required fence semantics cannot be preserved.
- Output: first buffer/fence protocol and allocator provider requirements;
  update ADR-0010/0012. Tasks M6.4–M6.5 and M8.1–M8.3.

## SPIKE-004

**Question:** Can an imported GPU image appear in a normal X11 window on the
current RTX-driven Xorg server, and what copies/synchronization are needed?

- Dependencies: host-only synthetic Vulkan/GBM producer initially; SPIKE-003 for
  real Android output. Does not require AOSP to start.
- Method: create two normal XCB top-levels with WM properties; import a described
  image; compare Vulkan/EGL sampling into a native X11 swapchain against DRI3
  PixmapFromBuffers + Present where supported. Query actual server versions and
  modifiers; test syncobj Present only when advertised. Log EGL external-only
  results; a GL_TEXTURE_2D assumption must not silently reject valid samplers.
- Pass: independent WM move/resize/minimize/fullscreen/Alt+Tab/close behavior;
  no CPU copies in the accelerated candidate; delayed producer fences never
  show unfinished frames; source buffers are not reused before real release.
- Falsifier: no accelerated importer can display the selected output or native
  top-level lifecycle cannot be reconciled with Android output generations.
- Output: preferred X11 presentation path and optional fast-path capabilities;
  update ADR-0008/0010. Tasks M0.5, M7.1–M7.4, M8.3.

## SPIKE-005

**Question:** Can AOSP17 render GLES and Vulkan on the RTX 4070 while the current
Xorg/NVIDIA driver stack remains in use?

- Dependencies: host Vulkan allocation/import audit first; pinned Mesa/Venus,
  virglrenderer and ANGLE candidates, selected guest allocator/mapper, M4 image
  for Android phase. Keep the renderer independent of desktop backends.
- Phase A: host-create/export/import RGB images across processes; query compatible
  image formats, modifiers, memory types, DMA_BUF vs OPAQUE_FD, sync_file imports
  and exports. Test both producer and presentation roles and actual device IDs.
- Phase B: inspect/upstream-audit the current experimental vtest/AHB/fence work;
  pin all source revisions/licenses; prove a Bionic Venus client to an isolated
  host Vulkan renderer over a Unix transport with no VM/virtio PCI prerequisite.
- Phase C: integrate allocator requests and mapper metadata; run the test APK's
  Vulkan then ANGLE GLES paths and SF composition. Verify synchronization and
  report supported texture formats/features without fabricating Android guarantees.
- Pass: real app rendering on RTX through NVIDIA userspace; no mandatory CPU
  rendering/readback; correct 10,000-frame stress and resize/restart; exact patch
  set and worker sandbox documented. Open/proprietary kernel-module results are
  separate matrix rows; do not assume interchangeability.
- Falsifier: essential Android memory/fence contracts cannot be supported without
  large unmaintainable forks or unsafe privileged renderer access.
- Output: go/no-go for forwarded provider, upstream delta and maintenance estimate;
  update ADR-0013/0015. Tasks M0.5–M0.6 and M8.4–M8.7.

## SPIKE-006

**Question:** Can native window input and resize/focus reach exactly the intended
Android task without host input-device exposure?

- Dependencies: M7 basic window; SPIKE-002 display/task mapping.
- Method: translate X11 events with a recorded inverse geometry transform and
  inject through an Android platform service, with task/display generation,
  focus serial, timestamps and permitted target UID. Repeat the generic protocol
  using Wayland events when available.
- Pass: test APK reports correct coordinates under resize/rotation/letterboxing,
  keyboard/button/scroll state, no stuck keys on focus loss, and no events to a
  background task after focus changes. Basic text/IME path is observable.
- Falsifier: Android routing cannot enforce focus/task ownership or requires raw
  host input devices. Output: transform/event contract and limitations; M7.5/M9.

## SPIKE-007

**Question:** Can the same described allocation and task model support a native
Wayland top-level under Weston nested in the current X11 session?

- Dependencies: install/pin stable Weston; synthetic host producer first;
  SPIKE-003 for Android. Inspect pinned wlroots backend/allocator separation for
  design lessons, without adopting it as a client dependency.
- Method: negotiate xdg-shell, linux-dmabuf feedback and available sync protocols;
  handle configure/ack, frame pacing and release ownership. Run two top-levels
  with scale changes, close/focus/resize and delayed fences; record Weston renderer.
- Pass: two Wayland top-levels work with the same core/buffer contract; GPU import
  works on the selected renderer without software fallback; unsupported protocols
  produce explicit downgrade/refusal. Protocol-only software runs count separately.
- Falsifier: core types encode X11 concepts or Android output cannot match the
  compositor's allocation/sync requirements. Output: protocol/version capability
  matrix; update ADR-0009/0010. Tasks M0.7 and M11.

## SPIKE-008

**Question:** Can Intel-rendered Android content be displayed on an RTX-driven
desktop, and can future DRM presentation use the same descriptor contract?

- Dependencies: P530 actually enumerates and Mesa Vulkan/GLES drivers are installed;
  access to selected render nodes. No monitor switch needed for import tests.
- Method: enumerate render/export/display device identities; test Intel→NVIDIA
  and, separately, NVIDIA→Intel with intersection of format/modifier capabilities.
  Compare direct import, GPU conversion and explicit rejection. Test VKMS metadata/
  page-flip behavior separately from physical KMS.
- Pass: recorded path for each required direction with copies, fences and
  limitations; no device-number heuristics. Physical scanout is a later test on
  an unused device or an explicitly scheduled VT/lease.
- Falsifier: no practical accelerated sharing path for the reference pairing.
  Output: compatibility matrix, not a universal PRIME claim; M8.8 and M17.

## SPIKE-009

**Question:** What exact AOSP17 product/HAL/init changes are necessary for a
container image, and can they be rebuilt reproducibly?

- Dependencies: stable manifest inventory; adequate build disk/RAM; source access.
- Method: verify `aosp_64bitonly_x86_64-cp2a-userdebug` configuration; resolve all
  repository revisions; generate product/VINTF/service closure; identify existing
  implementations for mandatory HALs. Record each VM/mobile dependency and proposed
  replacement/omission. Create a minimal DroidLayer product only after this audit.
- Build comparison: two clean output directories with recorded environment;
  compare images and unpacked metadata; audit signing/timestamps/AVB/APEX. Record
  incomplete reproducibility rather than redefining the acceptance condition.
- Pass: buildable source recipe, exact required partitions/HALs, known module
  rebuild steps, patch inventory and reproducibility evidence. Boot is a separate
  SPIKE-001/ M4 result.
- Falsifier: essential components require unavailable proprietary mobile blobs
  or cannot be configured without unacceptable platform divergence.
- Output: resolved manifest, build recipe and Android adaptation budget;
  update ADR-0002/0003/0015. Tasks M2 and M4.1.

## SPIKE-010

**Question:** Can Android per-app SELinux enforcement coexist with host policy
and LXC user namespaces while sharing the host kernel?

- Dependencies: read-only kernel/AOSP/host policy audit first; any policy-changing
  test requires a dedicated approved test environment, never an automatic policy
  load on the developer desktop. Profile selection/preparation precedes M3 boot;
  full per-app enforcement tests require M4 services and M5 test apps.
- Method: enumerate Android init policy-loading assumptions, Binder labels,
  service/seapp contexts, file labels, subordinate-UID mapping and host domains.
  Design a host-owned integrated policy and an init handoff that prevents guest
  policy mutation. Assess coexistence with host LSM configuration and packaging.
- Validate on a suitable isolated test host: Android app domains enforced;
  denied cross-app file/Binder operations; host processes unaffected; guest cannot
  load policy/change enforcing mode or relabel arbitrary host resources.
- Pass: working enforcing profile with explicit host requirements, recoverable
  installation steps and user-namespace implications. If only policy design is
  possible, result is inconclusive rather than passed.
- Falsifier: required per-app semantics or host isolation cannot coexist.
  Document the smallest requirement change. A trusted-APK reduced-MAC profile
  remains a project decision; do not quietly implement it to obtain a boot.
- Output: ADR-0014 profile decision/gate for Android boot tasks at M0.4/M3.4;
  full enforcement result at M15.2. A profile decision is not a spike pass.
