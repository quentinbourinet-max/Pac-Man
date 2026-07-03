import asyncio
import src.__main__ # Votre code actuel

async def main():
    await src.__main__.main() # Votre fonction principale qui contient la boucle while

asyncio.run(main())
