# HighLife-discord

1. Configure `config.ini` and `messages.ini`

2. Build:
```
docker build -t dcbot .
```

3. Run:
```
docker run --restart=unless-stopped --name dcbot -itd -v $PWD/config.ini:/app/config.ini -v $PWD/messages.ini:/app/messages.ini dcbot
```