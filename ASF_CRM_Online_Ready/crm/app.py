
import os
import re
from pathlib import Path
from urllib.parse import quote
from datetime import date
import io

import pandas as pd
import altair as alt
import streamlit as st
from supabase import create_client

# ==================================================
# ASF DIGITAL SOLUTIONS CRM
# Application Logic
# Styling is maintained separately in style.css
# ==================================================

BASE_DIR = Path(__file__).parent

st.set_page_config(
    page_title="ASF Digital Solutions CRM",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CSS LOADER ----------------

def load_css():
    css_path = BASE_DIR / "style.css"

    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            "style.css file nahi mili. "
            "Please ensure both files are in the same folder."
        )

load_css()

# ---------------- CRM OPTIONS ----------------

CATEGORIES = [
    "Schools",
    "Colleges",
    "E-commerce",
    "Real Estate",
    "Restaurants",
    "Other",
]

STATUSES = [
    "New",
    "Contacted",
    "Interested",
    "Follow-up",
    "Converted",
    "Not Interested",
]

PRIORITIES = ["Hot", "Warm", "Cold"]

SERVICES = [
    "Website Development",
    "Mobile App Development",
    "School Management Software",
    "College Management Software",
    "E-commerce Software",
    "Fast-Food Management Software",
    "Social Media Marketing",
    "Lead Generation",
    "AI Chatbot & Automation",
    "Graphics Designing",
    "Training Courses",
    "Other",
]

LANGUAGES = [
    "English",
    "Urdu",
    "Roman Urdu",
    "Arabic",
    "Chinese",
    "French",
    "Spanish",
    "Punjabi",
    "Bengali",
    "Russian",
    "Portuguese",
    "German",
    "Turkish",
    "Hindi",
    "Persian",
]

LEAD_FIELDS = [
    "business_name",
    "category",
    "contact_person",
    "phone",
    "email",
    "city",
    "source_url",
    "status",
    "priority",
    "consent_to_marketing",
    "next_follow_up",
    "notes",
    "service_interest",
    "budget",
    "project_timeline",
    "preferred_language",
]

# ---------------- CONFIGURATION ----------------

def get_config(key, default=""):
    try:
        value = st.secrets.get(key, default)

        if value:
            return str(value).strip()

    except Exception:
        pass

    return os.getenv(key, default).strip()


# ---------------- SUPABASE ----------------

def connect_supabase():
    url = get_config("SUPABASE_URL")
    key = get_config("SUPABASE_KEY")

    if not url or not key:
        return None, "Supabase credentials configure nahi hain."

    try:
        client = create_client(url, key)
        return client, None

    except Exception as exc:
        return None, str(exc)


def get_all_leads(client):
    response = (
        client.table("leads")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


# ---------------- WHATSAPP ----------------

def normalize_phone(phone):
    digits = re.sub(r"\D", "", str(phone or ""))

    if digits.startswith("00"):
        digits = digits[2:]

    if digits.startswith("0") and len(digits) >= 10:
        digits = "92" + digits[1:]

    elif len(digits) == 10 and digits.startswith("3"):
        digits = "92" + digits

    return digits


def whatsapp_link(phone, message=""):
    phone = normalize_phone(phone)

    if not phone:
        return ""

    url = f"https://wa.me/{phone}"

    if message:
        url += "?text=" + quote(message)

    return url


def whatsapp_icon(size=22):
    """Official-style WhatsApp mark: green circle with white handset/chat shape."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
        viewBox="0 0 32 32" aria-hidden="true" focusable="false">
        <circle cx="16" cy="16" r="15" fill="#25D366"/>
        <path fill="#FFFFFF" d="M23.45 8.55A10.45 10.45 0 0 0 6.9 21.2l-1.4 5.1 5.25-1.38a10.45 10.45 0 0 0 12.7-16.37ZM16 24.45a8.4 8.4 0 0 1-4.28-1.17l-.31-.18-3.12.82.83-3.04-.2-.32A8.38 8.38 0 1 1 16 24.45Zm4.6-6.28c-.25-.13-1.5-.74-1.73-.82-.23-.08-.4-.13-.57.13-.17.25-.65.82-.8.99-.15.17-.3.19-.55.06-.25-.13-1.06-.39-2.02-1.24-.75-.67-1.25-1.5-1.4-1.75-.14-.25-.01-.39.11-.52.11-.11.25-.3.38-.44.13-.15.17-.25.25-.42.08-.17.04-.32-.02-.45-.06-.13-.57-1.38-.78-1.89-.2-.5-.41-.43-.57-.44h-.49c-.17 0-.45.06-.68.32-.23.25-.89.87-.89 2.12 0 1.25.91 2.46 1.04 2.63.13.17 1.79 2.73 4.33 3.83.6.26 1.07.42 1.43.54.6.19 1.15.16 1.58.1.48-.07 1.5-.62 1.71-1.21.21-.59.21-1.1.15-1.21-.06-.11-.23-.17-.48-.3Z"/>
    </svg>'''


def whatsapp_button(url, label="Open WhatsApp Chat", full_width=False):
    """Render a real WhatsApp-branded clickable link."""
    if not url:
        return
    width_style = "width:100%;" if full_width else "display:inline-flex;"
    st.markdown(
        f'''<a class="asf-whatsapp-button" href="{url}" target="_blank" rel="noopener noreferrer" style="{width_style}">
            {whatsapp_icon(23)}<span>{label}</span>
        </a>''',
        unsafe_allow_html=True,
    )


# ---------------- LOGIN ----------------

def check_login():
    password = get_config("APP_PASSWORD")

    if not password:
        st.session_state["authenticated"] = True
        return True

    if st.session_state.get("authenticated", False):
        return True

    st.markdown(
        """
        <div class="login-hero">
            <h1>ASF DIGITAL SOLUTIONS</h1>
            <p>BUSINESS • BRANDING • BEYOND</p>
            <h3>CRM WORKSPACE</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        entered_password = st.text_input(
            "Enter CRM Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    if submitted:
        if entered_password == password:
            st.session_state["authenticated"] = True
            st.rerun()

        else:
            st.error("Incorrect password.")

    return False


if not check_login():
    st.stop()


# ---------------- CONNECT DATABASE ----------------

client, connection_error = connect_supabase()

if client is None:
    st.title("ASF Digital Solutions CRM")

    st.error(connection_error)

    st.markdown(
        """
        ### Configure Supabase

        `.streamlit/secrets.toml` file mein apni configuration add karo.
        """
    )

    st.code(
        'SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"\n'
        'SUPABASE_KEY = "YOUR-SUPABASE-KEY"\n'
        'APP_PASSWORD = "YOUR-STRONG-PASSWORD"',
        language="toml",
    )

    st.stop()


# ---------------- LOAD LEADS ----------------

try:
    lead_records = get_all_leads(client)
    df = pd.DataFrame(lead_records)

except Exception as exc:
    st.title("ASF Digital Solutions CRM")
    st.error(f"Database error: {exc}")

    st.info(
        "Supabase mein 'leads' table aur required columns check karo."
    )

    st.stop()


if df.empty:
    df = pd.DataFrame(
        columns=["id", "created_at"] + LEAD_FIELDS
    )


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    logo_candidates = [
        "asf_logo.jpg",
        "asf-logo-original.jpg",
        "asf_logo.png",
        "asf-logo-original.png",
        "logo.png",
    ]

    for logo_name in logo_candidates:
        logo_path = BASE_DIR / logo_name

        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
            break

    st.markdown(
        '<div class="sidebar-brand">ASF DIGITAL SOLUTIONS</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-tagline">'
        'BUSINESS • BRANDING • BEYOND'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    page = st.radio(
        "MAIN MENU",
        [
            "Dashboard",
            "Add Lead",
            "Manage Leads",
            "Import / Export",
            "Setup Guide",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### 🟢 Quick WhatsApp")

    quick_phone = st.text_input(
        "Phone number",
        placeholder="03001234567",
        key="quick_phone",
    )

    if quick_phone.strip():

        quick_message = (
            "Assalam-o-Alaikum! We are contacting you "
            "from ASF Digital Solutions. "
            "How can we help with your business needs?"
        )

        quick_url = whatsapp_link(
            quick_phone,
            quick_message,
        )

        if quick_url:
            whatsapp_button(
                quick_url,
                "Open WhatsApp Chat",
                full_width=True,
            )

    st.divider()

    st.caption(
        "ASF Digital Solutions CRM\n\n"
        "Smart solutions. Meaningful growth."
    )


# ==================================================
# PAGE HEADER
# ==================================================

st.markdown(
    '<div class="topline">'
    'BUSINESS • BRANDING • BEYOND'
    '</div>',
    unsafe_allow_html=True,
)

st.title(page)

st.markdown(
    '<div class="page-subtitle">'
    'Manage your business leads and opportunities.'
    '</div>',
    unsafe_allow_html=True,
)


# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    total_leads = len(df)

    if "status" in df.columns:
        statuses = df["status"].fillna("New")
    else:
        statuses = pd.Series(dtype=str)

    if "priority" in df.columns:
        priorities = df["priority"].fillna("Warm")
    else:
        priorities = pd.Series(dtype=str)

    converted = int((statuses == "Converted").sum())
    hot_leads = int((priorities == "Hot").sum())

    if "next_follow_up" in df.columns and not df.empty:
        followup_dates = pd.to_datetime(
            df["next_follow_up"],
            errors="coerce",
        )

        due_followups = int(
            (
                followup_dates.notna()
                & (followup_dates.dt.date <= date.today())
                & (statuses != "Converted")
            ).sum()
        )
    else:
        due_followups = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Leads", total_leads)
    col2.metric("Hot Leads", hot_leads)
    col3.metric("Follow-ups Due", due_followups)
    col4.metric("Converted", converted)

    left, right = st.columns(2)

    with left:

        st.markdown(
            '<div class="section-heading">📊 Leads by Status</div>',
            unsafe_allow_html=True,
        )

        if total_leads and "status" in df.columns:
            status_chart = (
                df["status"].fillna("New").value_counts()
                .reindex(STATUSES, fill_value=0)
                .rename_axis("Status").reset_index(name="Leads")
            )
            status_vis = alt.Chart(status_chart).mark_bar(
                cornerRadiusTopLeft=5, cornerRadiusTopRight=5,
                color="#E8AD32", size=30
            ).encode(
                x=alt.X("Status:N", sort=STATUSES, axis=alt.Axis(labelAngle=-25, labelColor="#DCE5F2", title=None, tickColor="#274362", domainColor="#274362")),
                y=alt.Y("Leads:Q", axis=alt.Axis(labelColor="#DCE5F2", title=None, gridColor="#17304D", tickMinStep=1)),
                tooltip=[alt.Tooltip("Status:N"), alt.Tooltip("Leads:Q")]
            ).properties(height=245, background="#04162D").configure_view(stroke=None).configure_axis(
                labelFontSize=11, titleColor="#DCE5F2"
            )
            st.altair_chart(status_vis, use_container_width=True)

        else:
            st.info("Add leads to display the status chart.")

    with right:

        st.markdown(
            '<div class="section-heading">◉ Leads by Category</div>',
            unsafe_allow_html=True,
        )

        if total_leads and "category" in df.columns:
            category_chart = (
                df["category"].fillna("Other").value_counts()
                .reindex(CATEGORIES, fill_value=0)
                .rename_axis("Category").reset_index(name="Leads")
            )
            category_chart = category_chart[category_chart["Leads"] > 0]
            palette = ["#E8AD32", "#D99A27", "#9DB5D5", "#7AADE5", "#3D83C6", "#D6E0EE"]
            donut = alt.Chart(category_chart).mark_arc(
                innerRadius=65, outerRadius=105, stroke="#07172D", strokeWidth=2
            ).encode(
                theta=alt.Theta("Leads:Q", stack=True),
                color=alt.Color("Category:N", scale=alt.Scale(range=palette), legend=alt.Legend(orient="right", labelColor="#E6EDF7", title=None, labelLimit=180)),
                tooltip=[alt.Tooltip("Category:N"), alt.Tooltip("Leads:Q")]
            ).properties(height=265, background="#04162D").configure_view(stroke=None)
            st.altair_chart(donut, use_container_width=True)

        else:
            st.info("Add leads to display the category chart.")

    st.markdown(
        '<div class="section-heading">👥 Recent Leads</div>',
        unsafe_allow_html=True,
    )

    if total_leads:

        columns = [
            col for col in [
                "business_name",
                "category",
                "city",
                "phone",
                "status",
                "priority",
                "next_follow_up",
            ]
            if col in df.columns
        ]

        st.dataframe(
            df[columns].head(10),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "Abhi koi lead nahi. Apni first lead add karne ke liye "
            "'Add Lead' open karo."
        )


# ==================================================
# ADD LEAD
# ==================================================

elif page == "Add Lead":

    st.markdown(
        '<div class="section-heading">＋ Add New Business Lead</div>',
        unsafe_allow_html=True,
    )

    with st.form("add_lead_form", clear_on_submit=True):

        left, right = st.columns(2)

        with left:

            business_name = st.text_input(
                "Business / Organization Name *"
            )

            category = st.selectbox(
                "Category",
                CATEGORIES,
            )

            contact_person = st.text_input("Contact Person")

            phone = st.text_input("Phone / WhatsApp *")

            email = st.text_input("Email")

            city = st.text_input("City")

            source_url = st.text_input("Website / Source URL")

        with right:

            service_interest = st.selectbox(
                "Service Interest",
                SERVICES,
            )

            budget = st.text_input("Estimated Budget")

            project_timeline = st.selectbox(
                "Project Timeline",
                [
                    "Not specified",
                    "Urgent",
                    "Within 1 week",
                    "Within 1 month",
                    "1–3 months",
                    "3+ months",
                ],
            )

            preferred_language = st.selectbox(
                "Preferred Language",
                LANGUAGES,
            )

            status = st.selectbox("Lead Status", STATUSES)

            priority = st.selectbox("Priority", PRIORITIES)

            next_follow_up = st.date_input(
                "Next Follow-up Date",
                value=None,
            )

        consent = st.checkbox(
            "Marketing contact consent has been confirmed"
        )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Save Lead",
            use_container_width=True,
        )

    if submitted:

        if not business_name.strip():
            st.error("Business name is required.")

        elif not phone.strip():
            st.error("Phone number is required.")

        else:

            payload = {
                "business_name": business_name.strip(),
                "category": category,
                "contact_person": contact_person.strip(),
                "phone": phone.strip(),
                "email": email.strip(),
                "city": city.strip(),
                "source_url": source_url.strip(),
                "status": status,
                "priority": priority,
                "consent_to_marketing": consent,
                "next_follow_up": (
                    str(next_follow_up)
                    if next_follow_up
                    else None
                ),
                "notes": notes.strip(),
                "service_interest": service_interest,
                "budget": budget.strip(),
                "project_timeline": project_timeline,
                "preferred_language": preferred_language,
            }

            try:
                client.table("leads").insert(payload).execute()

                st.success("Lead successfully saved!")

                st.rerun()

            except Exception as exc:
                st.error(f"Could not save lead: {exc}")


# ==================================================
# MANAGE LEADS
# ==================================================

elif page == "Manage Leads":

    if df.empty:

        st.info("No leads available. Add a lead first.")

    else:

        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All"] + STATUSES,
            )

        with col2:
            priority_filter = st.selectbox(
                "Filter by Priority",
                ["All"] + PRIORITIES,
            )

        with col3:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All"] + CATEGORIES,
            )

        search = st.text_input(
            "🔎 Search business, contact, phone, email or city"
        )

        filtered = df.copy()

        if status_filter != "All" and "status" in filtered.columns:
            filtered = filtered[
                filtered["status"].fillna("New") == status_filter
            ]

        if priority_filter != "All" and "priority" in filtered.columns:
            filtered = filtered[
                filtered["priority"].fillna("Warm") == priority_filter
            ]

        if category_filter != "All" and "category" in filtered.columns:
            filtered = filtered[
                filtered["category"].fillna("Other") == category_filter
            ]

        if search.strip():

            search_columns = [
                col for col in [
                    "business_name",
                    "contact_person",
                    "phone",
                    "email",
                    "city",
                ]
                if col in filtered.columns
            ]

            mask = pd.Series(False, index=filtered.index)

            for col in search_columns:
                mask |= (
                    filtered[col]
                    .fillna("")
                    .astype(str)
                    .str.contains(
                        search.strip(),
                        case=False,
                        regex=False,
                    )
                )

            filtered = filtered[mask]

        st.caption(f"{len(filtered)} lead(s) found.")

        visible_columns = [
            col for col in [
                "business_name",
                "category",
                "contact_person",
                "phone",
                "email",
                "city",
                "status",
                "priority",
                "service_interest",
                "next_follow_up",
            ]
            if col in filtered.columns
        ]

        st.dataframe(
            filtered[visible_columns],
            use_container_width=True,
            hide_index=True,
        )

        if not filtered.empty:

            options = {}

            for _, row in filtered.iterrows():

                label = (
                    f"{row.get('business_name', 'Business')} | "
                    f"{row.get('phone', 'No phone')} | "
                    f"ID {row.get('id')}"
                )

                options[label] = row.to_dict()

            st.markdown(
                '<div class="section-heading">🟢 WhatsApp Contact</div>',
                unsafe_allow_html=True,
            )

            selected_label = st.selectbox(
                "Select lead",
                list(options.keys()),
            )

            selected = options[selected_label]

            message = (
                "Assalam-o-Alaikum! This is ASF Digital Solutions. "
                f"We would like to discuss how we can help "
                f"{selected.get('business_name', 'your business')} "
                "with digital solutions. Please let us know a "
                "convenient time."
            )

            wa_url = whatsapp_link(
                selected.get("phone", ""),
                message,
            )

            if wa_url:
                whatsapp_button(
                    wa_url,
                    "Open WhatsApp Chat",
                )
            else:
                st.warning("This lead has no valid phone number.")

            st.markdown(
                '<div class="section-heading">✎ Update Lead</div>',
                unsafe_allow_html=True,
            )

            lead_id = selected.get("id")

            old_status = selected.get("status")
            if old_status not in STATUSES:
                old_status = "New"

            old_priority = selected.get("priority")
            if old_priority not in PRIORITIES:
                old_priority = "Warm"

            with st.form("update_lead_form"):

                new_status = st.selectbox(
                    "Status",
                    STATUSES,
                    index=STATUSES.index(old_status),
                )

                new_priority = st.selectbox(
                    "Priority",
                    PRIORITIES,
                    index=PRIORITIES.index(old_priority),
                )

                new_followup = st.text_input(
                    "Next Follow-up (YYYY-MM-DD)",
                    value=str(selected.get("next_follow_up") or ""),
                )

                new_notes = st.text_area(
                    "Notes",
                    value=str(selected.get("notes") or ""),
                )

                update_clicked = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

            if update_clicked:

                followup_value = new_followup.strip() or None

                if followup_value:

                    try:
                        date.fromisoformat(followup_value)

                    except ValueError:
                        st.error(
                            "Date format YYYY-MM-DD use karo."
                        )
                        st.stop()

                try:

                    client.table("leads").update(
                        {
                            "status": new_status,
                            "priority": new_priority,
                            "next_follow_up": followup_value,
                            "notes": new_notes.strip(),
                        }
                    ).eq("id", lead_id).execute()

                    st.success("Lead updated successfully.")

                    st.rerun()

                except Exception as exc:
                    st.error(f"Update failed: {exc}")

            with st.expander("Delete Selected Lead"):

                st.warning(
                    "Delete karne se lead permanently remove ho jayegi."
                )

                confirm_delete = st.checkbox(
                    "I confirm permanent deletion",
                    key=f"delete_{lead_id}",
                )

                if st.button("Delete Lead"):

                    if not confirm_delete:
                        st.error("Please confirm deletion first.")

                    else:

                        try:

                            client.table("leads").delete().eq(
                                "id", lead_id
                            ).execute()

                            st.success("Lead deleted.")

                            st.rerun()

                        except Exception as exc:
                            st.error(f"Delete failed: {exc}")


# ==================================================
# IMPORT / EXPORT
# ==================================================

elif page == "Import / Export":

    st.markdown(
        '<div class="section-heading">⬇ Export Leads</div>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("No leads available to export.")

    else:

        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="asf_leads.csv",
            mime="text/csv",
        )

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl",
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Leads",
            )

        st.download_button(
            "Download Excel",
            data=excel_buffer.getvalue(),
            file_name="asf_leads.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.markdown(
        '<div class="section-heading">⬆ Import Leads</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "CSV/Excel file mein business_name aur phone columns zaroor hon."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV or Excel",
        type=["csv", "xlsx"],
    )

    if uploaded_file:

        try:

            if uploaded_file.name.lower().endswith(".csv"):

                incoming = pd.read_csv(
                    uploaded_file,
                    dtype=str,
                ).fillna("")

            else:

                incoming = pd.read_excel(
                    uploaded_file,
                    dtype=str,
                ).fillna("")

            st.dataframe(
                incoming.head(10),
                use_container_width=True,
            )

            if st.button("Import Rows to Supabase"):

                required = ["business_name", "phone"]

                missing = [
                    field for field in required
                    if field not in incoming.columns
                ]

                if missing:

                    st.error(
                        "Required columns missing: "
                        + ", ".join(missing)
                    )

                else:

                    records = []

                    for _, row in incoming.iterrows():

                        name = str(
                            row.get("business_name", "")
                        ).strip()

                        phone_value = str(
                            row.get("phone", "")
                        ).strip()

                        if not name or not phone_value:
                            continue

                        record = {}

                        for field in LEAD_FIELDS:

                            if field not in incoming.columns:
                                continue

                            value = str(
                                row.get(field, "")
                            ).strip()

                            if field == "consent_to_marketing":

                                record[field] = (
                                    value.lower()
                                    in ["true", "1", "yes", "y"]
                                )

                            elif field == "next_follow_up":

                                record[field] = value or None

                            else:

                                record[field] = value

                        record.setdefault("category", "Other")
                        record.setdefault("status", "New")
                        record.setdefault("priority", "Warm")
                        record.setdefault(
                            "preferred_language",
                            "English",
                        )

                        records.append(record)

                    if not records:

                        st.warning("No valid records found.")

                    else:

                        try:

                            for start in range(
                                0,
                                len(records),
                                100,
                            ):

                                batch = records[start:start + 100]

                                client.table("leads").insert(
                                    batch
                                ).execute()

                            st.success(
                                f"{len(records)} lead(s) imported."
                            )

                            st.rerun()

                        except Exception as exc:
                            st.error(f"Import failed: {exc}")

        except Exception as exc:
            st.error(f"File could not be read: {exc}")


# ==================================================
# SETUP GUIDE
# ==================================================

elif page == "Setup Guide":

    st.markdown(
        '<div class="section-heading">⚙ CRM Setup Guide</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
### Required Files

- `app.py` — CRM functionality
- `style.css` — complete visual styling
- `asf_logo.jpg` — original ASF logo
- `requirements.txt` — dependencies
- `.streamlit/secrets.toml` — private configuration

### Supabase Configuration

`.streamlit/secrets.toml` file mein ye settings add karo:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_KEY = "YOUR-SUPABASE-KEY"
APP_PASSWORD = "YOUR-STRONG-PASSWORD"
```

Placeholders ko apni credentials se replace karna.

**Important:** Private keys ko GitHub par upload mat karna.

### WhatsApp

WhatsApp buttons prepared chat open karte hain.
Message tum khud review karke send karogi.

### Database

Application tumhari existing Supabase `leads` table use karti hai.
"""

    )

    st.code(
        ", ".join(["id", "created_at"] + LEAD_FIELDS)
    )

    st.info(
        "Agar database missing-column error de, "
        "pehle existing table ka schema check karna."
    )


# ==================================================
# FOOTER
# ==================================================

st.markdown(
    """
    <div class="app-footer">
        <strong>ASF DIGITAL SOLUTIONS</strong>
        <span> | </span>
        BUSINESS • BRANDING • BEYOND
        <br>
        <small>Smart solutions. Meaningful growth.</small>
    </div>
    """,
    unsafe_allow_html=True,
)



