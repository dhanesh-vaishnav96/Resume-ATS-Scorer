import re
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings
from app.utils.logger import logger

_SKILLS_DB_PATH = settings.SKILLS_DB_PATH

class SkillMatcher:
    def __init__(self):
        self.master_skills, self.aliases, self.soft_skills = self._load_skills_db()
        try:
            # Industry-level: Use a fast, local embedding model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.skill_list = list(self.master_skills)
            self.skill_embeddings = self.model.encode(self.skill_list, convert_to_tensor=True)
            logger.info("Semantic model loaded and skills embedded.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None

    def _normalize(self, skill: str) -> str:
        if not skill: return ""
        s = skill.lower().replace("-", " ").strip()
        s = re.sub(r"\s+", " ", s)
        return s

    def _load_skills_db(self):
        try:
            with open(_SKILLS_DB_PATH) as f:
                db = json.load(f)
            
            aliases = {}
            for canonical, alias_list in db.get("skill_aliases", {}).items():
                canon_norm = self._normalize(canonical)
                aliases[canon_norm] = canon_norm 
                for alias in alias_list:
                    aliases[self._normalize(alias)] = canon_norm

            flat = set()
            for s in db.get("technical_skills", []):
                norm = self._normalize(s)
                flat.add(aliases.get(norm, norm))
            flat.update(aliases.values())

            soft = set(self._normalize(s) for s in db.get("soft_skills", []))
            return flat, aliases, soft
        except Exception as e:
            logger.error(f"Error loading skills db: {str(e)}")
            return set(), {}, set()

    def rule_based_match(self, text: str, pool: set = None) -> set:
        target_pool = pool if pool is not None else self.master_skills
        text_norm = self._normalize(text)
        found = set()

        for skill in target_pool:
            pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
            if re.search(pattern, text_norm):
                found.add(skill)
                continue
            
            # Check aliases
            for alias, canon in self.aliases.items():
                if canon == skill:
                    if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", text_norm):
                        found.add(skill)
                        break
        return found

    def semantic_match(self, text: str, threshold: float = 0.75) -> set:
        """Find skills based on semantic similarity to text segments."""
        if not self.model: return set()
        
        # Split text into chunks (e.g., sentences or lines) for local context
        chunks = [line.strip() for line in text.split("\n") if len(line.strip()) > 5]
        if not chunks: return set()

        try:
            chunk_embeddings = self.model.encode(chunks, convert_to_tensor=True)
            # Compute cosine similarity between chunks and all skills
            # This is a broad search; in production, you might use FAISS for speed
            import torch
            cos_scores = torch.nn.functional.cosine_similarity(chunk_embeddings.unsqueeze(1), self.skill_embeddings.unsqueeze(0), dim=2)
            
            found = set()
            # Find indices where similarity > threshold
            matches = (cos_scores > threshold).nonzero()
            for idx in matches:
                skill_idx = idx[1].item()
                found.add(self.skill_list[skill_idx])
            return found
        except Exception as e:
            logger.error(f"Semantic match failed: {e}")
            return set()

    def get_combined_skills(self, text: str) -> set:
        """Hybrid matching: Rules (Exact) + Semantic (Contextual)."""
        exact = self.rule_based_match(text)
        # If we found few skills, or just as a safety net, add semantic results
        semantic = self.semantic_match(text)
        return exact.union(semantic)

    def extract_soft_skills(self, text: str) -> list[str]:
        text_norm = self._normalize(text)
        found = set()
        for skill in self.soft_skills:
            if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", text_norm):
                found.add(skill)
        return sorted(found)

    def extract_projects(self, resume_text: str) -> list[str]:
        PROJECT_HEADERS = {"project", "projects", "portfolio", "built", "developed"}
        lines = resume_text.split("\n")
        projects, current, in_project = [], [], False

        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()
            is_header = any(kw == lower or f"{kw}:" in lower for kw in PROJECT_HEADERS)
            if is_header:
                if current: projects.append(" ".join(current))
                current, in_project = [stripped], True
            elif in_project and stripped:
                current.append(stripped)
            elif in_project and not stripped:
                if current: projects.append(" ".join(current))
                current, in_project = [], False

        if current: projects.append(" ".join(current))
        return projects

    def extract_experience_score(self, resume_text: str) -> float:
        text_lower = resume_text.lower()
        explicit = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?\b", text_lower)
        if explicit:
            years = max(float(y) for y in explicit)
            return self._years_to_score(years)
        if any(kw in text_lower for kw in ["intern", "internship", "trainee"]):
            return 4.0
        return 0.0

    def _years_to_score(self, years: float) -> float:
        if years >= 3: return 10.0
        if years >= 1: return 7.0
        return 4.0

matcher = SkillMatcher()
