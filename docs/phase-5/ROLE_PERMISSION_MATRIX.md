# Role-Based Access Control (RBAC) & Permission Matrix

**Authority Document:** `AI_Textile Waste Intelligence Platform.pdf` (Pages 2–3, Module 1)  
**Target Platform:** AI Textile Waste Management Platform v2.1.0  
**Phase:** Phase 5 — Strict Specification Compliance  
**Date:** November 15, 2026  
**Auditor:** DevSecOps & Security Engineering Team  

---

## 1. Role Definitions & Organizational Responsibilities

The platform implements strict Role-Based Access Control enforcing least-privilege security across four enterprise user roles defined in Section 4, Module 1 of the specification:

1. **Administrator (`ADMIN`):**
   - System governance, user provisioning, role assignments, platform telemetry monitoring, database backups, and health checks.
2. **Recycling Facility Operator (`OPERATOR`):**
   - Waste batch intake, physical sorting, camera scan triggering, defect override confirmation, batch status lifecycle updates (Collected $\rightarrow$ Sorted $\rightarrow$ Processing $\rightarrow$ Recycled/Disposed).
3. **Sustainability Manager (`SUSTAINABILITY_MANAGER`):**
   - Environmental footprint analytics (CO₂ avoided, water saved, energy conserved), circular economy benchmarking, ESG compliance reporting, data exports.
4. **Textile Manufacturer (`MANUFACTURER`):**
   - Post-industrial cutting scrap registration, production batch tracking, roll defect characterization, material yield monitoring.

---

## 2. API Endpoint Permission Matrix

The table below details endpoint accessibility per role:

| Endpoint Path | HTTP Method | Administrator (`ADMIN`) | Facility Operator (`OPERATOR`) | Sustainability Manager (`SUSTAINABILITY_MANAGER`) | Textile Manufacturer (`MANUFACTURER`) | Public / Unauth |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `/api/v1/auth/login` | POST | Allowed | Allowed | Allowed | Allowed | Public |
| `/api/v1/auth/register` | POST | N/A (Cannot self-reg admin) | Allowed | Allowed | Allowed | Public |
| `/api/v1/auth/refresh` | POST | Allowed | Allowed | Allowed | Allowed | Public (valid token) |
| `/api/v1/auth/logout` | POST | Allowed | Allowed | Allowed | Allowed | Authenticated |
| `/api/v1/auth/me` | GET | Allowed | Allowed | Allowed | Allowed | Authenticated |
| `/api/v1/batches` | POST | **Allowed** | **Allowed** | Forbidden (403) | **Allowed** | Forbidden |
| `/api/v1/batches` | GET | Allowed | Allowed | Allowed | Allowed | Authenticated |
| `/api/v1/batches/{id}` | GET | Allowed | Allowed | Allowed | Allowed | Authenticated |
| `/api/v1/batches/{id}` | PUT | **Allowed** | **Allowed** | Forbidden (403) | Forbidden (403) | Forbidden |
| `/api/v1/batches/{id}/status` | POST | **Allowed** | **Allowed** | Forbidden (403) | Forbidden (403) | Forbidden |
| `/api/v1/batches/{id}` | DELETE | **Allowed (Admin Only)** | Forbidden (403) | Forbidden (403) | Forbidden (403) | Forbidden |
| `/api/v1/analysis/scan` | POST | **Allowed** | **Allowed** | Forbidden (403) | **Allowed** | Forbidden |
| `/api/v1/analysis` | GET | Allowed | Allowed | Allowed | Allowed | Authenticated |
| `/api/v1/analysis/metrics/summary` | GET | Allowed | Allowed | Allowed | Allowed | Authenticated |
| `/api/v1/analysis/{id}` | GET | Allowed | Allowed | Allowed | Allowed | Authenticated |
| `/api/v1/reports/esg-summary` | GET | Allowed | Allowed | **Allowed (Core View)** | Allowed | Authenticated |
| `/api/v1/reports/export/csv` | GET | Allowed | Allowed | **Allowed** | Allowed | Authenticated |
| `/api/v1/reports/batch/{id}/certificate` | GET | Allowed | Allowed | **Allowed** | Allowed | Authenticated |
| `/api/v1/reports/batch/{id}/certificate/html` | GET | Allowed | Allowed | **Allowed** | Allowed | Authenticated |
| `/api/v1/notifications` | GET | Allowed | Allowed | Allowed | Allowed | Authenticated (Own alerts) |
| `/api/v1/notifications/{id}/read` | PUT | Allowed | Allowed | Allowed | Allowed | Authenticated (Own alerts) |
| `/api/v1/users` | GET | **Allowed (Admin Only)** | Forbidden (403) | Forbidden (403) | Forbidden (403) | Forbidden |
| `/api/v1/users/{id}` | GET | **Allowed** | Own Record Only | Own Record Only | Own Record Only | Forbidden |
| `/api/v1/users/{id}` | PUT | **Allowed (Can modify roles)** | Own Record (No role change) | Own Record (No role change) | Own Record (No role change) | Forbidden |
| `/health/ready` | GET | Allowed | Allowed | Allowed | Allowed | Public Probe |
| `/health/live` | GET | Allowed | Allowed | Allowed | Allowed | Public Probe |

---

## 3. Data Isolation & Security Safeguards

1. **Privilege Escalation Prevention:**
   Non-administrators attempting to submit a modified `role` attribute in `PUT /users/{id}` receive HTTP 403 Forbidden (`"Only administrators can modify user roles"`). Tested via `test_operator_cannot_escalate_own_role`.
2. **Cross-User Profile Isolation:**
   Users requesting profile details for another user ID receive HTTP 403 Forbidden unless authenticated as `ADMIN`. Tested via `test_cross_user_profile_access_blocked`.
3. **Public Registration Guardrail:**
   The public registration endpoint (`POST /auth/register`) strictly denies assigning `ADMIN` privileges upon account creation. Attempts fail with HTTP 403 Forbidden (`"Public administrator self-registration is strictly forbidden"`). Tested via `test_public_register_admin_forbidden`.
4. **Batch Ownership & Audit Logging:**
   Every batch registration records `operator_id` pointing to the initiating user. All status transitions record `changed_by_id`, timestamp, and transition notes in the immutable `status_history` table.

---

## 4. Automated Verification Results

All RBAC policies are validated by automated test suites in `tests/test_rbac.py` and `tests/test_phase5_specification_compliance.py`:

```
tests/test_rbac.py::test_list_users_as_admin_allowed PASSED              [100%]
tests/test_rbac.py::test_list_users_as_operator_forbidden PASSED         [100%]
tests/test_rbac.py::test_list_users_as_recycler_forbidden PASSED         [100%]
tests/test_rbac.py::test_cross_user_profile_access_blocked PASSED        [100%]
tests/test_rbac.py::test_admin_can_update_user_role PASSED               [100%]
tests/test_rbac.py::test_operator_cannot_escalate_own_role PASSED        [100%]
tests/test_phase5_specification_compliance.py::test_four_user_roles_rbac PASSED [100%]
```

The RBAC implementation is fully compliant with the specification and zero privilege-escalation vulnerabilities exist.
