import json
import csv
from groq import Groq

# --- Configuration ---
GROQ_API_KEY = "your api key"
client = Groq(api_key=GROQ_API_KEY)

# --- Load all datasets ---
def load_data():
    docs = {}

    with open("data/employees.csv") as f:
        docs["employees.csv"] = list(csv.DictReader(f))

    with open("data/audit_log.json") as f:
        docs["audit_log.json"] = json.load(f)

    with open("data/policy.txt") as f:
        docs["policy.txt"] = f.read()

    return docs

# --- Load RBAC ---
def load_rbac():
    with open("data/access_control.json") as f:
        data = json.load(f)
    return data["roles"], data["users"]

# --- Get allowed sources for a role ---
def get_allowed_sources(role, rbac_roles, all_docs):
    allowed = rbac_roles.get(role, [])
    if "*" in allowed:
        return list(all_docs.keys())
    return allowed

# --- Retrieve relevant context ---
def retrieve(query, allowed_sources, docs):
    context_parts = []
    query_lower = query.lower()

    for source in allowed_sources:
        data = docs.get(source)
        if not data:
            continue

        if isinstance(data, str):
            if any(word in data.lower() for word in query_lower.split()):
                context_parts.append(f"[Source: {source}]\n{data[:800]}")

        elif isinstance(data, list):
            relevant = [
                row for row in data
                if any(word in str(row).lower() for word in query_lower.split())
            ]
            if not relevant:
                relevant = data
            if relevant:
                context_parts.append(f"[Source: {source}]\n{json.dumps(relevant[:5], indent=2)}")

    if not context_parts:
        for source in allowed_sources:
            data = docs.get(source)
            if isinstance(data, str):
                context_parts.append(f"[Source: {source}]\n{data[:500]}")
            elif isinstance(data, list):
                context_parts.append(f"[Source: {source}]\n{json.dumps(data[:3], indent=2)}")

    return context_parts

# --- Generate answer using Groq ---
def generate_answer(query, context_parts, role):
    if not context_parts:
        return "No relevant data found in your permitted sources."

    context_text = "\n\n".join(context_parts)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a secure enterprise assistant.
Answer ONLY using the provided context.
Always mention which source you used like [Source: filename].
If the answer is not in the context, say 'This information is not available in your permitted sources.'
Never make up information."""
            },
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion: {query}\n\nUser role: {role}"
            }
        ]
    )
    return response.choices[0].message.content

# --- Main RAG query function ---
def query_rag(user_query, username, docs, rbac_roles, rbac_users):
    role = rbac_users.get(username.lower(), None)
    if not role:
        return f"User '{username}' not found in the system."

    allowed = get_allowed_sources(role, rbac_roles, docs)
    print(f"\n[RBAC]      User: {username} | Role: {role}")
    print(f"[RBAC]      Allowed sources: {allowed}")

    context = retrieve(user_query, allowed, docs)
    print(f"[Retrieval] Found {len(context)} relevant source(s)")

    answer = generate_answer(user_query, context, role)
    return answer

# --- Interactive CLI ---
def main():
    print("Loading data...")
    docs = load_data()
    rbac_roles, rbac_users = load_rbac()
    print("Data loaded successfully!")

    print("\n========================================")
    print("   Enterprise RAG Intelligence System   ")
    print("========================================")
    print("Available users: john, sara, mike, priya, admin, lisa, tom, amy, raj, steve")
    print("Type 'quit' to exit\n")

    username = input("Enter your username: ").strip().lower()

    while True:
        query = input("\nAsk a question: ").strip()
        if query.lower() == "quit":
            print("Goodbye!")
            break

        print("\nProcessing...")
        answer = query_rag(query, username, docs, rbac_roles, rbac_users)
        print(f"\n Answer:\n{answer}")
        print("\n" + "-"*50)

if __name__ == "__main__":
    main()