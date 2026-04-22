1. Connection string
Copy the connection details for your database.
Details:
Shared Pooler
Only use on a IPv4 networkSession pooler connections are IPv4 proxied for free.
Use Direct Connection if connecting via an IPv6 network.
host:aws-1-us-east-2.pooler.supabase.com
port:5432
database:postgres
user:postgres.oblpspanwdmuikhhqnns
Code:
File: Code
```
postgresql://postgres.oblpspanwdmuikhhqnns:[YOUR-PASSWORD]@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

2. Install Agent Skills (Optional)
Agent Skills give AI coding tools ready-made instructions, scripts, and resources for working with Supabase more accurately and efficiently.
Details:
npx skills add supabase/agent-skills
Code:
File: Code
```
npx skills add supabase/agent-skills
```
