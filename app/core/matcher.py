import re
import json
from app.config import settings
from app.utils.logger import logger

_SKILLS_DB_PATH = settings.SKILLS_DB_PATH

def _normalize(skill: str) -> str:
    """Basic syntactic normalization: lowercase, remove hyphens, collapse whitespace."""
    if not skill: return ""
    s = skill.lower().replace("-", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def _load_skills_db():
    try:
        with open(_SKILLS_DB_PATH) as f:
            db = json.load(f)

        # 1. Build alias map: normalized alias -> normalized canonical
        aliases = {}
        for canonical, alias_list in db.get("skill_aliases", {}).items():
            canon_norm = _normalize(canonical)
            # Map canonical to itself for stability
            aliases[canon_norm] = canon_norm 
            for alias in alias_list:
                aliases[_normalize(alias)] = canon_norm

        # 2. Build canonical Technical skills pool
        flat = set()
        tech_list = db.get("technical_skills", [])
        for s in tech_list:
            norm = _normalize(s)
            # Resolve to canonical if it's an alias
            flat.add(aliases.get(norm, norm))
        
        # Add all canonical names from alias map to the flat pool
        flat.update(aliases.values())

        # 3. Soft skills (all normalized)
        soft = set()
        for s in db.get("soft_skills", []):
            soft.add(_normalize(s))

        return flat, aliases, soft
    except Exception as e:
        logger.error(f"Error loading skills db: {str(e)}")
        return set(), {}, set()

# Initialize global state
_MASTER_SKILLS, _ALIASES, _SOFT_SKILLS = _load_skills_db()

def _canonicalize(skill: str) -> str:
    """Map normalized skill to its canonical name from the database."""
    norm = _normalize(skill)
    return _ALIASES.get(norm, norm)

def extract_skills_from_text(text: str, candidate_pool: set = None) -> set:
    pool = candidate_pool if candidate_pool is not None else _MASTER_SKILLS
    # Normalize the entire text for matching
    text_norm = _normalize(text)
    found = set()

    for skill in pool:
        # Check canonical skill directly
        pattern = re.escape(skill)
        if re.search(rf"(?<!\w){pattern}(?!\w)", text_norm):
            found.add(skill)
            continue
        
        # Check if any alias matches this canonical skill
        for alias, canon in _ALIASES.items():
            if canon == skill:
                pattern_alias = re.escape(alias)
                if re.search(rf"(?<!\w){pattern_alias}(?!\w)", text_norm):
                    found.add(skill)
                    break

    return found

def extract_soft_skills(text: str) -> list[str]:
    """Extract soft skills from normalized text."""
    text_norm = _normalize(text)
    found = set()
    for skill in _SOFT_SKILLS:
        pattern = re.escape(skill)
        if re.search(rf"(?<!\w){pattern}(?!\w)", text_norm):
            found.add(skill)
    return sorted(found)

def extract_projects(resume_text: str) -> list[str]:
    """Detect project blocks using broad header and keyword signals."""
    PROJECT_HEADERS = {
        "project", "projects", "portfolio", "what i built", "case study",
        "case studies", "work", "personal work", "open source", "side project",
        "academic project", "major project", "mini project", "capstone",
        "built", "developed", "created", "implemented"
    }
    SKILL_KEYWORDS = {"using", "built with", "tech stack", "tools used",
                      "technologies", "framework"}

    lines = resume_text.split("\n")
    projects = []
    current = []
    in_project = False

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        # Robust header detection
        is_header = any(kw == lower for kw in PROJECT_HEADERS)
        if not is_header and len(line) < 60:
             is_header = any(rf"{kw}\s*[:\-]" in lower for kw in PROJECT_HEADERS) or \
                         any(lower.startswith(kw) for kw in ["project", "case study"])
             
        has_skills = any(kw in lower for kw in SKILL_KEYWORDS)

        if is_header or has_skills:
            if current and in_project:
                projects.append(" ".join(current))
            current = [stripped]
            in_project = True
        elif in_project and stripped:
            current.append(stripped)
        elif in_project and not stripped:
            if current:
                projects.append(" ".join(current))
            current = []
            in_project = False

    if current and in_project:
        projects.append(" ".join(current))

    return projects

def _years_to_score(years: float) -> float:
    if years >= 3: return 10.0
    elif years >= 1: return 7.0
    else: return 4.0

def extract_experience_score(resume_text: str) -> float:
    """
    Detect years of experience from:
    - Explicit jobs/roles or date ranges
    - Internships and traineeships
    - IF Fresher (no job/internship): return 0.0
    """
    text_lower = resume_text.lower()

    # Signals for experience (jobs or internships)
    exp_signals = r"experience|exp\.?|work|industry|professional|intern|internship|trainee"

    # Pattern 1: explicit years
    explicit = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?\b", text_lower)
    if explicit:
        if re.search(exp_signals, text_lower):
            years = max(float(y) for y in explicit)
            if years > 0:
                return _years_to_score(years)

    # Pattern 2: date ranges
    year_matches = re.findall(r"\b(20\d{2})\b", text_lower)
    if year_matches:
        years_list = sorted(set(int(y) for y in year_matches))
        span = max(years_list) - min(years_list)
        if span > 0:
            if re.search(exp_signals, text_lower):
                return _years_to_score(float(span))

    # Pattern 3: explicit internship mention counts as experience (min score 4.0 if found)
    if any(kw in text_lower for kw in ["intern", "internship", "trainee"]):
        return 4.0

    # Else: Fresher (Score = 0.0 as requested)
    return 0.0

class SkillMatcher:
    def rule_based_match(self, text: str) -> set:
        return extract_skills_from_text(text)
    
    def get_combined_skills(self, text: str) -> set:
        return extract_skills_from_text(text)
    
    def extract_projects(self, text: str) -> list[str]:
        return extract_projects(text)
    
    def extract_soft_skills(self, text: str) -> list[str]:
        return extract_soft_skills(text)

# Initialize global state once
_MASTER_SKILLS, _ALIASES, _SOFT_SKILLS = _load_skills_db()
matcher = SkillMatcher()
