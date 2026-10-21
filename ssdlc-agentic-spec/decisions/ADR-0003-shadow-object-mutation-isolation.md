# ADR-0003: Shadow Object Cloning for Destructive Mutation Testing

- **Status**: Accepted
- **Deciders**: Safety & Execution Lead
- **Date**: 2026-10-21

## Context
Testing state-changing authorization flaws (BOLA on `PUT`, `PATCH`, `DELETE`) mutates or permanently destroys target objects. In multi-step pentesting, deleting an object early in the test session invalidates all downstream test cases for that entity, corrupting the benchmark harness and causing cascading test failures.

## Decision
Before executing any destructive HTTP verb (`DELETE`, `PUT`, `PATCH`) against an object, the `ShadowObjectCloner` automatically creates an ephemeral clone of the target object using the authorized owner's credentials. The test is then performed exclusively against the shadow clone.

## Consequences
- **Positive**: Protects benchmark state integrity; enables safe execution in staging environments; eliminates test interference.
- **Negative**: Adds 1-2 pre-flight API calls to clone or recreate objects before write-testing.
