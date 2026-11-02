# Part E poster panel text (English)

Copy-ready text of `docs/poster/E_panel.html` for the team poster tool. Numbers come from `outputs/poster/poster_numbers.json` (run `scripts/14_poster_figures.py`). Figure data for re-plotting: `outputs/poster/tables/E_poster_figure_data.xlsx`.

## Title

Component-level dose-aware trajectory optimization for remote Xe adsorption-bed exchange

Part E · Path-planning algorithm design and simulation · Jaeeun Baek

## Background

A marine molten salt reactor strips fission gases from the fuel salt into an off-gas system, where activated-carbon beds hold up xenon until it decays. Two Xe beds alternate: one captures while the saturated one is swapped by a remote manipulator. Every swap adds dose to the robot's electronics. Dose-aware planners usually model the robot as a single point, the tool centre point (TCP), but the robot fails when its most sensitive part (an encoder, the tool controller or the camera) reaches its limit.

## Objective

- Track dose on 10 robot parts instead of one point: 7 joint drives, tool drive, wrist camera, base connector.
- Rank the levers that reduce part dose (path, dwell posture, part placement) and show how part-level evaluation changes the shielding, module mass and robot needed for a Xe bed exchange.

## Methods

- **Simulation.** PyBullet hot cell, KUKA LBR iiwa 14 (7 axes), exchange task S1 to S6: approach, unlock, remove to cask, fetch new bed, install and lock, return. Joint torques are kept within 80% of the limit over 7 ship inclination cases (MARINA specification).
- **Part dose.** D_k = S_k ∫ Ḋ(p_k(q(t))) dt at each part position p_k. Budget-weighted sum J = Σ D_k / TID_lim,k, with TID_lim = failure dose / 2: encoder 164.55 Gy [1], controller 219 Gy [2], camera 120 Gy (team survey).
- **B0 baseline.** RRT-Connect [3], shortcutting and time-optimal TOPP-RA [4]. **B1:** TCP-dose-weighted 3D A* path.
- **P3 dwell posture.** For each unlock and lock pose, about 450 IK candidates (24 tool yaw angles × 21 null-space elbow poses) with the same TCP; the one with the lowest J over the following moves and dwell is kept.
- **Camera mount search.** 37,044 grid points (2.5 cm) on links A4 to A7. A mount must lie outside the robot body within a 12 cm bracket, stay clear of the robot, cell and beds over the whole task, and see at least 3 of 8 tool-tip edge points from within 0.5 m during unlock and lock.
- **Link to Xe bed design.** Upper-bound Xe inventory from MARINA data; the W shield of the exchange module is sized so that every part stays within its lifetime budget, then the module mass is compared with robot payload.

Scene caption: Unlock dwell (P3). Red: spent Bed A, orange: online Bed B, green: new bed. Yellow dot: current camera beside the tool tip; purple dot: optimized mount on an A4-link bracket (grey bar).

## Figures

**Fig. 1** Dose per part over one exchange (B0, virtual source, wrist camera C09 = 1). The TCP value is 1.70 times the most exposed part, so a point model misstates every part budget. 75% of the summed part dose comes from dwelling (60 s unlock and 60 s lock), 22% from slow straight moves near the beds and only 3% from planned transfers, the only share a path planner can change.

**Fig. 2** Dose change against B0. Path optimization: J −0.6% (summed part dose −0.4 to −1.0% against 30 B0 seeds). Dwell posture: J −2.2% and A4 drive −9.4%, while the TCP dose does not change, so a point model cannot see this gain. Moving the camera to the best mountable spot (A4-link bracket, 0.5 m from the tool tip) cuts camera dose by 81% (72 to 81% under the alternative constraints in the error bar) on the same trajectory. Shifting it 10 to 20 cm back along the tool axis would look similar on paper but places it inside the wrist.

**Fig. 3** Exchange module mass vs. exchange interval (sorbent at 0 °C and 7 bar, fixed wall on the online bed, 3-day cooling, robot parts replaced yearly, W shield, upper-bound source). Sizing the shield on the TCP dose inflates the limiting part by 1.83 times. With the same KR 120, the longest interval grows from 5.3 days (point model) to 7.1 days (part level) and 9.8 days (part level with camera mount): 69, 51 and 37 exchanges per year. Posture (P3) leaves the shield unchanged because the limiting parts, camera and then tool drive, sit on the tool axis.

## Why posture cannot protect the camera

- During unlock and lock the tool axis lines up with the bed axis, and the bed acts as a line source along that axis.
- Turning the tool about this axis or swinging the elbow through the null space keeps the wrist at the same distance from the bed. Only the elbow-side drives gain: A3 −6.1%, A4 −9.4%, A5 −4.8%.
- The wrist camera and the tool drive, the two most exposed parts, can therefore be protected only by distance (placement), shorter dwell or local shielding, which is what the camera mount search exploits.

## Conclusions

1. For this task, part dose is reduced most by dwell time, cooling and shielding, then by part placement, then by dwell posture; the path itself matters least (3% of the dose).
2. A TCP-only evaluation overstates the limiting part by 1.7 to 1.8 times and is blind to posture and placement gains. Part-level evaluation is needed to size shields and choose robots.
3. Part placement is a design variable: moving the camera saves 20 kg of module at a 7-day interval (119 to 99 kg). The tool drive becomes limiting next and needs local shielding or a radiation-tolerant controller.

## Limitations and next steps

- Fig. 1 and 2 use a virtual source (relative values only); Fig. 3 is an upper bound (release fraction 1, no self-shielding or buildup). Dose grids from the radiation part will replace both.
- The 60 s dwell and 5 cm/s near-bed speed are assumptions awaiting the process part.
- Camera constraints are assumptions; view during moves, cabling and added mass are not yet checked.
- Modules of 99 to 137 kg need a KR 120 class robot. A 6-axis arm has no null space, so P3 keeps only the tool yaw.
- Next: optimize posture and part placement together, and treat local shielding of the tool drive as a design variable with its mass charged to the payload.

## References

1. Zhang, Hutson, Knighton, Herrmann, Scott (2020). Radiation tolerance testing methodology of robotic manipulator prior to nuclear waste handling. Front. Robot. AI 7:6. doi:10.3389/frobt.2020.00006
2. Coloma, S. et al. (2023). The effect of ionizing radiation on robotic trajectory movement and electronic components. Nucl. Eng. Technol. 55, 4191-4203.
3. Kuffner, J. J. and LaValle, S. M. (2000). RRT-Connect: An efficient approach to single-query path planning. ICRA 2000, 995-1001.
4. Pham, H. and Pham, Q.-C. (2018). A new approach to time-optimal path parameterization based on reachability analysis. IEEE Trans. Robot. 34(3), 645-659.

Code and data: github.com/Jaeeun-B/EPH_NE_26_fall (dose-aware-traj)
