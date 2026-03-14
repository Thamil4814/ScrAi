from __future__ import annotations

import re
from typing import Iterable

from pyscrai.contracts.models import (
    Entity,
    Scenario,
    SimulationRun,
    SimulationRunRequest,
    WorldBranch,
    WorldMatrix,
    utc_now,
)


class ScenarioRuntimeEngine:
    """Deterministic MVP runtime for scenario smoke tests."""

    ACTION_CYCLE = ("observe", "negotiate", "signal", "pressure")
    TENSION_SCORES = {"low": 2, "medium": 5, "high": 8}
    TURN_LIMIT_PATTERN = re.compile(r"turn_limit\s*=\s*(\d+)", re.IGNORECASE)

    def run(
        self,
        scenario: Scenario,
        branch: WorldBranch,
        worldmatrix: WorldMatrix,
        request: SimulationRunRequest | None = None,
    ) -> SimulationRun:
        config = request or SimulationRunRequest()
        actors = self._resolve_actors(scenario, worldmatrix.payload.entities)
        turn_limit = self._resolve_turn_limit(
            config.turn_limit, scenario.stop_conditions
        )
        tension = self._initial_tension(scenario.initial_state.get("tension"))
        stop_conditions = [item.casefold() for item in scenario.stop_conditions]

        run = SimulationRun(scenario_id=scenario.id)
        for event in config.inject_events:
            run.event_log.append({"turn": "0", "event": event, "tension": str(tension)})

        stop_reason = "turn_limit_reached"
        turns_executed = 0
        pressure_actions = 0
        negotiate_actions = 0
        tension_history = [tension]

        for turn in range(1, turn_limit + 1):
            turns_executed = turn
            for actor_index, actor in enumerate(actors):
                action = self.ACTION_CYCLE[
                    (turn + actor_index) % len(self.ACTION_CYCLE)
                ]
                if action == "pressure":
                    pressure_actions += 1
                if action == "negotiate":
                    negotiate_actions += 1
                tension = max(0, min(10, tension + self._tension_delta(action)))
                run.runtime_trace.append(
                    {
                        "turn": str(turn),
                        "actor": actor,
                        "action": action,
                        "objective": config.objective,
                        "worldbranch_id": branch.id,
                    }
                )
                run.event_log.append(
                    {
                        "turn": str(turn),
                        "event": f"{actor} executes {action}",
                        "tension": str(tension),
                    }
                )

            run.state_snapshots.append(
                {
                    "turn": str(turn),
                    "active_actors": str(len(actors)),
                    "tension": str(tension),
                }
            )
            tension_history.append(tension)

            if self._deescalation_reached(stop_conditions, tension):
                stop_reason = "de-escalation reached"
                break

        volatility = sum(
            abs(current - previous)
            for previous, current in zip(tension_history, tension_history[1:])
        )
        stability_score = max(
            0,
            100
            - (tension * 8)
            - (pressure_actions * 4)
            + (negotiate_actions * 3)
            - (volatility * 2),
        )
        run.completed_at = utc_now()
        run.result_summary = {
            "objective": config.objective,
            "turns_executed": str(turns_executed),
            "stop_reason": stop_reason,
            "actor_count": str(len(actors)),
            "final_tension": str(tension),
            "pressure_actions": str(pressure_actions),
            "negotiate_actions": str(negotiate_actions),
            "volatility": str(volatility),
            "stability_score": str(stability_score),
        }
        return run

    @classmethod
    def _resolve_actors(cls, scenario: Scenario, entities: list[Entity]) -> list[str]:
        if scenario.actor_bindings:
            unique_actors = list(dict.fromkeys(scenario.actor_bindings.values()))
            if unique_actors:
                return unique_actors
        if entities:
            return [entity.name for entity in entities[:4]]
        return ["actor_alpha", "actor_bravo"]

    @classmethod
    def _resolve_turn_limit(
        cls, request_limit: int | None, stop_conditions: Iterable[str]
    ) -> int:
        explicit_limit = request_limit
        for condition in stop_conditions:
            match = cls.TURN_LIMIT_PATTERN.search(condition)
            if match:
                matched_limit = int(match.group(1))
                explicit_limit = (
                    matched_limit
                    if explicit_limit is None
                    else min(explicit_limit, matched_limit)
                )
        return explicit_limit or 6

    @classmethod
    def _initial_tension(cls, tension: str | None) -> int:
        if not tension:
            return cls.TENSION_SCORES["medium"]
        return cls.TENSION_SCORES.get(tension.casefold(), cls.TENSION_SCORES["medium"])

    @staticmethod
    def _tension_delta(action: str) -> int:
        if action == "negotiate":
            return -1
        if action == "pressure":
            return 1
        return 0

    @staticmethod
    def _deescalation_reached(stop_conditions: list[str], tension: int) -> bool:
        return (
            any("de-escalation" in condition for condition in stop_conditions)
            and tension <= 2
        )
