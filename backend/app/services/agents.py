from datetime import datetime
from typing import Any
import re
import logging

from sqlalchemy.orm import Session

from app.models.expert import Expert
from app.models.chat_history import ChatHistory
from app.models.action_plan import ActionPlan
from app.models.booking import Booking

from app.services.llm_service import llm_service
from app.services.embeddings import get_text_response, get_embedding
from app.services.vector_store import query_expert_documents
from app.services.intent_service import (
    extract_user_intent,
    is_expert_domain_compatible,
    DOMAIN_TAXONOMY,
)

logger = logging.getLogger("expertverse.agents")


def _domain_specific_roadmap(intent_data: dict[str, Any], user_input: str) -> dict[str, Any]:
    """
    Generates an authentic, domain-tailored 4-phase strategic action roadmap
    reflecting real professional milestones for the extracted domain.
    """
    domain = intent_data.get("domain", "other")
    goal = intent_data.get("goal", user_input)

    if domain == "medicine":
        return {
            "phase_1": {
                "milestones": "Pre-medical foundational science mastery and entrance examination strategy.",
                "tasks": f"Target goal: {goal}. Master Physics, Chemistry, and Biology (PCB). Build high-yield test prep routines for entrance examinations (NEET UG / MCAT / UKCAT).",
                "next_steps": "Analyze previous year entrance papers, diagnose conceptual gaps in organic chemistry and human physiology, and set mock test benchmarks.",
            },
            "phase_2": {
                "milestones": "Pre-clinical medical sciences, anatomy, and physiological systems.",
                "tasks": "Complete rigorous academic coursework in Human Anatomy, Medical Physiology, and Biochemistry. Participate in laboratory dissections and histological slide evaluations.",
                "next_steps": "Review clinical case presentations and establish high-retention spaced-repetition flashcard decks (Anki) for pharmacology and pathology.",
            },
            "phase_3": {
                "milestones": "Clinical hospital postings, diagnostic acumen, and supervised clerkships.",
                "tasks": "Undertake clinical rotations across Internal Medicine, General Surgery, Pediatrics, Obstetrics, and Emergency Care. Learn bedside manner, patient history taking, and differential diagnosis.",
                "next_steps": "Shadow attending physicians, practice clinical procedural skills (IV access, suturing, vitals), and prepare for licensing board examinations.",
            },
            "phase_4": {
                "milestones": "Medical licensing, compulsory rotatory internship, and residency specialization.",
                "tasks": "Complete hospital housemanship/internship duties. Sit for licensing and postgraduate entrance examinations (NEET PG / USMLE Step 2 / PLAB). Apply for specialized residency programs.",
                "next_steps": "Book a 1-on-1 strategy session with a verified medical career mentor on ExpertVerse AI to review residency applications and clinical focus areas.",
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    elif domain == "ui_ux_design":
        return {
            "phase_1": {
                "milestones": "Design principles, visual ergonomics, and industry tooling proficiency.",
                "tasks": f"Target goal: {goal}. Master Figma auto-layout, components, variants, typography scales, color accessibility (WCAG), and responsive grid systems.",
                "next_steps": "Reverse-engineer 3 top-tier mobile apps in Figma to understand spacing tokens and design system hierarchies.",
            },
            "phase_2": {
                "milestones": "User research methodologies, empathy mapping, and information architecture.",
                "tasks": "Conduct user interviews, synthesize affinity diagrams, create detailed user personas, and map out friction-free user journeys and site architectures.",
                "next_steps": "Draft low-fidelity paper wireframes and user flow diagrams for a real-world product problem.",
            },
            "phase_3": {
                "milestones": "Interactive prototyping, micro-interactions, and usability testing.",
                "tasks": "Convert wireframes into clickable high-fidelity interactive prototypes. Conduct structured usability tests with 5 target users and document heuristic evaluation findings.",
                "next_steps": "Iterate on user feedback and finalize design system component tokens in Figma.",
            },
            "phase_4": {
                "milestones": "Comprehensive product case study, portfolio defense, and design reviews.",
                "tasks": "Document the end-to-end design story: problem framing, data-driven decisions, visual iterations, and measurable product outcomes. Publish a polished portfolio.",
                "next_steps": "Schedule a portfolio critique session with a verified UI/UX design lead on ExpertVerse AI.",
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    elif domain == "cybersecurity":
        return {
            "phase_1": {
                "milestones": "Networking protocols, Linux architecture, and core security fundamentals.",
                "tasks": f"Target goal: {goal}. Master the TCP/IP stack, DNS, routing, firewalls, Linux command line, bash scripting, and the CIA triad principles.",
                "next_steps": "Set up a local virtualized security lab (VirtualBox/VMware) with Kali Linux and vulnerable target machines (Metasploitable).",
            },
            "phase_2": {
                "milestones": "Vulnerability assessment, network analysis, and hands-on CTF challenges.",
                "tasks": "Learn port scanning (Nmap), packet analysis (Wireshark), web vulnerabilities (OWASP Top 10), and solve beginner-to-intermediate rooms on TryHackMe/HackTheBox.",
                "next_steps": "Document step-by-step writeups of solved challenges to develop structured forensic methodologies.",
            },
            "phase_3": {
                "milestones": "Defensive engineering, SIEM operations, and industry credentials.",
                "tasks": "Configure SIEM platforms (Splunk/Elastic), inspect intrusion detection logs (Suricata/Snort), implement access controls, and prepare for industry certifications (Security+, CEH, or OSCP).",
                "next_steps": "Conduct simulated penetration tests or audit mock enterprise cloud infrastructure against CIS benchmarks.",
            },
            "phase_4": {
                "milestones": "Enterprise security defense, threat modeling, and professional transition.",
                "tasks": "Implement Zero Trust access patterns, automated vulnerability scanning in CI/CD, and practice incident response simulations.",
                "next_steps": "Book a technical design and mock security interview session with a verified cybersecurity specialist on ExpertVerse AI.",
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    elif domain == "ai_ml_data":
        return {
            "phase_1": {
                "milestones": "Mathematical foundations, Python data stacks, and exploratory analysis.",
                "tasks": f"Target goal: {goal}. Review Linear Algebra, Multivariate Calculus, Probability & Statistics. Master Python, NumPy, Pandas, and Matplotlib.",
                "next_steps": "Complete 2 exploratory data analysis (EDA) projects on real-world tabular datasets and publish clear statistical findings.",
            },
            "phase_2": {
                "milestones": "Classical machine learning, feature engineering, and rigorous validation.",
                "tasks": "Implement supervised and unsupervised algorithms (linear/logistic regression, random forests, gradient boosting, k-means). Master cross-validation, regularization, and ROC-AUC metrics.",
                "next_steps": "Build and evaluate end-to-end predictive pipelines using Scikit-Learn with zero data leakage.",
            },
            "phase_3": {
                "milestones": "Deep learning architectures, neural networks, and modern transformers.",
                "tasks": "Master PyTorch/TensorFlow fundamentals, backpropagation, CNNs for vision, and transformer attention mechanisms (Hugging Face) for NLP and Generative AI.",
                "next_steps": "Fine-tune an open-weights LLM or implement a Retrieval-Augmented Generation (RAG) pipeline with vector embeddings.",
            },
            "phase_4": {
                "milestones": "Production MLOps, model deployment, latency optimization, and governance.",
                "tasks": "Containerize models with Docker, deploy high-throughput inference APIs with FastAPI/vLLM, implement model monitoring (MLflow), and conduct fairness audits.",
                "next_steps": "Book a 1-on-1 architecture review session with a verified AI/ML specialist on ExpertVerse AI.",
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    elif domain == "software_engineering":
        return {
            "phase_1": {
                "milestones": "Core programming paradigms, algorithms, and version control discipline.",
                "tasks": f"Target goal: {goal}. Master data structures, algorithmic complexity (Big-O), clean code principles, and collaborative Git branching workflows.",
                "next_steps": "Implement 30 intermediate algorithmic challenges and push clean, tested implementations to GitHub.",
            },
            "phase_2": {
                "milestones": "Full-stack framework proficiency, RESTful APIs, and database modeling.",
                "tasks": "Build responsive frontend interfaces with React/TypeScript and integrate them with modular backend services (FastAPI/Node) and relational databases (PostgreSQL).",
                "next_steps": "Write automated unit and integration tests (pytest/vitest) covering core API business logic.",
            },
            "phase_3": {
                "milestones": "Production-grade cloud architecture, authentication, and CI/CD pipelines.",
                "tasks": "Implement secure authentication (OAuth/JWT, RBAC), containerize with Docker, configure automated CI/CD deployment pipelines, and configure production monitoring.",
                "next_steps": "Deploy a live production full-stack application with real users and automated error reporting.",
            },
            "phase_4": {
                "milestones": "System design mastery, microservices scalability, and engineering leadership.",
                "tasks": "Study high-scale architectural patterns: database sharding, caching strategies (Redis), message queues (Kafka/RabbitMQ), and distributed consensus.",
                "next_steps": "Book an architectural mock interview session with a verified Principal Engineer on ExpertVerse AI.",
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    else:
        # Generic & Emerging domains (Business, Career, Science)
        return {
            "phase_1": {
                "milestones": "Goal deconstruction, prerequisite mapping, and foundational competencies.",
                "tasks": f"Clarify target objective: {goal}. Audit required skills and curate structured study materials.",
                "next_steps": "Establish daily deliberate practice routines and track weekly milestone progress.",
            },
            "phase_2": {
                "milestones": "Applied domain practice and guided intermediate execution.",
                "tasks": "Engage in hands-on practical exercises, case study evaluations, and solve real-world problem sets in the target domain.",
                "next_steps": "Solicit feedback from industry peers to eliminate conceptual blind spots.",
            },
            "phase_3": {
                "milestones": "Independent project synthesis and tangible proof of work.",
                "tasks": "Develop and document an end-to-end milestone deliverable demonstrating depth of domain competence.",
                "next_steps": "Publish your project or findings publicly for community and mentor review.",
            },
            "phase_4": {
                "milestones": "Professional positioning, mentorship review, and industry advancement.",
                "tasks": "Prepare career assets, articulate your problem-solving narrative, and connect with domain leaders.",
                "next_steps": "Schedule an advisory consultation with a verified mentor on ExpertVerse AI.",
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }


def analyze_problem(db: Session, user_input: str) -> dict[str, Any]:
    """
    Analyzes the user's inquiry, extracting structured intent, domain, and goal.
    """
    intent_data = extract_user_intent(user_input)

    analysis_text = (
        f"Domain: {intent_data['domain_display']}\n"
        f"Goal: {intent_data['goal']}\n"
        f"Intent Type: {intent_data['intent'].replace('_', ' ').title()}\n"
        f"Subdomains: {', '.join(intent_data['subdomains'])}\n"
        f"Target Mentor Profile: {intent_data['desired_expert_type']}"
    )

    return {
        "analysis_text": analysis_text,
        "intent_data": intent_data,
    }


def match_experts(db: Session, user_input: str) -> list[dict[str, Any]]:
    """
    Ranks verified experts using multi-signal semantic relevance strictly gated by domain compatibility.
    1. Extracts query domain and goal
    2. Strictly rejects domain-incompatible experts (e.g. software engineer for medicine query)
    3. Ranks remaining eligible experts by vector similarity, skill matches, and credentials
    4. Returns empty list if no compatible verified experts exist (never fabricates or defaults)
    """
    intent_data = extract_user_intent(user_input)
    target_domain = intent_data["domain"]

    # ONLY approved and active experts are eligible
    verified_experts = (
        db.query(Expert)
        .filter(Expert.is_verified == True, Expert.is_active == True)
        .all()
    )
    if not verified_experts:
        return []

    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can", "could", "did", "do",
        "does", "doing", "down", "during", "each", "few", "for", "from", "further",
        "had", "has", "have", "having", "he", "her", "here", "him", "his", "how",
        "i", "if", "in", "into", "is", "it", "its", "me", "more", "most", "my",
        "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
        "other", "our", "out", "over", "own", "same", "she", "should", "so",
        "some", "such", "than", "that", "the", "their", "theirs", "them", "then",
        "there", "these", "they", "this", "those", "through", "to", "too", "under",
        "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
        "while", "who", "whom", "why", "with", "would", "you", "your", "yours",
        "want", "need", "help", "looking", "build", "learn", "please", "can"
    }

    raw_tokens = re.findall(r"\w+", user_input.lower())
    tokens = {t for t in raw_tokens if len(t) > 1 and t not in STOPWORDS}
    query_emb = get_embedding(user_input)

    # 1. FAISS Document search
    doc_matches = query_expert_documents(user_input, top_k=5)
    doc_expert_scores = {}
    if isinstance(doc_matches, list):
        for match in doc_matches:
            meta = match.get("metadata", {})
            eid = meta.get("expert_id")
            score = match.get("score", 999.0)
            if eid:
                sim = max(0.0, 1.0 / (1.0 + float(score)))
                doc_expert_scores[eid] = max(doc_expert_scores.get(eid, 0.0), sim)

    scored_experts = []
    logger.info(f"Matching experts for query: '{user_input}' | Detected Domain: '{target_domain}'")

    for expert in verified_experts:
        # STEP 1: Strict Domain Compatibility Gate
        is_compatible, domain_reason = is_expert_domain_compatible(
            expert.title,
            expert.skills,
            expert.bio,
            target_domain
        )

        if not is_compatible:
            # Strictly reject cross-domain expert recommendations
            logger.debug(f"Expert #{expert.id} '{expert.title}' rejected: {domain_reason}")
            continue

        relevance_score = 0.0
        reasons = []

        # Vector document similarity from FAISS
        if expert.id in doc_expert_scores:
            doc_sim = doc_expert_scores[expert.id]
            relevance_score += doc_sim * 4.0
            reasons.append("Published curriculum & technical documentation match")

        # Semantic profile embedding similarity (title + skills + bio)
        expert_doc = f"{expert.title or ''} {expert.skills or ''} {expert.bio or ''}"
        expert_emb = get_embedding(expert_doc)
        profile_sim = sum(a * b for a, b in zip(query_emb, expert_emb))
        if profile_sim > 0.10:
            relevance_score += profile_sim * 3.5

        # Exact skill keyword matches (excluding stopwords)
        expert_skills_raw = re.findall(r"\w+", (expert.skills or "").lower())
        expert_skills = {s for s in expert_skills_raw if len(s) > 1 and s not in STOPWORDS}
        matched_skills = tokens.intersection(expert_skills)
        if matched_skills:
            relevance_score += len(matched_skills) * 2.5
            top_skills_str = ", ".join(list(matched_skills)[:3]).title()
            reasons.append(f"Expertise in {top_skills_str}")

        # Title keyword matches (excluding stopwords)
        expert_title_words = {w for w in re.findall(r"\w+", (expert.title or "").lower()) if len(w) > 1 and w not in STOPWORDS}
        matched_title = tokens.intersection(expert_title_words)
        if matched_title:
            relevance_score += len(matched_title) * 2.0
            reasons.append(f"Role alignment: {expert.title}")

        # Domain specialist booster
        relevance_score += 3.0
        reasons.append(domain_reason)

        if relevance_score >= 1.5:
            relevance_reason = " • ".join(reasons) if reasons else f"Verified mentor with {expert.experience_years} years experience in {expert.title}."
            scored_experts.append({
                "expert": expert,
                "score": relevance_score,
                "relevance_reason": relevance_reason,
            })

    # Sort strictly by relevance score descending, then rating
    scored_experts.sort(key=lambda x: (x["score"], x["expert"].rating or 0.0), reverse=True)

    results = [
        {
            "id": item["expert"].id,
            "name": item["expert"].user.name if item["expert"].user else "Expert",
            "title": item["expert"].title,
            "company": item["expert"].company,
            "hourly_rate": item["expert"].hourly_rate,
            "experience_years": item["expert"].experience_years,
            "skills": [s.strip() for s in item["expert"].skills.split(",") if s.strip()] if item["expert"].skills else [],
            "rating": item["expert"].rating,
            "relevance_reason": item["relevance_reason"],
            "score": round(item["score"], 2),
        }
        for item in scored_experts[:5]
    ]

    logger.info(f"Query '{user_input}' matched {len(results)} verified experts.")
    return results


def generate_roadmap(db: Session, user_input: str) -> dict[str, Any]:
    """
    Generates a structured 4-phase roadmap tailored to the extracted domain and goal.
    """
    intent_data = extract_user_intent(user_input)
    prompt = f"""Create a 4-phase professional roadmap for: {user_input}
Domain: {intent_data['domain_display']}
Goal: {intent_data['goal']}
Return EXACTLY in this format:
Phase 1
Milestones: ...
Tasks: ...
Next Steps: ...

Phase 2
Milestones: ...
Tasks: ...
Next Steps: ...

Phase 3
Milestones: ...
Tasks: ...
Next Steps: ...

Phase 4
Milestones: ...
Tasks: ...
Next Steps: ...
Do not use markdown."""

    raw = get_text_response(prompt)
    if not raw or "temporarily unavailable" in raw.lower() or "fallback" in raw.lower():
        return _domain_specific_roadmap(intent_data, user_input)

    raw = raw.replace("**", "").replace("#", "").replace("\t", "")

    phases = {}
    for i in range(1, 5):
        phase_name = f"Phase {i}"
        if phase_name in raw:
            start = raw.find(phase_name)
            if i < 4 and f"Phase {i+1}" in raw:
                end = raw.find(f"Phase {i+1}")
                section = raw[start:end]
            else:
                section = raw[start:]

            milestones = ""
            tasks = ""
            next_steps = ""
            if "Milestones:" in section and "Tasks:" in section:
                milestones = section.split("Milestones:")[1].split("Tasks:")[0].strip()
            if "Tasks:" in section and "Next Steps:" in section:
                tasks = section.split("Tasks:")[1].split("Next Steps:")[0].strip()
            if "Next Steps:" in section:
                next_steps = section.split("Next Steps:")[1].strip()

            phases[f"phase_{i}"] = {
                "milestones": milestones,
                "tasks": tasks,
                "next_steps": next_steps
            }

    if not any(key.startswith("phase_") for key in phases):
        return _domain_specific_roadmap(intent_data, user_input)

    phases["generated_at"] = datetime.utcnow().isoformat() + "Z"
    return phases


def _generate_ethical_reasoner_response(
    user_input: str,
    analysis: dict[str, Any],
    matched_experts: list[dict[str, Any]],
    roadmap: dict[str, Any]
) -> str:
    """
    Synthesizes a structured, highly relevant, domain-specific, and ethically grounded
    response directly answering the user query across all fields.
    """
    intent_data = extract_user_intent(user_input)
    domain = intent_data.get("domain", "other")
    domain_display = intent_data.get("domain_display", "Professional Advisory")
    goal = intent_data.get("goal", user_input)

    # Expert Recommendations Section
    if matched_experts:
        expert_items = []
        for e in matched_experts[:3]:
            reason = e.get("relevance_reason", "Verified domain advisor")
            rate_str = f"₹{e.get('hourly_rate', 0)}/hr"
            expert_items.append(
                f"• **{e['name']}** — {e['title']} ({e['experience_years']} yrs exp, ★{e['rating']}) | Rate: {rate_str}\n"
                f"  ↳ *Relevance*: {reason}"
            )
        expert_summary_str = "\n\n".join(expert_items)
        mentorship_cta = "\n*You can book a 1-on-1 consultation session with any matched expert below to review your action plan.*"
    else:
        expert_summary_str = (
            f"**Notice**: While I can guide you through the pathway to **{goal}**, there are currently no verified "
            f"ExpertVerse mentors specialized in **{domain_display}** available in our public directory. "
            f"Our admissions and verification committee regularly reviews and onboards new accredited specialists in this field."
        )
        mentorship_cta = "\n*Stay tuned as newly verified experts in this specialization will appear in the Experts directory.*"

    # Domain Classification & Tailored Knowledge Synthesis
    if domain == "medicine":
        domain_title = "Medicine, Healthcare & Clinical Education"
        key_insights = (
            "- **Academic & Entrance Foundations**: The medical pathway requires rigorous mastery of Physics, Chemistry, and Biology (PCB), with focused preparation for standardized entrance exams (such as NEET UG in India, MCAT in the US, or UCAT in the UK).\n"
            "- **Pre-Clinical to Clinical Continuum**: Medical education advances through preclinical sciences (Anatomy, Physiology, Biochemistry), paraclinical disciplines (Pathology, Pharmacology, Microbiology), and extensive clinical ward postings.\n"
            "- **Bedside Training & Rotations**: Direct patient contact, clinical history elicitation, physical diagnosis, and procedural skills form the core of undergraduate hospital training (MBBS / MD)."
        )
        ethical_guidance = (
            "- **Primum Non Nocere (First, Do No Harm)**: Medical practice is rooted in ethical beneficence, non-maleficence, and uncompromised patient safety.\n"
            "- **Patient Confidentiality & Informed Consent**: Strict adherence to medical privacy and autonomous, fully informed patient decision-making.\n"
            "- **Evidence-Based Practice & Humility**: Continuous learning, reliance on peer-reviewed clinical guidelines, and recognizing the limits of one's clinical competence."
        )
    elif domain == "ui_ux_design":
        domain_title = "UI/UX & Product Design Engineering"
        key_insights = (
            "- **User-Centered Design**: Great design starts with rigorous user research, empathy mapping, and deeply understanding user pain points before opening visual design tools.\n"
            "- **Design Systems & Hierarchy**: Master typography scales, spacing tokens, color accessibility (WCAG 2.1 AA), and scalable component architectures in Figma.\n"
            "- **Case Study Narrative**: The best design portfolios articulate *why* decisions were made, demonstrating problem framing, iterative user testing, and measurable business impact."
        )
        ethical_guidance = (
            "- **Accessible & Inclusive Design**: Guarantee that digital products are usable by individuals with visual, motor, auditory, and cognitive impairments.\n"
            "- **Ethical UX vs. Dark Patterns**: Never employ manipulative psychological tricks (hidden fees, deceptive opt-outs, forced continuity) designed to trick users.\n"
            "- **Respect for User Attention**: Design interfaces that empower productivity rather than exploiting dopamine loops and addictive behavioral triggers."
        )
    elif domain == "cybersecurity":
        domain_title = "Cybersecurity & Information Assurance"
        key_insights = (
            "- **Defense-in-Depth**: Build layered defense architectures spanning network perimeter security, host hardening, identity access management, and endpoint detection.\n"
            "- **Offensive & Defensive Mastery**: Understanding attack vectors (OWASP Top 10, MITRE ATT&CK) is prerequisite to architecting resilient, zero-trust enterprise defenses.\n"
            "- **Hands-On Practical Auditing**: Complement theoretical certifications with verifiable CTF challenge completions, virtual lab configurations, and security audit writeups."
        )
        ethical_guidance = (
            "- **Strict Authorization & Scope**: Always operate within explicit, written legal frameworks and formal rules of engagement; never perform unauthorized security scans.\n"
            "- **Responsible Disclosure**: Report vulnerabilities privately to vendors and project owners following established coordinated vulnerability disclosure timelines.\n"
            "- **Proportional Defense**: Ensure security measures safeguard user safety without imposing unreasonable operational burdens that compromise usability."
        )
    elif domain == "ai_ml_data":
        domain_title = "Artificial Intelligence, Machine Learning & Data Science"
        key_insights = (
            "- **Mathematical Foundations**: Focus on core mathematics (linear algebra, multivariate calculus, probability, statistics) alongside hands-on proficiency in PyTorch, Scikit-Learn, and vector databases.\n"
            "- **Systems & MLOps**: Industry readiness requires building clean data pipelines, model quantization, containerization (Docker), latency optimization, and continuous evaluation in production.\n"
            "- **Retrieval-Augmented Generation (RAG)**: When architecting domain-specific assistants, prioritize clean chunking strategies, hybrid keyword/vector search, and guardrails against hallucinations."
        )
        ethical_guidance = (
            "- **Fairness & Bias Mitigation**: Proactively audit training datasets for demographic, linguistic, and historical bias prior to deployment.\n"
            "- **Data Privacy & Governance**: Never ingest sensitive user data or proprietary source materials into public model endpoints without encryption and explicit consent.\n"
            "- **Explainability & Transparency**: Provide observable decision paths, citation capabilities, and confidence metrics so users understand how outputs are generated."
        )
    elif domain == "software_engineering":
        domain_title = "Modern Full-Stack Software Engineering"
        key_insights = (
            "- **Type Safety & Maintainability**: Leverage modern TypeScript across both frontend and backend interfaces to establish robust contracts and eliminate entire classes of runtime defects.\n"
            "- **Architectural Separation**: Maintain clean boundaries between data access layers, business domains, and presentation components. Utilize RESTful or GraphQL paradigms with rigorous input validation.\n"
            "- **State & Performance**: Master asynchronous request states, client-side caching (e.g., React Query), lazy loading, and efficient rendering cycles."
        )
        ethical_guidance = (
            "- **Accessibility (a11y) as a Baseline**: Design interfaces compliant with WCAG 2.1 AA standards, ensuring assistive technologies and keyboard-only users have equitable access.\n"
            "- **Security-by-Design**: Enforce strict input sanitization, CSRF/CORS protections, rate limiting, and secure password hashing (Argon2 / bcrypt) to protect users from exploitation.\n"
            "- **User Data Rights**: Minimize data collection, implement straightforward consent mechanisms, and uphold consumer privacy principles in storage and deletion workflows."
        )
    elif domain == "cloud_devops":
        domain_title = "Cloud Infrastructure & DevOps Engineering"
        key_insights = (
            "- **Infrastructure as Code (IaC)**: Provision and manage cloud resources declaratively using Terraform or CloudFormation to ensure reproducibility and version-controlled environments.\n"
            "- **Container Orchestration**: Master Docker containerization and Kubernetes cluster management, focusing on pod autoscaling, health probes, and ingress controllers.\n"
            "- **CI/CD & Observability**: Automate deployment pipelines with GitHub Actions or GitLab CI, incorporating distributed tracing (OpenTelemetry) and structured metrics."
        )
        ethical_guidance = (
            "- **Resource Stewardship & Sustainability**: Optimize cloud compute and storage utilization to prevent unnecessary energy consumption and compute waste.\n"
            "- **Security Isolation**: Enforce principle of least privilege in IAM roles and maintain isolated virtual private clouds (VPCs) with private subnets."
        )
    elif domain == "business_finance":
        domain_title = "Entrepreneurship, Business Strategy & Finance"
        key_insights = (
            "- **Customer Problem Validation**: Validate genuine customer willingness-to-pay through qualitative user interviews before committing significant capital to product development.\n"
            "- **Unit Economics & Financial Modeling**: Understand customer acquisition cost (CAC), lifetime value (LTV), gross margin structure, and cash runway management.\n"
            "- **Go-to-Market (GTM) Strategy**: Develop repeatable distribution channels, whether through inbound content, strategic partnerships, or direct enterprise sales."
        )
        ethical_guidance = (
            "- **Transparency & Fair Dealing**: Represent financial figures, business performance, and product capabilities truthfully to investors, customers, and partners.\n"
            "- **Stakeholder Responsibility**: Balance financial returns with employee well-being, ethical labor practices, and sustainable long-term value creation."
        )
    else:
        domain_title = f"{domain_display} Exploration & Strategy"
        key_insights = (
            "- **Core Domain Principles**: Break complex career transitions into modular, verifiable milestones with clear measurable outcomes.\n"
            "- **Deliberate Practice**: Focus on high-leverage activities, practical problem-solving, and establishing tangible proof of work in your chosen field.\n"
            "- **Continuous Feedback**: Seek constructive critique from experienced practitioners to accelerate mastery and uncover blind spots."
        )
        ethical_guidance = (
            "- **Integrity & Authenticity**: Present your qualifications honestly, contribute constructively to peer communities, and uphold professional codes of ethics.\n"
            "- **Sustainable Professional Pacing**: Prioritize consistent deliberate practice over burnout-inducing cramming; cultivate long-term industry relationships grounded in mutual assistance."
        )

    response_parts = [
        f"### Strategic Assessment: {domain_title}\n",
        f"Thank you for reaching out. Based on your inquiry: *\"{user_input}\"*, here is an authentic, ethical, and structured plan designed to guide you toward measurable success.\n",
        "#### 1. Core Industry Insights & Best Practices",
        key_insights,
        "\n#### 2. Ethical, Responsible & Sustainable Principles",
        ethical_guidance,
        "\n#### 3. Immediate Action Plan",
        f"- **Phase 1 Priority**: {roadmap.get('phase_1', {}).get('tasks', 'Clarify baseline goals and establish core foundations.')}",
        f"- **Core Milestone**: {roadmap.get('phase_1', {}).get('milestones', 'Achieve baseline competencies.')}",
        f"- **Next Actionable Step**: {roadmap.get('phase_1', {}).get('next_steps', 'Begin focused daily practice.')}",
        f"\n#### 4. Accelerate Your Progress With 1-on-1 Mentorship in {domain_display}",
        f"Self-guided study is essential, but personalized feedback eliminates blind spots. Here are the verified advisors matching your specific domain:\n",
        expert_summary_str,
        mentorship_cta
    ]

    return "\n".join(response_parts)


def generate_conversational_response(
    db: Session,
    user_input: str,
    analysis: dict[str, Any],
    matched_experts: list[dict[str, Any]],
    roadmap: dict[str, Any]
) -> str:
    """
    Generates a personalized, insightful, and ethically grounded answer.
    Calls configured LLM (Groq, Gemini, Ollama) if available, or falls back to the
    integrated domain-adaptive ethical reasoning engine.
    """
    intent_data = extract_user_intent(user_input)
    experts_brief = ", ".join([f"{e['name']} ({e['title']})" for e in matched_experts[:3]]) if matched_experts else "No verified experts currently listed for this domain"

    prompt = f"""The user asked: "{user_input}"
Detected Domain: {intent_data['domain_display']}
Goal: {intent_data['goal']}
Analysis: {analysis.get('analysis_text', '')}
Matched Mentors: {experts_brief}

Provide an outstanding, highly articulate, clear, and ethically relevant response that:
1. Directly answers the user's inquiry with domain-accurate clarity and actionable depth.
2. Does NOT assume software engineering if the user is asking about medicine, design, business, or another domain.
3. Discusses ethical dimensions relevant to the specific domain.
4. Explains the proposed 4-phase roadmap and connects any supplied matched mentors (or explicitly notes if none are currently listed).
5. Concludes with practical immediate next steps.
Use clear Markdown headings and bullet points."""

    # Attempt LLM generation
    llm_output = llm_service.generate_text(prompt)
    if llm_output and len(llm_output.strip()) > 100 and "temporarily unavailable" not in llm_output.lower():
        return llm_output.strip()

    # Fallback to rich domain-adaptive reasoner
    return _generate_ethical_reasoner_response(user_input, analysis, matched_experts, roadmap)


def save_chat_history(
    db: Session,
    user_id: int,
    message: str,
    response_text: str
) -> ChatHistory:
    chat = ChatHistory(
        user_id=user_id,
        message=message,
        response=response_text
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def save_action_plan(
    db: Session,
    user_id: int,
    plan_json: str
) -> ActionPlan:
    plan = ActionPlan(
        user_id=user_id,
        plan_json=plan_json
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def create_booking_record(
    db: Session,
    user_id: int,
    expert_id: int,
    slot: datetime
) -> Booking:
    booking = Booking(
        user_id=user_id,
        expert_id=expert_id,
        slot=slot,
        status="confirmed"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking
