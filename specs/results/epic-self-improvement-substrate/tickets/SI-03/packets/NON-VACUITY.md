# SI-03 negative control: the redaction pair, and its non-vacuity check

The improvement card requires a negative control per dimension AND evidence that
the control's low score comes from the dimension rather than from an unrelated
defect in the packet. SI-10's first control was vacuous; this is the check that
would have caught that.

Subject: PR #352 (SI-06), the wave-3 ticket with four reported blockers, each
carrying a proposed change and a stated disposition.

- full packet      : 208 lines  sha256 b053bfcd51202489
- redacted packet  : 159 lines  sha256 10616f0b5a2d18b0
- lines ADDED by the redaction   : 0   (must be 0 -- a redaction adds nothing)
- lines REMOVED by the redaction : 48
- removed lines NOT belonging to the two redacted sections: 0   (must be 0)

The pair therefore differs in EXACTLY `## Skill changes proposed` and
`## Review input` and in nothing else. If both halves score the same on I1, I2
or I3, the check is reading something other than the sections it claims to read,
and the control is vacuous.

Sections surviving redaction: ['What landed', 'Dependency and promotion checks', 'Validation', 'Goal contribution', 'Deferred findings', '`home close-out` verdict', 'Reconciled onto the epic tip (2026-09-18)']
