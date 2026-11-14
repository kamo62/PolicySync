# Lark Base integration technical notes

Researched 14 November 2026. Documentation/source review only: no tenant, credentials, API calls against customer resources or live permission tests. This note supplements PRD §14; it does not enable integration or change the synthetic-only boundary.

## Proposed implementation contract

Use an enterprise custom app with app-identity authentication for a manually initiated, read-only organisation import. No OAuth login flow, webhook receiver, Base provisioning or write-back is needed for the initial adapter. This is a proposed implementation of the PRD boundary.

| Operation | Contract verified in official sources |
|---|---|
| API host | `https://open.larksuite.com`, explicitly selected for international Lark. The official Python SDK also defines a separate Feishu host; do not accept its default without checking. |
| Obtain app-identity token | `POST /open-apis/auth/v3/tenant_access_token/internal`, JSON body containing `app_id` and `app_secret`. The SDK request declares no prerequisite access-token type. |
| Read organisation records | `GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`; supports tenant or user access tokens. Proposed adapter uses tenant identity. |
| Select fields | `field_names` query parameter is supported; configure explicit field names and validate the returned mapping. It is a data-minimisation mechanism, not an authorisation barrier. |
| Pagination | Request `page_size` and opaque `page_token`; response body has `items`, `has_more`, `page_token` and `total`. Continue until `has_more` is false; detect repeated/missing continuation tokens and surface incomplete runs. |

Sources: official SDK [host constants](https://github.com/larksuite/oapi-sdk-python/blob/v2_main/lark_oapi/core/const.py), [token request](https://github.com/larksuite/oapi-sdk-python/blob/v2_main/lark_oapi/api/auth/v3/model/internal_tenant_access_token_request.py), [token body](https://github.com/larksuite/oapi-sdk-python/blob/v2_main/lark_oapi/api/auth/v3/model/internal_tenant_access_token_request_body.py), [record-list request](https://github.com/larksuite/oapi-sdk-python/blob/v2_main/lark_oapi/api/bitable/v1/model/list_app_table_record_request.py) and [response body](https://github.com/larksuite/oapi-sdk-python/blob/v2_main/lark_oapi/api/bitable/v1/model/list_app_table_record_response_body.py). These are moving branch references checked on the research date; pin a chosen dependency and recheck contracts during implementation. No SDK dependency is selected by this note.

The Base `app_token` identifies the Base resource and differs from the developer app ID and bearer token. `table_id` identifies a table within that Base. The API overview requires the app to be an owner or collaborator before tenant-token resource access succeeds. Therefore successful token acquisition alone is insufficient evidence of record access. [Official Base overview](https://open.larksuite.com/document/server-docs/docs/bitable-v1/bitable-overview).

## Permissions and onboarding

Request the minimum read permission accepted by the selected record-list endpoint in the actual tenant. `bitable:app:readonly` is a documented scope identifier, but its sufficiency for this app-identity endpoint and any newer granular alternative must be confirmed in the endpoint permission panel and tenant console. Do not grant broad write, contact-directory, messaging or file-download scopes for this import. Lark documents scope application and tenant-dependent approval; confirm that grants have taken effect before testing the target Base. [Official scope example](https://open.larksuite.com/document/ukTMukTMukTM/uETOwYjLxkDM24SM5AjN), [permission application guide](https://open.larksuite.com/document/ukTMukTMukTM/uQjN3QjL0YzN04CN2cDN).

Use a dedicated Base/table containing only permitted CRM data. Selective field retrieval cannot protect data already readable by an overprivileged app. Before connecting, confirm tenant, region, administrator approval, app collaborator access, exact field types/names, permission grants, processing terms and current tier/API allowance. Do not assume Starter/free pricing or residency from API availability.

## Mapping, failure and privacy rules

These are proposed local adapter rules, not claims about provider guarantees:

- Configure app ID/secret and Base/table identifiers outside Git. Cache tokens in memory, refresh using the returned expiry with a safety margin, and never log request bodies, tokens or record payloads. Confirm exact token response/expiry parsing against the selected implementation before coding.
- Allow only CRM organisation ID, trading name, business segment and non-sensitive onboarding status. Discard unconfigured fields before persistence. No claim IDs, insured/claimant identities, evidence, policies, medical information, reserves or legal commentary.
- Retain provider, Base, table and record identity in the external reference mapping. PRD's unique provider/external ID must use a namespaced external ID if more than one Base/table is configured. Never match organisations by trading name alone.
- Treat import as a bounded job with connect/read timeouts and visible run status, source timestamp, counts and errors. Stage validated pages and reconcile before marking a run complete; a truncated run must not delete local organisations or imply source deletions.
- Check HTTP status and provider application error result. Retry transient reads and throttling with bounded backoff/jitter and provider wait guidance when available; stop on permissions/schema failures. Do not retry indefinitely or block ordinary claims operations.
- Start conservatively with a proposed page size of 100, one import at a time and a bounded retry budget. These are local choices, not verified provider quotas. No batch writes are in scope.

## Unresolved provider details and implementation checks

The older official [Base notification/overview](https://open.larksuite.com/document/server-docs/docs/bitable-v1/notification) describes a 500-record list limit and smaller batch guidance, while the newer [Base overview](https://open.larksuite.com/document/server-docs/docs/bitable-v1/bitable-overview) describes a 1,000-record batch limit and tenant-dependent capacity. Do not apply a batch-write number to record-list pagination. Recheck the chosen endpoint's current limits before implementing; no numerical requests-per-second quota was verified here.

The [record-list page](https://open.larksuite.com/document/server-docs/docs/bitable-v1/app-table-record/list) returned no readable content in the research tool. The [token reference](https://open.larksuite.com/document/server-docs/authentication-management/access-token/tenant_access_token_internal) and [frequency-control page](https://open.larksuite.com/document/server-docs/api-call-guide/frequency-control) could not be retrieved. SDK source was used for the request contracts above; exact throttle headers/codes, token expiry response shape, endpoint quota and tenant permissions remain checks before live use.

At implementation, mock pagination, duplicate records, field rename/type mismatch, prohibited extra fields, token expiry, nonzero application errors, permission denial, throttling, timeout and interrupted runs. Verify offline claims remain usable. When a live connection is chosen, first test only a dedicated synthetic CRM table and record redacted evidence of both authentication and permitted record access. No live checks or account setup have been performed.
