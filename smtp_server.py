import asyncio
import threading
from aiosmtpd.controller import Controller

class EmailHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f"📩 Recebido e-mail de {envelope.mail_from} para {envelope.rcpt_tos}")
        print(f"✉️ Conteúdo:\n{envelope.content.decode('utf-8')}")
        return '250 OK'

class SMTPServer(Controller):
    def __init__(self):
        super().__init__(EmailHandler(), hostname="0.0.0.0", port=1025)

def start_smtp():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    server = SMTPServer()

    def run():
        print("📡 Servidor SMTP rodando na porta 1025...")
        loop.run_until_complete(server.start())
        loop.run_forever()

    smtp_thread = threading.Thread(target=run, daemon=True)
    smtp_thread.start()
