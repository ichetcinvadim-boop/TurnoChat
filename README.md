diff --git a/README.md b/README.md
new file mode 100644
index 0000000000000000000000000000000000000000..616ac67226583581599816b043dba35a8cc02f50
--- /dev/null
+++ b/README.md
@@ -0,0 +1,42 @@
+# TurnoChat Preview
+
+Если у вас не открывается `http://127.0.0.1:4173/messenger_preview.html`, обычно причина в том, что локальный сервер не запущен.
+
+## Быстрый запуск
+
+```bash
+cd /workspace/TurnoChat
+./run_preview.sh
+```
+
+После запуска откройте:
+
+- http://127.0.0.1:4173/messenger_preview.html
+
+## Если порт 4173 занят
+
+```bash
+cd /workspace/TurnoChat
+./run_preview.sh 8080
+```
+
+Тогда URL будет:
+
+- http://127.0.0.1:8080/messenger_preview.html
+
+## Альтернатива без скрипта
+
+```bash
+cd /workspace/TurnoChat
+python3 -m http.server 4173
+```
+
+## Проверка, что сервер поднялся
+
+В отдельном терминале:
+
+```bash
+curl -I http://127.0.0.1:4173/messenger_preview.html
+```
+
+Ожидается ответ со статусом `HTTP/1.0 200 OK` или `HTTP/1.1 200 OK`.
