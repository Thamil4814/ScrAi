from __future__ import annotations

import re
from dataclasses import dataclass

from pyscrai.contracts.models import (
    Entity,
    Polity,
    ProvenanceRecord,
    Rule,
    WorldMatrixDraft,
    utc_now,
)
from pyscrai.domain.enums import OperatorMode, ProvenanceKind, SessionPhase


@dataclass(slots=True)
class SetupMappingResult:
    extracted_facts: list[str]
    captured_updates: list[str]


class SetupInterviewMapper:
    ENTITY_CUES = ("actors", "entities", "individuals", "people")
    POLITY_CUES = ("polities", "factions", "groups", "states", "organizations")
    RULE_CUES = ("rules", "constraints")
    TIME_PATTERNS = (
        (re.compile(r"\bnear[- ]future\b", re.IGNORECASE), "near-future"),
        (
            re.compile(
                r"\bpresent[- ]day\b|\bcurrent day\b|\bmodern day\b", re.IGNORECASE
            ),
            "present-day",
        ),
        (re.compile(r"\b(\d{4}s)\b"), None),
        (re.compile(r"\b(\d{4})\b"), None),
    )
    SPATIAL_PATTERNS = (
        re.compile(
            r"\bin ((?:the )?[A-Za-z][A-Za-z0-9' -]+?)(?=,|\.|\bcentered\b|\bwith\b|\bwhere\b|$)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bacross ((?:the )?[A-Za-z][A-Za-z0-9' -]+?)(?=,|\.|\bwith\b|\bwhere\b|$)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bwithin ((?:the )?[A-Za-z][A-Za-z0-9' -]+?)(?=,|\.|\bwith\b|\bwhere\b|$)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bcentered on ((?:the )?[A-Za-z][A-Za-z0-9' -]+?)(?=,|\.|\bwith\b|\bwhere\b|$)",
            re.IGNORECASE,
        ),
    )
    OPERATOR_MODE_PATTERNS = (
        (
            re.compile(
                r"\boperator (?:mode|role)\s+(?:is|=)\s+observer\b", re.IGNORECASE
            ),
            OperatorMode.OBSERVER,
        ),
        (
            re.compile(
                r"\boperator (?:mode|role)\s+(?:is|=)\s+director\b", re.IGNORECASE
            ),
            OperatorMode.DIRECTOR,
        ),
        (
            re.compile(r"\boperator (?:mode|role)\s+(?:is|=)\s+zeus\b", re.IGNORECASE),
            OperatorMode.ZEUS,
        ),
        (
            re.compile(
                r"\boperator (?:mode|role)\s+(?:is|=)\s+entity possession\b",
                re.IGNORECASE,
            ),
            OperatorMode.ENTITY_POSSESSION,
        ),
        (
            re.compile(
                r"\boperator (?:mode|role)\s+(?:is|=)\s+polity possession\b",
                re.IGNORECASE,
            ),
            OperatorMode.POLITY_POSSESSION,
        ),
    )

    def apply_operator_message(
        self,
        draft: WorldMatrixDraft,
        content: str,
        phase: SessionPhase,
    ) -> SetupMappingResult:
        trimmed = content.strip()
        before = self._snapshot(draft)
        if phase == SessionPhase.INTENT_FRAMING:
            self._apply_environment(draft, trimmed)
        for clause in self._split_clauses(trimmed):
            self._apply_phase_aware_clause(draft, clause, phase)
        self._append_provenance(draft, trimmed)
        draft.metadata.updated_at = utc_now()

        return SetupMappingResult(
            extracted_facts=self.extract_facts(draft),
            captured_updates=self._captured_updates(before, draft),
        )

    def extract_facts(self, draft: WorldMatrixDraft) -> list[str]:
        facts: list[str] = []
        if draft.environment.description:
            facts.append(f"Environment described: {draft.environment.description}")
        if draft.domain.time_scope != "unspecified":
            facts.append(f"Time scope: {draft.domain.time_scope}")
        if draft.domain.spatial_scope != "unspecified":
            facts.append(f"Spatial scope: {draft.domain.spatial_scope}")
        if draft.environment.locations:
            facts.append(f"Locations: {', '.join(draft.environment.locations)}")
        if draft.operator_role.mode:
            facts.append(f"Operator mode: {draft.operator_role.mode}")
        if draft.entities:
            facts.append(
                f"Entities: {', '.join(entity.name for entity in draft.entities)}"
            )
        if draft.polities:
            facts.append(
                f"Polities: {', '.join(polity.name for polity in draft.polities)}"
            )
        if draft.rules:
            facts.append(f"Rules captured: {len(draft.rules)}")
        return facts

    def _apply_environment(self, draft: WorldMatrixDraft, content: str) -> None:
        if not draft.environment.description:
            draft.environment.description = content
            return
        draft.environment.macro_conditions.append(content)

    def _apply_phase_aware_clause(
        self, draft: WorldMatrixDraft, clause: str, phase: SessionPhase
    ) -> None:
        self._apply_time_scope(draft, clause)
        self._apply_spatial_scope(draft, clause)

        if phase in {
            SessionPhase.WORLD_POPULATION,
            SessionPhase.RULES_AND_KNOWLEDGE_BOUNDARIES,
            SessionPhase.VALIDATION_PASS,
        }:
            self._apply_entities(draft, clause)
            self._apply_polities(draft, clause)

        if phase in {
            SessionPhase.RULES_AND_KNOWLEDGE_BOUNDARIES,
            SessionPhase.VALIDATION_PASS,
        }:
            self._apply_operator_mode(draft, clause)
            self._apply_rules(draft, clause)
            self._apply_knowledge_layers(draft, clause)

    def _apply_time_scope(self, draft: WorldMatrixDraft, content: str) -> None:
        if draft.domain.time_scope != "unspecified":
            return
        for pattern, fixed_value in self.TIME_PATTERNS:
            match = pattern.search(content)
            if not match:
                continue
            draft.domain.time_scope = fixed_value or match.group(1)
            return

    def _apply_spatial_scope(self, draft: WorldMatrixDraft, content: str) -> None:
        candidate = self._extract_spatial_scope(content)
        if not candidate:
            return
        if draft.domain.spatial_scope == "unspecified":
            draft.domain.spatial_scope = candidate
        if candidate not in draft.environment.locations:
            draft.environment.locations.append(candidate)

    def _extract_spatial_scope(self, content: str) -> str | None:
        for pattern in self.SPATIAL_PATTERNS:
            match = pattern.search(content)
            if match:
                return match.group(1).strip(" .,")
        return None

    def _apply_operator_mode(self, draft: WorldMatrixDraft, content: str) -> None:
        for pattern, operator_mode in self.OPERATOR_MODE_PATTERNS:
            if pattern.search(content):
                draft.operator_role.mode = operator_mode
                return

    def _apply_entities(self, draft: WorldMatrixDraft, content: str) -> None:
        items = self._extract_list_after_cues(content, self.ENTITY_CUES)
        for item in items:
            if self._has_named_item(draft.entities, item):
                continue
            draft.entities.append(Entity(name=item, type="actor"))

    def _apply_polities(self, draft: WorldMatrixDraft, content: str) -> None:
        items = self._extract_list_after_cues(content, self.POLITY_CUES)
        for item in items:
            if self._has_named_item(draft.polities, item):
                continue
            draft.polities.append(Polity(name=item, category="group"))

    def _apply_rules(self, draft: WorldMatrixDraft, content: str) -> None:
        for item in self._extract_list_after_cues(content, self.RULE_CUES):
            if self._has_rule(draft.rules, item):
                continue
            draft.rules.append(Rule(category="constraint", description=item))

        forbidden_match = re.search(
            r"\bforbidden(?: actions?)?\s*(?:are|include|:)\s*(.+)$",
            content,
            re.IGNORECASE,
        )
        if not forbidden_match:
            return
        for item in self._split_list_items(forbidden_match.group(1)):
            if self._has_rule(draft.rules, item):
                continue
            draft.rules.append(
                Rule(
                    category="forbidden_action",
                    description=f"Forbidden action: {item}",
                    forbidden_actions=[item],
                )
            )

    def _apply_knowledge_layers(self, draft: WorldMatrixDraft, content: str) -> None:
        public_match = re.search(
            r"\bpublic knows(?: that)?\s+(.+)$", content, re.IGNORECASE
        )
        if public_match:
            claim = public_match.group(1).strip(" .")
            if claim and claim not in draft.knowledge_layers.public_knowledge:
                draft.knowledge_layers.public_knowledge.append(claim)

        contested_match = re.search(
            r"\bcontested(?: claims?)?\s*:\s*(.+)$", content, re.IGNORECASE
        )
        if contested_match:
            for item in self._split_list_items(contested_match.group(1)):
                if item not in draft.knowledge_layers.contested_claims:
                    draft.knowledge_layers.contested_claims.append(item)

    @staticmethod
    def _split_clauses(content: str) -> list[str]:
        return [part.strip() for part in re.split(r"[.;\n]+", content) if part.strip()]

    @staticmethod
    def _extract_list_after_cues(content: str, cues: tuple[str, ...]) -> list[str]:
        for cue in cues:
            match = re.search(
                rf"\b{cue}\s*(?:are|include|:)\s*(.+)$", content, re.IGNORECASE
            )
            if match:
                return SetupInterviewMapper._split_list_items(match.group(1))
        return []

    @staticmethod
    def _split_list_items(raw_items: str) -> list[str]:
        normalized = re.sub(r"\band\b", ",", raw_items, flags=re.IGNORECASE)
        return [
            item.strip(" ,.") for item in normalized.split(",") if item.strip(" ,.")
        ]

    @staticmethod
    def _has_named_item(items: list[Entity] | list[Polity], candidate: str) -> bool:
        candidate_key = candidate.casefold()
        return any(item.name.casefold() == candidate_key for item in items)

    @staticmethod
    def _has_rule(rules: list[Rule], candidate: str) -> bool:
        candidate_key = candidate.casefold()
        return any(
            rule.description.casefold().endswith(candidate_key) for rule in rules
        )

    @staticmethod
    def _append_provenance(draft: WorldMatrixDraft, content: str) -> None:
        draft.provenance.append(
            ProvenanceRecord(
                kind=ProvenanceKind.OPERATOR_DEFINED,
                source="setup.message",
                detail=content,
                confidence=1.0,
            )
        )

    @staticmethod
    def _snapshot(draft: WorldMatrixDraft) -> dict[str, object]:
        return {
            "environment": draft.environment.description,
            "time_scope": draft.domain.time_scope,
            "spatial_scope": draft.domain.spatial_scope,
            "operator_mode": draft.operator_role.mode,
            "entities": [entity.name for entity in draft.entities],
            "polities": [polity.name for polity in draft.polities],
            "rule_count": len(draft.rules),
            "public_knowledge_count": len(draft.knowledge_layers.public_knowledge),
            "contested_claim_count": len(draft.knowledge_layers.contested_claims),
        }

    @staticmethod
    def _captured_updates(
        before: dict[str, object], draft: WorldMatrixDraft
    ) -> list[str]:
        updates: list[str] = []
        if (
            before["environment"] != draft.environment.description
            and draft.environment.description
        ):
            updates.append("environment framing")
        if (
            before["time_scope"] != draft.domain.time_scope
            and draft.domain.time_scope != "unspecified"
        ):
            updates.append(f"time scope {draft.domain.time_scope}")
        if (
            before["spatial_scope"] != draft.domain.spatial_scope
            and draft.domain.spatial_scope != "unspecified"
        ):
            updates.append(f"spatial scope {draft.domain.spatial_scope}")
        if before["operator_mode"] != draft.operator_role.mode:
            updates.append(f"operator mode {draft.operator_role.mode}")

        before_entities_list = before["entities"]
        assert isinstance(before_entities_list, list), "Expected entities to be a list"
        before_entities = set(before_entities_list)
        new_entities = [
            entity.name
            for entity in draft.entities
            if entity.name not in before_entities
        ]
        if new_entities:
            updates.append(f"entities {', '.join(new_entities)}")

        before_polities_list = before["polities"]
        assert isinstance(before_polities_list, list), "Expected polities to be a list"
        before_polities = set(before_polities_list)
        new_polities = [
            polity.name
            for polity in draft.polities
            if polity.name not in before_polities
        ]
        if new_polities:
            updates.append(f"polities {', '.join(new_polities)}")

        rule_count = before["rule_count"]
        assert isinstance(rule_count, int), "Expected rule_count to be an int"
        if rule_count != len(draft.rules):
            updates.append(f"{len(draft.rules) - rule_count} rule updates")
        if before["public_knowledge_count"] != len(
            draft.knowledge_layers.public_knowledge
        ):
            updates.append("public knowledge")
        if before["contested_claim_count"] != len(
            draft.knowledge_layers.contested_claims
        ):
            updates.append("contested claims")
        return updates
