# Privacy logging policy

Разрешено: event, bounded request ID, route path, method, status, duration,
error type, model status, service/version.

Запрещено: image bytes, filename, patient/slide identity, Authorization/Cookie,
query string, exception message/path, model local path, Hugging Face token,
multipart body и unrestricted user-agent.

Текущий formatter игнорирует traceback и неизвестные extras, экранирует CR/LF.
Для расследований следует использовать код ошибки и защищённую internal
telemetry, а не раскрывать чувствительный traceback в stdout.
