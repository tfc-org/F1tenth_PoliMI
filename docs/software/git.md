# Git and submodules

The car's drivers live in a separate repository that we forked, linked here as a submodule. That keeps upstream's history intact and lets us pull their fixes, at the price of one extra commit whenever we change the fork.

- `ros2_ws/src/f1tenth_system` is a submodule: our fork `tfc-org/f1tenth_system`, branch `humble-polimi`.
- Its own submodules: `vesc` (`ros2`), `ackermann_mux` (`foxy-devel`, builds on Humble), `teleop_tools` (`humble-devel`).
- `setup_git.sh` adds `upstream` → `f1tenth/f1tenth_system`.

## Edit the fork (two commits)

A submodule is a pointer to one commit of the other repository. Changing the fork therefore takes a commit there, then a commit here that moves the pointer:

```bash
cd ros2_ws/src/f1tenth_system
git switch humble-polimi                  # submodules start detached
git add -A && git commit -m "..." && git push              # 1) fork
cd ../../..
git add ros2_ws/src/f1tenth_system
git commit -m "Bump f1tenth_system: ..." && git push       # 2) pointer
```

`push.recurseSubmodules=check` blocks step 2 if step 1 wasn't pushed.

## Sync with upstream

To bring in what the F1TENTH maintainers changed since our fork:

```bash
cd ros2_ws/src/f1tenth_system
git fetch upstream
git log --oneline humble-polimi..upstream/humble-devel     # preview
git switch humble-polimi && git merge upstream/humble-devel
git submodule update --init --recursive
git push
```

Then bump the pointer as in step 2.

## Pick up someone else's bump

```bash
git pull                                  # submodule.recurse moves the submodule too
```
