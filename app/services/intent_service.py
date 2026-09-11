"""
Intent & Domain Classification Service for ExpertVerse AI.
Extracts user intent, career goal, domain, subdomains, key skills, and expert requirements
from natural language queries using multi-signal linguistic analysis and semantic patterns.
"""

from typing import Any
import re

# Comprehensive Domain Taxonomy
DOMAIN_TAXONOMY: dict[str, dict[str, Any]] = {
    "medicine": {
        "display_name": "Medicine & Healthcare",
        "keywords": [
            "doctor", "doc", "physician", "surgeon", "medicine", "medical",
            "mbbs", "md", "neet", "neet pg", "usmle", "plab", "clinic", "clinical",
            "healthcare", "hospital", "patient", "nursing", "nurse", "pediatric",
            "orthopedic", "cardiology", "neurology", "dermatology", "radiology",
            "pathology", "pharmacology", "dentist", "dental", "bds", "pre-med"
        ],
        "subdomains": ["Medical Education", "Clinical Medicine", "Healthcare Admissions", "Specialist Residency"],
        "desired_expert_type": "Medical Doctor & Healthcare Career Mentor",
        "related_expert_tags": ["medicine", "doctor", "mbbs", "healthcare", "clinical", "neet", "medical education", "surgeon"]
    },
    "ui_ux_design": {
        "display_name": "UI/UX & Product Design",
        "keywords": [
            "ui", "ux", "ui/ux", "ui ux", "user interface", "user experience",
            "product design", "figma", "wireframe", "wireframing", "prototype",
            "prototyping", "design system", "user research", "usability",
            "interaction design", "visual design", "design portfolio", "case study"
        ],
        "subdomains": ["User Experience Research", "Interface Design", "Design Systems", "Product Strategy"],
        "desired_expert_type": "Principal UI/UX & Product Design Lead",
        "related_expert_tags": ["ui", "ux", "figma", "product design", "design systems", "wireframing", "interaction design"]
    },
    "cybersecurity": {
        "display_name": "Cybersecurity & Information Assurance",
        "keywords": [
            "cybersecurity", "cyber security", "ethical hacking", "hacker", "hacking",
            "penetration testing", "pen test", "infosec", "information security",
            "network security", "vulnerability", "malware", "soc", "siem", "cissp",
            "oscp", "ceh", "cryptography", "zero trust", "threat modeling", "incident response"
        ],
        "subdomains": ["Offensive Security", "Defensive Engineering", "Zero Trust Architecture", "Security Auditing"],
        "desired_expert_type": "Cybersecurity & Information Assurance Specialist",
        "related_expert_tags": ["cybersecurity", "ethical hacking", "infosec", "penetration testing", "security", "zero trust"]
    },
    "ai_ml_data": {
        "display_name": "Artificial Intelligence, Machine Learning & Data Science",
        "keywords": [
            "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
            "neural network", "neural networks", "transformer", "transformers", "llm",
            "llms", "genai", "generative ai", "nlp", "computer vision", "pytorch",
            "tensorflow", "data science", "data scientist", "data analysis", "analytics",
            "langchain", "rag", "vector database", "hugging face", "model training", "mlops"
        ],
        "subdomains": ["Generative AI & LLMs", "Deep Learning Systems", "MLOps & Model Deployment", "Data Analytics"],
        "desired_expert_type": "AI Strategy, Machine Learning & Data Architect",
        "related_expert_tags": ["ai", "machine learning", "ml", "deep learning", "data science", "llms", "rag", "pytorch"]
    },
    "software_engineering": {
        "display_name": "Software Engineering & Full-Stack Development",
        "keywords": [
            "software engineer", "software engineering", "developer", "programmer",
            "full stack", "fullstack", "frontend", "front end", "backend", "back end",
            "web development", "web developer", "react", "nextjs", "javascript",
            "typescript", "node", "nodejs", "python", "java", "golang", "c++",
            "api", "rest api", "graphql", "system design", "microservices", "sql",
            "postgresql", "mongodb", "database design"
        ],
        "subdomains": ["Frontend Architecture", "Backend & APIs", "Distributed Systems", "Full-Stack Development"],
        "desired_expert_type": "Principal Full-Stack & Systems Architect",
        "related_expert_tags": ["software engineering", "react", "typescript", "full-stack", "backend", "fastapi", "python"]
    },
    "cloud_devops": {
        "display_name": "Cloud Computing & DevOps",
        "keywords": [
            "cloud", "aws", "azure", "gcp", "google cloud", "devops", "kubernetes",
            "k8s", "docker", "container", "containers", "ci/cd", "terraform",
            "infrastructure as code", "ansible", "cloud architect", "site reliability", "sre"
        ],
        "subdomains": ["Cloud Infrastructure", "Kubernetes Orchestration", "CI/CD Automation", "Site Reliability"],
        "desired_expert_type": "Cloud Infrastructure & DevOps Lead",
        "related_expert_tags": ["cloud", "aws", "kubernetes", "docker", "devops", "systems"]
    },
    "business_finance": {
        "display_name": "Business, Finance & Entrepreneurship",
        "keywords": [
            "business", "startup", "startups", "founder", "entrepreneur", "entrepreneurship",
            "venture capital", "vc", "pitch deck", "funding", "finance", "financial",
            "marketing", "growth hacking", "sales", "product manager", "product management",
            "mba", "investment", "accounting"
        ],
        "subdomains": ["Startup Strategy", "Product Management", "Financial Analysis", "Growth & Marketing"],
        "desired_expert_type": "Startup Founder & Strategic Business Mentor",
        "related_expert_tags": ["business", "startup", "finance", "marketing", "product management", "entrepreneurship"]
    },
    "career_growth": {
        "display_name": "Career Growth & Transition Advisory",
        "keywords": [
            "career guidance", "career transition", "career switch", "resume", "cv",
            "interview", "interview preparation", "mock interview", "salary negotiation",
            "job search", "linkedin profile", "promotion", "career advice"
        ],
        "subdomains": ["Resume & Portfolio Review", "Interview Strategy", "Career Transitions", "Leadership"],
        "desired_expert_type": "Executive Career Coach & Transition Advisor",
        "related_expert_tags": ["career", "mentorship", "interview", "resume", "leadership"]
    }
}


def extract_user_intent(query: str) -> dict[str, Any]:
    """
    Analyzes user message to determine exact goal, career domain, and expert requirements.
    Ensures clear, reliable domain categorization without confusing topic with career goal.
    """
    if not query or not query.strip():
        return {
            "intent": "general_inquiry",
            "goal": "General platform inquiry",
            "domain": "general",
            "domain_display": "General Professional Advisory",
            "subdomains": ["Career Exploration"],
            "keywords": [],
            "desired_expert_type": "General Professional Mentor"
        }

    q_lower = query.lower()
    cleaned = re.sub(r"[^\w\s]", " ", q_lower)
    words = set(cleaned.split())

    # 1. Score each domain by keyword and phrase matches
    domain_scores: dict[str, float] = {}
    for domain_key, info in DOMAIN_TAXONOMY.items():
        score = 0.0
        for kw in info["keywords"]:
            if " " in kw:
                # Multi-word phrase match (higher weight)
                if kw in q_lower:
                    score += 3.0
            else:
                # Exact word match
                if kw in words:
                    score += 2.0
                elif len(kw) >= 4 and kw in q_lower:
                    score += 1.0

        if score > 0:
            domain_scores[domain_key] = score

    # 2. Determine Primary Domain
    if domain_scores:
        # Sort domains by highest match score
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        primary_domain = sorted_domains[0][0]
        domain_info = DOMAIN_TAXONOMY[primary_domain]
    else:
        # Check for generic career or general inquiries
        primary_domain = "other"
        domain_info = {
            "display_name": "Specialized / Emerging Domain",
            "subdomains": ["Exploratory Guidance"],
            "desired_expert_type": "Domain Specialist",
            "related_expert_tags": []
        }

    # 3. Classify high-level intent type
    if any(k in q_lower for k in ["become", "start career", "career in", "study", "degree", "enter", "transition", "switch", "prepare for", "admissions"]):
        intent_type = "career_guidance"
    elif any(k in q_lower for k in ["how to", "how do i", "deploy", "build", "code", "architecture", "setup", "configure", "debug"]):
        intent_type = "technical_guidance"
    elif any(k in q_lower for k in ["learn", "master", "course", "tutorial", "roadmap", "syllabus", "books", "study"]):
        intent_type = "skill_development"
    else:
        intent_type = "consultation_advisory"

    # 4. Extract clean goal statement
    goal = query.strip()
    for prefix in ["i want to ", "i wanna ", "how can i ", "how do i ", "can you tell me how to ", "help me "]:
        if q_lower.startswith(prefix):
            goal = query[len(prefix):].strip()
            break

    # Extract keywords present in query
    extracted_keywords = [
        kw for kw in domain_info.get("keywords", [])
        if kw in q_lower
    ]

    return {
        "intent": intent_type,
        "goal": goal.rstrip(".?!"),
        "domain": primary_domain,
        "domain_display": domain_info["display_name"],
        "subdomains": domain_info.get("subdomains", []),
        "keywords": extracted_keywords,
        "desired_expert_type": domain_info.get("desired_expert_type", "Specialist Mentor"),
        "related_expert_tags": domain_info.get("related_expert_tags", []),
        "match_confidence": domain_scores.get(primary_domain, 0.0)
    }


def is_expert_domain_compatible(expert_title: str, expert_skills: str, expert_bio: str, target_domain: str) -> tuple[bool, str]:
    """
    Strictly evaluates if an expert belongs to the target domain.
    Rejects cross-domain mismatches across all categories.
    Returns (is_compatible: bool, domain_reason: str).
    """
    if target_domain == "other":
        return False, "No verified specialist currently listed in this specific niche"

    domain_info = DOMAIN_TAXONOMY.get(target_domain)
    if not domain_info:
        return False, "Unrecognized domain category"

    expert_profile_text = f"{expert_title or ''} {expert_skills or ''} {expert_bio or ''}".lower()
    target_tags = domain_info.get("related_expert_tags", [])

    # Exact Domain Match Check
    matched_tags = [tag for tag in target_tags if tag in expert_profile_text]
    if matched_tags:
        return True, f"Specialist in {domain_info['display_name']} ({', '.join(matched_tags[:2]).title()})"

    # Domain specific rejections
    if target_domain == "medicine":
        return False, "Not verified in Medicine or Healthcare"
    elif target_domain == "ui_ux_design":
        return False, "Not specialized in UI/UX or Product Design"
    elif target_domain == "cybersecurity":
        return False, "Not verified in Cybersecurity"
    elif target_domain == "ai_ml_data":
        return False, "Not verified in Artificial Intelligence or Data Science"
    elif target_domain == "software_engineering":
        return False, "Not verified in Software Engineering or Web Development"
    elif target_domain == "cloud_devops":
        return False, "Not verified in Cloud Computing or DevOps"
    elif target_domain == "business_finance":
        return False, "Not verified in Business, Finance or Entrepreneurship"

    return False, f"Not aligned with {domain_info['display_name']}"
