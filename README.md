# 🎭 Fake Quote Generator module (Pyrogram)

Create **fake quote stickers** in Telegram using custom text and a replied user’s identity.  
Built using [Pyrogram](https://docs.pyrogram.org/).

---

## ✨ Features

- 🔁 Generate **fake replies** with custom message
- 🖼️ Quote-style sticker output (like Quotly)
- 🧹 Auto-deletes command and sticker after a short timeout
- ⚙️ Simple, clean, and group-safe
- 💬 Works as a reply to any message

---

## 🚀 Usage

Use the bot by replying to a message and sending:

```
/fakeq <your custom text>
```
or
```
/fq <your custom text>
```

📌 Example:

1. Reply to someone's message  
2. Send:
```
/fakeq I hacked NASA last night 🚀
```

🤖 Bot will generate a **fake sticker** that looks like the replied user said it.

---

## 🔧 Setup Instructions

1. Add this module to your existing Pyrogram bot project.
2. Install required dependencies:
```bash
pip install httpx pyrogram tgcrypto
```

---

## 🧠 How it works

- Creates a dummy message using your custom text
- Mimics the replied user’s identity
- Sends the payload to `https://bot.lyo.su/quote/generate.png`
- Returns a **.webp sticker** with fake quote

---

## 🙏 Credits

- [Bisu G](https://github.com/bisug)
- 🤖 Made using ChatGpt. 
---
