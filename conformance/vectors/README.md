# RL2 0.7 Semantic Conformance Vectors

These vectors state evaluator-independent observations of the normative evaluation contract. They
are not traces from a particular implementation.

- [Snapshot resolution](snapshot-resolution.md): fact and evidence normalization, attribution, and error handling.
- [Duty and Promise status](duty-status.md): status boundaries and temporal evidence.
- [Duty attachment](duty-attachment.md): prerequisite locality in access decisions.
- [Offer materialization](offer-materialization.md): pure Offer-to-Agreement transformation.

Each vector identifies the policy universe, request, world snapshot, evaluation
configuration, and expected result or diagnostic. A conforming evaluator produces the stated
observable result for every well-formed vector.
