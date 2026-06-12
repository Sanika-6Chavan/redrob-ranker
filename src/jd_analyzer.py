# src/jd_analyzer.py
# Job Description ko machine-readable format mein convert karo
# Yeh module system ko batata hai kya dekhna hai candidates mein

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# ── JD se extracted signals ──────────────────────────────────────────────────
# Yeh manually JD padhke define kiye hain
# Real system mein yeh LLM se extract ho sakta tha, 
# but hackathon constraints mein hum hardcode karenge

JD_SIGNALS = {
    
    # Must-have skills — yeh hone chahiye candidate mein
    "required_skills": [
        "embeddings", "sentence transformers", "vector database",
        "semantic search", "retrieval", "ranking", "python",
        "FAISS", "elasticsearch", "information retrieval",
        "NLP", "machine learning", "production ML",
        "NDCG", "evaluation", "A/B testing",
        "recommendation system", "search system"
    ],
    
    # Good-to-have skills — extra points
    "preferred_skills": [
        "fine-tuning", "LoRA", "QLoRA", "LLM",
        "RAG", "Pinecone", "Weaviate", "Qdrant",
        "learning to rank", "XGBoost", "transformer",
        "open source", "GitHub", "research"
    ],
    
    # Yeh titles wale candidates fit hain
    "good_titles": [
        "machine learning engineer", "ml engineer",
        "ai engineer", "data scientist", "nlp engineer",
        "search engineer", "applied scientist",
        "software engineer", "backend engineer",
        "research engineer", "senior engineer"
    ],
    
    # Yeh titles wale fit NAHI hain (red flags)
    "bad_titles": [
        "marketing manager", "hr manager", "sales",
        "business analyst", "project manager", "product manager",
        "accountant", "graphic designer", "content writer",
        "data analyst"  # analyst ≠ engineer
    ],
    
    # Yeh companies bad fit hain (pure consulting)
    "disqualified_companies": [
        "tcs", "tata consultancy", "infosys", "wipro",
        "accenture", "cognizant", "capgemini", "hcl",
        "tech mahindra", "mphasis", "hexaware", "l&t infotech"
    ],
    
"good_industries": [
    "technology", "software", "internet", "saas",
    "artificial intelligence", "machine learning",
    "fintech", "edtech", "healthtech", "ecommerce"
],

    # Experience range
    "min_years": 4,
    "max_years": 12,
    "ideal_min": 5,
    "ideal_max": 9,
    
    # Location preferences
    "preferred_cities": ["pune", "noida", "delhi ncr", "gurgaon"],
    "acceptable_cities": ["hyderabad", "mumbai", "bangalore", 
                          "bengaluru", "chennai"],
    
    # Company type preferences
    "preferred_company_types": ["product", "startup", "saas", "ai"],
    "bad_company_types": ["consulting", "services", "outsourcing"],
}


def load_jd_text():
    """JD text file load karo"""
    try:
        with open(config.JD_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("⚠️  JD file not found, using embedded JD text")
        return get_embedded_jd()


def get_embedded_jd():
    """
    Backup JD text — agar file na mile toh yeh use karo.
    Yeh JD ka most important part capture karta hai embedding ke liye.
    """
    return """
    Senior AI Engineer role requiring production experience with 
    embeddings-based retrieval systems, vector databases, semantic search,
    ranking systems, NLP, machine learning in production environment.
    Must have Python expertise, evaluation framework design experience,
    NDCG MRR MAP metrics knowledge. Experience with sentence transformers,
    FAISS, Elasticsearch, Pinecone or similar vector databases.
    Product company background required, not pure consulting or research.
    Startup experience preferred, fast shipping mindset needed.
    Located in Pune or Noida India preferred, open to relocation.
    5 to 9 years experience in applied ML and AI at product companies.
    Must have shipped ranking or recommendation or search system to real users.
    """


def get_jd_signals():
    """JD signals dictionary return karo"""
    return JD_SIGNALS

# Alias - dono naam se access ho sake
def get_jd_text(): 
    return load_jd_text()

def get_jd_embedding_text():
    """
    Chota, keyword-dense JD text — sirf embedding ke liye.
    256 token limit ke andar fit hone ke liye design kiya hai.
    Sabse important requirements pehle.
    """
    return (
        "Senior AI Engineer at AI startup. Must have production experience "
        "with embeddings-based retrieval systems using sentence-transformers, "
        "OpenAI embeddings, BGE, or E5. Hands-on experience with vector databases "
        "and hybrid search: Pinecone, Weaviate, Qdrant, Milvus, FAISS, Elasticsearch, "
        "OpenSearch. Strong Python coding skills. Experience designing evaluation "
        "frameworks for ranking systems: NDCG, MRR, MAP, A/B testing, offline-online "
        "correlation. Shipped end-to-end ranking, search, or recommendation systems "
        "to real users at product companies. 5 to 9 years applied machine learning "
        "and AI experience, not pure research, not pure consulting like TCS Infosys "
        "Wipro Accenture. LLM fine-tuning LoRA QLoRA PEFT, learning to rank XGBoost, "
        "NLP information retrieval background preferred. Located in Pune or Noida "
        "India, open to relocation. Production deployment experience, not only "
        "architecture or research roles. Open to work, active candidates preferred."
    )