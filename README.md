# Jumper

Jumper is a browser-based city-scale flight game built around one input: hold **Space** to charge a jump, release to launch, and press Space again in the air to spin. Land upright, earn score and coins, unlock new cities, and collect shoes with different movement bonuses.

## Features

- Six city stages with five levels per city.
- Charge-and-release jumping with trajectory preview.
- Frontflip/backflip mode switching with `F`.
- Timing-based landings, score, aura, coins, revive, and progression.
- Unlockable shoes that change speed, jump, spin, and coin rewards.
- Account registration and login.
- Server-side progress persistence with SQLite and optimistic version checks.
- Unit-tested game-engine functions for trajectories, rewards, progression, and penalties.

## Run locally

Requirements: Node.js and npm.

```bash
npm install
npm run dev
```

The development command starts the API server and Vite frontend. For a production-style local run:

```bash
npm run build
npm start
```

## Controls

| Input | Action |
| --- | --- |
| Hold Space | Charge a jump |
| Release Space | Launch |
| Press Space in the air | Spin |
| F | Switch frontflip/backflip |

## Architecture

- `src/main.tsx` — React UI, authentication flow, canvas game loop, and progression state.
- `src/game/engine.ts` — deterministic game rules and reward calculations.
- `src/game/levels.ts` — cities, levels, pads, and shoes.
- `server/index.js` — Express API, authentication, SQLite persistence, and progress conflict handling.
- `src/game/engine.test.ts` — game-engine tests.

## Verification

```bash
npm test
npm run build
```

This project is a playable prototype. Before production use, authentication hardening, password-reset flows, rate limiting, CSRF protection, and operational database management would still be required.
