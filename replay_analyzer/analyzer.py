# analyzer.py
import json
from .models import PlayerStats
from .utils import count_boost_pads, estimate_boost_time

class ReplayAnalyzer:
    def __init__(self, replay_json: dict):
        # Vérifier la structure critique
        if not isinstance(replay_json.get('objects'), list) or not isinstance(replay_json.get('properties'), dict):
            raise ValueError("Structure JSON invalide pour un replay Rocket League")
            
        self.data = replay_json
        self.props = replay_json.get('properties', {})
        self.network = replay_json.get('network_frames', {})

    def _find_player_actor_id(self, player_name: str) -> int:
        """Trouve l'actor_id via les données network_frames"""
        print(f"[DEBUG] Recherche Actor ID pour {player_name}")
    
        target_name_lower = player_name.lower()
    
        for frame in self.network.get('frames', []):
            for actor in frame.get('updated_actors', []):
                attributes = actor.get('attribute', {})
            
                # Recherche du nom dans les attributs PRI
                for key, value in attributes.items():
                    if 'Engine.PlayerReplicationInfo:PlayerName' in key:
                        actor_name = value.strip().lower()
                        if actor_name == target_name_lower:
                            print(f"[SUCCÈS] Actor ID {actor['actor_id']} trouvé pour {player_name}")
                            return actor['actor_id']
                
                    # Solution de repli pour les véhicules
                    if 'TAGame.Car_TA:ReplicatedOwnerName' in key:
                        car_owner = value.strip().lower()
                        if car_owner == target_name_lower:
                            print(f"[SUCCÈS] Actor ID {actor['actor_id']} (via Car) pour {player_name}")
                            return actor['actor_id']

        raise ValueError(f"Aucun Actor ID trouvé pour {player_name} dans network_frames")

    def get_player_data(self, player_name: str) -> PlayerStats:
        print(f"[ANALYSE] Début get_player_data pour {player_name}")
    
        # Récupération des stats depuis PlayerStats
        player_stats = next((p for p in self.props.get('PlayerStats', []) 
                            if p.get('Name', '').lower() == player_name.lower()), None)
    
        if not player_stats:
            raise ValueError(f"Aucune statistique trouvée pour {player_name}")

        # Calcul du boost
        try:
            actor_id = self._find_player_actor_id(player_name)
            small, big = count_boost_pads(self.network, actor_id)
            boost_time = estimate_boost_time(self.network, actor_id)
        except Exception as e:
            print(f"[ERREUR] Calcul boost: {str(e)}")
            small = big = boost_time = 0

        return PlayerStats(
            name=player_name,
            goals=player_stats.get('Goals', 0),
            saves=player_stats.get('Saves', 0),
            shots=player_stats.get('Shots', 0),
            small_boosts=small,
            big_boosts=big,
            boost_time=boost_time,
            total_time=self.props.get('TotalSecondsPlayed', 0),
            won=(self.props.get('Team0Score', 0) > self.props.get('Team1Score', 0)) 
                if player_stats.get('Team') == 0 else 
                (self.props.get('Team1Score', 0) > self.props.get('Team0Score', 0))
        )

    def generate_report(self, stats: PlayerStats) -> str:
        boost_pct = (stats.boost_time / stats.total_time * 100) if stats.total_time else 0
        return (
            f"**Statistiques de {stats.name} :**\n"
            f"Victoire : {'✅' if stats.won else '❌'}\n"
            f"⮕ Buts : {stats.goals}\n"
            f"⮕ Saves : {stats.saves}\n"
            f"⮕ Tirs : {stats.shots}\n"
            f"⮕ Pastilles boost : {stats.small_boosts}\n"
            f"⮕ Gros boosts : {stats.big_boosts}\n"
            f"⮕ Temps en boost : {boost_pct:.1f}%"
        )

    def generate_history_summary(self, stats_list: list[PlayerStats]) -> str:
        if not stats_list:
            return "Aucun historique disponible."
        n = len(stats_list)
        avg = lambda key: sum(getattr(s, key) for s in stats_list) / n
        wins = sum(1 for s in stats_list if s.won)
        return (
            f"**Résumé des {n} derniers matchs :**\n"
            f"Victoires : {wins}/{n}\n"
            f"⮕ Buts/match : {avg('goals'):.1f}\n"
            f"⮕ Saves/match : {avg('saves'):.1f}\n"
            f"⮕ Tirs/match : {avg('shots'):.1f}\n"
            f"⮕ Pastilles/match : {avg('small_boosts'):.1f}\n"
            f"⮕ Gros boosts/match : {avg('big_boosts'):.1f}"
        )