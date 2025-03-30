from models import TeamForm


def make_tg_message(data: TeamForm):
    return (
        f"🏀 Новая заявка на турнир!\n\n"
        f"📌 *Команда:* {data.team_name}\n\n"
        f"👤 *Игроки:*\n"
        f"1️⃣ {data.player1}\n"
        f"2️⃣ {data.player2}\n"
        f"3️⃣ {data.player3}\n"
        f"4️⃣ {data.player4}\n"
        f"5️⃣ {data.player5}"
    )
