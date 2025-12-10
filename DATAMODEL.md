# Data Model

This data model is designed for **flexibility** (handling variety via JSONB) and **trust** (keeping AI suggestions distinct from user-verified truth).

We will use **PostgreSQL**. The superpower here is combining strict relational integrity (for users, IDs, timestamps) with unstructured flexibility (JSONB) for the diverse nature of legal contracts.

## I. The Extraction Spectrum (What we hunt for)

Before the database, we define the "Target Schema" for the AI. When a document hits the Triage stage, the AI attempts to extract every single one of these fields.

### 1. Core Metadata

* **Document Type:** (e.g., MSA, NDA, Invoice, Court Order, Insurance Policy).
* **Title:** A human-readable summary (e.g., "Office Lease - 2nd Floor").
* **Language:** (e.g., EN, DE, FR).

### 2. The "Who" (Counterparties)

* **Counterparty Name:** (e.g., "Acme Corp," "John Doe").
* **Counterparty Role:** (e.g., Landlord, Client, Plaintiff, Insurer).
* **Contact Details:** Extracted emails or physical addresses found in the header/footer.

### 3. The "When" (Temporal Logic)

* **Execution Date:** Date signed.
* **Effective Date:** Date obligations start.
* **Expiration Date:** Hard end date.
* **Auto-Renewal Logic:** Boolean (True/False) + Notice Period (e.g., "30 days before expiration").
* **Termination Notice:** How much warning is needed to quit?

### 4. The "How Much" (Liabilities & Economics)

* **Total Contract Value (TCV):** Fixed cap or total estimation.
* **Recurring Fees:** Amount + Frequency (e.g., "$5,000 / Monthly").
* **Payment Terms:** (e.g., "Net 30", "Due on Receipt").
* **Late Fees/Penalties:** Interest rates or fixed fees for delays.

### 5. The "What" (Clauses & Scope)

* **Scope Summary:** A 2-sentence summary of what is being exchanged.
* **Jurisdiction:** Which country/state laws apply (e.g., "State of Delaware").
* **Exclusivity/Non-Compete:** Boolean flags indicating restrictive covenants.

-----

## II. The Entity Relationship Strategy

We need a "Staging" approach. We do not write directly to the final `Matter` table from the AI. We write to a `Triage` table.

[Image of entity relationship diagram for legal document management system]

## III. Detailed Schema Definition (Pseudo-SQL)

Here is the structure. I have highlighted the **JSONB** columns where the variety lives.

### 1\. The Inbox & Triage (The "Waiting Room")

This captures the raw chaos before it becomes structured order.

```sql
TABLE inbox_items {
  id: uuid (PK)
  user_id: uuid (FK)
  
  -- The Raw Input
  file_url: string        -- Path to S3/Blob storage
  original_filename: string
  mime_type: string       -- pdf, jpeg, msg (email)
  ingestion_source: enum  -- 'email_forward', 'upload', 'mobile_scan'
  
  -- The State Machine
  status: enum            -- 'processing', 'ready_for_review', 'converted', 'rejected'
  
  -- The AI Brain Dump (Crucial)
  ai_extraction_payload: jsonb 
  -- This stores the COMPLETE AI guess. 
  -- If the user rejects the extraction, we keep this for retraining later.
  
  created_at: timestamp
}
```

### 2\. Matters (The Core Container)

Once an `inbox_item` is approved, it converts into (or attaches to) a `Matter`.

```sql
TABLE matters {
  id: uuid (PK)
  user_id: uuid (FK)
  
  -- Classification
  title: string           -- "Headquarters Lease"
  category: enum          -- 'contract', 'dispute', 'compliance', 'personal', 'insurance'
  status: enum            -- 'active', 'expired', 'terminated', 'dispute_ongoing'
  
  -- Key Dates (Indexed for fast dashboard queries)
  start_date: date
  end_date: date          -- Nullable (for indefinite contracts)
  
  -- The Variety Handler
  attributes: jsonb       
  /* Example for Lease: { "sq_ft": 500, "floor": 2, "landlord_email": "..." }
     Example for Car Insurance: { "vin": "123", "deductible": 500, "coverage_type": "comprehensive" }
  */
  
  -- The Narrative
  summary: text           -- AI generated executive summary
}
```

### 3\. Documents (The Evidence)

A Matter has many documents. The Lease (Matter) has the original PDF, the 2024 Amendment, and an angry letter (Documents).

```sql
TABLE documents {
  id: uuid (PK)
  matter_id: uuid (FK)    -- Which matter does this belong to?
  inbox_item_id: uuid     -- Traceability back to source
  
  title: string           -- "Signed Amendment v2"
  doc_type: enum          -- 'contract_original', 'amendment', 'invoice', 'correspondence'
  
  -- Search Capability
  full_text_content: text -- OCR output for simple search
  embedding: vector(1536) -- For Semantic Search ("The Oracle")
  
  created_at: timestamp
}
```

### 4\. Events & Deadlines (The Sentinel)

This table drives the dashboard and notifications.

```sql
TABLE events {
  id: uuid (PK)
  matter_id: uuid (FK)
  source_document_id: uuid (FK) -- Link to the doc that caused this event
  
  title: string           -- "Renewal Notice Deadline"
  due_date: timestamp
  
  event_type: enum        -- 'payment', 'expiry', 'notice_deadline', 'compliance_check'
  status: enum            -- 'upcoming', 'completed', 'dismissed', 'overdue'
  
  -- Verification
  is_ai_generated: boolean -- True if user hasn't manually confirmed it yet
  confidence_score: float  -- 0.0 to 1.0. High confidence = auto-approve?
}
```

### 5\. Liabilities (The Ledger)

Strict financial tracking.

```sql
TABLE liabilities {
  id: uuid (PK)
  matter_id: uuid (FK)
  
  title: string           -- "Monthly Rent"
  amount: decimal(12, 2)
  currency: string        -- 'USD', 'EUR'
  
  frequency: enum         -- 'one_time', 'monthly', 'quarterly', 'annually'
  
  -- Logic
  next_due_date: date
  auto_pay: boolean       -- Is this set to auto-pay in real life?
}
```

-----

## IV. Handling Variety in Practice

The key to your success is the `attributes` (JSONB) column in the `Matters` table. Here is how we handle the "Variety" you requested:

**Scenario A: A Software License (SaaS)**
We extract and store this in `attributes`:

```json
{
  "seats": 50,
  "overage_cost": "$10/user",
  "data_residency": "EU-Frankfurt",
  "sla_uptime": "99.9%"
}
```

**Scenario B: A Freelancer Contract**
We store this:

```json
{
  "hourly_rate": 150,
  "ip_assignment": "transfer_upon_payment",
  "deliverables": ["UI Design", "React Frontend"]
}
```

If we build a flexible JSON database but then hard-code `if (category == 'saas') { show('seats') }` in the React frontend, we have re-introduced rigidity. We have just moved the "schema migration" problem from the database to the frontend code. Every time we want to support a "Vehicle Lease," we would have to deploy new frontend code.

To solve this, we need a **Schema-Driven UI (SDUI)** approach. The backend should tell the frontend *what* to render, rather than the frontend guessing based on hard-coded rules.

Here is the refined architecture to bridge **Flexibility** (Backend) and **Usability** (Frontend).

### 1\. The Conflict: "Wild West" vs. "Rigid Rules"

* **The "Wild West" (Pure Flexibility):** We just dump the entire extracted JSON into a generic key-value table on the screen.
  * *Pros:* Zero maintenance. Handles any new contract type instantly.
  * *Cons:* Bad UX. It looks like a debug console. Users don't want to see "confidence\_score: 0.98" next to "Rent Amount." They want a curated view.
* **The "Rigid Rules" (Hard-coding):** We code specific components for `LeaseView`, `SaaSView`, `EmploymentView`.
  * *Pros:* Beautiful, tailored UX.
  * *Cons:* High maintenance. Adding "Boat Insurance" requires a code deploy.

### 2\. The Solution: "Dynamic Templates" (The Registry)

We introduce a **Template Registry** in the database (or a config file served by the API). This registry defines "blueprints" for known categories, but remains flexible enough to handle unknown ones.

#### The Data Model Refinement

We add a `SchemaDefinition` or `CategoryTemplate` concept.

```typescript
// Conceptual Typescript definition of the Template Registry

interface AttributeDefinition {
  key: string;           // e.g., "annual_deductible"
  label: string;         // e.g., "Annual Deductible"
  dataType: "currency" | "date" | "string" | "boolean" | "percentage";
  importance: "primary" | "secondary" | "hidden"; 
  // 'primary' = Show in the Header/Cards
  // 'secondary' = Show in the 'Details' tab
  // 'hidden' = Don't show (internal logic only)
}

interface CategoryTemplate {
  categorySlug: string;  // e.g., "insurance_policy"
  displayName: string;   // "Insurance Policy"
  attributes: AttributeDefinition[];
  fallbackStrategy: "show_all_others"; // If a key exists in data but not in template, show it anyway?
}
```

### 3\. How it works in Practice (The Flow)

**Step 1: The AI Extraction (The "Superset")**
The AI extracts *everything* it finds relevant into the JSONB column.

* *Data:* `{ "premium": 500, "policy_number": "X123", "weird_clause": "active_on_tuesdays" }`

**Step 2: The API Response**
When the frontend requests `GET /api/matters/123`, the backend sends two things:

1. **The Data:** The extraction payload.
2. **The Layout Hint:** The template for that category.

**Step 3: The Frontend "Smart Renderer"**
The Frontend does not contain `if (saas)` logic. It contains a generic **`AttributeRenderer`** component.

It iterates through the **Data**:

1. Does this key exist in the **Template**?
      * **Yes:** Render it using the rules (e.g., Format as Currency, Label as "Monthly Premium", place in "Primary" card).
      * **No (The "Catch-All"):** Render it in a generic "Additional Details" section at the bottom.

**This is the crucial fix.** It allows "Curated Views" for things we know (Leases, SaaS), but "Safe Fallbacks" for things we haven't anticipated yet (e.g., a "Horse Stabling Agreement"). The UI never breaks; it just degrades gracefully from "Tailored" to "Generic List."

### 4\. The "Category & Key" Registry

To make this concrete, here is the starting list of Categories and their specific Keys we should seed the system with.

| Category | Primary Keys (Header) | Secondary Keys (Details) |
| :--- | :--- | :--- |
| **General Contract** | `total_value`, `expiration_date` | `jurisdiction`, `governing_law` |
| **Real Estate Lease** | `monthly_rent`, `address`, `landlord_name` | `deposit_amount`, `square_footage`, `permitted_use`, `utilities_included` |
| **Employment/Contractor** | `salary/rate`, `start_date`, `role_title` | `notice_period`, `probation_period`, `ip_assignment`, `non_compete_duration` |
| **SaaS / Software** | `annual_cost`, `renewal_date`, `seat_count` | `data_residency`, `sla_uptime`, `support_level`, `payment_terms` |
| **Insurance Policy** | `premium_amount`, `policy_number`, `coverage_limit` | `deductible`, `insured_items`, `provider_contact`, `claim_deadline` |
| **Loan / Liability** | `principal_amount`, `interest_rate`, `next_payment` | `lender_name`, `maturity_date`, `collateral`, `early_repayment_fee` |
| **NDA / Confidentiality** | `parties`, `effective_date` | `confidentiality_duration`, `excluded_information`, `return_of_data_clause` |

### 5\. Critical Review: The "Square Peg" Problem

**The Problem:** What if a document is *technically* a "Lease" but contains a really weird field, like "Pet Rent: $50 per iguana"?

* **Old Approach (Strict):** The frontend ignores it because it's not in the hard-coded list.
* **New Approach (SDUI):**
  * The backend sends `{ "pet_rent": { "amount": 50, "currency": "USD", "note": "per iguana" } }`.
  * The Template Registry *doesn't* have "pet\_rent".
  * The Frontend Logic sees the extra key. It renders it in the **"Other Attributes"** section.
  * *Result:* The user sees the data. Nothing is lost.
