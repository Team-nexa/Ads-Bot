from Nexa.bot import bot
import Nexa.plugins  


def main():
    print("💡 Starting Ads Bot...")
    print("🔌 Loading plugins...")

    try:
        print("🚀 Bot is now running...")
        bot.run()
    except KeyboardInterrupt:
        print("🛑 Bot stopped manually (Ctrl+C)")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
    finally:
        print("⏹ Bot shutdown complete.")


if __name__ == "__main__":
    main()
    
