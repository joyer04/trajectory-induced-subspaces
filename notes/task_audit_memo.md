# Task Cleanliness Audit

Artifacts:

- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/task_audit_compile_check/task_audit_table.csv`
- `/Users/tedhong/Research/trajectory-induced-subspaces/outputs/task_audit_compile_check/subfamily_clean_support.csv`

## Summary

- prompts audited: `58`
- clean mixed prompts: `17`
- parser-fragile prompts: `6`
- single-outcome prompts: `35`

## Read

Use `clean_mixed` prompts for mechanism validation whenever possible.
Use `single_outcome` prompts for generation-quality diagnostics, not for same-location/history tests.
Treat `parser_fragile` prompts as excluded until the oracle is improved.
