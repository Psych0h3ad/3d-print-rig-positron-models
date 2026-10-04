# Positron models for 3D Print Rig

Browser display assets derived from the official assembled Positron V3.2.2 CAD (2026-01-26), with all 1,314 native assembly leaves. The viewer includes a guided rigid folding sequence and configurable colors.

- [3D Print Rig](https://psych0h3ad.github.io/3d-print-rig/viewer/positron.html?machine=positron_v322)
- [Original Positron CAD](https://github.com/Positron3D/Positron/tree/75ac17a07e02694e1fc80a3a256ede64cca90e6d)
- [Positron 3D](https://positron3d.com/)
- [LDO folding guide](https://ldomotion.com/guides/10---positron-v32---folding)

Credit Positron 3D Team and LDO Motors; original V3 by Kralyn. Hardware and documentation retain CC BY-SA 4.0. The upstream exception for LDO-manufactured PCB designs also applies; see [the notice](site/NOTICE.txt) and the pinned original repository.

Native CNC slot and hinge geometry is retained. Hand-carried parts use illustrative paths. The master CAD contains no flexible belt or wiring models. Small details are reduced for display, and four invalid native reference leaves remain reference geometry. Finite structural checks are not physical clearance certification.

`site/ASSET_INDEX.json` records exact compressed and decoded hashes. Build with `python scripts/build_site.py --output _site`.
