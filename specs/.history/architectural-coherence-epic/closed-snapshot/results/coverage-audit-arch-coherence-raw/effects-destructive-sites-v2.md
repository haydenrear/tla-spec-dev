| # | Site | Line | In/Out of model | representation_scope line |
|---|---|---|---|---|
| 1 | `examples/distributed_history/scripts/regenerate_tlc_cases.py:58` | `shutil.rmtree(path)` | OUT | CP2:236 |
| 2 | `examples/effect_providers/atomic_publisher/conformance.py:82` | `os.replace(command.source, command.target)` | OUT | CP2:236 |
| 3 | `examples/effect_providers/atomic_publisher/conformance.py:91` | `path.unlink()` | OUT | CP2:236 |
| 4 | `examples/effect_providers/atomic_publisher/providers.py:180` | `shutil.rmtree(lifecycle_root)` | OUT | CP2:236 |
| 5 | `examples/effect_providers/atomic_publisher/regenerate.py:44` | `shutil.rmtree(target)` | OUT | CP2:236 |
| 6 | `examples/effect_providers/legacy_payment_http/scripts/regenerate.py:53` | `shutil.rmtree(contract)` | OUT | CP2:236 |
| 7 | `examples/effect_providers/legacy_payment_http/scripts/regenerate.py:73` | `shutil.rmtree(package_dir)` | OUT | CP2:236 |
| 8 | `examples/effect_providers/legacy_payment_http/scripts/run_experiment.py:794` | `path.unlink()` | OUT | CP2:236 |
| 9 | `examples/effect_providers/reminder_worker/regenerate.py:50` | `shutil.rmtree(path)` | OUT | CP2:236 |
| 10 | `examples/run_distributed_history_validation.py:430` | `shutil.rmtree(path)` | OUT | CP2:236 |
| 11 | `examples/run_distributed_history_validation.py:432` | `shutil.rmtree(path)` | OUT | CP2:236 |
| 12 | `examples/validation/runs/ex1-run4/artifacts/providers.py:102` | `shutil.rmtree(self.root)` | OUT | CP2:236 |
| 13 | `examples/validation/runs/ex4-run1/artifacts/kill_matrix.py:76` | `shutil.rmtree(pyc, ignore_errors=True)` | OUT | CP2:236 |
| 14 | `examples/validation/runs/ex4-run1/artifacts/kill_matrix.py:99` | `shutil.rmtree(pyc, ignore_errors=True)` | OUT | CP2:236 |
| 15 | `examples/validation/runs/ex4-run1/artifacts/kill_matrix.py:117` | `shutil.rmtree(pyc, ignore_errors=True)` | OUT | CP2:236 |
| 16 | `examples/validation/runs/ex4-run1/artifacts/replay.py:48` | `shutil.rmtree(pyc, ignore_errors=True)` | OUT | CP2:236 |
| 17 | `examples/validation/runs/ex4-run1/artifacts/replay.py:62` | `shutil.rmtree(pyc, ignore_errors=True)` | OUT | CP2:236 |
| 18 | `examples/validation/runs/ex4-run4/artifacts/kill_matrix_round2.py:59` | `shutil.rmtree(pyc, ignore_errors=True)` | OUT | CP2:236 |
| 19 | `examples/validation/runs/ex4-run5/artifacts/replay.py:48` | `shutil.rmtree(pyc, ignore_errors=True)` | OUT | CP2:236 |
| 20 | `examples/validation/runs/ex4-run5/artifacts/replay.py:62` | `shutil.rmtree(pyc, ignore_errors=True)` | OUT | CP2:236 |
| 21 | `scripts/close_spec_workflow.py:49` | `shutil.rmtree(path)` | IN | CP2:231 |
| 22 | `scripts/close_tickets.py:127` | `dst_files[relative].unlink()` | IN | CP2:231 |
| 23 | `scripts/close_tickets.py:232` | `shutil.rmtree(directory)` | IN | CP2:231 |
| 24 | `scripts/effect_conformance.py:692` | `self._patch_module(shutil, "rmtree", "filesystem.delete", 0)` | IN | CP2:231 |
| 25 | `scripts/generate_cases_from_tlc_dump.py:139` | `shutil.rmtree(metadir, ignore_errors=True)` | IN | CP2:231 |
| 26 | `scripts/spec_evolution.py:154` | `shutil.rmtree(state_dir)` | IN | CP2:231 |
| 27 | `scripts/spec_evolution.py:383` | `def replace_tree(src: Path, dst: Path) -> list[dict[str, Any]]:` | IN | CP2:231 |
| 28 | `scripts/spec_evolution.py:385` | `shutil.rmtree(dst)` | IN | CP2:231 |
| 29 | `scripts/spec_evolution.py:477` | `target.unlink()` | IN | CP2:231 |
| 30 | `specs/results/epic-close/sweep-raw-run4/ca4_classify.py:73` | `"scripts/close_spec_workflow.py": "close wrapper; rmtree :49 not performed by a modeled action, no p` | ESCALATION | none — no representation_scope line covers it |
| 31 | `specs/results/epic-close/sweep-raw-run4/ca4_classify.py:75` | `"scripts/close_tickets.py": "batch close (promotion_rule :565 forbids ticket agents running it); unl` | ESCALATION | none — no representation_scope line covers it |
| 32 | `specs/results/epic-close/sweep-raw-run4/ca4_classify.py:185` | `pat = re.compile(r"shutil\.rmtree|\.unlink\(|os\.remove\(")` | ESCALATION | none — no representation_scope line covers it |
| 33 | `specs/results/epic-close/sweep-raw-run5/ca5_changed_enum.sh:15` | `'\b(open|Path|write_text|read_text|write_bytes|mkdir|makedirs|remove|unlink|rename|replace|copy|copy` | ESCALATION | none — no representation_scope line covers it |
| 34 | `specs/results/epic-close/sweep-raw-run5/ca5_delta_check.sh:11` | `'\b(open|Path|write_text|read_text|write_bytes|mkdir|makedirs|remove|unlink|rename|replace|copy|copy` | ESCALATION | none — no representation_scope line covers it |
| 35 | `specs/results/finalization/sweep-raw-close2/cac2_classify.py:219` | `pat = re.compile(r"shutil\.rmtree|\.rmtree\(|\.unlink\(|os\.remove\(|rm -rf|deleteRecursively|Files\` | ESCALATION | none — no representation_scope line covers it |
| 36 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py:32` | `shutil.rmtree(repo)` | ESCALATION | none — no representation_scope line covers it |
| 37 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py:36` | `shutil.rmtree(repo_dir)` | ESCALATION | none — no representation_scope line covers it |
| 38 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py:47` | `shutil.rmtree(target)` | ESCALATION | none — no representation_scope line covers it |
| 39 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py:32` | `shutil.rmtree(repo)` | ESCALATION | none — no representation_scope line covers it |
| 40 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py:36` | `shutil.rmtree(repo_dir)` | ESCALATION | none — no representation_scope line covers it |
| 41 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py:47` | `shutil.rmtree(target)` | ESCALATION | none — no representation_scope line covers it |
| 42 | `test_graph/sources/spec_workflow_cleanup.py:32` | `shutil.rmtree(repo)` | OUT | CP2:235 |
| 43 | `test_graph/sources/spec_workflow_create_repo.py:36` | `shutil.rmtree(repo_dir)` | OUT | CP2:235 |
| 44 | `test_graph/sources/spec_workflow_failure_cleanup_probe.py:49` | `shutil.rmtree(target)` | OUT | CP2:235 |
| 45 | `tests/test_architecture_reflexion.py:1746` | `(deleted / "pkg" / "deliver.py").unlink()` | OUT | CP2:235 |
| 46 | `tests/test_effect_conformance.py:129` | `victim.unlink()` | OUT | CP2:235 |
| 47 | `tests/test_effect_conformance.py:824` | `subprocess.run([sys.executable, "-c", f"import os; os.remove({str(victim)!r})"], check=True)` | OUT | CP2:235 |
| 48 | `tests/test_effect_provider_fuzzing.py:1320` | `event_log.unlink()` | OUT | CP2:235 |
| 49 | `tests/test_effect_provider_fuzzing.py:1369` | `event_log.unlink()` | OUT | CP2:235 |
| 50 | `tests/test_effect_provider_runtime.py:1370` | `(spec_dir / "events.txt").unlink()` | OUT | CP2:235 |
| 51 | `tests/test_kill_test.py:950` | `(spec_dir / "MC.cfg").unlink()` | OUT | CP2:235 |
| 52 | `tests/test_new_ticket_workflow.py:236` | `(ticket_dir / model_dir / "seeded_stale_adapter.py").unlink()` | OUT | CP2:235 |
| 53 | `tests/test_promotion_preserves_current.py:4` | ```shutil.rmtree``'d ``specs/current`` before copying the ticket's ``desired/``` | OUT | CP2:235 |
| 54 | `tests/test_skill_feedback.py:244` | `# GitHub #22 / MF-021: promotion rmtree'd specs/current and destroyed` | OUT | CP2:235 |
