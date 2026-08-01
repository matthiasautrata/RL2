# ODRL 2.2 to RL2 0.7 Migration Fixtures

Each fixture pairs a small ODRL 2.2 source graph with its canonical RL2 result or an importer
diagnostic. The mapping rules are normative in [RL2_ODRL_Mapping.md](../../spec/RL2_ODRL_Mapping.md).

| Fixture | ODRL construct | Expected outcome |
|---|---|---|
| [Permission](permission.md) | `odrl:Permission` | canonical `rl2:Privilege` |
| [Prohibition](prohibition.md) | `odrl:Prohibition` | canonical `rl2:Prohibition` |
| [Attached Duty](attached-duty.md) | Permission `odrl:duty` | attached `rl2:prerequisiteDuty` |
| [Conflict](conflict.md) | conflicting Permission and Prohibition | declared evaluation strategy |
| [Ordered Constraint](rejected-ordered-constraint.md) | ordered constraint relation | rejection |

A fixture records its source graph, translation disposition, expected RL2 graph or diagnostic, and
the stated preservation claim. Importers must not introduce unstated assumptions.
