# Report Data Schema

Complete JSON schema for the PDF generator. Only read this file if you need schema details.

## Full Schema

```json
{
  "company_name": "string (required)",
  "source_url": "string (required)",
  "report_date": "string, e.g., 'January 20, 2026'",

  "executive_summary": "string, 3-5 sentences covering what the company does, who they serve, market position",

  "profile": {
    "name": "string",
    "industry": "string, e.g., 'AI/ML Platform', 'FinTech'",
    "headquarters": "string, e.g., 'San Francisco, CA'",
    "founded": "string, e.g., '2019'",
    "ceo": "string, name and title",
    "size": "string, e.g., '50-200 employees'",
    "website": "string, URL",
    "funding": "string, e.g., '$50M Series B (2024)'"
  },

  "products": {
    "offerings": [
      {
        "name": "string, product name",
        "description": "string, what it does and value"
      }
    ],
    "differentiators": ["string array of unique selling points"],
    "tech_stack": {
      "Core": "string",
      "Cloud": "string",
      "AI/ML": "string"
    }
  },

  "target_market": {
    "segments": "string, description of primary customer segments",
    "verticals": ["string array of industries served"],
    "personas": [
      {
        "title": "string, e.g., 'VP of Engineering'",
        "description": "string, their needs and why they buy"
      }
    ],
    "business_model": "string, how they make money"
  },

  "use_cases": [
    {
      "title": "string, use case name",
      "description": "string, problem solved and outcomes"
    }
  ],

  "competitors": [
    {
      "name": "string",
      "strengths": "string",
      "differentiation": "string, how target company is different"
    }
  ],

  "competitive_positioning": "string, summary of market position",

  "industry": {
    "trends": ["string array of market trends"],
    "opportunities": ["string array of growth opportunities"],
    "challenges": ["string array of industry challenges"]
  },

  "developments": [
    {
      "date": "string, e.g., 'Dec 2024'",
      "title": "string, headline",
      "description": "string, details and significance"
    }
  ],

  "lead_gen": {
    "keywords": {
      "primary": ["string array, service keywords"],
      "vertical": ["string array, industry keywords"],
      "technology": ["string array, tech keywords"],
      "pain_point": ["string array, problem keywords"]
    },
    "outreach_angles": [
      {
        "title": "string, angle name",
        "description": "string, talking points"
      }
    ],
    "partnership_targets": [
      {
        "name": "string, partner type or name",
        "rationale": "string, why this partnership"
      }
    ]
  },

  "info_gaps": ["string array of unavailable information"]
}
```

## Example

```json
{
  "company_name": "Acme AI",
  "source_url": "https://acme.ai",
  "report_date": "January 20, 2026",
  "executive_summary": "Acme AI provides enterprise MLOps solutions that simplify model deployment and monitoring. They serve mid-market and enterprise companies in financial services and healthcare, with a strong focus on compliance and security. Founded in 2020, they've raised $75M and compete primarily with DataRobot and MLflow.",
  "profile": {
    "name": "Acme AI",
    "industry": "AI/ML Platform",
    "headquarters": "San Francisco, CA",
    "founded": "2020",
    "ceo": "Jane Smith, CEO & Co-founder",
    "size": "100-250 employees",
    "website": "https://acme.ai",
    "funding": "$75M Series B (Oct 2024)"
  },
  "products": {
    "offerings": [
      {
        "name": "Acme Deploy",
        "description": "One-click model deployment with automatic scaling and A/B testing"
      },
      {
        "name": "Acme Monitor",
        "description": "Real-time model performance tracking with drift detection"
      }
    ],
    "differentiators": [
      "HIPAA and SOC2 compliant out of the box",
      "50% faster deployment than competitors",
      "No-code interface for business users"
    ],
    "tech_stack": {
      "Core": "Python, Kubernetes",
      "Cloud": "AWS, GCP, Azure",
      "AI/ML": "PyTorch, TensorFlow, scikit-learn"
    }
  },
  "target_market": {
    "segments": "Mid-market and enterprise companies with existing data science teams looking to operationalize ML models",
    "verticals": ["Financial Services", "Healthcare", "Insurance", "Retail"],
    "personas": [
      {
        "title": "VP of Data Science",
        "description": "Needs to scale ML operations and demonstrate ROI to leadership"
      },
      {
        "title": "ML Engineer",
        "description": "Wants to reduce deployment friction and focus on model development"
      }
    ],
    "business_model": "SaaS subscription based on model deployments and API calls. Enterprise contracts start at $100K/year."
  },
  "use_cases": [
    {
      "title": "Fraud Detection at Scale",
      "description": "Financial services companies use Acme to deploy real-time fraud models, reducing false positives by 40% while maintaining sub-100ms latency."
    },
    {
      "title": "Healthcare Risk Stratification",
      "description": "Health insurers deploy patient risk models with full HIPAA compliance, enabling proactive care management."
    }
  ],
  "competitors": [
    {
      "name": "DataRobot",
      "strengths": "End-to-end AutoML, large customer base",
      "differentiation": "Acme is 50% cheaper and more flexible for custom models"
    },
    {
      "name": "MLflow",
      "strengths": "Open source, developer-friendly",
      "differentiation": "Acme provides enterprise support and compliance features"
    }
  ],
  "competitive_positioning": "Positioned as the enterprise-ready alternative to open source MLOps, with a focus on regulated industries.",
  "industry": {
    "trends": [
      "Increasing ML model complexity requires better tooling",
      "Regulatory pressure driving demand for model explainability"
    ],
    "opportunities": [
      "Expansion into European market with GDPR compliance",
      "Generative AI deployment tools"
    ],
    "challenges": [
      "Competition from cloud provider native tools",
      "Economic uncertainty affecting enterprise budgets"
    ]
  },
  "developments": [
    {
      "date": "Oct 2024",
      "title": "$75M Series B Funding",
      "description": "Led by Sequoia Capital to accelerate product development and international expansion"
    },
    {
      "date": "Aug 2024",
      "title": "Partnership with AWS",
      "description": "Available on AWS Marketplace, enabling faster enterprise procurement"
    }
  ],
  "lead_gen": {
    "keywords": {
      "primary": ["MLOps platform", "model deployment", "ML monitoring"],
      "vertical": ["healthcare AI compliance", "financial services ML"],
      "technology": ["Kubernetes ML", "PyTorch deployment"],
      "pain_point": ["ML model deployment challenges", "AI governance"]
    },
    "outreach_angles": [
      {
        "title": "Compliance-First Approach",
        "description": "Lead with HIPAA/SOC2 compliance for regulated industries"
      },
      {
        "title": "Cost Reduction",
        "description": "Highlight 50% cost savings vs DataRobot with comparable features"
      }
    ],
    "partnership_targets": [
      {
        "name": "Consulting Firms",
        "rationale": "Deloitte, Accenture have large AI practices needing deployment tools"
      }
    ]
  },
  "info_gaps": [
    "Exact customer count",
    "Revenue figures",
    "Employee breakdown by department"
  ]
}
```
