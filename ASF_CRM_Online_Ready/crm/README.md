# ASF Digital Solutions CRM — Online-ready MVP

Branded with the original uploaded ASF logo and navy/gold/black palette.

Features: dashboard metrics, lead categories/status/priority, follow-up dates, source URLs, consent field, search/filter, CSV import/export, Supabase cloud database connection, and a simple password gate.

## Local run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Online setup
1. Create a Supabase project.
2. In Supabase SQL Editor, create a `public.leads` table with columns matching the fields used by `app.py` (see Setup Guide in the app for SQL).
3. Upload this `crm` folder to a private GitHub repository.
4. Deploy `app.py` through Streamlit Community Cloud.
5. In Streamlit app Settings → Secrets, set `APP_PASSWORD`, `SUPABASE_URL`, and `SUPABASE_KEY`.
6. Keep the private key out of GitHub. Before storing real leads, configure proper individual user authentication and restrictive database policies.

This is an online-ready MVP, not a fully security-audited production CRM. It does not send WhatsApp messages automatically.
