# Gas Price Discord Bot

A Discord bot that provides real-time gas price updates for specific states and sends scheduled notifications.

## Features
- **Real-time Gas Prices**: Fetch current prices using `!gas <state>`.
- **User Preferences**: Save your location with `!setlocation <state>` so you can just type `!gas`.
- **Scheduled Updates**: Automatically posts gas prices to your channel every hour.
- **Reliability**: Uses CollectAPI with an EIA (Energy Information Administration) fallback for data.

## Setup & Local Running

1.  **Install Requirements**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Create a `.env` file in this directory with the following secrets:
    ```env
    DISCORD_BOT_TOKEN=your_discord_bot_token
    COLLECT_API_KEY=your_collectap_key
    EIA_API_KEY=your_eia_api_key
    ```

3.  **Run the Bot**
    ```bash
    python dBot.py
    ```

## ☁️ How to Host 24/7 (Deployment)

To keep the bot running constantly without your computer, use a cloud provider. This project includes a `Procfile` ready for deployment.

### Option 1: Railway (Recommended - Easiest)
1.  **Upload to GitHub**: Push this code to a new GitHub repository.
2.  **Sign Up**: Go to [railway.app](https://railway.app/) and sign in with GitHub.
3.  **New Project**: Click "New Project" -> "Deploy from GitHub repo" -> Select this repo.
4.  **Variables**: 
    - Go to the "Variables" tab in your new project.
    - Add your secrets: `DISCORD_BOT_TOKEN`, `COLLECT_API_KEY`, `EIA_API_KEY`.
5.  **Deploy**: Railway will automatically build using the `Procfile` and start your bot!

### Option 2: Fly.io (Command Line)
1.  **Install CLI**: Download `flyctl`.
2.  **Login**: `fly auth login`
3.  **Launch**: Run `fly launch` in this folder.
4.  **Secrets**: Set secrets using `fly secrets set DISCORD_BOT_TOKEN=...`

### Option 3: Heroku
1.  **Install CLI**: Download Heroku CLI.
2.  **Create**: `heroku create`
3.  **Secrets**: Set env vars in the dashboard or via CLI.
4.  **Deploy**: `git push heroku main`
