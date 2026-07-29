# Privacy gap analysis

## Current safeguards

- изображения обрабатываются в памяти и не сохраняются приложением;
- filename не пишется в structured logs;
- API отвечает `Cache-Control: no-store`;
- лог-поля allowlisted;
- CORS opt-in;
- UI/API говорят research-only.

## Deployment gaps

- нет documented lawful basis/consent и controller/processor roles;
- нет retention/deletion schedule для proxy/log/backup layers;
- нет encryption/key-management evidence;
- нет access control или user identity;
- нет DPIA/records of processing;
- нет data residency/transfer assessment;
- нет incident/breach workflow;
- нет privacy-preserving production telemetry validation.

До закрытия gaps нельзя заявлять GDPR compliance.
