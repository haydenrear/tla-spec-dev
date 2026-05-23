# First-Class Resource Boundaries

Status: Open

The first production use showed that adapters can accidentally hide important
distributed resources by materializing files or fake transports without those
resources being represented in the TLA+ state.

Add generator and documentation support for first-class resource boundaries.

Acceptance criteria:

- Manifest/schema guidance for resource variables such as Kafka topics,
  consumer offsets, append-log files, manifests, notification queues, and
  training lifecycle state.
- Optional generated Python helper types for resource records, such as topic
  records and append-log rows.
- Adapter runner examples that materialize resource variables into temp files or
  fake transports and observe them back into modeled state.
- Coverage reporting support that lists modeled resources and adapter side
  effects that remain outside the spec.

