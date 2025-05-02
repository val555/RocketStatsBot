# utils.py
from typing import Dict, Tuple

def count_boost_pads(frames: Dict, actor_index: int) -> Tuple[int, int]:
    print(f"[UTILS] Début count_boost_pads (actor_index: {actor_index}, type frames: {type(frames)})")
    
    small = big = 0
    total_frames = len(frames.get('frames', []))
    print(f"[UTILS] Nombre total de frames à analyser : {total_frames}")
    
    for frame_idx, frame in enumerate(frames.get('frames', [])):
        if not isinstance(frame, dict):
            print(f"[UTILS] Frame #{frame_idx} ignorée (type invalide: {type(frame)})")
            continue
            
        for upd_idx, upd in enumerate(frame.get('updated_actors', [])):
            if upd.get('actor_id') == actor_index:
                print(f"[UTILS] Match actor_index dans frame {frame_idx}-{upd_idx}")
                attr = upd.get('attribute', {})
                
                for key in attr:
                    if 'ReplicatedBoost' in key:
                        amt = attr[key].get('boost_amount', 0)
                        if amt <= 12:
                            small += 1
                            print(f"[UTILS] Small boost détecté (montant: {amt})")
                        else:
                            big += 1
                            print(f"[UTILS] Big boost détecté (montant: {amt})")
    
    print(f"[UTILS] Résultat final - small: {small}, big: {big}")
    return small, big

def estimate_boost_time(frames: Dict, actor_index: int) -> float:
    print(f"[UTILS] Début estimate_boost_time (actor_index: {actor_index})")
    
    boost_time = 0.0
    prev_time = 0.0
    current_boost = 0.0
    
    for frame_idx, frame in enumerate(frames.get('frames', [])):
        current_time = frame.get('time', 0.0)
        delta = current_time - prev_time if prev_time else 0
        
        print(f"[UTILS] Frame {frame_idx} - temps: {current_time}, delta: {delta}")
        
        for upd in frame.get('updated_actors', []):
            if upd.get('actor_id') == actor_index:
                attr = upd.get('attribute', {})
                print(f"[UTILS] Mise à jour boost trouvée dans frame {frame_idx}")
                
                for key in attr:
                    if 'ReplicatedBoost' in key:
                        new_boost = attr[key].get('boost_amount', 0)
                        print(f"[UTILS] Boost changé: {current_boost} -> {new_boost}")
                        current_boost = new_boost
        
        if current_boost > 0:
            boost_time += delta
            print(f"[UTILS] Ajout delta {delta} (total: {boost_time})")
            
        prev_time = current_time
    
    print(f"[UTILS] Temps total en boost: {boost_time}")
    return boost_time