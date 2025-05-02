# bot.py
import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from replay_analyzer import ReplayAnalyzer, storage
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("Token manquant dans .env !")

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_connect():
    print("Synchronisation des commandes avec Discord...")
    await bot.tree.sync()

@bot.tree.command(name="upload_replay", description="Upload un replay Rocket League")
async def upload_replay(interaction: discord.Interaction, fichier: discord.Attachment):
    await interaction.response.defer()
    
    try:
        content = await fichier.read()
        replay = json.loads(content)
                # Validation approfondie
        if not isinstance(replay.get('objects'), list):
            raise ValueError("Structure invalide : 'objects' doit être une liste")
        
        # Log supplémentaire
        sample_objects = [str(o)[:100] for o in replay.get('objects', [])[:3]]
        print(f"[DEBUG] Exemple d'objets : {sample_objects}")
        print(f"[DEBUG] Type du contenu brut: {type(content)}")  # Devrait être bytes
        
        replay = json.loads(content)
        print(f"[DEBUG] Type après json.loads: {type(replay)}")  # Devrait être dict
        print(f"[DEBUG] Clés principales: {replay.keys()}")
        
        # Validation approfondie
        required_keys = {'properties', 'network_frames', 'objects'}
        if not required_keys.issubset(replay.keys()):
            missing = required_keys - replay.keys()
            raise ValueError(f"Clés manquantes dans le JSON: {missing}")
            
        print("[DEBUG] Initialisation de ReplayAnalyzer...")
        analyzer = ReplayAnalyzer(replay)
        
        print("[DEBUG] Chargement des mappings...")
        mappings = storage.load_mappings()
        player_name = mappings.get(str(interaction.user.id))
        
        if not player_name:
            return await interaction.followup.send("Utilisez d'abord /register [pseudo]")
        
        print(f"[DEBUG] Récupération des données pour {player_name}...")
        stats = analyzer.get_player_data(player_name)
        
        print(f"[DEBUG] Stats obtenues: {stats.__dict__}")
        storage.save_player_stats(str(interaction.user.id), stats.__dict__)
        
        print("[DEBUG] Génération du rapport...")
        report = analyzer.generate_report(stats)
        await interaction.followup.send(report)
        
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        await interaction.followup.send(f"🚨 Erreur critique : {str(e)}")
    
    except json.JSONDecodeError:
        await interaction.followup.send("❌ Fichier JSON corrompu !")
    except ValueError as e:
        await interaction.followup.send(f"❌ Format de replay invalide : {str(e)}")    
    except Exception as e:
        await interaction.followup.send(f"🚨 Erreur : {str(e)}")

@bot.tree.command(name="register", description="Lier son pseudo Rocket League")
async def register(interaction: discord.Interaction, pseudo: str):
    storage.register_player(str(interaction.user.id), pseudo)
    await interaction.response.send_message(f"✅ Pseudo **{pseudo}** enregistré !")

@bot.tree.command(name="history", description="Affiche l'historique")
async def history(interaction: discord.Interaction):
    history_data = storage.load_history().get(str(interaction.user.id), [])
    
    if not history_data:
        return await interaction.response.send_message("📭 Aucun historique trouvé.")
    
    analyzer = ReplayAnalyzer({})
    stats_list = [storage.PlayerStats(**h) for h in history_data]
    summary = analyzer.generate_history_summary(stats_list)
    
    await interaction.response.send_message(summary)

if __name__ == "__main__":
    bot.run(TOKEN)  # ✅ TOKEN est bien un str ici