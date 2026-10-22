# Today I Learned
 
A running collection of short study notes and runnable code examples on **security, cloud, and backend engineering** topics. I use it as a review resource, and it doubles as a working example of a serverless AI pipeline on AWS.
 
> **Transparency note:** The notes and example scripts in this repo are **AI-generated** (Claude via Amazon Bedrock) from a topic list I curate. They are study material, not original research, so verify anything important against primary sources.
 
## What's inside
 
```
.
├── til/          # Short Markdown notes (200-350 words each)
└── examples/     # Self-contained, commented Python scripts (stdlib only)
```
 
- **`til/`**: each note has a problem statement, key concepts and technical details, and a practical takeaway or real-world gotcha.
- **`examples/`**: each script demonstrates one concept, with comments covering what the pattern does, when to use it, and best practices.
## Topics covered
 
| Area | Examples |
|------|----------|
| Application security | OWASP API Top 10, CSRF defenses, JWT validation flaws, OAuth 2.0 PKCE |
| Infrastructure and cloud | AWS IAM least privilege, Linux capabilities, Docker container escapes, Zero Trust |
| Detection and forensics | DNS exfiltration detection, Wireshark TCP reassembly, Merkle-tree log integrity |
| Backend engineering | Token bucket rate limiting, connection pool exhaustion, optimistic vs pessimistic locking, distributed tracing |
| Supply chain and memory safety | SLSA framework, Rust vs C allocators |
 
## How it works
 
A scheduled **AWS Lambda** function (Python 3.12) builds each entry:
 
1. Picks a topic from a curated list.
2. Calls **Claude on Amazon Bedrock** to generate either a Markdown note or a Python example.
3. Commits the result to this repo through the **GitHub Contents API**.
```
EventBridge schedule → Lambda → Amazon Bedrock (Claude) → GitHub API → this repo
```
 
**Tech:** Python · AWS Lambda · Amazon Bedrock · EventBridge · GitHub REST API · IAM
 
## Running the examples
 
Every script in `examples/` uses only the Python standard library:
 
```bash
python examples/<script-name>.py
```
 
## About
 
Maintained by [William Cantera](https://github.com/William-Cantera). Corrections and suggestions are welcome via issues.
