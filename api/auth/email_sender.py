import aiohttp

from config import settings


def get_html(code):
    return f'''
<div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
  <div style="margin:50px auto;width:70%;padding:20px 0">
    <div style="border-bottom:1px solid #eee">
      <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">Papper</a>
    </div>
    <p style="font-size:1.1em">Здравствуйте,</p>
    <p>Спасибо, что выбрали Papper. Ваш постоянный пароль для входа в аккаунт:</p>
    <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{code}</h2>
    <p style="font-size:0.9em;">С уважением,<br />команда Papper</p>
    <hr style="border:none;border-top:1px solid #eee" />
    <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
      <p>AI_кабанчики</p>
    </div>
  </div>
</div>'''


async def send_email(code: str, email: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(url="https://api.mailgun.net/v3/auth.papper.tech"
                                    "/messages",
                                auth=aiohttp.BasicAuth("api", settings.mailgun_api_key),
                                data={
                                    "from": "Papper Auth <support@auth.papper.tech>",
                                    "to": [email],
                                    "subject": "Код подтверждения авторизации",
                                    "text": "Hello World",
                                    "html": get_html(code)}) as response:
            print(response.status)
            print(await response.text())