# Final deferred security and operational report

This report records verified evidence and explicit limits only. PMA accepts the functional repair/deployment; this is not a fresh security audit and authorizes no remediation or runtime change

## Security deferrals

| Item | Verified record and limit | Deferred owner decision |
| --- | --- | --- |
| Historical private tool output | TASK-2026-09-04-004 records the PO classification: sensitive values appeared in private local tool output, without recorded repetition, persistence, commit or external disclosure in that incident. This closure does not independently re-investigate it or assert a broader absence of compromise | Credential owners retain the recorded rotation recommendation; rotation was neither performed nor verified by this closure |
| Exact final-image audit/signatures | Earlier qualification/signing evidence covers source bf58974a935521fa570fa7e280c51a00b2e5b54e and its earlier image subjects. The final source 6ba4b3b366386e16364a6723c43319f4e52cc7a0 / digest 0c8009530d20ca8a5306f38ff4f6aecb6e3261ded0c5e7336237033b6557717c has clean-source build/identity and functional evidence, but no fresh complete SBOM/vulnerability/provenance/Cosign verification packet is claimed | Release/security owners may separately commission exact-final-subject audit and signature/attestation refresh. This is an evidence gap, not proof that signatures are absent or that a particular vulnerability exists |
| Release signing custody | TASK-2026-09-03-004 records a dedicated approved self-managed StaticDuo signer and protected private material outside repository/Syncthing; the later readiness review notes it is not hardware-backed | Key access, recovery, backup and rotation remain release-owner responsibilities. No key access or change was made here |

No historical RestrictedPython, Tornado or builder finding is asserted to affect the final image merely because it appeared in a rejected earlier candidate. Conversely, earlier zero-Critical/High scans do not prove the final digest currently has zero findings

Security sources: [private-output classification](../TASK-2026-09-04-004-classify-private-tool-output/SUMMARY.md), [earlier exact-image signing](../../tasks/todo/TASK-2026-09-03-004-sign-attest-release-images.md), [earlier readiness review](../../tasks/todo/TASK-2026-09-03-002-review-fedora-release-readiness.md), [final functional limits](../TASK-2026-09-05-002-fix-nas-functional-residuals/logs/10-reopen1-dual-host-pass.md)

## Operational decisions and external limits

- Both hosts retain 8-GiB/no-swap containment and restart=no. This deliberately prevents automatic restart loops; recovery/restart policy remains an availability decision for the service owner. No policy change or rollback is performed by closure
- Each final 900-second window passed 31/31 readiness samples with zero memory-limit/OOM events. Memory grew by 205074432 bytes on Fedora and 114589696 bytes on NAS, so these finite windows do not establish a plateau or indefinite leak freedom
- Three NAS Frigate registrations remain externally TCP-unreachable and report timeouts. Fedora retains one timeout and one auth-required peer. Healthy aggregate tools and real calls passed; no universal peer/provider availability is claimed
- Ordinary client/provider limits and rejected requests remain in logs. The corrected sanitizer has zero post-deployment RecursionError markers in the final observed windows. NAS spend records retain token and structured response fields. Fedora's recent-spend query returned zero rows; no Fedora DB-persistence conclusion is manufactured from it
- Protected host-local backups were retained by the deployment tasks. This closure neither accesses them nor performs a fresh backup/restore rehearsal or DB restore
- Deferred experimental DCR-client failure, existing manager-test style findings and the documented combined-process test timeout are not hidden as passes. The four complete isolated mapped files passed 951 tests without skips; this closure does not repair testing tools or rerun runtime qualification

The remaining items are separate owner decisions or evidence limits, not reasons to reopen the accepted functional repair absent new evidence
