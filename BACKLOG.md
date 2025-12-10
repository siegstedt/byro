# Backlog

## Phase 1: Ingestion & The "Brain" (The Triage Loop)

### F-01: Multi-Channel Document Ingestion

* **User Story:** As a user, I want to forward emails or upload files directly to the app so that I don't have to manually download and re-upload documents.
* **Functional Detail:**
  * **Email Hook:** System generates a unique `user_id@inbox.byro.app` address. Emails sent here are parsed; attachments (PDF, DOCX, IMG) are extracted; body text is treated as a "Note."
  * **Drag & Drop UI:** A persistent "Upload" zone on the dashboard.
  * **Queue Creation:** Successfully ingested files immediately appear in the `Inbox_Items` table with a status of `processing`.
* **Acceptance Criteria:**
  * User can upload PDF, PNG, JPG, and DOCX.
  * System handles email forwarding with multiple attachments (creates multiple queue items).
  * User receives a UI notification (toast/spinner) when upload is complete.
  * Max file size limit is enforced (e.g., 25MB) with a clear error message.

### F-02: The Extraction Pipeline (OCR & LLM)

* **User Story:** As a system, I need to read the raw uploaded document and structure its data into JSON so that the user doesn't have to type it manually.
* **Functional Detail:**
  * **Trigger:** Automated background job starts upon ingestion.
  * **OCR:** Converts images/PDFs to raw text strings.
  * **Normalization:** The LLM analyzes the text against the **Target Schema** (Date, Counterparty, Total Value, Auto-Renewal, Category).
  * **Payload Generation:** The system stores the result as a JSON object in the `Inbox_Items` table. It does *not* create a Matter yet.
* **Acceptance Criteria:**
  * Pipeline extracts correct ISO dates (YYYY-MM-DD) from various text formats ("Jan 1st", "01/01/24").
  * Pipeline identifies the correct "Category" (e.g., Lease vs. Invoice) with >80% accuracy.
  * If extraction fails (corrupt file), status updates to `error` and alerts the user.

### F-03: The Triage Workbench (Review UI)

* **User Story:** As a user, I want to review the AI's extraction side-by-side with the original document to correct errors before saving it to my permanent records.
* **Functional Detail:**
  * **Split-Screen Interface:** Left panel renders the PDF. Right panel displays a Form pre-filled with the AI's extraction JSON.
  * **Routing Logic:**
    * *Option A (New):* "Create New Matter."
    * *Option B (Existing):* "Attach to Existing Matter" (Searchable dropdown of existing matters).
  * **Validation:** User can edit any field (e.g., change the extracted date).
  * **Commit:** Clicking "Approve" moves data from `Inbox_Items` $\rightarrow$ `Matters` (or `Documents`) and archives the inbox item.
* **Acceptance Criteria:**
  * The PDF viewer supports zooming and scrolling.
  * If "Attach to Existing" is selected, the form adapts to show only relevant fields (e.g., "Invoice Date" and "Amount" rather than "Contract Start Date").
  * Data is only persisted to the core tables (`Matters`, `Liabilities`) upon explicit user click.

---

## Phase 2: The Core Data Experience (Matter Management)

### F-04: Dynamic Matter View (Schema-Driven UI)

* **User Story:** As a user, I want to see specific details relevant to the type of contract I am viewing (e.g., "Rent" for Leases, "Seats" for Software) without seeing a cluttered list of empty fields.
* **Functional Detail:**
  * **Template Registry:** The frontend fetches a configuration object for the active Category.
  * **Render Logic:**
    * *Header:* Renders "Primary" keys defined in the template.
    * *Details Tab:* Renders "Secondary" keys.
    * *Fallbacks:* Any data present in the extraction but *missing* from the template is rendered in an "Additional Attributes" generic list.
* **Acceptance Criteria:**
  * A "SaaS" matter shows "Renewal Date" and "Cost" prominently.
  * A "Vehicle Lease" matter shows "VIN" and "Mileage Limit."
  * Unknown/New attributes are still visible, never hidden.

### F-05: The "Life of a Matter" Timeline

* **User Story:** As a user, I want to see a chronological feed of everything that has happened with a specific legal matter so I can understand the narrative.
* **Functional Detail:**
  * **Unified Feed:** Aggregates three sources into one vertical timeline:
        1. **Documents:** (e.g., "Dec 1: Original Contract Uploaded").
        2. **Events:** (e.g., "Jan 1: Effective Date started").
        3. **Liabilities/Invoices:** (e.g., "Feb 1: Invoice #001 for $500").
  * **Gap Detection:** Visual indicator if a recurring event (like a monthly invoice) is expected but missing.
* **Acceptance Criteria:**
  * Timeline is sorted reverse-chronological by default.
  * Clicking a timeline item (e.g., an uploaded document) opens the document viewer overlay.

### F-06: The Financial Ledger (Liabilities)

* **User Story:** As a user, I want to see a consolidated list of financial obligations for a contract so I know exactly what I owe and when.
* **Functional Detail:**
  * **Structured Table:** Columns for Title, Due Date, Amount, Status (Paid/Unpaid/Disputed).
  * **Extraction Source:** These rows are generated during the Triage phase (e.g., extracting a "Payment Schedule" table from a PDF).
* **Acceptance Criteria:**
  * Supports multiple currencies (display only, no live conversion required for V1).
  * User can manually toggle status from "Unpaid" to "Paid."

---

## Phase 3: The Sentinel (Dashboard & Intelligence)

### F-07: The "Horizon" Dashboard

* **User Story:** As a user, I want a high-level overview of immediate risks and deadlines so I don't miss critical dates.
* **Functional Detail:**
  * **Traffic Light Widget:**
    * *Red:* Overdue or Due in < 48 hours.
    * *Yellow:* Due within 7 days.
    * *Green:* Due within 30 days.
  * **Task List:** Aggregates all `Events` where `status != completed`.
* **Acceptance Criteria:**
  * Dashboard loads under 200ms (requires efficient indexing on `due_date`).
  * Clicking a task deep-links directly to the relevant Matter.

#### F-08: Calendar Integration (ICS Export)

* **User Story:** As a user, I want to see my contract deadlines in my Outlook/Google Calendar so I get reminded even when not using the app.
* **Functional Detail:**
  * **Subscription Link:** App generates a secure `.ics` feed URL.
  * **Data Mapping:** Maps `Event.title` to Calendar Subject and `Event.due_date` to Calendar Date.
* **Acceptance Criteria:**
  * The feed updates automatically when a date is changed in the app (standard polling intervals apply).

#### F-09: The "Oracle" (Semantic Search)

* **User Story:** As a user, I want to ask questions about my documents using natural language so I can find information without knowing the exact keywords.
* **Functional Detail:**
  * **Embedding Pipeline:** On upload, document text is chunked and vectorized (stored in `pgvector`).
  * **Search Interface:** A chat-like input bar.
  * **Retrieval:** System performs cosine similarity search $\rightarrow$ retrieves relevant text chunks $\rightarrow$ LLM synthesizes an answer.
* **Acceptance Criteria:**
  * Query: "Which contracts have a non-compete?" returns a list of Matters, not just raw text snippets.
  * Response includes "Citations" (links to the specific document source).

---

## Phase 4: Data Integrity (The Guardrails)

### F-10: Audit Log & Versioning

* **User Story:** As a user, I need to know that my data hasn't been silently changed by the AI or a bug.
* **Functional Detail:**
  * **Edit History:** Any change to a `Matter` field (e.g., changing Rent from $500 to $600) is recorded in a `History` table.
  * **Source Truth:** Every field in a Matter keeps a reference ID to the `Inbox_Item` that originated it.
* **Acceptance Criteria:**
  * User can view "Previous Values" for any field.
